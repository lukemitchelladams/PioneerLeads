"""SAM.gov without an API key: the public search and attachment endpoints sam.gov's own pages use.

    search      GET https://sam.gov/api/prod/sgs/v1/search/?index=opp&page=0&size=100&sort=-modifiedDate&is_active=true
                    &notice_type=o,k&pop_state=CO (or psc=3110)&modified_date.from=2026-11-17+00:00&response_date.from=...
    attachments GET https://sam.gov/api/prod/opps/v3/opportunities/<noticeId>/resources?excludeDeleted=false&withScanResult=false
    download    GET https://sam.gov/api/prod/opps/v3/opportunities/resources/files/<resourceId>/download  (303 to S3)

Why (2026-11-20): with SAM_API_KEY unset since 2026-11-19, SAM.gov coverage was the nightly bulk file alone (samgov_bulk.py):
no notice or amendment posted since the last rebuild, and no attachments. run.py uses this module two ways:
  * collect(): with the key unset, the profiles' queries (samgov.profile_queries, the API's own) against the public search for
    active solicitations modified in the last MODIFIED_DAYS days, matched locally by samgov.accept, rows in samgov.normalize's
    shape with via="public";
  * fetch_notice_files(): a watched notice's attachments, key or no key (the API path downloads none).
Every request of a scan comes out of one Budget (BIDWATCH_SAM_PUBLIC_MAX, default 40), SLEEP_S apart; a failure is a line in
the caller's errors, never an exception into the scan.

Seen live 2026-11-20: the search answers HTTP 406 to "Accept: application/json" (it serves application/hal+json); its date
filters take a date plus a UTC offset ("2026-11-17+00:00", "2026-11-17-07:00"), a bare date or an ISO timestamp is HTTP 400;
`state=` is ignored (0 hits) where `pop_state=` filters; a place of performance's "city" is a FIPS place or district code
("16000", "CO-03"), not a name; a notice without attachments answers 200 with no "_embedded"; deleted (superseded) attachments
are listed with deletedFlag "1"; a "link" attachment has no file (the download answers 400).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from . import samgov
from .common import DOWNLOAD_DIR, now_utc

SEARCH_API = "https://sam.gov/api/prod/sgs/v1/search/"
RESOURCES_API = "https://sam.gov/api/prod/opps/v3/opportunities/{nid}/resources?excludeDeleted=false&withScanResult=false"
DOWNLOAD_API = "https://sam.gov/api/prod/opps/v3/opportunities/resources/files/{rid}/download"
VIEW_URL = "https://sam.gov/opp/{nid}/view"
NOTICE_TYPES = "o,k"  # Solicitation, Combined Synopsis/Solicitation: the notices that take a bid
SOLICITATION_CODES = set(NOTICE_TYPES.split(","))
MODIFIED_DAYS = 3  # the window the bulk file may not have yet (a nightly rebuild, a weekend), with room to spare
PAGE_SIZE = 100
MAX_PAGES = 5  # per query; a 3-day Colorado window held 10 notices on 2026-11-20
MAX_REQUESTS_ENV = "BIDWATCH_SAM_PUBLIC_MAX"
MAX_REQUESTS = 40  # every public request of a scan: searches, look-ups, attachment lists and downloads
SLEEP_S = 0.7  # between two requests; tests set 0
TIMEOUT_S = 30
MAX_FAILS_IN_A_ROW = 2  # transport failures (timeout, refused, 5xx) in a row: sam.gov is not answering, stop asking this scan
MAX_DOCS = 10  # files fetched for one notice in one scan (as coloradovss.MAX_DOCS); the rest wait for the next scan
ACCEPT = "application/hal+json, */*"  # "application/json" alone is refused with HTTP 406
UA = "BrownBisonBidWatch/2.0"
_sleep = time.sleep  # looked up at call time so tests can replace it


class CapReached(RuntimeError):
    """The scan's Budget refused the request (cap reached, or sam.gov stopped answering)."""


class Budget:
    """One scan's allowance of public-endpoint requests, shared by the search, the look-ups and the attachment downloads: at most
    `max_requests` (default: env BIDWATCH_SAM_PUBLIC_MAX, else MAX_REQUESTS), SLEEP_S apart, and none once MAX_FAILS_IN_A_ROW
    transport failures came in a row (a timeout per query would otherwise hold the scan for minutes)."""

    def __init__(self, max_requests: int | None = None):
        if max_requests is None:
            try:
                max_requests = int(os.environ.get(MAX_REQUESTS_ENV) or MAX_REQUESTS)
            except ValueError:
                max_requests = MAX_REQUESTS
        self.max = max(0, int(max_requests))
        self.used = 0
        self.fails = 0  # transport failures in a row
        self.refused = 0  # requests not made: cap reached or sam.gov down

    @property
    def down(self) -> bool:
        return self.fails >= MAX_FAILS_IN_A_ROW

    def why(self) -> str:
        if self.down:
            return f"sam.gov did not answer {self.fails} requests in a row"
        return f"request cap {self.max} reached"

    def take(self) -> bool:
        if self.down or self.used >= self.max:
            self.refused += 1
            return False
        if self.used:
            _sleep(SLEEP_S)
        self.used += 1
        return True


def _http_get(url: str, timeout: int = TIMEOUT_S) -> bytes:
    """Default `fetch`: one GET, the body as bytes (redirects followed: a download goes 303 to S3)."""
    req = urllib.request.Request(url, headers={"Accept": ACCEPT, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _transport(e: Exception) -> bool:
    if isinstance(e, urllib.error.HTTPError):
        return e.code >= 500
    return isinstance(e, (urllib.error.URLError, ConnectionError, TimeoutError, OSError))


def _request(url: str, budget: Budget, fetch=None) -> bytes:
    """One budgeted request. `fetch(url) -> bytes` replaces the GET (tests). Raises CapReached when the budget says no, else
    whatever the GET raised; a transport failure counts towards Budget.down, any answer resets the count."""
    if not budget.take():
        raise CapReached(budget.why())
    try:
        body = (fetch or _http_get)(url)
    except Exception as e:
        budget.fails = budget.fails + 1 if _transport(e) else 0
        raise
    budget.fails = 0
    return body


def _json(body) -> dict:
    data = json.loads(body.decode("utf-8", "ignore") if isinstance(body, (bytes, bytearray)) else body)
    return data if isinstance(data, dict) else {}


def _date_param(d: dt.date) -> str:
    """The search's date filters: the date plus a UTC offset (a bare date or an ISO timestamp is HTTP 400)."""
    return f"{d.isoformat()}+00:00"


def _url(params: dict) -> str:
    return SEARCH_API + "?" + urllib.parse.urlencode(params, safe=",:")


def search_params(q: dict, now: dt.datetime, page: int = 0) -> dict | None:
    """samgov.profile_queries' query `q` as public-search parameters ({"state": "CO"} -> pop_state=CO, {"ccode": "3110"} ->
    psc=3110): active solicitations (NOTICE_TYPES) modified in the last MODIFIED_DAYS days with a response date today or later.
    None for a query this endpoint cannot express."""
    p = {"index": "opp", "page": page, "size": PAGE_SIZE, "sort": "-modifiedDate", "is_active": "true",
         "notice_type": NOTICE_TYPES, "modified_date.from": _date_param((now - dt.timedelta(days=MODIFIED_DAYS)).date()),
         "response_date.from": _date_param(now.date())}
    if q.get("state"):
        p["pop_state"] = q["state"]
    elif q.get("ccode"):
        p["psc"] = q["ccode"]
    else:
        return None
    return p


def _when(s) -> dt.datetime | None:
    try:
        t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def _first_code(items) -> str | None:
    """The first real code of a search result's naics / psc list (a PSC list also holds its group label, "J0 - MAINT, ...")."""
    for c in items or []:
        code = str((c or {}).get("code") or "").strip() if isinstance(c, dict) else ""
        if code and " " not in code:
            return code
    return None


def _set_aside(x: dict):
    sa = (x.get("solicitation") or {}).get("setAside")
    return (sa.get("value") or sa.get("code")) if isinstance(sa, dict) else (sa or None)


def normalize(x: dict) -> dict:
    """One search result in samgov.normalize's row shape (plus office_state like the bulk rows, and the notice's modifiedDate).
    closing is the response date in the notice's own time zone (responseDateActual), the date the API and the bulk file give."""
    nid = str(x.get("_id") or "")
    pops = [p for p in x.get("placeOfPerformance") or [] if isinstance(p, dict)]
    pop = next((p for p in pops if p.get("state")), pops[0] if pops else {})
    org = sorted((o for o in x.get("organizationHierarchy") or [] if isinstance(o, dict)), key=lambda o: o.get("level") or 0)
    office = next((o for o in reversed(org) if o.get("type") == "OFFICE"), org[-1] if org else {})
    typ = (x.get("type") or {}).get("value")
    city = str(pop.get("city") or "")
    return {
        "source": "samgov", "id": nid, "title": x.get("title") or "", "sol": x.get("solicitationNumber") or None,
        "agency": ".".join(str(o["name"]) for o in org if o.get("name")),  # the API's fullParentPathName form
        "type": typ, "upcoming": typ in samgov.UPCOMING_TYPES,
        "published": (x.get("publishDate") or "")[:10],
        "closing": str(x.get("responseDateActual") or x.get("responseDate") or "")[:10] or None,
        "naics": _first_code(x.get("naics")), "psc": _first_code(x.get("psc")), "set_aside": _set_aside(x),
        "state": pop.get("state") or None,
        "city": city if city and not re.search(r"\d", city) else None,  # a FIPS place / district code is no city name
        "office_state": ((office or {}).get("address") or {}).get("state") or None,
        "url": VIEW_URL.format(nid=nid), "description_url": None, "documents": [], "via": "public",
        "modified": x.get("modifiedDate"),
    }


def is_open_solicitation(x: dict, now: dt.datetime) -> bool:
    """Active, not cancelled, a solicitation type (NOTICE_TYPES), and a response date still ahead."""
    if x.get("isActive") is False or x.get("isCanceled"):
        return False
    if (x.get("type") or {}).get("code") not in SOLICITATION_CODES:
        return False
    t = _when(x.get("responseDate") or x.get("responseDateActual"))
    return bool(t and t > now)


def collect(profiles: dict, budget: Budget | None = None, fetch=None, now: dt.datetime | None = None) -> tuple[dict, list[str], dict]:
    """The keyless pass: each profile's samgov.profile_queries against the public search (search_params), up to MAX_PAGES pages a
    query, each open solicitation (is_open_solicitation) normalized and kept by samgov.accept. Returns ({notice id: row with
    "profiles"}, error lines, stats). An HTTP error or timeout is one line and the next query goes on; a refused request (the
    budget's cap, or sam.gov down) ends the pass with one line naming the queries left. Never raises."""
    budget = budget if budget is not None else Budget()
    now = now or now_utc()
    plan = [(name, prof, q) for name, prof in profiles.items() for q in samgov.profile_queries(prof)]
    rows: dict[str, dict] = {}
    errors: list[str] = []
    stats = {"queries": len(plan), "requests": 0, "results": 0, "kept": 0}
    used0 = budget.used
    for i, (name, prof, q) in enumerate(plan):
        page, stopped = 0, None
        while page < MAX_PAGES:
            params = search_params(q, now, page)
            if params is None:
                break
            try:
                data = _json(_request(_url(params), budget, fetch))
            except CapReached as e:
                stopped = str(e)
                break
            except Exception as e:  # noqa: BLE001 - one line, then the next query
                errors.append(f"SAM.gov public search {q}: {samgov._err_text(e)}")
                break
            res = (data.get("_embedded") or {}).get("results") or []
            stats["results"] += len(res)
            for x in res:
                if not isinstance(x, dict) or not is_open_solicitation(x, now):
                    continue
                rec = normalize(x)
                if not samgov.accept(rec, prof, q):
                    continue
                cur = rows.setdefault(rec["id"], {**rec, "profiles": []})
                if name not in cur["profiles"]:
                    cur["profiles"].append(name)
            pages = int((data.get("page") or {}).get("totalPages") or 0)
            page += 1
            if not res or page >= pages:
                break
            if page >= MAX_PAGES:
                errors.append(f"SAM.gov public search {q}: {pages} pages, the first {MAX_PAGES} read")
        if stopped:
            errors.append(f"SAM.gov public search: {stopped} after {budget.used - used0} requests; "
                          f"{len(plan) - i} of {len(plan)} queries wait for the next scan")
            break
    stats["requests"] = budget.used - used0
    stats["kept"] = len(rows)
    return rows, errors, stats


def find_notices(term: str, budget: Budget, fetch=None) -> list[dict]:
    """Active notices the public search finds for `term` (a solicitation number), normalized; any notice type, since a watched notice
    can be a sources sought. One budgeted request. Raises on failure (CapReached included); the caller records it."""
    params = {"index": "opp", "page": 0, "size": 10, "sort": "-modifiedDate", "is_active": "true", "q": term}
    data = _json(_request(_url(params), budget, fetch))
    res = (data.get("_embedded") or {}).get("results") or []
    return [normalize(x) for x in res if isinstance(x, dict) and x.get("isActive") is not False and not x.get("isCanceled")]


# ---------------------------------------------------------------- attachments of a watched notice

def dest_dir(notice_id: str) -> Path:
    """bids/_watch/downloads/samgov/<notice id>/, where the files of a SAM.gov notice go (as bidnet/<id>/, coloradovss/<id>/)."""
    return DOWNLOAD_DIR / "samgov" / (re.sub(r"[^\w.\-]+", "_", str(notice_id)).strip("_") or "unknown")


def safe_name(name: str) -> str:
    """The on-disk name of an attachment (the characters bidnet.doc_path keeps)."""
    return re.sub(r"[^\w.\- ]", "_", " ".join(str(name or "").split())).strip()


def _norm(name) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name or "").lower())


def _size(att: dict) -> int | None:
    try:
        return int(att.get("size")) if att.get("size") not in (None, "") else None
    except (TypeError, ValueError):
        return None


def in_hand(att: dict, dirs) -> Path | None:
    """The file already on disk for attachment `att`, or None: in one of `dirs` (the notice's downloads folder, the bid folder's
    docs/), a non-empty file whose name, letters and digits only, is the attachment's or ends with it (a person's prefix such as
    "C04a " or "B08_-_"), with the attachment's size when SAM.gov states one (a revised file under the same name is not in hand)."""
    want, size = _norm(att.get("name")), _size(att)
    if not want:
        return None
    for d in dirs:
        d = Path(d)
        if not d.is_dir():
            continue
        for f in d.iterdir():
            if f.is_file() and not f.name.endswith(".part") and _norm(f.name).endswith(want):
                n = f.stat().st_size
                if n > 0 and (size is None or n == size):
                    return f
    return None


def list_attachments(notice_id: str, budget: Budget, fetch=None) -> list[dict]:
    """Every attachment record of the notice (deleted ones included, flagged deletedFlag "1"). One budgeted request; raises."""
    data = _json(_request(RESOURCES_API.format(nid=urllib.parse.quote(str(notice_id))), budget, fetch))
    out: list[dict] = []
    for g in (data.get("_embedded") or {}).get("opportunityAttachmentList") or []:
        out += [a for a in (g or {}).get("attachments") or [] if isinstance(a, dict)]
    return out


def _bad_body(body: bytes, att: dict) -> str | None:
    if not body:
        return "empty download"
    if not str(att.get("name") or "").lower().endswith((".htm", ".html")) \
            and re.match(rb"\s*(<!doctype html|<html)", body[:200], re.I):
        return "an HTML page came back instead of the file"
    size = _size(att)
    if size is not None and len(body) != size:
        return f"got {len(body)} bytes, SAM.gov lists {size} (tried again next scan)"
    return None


def fetch_notice_files(notice_id: str, budget: Budget, extra_dirs=(), fetch=None, max_docs: int = MAX_DOCS,
                       dest: Path | None = None) -> dict:
    """List notice `notice_id`'s attachments (one request) and download each live, public "file" attachment not in hand (in_hand:
    `dest`, default dest_dir(notice_id), or one of `extra_dirs`) into `dest`, at most `max_docs` tries a call, one request each.
    Returns {"listed": bool, "documents": [{name: resource id, url, file}] (the live public files, named by resource id as the API's
    resourceLinks are), "saved": [paths], "in_hand": [names], "links": [names], "restricted": [names], "deferred": [names],
    "errors": [lines], "stopped": why the budget refused, or None}. Deleted (superseded) attachments are left out, "link" ones and
    non-public ones are only named. Never raises."""
    out = {"listed": False, "documents": [], "saved": [], "in_hand": [], "links": [], "restricted": [], "deferred": [],
           "errors": [], "stopped": None}
    dest = Path(dest) if dest else dest_dir(notice_id)
    try:
        atts = list_attachments(notice_id, budget, fetch)
    except CapReached as e:
        out["stopped"] = str(e)
        return out
    except Exception as e:  # noqa: BLE001
        out["errors"].append(f"attachment list: {samgov._err_text(e)}")
        return out
    out["listed"] = True
    todo = []
    for a in atts:
        if str(a.get("deletedFlag") or "0") == "1":
            continue  # superseded by a later posting
        name = str(a.get("name") or a.get("resourceId") or "?")
        if a.get("type") != "file":
            out["links"].append(name)
            continue
        if str(a.get("accessLevel") or "public").lower() != "public":
            out["restricted"].append(name)
            continue
        rid = a.get("resourceId")
        if not rid:
            continue
        url = DOWNLOAD_API.format(rid=rid)
        out["documents"].append({"name": rid, "url": url, "file": name})
        if in_hand(a, [dest, *extra_dirs]):
            out["in_hand"].append(name)
        else:
            todo.append((a, name, rid, url))
    taken: set[str] = set()
    for i, (a, name, rid, url) in enumerate(todo):
        if i >= max_docs:
            out["deferred"] += [n for _, n, _, _ in todo[i:]]
            break
        try:
            body = _request(url, budget, fetch)
        except CapReached as e:
            out["stopped"] = str(e)
            out["deferred"] += [n for _, n, _, _ in todo[i:]]
            break
        except Exception as e:  # noqa: BLE001 - this file only; the next one is tried
            out["errors"].append(f"{name}: {samgov._err_text(e)}")
            continue
        why = _bad_body(body, a)
        if why:
            out["errors"].append(f"{name}: {why}")
            continue
        fn = safe_name(name) or rid
        if fn in taken:  # two live attachments under one name: keep both
            p = Path(fn)
            fn = f"{p.stem} ({rid[:8]}){p.suffix}"
        taken.add(fn)
        try:
            dest.mkdir(parents=True, exist_ok=True)
            target = dest / fn
            tmp = target.with_name(target.name + ".part")
            tmp.write_bytes(body)
            os.replace(tmp, target)
        except OSError as e:
            out["errors"].append(f"{name}: not saved: {type(e).__name__}: {str(e)[:120]}")
            continue
        out["saved"].append(str(target))
    return out
