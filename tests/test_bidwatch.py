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
import re
import sys
import tempfile
import threading
import time
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
pb3 = common.extract_prebid("Pre-Bid Conference: None. Site Visit: Mandatory, 10/21/2026 9:00 AM at Town Hall. Questions due 10/23.")
check("prebid: 'None' phrase skipped, later mandatory walk found", pb3 and pb3["date"] == "2026-10-21" and pb3["mandatory"] is True, pb3)
pb4 = common.extract_prebid("MANDATORY pre-bid meeting on 10/21/2026 at 10:00 AM at the site. Attendance is required. "
                            "Questions are optional and may be submitted by email until 10/23/2026.")
check("prebid: 'optional' elsewhere does not flip a mandatory walk", pb4 and pb4["mandatory"] is True and pb4["date"] == "2026-10-21", pb4)
pb5 = common.extract_prebid("Prebid Conference 10/01/2026 01:00 PM MDT Location CU Boulder Attendance Mandatory Contact ...")
check("prebid: BidNet detail style 'Attendance Mandatory' after the date", pb5 and pb5["mandatory"] is True and pb5["date"] == "2026-10-01", pb5)
pb6 = common.extract_prebid("Prebid Conference 10/01/2026 01:00 PM MDT Contact Information Procurement Office 1234 Main St Boulder CO "
                            "80309 Phone 303-555-0100 Email procurement@example.edu Pre-Bidding Events Event Type Prebid Conference "
                            "Attendance Mandatory Event date 10/01/2026 01:00 PM MDT Location Regent Hall Note Sign in required")
check("prebid: BidNet flattened page, mandatory read from the later structured block", pb6 and pb6["mandatory"] is True and pb6["date"] == "2026-10-01", pb6)
pb7 = common.extract_prebid("Pre-Bidding Events Event Type Onsite Visit Attendance Recommended Event date 10/26/2026 10:00 AM MDT Location 900 Colorow Road, Golden")
check("prebid: 'Attendance Recommended' is not mandatory", pb7 and pb7["date"] == "2026-10-26" and pb7["mandatory"] is not True, pb7)
check("samgov document name = file id, not 'download'",
      samgov.normalize({"noticeId": "n1", "resourceLinks": ["https://api.sam.gov/prod/opportunities/v3/opportunities/resources/files/abc123def/download"]})["documents"][0]["name"] == "abc123def")

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
# Communication / Q & A tabs (text as rendered on 0000440322, 2026-11-06): the walkthrough-time notice lived only there
_comm = ("<h1>Bid</h1><select hidden><option data-ajax-url='/public/solicitations/1/abstract/communication'>Communication</option></select>"
         "<div id='communication'><h3>Communication No.1 - 11/05/2026 03:48 PM MST</h3><p>Please note that the walkthrough time has "
         "changed from 9 am to 10:30 am. If you have any questions please email shickman@cvprd.com.</p>"
         "<h3>Communication No.2 - 11/06/2026 09:00 AM MST</h3><div>Addendum <b>2</b> posted.</div></div>"
         "<footer><p>Print Options</p><p>Terms of Use</p><p>© 2026 BidNet</p></footer>")
_cm = bidnet.parse_communications(_comm)
check("Communication tab: number, date as printed, text up to the next entry or the page chrome",
      _cm == [{"no": "1", "date": "11/05/2026 03:48 PM MST", "text": "Please note that the walkthrough time has changed from 9 am to "
               "10:30 am. If you have any questions please email shickman@cvprd.com."},
              {"no": "2", "date": "11/06/2026 09:00 AM MST", "text": "Addendum 2 posted."}], _cm)
check("Communication tab: empty tab ('No results match your criteria.') -> []",
      bidnet.parse_communications("<h1>Bid</h1><p>No results match your criteria.</p>") == [])
_cm_live = bidnet.parse_communications((FX / "bidnet_communication_0000440322.html").read_text())
check("real Communication tab (Carbon Valley 0000440322, 2026-11-06): the walkthrough-time notice, nothing else",
      _cm_live == [{"no": "1", "date": "11/05/2026 03:48 PM MST", "text": "Please note that the walkthrough time has changed from 9 am to "
                    "10:30 am. If you have any questions please email shickman@cvprd.com."}], _cm_live)
check("a notice with attached files: the files table's column headings and 'No Documents' are not text",
      bidnet.parse_communications("<h3>Communication No.6 - 11/04/2026 10:04 AM MST</h3><p>Q &amp; A #4</p><table><tr><th>Communication Documents"
                                  "</th></tr><tr><th>Document</th><th>Size</th><th>Uploaded Date</th></tr><tr><td>Q&amp;A Set #4.pdf</td><td>110 Kb"
                                  "</td><td>11/04/2026 10:03 AM MST</td></tr></table><p>No Documents</p>")[0]["text"]
      == "Q & A #4 Q&A Set #4.pdf 110 Kb 11/04/2026 10:03 AM MST")
# Q & A tab, real pages saved 2026-11-06 (live report that morning: every empty tab read as 1 awaiting answer: "/" from the
# thead's "Question/Answer", and real rows carried "Arrow Right" / "Q2" chrome)
_qa0 = bidnet.parse_qa((FX / "bidnet_qa_empty_0000440322.html").read_text())
check("real Q & A tab with no questions (0000440322): deadline read, zero items, no pager total",
      _qa0 == {"questions_deadline": "2026-11-17", "items": [], "total": None}, _qa0)
_qa5 = bidnet.parse_qa((FX / "bidnet_qa_5_answered_0000441328.html").read_text())
check("real Q & A tab (HVAC Filters & Belts 0000441328): 5 rows = pager's 5 results, clean subject + question, answer text, ISO dates",
      _qa5 and _qa5["questions_deadline"] == "2026-11-02" and _qa5["total"] == 5 and len(_qa5["items"]) == 5
      and _qa5["items"][0] == {"no": "Q1", "question": "General Question: Is this an all or nothing award?", "answer": "Answered in Addendum 1",
                               "question_date": "2026-10-26", "answer_date": "2026-11-04"}
      and _qa5["items"][1]["question"].startswith("Incumbent details: Was there a previous incumbent?")
      # a leaked caption would sit at the start ("Question: General Question ...") or before the answer ("Answer: Answered in");
      # "General Question:" is the buyer's own subject line and stays
      and not any(re.search(r"Arrow|^Question:|\bAnswer:|\bQ\d\b|results found", f"{i['question']} {i['answer']}") for i in _qa5["items"]),
      _qa5)
_qa266 = bidnet.parse_qa((FX / "bidnet_qa_266_results_0000437813.html").read_text())
check("real Q & A tab (District Wide Custodial 0000437813, trimmed to 10 of its 266 rows): items = rows on the page, total = the pager",
      _qa266 and _qa266["total"] == 266 and len(_qa266["items"]) == 10 and all(i["answer"] == "Answered in Addendum 3" for i in _qa266["items"])
      and _qa266["items"][0]["no"] == "Q1" and _qa266["items"][-1]["no"] == "Q266" and _qa266["questions_deadline"] == "2026-10-21", _qa266)
check("Q & A: a page without the tab's form (the Details tab also prints 'Question Acceptance Deadline') is None, not an empty result",
      bidnet.parse_qa((FX / "bidnet_detail_littleton_2126.html").read_text() + "<p>Question Acceptance Deadline 11/17/2026 12:00 AM MST</p>") is None)
_li = ("<table><tr class='mets-table-row'><td><a class='solicitation-link mets-command-link' id='444202844454' "
       "href='/private/supplier/interception/open-notice/444202844454?target=view'>Housing Action Plan</a>"
       "<span class='sol-region-item'>Colorado</span><span class='sol-closing-date'><span class='date-value'>11/10/2026</span></span>"
       "</td></tr></table>")
_lr = bidnet.parse_listing(_li)[0]
check("logged-in aggregate rows (open-notice links) parse with the same id", len(_lr) == 1 and _lr[0]["id"] == "444202844454"
      and _lr[0]["closing"] == "2026-11-10", _lr)
check("bidnet page_url keeps query", bidnet.page_url(bidnet.CO_OPEN + "?keywords=hvac", 2)
      == bidnet.CO_OPEN + "/page2?keywords=hvac")
d = bidnet.parse_detail((FX / "bidnet_detail_littleton_2126.html").read_text())
check("real bidnet detail: closing + time", d["closing"] == "2026-10-28" and d["closing_text"] == "10/28/2026 02:00 PM MDT", d)
check("real bidnet detail: locked fields not invented", d["login_required_for_docs"] and d["agency"] is None and d["sol"] is None, d)
_ev_cu = bidnet.parse_detail((FX / "bidnet_prebid_events_cu_ucb001284.html").read_text()
                             + "<p>Site visit optional for returning vendors.</p>")["prebid"]
check("BidNet events block: 'Attendance Mandatory' is MANDATORY even when the text elsewhere says optional",
      _ev_cu and _ev_cu["mandatory"] is True and _ev_cu["date"] == "2026-10-01" and _ev_cu["source"] == "bidnet events", _ev_cu)
_ev_bo = bidnet.parse_detail((FX / "bidnet_prebid_events_boettcher.html").read_text())["prebid"]
check("BidNet events block: 'Attendance Recommended' is not mandatory", _ev_bo and _ev_bo["mandatory"] is False
      and _ev_bo["date"] == "2026-10-26" and "Recommended" in _ev_bo["quote"], _ev_bo)
_ev_ad = bidnet.parse_detail((FX / "bidnet_prebid_events_addendum_label.html").read_text())["prebid"]
check("RSVP in an event note is flagged (Cherry Creek: 'you must RSVP'); none on CU's event",
      _ev_ad and _ev_ad.get("rsvp") is True and _ev_ad.get("rsvp_by") is None and _ev_cu.get("rsvp") is False, (_ev_ad, _ev_cu))
_rsvp_html = ('<div class="preBidEventList"><ul><li>'
              '<div class="mets-field"><span class="mets-field-label">Event Type</span><div class="mets-field-body"><p>Site Visit</p></div></div>'
              '<div class="mets-field"><span class="mets-field-label">Attendance</span><div class="mets-field-body"><p>Recommended</p></div></div>'
              '<div class="mets-field"><span class="mets-field-label">Event date</span><div class="mets-field-body"><p>10/27/2026 09:00 AM MDT</p></div></div>'
              '<div class="mets-field"><span class="mets-field-label">Event Note</span><div class="mets-field-body"><p>Please RSVP by October 23, 2026 to the buyer.</p></div></div>'
              '</li></ul></div>')
_ev_rs = bidnet.parse_detail(_rsvp_html)["prebid"]
from scripts.bidwatch import run as _run_early  # noqa: E402  (same module object part 2 patches later)

check("RSVP deadline read from the note and shown in the walk column",
      _ev_rs and _ev_rs["rsvp_by"] == "2026-10-23"
      and "RSVP by 2026-10-23" in _run_early._row({"source": "bidnet", "id": "1", "prebid": _ev_rs}),
      _ev_rs)
check("BidNet events block changed by an addendum ('Attendance A - Previous Addendum') still parses: not mandatory",
      _ev_ad and _ev_ad["source"] == "bidnet events" and _ev_ad["mandatory"] is False and _ev_ad["date"] == "2026-10-13", _ev_ad)
# the report's change lines for the two tabs: each entry once, the first scan that sees it; an answer makes its question news again
_c1 = {"no": "1", "date": "11/05/2026 03:48 PM MST", "text": "Please note that the walkthrough time has changed from 9 am to 10:30 am."}
_c2 = {"no": "2", "date": "11/06/2026 09:00 AM MST", "text": "Addendum 2 posted."}
_q = {"question": "Is the walkthrough mandatory?", "answer": None, "question_date": "2026-11-06", "answer_date": None}
_qa_a = {"questions_deadline": "2026-11-17", "items": [_q]}
_qa_b = {"questions_deadline": "2026-11-17", "items": [{**_q, "answer": "Yes.", "answer_date": "2026-11-06"}]}
_d1 = _run_early._diff({"title": "x"}, {"title": "x", "communications": [_c1], "qa": _qa_a})
check("first sight: NEW COMMUNICATION with its number, date and text; the question deadline; the unanswered question",
      _d1 == ['NEW COMMUNICATION No.1 11/05/2026 03:48 PM MST: "Please note that the walkthrough time has changed from 9 am to 10:30 am."',
              'NEW Q&A: 0 answered, 1 awaiting answer: "Is the walkthrough mandatory?"', "questions deadline 2026-11-17"], _d1)
check("unchanged tabs: no line", _run_early._diff({"communications": [_c1], "qa": _qa_a}, {"communications": [_c1], "qa": _qa_a}) == [])
_d2 = _run_early._diff({"communications": [_c1], "qa": _qa_a}, {"communications": [_c1, _c2], "qa": _qa_b})
check("a second notice and an answer: only the new entry and the newly answered question are reported",
      _d2 == ['NEW COMMUNICATION No.2 11/06/2026 09:00 AM MST: "Addendum 2 posted."', 'NEW Q&A: 1 answered: "Yes."'], _d2)
check("a changed question deadline is reported; a blind read (no tabs) reports nothing",
      _run_early._diff({"qa": _qa_a}, {"qa": {**_qa_a, "questions_deadline": "2026-11-20"}}) == ["questions deadline 2026-11-20"]
      and _run_early._diff({"communications": [_c1], "qa": _qa_a}, {"title": "x"}) == [])
check("an empty Q & A tab (no items, same deadline) prints nothing; a paged list says how much of it the page held",
      _run_early._diff({"qa": {"questions_deadline": "2026-11-17", "items": [], "total": None}},
                       {"qa": {"questions_deadline": "2026-11-17", "items": [], "total": None}}) == []
      and _run_early._diff({"qa": _qa_a}, {"qa": {**_qa_b, "total": 266}}) == ['NEW Q&A: 1 answered (1 of 266 shown): "Yes."'])
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

# ColoradoVSS: the JSON the public Angular grid and detail page receive (live 2026-10-29, trimmed)
from scripts.bidwatch import coloradovss  # noqa: E402
vl = coloradovss.parse_list_payload(_json.loads((FX / "coloradovss_list.json").read_text()))
vb = {r["id"]: r for r in vl}
ih = vb.get("DQ1-AAHA-2027000145") or {}
tcf = vb.get("DQ1-CAAA-2027000037") or {}
check("vss list: 8 fixture rows parsed", len(vl) == 8, len(vl))
check("vss id drops the version suffix, sol keeps it", ih.get("sol") == "DQ1-AAHA-2027000145-1" and ih.get("version") == 1
      and tcf.get("sol") == "DQ1-CAAA-2027000037-3", (ih, tcf))
check("vss closing epoch ms -> Mountain time (MST after the DST change)",
      ih.get("closing") == "2026-11-06" and ih.get("closing_text") == "2026-11-06 14:00 MST", ih)
check("vss closing in MDT before the DST change + category name",
      tcf.get("closing_text") == "2026-10-29 17:00 MDT" and tcf.get("category") == "Water/Sewer", tcf)
check("vss record shape matches the other sources",
      all(ih.get(k) for k in ("title", "agency", "url", "published", "closing")) and ih.get("state") == "CO"
      and ih.get("source") == "coloradovss" and ih.get("published") == "2026-10-28", ih)
check("vss sole-source and settlement notices flagged; RFI is upcoming",
      vb["NPSS1-GJHA-2027000072"].get("notice_only") and vb["NCS1-IHHA-2027000075"].get("notice_only")
      and vb["RFI-FAAA-2027000011"].get("upcoming") and not ih.get("notice_only"))
check("vss notice never matches a profile (even with a trade word)",
      _run_early.profile_hits({**vb["NPSS1-GJHA-2027000072"], "title": "HVAC sole source"}, profiles) == [])
check("vss TCF boiler DQ matches brownbison", "brownbison" in _run_early.profile_hits(tcf, profiles))
d_ih = coloradovss.parse_detail_payload(_json.loads((FX / "coloradovss_detail_ih25043.json").read_text()))
pb_ih = d_ih.get("prebid") or {}
check("vss detail: MANDATORY pre-bid walk read from the Schedule of Events",
      pb_ih.get("date") == "2026-10-29" and pb_ih.get("mandatory") is True and pb_ih.get("time") == "9:00AM"
      and "Mandatory Pre-Bid Walk" in pb_ih.get("quote", "") and pb_ih.get("source") == "coloradovss schedule of events", pb_ih)
check("vss prebid has the shared prebid shape", {"date", "mandatory", "quote", "rsvp", "rsvp_by", "source"} <= set(pb_ih), pb_ih)
check("vss detail: questions due, 3 attachments, instructions text",
      d_ih.get("questions_due") == "2026-10-30" and len(d_ih.get("documents") or []) == 3
      and "Budget: $75,000" in (d_ih.get("description") or ""), d_ih)
pb_mo = coloradovss.parse_detail_payload(_json.loads((FX / "coloradovss_detail_montrose.json").read_text())).get("prebid") or {}
check("vss Montrose: 'Mandatory Pre-Submittal Conference' 2026-11-05, instructions quoted",
      pb_mo.get("date") == "2026-11-05" and pb_mo.get("mandatory") is True and "Montrose RC" in pb_mo.get("quote", ""), pb_mo)
d_pcc = coloradovss.parse_detail_payload(_json.loads((FX / "coloradovss_detail_pcc_ada.json").read_text()))
check("vss PCC ADA: no event and no instructions -> no pre-bid claimed (it is only in the PDF)",
      d_pcc.get("prebid") is None and len(d_pcc.get("documents") or []) == 2, d_pcc)
check("vss split_ref without the bracket form", coloradovss.split_ref("RFP-IHJA-2022000320-10")
      == ("RFP-IHJA-2022000320", "RFP-IHJA-2022000320-10", 10))
_vo = coloradovss.prebid_from([{"event": "Optional Pre-Bid Conference", "date": "2026-11-02", "time": "10:00AM",
                                "when": "2026-11-02 10:00AM"}], "")
check("vss optional event is not mandatory", _vo and _vo["mandatory"] is False and _vo["date"] == "2026-11-02", _vo)
_vi = coloradovss.prebid_from([], "A non-mandatory site visit will be held 11/12/2026 at 10:00 AM.")
check("vss pre-bid from the instructions text when no event", _vi and _vi["mandatory"] is False
      and _vi["date"] == "2026-11-12" and _vi["source"] == "coloradovss instructions", _vi)
check("run.py knows coloradovss (host, no credentials)", "coloradovss" in _run_early.KNOWN_SOURCES
      and "coloradovss" in _run_early.HOSTS and _run_early.CRED_NAMES["coloradovss"] == [])


class _VssFakePage:
    """Home page that renders the list link only on the Nth goto (0 = never); status fixed."""

    def __init__(self, link_on_attempt, status=200, body="<html>Colorado VSS home</html>"):
        self.link_on_attempt, self.status, self.body = link_on_attempt, status, body
        self.gotos, self.waits = 0, []

    def goto(self, url, wait_until=None):
        self.gotos += 1
        return type("R", (), {"status": self.status})()

    def locator(self, sel):
        page = self

        class _Link:
            def wait_for(self_inner, state=None, timeout=None):
                if page.gotos != page.link_on_attempt:
                    raise TimeoutError("no link yet")
        link = _Link()
        link.first = link
        return link

    def wait_for_timeout(self, ms):
        self.waits.append(ms)

    def content(self):
        return self.body

    def title(self):
        return "VSS"


class _VssFakeSession:
    def __init__(self, page):
        self.page, self.dumps = page, []

    def debug_dump(self, tag):
        self.dumps.append(tag)


_p2 = _VssFakePage(link_on_attempt=2)
_s2 = _VssFakeSession(_p2)
_lk, _st, _at = coloradovss._home_link(_s2)
check("vss home retry: link missing once, found on the reload (attempt 2, one wait, no dump)",
      _at == 2 and _p2.gotos == 2 and _p2.waits == [coloradovss.HOME_RETRY_WAIT_MS] and _s2.dumps == [] and _st == 200,
      (_at, _p2.gotos, _p2.waits, _s2.dumps))
_p1 = _VssFakePage(link_on_attempt=1)
_s1 = _VssFakeSession(_p1)
check("vss home retry: link on the first try needs no reload", coloradovss._home_link(_s1)[2] == 1 and _p1.gotos == 1
      and _p1.waits == [], (_p1.gotos, _p1.waits))
_p0 = _VssFakePage(link_on_attempt=0)
_s0 = _VssFakeSession(_p0)
try:
    coloradovss._home_link(_s0)
    _err0 = None
except RuntimeError as e:
    _err0 = str(e)
check("vss home retry: missing twice -> one RuntimeError naming 2 attempts, one debug dump",
      _err0 and "after 2 attempts" in _err0 and _p0.gotos == 2 and _s0.dumps == ["coloradovss-no-list-link"],
      (_err0, _p0.gotos, _s0.dumps))
_pb = _VssFakePage(link_on_attempt=0, status=403)
_sb = _VssFakeSession(_pb)
try:
    coloradovss._home_link(_sb)
    _errb = None
except coloradovss.Challenged as e:
    _errb = str(e)
check("vss home retry: a 403 refusal raises Challenged at once, no reload", _errb and _pb.gotos == 1 and _pb.waits == [],
      (_errb, _pb.gotos, _pb.waits))
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
LOGIN_POSTS = {"n": 0}  # every POST to the login endpoint, accepted or not (= a password sent)
CODES = {"sent": 0, "last": ""}
BAD = {"n": 0}
HITS2 = {"home": 0, "list": 0, "detail": 0, "comm": 0, "qa": 0}
ROBOT = "<html><head><title>BidNet Direct</title></head><body><p>Please verify that you're not a robot.</p></body></html>"
# the Communication tab text as BidNet rendered it on 0000440322 (2026-11-05 15:48 MST): the notice that was missed
COMM_TEXT = ("Please note that the walkthrough time has changed from 9 am to 10:30 am. If you have any questions please "
             "email shickman@cvprd.com.")
NO_RESULTS = "<p class='mets-no-results'>No results match your criteria.</p>"


def _ahead(days: int) -> str:
    """Fake-site dates relative to today, so fixtures never age past their closing date (the list fixture's
    fixed 10/28/2026 closing made 'robot check on the list' fail from 2026-10-29)."""
    import datetime as _dt
    return (_dt.date.today() + _dt.timedelta(days=days)).strftime("%m/%d/%Y")



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
            HITS2["home"] += 1
            if os.environ.get("FAKE_ROBOT_HOME"):
                return self._send(ROBOT)
            # mirrors the real site: the login window sits on every page until you are logged in
            form = ("<form id='loginWindowForm' method='post' action='/public/authentication/login'>"
                    "<input id='loginBox_j_username' name='j_username'><input id='loginBox_j_password' name='j_password' type='password'>"
                    "<input type='hidden' name='_csrf' value='x'><button id='loginWindowButton' type='submit'>Login</button></form>")
            body = "<a href='/logout'>Logout</a>" if self._authed() else form
            return self._send(f"<html><head><title>Colorado Bids | Fake BidNet Direct</title></head><body>"
                              f"<a aria-label='my account' href='#'>avatar</a>{body}</body></html>")
        if p.startswith("/colorado/solicitations/open-bids"):
            HITS2["list"] += 1
            if os.environ.get("FAKE_ROBOT_LIST"):
                return self._send(ROBOT)
            if "selectedContent=STUCK" in p:  # every page the same rows plus a Next link, like a disabled last-page link
                return self._send("<span class='simpleResultsNumResults'>2 Open Solicitations</span><table>"
                                  f"<tr><td><a href='/colorado/x/solicitations/A/0000600001'>Stuck A</a></td><td>Closing {_ahead(21)}</td></tr>"
                                  f"<tr><td><a href='/colorado/x/solicitations/B/0000600002'>Stuck B</a></td><td>Closing {_ahead(21)}</td></tr>"
                                  "</table><a class='next' href='javascript:;'>Next</a>")
            if "selectedContent=BROKEN" in p:
                return self._send("<h1>Service unavailable</h1>", 503)
            if "/page2" in p:
                return self._send("<table><tr><td><a href='/colorado/city-of-littleton/solicitations/On-Call-Commercial-Plumbing-Services-2126/0000500002'>"
                                  f"On-Call Commercial Plumbing Services RFQ 2126</a></td><td>Closing {_ahead(21)}</td></tr></table>")
            if "/page3" in p:
                return self._send("<span class='simpleResultsNumResults'>3 Open Solicitations</span>")
            if "AGGREGATE" in p:
                return self._send("<p>We can't find any current bids with your keywords.</p>")
            if "keywords=" in p:
                KW_HITS["n"] += 1
                return self._send("<span class='simpleResultsNumResults'>0 Open Solicitations</span>")
            return self._send("<span class='simpleResultsNumResults'>3 Open Solicitations</span>"
                              "<table><tr><td><a href='/colorado/town-of-castle-rock/solicitations/HVAC-Maintenance/0000500001'>HVAC Maintenance Services</a>"
                              f"</td><td>Closing {_ahead(21)}</td></tr><tr><td><a href='/colorado/x/solicitations/Road-Paving/0000500003'>Road Paving 2027</a></td>"
                              f"<td>Closing {_ahead(2)}</td></tr></table><a class='next' href='/colorado/solicitations/open-bids/page2'>Next</a>")
        if "/solicitations/" in p:
            HITS2["detail"] += 1
            if os.environ.get("FAKE_ROBOT_DETAIL"):
                return self._send(ROBOT)
            docs = "<a href='/dl/rfq.pdf'>RFQ.pdf</a>" + ("<a href='/dl/addendum1.pdf'>Addendum 1.pdf</a>" if os.environ.get("FAKE_ADDENDUM") else "") \
                + ("<a href='/dl/missing.pdf'>Missing.pdf</a>" if os.environ.get("FAKE_MISSING_DOC") else "")
            # the real page's tab strip (hrefs carry innerTabId=...; here each tab is its own page) plus the hidden
            # mobile <select> whose options name the same tabs
            tabs = ("<ul class='tabs'><li><a href='?innerTabId=communication'>Communication</a></li>"
                    "<li><a href='?innerTabId=questions-answers'>Q &amp; A</a></li></ul>"
                    "<select hidden><option data-ajax-url='/public/solicitations/9745843859/abstract/communication'>Communication</option></select>")
            pane = ""
            if "innerTabId=" in p:
                if os.environ.get("FAKE_ROBOT_TAB"):
                    return self._send(ROBOT)
                if os.environ.get("FAKE_TAB_DOWN"):
                    return self._send("<h1>Service unavailable</h1>", 503)
            # the tab panes mirror the live markup (tests/fixtures/bidnet_communication_0000440322.html, bidnet_qa_*.html)
            if "innerTabId=communication" in p:
                HITS2["comm"] += 1
                n = int(os.environ.get("FAKE_COMM") or 0)
                pane = "<div id='innerTabContent'>" + ("".join(
                    f"<div class='fieldset communications content-block'><h3 class='content-block-title'>Communication No.{i} - "
                    f"11/0{4 + i}/2026 03:48 PM MST</h3><div class='communicationTabDescription'><p>"
                    f"{COMM_TEXT if i == 1 else f'Addendum {i} posted.'}</p></div></div>"
                    for i in range(1, n + 1)) or NO_RESULTS) + "</div>"
            elif "innerTabId=questions-answers" in p:
                HITS2["qa"] += 1
                rows = ("<tr class='mets-table-row odd' id='9901533414'><td class='questionNo'>Q1</td><td class='questionAnswer'>"
                        "<div class='subjectQuestionContainer'><div class='questionAnswerTitle expandable' data-type='question'>"
                        "<svg class='mets-icon svg-arrow-right'></svg><span class='accessibility-hidden'>Arrow Right</span>"
                        "<strong>Question: Walkthrough</strong></div><div id='questionContainer_9901533414'>Is the walkthrough mandatory?</div></div>"
                        "<div class='answerContainer'><strong class='questionAnswerTitle' data-type='answer'>Answer:</strong>"
                        "<div class='italic' id='answerContainer_9901533414'>Yes, attendance is mandatory.</div></div></td>"
                        "<td class='questionDate'>11/06/2026 08:00 AM MST</td><td class='answerDate'>11/06/2026 01:00 PM MST</td></tr>"
                        "<div class='mets-pagination'><span class='mets-total-elements-display'>1 results found</span></div>"
                        if os.environ.get("FAKE_QA") else "")
                pane = ("<div id='innerTabContent'><form id='questionsAnswersSearchForm' class='content-block'>"
                        "<h2 class='content-block-title'>Questions &amp; Answers</h2>"
                        "<div class='mets-field'><span class='mets-field-label'>Question Acceptance Deadline</span>"
                        "<div class='mets-field-body'>11/17/2026 12:00 AM MST ( 10d 16h 10m )</div></div><div class='mets-field'>"
                        f"<span class='mets-field-label'>Closing Date</span><div class='mets-field-body'>{_ahead(21)} 02:00 PM MST</div></div>"
                        "<table class='qnaTable'><thead><tr><th class='questionNo'>No <span class='accessibility-hidden'>Arrow Up</span></th>"
                        "<th class='questionAnswer'>Question/Answer</th><th>Question Date</th><th>Answer Date</th></tr></thead><tbody>"
                        f"{rows}<tr class='mets-table-row-empty'><td colspan='4'>No results match your criteria.</td></tr></tbody></table>"
                        "</form></div>")
            return self._send(f"<h1>Bid</h1><div>Closing Date {_ahead(21)}</div><p>MANDATORY pre-bid site walk on {_ahead(3)} at 9 AM.</p>"
                              f"{docs}{tabs}{pane}<footer><p>Print Options</p><p>Terms of Use</p></footer>")
        if p.startswith("/dl/missing"):
            return self._send("not found", 404)
        if p.startswith("/dl/"):
            if not self._authed():
                return self._send("login required", 403)
            body = b"%PDF-1.4 fake " + p.rsplit("/", 1)[-1].encode() + (b" rev2" if os.environ.get("FAKE_REV") else b"")
            return self._send(body, headers={"Content-Disposition": f"attachment; filename={p.rsplit('/', 1)[-1]}"},
                              ctype="application/pdf")
        return self._send("not found", 404)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        f = parse_qs(self.rfile.read(n).decode())
        if self.path.startswith("/public/authentication/login"):
            LOGIN_POSTS["n"] += 1
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
            hop = int(os.environ.get("FAKE_SSO_HOP_MS") or 0)
            if hop:
                # like BidNet's Shibboleth hop: an IdP page that posts the SAML response back by script, later
                return self._send("<html><head><title>Fake BidNet IdP</title></head>"
                                  f"<body onload=\"setTimeout(function(){{document.forms[0].submit()}}, {hop})\">"
                                  "<p>Signing you in...</p><form method='post' action='/sso/acs'>"
                                  f"<input type='hidden' name='SAMLResponse' value='{sid}'></form></body></html>")
            SESSIONS.add(sid)
            return self._send("", 302, {"Location": "/colorado", "Set-Cookie": f"sid={sid}; Path=/"})
        if self.path.startswith("/public/authentication/code"):
            if f.get("code") == [CODES["last"]]:
                sid = f"s{LOGINS['n']}"
                SESSIONS.add(sid)
                return self._send("", 302, [("Location", "/colorado"), ("Set-Cookie", f"sid={sid}; Path=/"),
                                            ("Set-Cookie", "device_ok=1; Path=/")])
            return self._send("<p>Enter the confirmation code we emailed you. That code was wrong.</p>", 401)
        if "j_password" in f:  # wrong password: back to a login form with an error, like BidNet's sign-on server
            BAD["n"] += 1
            return self._send("<html><head><title>Login | Fake BidNet Direct</title></head><body>"
                              "<p class='error'>Invalid username or password.</p><form method='post' action='/public/authentication/login'>"
                              "<input name='j_username'><input name='j_password' type='password'><button type='submit'>Log in</button>"
                              "</form></body></html>", 401)
        if self.path.startswith("/sso/acs"):
            sid = (f.get("SAMLResponse") or [""])[0]
            SESSIONS.add(sid)
            return self._send("", 302, {"Location": "/colorado", "Set-Cookie": f"sid={sid}; Path=/"})
        return self._send("bad login", 401)


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}"
bidnet.BASE, bidnet.LOGIN_URL, bidnet.CO_OPEN = BASE, BASE + "/public/authentication/login", BASE + "/colorado/solicitations/open-bids"
os.environ["BIDNET_USER"], os.environ["BIDNET_PASS"] = USER, PW

from scripts.bidwatch.browser import Browser, PortalSession  # noqa: E402
import scripts.bidwatch.browser as _brmod  # noqa: E402

_brmod.DEBUG_DIR = TMP / "debug"  # fake-portal debug dumps stay out of the real bids/_watch/debug

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
# a fresh login that worked starts the login gap (default 3 h); like the cool-down file, each test that needs a
# fresh login clears it first so the tests stay independent (the gap itself is tested after the cool-down)
common.BIDNET_LAST_LOGIN_FILE.unlink(missing_ok=True)
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
SESSIONS.clear()  # the session times out again; this time the login goes through a slow single-sign-on hop
os.environ["FAKE_SSO_HOP_MS"] = "4500"
common.BIDNET_LAST_LOGIN_FILE.unlink(missing_ok=True)
s4 = PortalSession(b, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
check("slow SSO redirect chain (IdP posts back by script after 4.5 s): login waits for it, attempt 1 succeeds",
      s4.ensure_login() and s4.login_note == "logged in (attempt 1)", s4.login_note)
del os.environ["FAKE_SSO_HOP_MS"]
s4.close()


def _leaky_login(page, u, p):
    raise RuntimeError(f"fill('#loginBox_j_password', '{p}') timed out for {u}")


s5 = PortalSession(b, "scrubtest", _leaky_login, lambda page: False, bidnet.CREDS)
check("a login error never carries the password or user into the note (health.json is committed)",
      not s5.ensure_login(attempts=1) and PW not in s5.login_note and USER not in s5.login_note
      and "***" in s5.login_note, s5.login_note)
s5.close()
_tries = {"n": 0}


def _flaky_login(page, u, p):
    _tries["n"] += 1
    if _tries["n"] == 1:
        raise RuntimeError("Unable to retrieve content because the page is navigating")


class _SsoRestoredPage:
    """Stands in for a page where single sign-on restored the session while the login window was being opened."""

    def locator(self, sel):
        logged_in_sel = sel == bidnet.LOGGED_IN_SEL
        return type("L", (), {"count": lambda self_: 1 if logged_in_sel else 0})()

    def click(self, *a, **k):
        raise RuntimeError("not clickable")

    def wait_for_selector(self, *a, **k):
        raise RuntimeError("Timeout 5000ms exceeded")

    def wait_for_timeout(self, ms):
        pass

    def wait_for_load_state(self, *a, **k):
        pass

    def evaluate(self, *a, **k):
        raise RuntimeError("Error: Page.evaluate: Error: login form not found\n    at eval (eval at evaluate (:370:30))")


try:
    bidnet._submit_login_window(_SsoRestoredPage(), USER, PW)
    _sso_ok = True
except Exception as _e:  # noqa: BLE001
    _sso_ok = repr(_e)
check("login form gone because single sign-on already restored the session: treated as logged in, no error", _sso_ok is True, _sso_ok)


def _multiline_fail(page, u, p):
    raise RuntimeError("Error: login form not found\n    at eval (eval at evaluate (:370:30))\n    at UtilityScript")


s6b = PortalSession(b, "multiline", _multiline_fail, lambda page: False, bidnet.CREDS)
s6b.ensure_login(attempts=1)
check("login notes are one line (a stack trace broke the report table)", "\n" not in s6b.login_note, s6b.login_note)
from scripts.bidwatch import run as _run_ol  # noqa: E402

check("report cells and error bullets stay on one line (a 504 page's HTML broke the Errors list)",
      _run_ol._one_line("HTTP 504 <html>\n<head><title>504 Gateway Time-out</title></head>\n</html>") ==
      "HTTP 504 <html> <head><title>504 Gateway Time-out</title></head> </html>" and _run_ol._one_line("a | b") == "a / b")
s6b.close()
s6 = PortalSession(b, "retrytest", _flaky_login, lambda page: _tries["n"] >= 2, bidnet.CREDS)
check("a retried login records why the previous attempt failed",
      s6.ensure_login() and s6.login_note.startswith("logged in (attempt 2); previous attempt: RuntimeError: Unable"),
      s6.login_note)
s6.close()
b.close()

# full scan against the fake site, with temp state files
from scripts.bidwatch import run  # noqa: E402

run.samgov_bulk.URL = "http://127.0.0.1:1/no-bulk-file-in-tests"  # part 5 serves a fake one
for name in ["OPEN_BIDS_FILE", "HEALTH_FILE", "REPORT_FILE", "WATCHLIST_FILE", "LAST_SCAN_FILE"]:
    setattr(run, name, TMP / f"{name}.json")
LAST_SCAN = TMP / "LAST_SCAN_FILE.json"
(TMP / "WATCHLIST_FILE.json").write_text('{"bids":[{"name":"Littleton 2126","source":"bidnet","match":"\\\\b2126\\\\b"}]}')
run.HOSTS["bidnet"] = BASE + "/colorado"
run.bidnet.download_docs.__globals__["DOWNLOAD_DIR"] = TMP / "downloads"
r1 = run.scan(["bidnet"])
rep = (TMP / "REPORT_FILE.json").read_text()
check("scan sees 3 open bids", r1["health"]["bidnet"]["count"] == 3, r1["health"]["bidnet"])
check("scan matches HVAC + plumbing, excludes paving", r1["health"]["bidnet"]["matches"] == 2, r1["health"]["bidnet"]["matches"])
check("mandatory walk extracted", any((x.get("prebid") or {}).get("mandatory") for x in r1["found"].values()))
check("watched bid flagged", any(x.get("watched") for x in r1["found"].values()))
check("a long-closed bid that BidNet still lists is not open (never reported as NEW)",
      not run._is_open({"closing": "2021-12-15"}) and run._is_open({"closing": "2099-01-01"}) and run._is_open({"closing": None}))
check("watched bid docs downloaded when logged in", any(r1["downloads"].values()), r1["downloads"])
check("report has source health + all open", "## Source health" in rep and "All open matching bids" in rep)
# LAST_SCAN.md: the operator's six-line digest, written next to the report on every scan
_ls = LAST_SCAN.read_text()
_ls_labels = [ln.split(":")[0] for ln in _ls.splitlines()[1:] if not ln.startswith("  - ")]
check("LAST_SCAN.md written: a heading with the scan's UTC time, then the six labelled lines in order, nothing else",
      _ls.splitlines()[0] == f"# Last scan {r1['started']}" and _ls_labels == ["Logged in", "Counts", "New matching bids",
                                                                                "Changes on watched bids", "Documents downloaded", "Errors"]
      and "|---" not in _ls, _ls)
check("LAST_SCAN.md: BidNet logged in with its note; open/matching per source and in total; no BLIND marker on a clean scan",
      _ls.splitlines()[1].startswith("Logged in: yes (") and r1["health"]["bidnet"]["logged_in"]
      and "Counts: bidnet 3/2 | samgov -/- | coloradovss -/- | bonfire -/- | total 3/2" in _ls and "BLIND" not in _ls, _ls)
check("LAST_SCAN.md: first sight of the two matching bids lists them as new (not in the previous open_bids.json), watched flag read",
      "New matching bids: 2" in _ls
      and re.search(r"^  - bidnet 0000500001 \| HVAC Maintenance Services \| [^|]*\| closes \d{4}-\d{2}-\d{2} \| brownbison \| watched no$", _ls, re.M)
      and re.search(r"^  - bidnet 0000500002 \| On-Call Commercial Plumbing Services RFQ 2126 \| [^|]*\| closes \d{4}-\d{2}-\d{2} \| brownbison \| watched yes$",
                    _ls, re.M), _ls)
check("LAST_SCAN.md: the downloaded document is listed under the bid's source:id (no bid folder in the watchlist yet)",
      "Changes on watched bids: 0" in _ls and "Documents downloaded: 1" in _ls and "  - bidnet:0000500002: RFQ.pdf" in _ls, _ls)
check("LAST_SCAN.md: the Errors line ends with the exit code; the same text comes back for the log",
      re.search(r"^Errors: (none|.+; first: .+); exit code 0$", _ls.rstrip().splitlines()[-1]) and r1["last_scan"] == _ls, _ls)
os.environ["FAKE_ADDENDUM"] = "1"
r2 = run.scan(["bidnet"])
ch = [c for c in r2["changed"].values() if any("NEW DOCUMENTS" in d for d in c["diffs"])]
check("second scan detects addendum on watched bid", bool(ch), r2["changed"])
check("second scan: nothing falsely NEW", not r2["new"], list(r2["new"]))
_ls2 = LAST_SCAN.read_text()
check("LAST_SCAN.md next scan: the bids seen before are not new again; the addendum is a change on the watched bid and a download",
      "New matching bids: 0" in _ls2 and "  - bidnet 0000500001 |" not in _ls2 and f"Changes on watched bids: {len(r2['changed'])}" in _ls2
      and "  - **On-Call Commercial Plumbing Services RFQ 2126** (bidnet): NEW DOCUMENTS (addendum?): Addendum 1.pdf" in _ls2
      and "Documents downloaded: 1" in _ls2 and "  - bidnet:0000500002: Addendum 1.pdf" in _ls2, _ls2)
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
check("fully blind source: report says BLIND and last_success keeps its old time",
      r3["health"]["samgov"].get("blind") is True and r3["health"]["samgov"].get("last_success") != r3["started"]
      and "BLIND this run" in (TMP / "REPORT_FILE.json").read_text(), r3["health"]["samgov"])
_ls3 = LAST_SCAN.read_text()
check("LAST_SCAN.md on a blind source: the BLIND marker with its last good time after the carried-forward count, the errors "
      "counted with the first one quoted, exit code 3 (degraded)",
      "Counts: bidnet 3/2 | samgov 1/1 (BLIND, last good never) |" in _ls3 and "| total 4/3" in _ls3
      and re.search(r"^Errors: (bidnet \d+, )?samgov \d+; first: \w+: .+; exit code 3$", _ls3.rstrip().splitlines()[-1]), _ls3)
r4 = run.scan(["bidnet"])
check("source not in this run: rows kept and health row marked not scanned",
      "samgov:seed1" in r4["found"] and r4["health"]["samgov"].get("not_scanned_this_run") is True
      and "NOT SCANNED THIS RUN" in (TMP / "REPORT_FILE.json").read_text(), r4["health"].get("samgov"))
# robot-check cool-down: BidNet skipped, previous rows kept, nothing closed
until = bidnet.start_cooldown()
check("cool-down recorded", bidnet.cooldown_until() == until, until)
_cd_before = (bidnet.cooldown_until(), str(common.BIDNET_COOLDOWN_FILE), common.BIDNET_COOLDOWN_FILE.exists(),
              run.health_check(["bidnet"])["bidnet"]["reachable"])
r5 = run.scan(["bidnet"])
check("during cool-down BidNet is not contacted and its rows are carried forward",
      "COOL-DOWN" in (r5["health"]["bidnet"]["login_note"] or "") and not r5["closed"]
      and any(k.startswith("bidnet:") for k in r5["found"]),
      (r5["health"]["bidnet"].get("login_note"), list(r5["closed"]), _cd_before, bidnet.__file__, run.bidnet is bidnet))
common.BIDNET_COOLDOWN_FILE.unlink()
check("cool-down cleared", bidnet.cooldown_until() is None)

# fresh-login gap (2026-10-30 06:37Z: the 4th fresh login in ~6 h tripped the robot check): a valid saved session is
# reused at any time; an expired one gets no new password until BIDWATCH_BIDNET_LOGIN_GAP_H (default 3) hours after
# the last fresh login, and meanwhile BidNet is skipped like a cool-down
import datetime as _dtg  # noqa: E402

os.environ.pop("BIDWATCH_BIDNET_LOGIN_GAP_H", None)


def _set_last_login(hours_ago: float) -> str:
    t = common.iso(common.now_utc() - _dtg.timedelta(hours=hours_ago))
    common.BIDNET_LAST_LOGIN_FILE.write_text(t)
    return t


_t1h = _set_last_login(1)
_p0, _l0 = LOGIN_POSTS["n"], HITS2["list"]
r5b = run.scan(["bidnet"])
_hb = r5b["health"]["bidnet"]
check("login gap (c): a still-valid session is reused although the last fresh login was 1 h ago; no password sent",
      _hb["logged_in"] and _hb["login_note"] == "session reused" and LOGIN_POSTS["n"] == _p0 and HITS2["list"] > _l0
      and not _hb.get("login_deferred") and common.BIDNET_LAST_LOGIN_FILE.read_text() == _t1h, (_hb["login_note"], LOGIN_POSTS))
SESSIONS.clear()  # BidNet times the session out
_prev_bn = {k for k in json.loads((TMP / "OPEN_BIDS_FILE.json").read_text())["bids"] if k.startswith("bidnet:")}
_p0, _l0, _d0 = LOGIN_POSTS["n"], HITS2["list"], HITS2["detail"]
r5c = run.scan(["bidnet"])
_hc = r5c["health"]["bidnet"]
_until = common.iso(_dtg.datetime.fromisoformat(_t1h) + _dtg.timedelta(hours=3))
_rep = (TMP / "REPORT_FILE.json").read_text()
check("login gap (a): expired session + last fresh login 1 h ago -> no POST to the login endpoint, lists and details "
      "not read", LOGIN_POSTS["n"] == _p0 and HITS2["list"] == _l0 and HITS2["detail"] == _d0 and not _hc["logged_in"],
      (LOGIN_POSTS, HITS2, _hc["login_note"]))
check("login gap (a): health and report say the login was deferred and when the next one is allowed",
      _hc["login_note"].startswith(f"login deferred: last fresh login {_t1h}, next allowed after {_until}")
      and _hc.get("login_deferred") is True and f"next allowed after {_until}" in _rep
      and "BLIND: bidnet (login deferred on purpose)" in _rep, (_hc["login_note"], _until))
check("login gap (a): earlier BidNet rows carried forward, none marked closed, last-login time untouched",
      len(_prev_bn) == 3 and all(r5c["found"].get(k, {}).get("carried_forward") for k in _prev_bn) and not r5c["closed"]
      and _hc.get("carried_forward") and common.BIDNET_LAST_LOGIN_FILE.read_text() == _t1h,
      (_prev_bn, list(r5c["closed"]), _hc))
_ls5c = LAST_SCAN.read_text()
check("LAST_SCAN.md on a deferred BidNet login: 'no: login deferred ...', BidNet BLIND with its carried rows, exit code 0 (a skip)",
      f"Logged in: no: login deferred: last fresh login {_t1h}, next allowed after {_until}" in _ls5c
      and re.search(r"bidnet 3/2 \(BLIND, last good 20\d\d-", _ls5c) and _ls5c.rstrip().endswith("; exit code 0"), _ls5c)
_t4h = _set_last_login(4)
_p0, _n0 = LOGIN_POSTS["n"], LOGINS["n"]
r5d = run.scan(["bidnet"])
_hd = r5d["health"]["bidnet"]
_last = common.BIDNET_LAST_LOGIN_FILE.read_text()
check("login gap (b): last fresh login 4 h ago -> the password login goes ahead and BidNet is read again",
      LOGIN_POSTS["n"] == _p0 + 1 and LOGINS["n"] == _n0 + 1 and _hd["logged_in"] and _hd["count"] == 3
      and not _hd.get("carried_forward") and not _hd.get("login_deferred"), (LOGIN_POSTS, _hd))
check("login gap (b): a fresh login that worked updates the last-login time",
      _last > _t4h and (common.now_utc() - _dtg.datetime.fromisoformat(_last)).total_seconds() < 600, (_t4h, _last))
_set_last_login(1)
_gap = []
for _v in ("0", "0.5", "5", "nonsense", "-2"):
    os.environ["BIDWATCH_BIDNET_LOGIN_GAP_H"] = _v
    _gap.append(bool(bidnet.login_deferred_until()))
os.environ.pop("BIDWATCH_BIDNET_LOGIN_GAP_H")
check("BIDWATCH_BIDNET_LOGIN_GAP_H: 0 turns the gap off, a gap shorter than 1 h has passed, 5 h holds, a bad value "
      "means the 3 h default", _gap == [False, False, True, True, True], _gap)
common.BIDNET_LAST_LOGIN_FILE.unlink()

# A bid that became watched after its documents were first listed: its files are fetched because they are
# missing on disk, then filed into the bid folder the watchlist names (CLAUDE.md rule 0c).
_REPO0 = run.REPO
run.REPO = TMP / "repo"
_bf = run.REPO / "bids/littleton-2126"
(_bf / "docs").mkdir(parents=True)
(_bf / "docs/RFQ-saved-by-Luke.pdf").write_bytes(b"%PDF-1.4 fake rfq.pdf")  # same bytes as the portal's RFQ.pdf
(TMP / "WATCHLIST_FILE.json").write_text(json.dumps({"bids": [{"name": "Littleton 2126", "source": "bidnet",
                                                               "match": "\\b2126\\b", "folder": "bids/littleton-2126"}]}))
import shutil as _sh  # noqa: E402

_sh.rmtree(TMP / "downloads" / "bidnet", ignore_errors=True)
r8 = run.scan(["bidnet"])
_got = sorted(Path(f).name for fs in r8["downloads"].values() for f in fs)
check("watched bid: documents missing on disk are downloaded although the document list did not change",
      _got == ["Addendum 1.pdf", "RFQ.pdf"], r8["downloads"])
check("filed into the bid folder; bytes already there under another name are not copied again",
      sorted(x.name for x in (_bf / "docs").iterdir()) == ["Addendum 1.pdf", "RFQ-saved-by-Luke.pdf"]
      and r8["filed"] == ["bids/littleton-2126/docs/Addendum 1.pdf"], (r8["filed"], sorted((_bf / "docs").iterdir())))
check("report lists what was filed", "## Filed into bid folders" in (TMP / "REPORT_FILE.json").read_text())
_ls8 = LAST_SCAN.read_text()
check("LAST_SCAN.md names the bid folder the watchlist gives for each downloaded file",
      "Documents downloaded: 2" in _ls8 and "  - bids/littleton-2126: Addendum 1.pdf" in _ls8 and "  - bids/littleton-2126: RFQ.pdf" in _ls8, _ls8)
r9 = run.scan(["bidnet"])
check("next scan: nothing downloaded or filed twice", not r9["downloads"] and not r9["filed"], (r9["downloads"], r9["filed"]))
os.environ["FAKE_REV"] = "1"
[Path(f) for fs in r8["downloads"].values() for f in fs if f.endswith("Addendum 1.pdf")][0].unlink()
r10 = run.scan(["bidnet"])
check("a revised file with the same name is filed next to the original, dated",
      any(f.startswith("bids/littleton-2126/docs/Addendum 1 (rev ") for f in r10["filed"]), r10["filed"])
del os.environ["FAKE_REV"]
run.REPO = _REPO0

# code-review fixes (2026-10-20 07:30 UTC)
# (c) a stale password is submitted once, then held back; new credentials are tried at once
SESSIONS.clear()
common.BIDNET_LAST_LOGIN_FILE.unlink(missing_ok=True)
os.environ["BIDNET_PASS"] = "stale-password"
b2 = Browser()
s7 = PortalSession(b2, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
check("rejected password: one submission, no retries, BLOCKED with the reason",
      not s7.ensure_login() and BAD["n"] == 1 and "rejected" in s7.login_note and "stale-password" not in s7.login_note,
      (BAD, s7.login_note))
s7.close()
s8 = PortalSession(b2, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
check("same rejected password next run: not submitted again", not s8.ensure_login() and BAD["n"] == 1
      and "not submitting them again" in s8.login_note, (BAD, s8.login_note))
s8.close()
check("the hold stores a hash, never the password", "stale-password" not in bidnet.BAD_CREDS_MARKER.read_text())
os.environ["BIDNET_PASS"] = PW
s9 = PortalSession(b2, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
check("new password: tried at once and the hold is cleared",
      s9.ensure_login() and not bidnet.BAD_CREDS_MARKER.exists() and BAD["n"] == 1, (s9.login_note, BAD))
s9.close()
# (c) a failed attempt whose page turns out logged in is not followed by a second password submission
_calls = {"login": 0, "check": 0}


def _slow_login(page, u, p):
    _calls["login"] += 1
    raise RuntimeError("Timeout 30000ms exceeded while the sign-on redirect was still running")


def _late_check(page):
    _calls["check"] += 1
    return _calls["check"] >= 2  # logged out before the attempt, logged in once the redirect finished


s10 = PortalSession(b2, "recheck", _slow_login, _late_check, bidnet.CREDS)
check("a login that finished late is confirmed on re-check, password submitted once",
      s10.ensure_login() and _calls["login"] == 1 and "confirmed on re-check" in s10.login_note, (_calls, s10.login_note))
s10.close()
b2.close()

# (a) a row BidNet labels closed counts toward the site's total but is never returned as open
_closed_html = ("""<table><tr class="mets-table-row"><td><a class="solicitation-link" href="/colorado/solicitations/open-bids/A/0000700001">Open HVAC job</a>
<span class="sol-closing-date open"><span class="date-label">Closing</span><span class="date-value">11/10/2026</span></span></td></tr>
<tr class="mets-table-row"><td><a class="solicitation-link" id="2289300002" href="/private/supplier/interception/open-notice/2289300002?target=view">Janitorial Services for the Pagosa Ranger District</a>
<span class="sol-closing-date closed"><span class="date-label">Closed Bid</span><span class="date-value">12/15/2021</span></span></td></tr></table>""")
_rows, _ = bidnet.parse_listing(_closed_html, bidnet.BASE)
_t = {}
_kept = bidnet._drop_closed({r["id"]: r for r in _rows}, _t)
check("BidNet 'Closed Bid' rows are parsed, counted, then dropped", len(_rows) == 2 and list(_kept) == ["0000700001"]
      and _t.get("_closed_listed") == 1, (_rows, _t))

# (e) watch patterns match the title and solicitation number, never the URL
_ws = run._WatchSet([{"name": "Jeffco 26-18863AP", "source": "bidnet", "match": "18863|dome glass"}])
_ws3 = run._WatchSet([{"name": "by id", "source": "bidnet", "id": "1", "match": "zzz-no-match", "folder": "bids/x"},
                      {"name": "by pattern", "source": "bidnet", "match": "003-27|mowing services"}])
_e3 = _ws3.entry({"source": "bidnet", "id": "1", "title": "003-27 RFP - Mowing Services - Groups 2, 5, 7 & 8"})
check("a bid watched twice (id and pattern): the id entry wins, the pattern entry still counts as seen",
      _e3 and _e3["name"] == "by id" and "by pattern" in _ws3.hits, (_e3, _ws3.hits))
check("a short solicitation number no longer matches a BidNet id inside a URL",
      not _ws.check({"source": "bidnet", "id": "444188638946", "title": "Flood Assessment and Preliminary Design Services",
                     "url": "https://www.bidnetdirect.com/private/supplier/interception/open-notice/444188638946?target=view"})
      and _ws.check({"source": "bidnet", "id": "1", "title": "26-18863AP-FM Dome Glass Replacement", "url": ""}))

# (b) a failed or thin detail page keeps the documents and pre-bid an earlier scan read
import types as _types  # noqa: E402

_old = {"source": "bidnet", "id": "9", "title": "Watched HVAC bid 26-77", "documents": [{"name": "RFP.pdf", "url": "u"}],
        "prebid": {"date": "2026-11-01", "mandatory": True}, "sol": "26-77", "last_seen": "x"}
_ws2 = run._WatchSet([{"name": "w", "source": "bidnet", "match": "26-77"}])
_ses = _types.SimpleNamespace(logged_in=False)
_h = {"errors": []}
for _label, _enrich in (("thin page", lambda ses, b: {**b, "documents": [], "prebid": None}),
                        ("failed page", lambda ses, b: (_ for _ in ()).throw(RuntimeError("docs tab did not load")))):
    _found = {"bidnet:9": {"source": "bidnet", "id": "9", "title": "Watched HVAC bid 26-77", "url": "u"}}
    run._enrich_and_download(_ses, _types.SimpleNamespace(enrich=_enrich), _found, "bidnet", profiles, _ws2,
                             {"bidnet:9": _old}, True, {}, _h)
    _r = _found["bidnet:9"]
    check(f"{_label}: earlier documents and pre-bid are kept (no false addendum next scan)",
          _r.get("documents") == _old["documents"] and _r.get("prebid") == _old["prebid"], _r)
_found = {"bidnet:8": {"source": "bidnet", "id": "8", "title": "HVAC Maintenance Services", "url": "u"}}
_old8 = {**_found["bidnet:8"], "documents": [{"name": "RFP.pdf", "url": "u"}], "prebid": {"date": "2026-11-02", "mandatory": True}}
run._enrich_and_download(_ses, _types.SimpleNamespace(enrich=lambda ses, b: 1 / 0), _found, "bidnet", profiles,
                         run._WatchSet([]), {"bidnet:8": _old8}, True, {}, _h)
check("logged out (e.g. a mid-scan re-login deferred): an unwatched match is not opened but keeps its earlier detail",
      _found["bidnet:8"].get("prebid") == _old8["prebid"] and _found["bidnet:8"].get("documents") == _old8["documents"],
      _found["bidnet:8"])

# second review pass (2026-10-20 07:50 UTC)
(TMP / "WATCHLIST_FILE.json").write_text('{"bids":[{"name":"Littleton 2126","source":"bidnet","match":"\\\\b2126\\\\b"}]}')
common.BIDNET_COOLDOWN_FILE.unlink(missing_ok=True)
os.environ["FAKE_ROBOT_DETAIL"] = "1"
_d0 = HITS2["detail"]
r11 = run.scan(["bidnet"])
_h11 = r11["health"]["bidnet"]
check("robot check on a detail page: the pass stops at the first one, cool-down starts, stored detail kept",
      HITS2["detail"] - _d0 == 1 and bidnet.cooldown_until() and any("blocked" in e for e in _h11["errors"])
      and r11["found"]["bidnet:0000500002"].get("documents"), (HITS2, _d0, _h11["errors"]))
check("robot check on a detail page: the health note / cycle line says it hit an enrichment page, not the login form",
      "CHALLENGED on an enrichment page, not the login form: BidNet robot check on a detail page" in (_h11.get("login_note") or "")
      and not (_h11.get("login_note") or "").startswith("CHALLENGED"), _h11.get("login_note"))
del os.environ["FAKE_ROBOT_DETAIL"]
common.BIDNET_COOLDOWN_FILE.unlink(missing_ok=True)
os.environ["FAKE_ROBOT_LIST"] = "1"
_d0 = HITS2["detail"]
r12 = run.scan(["bidnet"])
check("robot check on the list: no detail pages or downloads; earlier rows and their detail carried forward",
      HITS2["detail"] == _d0 and r12["found"].get("bidnet:0000500002", {}).get("documents") and not r12["closed"],
      (r12["health"]["bidnet"]["errors"], list(r12["closed"])))
del os.environ["FAKE_ROBOT_LIST"]
common.BIDNET_COOLDOWN_FILE.unlink(missing_ok=True)

SESSIONS.clear()
os.environ["FAKE_ROBOT_HOME"] = "1"
_hh0, _bad0 = HITS2["home"], BAD["n"]
b3 = Browser()
s11 = PortalSession(b3, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
check("robot check on the login page: BLOCKED at once, no password sent, no retries, cool-down",
      not s11.ensure_login() and "robot check" in s11.login_note and HITS2["home"] - _hh0 == 2 and BAD["n"] == _bad0
      and bidnet.cooldown_until(), (s11.login_note, HITS2))
s11.close()
del os.environ["FAKE_ROBOT_HOME"]
common.BIDNET_COOLDOWN_FILE.unlink(missing_ok=True)

s12 = PortalSession(b3, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
_o, _e, _tt = {}, [], {}
_l0 = HITS2["list"]
bidnet._walk(s12, "statewide STUCK", f"{bidnet.CO_OPEN}?selectedContent=STUCK", _o, _e, _tt, 40)
check("paging stops when the site serves a page this walk already had", HITS2["list"] - _l0 == 2 and len(_o) == 2,
      (HITS2["list"] - _l0, len(_o)))
_tabs = bidnet.CO_TABS
bidnet.CO_TABS = ["BUYER", "BROKEN"]
_k0 = KW_HITS["n"]
_r2, _e2, _t2 = bidnet.collect_open(s12, ["hvac", "boiler"])
check("a failed statewide tab skips the keyword searches (carry-forward covers it)",
      KW_HITS["n"] == _k0 and _t2.get("_complete") is False, (KW_HITS["n"] - _k0, _e2))
bidnet.CO_TABS = ["BUYER"]
_tc = bidnet.total_count
bidnet.total_count = lambda html: 99 if "Open Solicitations" in html else _tc(html)
_k0 = KW_HITS["n"]
bidnet.collect_open(s12, [f"kw{i}" for i in range(20)])
bidnet.total_count = _tc
bidnet.CO_TABS = _tabs
check("a short list runs at most 12 keyword searches per scan", KW_HITS["n"] - _k0 == 12, KW_HITS["n"] - _k0)
s12.close()
b3.close()

os.environ["FAKE_MISSING_DOC"] = "1"
common.BIDNET_LAST_LOGIN_FILE.unlink(missing_ok=True)  # the session expired at the robot-check test: log in again
r13 = run.scan(["bidnet"])
check("a document that does not download is reported (and tried again next scan)",
      any("not downloaded yet" in e for e in r13["health"]["bidnet"]["errors"]), r13["health"]["bidnet"]["errors"])
del os.environ["FAKE_MISSING_DOC"]

# Communication + Q & A tabs on watched bids (2026-11-05 15:48 MST: a walkthrough-time change on 0000440322 was posted
# only on the Communication tab, no addendum, so the Documents diff never saw it)
_W = "bidnet:0000500002"  # the watched Littleton bid on the fake site
_bid = {"source": "bidnet", "id": "0000500002", "title": "On-Call Commercial Plumbing Services RFQ 2126",
        "url": BASE + "/colorado/city-of-littleton/solicitations/On-Call-Commercial-Plumbing-Services-2126/0000500002"}
b4 = Browser()
s13 = PortalSession(b4, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
s13.ensure_login()
_c0, _q0 = HITS2["comm"], HITS2["qa"]
_e = bidnet.enrich(s13, {**_bid, "watched": True})
check("logged in + watched: both tabs read; empty Communication tab stores nothing, Q & A keeps its deadline and zero items",
      s13.logged_in and HITS2["comm"] == _c0 + 1 and HITS2["qa"] == _q0 + 1 and "communications" not in _e
      and _e.get("qa") == {"questions_deadline": "2026-11-17", "items": [], "total": None} and _e.get("prebid") and _e.get("documents"), _e)
os.environ["FAKE_COMM"], os.environ["FAKE_QA"] = "1", "1"
_e = bidnet.enrich(s13, {**_bid, "watched": True})
check("enrich picks up the notice and the answered question",
      _e.get("communications") == [{"no": "1", "date": "11/05/2026 03:48 PM MST", "text": COMM_TEXT}]
      and _e.get("qa") == {"questions_deadline": "2026-11-17", "total": 1,
                           "items": [{"no": "Q1", "question": "Walkthrough: Is the walkthrough mandatory?", "answer": "Yes, attendance is mandatory.",
                                      "question_date": "2026-11-06", "answer_date": "2026-11-06"}]}, _e)
_c0, _q0 = HITS2["comm"], HITS2["qa"]
_e = bidnet.enrich(s13, _bid)
_e2 = bidnet.enrich(_types.SimpleNamespace(logged_in=False, page=s13.page, debug_dump=lambda tag: None), {**_bid, "watched": True})
check("an unwatched match, or a logged-out session, never opens the tabs",
      HITS2["comm"] == _c0 and HITS2["qa"] == _q0 and "communications" not in _e and "qa" not in _e and "qa" not in _e2, (_e, _e2))
os.environ["FAKE_TAB_DOWN"] = "1"
_e = bidnet.enrich(s13, {**_bid, "watched": True})
check("a tab that fails to load costs nothing from the main page and stores no tab fields",
      _e.get("prebid") and _e.get("documents") and "communications" not in _e and "qa" not in _e, _e)
del os.environ["FAKE_TAB_DOWN"]
s13.close()
b4.close()
# the full scan: the lines reach the report once, stay stored, survive a blind scan and a broken tab
r15 = run.scan(["bidnet"])
_rep = (TMP / "REPORT_FILE.json").read_text()
_line = 'NEW COMMUNICATION No.1 11/05/2026 03:48 PM MST: "Please note that the walkthrough time has changed from 9 am to 10:30 am.'
check("first sight: the notice and the answer are in the report's changes for the watched bid",
      _line in _rep and 'NEW Q&A: 1 answered: "Yes, attendance is mandatory."' in _rep
      and any(x.startswith("NEW COMMUNICATION") for x in r15["changed"].get(_W, {}).get("diffs", [])), (r15["changed"], _rep[-1500:]))
_ob = json.loads((TMP / "OPEN_BIDS_FILE.json").read_text())["bids"][_W]
check("open_bids.json keeps the tabs", len(_ob.get("communications") or []) == 1 and len((_ob.get("qa") or {}).get("items") or []) == 1, _ob)
r16 = run.scan(["bidnet"])
check("unchanged next scan: not reported again", _W not in r16["changed"] and "NEW COMMUNICATION" not in (TMP / "REPORT_FILE.json").read_text(),
      r16["changed"])
os.environ["FAKE_COMM"] = "2"
r17 = run.scan(["bidnet"])
_d17 = r17["changed"].get(_W, {}).get("diffs", [])
check("a second notice: only No.2 reported", _d17 == ['NEW COMMUNICATION No.2 11/06/2026 03:48 PM MST: "Addendum 2 posted."'], _d17)
os.environ["FAKE_ROBOT_LIST"] = "1"
r18 = run.scan(["bidnet"])
_cf = r18["found"].get(_W, {})
check("BidNet blind (robot check on the list): both tabs carried forward with the row, nothing reported",
      _cf.get("carried_forward") and len(_cf.get("communications") or []) == 2 and (_cf.get("qa") or {}).get("items") and _W not in r18["changed"],
      (_cf.get("communications"), _cf.get("qa"), r18["changed"]))
del os.environ["FAKE_ROBOT_LIST"]
common.BIDNET_COOLDOWN_FILE.unlink(missing_ok=True)
os.environ["FAKE_TAB_DOWN"] = "1"
r19 = run.scan(["bidnet"])
_cf = r19["found"].get(_W, {})
check("tabs down this scan: the main page is read, last scan's notices and answers are kept, no false NEW next time",
      not _cf.get("carried_forward") and _cf.get("detail_at", "") >= r19["started"] and len(_cf.get("communications") or []) == 2
      and (_cf.get("qa") or {}).get("items") and _W not in r19["changed"], (_cf.get("communications"), _cf.get("qa"), r19["changed"]))
del os.environ["FAKE_TAB_DOWN"]
os.environ["FAKE_ROBOT_TAB"] = "1"
r20 = run.scan(["bidnet"])
_cf = r20["found"].get(_W, {})
check("robot check on a tab: detail pass stops, cool-down starts, stored tabs kept",
      bidnet.cooldown_until() and any("blocked" in e and "Communication tab" in e for e in r20["health"]["bidnet"]["errors"])
      and len(_cf.get("communications") or []) == 2 and _W not in r20["changed"], (r20["health"]["bidnet"]["errors"], _cf.get("communications")))
check("robot check on a tab: the health note names the tab, not the login form (the cycle line read 'session reused' on 2026-11-06)",
      r20["health"]["bidnet"]["logged_in"] and "CHALLENGED on an enrichment page, not the login form: BidNet robot check on the "
      "Communication tab" in (r20["health"]["bidnet"].get("login_note") or ""), r20["health"]["bidnet"].get("login_note"))
del os.environ["FAKE_ROBOT_TAB"]
common.BIDNET_COOLDOWN_FILE.unlink(missing_ok=True)
for _k in ("FAKE_COMM", "FAKE_QA"):
    del os.environ[_k]

_B = _brmod.Browser


def _no_browser(*a, **k):
    raise RuntimeError("Executable doesn't exist at /opt/pw-browsers/chromium")


_brmod.Browser = _no_browser
r14 = run.scan(["bidnet"])
_brmod.Browser = _B
check("browser fails to start: the scan still finishes, BidNet marked incomplete and its rows kept",
      any("browser did not start" in e for e in r14["health"]["bidnet"]["errors"])
      and r14["health"]["bidnet"].get("carried_forward") and "bidnet:0000500002" in r14["found"], r14["health"]["bidnet"]["errors"])

import subprocess as _sp  # noqa: E402

_gr = TMP / "gitrepo"
_gr.mkdir()
for _cmd in (["git", "init", "-q"], ["git", "config", "user.email", "t@example.invalid"], ["git", "config", "user.name", "t"]):
    _sp.run(_cmd, cwd=_gr, check=True)
(_gr / "README").write_text("x")
_sp.run(["git", "add", "-A"], cwd=_gr, check=True)
_sp.run(["git", "commit", "-q", "-m", "init"], cwd=_gr, check=True)
(_gr / "small.txt").write_text("ok")
(_gr / "big.bin").write_bytes(b"x" * 64)
_sp.run(["git", "add", "-A"], cwd=_gr, check=True)
_REPO1, _MAX = run.REPO, run.MAX_PUSH_BYTES
run.REPO, run.MAX_PUSH_BYTES = _gr, 32
_held = run._hold_back_large()
_staged = _sp.run(["git", "diff", "--cached", "--name-only"], cwd=_gr, capture_output=True, text=True).stdout.split()
run.REPO, run.MAX_PUSH_BYTES = _REPO1, _MAX
check("a file over the push limit is held back; the rest is still committed", _held == ["big.bin"] and _staged == ["small.txt"],
      (_held, _staged))
# a stale code-needed marker expires so a new attempt is allowed (max one code email per 6 h)
common.CODE_NEEDED_MARKER.write_text("2026-01-01T00:00:00+00:00")
os.utime(common.CODE_NEEDED_MARKER, (time.time() - 7 * 3600,) * 2)
check("code-needed marker older than 6 h is expired", bidnet._marker_expired())
common.CODE_NEEDED_MARKER.unlink()

# ---------------------------------------------------------------- part 2c: no-password mode + session sync (2026-11-06)
# The cloud scanner never submits the BidNet password (robot checks on fresh logins, sessions idle out while the container
# sleeps); Luke's Mac logs in, keeps the session warm and ships it encrypted; the cloud imports and reuses it.
print("no-password mode (the cloud only reuses a session fed from Luke's Mac) + session_sync export/import")
import contextlib as _ctx  # noqa: E402
import hashlib as _hl  # noqa: E402
import io as _io2  # noqa: E402
from scripts.bidwatch import keepalive, mac_session_feeder, session_sync  # noqa: E402

_SESS = TMP / "state/sessions/bidnet.json"
_dflt = session_sync.DEFAULT_ENC
session_sync.DEFAULT_ENC = TMP / "no-such-default.enc"  # the checkout's own ops/session file must not steer the tests
os.environ["STATE_PASSPHRASE"] = "test-only-passphrase-not-a-secret"
os.environ[common.NO_PASSWORD_ENV] = "1"
os.environ.pop(session_sync.IMPORT_ENV, None)
_p0, _l0 = LOGIN_POSTS["n"], HITS2["list"]
r15 = run.scan(["bidnet"])
_h15 = r15["health"]["bidnet"]
check("no-password mode, live saved session: reused, lists read, nothing POSTed to the login endpoint",
      _h15["logged_in"] and _h15["login_note"].startswith("session reused (no-password mode") and _h15["count"] == 3
      and LOGIN_POSTS["n"] == _p0 and HITS2["list"] > _l0 and not _h15.get("login_deferred"), (_h15["login_note"], LOGIN_POSTS))
SESSIONS.clear()  # BidNet times the session out; the cloud must not log in by itself
_prev15 = {k for k in json.loads((TMP / "OPEN_BIDS_FILE.json").read_text())["bids"] if k.startswith("bidnet:")}
_p0, _l0, _d0 = LOGIN_POSTS["n"], HITS2["list"], HITS2["detail"]
r16 = run.scan(["bidnet"])
_h16 = r16["health"]["bidnet"]
_rep16 = (TMP / "REPORT_FILE.json").read_text()
check("no-password mode, expired session: no login POST, no lists or details read, BidNet skipped like a deferred login",
      LOGIN_POSTS["n"] == _p0 and HITS2["list"] == _l0 and HITS2["detail"] == _d0 and not _h16["logged_in"]
      and _h16.get("login_deferred") is True and _h16["login_note"] == common.NO_PASSWORD_NOTE, (_h16, LOGIN_POSTS, HITS2))
check("no-password mode, expired session: rows carried forward, none closed, no cool-down, report says so plainly",
      len(_prev15) == 3 and all(r16["found"].get(k, {}).get("carried_forward") for k in _prev15) and not r16["closed"]
      and bidnet.cooldown_until() is None and "waiting for a synced session" in _rep16
      and "BLIND: bidnet (login deferred on purpose)" in _rep16, (list(r16["closed"]), _h16))
_argv0, _hb0 = sys.argv, run._heartbeat
_env0 = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("HC_PING_")}  # never ping a real monitor from a test
_env0["BIDWATCH_KEEPALIVE"] = os.environ.get("BIDWATCH_KEEPALIVE")
os.environ["BIDWATCH_KEEPALIVE"] = "0"  # never start the real keeper here
run._heartbeat = lambda **kw: None  # the heartbeat file lives in the real repo's debug dir
sys.argv = ["run.py", "--sources", "bidnet"]
_out16 = _io2.StringIO()
with _ctx.redirect_stdout(_out16):
    _rc16 = run.main()
sys.argv, run._heartbeat = _argv0, _hb0
_out16 = _out16.getvalue()
_ls16 = LAST_SCAN.read_text()
check("the run prints LAST_SCAN.md's lines after the cycle line, so a log tail shows the digest",
      "cycle 1:" in _out16 and _ls16.rstrip() in _out16 and _out16.index(_ls16.rstrip()) > _out16.index("cycle 1:")
      and f"Logged in: no: {common.NO_PASSWORD_NOTE}" in _ls16, _out16[-900:])
for _k, _v in _env0.items():
    if _v is None:
        os.environ.pop(_k, None)
    else:
        os.environ[_k] = _v
check("no-password mode, expired session: the whole run exits 0 (a deliberate skip, not a degraded run)",
      _rc16 == 0 and LOGIN_POSTS["n"] == _p0, (_rc16, LOGIN_POSTS))
_ks = keepalive.check_once()
check("keepalive in no-password mode: never logs in, says it waits for a session synced from the Mac",
      _ks["state"].startswith("expired") and "synced" in _ks["state"] and LOGIN_POSTS["n"] == _p0, _ks)

_orig = _SESS.read_bytes()
_enc = TMP / "bidnet-session.enc"
session_sync.export(_enc)
_blob = _enc.read_bytes()
check("export: an openssl enc file (Salted__ header, the failover workflow's scheme), mode 600, no plaintext inside",
      _blob.startswith(b"Salted__") and oct(_enc.stat().st_mode & 0o777) == "0o600" and b'"cookies"' not in _blob, _blob[:16])
_SESS.write_bytes(b"{}")  # a useless local copy, to prove the import replaces it
_rec = session_sync.import_(_enc)
check("import restores an identical session file, mode 600, and records the file it installed",
      _SESS.read_bytes() == _orig and oct(_SESS.stat().st_mode & 0o777) == "0o600" and _rec["cookies"] >= 1
      and json.loads(session_sync.IMPORT_RECORD.read_text())["sha256"] == _hl.sha256(_blob).hexdigest(), _rec)
_refused = []
for _label, _bad in (("garbage", b"not an encrypted file at all"),
                     ("tampered", _blob[:40] + bytes([_blob[40] ^ 0xFF]) + _blob[41:]),
                     ("truncated", _blob[:-7]),
                     ("not-a-session", session_sync.encrypt(b'{"foo": 1}'))):
    _bf = TMP / f"bad-{_label}.enc"
    _bf.write_bytes(_bad)
    try:
        session_sync.import_(_bf)
        _refused.append((_label, "ACCEPTED"))
    except session_sync.SyncError:
        _refused.append((_label, "refused" if _SESS.read_bytes() == _orig else "CLOBBERED"))
check("import refuses garbage, a tampered or truncated file and a non-session document; the saved session is untouched",
      len(_refused) == 4 and all(v == "refused" for _, v in _refused), _refused)
_kaB = keepalive.Browser
_brmod.Browser = keepalive.Browser = _no_browser
_buf = _io2.StringIO()
with _ctx.redirect_stdout(_buf):
    _rc_st = session_sync.main(["status"])
_brmod.Browser = keepalive.Browser = _B
_st_out = _buf.getvalue()
check("status prints age, cookie count, mode and the last import without opening a browser",
      _rc_st == 0 and "cookies: " in _st_out and "no_password_mode: on" in _st_out and "saved_age_min: " in _st_out
      and "last_import: " in _st_out, _st_out)
_src_none = session_sync.import_source()
session_sync.DEFAULT_ENC = _enc
_src_dflt = session_sync.import_source()
os.environ.pop(common.NO_PASSWORD_ENV)
_src_off = session_sync.import_source()
session_sync.DEFAULT_ENC = TMP / "no-such-default.enc"
check("import source: the default file only counts in no-password mode and when it exists; the env var always wins",
      _src_none is None and _src_dflt == _enc and _src_off is None, (_src_none, _src_dflt, _src_off))
check("import_if_new with nothing configured is a no-op (no note)", session_sync.import_if_new() is None)

# the Mac side (password mode there): the session expired, so one login, then export and the push command
common.BIDNET_LAST_LOGIN_FILE.unlink(missing_ok=True)
_stale = _SESS.read_bytes()  # the sid BidNet forgot
_pushed = TMP / "pushed" / "bidnet-session.enc"
os.environ[mac_session_feeder.PUSH_CMD_ENV] = f'mkdir -p "{_pushed.parent}" && cp "$BIDWATCH_SESSION_FILE" "{_pushed}"'
_p0, _n0 = LOGIN_POSTS["n"], LOGINS["n"]
_ft = mac_session_feeder.tick(TMP / "feeder-out.enc")
check("Mac feeder tick: expired session -> one password login (device already confirmed), export, push command run",
      _ft["state"] == "logged in; exported" and _ft["push"] == "pushed" and LOGINS["n"] == _n0 + 1
      and LOGIN_POSTS["n"] == _p0 + 1 and _pushed.read_bytes().startswith(b"Salted__"), (_ft, LOGINS))
_ft2 = mac_session_feeder.tick(TMP / "feeder-out.enc")
check("Mac feeder tick: live session -> keep-alive only, no password, exported and pushed again",
      _ft2["state"] == "alive; exported" and _ft2["push"] == "pushed" and LOGIN_POSTS["n"] == _p0 + 1, _ft2)
del os.environ[mac_session_feeder.PUSH_CMD_ENV]
os.environ[common.NO_PASSWORD_ENV] = "1"
check("feeder refuses to run where no-password mode is set (that flag belongs on the cloud)",
      mac_session_feeder.main(["--once"]) == 2)
# the cloud side: no-password mode, its own copy is the stale one, the pushed file is newer -> imported and reused
_SESS.write_bytes(_stale)
os.environ[session_sync.IMPORT_ENV] = str(_pushed)
_p0 = LOGIN_POSTS["n"]
r17 = run.scan(["bidnet"])
_h17 = r17["health"]["bidnet"]
check("cloud scan installs the pushed session before BidNet and reuses it: logged in, 3 rows read, no password",
      _h17["logged_in"] and _h17["count"] == 3 and "synced session imported" in _h17["login_note"]
      and LOGIN_POSTS["n"] == _p0 and not _h17.get("carried_forward") and _SESS.read_bytes() != _stale, _h17["login_note"])
r18 = run.scan(["bidnet"])
_h18 = r18["health"]["bidnet"]
check("same pushed file next scan: left alone (locally refreshed cookies kept), the note says unchanged, still logged in",
      "synced session unchanged since" in _h18["login_note"] and _h18["logged_in"] and LOGIN_POSTS["n"] == _p0, _h18["login_note"])
with _ctx.redirect_stdout(_io2.StringIO()):
    _chk_alive = session_sync.main(["check"])
    SESSIONS.clear()
    _chk_dead = session_sync.main(["check"])
check("session_sync check: alive -> 0, expired -> 1, never a login", _chk_alive == 0 and _chk_dead == 1 and LOGIN_POSTS["n"] == _p0,
      (_chk_alive, _chk_dead, LOGIN_POSTS))
for _k in (common.NO_PASSWORD_ENV, session_sync.IMPORT_ENV, "STATE_PASSPHRASE"):
    os.environ.pop(_k, None)
session_sync.DEFAULT_ENC = _dflt
session_sync.IMPORT_RECORD.unlink(missing_ok=True)
common.BIDNET_LAST_LOGIN_FILE.unlink(missing_ok=True)

# keepalive through a robot-check cool-down (2026-11-06 15:41Z: a watched bid's tab served the robot check mid-scan, the
# cool-down made the keepalive skip its 15:42Z tick, the session idled out, and the 16:36Z scan needed the fresh login
# that trips the robot check): the probe runs with the saved session (reuse only), skips only without a saved session
# file, and a challenged probe neither starts nor extends the cool-down
print("keepalive during a robot-check cool-down")
_kb = Browser()
_ks0 = PortalSession(_kb, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
_ks0.ensure_login()  # password mode here: one fresh login (device already confirmed), saved on close
_ks0.close()
_kb.close()
check("setup: a live saved session", _ks0.logged_in and _SESS.exists(), _ks0.login_note)
common.BIDNET_LAST_LOGIN_FILE.unlink(missing_ok=True)
_until = bidnet.start_cooldown()
_p0, _h0 = LOGIN_POSTS["n"], HITS2["home"]
_ka1 = keepalive.check_once()
check("keepalive probes during a cool-down with a live saved session: alive, one page load, no password, cool-down untouched",
      _ka1["state"] == "alive" and HITS2["home"] == _h0 + 1 and LOGIN_POSTS["n"] == _p0 and bidnet.cooldown_until() == _until,
      (_ka1, HITS2["home"] - _h0, LOGIN_POSTS["n"] - _p0))
SESSIONS.clear()  # BidNet times the session out inside the cool-down
_p0, _h0 = LOGIN_POSTS["n"], HITS2["home"]
_ka2 = keepalive.check_once()
check("keepalive during a cool-down with an expired session: reports expired (not skipped), no POST to the login endpoint",
      _ka2["state"].startswith("expired") and LOGIN_POSTS["n"] == _p0 and HITS2["home"] == _h0 + 1, (_ka2, LOGIN_POSTS["n"] - _p0))
_ft3 = mac_session_feeder.tick(TMP / "feeder-out.enc")
check("Mac feeder during a cool-down with an expired session: no password login until the cool-down ends",
      _ft3["state"].startswith("expired") and "cool-down" in _ft3["state"] and LOGIN_POSTS["n"] == _p0, (_ft3, LOGIN_POSTS["n"] - _p0))
os.environ["FAKE_ROBOT_HOME"] = "1"
_cd_file = common.BIDNET_COOLDOWN_FILE.read_text()
_ka3 = keepalive.check_once()
check("a challenged probe during a cool-down: logged as challenged, cool-down file untouched, no login",
      _ka3["state"] == f"probe challenged (cool-down until {_until})" and common.BIDNET_COOLDOWN_FILE.read_text() == _cd_file
      and LOGIN_POSTS["n"] == _p0, (_ka3, _cd_file, common.BIDNET_COOLDOWN_FILE.read_text()))
_ft4 = mac_session_feeder.tick(TMP / "feeder-out.enc")
check("Mac feeder on a challenged probe: the tick ends, no login",
      _ft4["state"].startswith("probe challenged") and LOGIN_POSTS["n"] == _p0, _ft4)
common.BIDNET_COOLDOWN_FILE.unlink()
_ka4 = keepalive.check_once()
check("a challenged probe outside a cool-down starts none (that is the scan's call, not the keepalive's)",
      _ka4["state"] == "probe challenged (no cool-down started here)" and not common.BIDNET_COOLDOWN_FILE.exists()
      and LOGIN_POSTS["n"] == _p0, _ka4)
del os.environ["FAKE_ROBOT_HOME"]
_until = bidnet.start_cooldown()
_aside = TMP / "bidnet-session.aside"
_SESS.rename(_aside)
_h0 = HITS2["home"]
_ka5 = keepalive.check_once()
_aside.rename(_SESS)
check("no saved session file during a cool-down: skipped, BidNet not touched",
      _ka5["state"].startswith("skipped") and "cool-down" in _ka5["state"] and HITS2["home"] == _h0 and _ka5.get("until") == _until, _ka5)
common.BIDNET_COOLDOWN_FILE.unlink()
common.BIDNET_LAST_LOGIN_FILE.unlink(missing_ok=True)
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

    def __init__(self, host, **kw):
        FakeIMAP.calls.append(("connect", host, "tls" if kw.get("ssl_context") is not None else "plain"))

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
check("mailbox connection uses a verified TLS context", any(c[0] == "connect" and c[2] == "tls" for c in FakeIMAP.calls), FakeIMAP.calls[:1])
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

# ---------------------------------------------------------------- part 4: dead-man pings + failover idle check
print("health pings (healthchecks.io style) and the failover's stay-idle check")
HITS = []


class _PingHandler(http.server.BaseHTTPRequestHandler):
    def _record(self):
        n = int(self.headers.get("Content-Length") or 0)
        HITS.append((self.command, self.path, self.rfile.read(n).decode() if n else ""))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    do_GET = do_POST = _record

    def log_message(self, *a):
        pass


_ps = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _PingHandler)
threading.Thread(target=_ps.serve_forever, daemon=True).start()
_mon = f"http://127.0.0.1:{_ps.server_address[1]}"
for _k in [k for k in os.environ if k.startswith("HC_PING_")]:
    del os.environ[_k]
run.ping("scan", "/start")
check("ping without HC_PING_SCAN is a silent no-op", HITS == [], HITS)
os.environ["HC_PING_SCAN"] = _mon + "/uuid-1/"
run.ping("scan", "/start")
run.ping("scan", "", "ok=True degraded=[]")
run.ping("scan", "/fail", "ok=False")
check("ping hits /start, the check URL, /fail", [h[1] for h in HITS] == ["/uuid-1/start", "/uuid-1", "/uuid-1/fail"], HITS)
check("success ping carries the run summary as its body", HITS[1][0] == "POST" and "degraded=[]" in HITS[1][2], HITS)
os.environ["HC_PING_SCAN"] = "http://127.0.0.1:9/nobody-listens"
_t0 = time.time()
run.ping("scan", "/fail", "x")
check("ping to a dead monitor never raises or stalls the scan", time.time() - _t0 < 11)
del os.environ["HC_PING_SCAN"]

import datetime as _dtm  # noqa: E402


class _Proc:
    def __init__(self, out=""):
        self.stdout = out


class _ScanCalled(BaseException):
    """Escapes main()'s 'except Exception' so the test sees that a scan started."""


def _git_with_health(minutes_ago):
    def fake(*args, **kw):
        GIT_CALLS.append(args)
        if args[0] == "show":
            if minutes_ago is None:
                raise RuntimeError("fatal: path not in origin")
            return _Proc(json.dumps({"checked_at": common.iso(common.now_utc() - _dtm.timedelta(minutes=minutes_ago))}))
        return _Proc()
    return fake


def _start_scan(*a, **k):
    raise _ScanCalled()


GIT_CALLS = []
_saved = (run._git, run._branch, run.scan, run._heartbeat, sys.argv)
run._branch = lambda: "test-branch"
run._heartbeat = lambda **kw: None
run.scan = _start_scan
run._git = _git_with_health(25)
_age = run.origin_health_age_min()
check("failover reads the primary's last scan time from origin/<branch>:health.json",
      _age is not None and 24 < _age < 26 and ("show", "origin/test-branch:bids/_watch/health.json") in GIT_CALLS,
      (_age, GIT_CALLS))


def _main_rc(argv):
    sys.argv = ["run.py"] + argv
    try:
        return run.main(), False
    except _ScanCalled:
        return None, True


check("failover stays idle while the primary scanned < 80 min ago",
      _main_rc(["--only-if-stale", "80", "--sources", "samgov"]) == (0, False))
run._git = _git_with_health(200)
check("failover scans when the primary's last scan is > 80 min old",
      _main_rc(["--only-if-stale", "80", "--sources", "samgov"]) == (None, True))
run._git = _git_with_health(None)
check("failover scans when the primary's health.json cannot be read",
      _main_rc(["--only-if-stale", "80", "--sources", "samgov"]) == (None, True))

HITS.clear()
os.environ.update({"HC_PING_SCAN": _mon + "/scan", "HC_PING_SAMGOV": _mon + "/samgov", "HC_PING_BONFIRE": _mon + "/bonfire"})
run.scan = lambda sources, enrich_details=True: {"health": {
    "samgov": {"count": 0, "reachable": False, "carried_forward": True},
    "bonfire": {"count": 5, "reachable": True}}}
_rc, _ = _main_rc(["--sources", "samgov,bonfire"])
check("degraded scan exits 3, pings /fail; the healthy source still pings, the blind one does not",
      _rc == 3 and [h[1] for h in HITS] == ["/scan/start", "/scan/fail", "/bonfire"], (_rc, HITS))


def _crashing_scan(sources, enrich_details=True):
    raise RuntimeError("Chromium went away")


run.scan = _crashing_scan
_outc = _io2.StringIO()
with _ctx.redirect_stdout(_outc), _ctx.redirect_stderr(_io2.StringIO()):
    _rc, _ = _main_rc(["--sources", "samgov"])
_lsc = LAST_SCAN.read_text()
check("a scan that crashes exits 2 and still writes a current LAST_SCAN.md with the crash in its Errors line, printed after the cycle line",
      _rc == 2 and _lsc.startswith("# Last scan 20") and "Errors: scan crashed: RuntimeError: Chromium went away; exit code 2" in _lsc
      and _outc.getvalue().index("Errors: scan crashed") > _outc.getvalue().index("cycle 1:"), (_rc, _lsc, _outc.getvalue()[-400:]))
HITS.clear()
_ka = os.environ.get("BIDWATCH_KEEPALIVE")
os.environ.update({"HC_PING_BIDNET": _mon + "/bidnet", "BIDWATCH_KEEPALIVE": "0"})  # never start the real keeper here
run.scan = lambda sources, enrich_details=True: {"health": {
    "bidnet": {"count": 3, "reachable": True, "carried_forward": True, "blind": True, "login_deferred": True,
               "login_note": "login deferred: last fresh login x, next allowed after y"},
    "samgov": {"count": 5, "reachable": True}}}
_rc, _ = _main_rc(["--sources", "bidnet,samgov"])
check("BidNet login deferred = a deliberate skip: exit 0 and a success ping, no /fail; BidNet's own check is not pinged",
      _rc == 0 and [h[1] for h in HITS] == ["/scan/start", "/scan", "/samgov"] and "skipped=['bidnet']" in HITS[1][2],
      (_rc, HITS))
if _ka is None:
    del os.environ["BIDWATCH_KEEPALIVE"]
else:
    os.environ["BIDWATCH_KEEPALIVE"] = _ka
for _k in ("HC_PING_SCAN", "HC_PING_SAMGOV", "HC_PING_BONFIRE", "HC_PING_BIDNET"):
    del os.environ[_k]
run._git, run._branch, run.scan, run._heartbeat, sys.argv = _saved
_ps.shutdown()

# ---------------------------------------------------------------- part 5: SAM.gov nightly bulk file (no key)
print("SAM.gov nightly bulk file: download, cache, filters, merge into the scan")
from scripts.bidwatch import samgov_bulk  # noqa: E402

_today = _dtm.date.today()
_fut, _past = (_today + _dtm.timedelta(days=20)).isoformat(), (_today - _dtm.timedelta(days=1)).isoformat()
_COLS = ["NoticeId", "Title", "Sol#", "Department/Ind.Agency", "Sub-Tier", "Office", "PostedDate", "Type", "ArchiveDate",
         "SetASide", "ResponseDeadLine", "NaicsCode", "ClassificationCode", "PopCity", "PopState", "Active", "State", "Link",
         "Description"]


def _sam_row(nid, title, typ="Solicitation", pop="CO", office="CO", naics="", psc="", deadline=_fut, archive=""):
    return {"NoticeId": nid, "Title": title, "Sol#": "S-" + nid, "Department/Ind.Agency": "VETERANS AFFAIRS, DEPARTMENT OF",
            "Sub-Tier": "VETERANS AFFAIRS", "Office": "NETWORK CONTRACT OFFICE 19", "PostedDate": f"{_today} 08:00:00",
            "Type": typ, "ArchiveDate": archive, "SetASide": "", "ResponseDeadLine": f"{deadline}T16:00:00-06:00" if deadline else "",
            "NaicsCode": naics, "ClassificationCode": psc, "PopCity": "", "PopState": pop, "Active": "Yes", "State": office,
            "Link": f"https://sam.gov/workspace/contract/opp/{nid}/view", "Description": "Long text, with \"quotes\", commas\nand lines."}


_rows = [
    _sam_row("a1", "Boiler replacement, Building 2, TRANE@REG@ controls", naics="238220"),             # keep: PoP CO + NAICS
    _sam_row("b2", "HVAC Preventive Maintenance \u2013 RMR VAMC", pop="", office="CO"),                 # keep: blank PoP, CO office
    _sam_row("c3", "HVAC Preventive Maintenance", pop="WY", office="CO"),                               # drop: PoP decides
    _sam_row("d4", "Asphalt paving and HVAC upgrade", naics="237310"),                                  # drop: exclude keyword
    _sam_row("e5", "HVAC service award", typ="Award Notice", naics="238220"),                          # drop: not a bid
    _sam_row("f6", "HVAC service", naics="238220", deadline=_past),                                     # drop: deadline passed
    _sam_row("g7", "BEARING,BALL", pop="TX", office="PA", psc="3110"),                                  # keep JB: PSC 3110
    _sam_row("h8", "31--WASHER,THRUST,FREE", pop="TX", office="PA", naics="332991", psc="31"),          # drop: NAICS-only nationwide
    _sam_row("i9", "Radiant Panel Replacement", typ="Sources Sought", pop="", naics="238220", deadline="", archive=_fut),
    _sam_row("j10", "Screw Conveyor Replacement", pop="FL", office="FL", psc="3990"),                   # keep JB: title phrase
    _sam_row("k11", "Aircraft Apron Paving", pop="AZ", office="AZ", psc="Y1LB"),                        # drop: 'apron' alone
]
import csv as _csv  # noqa: E402
import io as _io  # noqa: E402

_buf = _io.StringIO()
_w = _csv.DictWriter(_buf, fieldnames=_COLS, quoting=_csv.QUOTE_ALL)
_w.writeheader()
_w.writerows(_rows)
SAM_CSV = _buf.getvalue().encode("cp1252").replace(b"@REG@", "\u00ae".encode("utf-8"))  # mixed, like the real file
SAM_HITS = {"download": 0, "s3": 0}


class _SamHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/download"):
            SAM_HITS["download"] += 1
            self.send_response(303)
            self.send_header("Location", "/s3/ContractOpportunitiesFullCSV.csv?X-Amz-Signature=fake")
            self.end_headers()
            return
        SAM_HITS["s3"] += 1
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(SAM_CSV)))
        self.end_headers()
        self.wfile.write(SAM_CSV)

    def log_message(self, *a):
        pass


_ss = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _SamHandler)
threading.Thread(target=_ss.serve_forever, daemon=True).start()
samgov_bulk.URL = f"http://127.0.0.1:{_ss.server_address[1]}/download?privacy=Public"
samgov_bulk.MIN_BYTES = 100
_p, _note = samgov_bulk.refresh()
check("bulk file downloaded through the 303 redirect, outside the repo",
      _p == samgov_bulk.CSV_FILE and SAM_HITS == {"download": 1, "s3": 1} and str(TMP) in str(_p), (_p, _note, SAM_HITS))
samgov_bulk.refresh()
check("same nightly file is not downloaded twice", SAM_HITS["download"] == 1, SAM_HITS)
_old = time.time() - 30 * 3600
os.utime(samgov_bulk.CSV_FILE, (_old, _old))
samgov_bulk.refresh()
check("a copy older than the latest nightly rebuild is refreshed", SAM_HITS["download"] == 2, SAM_HITS)
_bulk, _bnote = samgov_bulk.collect(profiles)
_bp = {k: v["profiles"] for k, v in _bulk.items()}
check("bulk filters: CO place of performance + trade NAICS kept", _bp.get("a1") == ["brownbison"], _bp)
check("mixed encoding decoded: UTF-8 \u00ae and a Windows-1252 en dash in one file",
      "TRANE\u00ae controls" in _bulk["a1"]["title"] and "\u00c2" not in _bulk["a1"]["title"], _bulk["a1"]["title"])
check("bulk filters: blank place of performance + Colorado buying office kept, en dash decoded",
      _bp.get("b2") == ["brownbison"] and _bulk["b2"]["office_state"] == "CO" and "\u2013" in _bulk["b2"]["title"], _bulk.get("b2"))
check("bulk filters: a stated place of performance outside CO drops it, even with a CO office", "c3" not in _bp, _bp)
check("bulk filters: exclude keywords, award notices and past deadlines drop", not {"d4", "e5", "f6"} & set(_bp), _bp)
check("bulk filters: nationwide profile takes PSC 3110 and product phrases, not NAICS-only or 'apron' paving",
      _bp.get("g7") == ["jones-bearing"] and _bp.get("j10") == ["jones-bearing"] and not {"h8", "k11"} & set(_bp), _bp)
check("bulk filters: upcoming notice without a deadline kept until it archives",
      "i9" in _bp and _bulk["i9"]["upcoming"] and _bulk["i9"]["closing"] is None, _bulk.get("i9"))
check("bulk note says what it did", "matching of" in _bnote, _bnote)
_ = samgov_bulk.collect(profiles)
check("filtered rows cached until the file, profiles or date change", "parsed earlier" in _[1], _[1])

# merge into a scan: API unreachable and no key -> the file carries SAM.gov, earlier API rows are kept
_ob = json.loads((TMP / "OPEN_BIDS_FILE.json").read_text())
_ob["bids"]["samgov:api-today"] = {"source": "samgov", "id": "api-today", "title": "HVAC controls, posted today",
                                   "closing": "2099-01-01", "profiles": ["brownbison"], "via": "api"}
(TMP / "OPEN_BIDS_FILE.json").write_text(json.dumps(_ob))
r6 = run.scan(["samgov"])
_h6 = r6["health"]["samgov"]
check("scan with the API down: SAM.gov rows come from the bulk file",
      all(f"samgov:{i}" in r6["found"] for i in ("a1", "b2", "g7", "i9", "j10")) and r6["found"]["samgov:a1"]["via"] == "bulk"
      and _h6["bulk_added"] == 5, (_h6.get("bulk_note"), _h6.get("bulk_added")))
check("API down: the API's earlier rows are carried forward, nothing closed",
      "samgov:api-today" in r6["found"] and not any(k.startswith("samgov") for k in r6["closed"]), list(r6["closed"]))
check("report labels a notice whose place of performance is not stated",
      "place of performance not stated; CO buying office" in (TMP / "REPORT_FILE.json").read_text())
check("API down but the file answered: PARTIAL, not BLIND, and last_success is this run",
      _h6.get("carried_forward") and not _h6.get("blind") and _h6.get("last_success") == r6["started"]
      and "PARTIAL this run" in (TMP / "REPORT_FILE.json").read_text(), _h6)
_ss.shutdown()
samgov_bulk.URL = "http://127.0.0.1:1/gone"
for _f in (samgov_bulk.CSV_FILE, samgov_bulk.KEPT_FILE):
    _f.unlink(missing_ok=True)
r7 = run.scan(["samgov"])
check("bulk file unavailable: rows only it had found are carried forward, not closed",
      "samgov:b2" in r7["found"] and r7["found"]["samgov:b2"].get("carried_forward")
      and not any(k.startswith("samgov") for k in r7["closed"]), (list(r7["closed"]), r7["health"]["samgov"]["errors"]))

# ---- change detection: a casing/whitespace flip of a title is not a change (SAM API vs bulk file, 2026-11-10) ----
from scripts.bidwatch import run as _run_t  # noqa: E402
_t_old = {"title": "31- Bearing, Ball,  Annular", "url": "u", "due": "2026-11-24"}
_t_same = {"title": "31- BEARING, BALL, ANNULAR", "url": "u", "due": "2026-11-24"}
_t_new = {"title": "31- Bearing, Roller, Cylindrical", "url": "u", "due": "2026-11-24"}
_d_same = [x for x in _run_t._diff(_t_old, _t_same) if x.startswith("title changed")]
_d_new = [x for x in _run_t._diff(_t_old, _t_new) if x.startswith("title changed")]
check("_diff: title casing/whitespace flip is not a change, a real rewording is",
      _d_same == [] and len(_d_new) == 1 and "Roller" in _d_new[0], (_d_same, _d_new))

# ---- keepalive --ensure must not be fooled by pid reuse after a container sleep (2026-11-09) ----
from scripts.bidwatch import keepalive as _ka  # noqa: E402
import subprocess as _sp  # noqa: E402
_ka_pid_backup = _ka.PID_FILE
_ka.PID_FILE = ROOT / "tests" / "_tmp_keepalive.pid"
try:
    _ka.PID_FILE.write_text(str(os.getpid()))  # live pid, but this process is the test runner, not keepalive.py
    _reused = _ka.running_pid()
    _fake = _sp.Popen([sys.executable, "-c", "import time; time.sleep(30)", "keepalive-marker", "--every", "900"])
    _shell = _sp.Popen([sys.executable, "-c", "import time; time.sleep(30)", "keepalive.py --ensure"])  # a caller, not the loop
    time.sleep(0.3)
    _ka.PID_FILE.write_text(str(_fake.pid))
    _real = _ka.running_pid()
    _fake.kill(); _fake.wait()
    _dead = _ka.running_pid()
    _ka.PID_FILE.write_text(str(_shell.pid))
    _caller = _ka.running_pid()
    _shell.kill(); _shell.wait()
    _ka.PID_FILE.write_text("not-a-pid")
    _junk = _ka.running_pid()
    check("keepalive running_pid: reused pid -> None, loop pid -> pid, dead pid -> None, --ensure caller -> None, junk -> None",
          _reused is None and _real == _fake.pid and _dead is None and _caller is None and _junk is None,
          (_reused, _real, _fake.pid, _dead, _caller, _junk))
finally:
    _ka.PID_FILE.unlink(missing_ok=True)
    _ka.PID_FILE = _ka_pid_backup

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
