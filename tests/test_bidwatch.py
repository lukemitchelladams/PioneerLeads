#!/usr/bin/env python3
"""Offline tests for scripts/bidwatch. Run: python3 tests/test_bidwatch.py

Part 1: parsers (dates, pre-bid detection, BidNet listing/detail, Bonfire JSON/detail, SAM.gov records).
Part 2: a fake BidNet-style site on localhost with a real login form and cookie session, to prove that
        PortalSession logs in, saves the session, reuses it on the next run, and logs in again by itself
        after the server expires the session. Then a full scan() against the fake site.
The live portals are NOT reachable from the build environment; selectors are verified against these
fixtures only. The first live run saves debug HTML for any page that parses to nothing.
"""
from __future__ import annotations

import http.server
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

# ---------------------------------------------------------------- part 2: fake portal with real login
print("fake BidNet site: login, session reuse, auto re-login, full scan")
SESSIONS = set()
LOGINS = {"n": 0}
USER, PW = "luke@brownbisonco.com", "s3cret-test-only"


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _authed(self):
        c = self.headers.get("Cookie", "")
        return any(f"sid={s}" in c for s in SESSIONS)

    def _send(self, body, code=200, headers=None, ctype="text/html"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body.encode() if isinstance(body, str) else body)

    def do_GET(self):
        p = self.path
        if p.startswith("/public/authentication/login"):
            return self._send("<form method=post action='/public/authentication/login'><input name='j_username'>"
                              "<input name='j_password' type='password'><button type='submit'>Log in</button></form>")
        if p == "/colorado":
            return self._send("<a href='/logout'>Logout</a>" if self._authed() else "<a href='/public/authentication/login'>Login</a>")
        if p.startswith("/colorado/solicitations/open-bids"):
            if "pageNumber=2" in p:
                return self._send("<table><tr><td><a href='/colorado/city-of-littleton/solicitations/On-Call-Commercial-Plumbing-Services-2126/0000500002'>"
                                  "On-Call Commercial Plumbing Services RFQ 2126</a></td><td>Closing 10/28/2026</td></tr></table>")
            if "keywords=" in p:
                return self._send("<p>no results</p>")
            return self._send("<table><tr><td><a href='/colorado/town-of-castle-rock/solicitations/HVAC-Maintenance/0000500001'>HVAC Maintenance Services</a>"
                              "</td><td>Closing 11/20/2026</td></tr><tr><td><a href='/colorado/x/solicitations/Road-Paving/0000500003'>Road Paving 2027</a></td>"
                              "<td>Closing 11/01/2026</td></tr></table><a rel='next' href='/colorado/solicitations/open-bids?pageNumber=2'>Next</a>")
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
            sid = f"s{LOGINS['n']}"
            SESSIONS.add(sid)
            return self._send("", 302, {"Location": "/colorado", "Set-Cookie": f"sid={sid}; Path=/"})
        return self._send("bad login", 401)


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}"
bidnet.BASE, bidnet.LOGIN_URL, bidnet.CO_OPEN = BASE, BASE + "/public/authentication/login", BASE + "/colorado/solicitations/open-bids"
os.environ["BIDNET_USER"], os.environ["BIDNET_PASS"] = USER, PW

from scripts.bidwatch.browser import Browser, PortalSession  # noqa: E402

b = Browser()
s1 = PortalSession(b, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
check("first run logs in", s1.ensure_login() and LOGINS["n"] == 1, s1.login_note)
s1.close()
check("session saved outside repo", (TMP / "state/sessions/bidnet.json").exists())
s2 = PortalSession(b, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
check("second run reuses session (no new login)", s2.ensure_login() and LOGINS["n"] == 1, s2.login_note)
s2.close()
SESSIONS.clear()  # server expires every session (timeout)
s3 = PortalSession(b, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
check("expired session -> automatic re-login", s3.ensure_login() and LOGINS["n"] == 2, s3.login_note)
rows, errs = bidnet.collect_open(s3, ["hvac"])
check("collect follows pagination", len(rows) == 3, (len(rows), errs))
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
srv.shutdown()

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
