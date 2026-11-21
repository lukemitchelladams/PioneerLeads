"""Amendment watch on GO bids (scripts/bidwatch/amendments.py, wired into run.py). Every SAM.gov request is a fake.

Why: 140RR027Q0001 got Amendment 0003 on SAM.gov at 22:09Z (due date moved, price schedule replaced); SAM.gov gives each
amendment version a new notice id, the scanner listed it as one more "new" notice row and nobody noticed for 7.5 hours.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import tempfile
import urllib.error
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("BB_STATE_DIR", tempfile.mkdtemp(prefix="amend-state-"))  # never the real ~/.brownbison

from scripts.bidwatch import amendments, run, samgov_public  # noqa: E402

SOL = "140RR027Q0001"
OLD_ID = "b2e58c41cb4c4787813fbc1f31ea81f7"
NEW_ID = "c07d00c2d5e94b3a8f1e6a7b9c0d1e2f"
KANAB = "140LL027Q0009"
KANAB_ID = "7afe087450dd48268559b2f751b40e4b"
NOW = "2026-11-21T14:00:00+00:00"
FOLDER = "bids/zz-bor-amend-test"


def notice(nid, sol=SOL, due="2026-12-04T14:00:00-07:00", modified="2026-11-16T18:00:00+00:00", canceled=False,
           title="S--BGNDRF Custodial Services, Brackish Groundwater National Desalination Research Facility"):
    """One public-search result as sam.gov returns it (fields trimmed): responseDate in UTC, responseDateActual in the notice's zone."""
    t = dt.datetime.fromisoformat(due)
    return {"_id": nid, "title": title, "solicitationNumber": sol, "type": {"code": "o", "value": "Solicitation"},
            "isActive": True, "isCanceled": canceled, "modifiedDate": modified, "publishDate": modified,
            "responseDate": t.astimezone(dt.timezone.utc).isoformat(), "responseDateActual": t.isoformat()}


def att(rid, name, size, typ="file", access="public", deleted="0"):
    return {"resourceId": rid, "name": name, "type": typ, "accessLevel": access, "deletedFlag": deleted, "size": size}


class FakeSam:
    """The fake sam.gov: the search by its q (a solicitation number; any other search answers no results), attachment lists by
    notice id, downloads by resource id. A value that is an exception is raised. Every URL is recorded."""

    def __init__(self):
        self.search, self.atts, self.files, self.calls = {}, {}, {}, []

    def __call__(self, url):
        self.calls.append(url)
        u = urlparse(url)
        m = re.search(r"/opportunities/(\w+)/resources$", u.path)
        if m:
            v = self.atts.get(m.group(1), [])
            if isinstance(v, Exception):
                raise v
            return json.dumps({"_embedded": {"opportunityAttachmentList": [{"attachments": v}]}} if v else {"_links": {}}).encode()
        m = re.search(r"/resources/files/(\w+)/download$", u.path)
        if m:
            v = self.files[m.group(1)]
            if isinstance(v, Exception):
                raise v
            return v
        assert u.path.endswith("/search/"), url
        v = self.search.get((parse_qs(u.query).get("q") or [""])[0], [])
        if isinstance(v, Exception):
            raise v
        return json.dumps({"_embedded": {"results": v}, "page": {"totalPages": 1}}).encode()

    def downloads(self):
        return [re.search(r"/files/(\w+)/download", u).group(1) for u in self.calls if u.endswith("/download")]

    def lists(self):
        return [u for u in self.calls if "/resources?" in u or u.endswith("/resources")]


@pytest.fixture(autouse=True)
def _quiet(monkeypatch):
    monkeypatch.setattr(samgov_public, "SLEEP_S", 0)
    monkeypatch.delenv(samgov_public.MAX_REQUESTS_ENV, raising=False)
    monkeypatch.setattr(samgov_public, "_http_get", lambda url, timeout=30: pytest.fail(f"real request to {url}"))


@pytest.fixture
def repo(tmp_path):
    (tmp_path / FOLDER / "docs").mkdir(parents=True)
    return tmp_path


def rows(folder=FOLDER, decision="GO (HQ 2026-11-16 12:00 gate met)"):
    return [{"decision": decision, "sol": f"{SOL} (SAM.gov {OLD_ID})", "title": "S--BGNDRF Custodial Services", "folder": folder}]


def go(fake, rows_, state, repo, budget=None):
    return amendments.check(rows_, state, budget or samgov_public.Budget(40), repo=repo, fetch=fake, now=NOW)


def seeded(fake, repo, rows_=None, atts_=None):
    """State after a first-sight run on the original notice (OLD_ID, due 2026-12-04 14:00 MT, two attachments)."""
    fake.search[SOL] = [notice(OLD_ID)]
    fake.atts[OLD_ID] = atts_ if atts_ is not None else [att("r1", "Solicitation 140RR027Q0001.pdf", 5),
                                                          att("r2", "Attachment 1 Price Schedule.xlsx", 4)]
    state: dict = {}
    res = go(fake, rows_ or rows(), state, repo)
    assert res["alerts"] == [] and res["errors"] == []
    fake.calls.clear()
    return state


# ---------------------------------------------------------------- which rows are watched

def test_amend_targets_go_and_go_if_rows_with_a_federal_number_only():
    rs = [
        {"decision": "GO (HQ 2026-11-16)", "sol": f"{SOL} (SAM.gov {OLD_ID})", "folder": "bids/bor"},
        {"decision": "GO-IF BONDED (HQ worker)", "sol": "not in hand", "title": "RFQ 36C25927Q0048 Radiant Heating Panels",
         "folder": "va-rmr"},
        {"decision": "GO (HQ)", "sol": "127EAX27Q0015 (SAM.gov e022e329a81747a4b3119b645b6758de)"},
        {"decision": "EVALUATE (jones-bearing GO if ...)", "sol": "SPE8EF27T0258 (SAM.gov 994aa9e06162482d9a3c07be9ba67263)"},
        {"decision": "SUBMITTED", "sol": "1240LP27Q0008 (SAM 1d1b8d72c87844289d3efb4990073ded)"},
        {"decision": "NO-BID", "sol": "1333ND27R0001"},
        {"decision": "GO (HQ default)", "sol": "RFP 26-27-013 (BidNet 0000443304)"},
        {"decision": "GO-IF (pre-bid NOT mandatory)", "sol": "DQ1-PMAA-2027000176-1 (Colorado VSS, Documented Quote)"},
        {"decision": "GOOD LUCK", "sol": "140LL027Q0009"},
        {"decision": "GO", "sol": f"{SOL}", "folder": "bids/bor-second-row"},  # same number again: one target
    ]
    got = amendments.targets(rs)
    assert [(t["sol"], t["folder"]) for t in got] == [(SOL, "bids/bor"), ("36C25927Q0048", "bids/va-rmr"), ("127EAX27Q0015", None)]
    assert amendments.federal_sol("36C25927Q0048 (SAM.gov b4ea..., Amd 0001; sources sought was 36C25927Q0019)") == "36C25927Q0048"
    assert amendments.federal_sol("Hoods HoodsDucts12NOV26 BidNet 0000443963 b2e58c41cb4c4787813fbc1f31ea81f7") is None


def test_amend_real_pipeline_targets_are_the_go_federal_bids():
    real = json.loads((ROOT / "bids/_watch/pipeline.json").read_text())["bids"]
    sols = {t["sol"] for t in amendments.targets(real)}
    assert SOL in sols and all(re.fullmatch(r"[A-Z0-9]{10,17}", s) for s in sols)


# ---------------------------------------------------------------- first sight, quiet scans, alerts

def test_amend_first_sight_records_state_without_alert(repo):
    fake = FakeSam()
    fake.search[SOL] = [notice(OLD_ID)]
    fake.atts[OLD_ID] = [att("r1", "Solicitation 140RR027Q0001.pdf", 5), att("r3", "Wage Determination", None, typ="link")]
    state: dict = {}
    res = go(fake, rows(), state, repo)
    assert res["alerts"] == [] and res["errors"] == [] and res["saved"] == []
    assert len(fake.calls) == 2 and "q=140RR027Q0001" in fake.calls[0] and fake.downloads() == []
    s = state[SOL]
    assert s["notice_id"] == OLD_ID and s["modifiedDate"] == "2026-11-16T18:00:00+00:00"
    assert s["responseDate"] == "2026-12-04T21:00:00+00:00" and s["attachments"] == ["Solicitation 140RR027Q0001.pdf",
                                                                                      "Wage Determination"]
    assert s["pending"] == [] and s["relist"] is False and s["first_seen"] == NOW and res["stats"]["first_sight"] == 1


def test_amend_unchanged_notice_one_request_no_alert_no_state_write(repo, tmp_path):
    fake = FakeSam()
    fake.search[SOL] = [notice(OLD_ID)]
    fake.atts[OLD_ID] = [att("r1", "Solicitation 140RR027Q0001.pdf", 5)]
    sf = tmp_path / "amendment_state.json"
    first = amendments.watch(rows(), samgov_public.Budget(40), state_file=sf, repo=repo, fetch=fake, now=NOW)
    assert first["state_written"] and json.loads(sf.read_text())["solicitations"][SOL]["notice_id"] == OLD_ID
    mtime = sf.stat().st_mtime_ns
    fake.calls.clear()
    again = amendments.watch(rows(), samgov_public.Budget(40), state_file=sf, repo=repo, fetch=fake, now="2026-11-21T15:00:00+00:00")
    assert again["alerts"] == [] and again["errors"] == [] and not again["state_written"]
    assert len(fake.calls) == 1 and sf.stat().st_mtime_ns == mtime


def test_amend_changed_response_date_alerts(repo):
    fake = FakeSam()
    state = seeded(fake, repo)
    fake.search[SOL] = [notice(OLD_ID, due="2026-12-09T11:00:00-07:00", modified="2026-11-20T22:09:00+00:00")]
    res = go(fake, rows(), state, repo)
    assert [a["line"] for a in res["alerts"]] == [
        f"AMENDMENT: {SOL} due 2026-12-04T14:00-07:00 -> 2026-12-09T11:00-07:00 (notice b2e58c41...)"]
    assert state[SOL]["responseDate"] == "2026-12-09T18:00:00+00:00" and state[SOL]["last_alert"] == res["alerts"][0]["line"]
    # the same moment written another way is not a move
    s2 = {SOL: {**state[SOL], "responseDate": "2026-12-09T18:00:00Z"}}
    fake.calls.clear()
    assert go(fake, rows(), s2, repo)["alerts"] == []


def test_amend_new_notice_id_alerts_in_the_spec_format(repo):
    fake = FakeSam()
    state = seeded(fake, repo)
    # the search lists the older version first; the newest by modifiedDate wins
    fake.search[SOL] = [notice(OLD_ID), notice(NEW_ID, due="2026-12-09T11:00:00-07:00", modified="2026-11-20T22:09:00+00:00")]
    fake.atts[NEW_ID] = fake.atts[OLD_ID]
    res = go(fake, rows(), state, repo)
    assert [a["line"] for a in res["alerts"]] == [
        "AMENDMENT: 140RR027Q0001 due 2026-12-04T14:00-07:00 -> 2026-12-09T11:00-07:00 (new notice c07d00c2...)"]
    a = res["alerts"][0]
    assert a["old_notice"] == OLD_ID and a["new_notice"] == NEW_ID and a["url"] == f"https://sam.gov/opp/{NEW_ID}/view"
    assert state[SOL]["notice_id"] == NEW_ID and state[SOL]["changed_at"] == NOW
    # a new version with the due date unchanged still alerts
    fake.search[SOL] = [notice("d1" * 16, due="2026-12-09T11:00:00-07:00", modified="2026-11-21T09:00:00+00:00")]
    fake.atts["d1" * 16] = fake.atts[OLD_ID]
    assert [a["line"] for a in go(fake, rows(), state, repo)["alerts"]] == [
        "AMENDMENT: 140RR027Q0001 new notice d1d1d1d1... (due 2026-12-09T11:00-07:00 unchanged)"]


# ---------------------------------------------------------------- attachments

def test_amend_new_attachments_listed_and_downloaded_only_when_folder_set(repo):
    fake = FakeSam()
    rs = rows() + [{"decision": "GO (HQ 2026-11-18)", "sol": f"{KANAB} (SAM.gov {KANAB_ID})", "title": "BLM Kanab janitorial"}]
    fake.search[KANAB] = [notice(KANAB_ID, sol=KANAB, title="S--BLM Utah - Paria River District HQ Janitorial")]
    fake.atts[KANAB_ID] = [att("k1", "Sol_140LL027Q0009.pdf", 3)]
    state = seeded(fake, repo, rows_=rs)
    fake.search[SOL] = [notice(NEW_ID, due="2026-12-09T11:00:00-07:00", modified="2026-11-20T22:09:00+00:00")]
    fake.atts[NEW_ID] = fake.atts[OLD_ID] + [att("r7", "Amendment 0003.pdf", 6), att("r8", "Attachment 1 Price Schedule Rev 3.xlsx", 7),
                                             att("r9", "Site map (link)", None, typ="link"),
                                             att("r0", "superseded.pdf", 2, deleted="1")]
    fake.files.update({"r7": b"%PDF-3", "r8": b"XLSXrv3"})
    fake.search[KANAB] = [notice("e" * 32, sol=KANAB, modified="2026-11-21T01:00:00+00:00")]
    fake.atts["e" * 32] = fake.atts[KANAB_ID] + [att("k2", "Amendment 0001.pdf", 4)]
    fake.files["k2"] = AssertionError("a row without a folder downloads nothing")
    res = go(fake, rs, state, repo)
    bor, kanab = res["alerts"]
    assert bor["line"].endswith("(new notice c07d00c2..., 3 new attachments)")
    assert bor["new_attachments"] == ["Amendment 0003.pdf", "Attachment 1 Price Schedule Rev 3.xlsx", "Site map (link)"]
    assert sorted(fake.downloads()) == ["r7", "r8"]  # files only: not the link, not the deleted one, nothing for Kanab
    docs = repo / FOLDER / "docs"
    assert (docs / "Amendment 0003.pdf").read_bytes() == b"%PDF-3" and (docs / "Attachment 1 Price Schedule Rev 3.xlsx").is_file()
    assert sorted(res["saved"]) == [f"{FOLDER}/docs/Amendment 0003.pdf", f"{FOLDER}/docs/Attachment 1 Price Schedule Rev 3.xlsx"]
    assert res["folders"] == [FOLDER] and res["errors"] == []
    assert kanab["sol"] == KANAB and kanab["new_attachments"] == ["Amendment 0001.pdf"] and kanab["saved"] == []
    assert kanab["folder"] is None and "superseded.pdf" not in state[SOL]["attachments"]


def test_amend_existing_filenames_skipped(repo):
    fake = FakeSam()
    state = seeded(fake, repo)
    docs = repo / FOLDER / "docs"
    (docs / "Amendment 0003.pdf").write_bytes(b"saved by hand, another size")
    fake.search[SOL] = [notice(NEW_ID, modified="2026-11-20T22:09:00+00:00")]
    fake.atts[NEW_ID] = fake.atts[OLD_ID] + [att("r7", "Amendment 0003.pdf", 6), att("r8", "Q and A.pdf", 3)]
    fake.files.update({"r7": AssertionError("already in the folder"), "r8": b"Q&A"})
    res = go(fake, rows(), state, repo)
    assert fake.downloads() == ["r8"] and res["saved"] == [f"{FOLDER}/docs/Q and A.pdf"] and res["errors"] == []
    assert (docs / "Amendment 0003.pdf").read_bytes() == b"saved by hand, another size"
    assert res["alerts"][0]["new_attachments"] == ["Amendment 0003.pdf", "Q and A.pdf"]


def test_amend_replaced_file_under_same_name_saved_beside_the_old_one(repo):
    fake = FakeSam()
    state = seeded(fake, repo)
    docs = repo / FOLDER / "docs"
    (docs / "Attachment 1 Price Schedule.xlsx").write_bytes(b"XLSX")
    fake.search[SOL] = [notice(NEW_ID, due="2026-12-09T11:00:00-07:00", modified="2026-11-20T22:09:00+00:00")]
    fake.atts[NEW_ID] = [att("r1", "Solicitation 140RR027Q0001.pdf", 5), att("r2", "Attachment 1 Price Schedule.xlsx", 4, deleted="1"),
                         att("r5", "Attachment 1 Price Schedule.xlsx", 9)]
    fake.files["r5"] = b"XLSX rev3"
    res = go(fake, rows(), state, repo)
    a = res["alerts"][0]
    assert a["replaced"] == ["Attachment 1 Price Schedule.xlsx"] and a["line"].endswith("(new notice c07d00c2..., 1 replaced)")
    assert (docs / "Attachment 1 Price Schedule (rev 2026-11-21).xlsx").read_bytes() == b"XLSX rev3"
    assert (docs / "Attachment 1 Price Schedule.xlsx").read_bytes() == b"XLSX"


# ---------------------------------------------------------------- failures and caps

def test_amend_http_failures_are_error_lines_never_exceptions(repo):
    fake = FakeSam()
    rs = rows() + [{"decision": "GO", "sol": KANAB, "folder": FOLDER}]
    fake.search[KANAB] = [notice(KANAB_ID, sol=KANAB)]
    fake.atts[KANAB_ID] = []
    state = seeded(fake, repo, rows_=rs)
    before = json.dumps(state[SOL], sort_keys=True)
    # 1. the search answers 503 for one solicitation: one line, the next one still checked, its state untouched
    fake.search[SOL] = urllib.error.HTTPError("https://sam.gov/api/prod/sgs/v1/search/", 503, "Service Unavailable", {}, None)
    fake.search[KANAB] = [notice(KANAB_ID, sol=KANAB, due="2026-12-10T14:00:00-07:00")]
    res = go(fake, rs, state, repo)
    assert res["errors"] == [f"amendment watch {SOL}: search: HTTP 503 Service Unavailable"]
    assert [a["sol"] for a in res["alerts"]] == [KANAB] and json.dumps(state[SOL], sort_keys=True) == before
    # 2. the attachment list fails on the amendment: the alert still goes out, the list is read again next scan
    fake.search[SOL] = [notice(NEW_ID, modified="2026-11-20T22:09:00+00:00")]
    fake.atts[NEW_ID] = TimeoutError("timed out")
    res = go(fake, rows(), state, repo)
    assert [a["line"] for a in res["alerts"]] == [f"AMENDMENT: {SOL} new notice c07d00c2... (due 2026-12-04T14:00-07:00 unchanged)"]
    assert res["errors"] == [f"amendment watch {SOL}: attachment list: TimeoutError: timed out (read again next scan)"]
    assert state[SOL]["relist"] is True and state[SOL]["attachments"] == ["Solicitation 140RR027Q0001.pdf",
                                                                          "Attachment 1 Price Schedule.xlsx"]
    # 3. next scan: the list is read; the new file's download fails (HTTP 500): one line, the name kept pending
    fake.atts[NEW_ID] = fake.atts[OLD_ID] + [att("r7", "Amendment 0003.pdf", 6)]
    fake.files["r7"] = urllib.error.HTTPError("https://sam.gov/x", 500, "Internal Server Error", {}, None)
    res = go(fake, rows(), state, repo)
    assert [a["new_attachments"] for a in res["alerts"]] == [["Amendment 0003.pdf"]] and res["alerts"][0]["pending"] == ["Amendment 0003.pdf"]
    assert res["errors"] == [f"amendment watch {SOL}: Amendment 0003.pdf: HTTP 500 Internal Server Error (tried again next scan)"]
    assert state[SOL]["pending"] == [["Amendment 0003.pdf", "Amendment 0003.pdf"]] and state[SOL]["relist"] is False
    # 4. the scan after: tried again and saved, no second alert, nothing pending
    fake.files["r7"] = b"%PDF-3"
    fake.calls.clear()
    res = go(fake, rows(), state, repo)
    assert res["alerts"] == [] and res["errors"] == [] and res["saved"] == [f"{FOLDER}/docs/Amendment 0003.pdf"]
    assert fake.downloads() == ["r7"] and state[SOL]["pending"] == []


def test_amend_watch_swallows_unexpected_errors_and_a_corrupt_state_file(repo, tmp_path, monkeypatch):
    fake = FakeSam()
    sf = tmp_path / "amendment_state.json"
    sf.write_text("{not json")
    fake.search[SOL] = [notice(OLD_ID)]
    res = amendments.watch(rows(), samgov_public.Budget(40), state_file=sf, repo=repo, fetch=fake, now=NOW)
    assert res["errors"] == [] and json.loads(sf.read_text())["solicitations"][SOL]["notice_id"] == OLD_ID
    monkeypatch.setattr(amendments, "check", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    res = amendments.watch(rows(), samgov_public.Budget(40), state_file=sf, repo=repo, fetch=fake, now=NOW)
    assert res["errors"] == ["amendment watch: RuntimeError: boom"] and res["alerts"] == []


def test_amend_caps_files_bytes_and_the_shared_request_budget(repo, monkeypatch):
    fake = FakeSam()
    state = seeded(fake, repo)
    fake.search[SOL] = [notice(NEW_ID, modified="2026-11-20T22:09:00+00:00")]
    fake.atts[NEW_ID] = fake.atts[OLD_ID] + [att("r7", "A.pdf", 6), att("r8", "B.pdf", 6), att("r9", "Huge drawings.pdf", 50)]
    fake.files.update({"r7": b"AAAAAA", "r8": b"BBBBBB", "r9": AssertionError("over the cap: never requested")})
    monkeypatch.setattr(amendments, "MAX_BYTES", 10)
    res = go(fake, rows(), state, repo)
    assert fake.downloads() == ["r7"] and res["alerts"][0]["pending"] == ["B.pdf"]  # 6 + 6 > 10 bytes: next scan
    assert any("Huge drawings.pdf: 50 bytes, over the 0 MB a scan cap; download it from https://sam.gov/opp/" in e for e in res["errors"])
    monkeypatch.setattr(amendments, "MAX_BYTES", 25 * 2**20)
    monkeypatch.setattr(amendments, "MAX_FILES", 1)
    fake.atts[NEW_ID].append(att("r6", "C.pdf", 3))
    fake.files["r6"] = b"CCC"
    fake.calls.clear()
    res = go(fake, rows(), state, repo)  # B.pdf (pending) and C.pdf (new): one file a run
    assert fake.downloads() == ["r6"] and state[SOL]["pending"] == [["B.pdf", "B.pdf"]]
    fake.calls.clear()
    go(fake, rows(), state, repo)
    assert fake.downloads() == ["r8"] and state[SOL]["pending"] == []
    # BIDWATCH_SAM_PUBLIC_MAX: the scan's Budget() is the cap; 1 request = the first search, nothing more, nothing raised
    monkeypatch.setenv(samgov_public.MAX_REQUESTS_ENV, "1")
    fake.calls.clear()
    rs = rows() + [{"decision": "GO", "sol": KANAB}]
    res = go(fake, rs, {}, repo, budget=samgov_public.Budget())
    assert len(fake.calls) == 1 and res["alerts"] == []
    assert res["errors"] == [f"amendment watch {SOL}: request cap 1 reached; attachments read again next scan",
                             "amendment watch: request cap 1 reached; 1 of 2 GO solicitations wait for the next scan"]


# ---------------------------------------------------------------- run.py: REPORT.md headline and section, never fails the scan

@pytest.fixture
def scan_env(tmp_path, monkeypatch):
    """run.scan(["samgov"]) in a scratch repo: no key, the public search, bulk file and health probe faked."""
    r = tmp_path / "repo"
    (r / FOLDER / "docs").mkdir(parents=True)
    w = r / "bids" / "_watch"
    w.mkdir(parents=True)
    (w / "pipeline.json").write_text(json.dumps({"bids": rows()}))
    (w / "watchlist.json").write_text('{"bids": []}')
    for name, fn in (("OPEN_BIDS_FILE", "open_bids.json"), ("HEALTH_FILE", "health.json"), ("REPORT_FILE", "REPORT.md"),
                     ("WATCHLIST_FILE", "watchlist.json"), ("LAST_SCAN_FILE", "LAST_SCAN.md"), ("PIPELINE_FILE", "pipeline.json")):
        monkeypatch.setattr(run, name, w / fn)
    monkeypatch.setattr(run, "REPO", r)
    monkeypatch.setattr(run, "load_env_file", lambda *a, **k: None)
    monkeypatch.setattr(run, "reachable", lambda url, timeout=30: (True, "HTTP 404"))
    monkeypatch.setattr(run.samgov_bulk, "collect", lambda profiles: ({}, "bulk file cached; 0 matching"))
    monkeypatch.setattr(samgov_public, "DOWNLOAD_DIR", tmp_path / "downloads")
    monkeypatch.delenv("SAM_API_KEY", raising=False)
    monkeypatch.setenv("BIDWATCH_SAMGOV_BRIEF_MAX", "0")
    fake = FakeSam()
    monkeypatch.setattr(samgov_public, "_http_get", fake)
    return r, w, fake


def test_amend_scan_headline_opens_with_the_alert_and_report_lists_it(scan_env):
    r, w, fake = scan_env
    state = seeded(fake, r)
    (w / "amendment_state.json").write_text(json.dumps({"solicitations": state}))
    fake.search[SOL] = [notice(NEW_ID, due="2026-12-09T11:00:00-07:00", modified="2026-11-20T22:09:00+00:00")]
    fake.atts[NEW_ID] = fake.atts[OLD_ID] + [att("r7", "Amendment 0003.pdf", 6)]
    fake.files["r7"] = b"%PDF-3"
    res = run.scan(["samgov"])
    rep = run.REPORT_FILE.read_text()
    line = "AMENDMENT: 140RR027Q0001 due 2026-12-04T14:00-07:00 -> 2026-12-09T11:00-07:00 (new notice c07d00c2..., 1 new attachment)"
    assert rep.splitlines()[2].startswith(f"**Headline:** {line}; LOGGED OUT: samgov"), rep[:600]
    sec = rep.index("## Amendments on GO bids")
    assert sec < rep.index("## Source health")
    body = rep[sec:rep.index("## Source health")]
    assert f"- **{line}** | S--BGNDRF Custodial Services" in body and f"https://sam.gov/opp/{NEW_ID}/view" in body
    assert "  - new attachments: Amendment 0003.pdf" in body and "  - downloaded into the bid folder: Amendment 0003.pdf" in body
    assert (r / FOLDER / "docs" / "Amendment 0003.pdf").read_bytes() == b"%PDF-3"
    assert f"{FOLDER}/docs/Amendment 0003.pdf" in res["filed"] and "bids/_watch/amendment_state.json" in res["filed"]
    assert json.loads((w / "amendment_state.json").read_text())["solicitations"][SOL]["notice_id"] == NEW_ID
    assert res["amendments"][0]["line"] == line and res["health"]["samgov"]["amendment_watch"]["alerts"] == 1
    assert fake.calls[0].endswith("q=140RR027Q0001")  # GO bids first out of the shared request budget
    # the next scan: nothing new, no amendment line, no section
    run.scan(["samgov"])
    rep2 = run.REPORT_FILE.read_text()
    assert "AMENDMENT" not in rep2 and "## Amendments on GO bids" not in rep2


def test_amend_scan_survives_http_failure_and_a_crash_in_the_step(scan_env, monkeypatch):
    r, w, fake = scan_env
    fake.search[SOL] = urllib.error.HTTPError("https://sam.gov/api/prod/sgs/v1/search/", 503, "Service Unavailable", {}, None)
    res = run.scan(["samgov"])
    rep = run.REPORT_FILE.read_text()
    assert f"amendment watch {SOL}: search: HTTP 503 Service Unavailable" in res["health"]["samgov"]["errors"]
    assert f"- samgov: amendment watch {SOL}: search: HTTP 503 Service Unavailable" in rep and "AMENDMENT:" not in rep
    monkeypatch.setattr(run.amendments, "check", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    res = run.scan(["samgov"])
    assert "amendment watch: RuntimeError: boom" in res["health"]["samgov"]["errors"]
    assert run.REPORT_FILE.read_text().startswith("# Bid watch report") and run.LAST_SCAN_FILE.read_text().startswith("# Last scan")
    assert "- samgov: amendment watch: RuntimeError: boom" in run.REPORT_FILE.read_text()


def test_amend_errors_never_make_samgov_partial_with_the_api_key(scan_env, monkeypatch):
    """With the key, _merge_sam_bulk reads any line in h["errors"] as "the API failed" and marks SAM.gov PARTIAL; the watch's lines
    are added after it, so a failing amendment look-up leaves a clean API scan clean."""
    r, w, fake = scan_env
    monkeypatch.setenv("SAM_API_KEY", "dummy-key-for-the-test")
    row = {"source": "samgov", "id": "n1", "title": "HVAC preventive maintenance", "closing": "2099-01-01", "documents": [],
           "state": "CO"}
    monkeypatch.setattr(run.samgov, "collect", lambda profiles: ({"samgov:n1": dict(row)}, []))
    monkeypatch.setattr(run.samgov_bulk, "collect", lambda profiles: ({"samgov:n1": {**row, "via": "bulk"}}, "bulk ok"))
    fake.search[SOL] = urllib.error.HTTPError("https://sam.gov/api/prod/sgs/v1/search/", 503, "Service Unavailable", {}, None)
    res = run.scan(["samgov"])
    h = res["health"]["samgov"]
    assert h["errors"] == [f"amendment watch {SOL}: search: HTTP 503 Service Unavailable"]
    assert not h.get("carried_forward") and h.get("complete") is not False and "samgov" not in run.run_status(res["health"])["degraded"]
