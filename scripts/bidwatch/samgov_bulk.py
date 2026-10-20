"""SAM.gov Contract Opportunities nightly bulk file: open federal notices without an API key.

    https://sam.gov/api/prod/fileextractservices/v1/api/download/Contract%20Opportunities/datagov/
        ContractOpportunitiesFullCSV.csv?privacy=Public
    (303 to a signed S3 URL; ~205 MB; UTF-8 with stray Windows-1252 bytes; rebuilt nightly around 03:30 UTC.)

Why, next to the API (samgov.py):
  * the API's place-of-performance `state` filter cannot see notices whose PoP state is blank: 63 of 147
    (43%) in a 2026-10-20 sample of this file. The file also carries the buying office's state, so a notice
    with a blank PoP state and a Colorado office is kept for the Colorado profile;
  * discovery keeps working when the API key is missing, rotated, rate-limited or the API is down.
Limits: no attachments, and notices posted after the nightly rebuild appear the next day (the API has them
the same day). Rows found only here carry via="bulk".

The file is cached outside the repo (STATE_HOME/cache), downloaded at most once per rebuild, and the filtered
result is cached until the file, the profiles or the date change. Never raises: collect() returns ({}, note).
"""
from __future__ import annotations

import codecs
import csv
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import urllib.request
from pathlib import Path

from .common import STATE_HOME, iso, load_json, match_profiles, now_utc, save_json

URL = ("https://sam.gov/api/prod/fileextractservices/v1/api/download/Contract%20Opportunities/datagov/"
       "ContractOpportunitiesFullCSV.csv?privacy=Public")
CACHE_DIR = STATE_HOME / "cache"
CSV_FILE = CACHE_DIR / "ContractOpportunitiesFullCSV.csv"
KEPT_FILE = CACHE_DIR / "samgov_bulk_kept.json"
MIN_BYTES = 50_000_000  # the real file is ~205 MB; an error page or a cut-off transfer is far smaller
REBUILD_UTC_HOUR = 5    # SAM rebuilds around 03:30 UTC; files fetched before 05:00 UTC count as yesterday's
KEEP_TYPES = {"Solicitation", "Combined Synopsis/Solicitation", "Presolicitation", "Sources Sought", "Special Notice"}
UPCOMING_TYPES = {"Presolicitation", "Sources Sought", "Special Notice"}
UA = "BrownBisonBidWatch/2.0 (+luke@brownbisonco.com)"


def _latest_rebuild(now: dt.datetime) -> dt.datetime:
    mark = now.replace(hour=REBUILD_UTC_HOUR, minute=0, second=0, microsecond=0)
    return mark if now >= mark else mark - dt.timedelta(days=1)


def _mtime(p: Path) -> dt.datetime:
    return dt.datetime.fromtimestamp(p.stat().st_mtime, dt.timezone.utc)


def refresh(now: dt.datetime | None = None, timeout: int = 120) -> tuple[Path | None, str]:
    """Return (path to a usable copy of the file, note). Downloads only when the cached copy predates the
    latest nightly rebuild; a failed download falls back to the cached copy."""
    now = now or now_utc()
    if CSV_FILE.exists() and _mtime(CSV_FILE) >= _latest_rebuild(now):
        return CSV_FILE, f"bulk file cached {iso(_mtime(CSV_FILE))}"
    tmp = CSV_FILE.with_suffix(".part")
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r, open(tmp, "wb") as f:  # follows the 303 to S3
            shutil.copyfileobj(r, f, 1 << 20)
        size = tmp.stat().st_size
        if size < MIN_BYTES:
            raise RuntimeError(f"got {size} bytes, not the ~205 MB file")
        os.replace(tmp, CSV_FILE)
        return CSV_FILE, f"bulk file downloaded {size // 1_000_000} MB"
    except Exception as e:  # noqa: BLE001
        tmp.unlink(missing_ok=True)
        why = f"{type(e).__name__}: {str(e)[:120]}"
        if CSV_FILE.exists():
            return CSV_FILE, f"bulk download failed ({why}); using the copy from {iso(_mtime(CSV_FILE))}"
        return None, f"bulk download failed ({why}); no cached copy"


def _cp1252_fallback(err: UnicodeError):
    """The file is mostly UTF-8 (TRANE\u00ae arrives as C2 AE) with stray Windows-1252 bytes (0x96 en dash):
    decode as UTF-8 and read only the invalid bytes as Windows-1252."""
    bad = err.object[err.start:err.end]
    return bad.decode("cp1252", errors="replace"), err.end


codecs.register_error("bidwatch_cp1252_fallback", _cp1252_fallback)


def iter_rows(path: Path):
    csv.field_size_limit(2**31 - 1)  # Description cells run to tens of KB
    with open(path, encoding="utf-8", errors="bidwatch_cp1252_fallback", newline="") as f:
        yield from csv.DictReader(f)


def normalize_row(r: dict) -> dict:
    nid = (r.get("NoticeId") or "").strip()
    agency = " / ".join(x.strip() for x in (r.get("Department/Ind.Agency"), r.get("Sub-Tier"), r.get("Office"))
                        if x and x.strip())
    return {
        "source": "samgov", "id": nid, "title": (r.get("Title") or "").strip(), "sol": (r.get("Sol#") or "").strip() or None,
        "agency": agency, "type": r.get("Type"), "upcoming": r.get("Type") in UPCOMING_TYPES,
        "published": (r.get("PostedDate") or "")[:10], "closing": (r.get("ResponseDeadLine") or "")[:10] or None,
        "naics": (r.get("NaicsCode") or "").strip() or None, "psc": (r.get("ClassificationCode") or "").strip() or None,
        "set_aside": (r.get("SetASide") or "").strip() or None,
        "state": (r.get("PopState") or "").strip() or None, "city": (r.get("PopCity") or "").strip() or None,
        "office_state": (r.get("State") or "").strip() or None,
        "url": (r.get("Link") or "").strip() or f"https://sam.gov/opp/{nid}/view", "documents": [], "via": "bulk",
    }


def _word(p: str) -> re.Pattern:
    return re.compile(r"\b" + re.escape(p.lower()))


def keep(rec: dict, prof: dict) -> bool:
    """Same rules as the API path (samgov._keep), plus the office-state rule and the profile's SAM title phrases."""
    states = prof.get("states") or []
    if states and (rec.get("state") or rec.get("office_state")) not in states:
        return False  # the place of performance decides; only a blank one falls back to the buying office's state
    q = prof.get("samgov", [])
    # NAICS alone only counts inside a profile's states: nationwide, the bearing NAICS pulls in every DLA spare
    # part (thrust washers, internal gears; 205 rows on 2026-10-20). The API path is PSC-only there as well.
    if states and rec.get("naics") and rec["naics"] in {x["ncode"] for x in q if "ncode" in x}:
        return True
    if rec.get("psc") and any(str(rec["psc"]).startswith(x["ccode"]) for x in q if "ccode" in x):
        return True
    title = rec.get("title", "").lower()
    if any(_word(x).search(title) for x in prof.get("exclude_keywords", [])):
        return False
    if any(_word(x["title"]).search(title) for x in q if "title" in x):
        return True
    # a state-bound profile also takes its broad keyword list (as the API path does); a nationwide one does
    # not, because single words like 'apron' or 'lime' pull in airfield paving and place names nationwide
    return bool(states) and bool(match_profiles(rec.get("title", ""), {"x": prof}))


def _sig(path: Path, profiles: dict, today: str) -> str:
    """Cache key for the filtered rows: the file, the profiles, the date and this module's own code (a rule change
    must re-filter)."""
    h = hashlib.sha1(json.dumps(profiles, sort_keys=True).encode() + Path(__file__).read_bytes()).hexdigest()[:12]
    return f"{path.stat().st_size}:{path.stat().st_mtime_ns}:{h}:{today}"


def collect(profiles: dict, now: dt.datetime | None = None) -> tuple[dict, str]:
    """Open notices (deadline today or later; upcoming notices without a deadline until they archive) that match
    a profile. Returns ({notice_id: record}, note)."""
    try:
        path, note = refresh(now)
        if not path:
            return {}, note
        today = (now or now_utc()).date().isoformat()
        sig = _sig(path, profiles, today)
        cached = load_json(KEPT_FILE, {})
        if cached.get("sig") == sig:
            return cached.get("rows", {}), f"{note}; {len(cached.get('rows', {}))} matching (parsed earlier)"
        rows: dict[str, dict] = {}
        open_n = 0
        for r in iter_rows(path):
            if r.get("Active", "Yes") != "Yes" or r.get("Type") not in KEEP_TYPES:
                continue
            rec = normalize_row(r)
            if not rec["id"]:
                continue
            if rec["closing"]:
                if rec["closing"] < today:
                    continue
            elif not (rec["upcoming"] and (r.get("ArchiveDate") or "")[:10] >= today):
                continue
            open_n += 1
            for name, prof in profiles.items():
                if keep(rec, prof):
                    rows.setdefault(rec["id"], {**rec, "profiles": []})["profiles"].append(name)
        save_json(KEPT_FILE, {"sig": sig, "rows": rows, "open_notices": open_n, "parsed_at": iso()})
        return rows, f"{note}; {len(rows)} matching of {open_n} open notices"
    except Exception as e:  # noqa: BLE001 - the bulk file is a backup; it must never break a scan
        return {}, f"bulk file unusable: {type(e).__name__}: {str(e)[:150]}"
