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
import urllib.parse
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


# ---------------------------------------------------------------- --skip-list: pure pieces
print("--skip-list pure pieces")
check("bounce_query: mailer-daemon, window, quoted bare lower-case address",
      st.bounce_query("Sparky <Sparky@Gmail.com>", 7) == 'from:mailer-daemon newer_than:7d "sparky@gmail.com"', st.bounce_query("Sparky <Sparky@Gmail.com>", 7))
check("bounce_query default window 14d, floor 1d",
      'newer_than:14d "a@b.com"' in st.bounce_query("a@b.com") and "newer_than:1d" in st.bounce_query("a@b.com", 0))
SKIP_MANIFEST = MANIFEST + [{"key": "shared", "subject": "same domain as mixed", "to": ["Sales <SALES@hoodz.us.com>"],
                             "cc": ["Larry.Moss@hoodz.us.com"], "body_file": "e.txt", "files": []}]
ALL = st.all_recipients(SKIP_MANIFEST)
check("all_recipients: bare, lower-cased, de-duplicated across entries and to/cc/bcc, sorted",
      ALL == sorted(ALL) and len(ALL) == 10 and "larry.moss@hoodz.us.com" in ALL and "sales@hoodz.us.com" in ALL
      and not any("<" in a or a != a.lower() for a in ALL), ALL)
check("all_recipients ignores malformed input", st.all_recipients(None) == [] and st.all_recipients([None, {"to": "x"}, {"to": ["no-at"]}]) == [])
check("reply_term: domain for business, address for free-mail, '' for junk",
      st.reply_term("Larry <larry.moss@hoodz.us.com>") == "hoodz.us.com" and st.reply_term("Redwing@Comcast.net") == "redwing@comcast.net"
      and st.reply_term("nope") == "")

# ---------------------------------------------------------------- --skip-list: decide_skips with a fake Gmail (no network)
print("--skip-list decide_skips (faked Gmail)")
REPLY_MS = int(dt.datetime(2026, 11, 14, 15, 0, tzinfo=dt.timezone.utc).timestamp() * 1000)     # 2026-11-14
REDWING_MS = int(dt.datetime(2026, 11, 13, 9, 0, tzinfo=dt.timezone.utc).timestamp() * 1000)    # 2026-11-13


class FakeSkipGmail:
    """Stands in for scripts/gmail_api in --skip-list mode: hoodz.us.com replied (2026-11-14); sparky@gmail.com bounced
    (date only in the Date header: 2026-11-15); redwing@comcast.net replied (2026-11-13) AND bounced; broken.example raises on
    its reply term (when broken=True); everything else is silent. Records every call, never touches the network."""

    def __init__(self, broken=True):
        self.broken = broken
        self.calls = []

    def access_token(self):
        return "tok-s"

    def call(self, method, path, token, body=None, ctype="application/json"):
        self.calls.append((method, path, token))
        assert method == "GET", f"outbox_status must only GET, saw {method}"
        if path.startswith(st.LIST_PATH):
            q = urllib.parse.unquote(path[len(st.LIST_PATH):])
            if q.startswith("from:mailer-daemon"):
                if '"sparky@gmail.com"' in q:
                    return {"messages": [{"id": "b-sparky", "threadId": "tb1"}]}
                if '"redwing@comcast.net"' in q:
                    return {"messages": [{"id": "b-redwing", "threadId": "tb2"}]}
                return {"resultSizeEstimate": 0}
            if self.broken and q.startswith("from:broken.example "):
                raise SystemExit("Gmail API 403 on GET /gmail/v1/users/me/messages: forbidden")
            if q.startswith("from:hoodz.us.com "):
                return {"messages": [{"id": "r-hoodz", "threadId": "tr1"}, {"id": "r-hoodz-old", "threadId": "tr1"}]}
            if q.startswith("from:redwing@comcast.net "):
                return {"messages": [{"id": "r-redwing", "threadId": "tr2"}]}
            return {"resultSizeEstimate": 0}
        if "/messages/r-hoodz?format=metadata" in path:
            return {"id": "r-hoodz", "internalDate": str(REPLY_MS),
                    "payload": {"headers": [{"name": "From", "value": "Larry Moss <larry.moss@hoodz.us.com>"}, {"name": "Subject", "value": "Re: hood"}]}}
        if "/messages/r-redwing?format=metadata" in path:
            return {"id": "r-redwing", "internalDate": str(REDWING_MS), "payload": {"headers": []}}
        if "/messages/b-sparky?format=metadata" in path:                                       # no internalDate: Date header decides
            return {"id": "b-sparky", "payload": {"headers": [{"name": "From", "value": "Mail Delivery Subsystem <mailer-daemon@googlemail.com>"},
                                                               {"name": "Date", "value": "Sun, 15 Nov 2026 10:40:00 -0700"}]}}   # 17:40Z, UTC day 11-15
        if "/messages/b-redwing?format=metadata" in path:
            return {"id": "b-redwing", "internalDate": str(REPLY_MS + 86400000), "payload": {"headers": []}}       # 2026-11-15
        raise AssertionError(f"unexpected path {path}")


fake = FakeSkipGmail()
LOG = []
res = st.decide_skips(SKIP_MANIFEST, 7, fake.call, "tok-s", log=LOG.append)
check("decide_skips returns exactly days/skip/reasons/checked/errors", set(res) == {"days", "skip", "reasons", "checked", "errors"}, res)
check("days and checked", res["days"] == 7 and res["checked"] == 10, res)
check("a reply from a business domain skips every address at that domain, dated from internalDate",
      {"larry.moss@hoodz.us.com", "carlos.ahedo@hoodz.us.com", "sales@hoodz.us.com"} <= set(res["skip"])
      and res["reasons"]["larry.moss@hoodz.us.com"] == "replied 2026-11-14" and res["reasons"]["sales@hoodz.us.com"] == "replied 2026-11-14", res)
check("a mailer-daemon hit skips the gmail address, dated from the Date header when internalDate is missing",
      "sparky@gmail.com" in res["skip"] and res["reasons"]["sparky@gmail.com"] == "bounced 2026-11-15", res["reasons"])
check("replied and bounced both: replied+bounced with both dates",
      res["reasons"]["redwing@comcast.net"] == "replied+bounced 2026-11-13 2026-11-15", res["reasons"])
check("silent addresses are kept",
      not ({"info@chemaqua.com", "info@h2oeng.com", "sales@rkindustries.com", "contact@coloradomech.com"} & set(res["skip"])), res["skip"])
check("skip list is sorted, every skip has a reason, no reason without a skip",
      res["skip"] == sorted(res["skip"]) and set(res["skip"]) == set(res["reasons"]), res)
check("the failing term lands in errors and the run goes on; its address is kept (bounce check was clean)",
      list(res["errors"]) == ["from:broken.example"] and res["errors"]["from:broken.example"].startswith("Gmail API 403")
      and "ops@broken.example" not in res["skip"], res["errors"])
lists = [urllib.parse.unquote(p[len(st.LIST_PATH):]) for m, p, _ in fake.calls if p.startswith(st.LIST_PATH)]
check("one messages.list per distinct term: shared hoodz.us.com asked once for three addresses",
      sum(1 for q in lists if q.startswith("from:hoodz.us.com ")) == 1, lists)
check("8 reply terms + 10 bounce terms = 18 lists, no repeats",
      len(lists) == 18 and len(set(lists)) == 18 and sum(1 for q in lists if q.startswith("from:mailer-daemon")) == 10, lists)
check("reply searches reuse the reply_query shape (window, -from:luke)",
      all("newer_than:7d" in q and "-from:luke@brownbisonco.com" in q for q in lists if not q.startswith("from:mailer-daemon")), lists)
check("bounce searches quote the address and carry the window",
      all('"' in q and "newer_than:7d" in q and "-from:" not in q for q in lists if q.startswith("from:mailer-daemon")), lists)
gets = [p for m, p, _ in fake.calls if "format=metadata" in p]
check("one messages.get per term with a hit (newest only), format=metadata, token passed",
      len(gets) == 4 and not any("r-hoodz-old" in p for p in gets) and all(t == "tok-s" for _, _, t in fake.calls), gets)
check("only GET calls with the /gmail/v1 prefix", all(m == "GET" and p.startswith("/gmail/v1/users/me/messages") for m, p, _ in fake.calls))
check("progress lines go through log", LOG and LOG[0].startswith("skip-list: 10 addresses") and any("error on from:broken.example" in l for l in LOG), LOG)
clean = FakeSkipGmail(broken=False)
check("no failing term -> empty errors", st.decide_skips(SKIP_MANIFEST, 7, clean.call, "tok-s")["errors"] == {})
check("an exception that is not SystemExit is also caught",
      st.decide_skips([{"key": "k", "to": ["a@b.com"]}], 14, _boom, "t") == {"days": 14, "skip": [], "reasons": {}, "checked": 1,
                                                                             "errors": {"from:b.com": "connection refused", "bounce:a@b.com": "connection refused"}})
check("empty manifest -> nothing checked, no call", st.decide_skips([], 14, _boom, "t")["checked"] == 0)

# ---------------------------------------------------------------- --skip-list: apply_skips
print("--skip-list apply_skips")
before = json.dumps(SKIP_MANIFEST, sort_keys=True)
new, dropped = st.apply_skips(SKIP_MANIFEST, res["skip"] + ["INFO@chemaqua.com"])
check("input manifest unchanged", json.dumps(SKIP_MANIFEST, sort_keys=True) == before)
check("new entries are copies, not the same objects", all(n is not e for n in new for e in SKIP_MANIFEST))
nb = {e["key"]: e for e in new}
check("entry emptied of to and bcc is dropped and listed (mixed: all four skipped); shared (to+cc all skipped) too",
      dropped == ["mixed", "shared"] and "mixed" not in nb and "shared" not in nb, (dropped, list(nb)))
check("bcc trimmed case-insensitively, entry kept", nb["bcc-only"]["bcc"] == ["info@h2oeng.com", "sales@rkindustries.com"], nb["bcc-only"])
check("untouched entries keep every field", nb["unsent-one"] == MANIFEST[2] and nb["broken"] == MANIFEST[3])
check("manifest order preserved", [e["key"] for e in new] == ["bcc-only", "unsent-one", "broken"])
new2, dropped2 = st.apply_skips([{"key": "cc-only-left", "to": ["a@x.com"], "cc": ["keep@y.com"], "body_file": "f"}], ["a@x.com"])
check("an entry left with only cc is dropped (nothing to send to)", new2 == [] and dropped2 == ["cc-only-left"])
new3, _ = st.apply_skips([{"key": "k", "to": ["Name <A@X.com>", "b@x.com"], "cc": ["c@y.com"], "body_file": "f", "thread": "t1", "files": ["p.pdf"]}], ["a@x.com"])
check("'Name <addr>' entries match by bare address; emptied lists are removed; other fields survive",
      new3 == [{"key": "k", "to": ["b@x.com"], "cc": ["c@y.com"], "body_file": "f", "thread": "t1", "files": ["p.pdf"]}], new3)
check("non-dict entries pass through", st.apply_skips([None, "x"], ["a@b.c"]) == ([None, "x"], []))

# reply_thread entries (in-thread answers / follow-up questions to someone who wrote to us) are exempt: never pruned, never dropped
print("--skip-list apply_skips: reply_thread exempt")
EXEMPT_REPLY = {"key": "reply-hoodz", "subject": "Re: hood cleaning: one more question", "to": ["Larry Moss <larry.moss@hoodz.us.com>"],
                "cc": ["carlos.ahedo@hoodz.us.com"], "body_file": "g.txt", "files": [], "thread": "1a1a878f8cda76a3", "reply_thread": True}
EXEMPT_BOUNCE = {"key": "reply-sparky", "subject": "Re: generator pricing", "to": ["sparky@gmail.com", "redwing@comcast.net"],
                 "body_file": "h.txt", "files": [], "thread": "t9", "reply_thread": True}
NOT_EXEMPT = {"key": "chase-hoodz", "subject": "chase of silence, same people", "to": ["larry.moss@hoodz.us.com"],
              "cc": ["carlos.ahedo@hoodz.us.com"], "body_file": "i.txt", "files": [], "thread": "1a1a878f8cda76a3"}
FALSE_FLAG = dict(NOT_EXEMPT, key="flag-false", reply_thread=False)
EXEMPT_MANIFEST = SKIP_MANIFEST + [EXEMPT_REPLY, EXEMPT_BOUNCE, NOT_EXEMPT, FALSE_FLAG]
before_x = json.dumps(EXEMPT_MANIFEST, sort_keys=True)
newx, droppedx = st.apply_skips(EXEMPT_MANIFEST, res["skip"] + ["INFO@chemaqua.com"])   # res: hoodz replied, sparky bounced, redwing both
nbx = {e["key"]: e for e in newx}
check("exempt entry keeps every skipped recipient and every other field, and is not dropped",
      nbx["reply-hoodz"] == EXEMPT_REPLY and nbx["reply-sparky"] == EXEMPT_BOUNCE and "reply-hoodz" not in droppedx
      and "reply-sparky" not in droppedx, (droppedx, nbx.get("reply-hoodz")))
check("exempt entries are deep copies, input unchanged",
      nbx["reply-hoodz"] is not EXEMPT_REPLY and nbx["reply-hoodz"]["to"] is not EXEMPT_REPLY["to"]
      and json.dumps(EXEMPT_MANIFEST, sort_keys=True) == before_x)
check("a chase to the same people without the flag is still pruned and dropped; 'reply_thread': false counts as no flag",
      droppedx == ["mixed", "shared", "chase-hoodz", "flag-false"] and "chase-hoodz" not in nbx and "flag-false" not in nbx, droppedx)
check("non-exempt entries behave exactly as before alongside exempt ones",
      nbx["bcc-only"]["bcc"] == ["info@h2oeng.com", "sales@rkindustries.com"] and nbx["unsent-one"] == MANIFEST[2]
      and [e["key"] for e in newx] == ["bcc-only", "unsent-one", "broken", "reply-hoodz", "reply-sparky"], [e["key"] for e in newx])
check("a partly skipped exempt entry is left whole (no list trimmed)",
      st.apply_skips([{"key": "k", "to": ["a@x.com", "b@x.com"], "reply_thread": True}], ["a@x.com"])
      == ([{"key": "k", "to": ["a@x.com", "b@x.com"], "reply_thread": True}], []))
check("is_reply_thread: only the JSON literal true counts",
      st.is_reply_thread(EXEMPT_REPLY) and not st.is_reply_thread(NOT_EXEMPT) and not st.is_reply_thread(FALSE_FLAG)
      and not st.is_reply_thread({"reply_thread": "true"}) and not st.is_reply_thread({"reply_thread": 1}) and not st.is_reply_thread(None))
check("exempt_keys: sorted keys of flagged entries, [] when none, malformed input ignored",
      st.exempt_keys(EXEMPT_MANIFEST) == ["reply-hoodz", "reply-sparky"] and st.exempt_keys(SKIP_MANIFEST) == []
      and st.exempt_keys(None) == [] and st.exempt_keys([None, {"reply_thread": True}]) == ["?"], st.exempt_keys(EXEMPT_MANIFEST))
check("exempt_bounced: bounced addresses on exempt entries only (replied-only exempt entry absent; non-exempt bounced entry absent)",
      st.exempt_bounced(EXEMPT_MANIFEST, res["reasons"]) == {"reply-sparky": ["redwing@comcast.net", "sparky@gmail.com"]},
      st.exempt_bounced(EXEMPT_MANIFEST, res["reasons"]))
check("exempt_bounced: {} with no exempt entries or no reasons",
      st.exempt_bounced(SKIP_MANIFEST, res["reasons"]) == {} and st.exempt_bounced(EXEMPT_MANIFEST, {}) == {} and st.exempt_bounced(None, None) == {})

# ---------------------------------------------------------------- --skip-list: the send copy never lands under ops/
print("--skip-list send copy path")
check("relative ops/ path refused", "tracked files" in st.send_copy_problem("ops/outbox/2026-11-16/send.json"))
check("absolute path under the repo's ops/ refused", st.send_copy_problem(str(ROOT / "ops" / "outbox" / "x" / "send.json")) != "")
check("the ops/ folder itself refused", st.send_copy_problem(str(ROOT / "ops")) != "")
check("scratchpad-style path accepted", st.send_copy_problem(str(TMP / "mon" / "send.json")) == "", st.send_copy_problem(str(TMP / "mon" / "send.json")))
check("the input manifest itself refused", "overwrite" in st.send_copy_problem(str(TMP / "outbox.json"), TMP / "outbox.json"))
check("a directory refused", "directory" in st.send_copy_problem(str(TMP)))
check("a sub-folder merely named ops outside the repo is fine", st.send_copy_problem(str(TMP / "ops" / "send.json")) == "")


def run_main2(argv):
    """Like run_main but also captures stderr and turns a SystemExit into its code."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = st.main(argv)
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue(), err.getvalue()


# ---------------------------------------------------------------- --skip-list end to end (faked Gmail)
print("--skip-list main")
(TMP / "skip.json").write_text(json.dumps(SKIP_MANIFEST, indent=1))
skip_bytes = (TMP / "skip.json").read_bytes()
st._gmail = lambda: FakeSkipGmail(broken=False)
try:
    rc, out, err = run_main2([str(TMP / "skip.json"), "--skip-list", "--days", "7"])
finally:
    st._gmail = _orig_gmail
doc = json.loads(out)                                                                             # the whole of stdout is one JSON object
SKIP_KEYS = {"days", "skip", "reasons", "checked", "errors", "exempt_entries", "exempt_bounced"}
check("--skip-list: exit 0, stdout is exactly one JSON object with exactly days/skip/reasons/checked/errors/exempt_entries/exempt_bounced",
      rc == 0 and set(doc) == SKIP_KEYS, (rc, list(doc)))
check("--skip-list JSON content", doc["days"] == 7 and doc["checked"] == 10 and doc["errors"] == {}
      and doc["skip"] == sorted(doc["skip"]) and doc["reasons"]["sparky@gmail.com"] == "bounced 2026-11-15", doc)
check("no reply_thread entries -> exempt_entries [] and exempt_bounced {}", doc["exempt_entries"] == [] and doc["exempt_bounced"] == {}, doc)
check("no ledger table or summary on stdout in --skip-list mode", "rcpts" not in out and "entries," not in out)
check("progress went to stderr", "skip-list: 10 addresses" in err, err)

SEND_COPY = TMP / "mon" / "send-copy.json"
st._gmail = lambda: FakeSkipGmail(broken=True)
try:
    rc, out, err = run_main2([str(TMP / "skip.json"), "--skip-list", "--write-send-copy", str(SEND_COPY)])
finally:
    st._gmail = _orig_gmail
doc = json.loads(out)
check("--write-send-copy: JSON adds dropped_entries, exit 1 because one term errored, still parseable",
      rc == 1 and set(doc) == SKIP_KEYS | {"dropped_entries"} and doc["days"] == 14
      and doc["dropped_entries"] == ["mixed", "shared"] and list(doc["errors"]) == ["from:broken.example"], (rc, doc))
check("exit-1 reason on stderr", "may be incomplete" in err, err)
copy_doc = json.loads(SEND_COPY.read_text())
check("send copy written (parent folder created) with the skip addresses gone and emptied entries dropped",
      [e["key"] for e in copy_doc] == ["bcc-only", "unsent-one", "broken"] and not any(a in json.dumps(copy_doc).lower() for a in doc["skip"]), copy_doc)
check("send copy keeps body_file/files/thread for the sender", all("body_file" in e and "files" in e for e in copy_doc))
check("input manifest file byte-identical after --write-send-copy", (TMP / "skip.json").read_bytes() == skip_bytes)

# the CLI with reply_thread entries: the live 2026-11-16 case (an in-thread follow-up whose domain had written back was dropped)
print("--skip-list main: reply_thread exempt")
(TMP / "exempt.json").write_text(json.dumps(EXEMPT_MANIFEST, indent=1))
EXEMPT_COPY = TMP / "mon" / "exempt-copy.json"
st._gmail = lambda: FakeSkipGmail(broken=False)
try:
    rc, out, err = run_main2([str(TMP / "exempt.json"), "--skip-list", "--days", "7", "--write-send-copy", str(EXEMPT_COPY)])
finally:
    st._gmail = _orig_gmail
doc = json.loads(out)
check("exempt_entries lists the reply_thread keys, sorted, in the --skip-list JSON; nothing else changes shape",
      rc == 0 and doc["exempt_entries"] == ["reply-hoodz", "reply-sparky"] and set(doc) == SKIP_KEYS | {"dropped_entries"}, (rc, doc))
check("exempt_bounced lists the bounced address(es) on an exempt entry, keyed by entry; replied-only exempt entry absent",
      doc["exempt_bounced"] == {"reply-sparky": ["redwing@comcast.net", "sparky@gmail.com"]}, doc["exempt_bounced"])
check("the skip list itself still names those addresses (decide_skips unchanged); exempt entries are not in dropped_entries",
      {"larry.moss@hoodz.us.com", "sparky@gmail.com", "redwing@comcast.net"} <= set(doc["skip"]) and doc["checked"] == 10
      and doc["dropped_entries"] == ["mixed", "shared", "chase-hoodz", "flag-false"], doc)
copy_x = json.loads(EXEMPT_COPY.read_text())
cbx = {e["key"]: e for e in copy_x}
check("send copy keeps the exempt entries whole (recipients, thread, flag) while the same addresses are gone from every other entry",
      [e["key"] for e in copy_x] == ["bcc-only", "unsent-one", "broken", "reply-hoodz", "reply-sparky"]
      and cbx["reply-hoodz"] == EXEMPT_REPLY and cbx["reply-sparky"] == EXEMPT_BOUNCE
      and not any("hoodz.us.com" in a or "sparky@" in a for e in copy_x if e["key"] not in ("reply-hoodz", "reply-sparky") for a in st.recipients(e)),
      copy_x)
check("stderr counts the exempt entries", "2 exempt reply-thread entries untouched" in err, err)

# refusals happen before any Gmail work
st._gmail = _NoGmail()
try:
    rc, out, err = run_main2([str(TMP / "skip.json"), "--skip-list", "--write-send-copy", "ops/outbox/2026-11-16/send.json"])
    rc2, out2, err2 = run_main2([str(TMP / "skip.json"), "--write-send-copy", str(TMP / "x.json")])
finally:
    st._gmail = _orig_gmail
check("--write-send-copy under ops/: exit 2, message on stderr, nothing on stdout, Gmail never loaded, nothing written",
      rc == 2 and out == "" and "tracked files" in err and not (ROOT / "ops" / "outbox" / "2026-11-16" / "send.json").exists(), (rc, out, err))
check("--write-send-copy without --skip-list: argparse error, exit 2", rc2 == 2 and out2 == "" and "needs --skip-list" in err2, (rc2, err2))
st._gmail = lambda: NoToken()
try:
    rc, out, err = run_main2([str(TMP / "skip.json"), "--skip-list", "--write-send-copy", str(TMP / "mon" / "never.json")])
finally:
    st._gmail = _orig_gmail
check("no Gmail token in --skip-list mode: exit 1, empty stdout (no misleading empty skip list), no send copy written",
      rc == 1 and out == "" and "no Gmail token" in err and not (TMP / "mon" / "never.json").exists(), (rc, out, err))

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
