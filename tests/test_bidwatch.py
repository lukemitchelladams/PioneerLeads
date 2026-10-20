#!/usr/bin/env python3
"""Offline tests for scripts/bidwatch. Run: python3 tests/test_bidwatch.py

Part 1: parsers (dates, pre-bid detection, BidNet listing/detail, Bonfire JSON/detail, SAM.gov records).
Part 2: a fake BidNet-style site on localhost with a real login form and cookie session, to prove that
        PortalSession logs in, saves the session, reuses it on the next run, and logs in again by itself
        after the server expires the session. Then a full scan() against the fake site.
Part 1b: trimmed copies of the REAL pages (tests/fixtures/, saved 2026-10-20 from the live sites):
        BidNet Colorado open-bids list + a public detail page, Bonfire Parker list JSON + the Cloudflare
        challenge its opportunity pages return to cloud IPs, DIBBS RFQ grid for FSC 3110.
"""
from __future__ import annotations

import http.server
import json
import os
import sys
import tempfile
import threading
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TMP = Path(tempfile.mkdtemp(prefix="bidwatch-test-"))
os.environ["BB_STATE_DIR"] = str(TMP / "state")

from scripts.bidwatch import bidnet, bonfire, common, samgov  # noqa: E402

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name} {detail}")


# ---------------------------------------------------------------- part 1: parsers
print("parsers")
check("parse_date m/d/y", common.parse_date("Closing 11/06/2026 02:00 PM") == "2026-11-06")
check("parse_date month name", common.parse_date("Oct 22nd 2026, 3:00PM MDT") == "2026-10-22")
check("parse_date iso", common.parse_date("due 2026-12-01") == "2026-12-01")

cdoc = ("4. SERVICE LOCATION AND MANDATORY SITE VISIT: Services will be performed at Trinidad Correctional "
        "Facility. Mandatory Site Visit - Time & Date: 10:00am, Wednesday, October 21, 2026. Bidders must attend.")
pb = common.extract_prebid(cdoc)
check("prebid mandatory detected", pb and pb["mandatory"] is True, pb)
check("prebid date", pb and pb["date"] == "2026-10-21", pb)
lit = "A pre-proposal meeting will be held 10/09/2026 at 10:00 AM via Teams. Attendance is not mandatory."
pb2 = common.extract_prebid(lit)
check("prebid optional detected", pb2 and pb2["mandatory"] is False and pb2["date"] == "2026-10-09", pb2)
check("no prebid in plain text", common.extract_prebid("Proposals due 10/28/2026 2:00 PM.") is None)

profiles = common.load_profiles()
check("profile match hvac", "brownbison" in common.match_profiles("Town of Parker HVAC Preventive Maintenance", profiles))
check("profile exclude excavation", common.match_profiles("Pond excavation and irrigation repair", profiles) == [])
check("street != trees", "brownbison" not in common.match_profiles("Street Sweeping Services", profiles))
check("jones bearing pulley", "jones-bearing" in common.match_profiles("PULLEY, GROOVE", profiles))

fixture = (ROOT / "bids/_watch/fixture-bidnet-sample.html").read_text()
rows, nxt = bidnet.parse_listing(fixture, "https://www.bidnetdirect.com/colorado/town-of-parker")
check("bidnet listing rows", len(rows) == 3, rows)
check("bidnet listing closing", rows and rows[0]["closing"] == "2026-11-06", rows[:1])
check("bidnet listing agency", rows and rows[0]["agency"] == "Town Of Parker", rows[:1])
check("bidnet awarded link skipped", all("awarded" not in r["url"] for r in rows))

detail_html = """<html><body><h1>On-Call Commercial Plumbing Services</h1>
<div>Publication Date 09/25/2026</div><div>Closing Date 10/28/2026 02:00 PM MDT</div>
<p>A non-mandatory pre-proposal meeting will be held October 9, 2026 at 10:00 AM on Teams.</p>
<p>Questions Deadline: 10/14/2026</p>
<a href="/docs/RFQ-2126.pdf">RFQ 2126.pdf</a><a href="/docs/Addendum-1.pdf">Addendum 1.pdf</a>
<a href="/somewhere">About us</a></body></html>"""
d = bidnet.parse_detail(detail_html, "https://www.bidnetdirect.com/x")
check("bidnet detail closing", d["closing"] == "2026-10-28", d)
check("bidnet detail questions", d["questions_due"] == "2026-10-14", d)
check("bidnet detail docs", [x["name"] for x in d["documents"]] == ["Addendum 1.pdf", "RFQ 2126.pdf"], d["documents"])
check("bidnet detail prebid optional", d["prebid"] and d["prebid"]["mandatory"] is False, d["prebid"])

bj = {"success": 1, "payload": {"projects": {"256465": {"ProjectID": 256465, "ProjectName": "Town of Parker HVAC Preventive Maintenance & Repair Services",
                                                       "ReferenceID": "26-028", "DateClose": "2026-10-22 15:00:00"}}}}
br = bonfire.parse_list_json(bj, "parkeronline")
check("bonfire json row", len(br) == 1 and br[0]["sol"] == "26-028" and br[0]["closing"] == "2026-10-22", br)
bd = bonfire.parse_detail("""<table><tr><td>Open Date</td><td>Oct 1st 2026, 3:00PM MDT</td></tr>
<tr><td>Questions Due Date</td><td>Oct 16th 2026, 10:00AM MDT</td></tr>
<tr><td>Mandatory Site Visit</td><td>Oct 12th 2026, 11:00AM MDT</td></tr>
<tr><td>Close Date</td><td>Oct 22nd 2026, 3:00PM MDT</td></tr></table><p>Ref. # 26-028</p>""")
check("bonfire detail close", bd["closing"] == "2026-10-22", bd)
check("bonfire detail mandatory walk", bd["prebid"] and bd["prebid"]["mandatory"] and bd["prebid"]["date"] == "2026-10-12", bd["prebid"])

sam = {"noticeId": "abc123", "title": "HVAC Preventive Maintenance, Fort Carson", "solicitationNumber": "W911RZ27Q0001",
       "fullParentPathName": "DEPT OF DEFENSE.DEPT OF THE ARMY", "type": "Presolicitation", "postedDate": "2026-10-18",
       "responseDeadLine": "2026-11-20T14:00:00-07:00", "naicsCode": "238220", "classificationCode": "J041",
       "placeOfPerformance": {"state": {"code": "CO"}, "city": {"name": "Fort Carson"}}, "uiLink": "https://sam.gov/opp/abc123/view",
       "resourceLinks": ["https://sam.gov/api/prod/opps/v3/opportunities/resources/files/x/download"]}
n = samgov.normalize(sam)
check("sam normalize", n["closing"] == "2026-11-20" and n["upcoming"] and n["state"] == "CO", n)
check("sam keep by naics", samgov._keep(n, profiles["brownbison"]))
check("sam drop unrelated", not samgov._keep(samgov.normalize({**sam, "title": "Actuarial services", "naicsCode": "524298",
                                                                     "classificationCode": "R499"}), profiles["brownbison"]))

# ---------------------------------------------------------------- part 1b: real-page fixtures
print("real-page fixtures (tests/fixtures, live 2026-10-20)")
import json as _json  # noqa: E402
FX = ROOT / "tests" / "fixtures"
rows, nxt = bidnet.parse_listing((FX / "bidnet_open_bids_co.html").read_text(), bidnet.CO_OPEN)
check("real bidnet list: 3 rows", len(rows) == 3, len(rows))
check("real bidnet list: id/title/dates", rows and rows[0]["id"] == "0000440693" and rows[0]["title"] == "DTD Freight Planning Support"
      and rows[0]["closing"] == "2026-11-10" and rows[0]["published"] == "2026-10-19", rows[:1])
check("real bidnet list: region -> state", rows and rows[0]["state"] == "CO", rows[:1])
check("real bidnet list: next page link", nxt == bidnet.BASE + "/colorado/solicitations/open-bids/page2", nxt)
check("real bidnet list: site total 400", bidnet.total_count((FX / "bidnet_open_bids_co.html").read_text()) == 400)
check("bidnet zero-result page = 0, not a parse failure",
      bidnet.total_count("<p>We can't find any current bids with your keywords. Get notified</p>") == 0)
check("bidnet robot-check page recognised", bool(bidnet.BOT_RX.search((FX / "bidnet_robot_check.html").read_text()))
      and not bidnet.parse_listing((FX / "bidnet_robot_check.html").read_text())[0])
_hl = ("<table><tr class='mets-table-row'><td><a class='solicitation-link' href='/colorado/solicitations/open-bids/x/0000438328'>"
       "<span class='iris-highlight'>On</span>-<span class='iris-highlight'>Call</span> Commercial Plumbing Services</a></td></tr></table>")
check("bidnet highlighted title not split", bidnet.parse_listing(_hl)[0][0]["title"] == "On-Call Commercial Plumbing Services",
      bidnet.parse_listing(_hl)[0])
_docs = ("<div id='docs'><table><tr><td><a class='mets-command-link' id='attachmentDownloadLnk_9747910258' "
         "href='/public/solicitations/9745843859/abstract/docs-items/9747910258/attachment-download'>"
         "Attachment A - Contract Certification Form.pdf</a></td><td>198 Kb</td></tr></table>"
         "<p>Items No Description UOM Qty 1 Non-Emergency Normal Business Hours Rate Hourly Rate 1</p>"
         "<p>There are no items associated with this solicitation.</p></div>")
_t = bidnet.parse_docs_tab(_docs, bidnet.BASE + "/colorado/solicitations/open-bids/x/0000438328")
check("logged-in Documents tab: attachment links (real markup, Littleton 2026-10-20)",
      len(_t["documents"]) == 1 and _t["documents"][0]["name"].startswith("Attachment A")
      and _t["documents"][0]["url"].endswith("/9747910258/attachment-download"), _t)
check("logged-in Documents tab: RMEPS pricing items captured", (_t["items_text"] or "").startswith("Items No Description")
      and "Hourly Rate" in _t["items_text"], _t)
check("bidnet page_url keeps query", bidnet.page_url(bidnet.CO_OPEN + "?keywords=hvac", 2)
      == bidnet.CO_OPEN + "/page2?keywords=hvac")
d = bidnet.parse_detail((FX / "bidnet_detail_littleton_2126.html").read_text())
check("real bidnet detail: closing + time", d["closing"] == "2026-10-28" and d["closing_text"] == "10/28/2026 02:00 PM MDT", d)
check("real bidnet detail: locked fields not invented", d["login_required_for_docs"] and d["agency"] is None and d["sol"] is None, d)
bf = bonfire.parse_list_json(_json.loads((FX / "bonfire_parker_open.json").read_text()), "parkeronline")
p28 = [r for r in bf if r["sol"] == "26-028"]
check("real bonfire list: 4 Parker opportunities", len(bf) == 4, len(bf))
check("real bonfire 26-028 close in Mountain time", p28 and p28[0]["closing"] == "2026-10-22"
      and p28[0]["closing_text"].startswith("2026-10-22 15:00"), p28)
check("real bonfire: UTC midnight rolls back to MT date", any(r["sol"] == "26-027" and r["closing"] == "2026-11-13" for r in bf))
try:
    bonfire.parse_detail((FX / "bonfire_opportunity_cloudflare.html").read_text())
    check("bonfire Cloudflare challenge detected", False)
except bonfire.Challenged:
    check("bonfire Cloudflare challenge detected", True)
sys.path.insert(0, str(ROOT / "scripts"))
import dibbs_watch  # noqa: E402
dh = (FX / "dibbs_rfq_3110.html").read_text()
dr = dibbs_watch.parse_rows(dh)
check("real dibbs grid: 6 rows", len(dr) == 6, len(dr))
check("real dibbs row fields", dr and dr[0]["sol"] == "SPE4A6-27-Q-0037" and dr[0]["nsn"] == "3110-01-341-6408"
      and dr[0]["qty"] == 11 and dr[0]["return_by"] == "2026-10-27" and dr[0]["pdf"].endswith(".PDF"), dr[:1])
check("real dibbs records found", dibbs_watch.records_found(dh) == 2675, dibbs_watch.records_found(dh))
check("dibbs sol regex: 3-char activity code", bool(dibbs_watch.SOL_RX.search("SPE4A0-26-T-2395")))

# ---------------------------------------------------------------- part 2: fake portal with real login
print("fake BidNet site: login, session reuse, auto re-login, full scan")
SESSIONS = set()
LOGINS = {"n": 0}
USER, PW = "luke@brownbisonco.com", "s3cret-test-only"


KW_HITS = {"n": 0}
CODES = {"sent": 0, "last": ""}


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _authed(self):
        c = self.headers.get("Cookie", "")
        return any(f"sid={s}" in c for s in SESSIONS)

    def _send(self, body, code=200, headers=None, ctype="text/html"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        for k, v in (headers.items() if isinstance(headers, dict) else (headers or [])):
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body.encode() if isinstance(body, str) else body)

    def do_GET(self):
        p = self.path
        if p.startswith("/public/authentication/login"):
            return self._send("<form method=post action='/public/authentication/login'><input name='j_username'>"
                              "<input name='j_password' type='password'><button type='submit'>Log in</button></form>")
        if p == "/colorado":
            # mirrors the real site: the login window sits on every page until you are logged in
            form = ("<form id='loginWindowForm' method='post' action='/public/authentication/login'>"
                    "<input id='loginBox_j_username' name='j_username'><input id='loginBox_j_password' name='j_password' type='password'>"
                    "<input type='hidden' name='_csrf' value='x'><button id='loginWindowButton' type='submit'>Login</button></form>")
            body = "<a href='/logout'>Logout</a>" if self._authed() else form
            return self._send(f"<html><head><title>Colorado Bids | Fake BidNet Direct</title></head><body>"
                              f"<a aria-label='my account' href='#'>avatar</a>{body}</body></html>")
        if p.startswith("/colorado/solicitations/open-bids"):
            if "selectedContent=BROKEN" in p:
                return self._send("<h1>Service unavailable</h1>", 503)
            if "/page2" in p:
                return self._send("<table><tr><td><a href='/colorado/city-of-littleton/solicitations/On-Call-Commercial-Plumbing-Services-2126/0000500002'>"
                                  "On-Call Commercial Plumbing Services RFQ 2126</a></td><td>Closing 10/28/2026</td></tr></table>")
            if "/page3" in p:
                return self._send("<span class='simpleResultsNumResults'>3 Open Solicitations</span>")
            if "AGGREGATE" in p:
                return self._send("<p>We can't find any current bids with your keywords.</p>")
            if "keywords=" in p:
                KW_HITS["n"] += 1
                return self._send("<span class='simpleResultsNumResults'>0 Open Solicitations</span>")
            return self._send("<span class='simpleResultsNumResults'>3 Open Solicitations</span>"
                              "<table><tr><td><a href='/colorado/town-of-castle-rock/solicitations/HVAC-Maintenance/0000500001'>HVAC Maintenance Services</a>"
                              "</td><td>Closing 11/20/2026</td></tr><tr><td><a href='/colorado/x/solicitations/Road-Paving/0000500003'>Road Paving 2027</a></td>"
                              "<td>Closing 11/01/2026</td></tr></table><a class='next' href='/colorado/solicitations/open-bids/page2'>Next</a>")
        if "/solicitations/" in p:
            docs = "<a href='/dl/rfq.pdf'>RFQ.pdf</a>" + ("<a href='/dl/addendum1.pdf'>Addendum 1.pdf</a>" if os.environ.get("FAKE_ADDENDUM") else "")
            return self._send(f"<h1>Bid</h1><div>Closing Date 11/20/2026</div><p>MANDATORY pre-bid site walk on 11/02/2026 at 9 AM.</p>{docs}")
        if p.startswith("/dl/"):
            if not self._authed():
                return self._send("login required", 403)
            return self._send(b"%PDF-1.4 fake", headers={"Content-Disposition": f"attachment; filename={p.rsplit('/', 1)[-1]}"},
                              ctype="application/pdf")
        return self._send("not found", 404)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        f = parse_qs(self.rfile.read(n).decode())
        if f.get("j_username") == [USER] and f.get("j_password") == [PW]:
            LOGINS["n"] += 1
            if "device_ok=1" not in (self.headers.get("Cookie") or ""):
                # like BidNet on a new device: password accepted, now an emailed confirmation code
                CODES["sent"] += 1
                CODES["last"] = f"{100000 + CODES['sent'] * 7919:06d}"  # a NEW code every time, like BidNet
                return self._send("<html><head><title>Fake BidNet Direct</title></head><body><h1>Confirm your device</h1>"
                                  "<p>Enter the confirmation code we emailed you.</p>"
                                  "<form method='post' action='/public/authentication/code'><input name='code'>"
                                  "<button type='submit'>Confirm</button></form></body></html>")
            sid = f"s{LOGINS['n']}"
            SESSIONS.add(sid)
            return self._send("", 302, {"Location": "/colorado", "Set-Cookie": f"sid={sid}; Path=/"})
        if self.path.startswith("/public/authentication/code"):
            if f.get("code") == [CODES["last"]]:
                sid = f"s{LOGINS['n']}"
                SESSIONS.add(sid)
                return self._send("", 302, [("Location", "/colorado"), ("Set-Cookie", f"sid={sid}; Path=/"),
                                            ("Set-Cookie", "device_ok=1; Path=/")])
            return self._send("<p>Enter the confirmation code we emailed you. That code was wrong.</p>", 401)
        return self._send("bad login", 401)


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}"
bidnet.BASE, bidnet.LOGIN_URL, bidnet.CO_OPEN = BASE, BASE + "/public/authentication/login", BASE + "/colorado/solicitations/open-bids"
os.environ["BIDNET_USER"], os.environ["BIDNET_PASS"] = USER, PW

from scripts.bidwatch.browser import Browser, PortalSession  # noqa: E402

b = Browser()
s1 = PortalSession(b, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
os.environ["BIDNET_CODE_WAIT"] = "1"
check("new device: login waits on the code prompt, then reports BLOCKED, no retry (one code email)",
      not s1.ensure_login() and "confirmation code" in s1.login_note and LOGINS["n"] == 1 and CODES["sent"] == 1,
      (s1.login_note, LOGINS, CODES))
marker = TMP / "state" / "bidnet_code_needed"
check("marker written: no more password logins until someone can supply a code", marker.exists())
check("with the marker present, ensure_login does not touch the portal",
      not s1.ensure_login() and LOGINS["n"] == 1 and CODES["sent"] == 1 and "no new login attempted" in s1.login_note, s1.login_note)
marker.unlink()
os.environ["BIDNET_CODE_WAIT"] = "20"


def _code_reader():  # what the MAIN session does: see the prompt, read the email, write the one-time file
    import time as _t
    while CODES["sent"] < 2:
        _t.sleep(0.2)
    _t.sleep(1)
    (TMP / "state" / "bidnet_code").write_text(CODES["last"] + "\n")


threading.Thread(target=_code_reader, daemon=True).start()
check("code supplied while the scanner waits on the prompt completes the login",
      s1.ensure_login() and LOGINS["n"] == 2 and CODES["sent"] == 2, (s1.login_note, LOGINS, CODES))
check("code file is single-use", not (TMP / "state" / "bidnet_code").exists())
s1.close()
check("session saved outside repo", (TMP / "state/sessions/bidnet.json").exists())
s2 = PortalSession(b, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
check("second run reuses session (no new login)", s2.ensure_login() and LOGINS["n"] == 2, s2.login_note)
s2.close()
SESSIONS.clear()  # server expires every session (timeout)
s3 = PortalSession(b, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
check("expired session -> automatic re-login, device already confirmed (no third code)",
      s3.ensure_login() and LOGINS["n"] == 3 and CODES["sent"] == 2, (s3.login_note, LOGINS, CODES))
rows, errs, _ = bidnet.collect_open(s3, ["hvac"])
check("collect follows pagination", len(rows) == 3, (len(rows), errs))
check("complete statewide list -> no keyword searches", KW_HITS["n"] == 0, KW_HITS)
bidnet.collect_open(s3, ["hvac"], force_keywords=True)
check("force_keywords runs keyword searches", KW_HITS["n"] == 1, KW_HITS)
_tabs = bidnet.CO_TABS
bidnet.CO_TABS = ["BUYER", "BROKEN"]  # second tab 404s on the fake site, like a list page that failed to load
_r, _e, _t = bidnet.collect_open(s3, [])
check("a statewide tab that fails marks the scan incomplete (previous bids are carried forward, none closed)",
      _t.get("_complete") is False and "statewide BROKEN" in _t.get("_failed", []) and len(_r) == 3, (_t, len(_r), _e))
bidnet.CO_TABS = _tabs
s3.close()
b.close()

# full scan against the fake site, with temp state files
from scripts.bidwatch import run  # noqa: E402

for name in ["OPEN_BIDS_FILE", "HEALTH_FILE", "REPORT_FILE", "WATCHLIST_FILE"]:
    setattr(run, name, TMP / f"{name}.json")
(TMP / "WATCHLIST_FILE.json").write_text('{"bids":[{"name":"Littleton 2126","source":"bidnet","match":"\\\\b2126\\\\b"}]}')
run.HOSTS["bidnet"] = BASE + "/colorado"
run.bidnet.download_docs.__globals__["DOWNLOAD_DIR"] = TMP / "downloads"
r1 = run.scan(["bidnet"])
rep = (TMP / "REPORT_FILE.json").read_text()
check("scan sees 3 open bids", r1["health"]["bidnet"]["count"] == 3, r1["health"]["bidnet"])
check("scan matches HVAC + plumbing, excludes paving", r1["health"]["bidnet"]["matches"] == 2, r1["health"]["bidnet"]["matches"])
check("mandatory walk extracted", any((x.get("prebid") or {}).get("mandatory") for x in r1["found"].values()))
check("watched bid flagged", any(x.get("watched") for x in r1["found"].values()))
check("watched bid docs downloaded when logged in", any(r1["downloads"].values()), r1["downloads"])
check("report has source health + all open", "## Source health" in rep and "All open matching bids" in rep)
os.environ["FAKE_ADDENDUM"] = "1"
r2 = run.scan(["bidnet"])
ch = [c for c in r2["changed"].values() if any("NEW DOCUMENTS" in d for d in c["diffs"])]
check("second scan detects addendum on watched bid", bool(ch), r2["changed"])
check("second scan: nothing falsely NEW", not r2["new"], list(r2["new"]))
# an unreachable source (SAM.gov API down, no key) must keep its previous rows and close nothing
ob = json.loads((TMP / "OPEN_BIDS_FILE.json").read_text())
ob["bids"]["samgov:seed1"] = {"source": "samgov", "id": "seed1", "title": "HVAC maintenance seed", "closing": "2099-01-01",
                             "profiles": ["brownbison"], "url": "https://sam.gov/x", "first_seen": "2026-01-01", "last_seen": "2026-01-01"}
(TMP / "OPEN_BIDS_FILE.json").write_text(json.dumps(ob))
run.HOSTS["samgov"] = "http://127.0.0.1:1/"
os.environ.pop("SAM_API_KEY", None)
r3 = run.scan(["bidnet", "samgov"])
check("unreachable source: previous rows carried forward, none closed",
      "samgov:seed1" in r3["found"] and not any(k.startswith("samgov") for k in r3["closed"])
      and r3["health"]["samgov"]["count"] == 1, (list(r3["closed"]), r3["health"]["samgov"]))
r4 = run.scan(["bidnet"])
check("source not in this run: rows kept and health row marked not scanned",
      "samgov:seed1" in r4["found"] and r4["health"]["samgov"].get("not_scanned_this_run") is True
      and "NOT SCANNED THIS RUN" in (TMP / "REPORT_FILE.json").read_text(), r4["health"].get("samgov"))
srv.shutdown()

# ---------------------------------------------------------------- part 3: BidNet confirmation code from the mailbox
print("mailbox confirmation-code reader (mailcode.py, fake IMAP)")
import datetime as _dt  # noqa: E402
import email.utils as _eu  # noqa: E402
from scripts.bidwatch import mailcode  # noqa: E402

check("extract_code: BidNet sentence", mailcode.extract_code("Your confirmation code for BidNet Direct is: 482910 .") == "482910")
check("extract_code: html body", mailcode.extract_code("<p>Your confirmation code for BidNet Direct is:</p><b>113355</b>") == "113355")
check("extract_code: none", mailcode.extract_code("Thanks for registering") is None)

_now = _dt.datetime.now(_dt.timezone.utc)


def _raw(code, when):
    return (f"From: BidNet Direct <noreply@bidnet.com>\r\nTo: luke@brownbisonco.com\r\n"
            f"Subject: Your BidNet Direct confirmation code\r\nDate: {_eu.format_datetime(when)}\r\n"
            f"Content-Type: text/plain; charset=utf-8\r\n\r\nLuke Adams, Your confirmation code for BidNet Direct is: {code}\r\n"
            ).encode()


class FakeIMAP:
    """Stands in for imaplib.IMAP4_SSL: three BidNet code emails, only #8 is newer than this login."""
    calls = []

    def __init__(self, host):
        FakeIMAP.calls.append(("connect", host))

    def login(self, user, secret):
        FakeIMAP.calls.append(("login", user))
        if secret != "fake-test-token":
            raise RuntimeError("mailbox refused the login")

    def select(self, box, readonly=False):
        FakeIMAP.calls.append(("select", box, readonly))

    def search(self, charset, query):
        FakeIMAP.calls.append(("search", query))
        return "OK", [b"7 8 9"]

    def fetch(self, num, what):
        FakeIMAP.calls.append(("fetch", num, what))
        msgs = {b"7": _raw("111111", _now - _dt.timedelta(hours=5)),     # yesterday's dead code
                b"8": _raw("654321", _now - _dt.timedelta(seconds=20)),  # this login's code
                b"9": _raw("777777", _now - _dt.timedelta(minutes=30))}  # an older login's code
        return "OK", [(b"%s (BODY[] {%d}" % (num, len(msgs[num])), msgs[num]), b")"]

    def logout(self):
        FakeIMAP.calls.append(("logout",))


os.environ[mailcode.ENV_PASS] = "fake-test-token"
mailcode.IMAP_FACTORY = FakeIMAP
got = mailcode.fetch_code(_now - _dt.timedelta(seconds=60))
check("fetch_code picks the code emailed after this login", got == "654321", got)
check("mailbox opened read-only, bodies peeked", any(c[0] == "select" and c[2] is True for c in FakeIMAP.calls)
      and all("PEEK" in c[2] for c in FakeIMAP.calls if c[0] == "fetch"), FakeIMAP.calls)
check("search limited to BidNet sender + subject", any(c[0] == "search" and "noreply@bidnet.com" in c[1]
                                                        and "confirmation code" in c[1] for c in FakeIMAP.calls))
check("fetch_code: nothing new -> None", mailcode.fetch_code(_now + _dt.timedelta(minutes=5)) is None)
os.environ[mailcode.ENV_PASS] = "not-the-token"
check("poll_code survives a mailbox error and times out to None",
      mailcode.poll_code(_now, timeout=0, sleep=lambda s: None) is None)
os.environ[mailcode.ENV_PASS] = "fake-test-token"
check("bidnet.wait_for_code reads the mailbox when configured",
      bidnet.wait_for_code(5, since=_now - _dt.timedelta(seconds=60)) == "654321")
del os.environ[mailcode.ENV_PASS]
check("wait_for_code without mailbox access times out to None", bidnet.wait_for_code(0) is None)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
