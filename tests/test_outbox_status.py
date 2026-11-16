#!/usr/bin/env python3
"""Offline tests for scripts/outbox_status.py (the read-only outbox ledger). Run: python3 tests/test_outbox_status.py

No network and nothing can send: the default path never loads gmail_api (a stand-in that raises proves it), and the --inbox path
runs with the Gmail module replaced by a fake that records every call, answers canned JSON, and fails one entry on purpose.
Plain asserts via check(); prints "N passed, M failed" and exits non-zero on any failure (same shape as tests/test_bidwatch.py).
"""
from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import outbox_status as st  # noqa: E402

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name} {detail}")


def run_main(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = st.main(argv)
    return rc, buf.getvalue()


# ---------------------------------------------------------------- fixture: a temp manifest + sent.json
TMP = Path(tempfile.mkdtemp(prefix="outbox-status-test-"))
LONG_SUBJECT = "CDOC Buena Vista boiler chemical treatment (DQ 2027000132): technician for Wednesday's mandatory walk"
MANIFEST = [
    {"key": "mixed", "subject": "Re: hood cleaning site visit", "to": ["Larry Moss <larry.moss@hoodz.us.com>"],
     "cc": ["carlos.ahedo@hoodz.us.com"], "bcc": ["sparky@gmail.com", "redwing@comcast.net"], "body_file": "a.txt", "files": [],
     "thread": "1a1a878f8cda76a3"},
    {"key": "bcc-only", "subject": LONG_SUBJECT, "bcc": ["info@chemaqua.com", "info@h2oeng.com", "sales@rkindustries.com"],
     "body_file": "b.txt", "files": []},
    {"key": "unsent-one", "subject": "Canon City RFP 129-26: will you price it?", "to": ["contact@coloradomech.com"],
     "body_file": "c.txt", "files": ["x.pdf"]},
    {"key": "broken", "subject": "forces an API error", "to": ["ops@broken.example"], "body_file": "d.txt", "files": []},
]
SENT = {
    "mixed": {"id": "1a1d5a22bbc07c56", "threadId": "1a1a878f8cda76a3", "to": ["larry.moss@hoodz.us.com"], "bcc_count": 2, "attachments": []},
    "bcc-only": {"id": "1a1d5a24d06ac325", "threadId": "1a1d5a24d06ac325", "to": [], "bcc_count": 3, "attachments": ["DQ.pdf"]},
}
(TMP / "outbox.json").write_text(json.dumps(MANIFEST))
(TMP / "sent.json").write_text(json.dumps(SENT))

# ---------------------------------------------------------------- rows
print("rows")
rows = st.build_rows(MANIFEST, SENT)
by = {r["key"]: r for r in rows}
check("one row per entry, in manifest order", [r["key"] for r in rows] == ["mixed", "bcc-only", "unsent-one", "broken"], rows)
check("sent entry shows its Gmail id", by["mixed"]["sent"] == "1a1d5a22bbc07c56", by["mixed"])
check("unsent entry shows 'not sent'", by["unsent-one"]["sent"] == "not sent" and by["broken"]["sent"] == "not sent")
check("bcc_count comes from sent.json", by["mixed"]["bcc_count"] == 2 and by["bcc-only"]["bcc_count"] == 3)
check("bcc_count is None when not sent", by["unsent-one"]["bcc_count"] is None)
check("recipients counted across to+cc+bcc", by["mixed"]["recipients"] == 4, by["mixed"])
check("recipients counted for bcc-only", by["bcc-only"]["recipients"] == 3)
check("recipients counted for to-only", by["unsent-one"]["recipients"] == 1)
check("subject truncated to 60 chars", len(by["bcc-only"]["subject"]) == 60 and by["bcc-only"]["subject"].endswith("..."), by["bcc-only"])
check("short subject kept whole", by["mixed"]["subject"] == "Re: hood cleaning site visit")
check("summary line", st.summary(rows) == "4 entries, 2 sent, 2 unsent", st.summary(rows))
check("malformed entries do not crash build_rows",
      st.build_rows([None, {"to": "not-a-list"}, {"key": "k", "to": ["a@b.c"]}], {})[2]["recipients"] == 1
      and st.build_rows([None], {})[0]["key"] == "?" and st.build_rows([None], {})[0]["recipients"] == 0)
check("no sent.json -> everything 'not sent'", all(r["sent"] == "not sent" for r in st.build_rows(MANIFEST, {})))

# ---------------------------------------------------------------- reply_query
print("reply_query")
q = st.reply_query(MANIFEST[0])
check("business addresses become their domain (once)", q.count("from:hoodz.us.com") == 1 and "larry.moss@" not in q, q)
check("gmail.com keeps the full address", "from:sparky@gmail.com" in q and "from:gmail.com" not in q, q)
check("comcast.net keeps the full address", "from:redwing@comcast.net" in q and "from:comcast.net" not in q, q)
check("default window newer_than:14d", "newer_than:14d" in q, q)
check("excludes Luke's own mail", "-from:luke@brownbisonco.com" in q, q)
check("several senders are OR-ed in parentheses", q.startswith("(from:") and " OR " in q and ")" in q, q)
q7 = st.reply_query(MANIFEST[2], days=7)
check("--days changes the window", "newer_than:7d" in q7, q7)
check("single sender has no parentheses", q7.startswith("from:coloradomech.com "), q7)
free = {"key": "f", "to": ["A@Yahoo.com", "b@hotmail.com", "c@outlook.com", "d@Acme.COM", "e@acme.com"]}
check("yahoo/hotmail/outlook use the address; case folded; business domain de-duplicated",
      st.reply_terms(free) == ["a@yahoo.com", "b@hotmail.com", "c@outlook.com", "acme.com"], st.reply_terms(free))
check("no recipients -> empty query", st.reply_query({"key": "none", "subject": "x"}) == "")
check("days below 1 floor to 1", "newer_than:1d" in st.reply_query(MANIFEST[2], days=0))
check("sender_domain prints the domain only",
      st.sender_domain("Larry Moss <larry.moss@hoodz.us.com>") == "hoodz.us.com" and st.sender_domain("no-address") == "?")
check("recipients() parses 'Name <addr>' entries into terms", "hoodz.us.com" in st.reply_terms(MANIFEST[0]))

# ---------------------------------------------------------------- default path: no Gmail module loaded, no network
print("default path")


class _NoGmail:
    def __call__(self):
        raise AssertionError("gmail_api must not be loaded without --inbox")


_orig_gmail = st._gmail
st._gmail = _NoGmail()
try:
    rc, out = run_main([str(TMP / "outbox.json")])
finally:
    st._gmail = _orig_gmail
lines = out.splitlines()
check("exit 0 and header row", rc == 0 and lines[0].startswith("key") and "| rcpts |" in lines[0] and "| subject" in lines[0], lines[:1])
check("table rows carry key, count, id, bcc, subject",
      re.search(r"^mixed\s+\|\s+4 \| 1a1d5a22bbc07c56 \|\s+2 \| Re: hood cleaning site visit$", out, re.M) is not None, out)
check("unsent row says 'not sent' with '-' bcc", re.search(r"^unsent-one\s+\|\s+1 \| not sent\s+\|\s+- \| Canon City", out, re.M) is not None, out)
check("summary printed last", lines[-1] == "4 entries, 2 sent, 2 unsent", lines[-1])
check("no inbox lines without --inbox", "inbox:" not in out)

# a manifest with no sent.json beside it
ALONE = TMP / "alone"
ALONE.mkdir()
(ALONE / "m.json").write_text(json.dumps(MANIFEST[:2]))
rc, out = run_main([str(ALONE / "m.json")])
check("missing sent.json: all rows 'not sent' and the summary says so",
      out.count("not sent") == 2 and "2 entries, 0 sent, 2 unsent" in out and "no sent.json" in out, out)

# ---------------------------------------------------------------- --inbox path with Gmail faked (no network)
print("--inbox path (faked Gmail)")
CALLS = []
TOKENS = []
NEWEST_MS = int(dt.datetime(2026, 11, 16, 12, 3, tzinfo=dt.timezone.utc).timestamp() * 1000)   # 2026-11-16 12:03Z


class FakeGmail:
    """Stands in for scripts/gmail_api: records every call, answers canned JSON, never touches the network."""

    def access_token(self):
        TOKENS.append("tok-1")
        return "tok-1"

    def call(self, method, path, token, body=None, ctype="application/json"):
        CALLS.append((method, path, token, body))
        assert method == "GET", f"outbox_status must only GET, saw {method}"
        if path.startswith(st.LIST_PATH):
            q = path[len(st.LIST_PATH):]
            if "broken.example" in q:
                raise SystemExit("Gmail API 403 on GET /gmail/v1/users/me/messages: forbidden")   # what gmail_api.call() does
            if "hoodz.us.com" in q:                                      # only the first entry has replies
                return {"messages": [{"id": "m-new", "threadId": "t1"}, {"id": "m-old", "threadId": "t1"}], "resultSizeEstimate": 2}
            return {"resultSizeEstimate": 0}
        if path.startswith("/gmail/v1/users/me/messages/m-new?format=metadata"):
            return {"id": "m-new", "threadId": "t1", "internalDate": str(NEWEST_MS),
                    "payload": {"headers": [{"name": "From", "value": "Larry Moss <larry.moss@hoodz.us.com>"},
                                            {"name": "Subject", "value": "Re: Kitchen hood cleaning subcontract: Poudre School District site visit Tuesday 1:30 PM"},
                                            {"name": "Date", "value": "Mon, 16 Nov 2026 05:03:00 -0700"}]}}
        raise AssertionError(f"unexpected path {path}")


st._gmail = lambda: FakeGmail()
try:
    rc, out = run_main([str(TMP / "outbox.json"), "--inbox", "--days", "7"])
finally:
    st._gmail = _orig_gmail
lines = out.splitlines()
check("exit 0 with --inbox", rc == 0)
check("token fetched once", TOKENS == ["tok-1"], TOKENS)
check("only GET calls, with the /gmail/v1 prefix and the token",
      all(m == "GET" and p.startswith("/gmail/v1/users/me/messages") and t == "tok-1" for m, p, t, _ in CALLS), CALLS)
check("no POST and nothing on a send endpoint", not any(m == "POST" or p.rstrip("?").split("?")[0].endswith("send") for m, p, _, _ in CALLS))
lists = [p for _, p, _, _ in CALLS if p.startswith(st.LIST_PATH)]
check("one messages.list per entry with a recipient, query URL-quoted with the 7-day window",
      len(lists) == 4 and all("newer_than%3A7d" in p and "-from%3Aluke%40brownbisonco.com" in p for p in lists), lists)
check("messages.get only for the newest hit, format=metadata with From/Subject/Date",
      [p for _, p, _, _ in CALLS if "m-new" in p] == [st.GET_PATH.format(id="m-new")]
      and "metadataHeaders=From" in st.GET_PATH and "metadataHeaders=Subject" in st.GET_PATH and "metadataHeaders=Date" in st.GET_PATH
      and not any("m-old" in p for _, p, _, _ in CALLS), CALLS)
inbox_lines = [l.strip() for l in lines if l.strip().startswith("inbox:")]
check("one inbox line per entry, indented under its row", len(inbox_lines) == 4 and all(l.startswith("    inbox:") for l in lines if "inbox:" in l), lines)
check("count, date and sender domain for the entry with replies",
      inbox_lines[0].startswith("inbox: 2 inbound in 7d; newest 2026-11-16 12:03Z from hoodz.us.com: Re: Kitchen hood"), inbox_lines[0])
check("the sender's mailbox is never printed", "larry.moss@" not in out and "larry.moss" not in out, out)
check("newest subject truncated to 60 chars", len(inbox_lines[0].split(": ", 2)[-1].split("hoodz.us.com: ", 1)[-1]) <= 60, inbox_lines[0])
check("entries with no replies: 0 inbound", inbox_lines[1] == inbox_lines[2] == "inbox: 0 inbound in 7d", inbox_lines[1:3])
check("API error on one entry is reported, not raised, and the run continues",
      inbox_lines[3].startswith("inbox: error Gmail API 403") and lines[-1] == "4 entries, 2 sent, 2 unsent", inbox_lines[3])

# pure check_inbox with an entry that has no recipients, and a raising stand-in
check("check_inbox: no recipients -> error dict, no call made",
      st.check_inbox({"key": "x"}, 14, "t", lambda *a, **k: (_ for _ in ()).throw(AssertionError("called"))) == {"error": "no recipients in entry"})


def _boom(*a, **k):
    raise OSError("connection refused")


check("check_inbox: a network exception becomes an error dict", st.check_inbox(MANIFEST[2], 14, "t", _boom) == {"error": "connection refused"})
check("format_inbox shows 40+ when Gmail has another page",
      st.format_inbox({"count": 40, "more": True, "newest": None}, 14) == "inbox: 40+ inbound in 14d")

# token failure (no GMAIL_* in the environment) is reported per entry, not raised
class NoToken(FakeGmail):
    def access_token(self):
        raise SystemExit("GMAIL_CLIENT_ID is not set. Add it in the cloud environment settings (never in chat or the repo).")


CALLS.clear()
st._gmail = lambda: NoToken()
try:
    rc, out = run_main([str(TMP / "outbox.json"), "--inbox"])
finally:
    st._gmail = _orig_gmail
check("token failure: table still prints, each entry says inbox: error, no API call made",
      rc == 0 and out.count("inbox: error GMAIL_CLIENT_ID is not set") == 4 and CALLS == [], out)

# ---------------------------------------------------------------- the source itself never sends
print("source")
src = (ROOT / "scripts" / "outbox_status.py").read_text(encoding="utf-8")
check("module docstring says read-only / never sends", "READ-ONLY" in src.split('"""')[1] and "never sends" in src.split('"""')[1])
check("source has no POST and no send/draft endpoint", "POST" not in src and "/send" not in src and "/drafts" not in src)

# ---------------------------------------------------------------- smoke on a real manifest when present (no --inbox, no network)
real = ROOT / "ops" / "outbox" / "2026-11-16" / "outbox-chases.json"
if real.exists():
    st._gmail = _NoGmail()
    try:
        rc, out = run_main([str(real)])
    finally:
        st._gmail = _orig_gmail
    check("real manifest renders with a summary line", rc == 0 and re.search(r"^\d+ entries, \d+ sent, \d+ unsent", out.splitlines()[-1]) is not None,
          out.splitlines()[-1:])

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
