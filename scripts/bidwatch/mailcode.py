"""Read BidNet's emailed confirmation code straight from the mailbox, so a new-device login needs no human.

BidNet emails "Your BidNet Direct confirmation code" (noreply@bidnet.com, body "Your confirmation code for
BidNet Direct is: 123456") after every password login from a device it has not seen. The scanner sits on the
code prompt (bidnet.login) and polls three sources: BIDNET_CODE, ~/.brownbison/bidnet_code (set_code.py), and,
when these two env vars are set, the inbox over IMAP:

    BIDNET_CODE_IMAP_USER   mailbox login (default luke@brownbisonco.com)
    BIDNET_CODE_IMAP_PASS   a Google "app password" for that mailbox (Google Account -> Security -> 2-Step
                            Verification -> App passwords). NOT the Gmail password. Set it in the cloud
                            environment's settings like the other secrets; never commit it.
    BIDNET_CODE_IMAP_HOST   default imap.gmail.com

Read-only on purpose: the mailbox is opened readonly and bodies are fetched with BODY.PEEK, so nothing is
marked read, moved or labeled (CLAUDE.md: Gmail is read-only for the agent). Only messages that arrived AFTER
the login attempt count, because each password login issues a new code and older codes are dead.
"""
from __future__ import annotations

import datetime as dt
import email
import email.utils
import imaplib
import os
import re
import time
from email.message import Message

SENDER = "noreply@bidnet.com"
SUBJECT = "confirmation code"
CODE_RX = re.compile(r"confirmation code for BidNet Direct is:?\s*(\d{6})\b|\b(\d{6})\b")
ENV_USER, ENV_PASS, ENV_HOST = "BIDNET_CODE_IMAP_USER", "BIDNET_CODE_IMAP_PASS", "BIDNET_CODE_IMAP_HOST"
IMAP_FACTORY = imaplib.IMAP4_SSL  # tests swap in a fake mailbox


def configured() -> bool:
    return bool(os.environ.get(ENV_PASS))


def creds() -> tuple[str, str, str]:
    return (os.environ.get(ENV_USER) or "luke@brownbisonco.com", os.environ.get(ENV_PASS, ""),
            os.environ.get(ENV_HOST) or "imap.gmail.com")


def extract_code(text: str) -> str | None:
    """The 6-digit code from the email body (prefers the sentence BidNet uses; falls back to any 6 digits)."""
    m = CODE_RX.search(text or "")
    return (m.group(1) or m.group(2)) if m else None


def message_text(msg: Message) -> str:
    parts = msg.walk() if msg.is_multipart() else [msg]
    out = []
    for p in parts:
        if p.get_content_type() in ("text/plain", "text/html"):
            payload = p.get_payload(decode=True) or b""
            out.append(payload.decode(p.get_content_charset() or "utf-8", errors="ignore"))
    text = " ".join(out)
    return re.sub(r"<[^>]+>", " ", text)  # html -> words; the code survives either way


def message_date(msg: Message) -> dt.datetime | None:
    try:
        d = email.utils.parsedate_to_datetime(msg.get("Date", ""))
    except (TypeError, ValueError):
        return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def fetch_code(since: dt.datetime, imap_factory=None) -> str | None:
    """Newest BidNet code emailed at or after `since` (tz-aware), or None. One connection, read-only."""
    user, pw, host = creds()
    if not pw:
        return None
    since = since if since.tzinfo else since.replace(tzinfo=dt.timezone.utc)
    conn = (imap_factory or IMAP_FACTORY)(host)
    try:
        conn.login(user, pw)
        conn.select("INBOX", readonly=True)
        day = (since - dt.timedelta(days=1)).strftime("%d-%b-%Y")  # IMAP SINCE is date-only; filter by Date below
        typ, data = conn.search(None, f'(FROM "{SENDER}" SUBJECT "{SUBJECT}" SINCE {day})')
        if typ != "OK" or not data or not data[0]:
            return None
        best: tuple[dt.datetime, str] | None = None
        for num in data[0].split()[-10:]:  # newest ten is plenty; BidNet sends one per login
            typ, parts = conn.fetch(num, "(BODY.PEEK[])")
            if typ != "OK" or not parts:
                continue
            raw = next((p[1] for p in parts if isinstance(p, tuple) and len(p) > 1), None)
            if not raw:
                continue
            msg = email.message_from_bytes(raw)
            when = message_date(msg)
            if when is None or when < since - dt.timedelta(seconds=90):  # clock slack between BidNet and Gmail
                continue
            code = extract_code(message_text(msg))
            if code and (best is None or when > best[0]):
                best = (when, code)
        return best[1] if best else None
    finally:
        try:
            conn.logout()
        except Exception:  # noqa: BLE001 - logout failures never matter
            pass


def poll_code(since: dt.datetime, timeout: float, every: float = 10.0, imap_factory=None,
              sleep=time.sleep) -> str | None:
    """Poll the mailbox until a code newer than `since` shows up or `timeout` seconds pass."""
    deadline = time.time() + max(0.0, timeout)
    while True:
        try:
            code = fetch_code(since, imap_factory)
        except Exception:  # noqa: BLE001 - a transient IMAP error is not a reason to abandon the login
            code = None
        if code or time.time() >= deadline:
            return code
        sleep(every)
