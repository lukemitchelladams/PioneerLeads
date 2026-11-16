#!/usr/bin/env python3
"""READ-ONLY ledger view of an outbox manifest: which entries went out, and (with --inbox) whether anyone wrote back.

    python3 scripts/outbox_status.py ops/outbox/2026-11-16/outbox-chases.json [--inbox] [--days N]

Default (no --inbox): no network at all. One row per manifest entry: key | recipients (count of to+cc+bcc) | sent (Gmail id
from sent.json beside the manifest, or "not sent") | bcc_count from sent.json | subject (60 chars), then "N entries, M sent,
K unsent".

--inbox: for each entry also asks Gmail, read-only, for inbound mail from the entry's recipient domains (the full address for
gmail.com / comcast.net / yahoo.com / hotmail.com / outlook.com) newer than N days (default 14), never from
luke@brownbisonco.com: one messages.list and, for the newest hit, one messages.get (format=metadata, headers From/Subject/Date).
It prints the count and the newest message's date, sender DOMAIN only (never a person's mailbox) and subject. An API error on one
entry prints "inbox: error ..." and the run goes on.

This script never sends, drafts, labels, trashes or modifies anything. scripts/gmail_api.py is imported only for --inbox; importing
it sends nothing (only its send() sends, and nothing here calls it).
"""
import argparse
import datetime as dt
import email.utils
import json
import sys
import urllib.parse
from pathlib import Path

OWNER = "luke@brownbisonco.com"
FREEMAIL = {"gmail.com", "comcast.net", "yahoo.com", "hotmail.com", "outlook.com"}   # a domain says nothing: use the address
SUBJECT_WIDTH = 60
LIST_PATH = "/gmail/v1/users/me/messages?maxResults=40&q="
GET_PATH = "/gmail/v1/users/me/messages/{id}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date"


def truncate(s, n=SUBJECT_WIDTH):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[: n - 3] + "..."


def recipients(entry):
    """to + cc + bcc as listed in the manifest (strings only; anything malformed counts nothing)."""
    out = []
    for k in ("to", "cc", "bcc"):
        v = entry.get(k) if isinstance(entry, dict) else None
        if isinstance(v, list):
            out += [x.strip() for x in v if isinstance(x, str) and x.strip()]
    return out


def build_rows(manifest, sent):
    """One row per entry. sent is the sent.json mapping key -> {id, threadId, to, bcc_count, attachments}. Pure: no I/O."""
    rows = []
    for e in manifest:
        key = str(e.get("key") or "?") if isinstance(e, dict) else "?"
        rec = sent.get(key) if isinstance(sent, dict) else None
        rows.append({
            "key": key,
            "recipients": len(recipients(e)),
            "sent": str(rec.get("id") or "sent (no id)") if isinstance(rec, dict) else "not sent",
            "bcc_count": rec.get("bcc_count") if isinstance(rec, dict) else None,
            "subject": truncate(e.get("subject") if isinstance(e, dict) else ""),
        })
    return rows


def summary(rows):
    n_sent = sum(1 for r in rows if r["sent"] != "not sent")
    return f"{len(rows)} entries, {n_sent} sent, {len(rows) - n_sent} unsent"


def _address(s):
    """Bare lowercase address from 'Name <a@b>' or 'a@b'."""
    name, addr = email.utils.parseaddr(str(s))
    return (addr or str(s)).strip().lower()


def reply_terms(entry):
    """Gmail from: terms for an entry: the domain of each business address, the whole address for free-mail domains; no repeats."""
    terms = []
    for a in recipients(entry):
        a = _address(a)
        if "@" not in a:
            continue
        domain = a.rpartition("@")[2]
        t = a if domain in FREEMAIL else domain
        if t not in terms:
            terms.append(t)
    return terms


def reply_query(entry, days=14):
    """Gmail search for inbound mail answering this entry; '' when the entry names no recipient."""
    terms = reply_terms(entry)
    if not terms:
        return ""
    who = f"from:{terms[0]}" if len(terms) == 1 else "(" + " OR ".join(f"from:{t}" for t in terms) + ")"
    return f"{who} newer_than:{max(1, int(days))}d -from:{OWNER}"


def sender_domain(from_header):
    """The part after @ of a From header, and only that: 'Larry Moss <larry.moss@hoodz.us.com>' -> 'hoodz.us.com'."""
    addr = _address(from_header)
    return addr.rpartition("@")[2] if "@" in addr else "?"


def _short(e):
    msg = e.code if isinstance(e, SystemExit) else e
    return " ".join(str(msg).split())[:90] or type(e).__name__


def _when(msg, headers):
    try:
        return dt.datetime.fromtimestamp(int(msg["internalDate"]) / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    except (KeyError, TypeError, ValueError):
        return headers.get("date", "?")[:25]


def check_inbox(entry, days, token, call):
    """Read-only reply check through `call` (gmail_api.call or a stand-in): messages.list, then messages.get on the newest hit.
    -> {"count", "more", "newest": None | {"date", "domain", "subject"}} or {"error": str}. Never raises."""
    q = reply_query(entry, days)
    if not q:
        return {"error": "no recipients in entry"}
    try:
        res = call("GET", LIST_PATH + urllib.parse.quote(q), token) or {}
        msgs = res.get("messages") or []
        out = {"count": len(msgs), "more": bool(res.get("nextPageToken")), "newest": None}
        if msgs:                                                  # Gmail lists newest first
            d = call("GET", GET_PATH.format(id=msgs[0]["id"]), token) or {}
            h = {x["name"].lower(): x["value"] for x in (d.get("payload") or {}).get("headers", [])}
            out["newest"] = {"date": _when(d, h), "domain": sender_domain(h.get("from", "")), "subject": truncate(h.get("subject", ""))}
        return out
    except (Exception, SystemExit) as e:                          # gmail_api.call() exits on an HTTP error; one entry must not end the run
        return {"error": _short(e)}


def format_inbox(r, days):
    if "error" in r:
        return f"inbox: error {r['error']}"
    n = f"{r['count']}{'+' if r.get('more') else ''}"
    if not r.get("newest"):
        return f"inbox: {n} inbound in {days}d"
    w = r["newest"]
    return f"inbox: {n} inbound in {days}d; newest {w['date']} from {w['domain']}: {w['subject']}"


def _gmail():
    """scripts/gmail_api.py beside this file, loaded only for --inbox. Importing it sends nothing."""
    here = str(Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    import gmail_api                                               # noqa: WPS433  (deliberately lazy)
    return gmail_api


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read-only ledger view of an outbox manifest (never sends).")
    ap.add_argument("manifest", help="outbox manifest .json; sent.json is read from the same folder when present")
    ap.add_argument("--inbox", action="store_true", help="also look for inbound replies (read-only Gmail list/get)")
    ap.add_argument("--days", type=int, default=14, help="reply window in days for --inbox (default 14)")
    a = ap.parse_args(argv)
    manifest_path = Path(a.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sent_path = manifest_path.with_name("sent.json")
    sent = json.loads(sent_path.read_text(encoding="utf-8")) if sent_path.exists() else {}
    rows = build_rows(manifest, sent)

    token = call = None
    tok_err = ""
    if a.inbox:
        gm = _gmail()
        try:
            token, call = gm.access_token(), gm.call
        except (Exception, SystemExit) as e:
            tok_err = _short(e)

    kw = min(max([3] + [len(r["key"]) for r in rows]), 40)
    print(f"{'key':<{kw}} | rcpts | {'sent':<16} | bcc | subject")
    for e, r in zip(manifest, rows):
        bcc = "-" if r["bcc_count"] is None else str(r["bcc_count"])
        print(f"{r['key'][:kw]:<{kw}} | {r['recipients']:>5} | {r['sent']:<16} | {bcc:>3} | {r['subject']}")
        if a.inbox:
            res = {"error": tok_err} if tok_err else check_inbox(e, a.days, token, call)
            print(" " * 4 + format_inbox(res, max(1, a.days)))
    print(summary(rows) + ("" if sent_path.exists() else f"  (no {sent_path.name} beside the manifest)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
