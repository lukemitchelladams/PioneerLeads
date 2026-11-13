"""State of Colorado Vendor Self Service (ColoradoVSS, CGI Advantage 4): the PUBLIC published-solicitations list.

Who posts here: state agencies (DPA Capitol Complex / State Architect, CDOC, CDHS, DMVA, CPW, CDPHE, ...), the
community colleges (Red Rocks, Pikes Peak State, Pueblo CC, Otero, CCCS) and AHEC. About half of it never reaches
our BidNet feed, and what does arrives late and untagged (docs/portal-expansion-2026-10-28.md).

Public, no login (verified 2026-10-29): home page -> "View Published Solicitations" -> grid of open solicitations
(20/50/100 rows a page); clicking a solicitation number opens its detail (general info, schedule of events,
attachments, commodity lines). We NEVER log in, and nothing here touches the vendor sign-in form. A captcha / bot
check / 4xx on the home page stops the source with a clean "blocked" result; it is never worked around.

The site is an Angular app that talks JSON over POSTs to /Advantage4, so this module reads the JSON the app
receives instead of scraping the DOM:
  * list:   data.ds_data.T1SO_SRCH_QRY.row_data  (DOC_REF, DOC_DSCR, DEPT_NM, SO_CLSNG_DT_TM epoch ms, PUB_DT, ...)
  * detail: data.ds_data.T1SO_DOC_HDR (ADDL_INFO = the "Solicitation Instructions" text),
            T35SO_DOC_SE (schedule of events: "Mandatory Pre-Bid Walk", questions due ...),
            T34IN_OBJ_ATT_CTLG (attachments), T6SO_DOC_COMMLN (commodity lines)
There is no deep link to one solicitation: `url` is the portal; open it, choose "View Published Solicitations"
and search the solicitation number (`sol`).

Record id = the solicitation number without its version suffix (DQ1-AAHA-2027000145), so an amendment
(-1 -> -2) shows up as a CHANGE on the same bid, not as a new bid plus a closed one. `sol` carries the version.
"""
from __future__ import annotations

import datetime as dt
import re
import time
from pathlib import Path
from zoneinfo import ZoneInfo

from .bidnet import RSVP_BY_RX, RSVP_RX
from .common import DOWNLOAD_DIR, MANDATORY_RX, NOT_MANDATORY_RX, PREBID_RX, extract_prebid, parse_date

BASE = "https://prd.co.cgiadvantage.com/PRDVSS1X1/Advantage4"
CREDS: tuple = ()  # public list only: no login, ever
MT = ZoneInfo("America/Denver")
LIST_DS, DETAIL_DS = "T1SO_SRCH_QRY", "T1SO_DOC_HDR"
MAX_PAGES = 10  # 100 rows a page; 59 open on 2026-10-29

# Not biddable: Notice of Contractor Settlement (final-payment notices on finished construction) and Sole Source
# notices / intents to award. Kept in open_bids.json for completeness, never tagged as a match.
NOTICE_CODES = {"NCS1", "NPSS1"}
UPCOMING_CODES = {"RFI"}  # market research, like SAM.gov sources sought
STATUS = {"A": "Awarded", "C": "Closed", "M": "Amended", "O": "Open", "R": "Reopened", "X": "Cancelled"}
# SO_CAT_CD as listed in the grid's own metadata on 2026-10-29 (the live payload's list is preferred)
CATEGORIES = {
    "01": "Admin/Mgmt Svc", "02": "Agriculture", "03": "Arts/Crafts/Ent", "04": "Auto Goods/Svcs",
    "05": "Bldg Equip/Svcs", "06": "Clothing", "07": "Communication", "08": "Computers", "09": "Food",
    "10": "Furnishings", "11": "Furniture", "12": "Hardware", "13": "Highway Equip", "14": "Janitorial",
    "15": "Lab Supp/Equip", "16": "MRO", "17": "Med Supp/Equip", "18": "Misc Comm/Svc", "19": "Office Supplies",
    "20": "Print Equip/Svc", "21": "Personal Svcs", "22": "Construction", "23": "Rental/Leasing",
    "24": "Safety Prod/Svc", "25": "School/Library", "26": "Sport/Outdoor", "27": "Test/Sampling", "28": "Trades",
    "29": "Mass Transit", "30": "Water/Sewer", "31": "Environmental",
}
# The schedule-of-events names seen on VSS: "Mandatory Pre-Bid Walk", "Mandatory Pre-Submittal Conference",
# "Pre-Bid Conference and Site Tour". common.PREBID_RX covers these; the extras catch the other usual wordings.
EVENT_RX = re.compile(PREBID_RX.pattern + r"|bidders?'?\s+conference|pre[- ]?offer|vendor conference|site tour|"
                      r"walk[- ]?thru|pre[- ]?(?:bid|proposal|submittal)", re.I)
QUESTIONS_RX = re.compile(r"question|inquir|clarification", re.I)
BLOCK_RX = re.compile(r"captcha|<title>\s*Just a moment|cf-challenge|challenge-platform|Access Denied|Request Rejected|"
                      r"unusual traffic|are you a robot|verify you are (?:a )?human", re.I)

# stable data-qa-id hooks in the Angular grid (2026-10-29)
SEL_OPEN_LIST = "text=/View Published Solicitations/i"
SEL_100 = "[data-qa-id$='grid1.pagination.100Records']"
SEL_NEXT = "[data-qa-id$='grid1.Next']"
SEL_DOC_LINK = "a[data-qa-id$='solNumTypCat.DOC_REF']"
SEL_BACK = "[data-qa-id$='actionGroupForPage.back.button']"

# Attachments (manual Playwright run, 2026-11-12): the detail view has exactly one element whose aria-label names
# "Attachment"; clicking it opens the attachments panel (no download starts on that click). About 3 s later each file
# is a row whose text is the file name (`text=/<part of the name>/i`); clicking the row starts the download, and the
# download's suggested_filename is the attachment name. There is no <a href> for the files, and neither
# [class*='View-Attachments'] nor [title*='Attachment' i] matches anything.
PUBLIC_DOCS = True  # attachments are public: run.py downloads them without a login (the other sources need one)
SEL_ATTACH = "[aria-label*='Attachment' i]"
SEL_FILE_ROW = r"text=/\.(?:pdf|docx?|xlsx?|xlsm|pptx?|zip|csv|txt|rtf|dwg|jpe?g|png)\s*$/i"  # fallback: any file-named row
PANEL_WAIT_MS = 3000        # the panel's rows render shortly after the click
DOWNLOAD_TIMEOUT_MS = 15000  # a row click that starts no download in this time is a failure for that file
MAX_DOCS = 10               # files a bid may fetch in one scan (the rest wait for the next scan, like BidNet's cap)
DOWNLOAD_BUDGET_S = 90      # wall clock for one bid's attachments; past it the remaining files are left for next scan


class Challenged(RuntimeError):
    """Captcha / bot check / refusal. Named like bonfire.Challenged so run.py stops the detail pass at once."""


# ---------------------------------------------------------------- pure parsers (offline-testable)

def _blank(v):
    return None if v in ("", None) else v


def _flat(s) -> str:
    return " ".join(str(s or "").split())


def _ms(v) -> dt.datetime | None:
    """VSS dates are epoch milliseconds; date-only fields are local midnight in Mountain time."""
    try:
        return dt.datetime.fromtimestamp(int(v) / 1000, tz=MT) if v not in ("", None) else None
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def _ms_date(v) -> str | None:
    t = _ms(v)
    return t.date().isoformat() if t else None


def _ms_closing(v) -> tuple[str | None, str | None]:
    t = _ms(v)
    return (t.date().isoformat(), t.strftime("%Y-%m-%d %H:%M ") + (t.tzname() or "MT")) if t else (None, None)


def _ds(payload, name: str) -> dict | None:
    data = (payload or {}).get("data") if isinstance(payload, dict) else None
    return ((data or {}).get("ds_data") or {}).get(name)


def _rows(payload, name: str) -> list[dict]:
    return list((_ds(payload, name) or {}).get("row_data") or [])


def split_ref(doc_ref: str) -> tuple[str | None, str | None, int | None]:
    """'[DQ1,AAHA,2027000145,1][DQ1-AAHA-2027000145-1]' -> ('DQ1-AAHA-2027000145', 'DQ1-AAHA-2027000145-1', 1)."""
    parts = re.findall(r"\[([^\]]*)\]", doc_ref or "")
    if parts:
        f = [x.strip() for x in parts[0].split(",")]
        if len(f) == 4 and all(f[:3]):
            sol = parts[1].strip() if len(parts) > 1 and parts[1].strip() else "-".join(f)
            return "-".join(f[:3]), sol, int(f[3]) if f[3].isdigit() else None
    m = re.search(r"([A-Z0-9]+-[A-Z0-9]+-\d+)(?:-(\d+))?", doc_ref or "")
    if not m:
        return None, None, None
    return m.group(1), m.group(0), int(m.group(2)) if m.group(2) else None


def _categories(payload) -> dict:
    try:
        cv = payload["page_metadata"]["datasources"][LIST_DS]["columns"]["SO_CAT_CD"]["codedValuesList"]
        live = {k: v for d in cv for k, v in d.items()}
        return {**CATEGORIES, **live}
    except (KeyError, TypeError, AttributeError):
        return CATEGORIES


def parse_list_payload(payload: dict) -> list[dict]:
    """The grid's rows as bid records."""
    cats = _categories(payload)
    out = []
    for r in _rows(payload, LIST_DS):
        bid_id, sol, ver = split_ref(r.get("DOC_REF") or "")
        if not bid_id:
            continue
        closing, closing_text = _ms_closing(r.get("SO_CLSNG_DT_TM"))
        code = (r.get("DOC_CD") or "").strip()
        rec = {
            "source": "coloradovss", "id": bid_id, "sol": sol, "version": ver,
            "title": _flat(r.get("DOC_DSCR")), "agency": _flat(r.get("DEPT_NM")),
            "closing": closing, "closing_text": closing_text,
            "published": _ms_date(r.get("PUB_DT")), "amended": _ms_date(r.get("AMND_DT")),
            "type": _blank(_flat(r.get("DOC_CD_CONCAT"))) or code, "doc_code": code,
            "category": cats.get(r.get("SO_CAT_CD") or "") or None,
            "status": STATUS.get(r.get("SO_STA") or "", _blank(r.get("SO_STA"))),
            "buyer": _blank(_flat(r.get("BUYR_NM"))), "buyer_email": _blank((r.get("BUYR_EMAIL_AD") or "").strip()),
            "buyer_phone": _blank((r.get("BUYR_PH_NO") or "").strip()),
            "state": "CO", "url": BASE,
        }
        if code in NOTICE_CODES:
            rec["notice_only"] = True
        if code in UPCOMING_CODES:
            rec["upcoming"] = True
        out.append(rec)
    return out


def list_meta(payload: dict) -> dict:
    ds = _ds(payload, LIST_DS) or {}
    return {k: ds.get(k) for k in ("rows_sent", "rows_total", "rows_per_page", "total_count_suffix",
                                   "start_data_window", "end_data_window")}


def _rsvp(text: str) -> tuple[bool, str | None]:
    by = RSVP_BY_RX.search(text or "")
    return bool(RSVP_RX.search(text or "")), (parse_date(by.group(1)) if by else None)


def _event_mandatory(name: str) -> bool | None:
    if NOT_MANDATORY_RX.search(name):
        return False
    if MANDATORY_RX.search(name):
        return True
    return None


def prebid_from(events: list[dict], text: str) -> dict | None:
    """The pre-bid / site visit, in the prebid shape the other sources use ({date, mandatory, quote, rsvp, rsvp_by,
    source}). The portal's own Schedule of Events wins (a mandatory event first, then the earliest); when its event
    name does not say mandatory or optional, the instructions text may. Without an event, the instructions /
    commodity text is read with common.extract_prebid."""
    cands = [e for e in events if EVENT_RX.search(e.get("event") or "")]
    if cands:
        e = sorted(cands, key=lambda x: (_event_mandatory(x["event"]) is not True, x.get("date") or "9999"))[0]
        mand = _event_mandatory(e["event"])
        tx = extract_prebid(text) if text else None
        if mand is None and tx and tx.get("date") in (None, e.get("date")):
            mand = tx.get("mandatory")
        rsvp, rsvp_by = _rsvp(f"{e['event']} {text or ''}")
        quote = f"Schedule of Events: {e['event']}, {e.get('when') or e.get('date') or ''}".strip(", ")
        if tx and tx.get("quote"):
            quote += f". Instructions: {tx['quote']}"
        return {"date": e.get("date"), "mandatory": mand, "time": e.get("time"), "quote": quote[:420],
                "rsvp": rsvp, "rsvp_by": rsvp_by, "source": "coloradovss schedule of events"}
    pb = extract_prebid(text) if text else None
    if pb:
        rsvp, rsvp_by = _rsvp(pb.get("quote") or "")
        pb.update(rsvp=rsvp, rsvp_by=rsvp_by, source="coloradovss instructions")
    return pb


def parse_detail_payload(payload: dict) -> dict:
    """One solicitation's detail JSON -> the detail fields run.py merges into the list record."""
    hdrs = _rows(payload, DETAIL_DS)
    if not hdrs:
        return {}
    h = hdrs[0]
    events = []
    for r in _rows(payload, "T35SO_DOC_SE"):
        name, date, tm = _flat(r.get("SCHED_EVNT_DSCR")), _ms_date(r.get("SCHED_EVNT_DT")), _flat(r.get("SCHED_EVNT_TM_STND"))
        if name:
            events.append({"event": name, "date": date, "time": tm or None, "when": " ".join(x for x in (date, tm) if x)})
    docs, seen = [], set()
    for r in _rows(payload, "T34IN_OBJ_ATT_CTLG"):
        name = _flat(r.get("OBJ_ATT_NM"))
        if name and name not in seen:
            seen.add(name)
            docs.append({"name": name, "date": _ms_date(r.get("OBJ_ATT_DT")), "note": _blank(_flat(r.get("OBJ_ATT_DSCR")))})
    comm = _rows(payload, "T6SO_DOC_COMMLN") or _rows(payload, "T3SO_DOC_COMMLN")
    instructions = (h.get("ADDL_INFO") or "").strip()
    texts = [instructions] + [c.get("EXT_DSCR") or "" for c in comm]
    uniq = []
    for t in texts:
        if _flat(t) and _flat(t) not in (_flat(u) for u in uniq):
            uniq.append(t)
    description = _flat(" | ".join(uniq))
    closing, closing_text = _ms_closing(h.get("SO_CLSNG_DT_TM"))
    q = next((e for e in events if QUESTIONS_RX.search(e["event"]) and e.get("date")), None)
    loc = ", ".join(x for x in (_flat(h.get("LOC_NM")), _flat(h.get("CITY"))) if x)
    out = {
        "closing": closing, "closing_text": closing_text, "questions_due": q["date"] if q else None,
        "events": events, "prebid": prebid_from(events, "\n".join(uniq)), "documents": docs,
        "description": description[:2000] or None, "first_published": _ms_date(h.get("ORIG_PUB_DT")),
        "commodities": sorted({f"{c.get('COMM_CD')} {_flat(c.get('COMM_DSCR') or c.get('CL_DSCR'))}".strip()
                               for c in comm if c.get("COMM_CD")}),
        "office": loc or None,
    }
    sol = _flat(h.get("SRCH_DOC_ID"))
    if sol:
        out["sol"] = sol
    return out


# ---------------------------------------------------------------- browser side

class _Grab:
    """Collects the JSON bodies the Angular app receives from its POSTs to /Advantage4 (its data channel)."""

    def __init__(self, page):
        self.page, self.payloads = page, []
        page.on("response", self._on)

    def _on(self, resp) -> None:
        try:
            if resp.request.method == "POST" and "/Advantage4" in resp.url:
                self.payloads.append(resp.json())
        except Exception:  # noqa: BLE001 - a non-JSON body is not ours
            pass

    def wait_for(self, ds: str, after: int, timeout_ms: int = 60000) -> dict | None:
        waited = 0
        while True:
            hit = next((p for p in reversed(self.payloads[after:]) if _ds(p, ds) is not None), None)
            if hit is not None or waited >= timeout_ms:
                return hit
            self.page.wait_for_timeout(500)
            waited += 500


def _grab(session) -> _Grab:
    g = getattr(session, "_vss_grab", None)
    if g is None or g.page is not session.page:
        g = session._vss_grab = _Grab(session.page)
    return g


def _check_blocked(page, status: int | None = None) -> None:
    head = ""
    try:
        head = page.content()[:60000]
    except Exception:  # noqa: BLE001
        pass
    if (status and status in (401, 403, 429)) or BLOCK_RX.search(head):
        title = ""
        try:
            title = page.title()
        except Exception:  # noqa: BLE001
            pass
        raise Challenged(f"ColoradoVSS refused the public page (HTTP {status or '?'}, title {title[:60]!r}); "
                         "not bypassed")


def _click_and_wait(session, locator, ds: str, timeout_ms: int = 60000) -> dict | None:
    g = _grab(session)
    n = len(g.payloads)
    locator.click()
    return g.wait_for(ds, n, timeout_ms)


def _show_100(session) -> dict | None:
    """Switch the grid to 100 rows a page (it resets to 20 after every Back). Returns the new list payload."""
    b = session.page.locator(SEL_100)
    if not b.count() or (b.first.get_attribute("aria-current") or "") == "page":
        return None
    return _click_and_wait(session, b.first, LIST_DS, 45000)


HOME_RETRY_WAIT_MS = 8000   # one reload after this pause when the home page renders without the list link


def _home_link(session, attempts: int = 2):
    """Open the home page and wait for the "View Published Solicitations" link. The VSS home page sometimes
    renders without it (seen 2026-11-10 19:41Z and 22:35Z, HTTP 200, fine on the next run), so a miss gets one
    reload before it counts as an error. A block (401/403/429 or a challenge page) is raised at once, never retried."""
    page = session.page
    status = None
    for attempt in range(1, attempts + 1):
        resp = page.goto(BASE, wait_until="domcontentloaded")
        status = resp.status if resp else None
        link = page.locator(SEL_OPEN_LIST)
        try:
            link.first.wait_for(state="visible", timeout=60000)
            return link, status, attempt
        except Exception:  # noqa: BLE001
            _check_blocked(page, status)          # raises Challenged on a refusal: no retry past that
            if attempt < attempts:
                page.wait_for_timeout(HOME_RETRY_WAIT_MS)
                continue
            session.debug_dump("coloradovss-no-list-link")
            raise RuntimeError(f"'View Published Solicitations' not found on the home page (HTTP {status}) "
                               f"after {attempts} attempts")
    raise RuntimeError("unreachable")  # pragma: no cover


def open_list(session) -> dict:
    """Home page -> View Published Solicitations -> 100 rows a page. Returns the first page's list payload."""
    page = session.page
    g = _grab(session)
    n = len(g.payloads)
    link, status, _attempt = _home_link(session)
    if status in (401, 403, 429):  # the page rendered but the server said no: never push past that
        raise Challenged(f"ColoradoVSS home page answered HTTP {status}; not bypassed")
    first = _click_and_wait(session, link.first, LIST_DS)
    if first is None:
        _check_blocked(page)
        session.debug_dump("coloradovss-no-list-data")
        raise RuntimeError("no solicitation list data after 60 s")
    page.wait_for_timeout(1000)
    return _show_100(session) or g.wait_for(LIST_DS, n, 1000) or first


def _next_page(session) -> dict | None:
    b = session.page.locator(SEL_NEXT)
    if not b.count() or (b.first.get_attribute("aria-disabled") or "").lower() == "true":
        return None
    return _click_and_wait(session, b.first, LIST_DS, 45000)


def collect_open(session) -> tuple[dict, list[str], dict]:
    """Every open solicitation on the public list. Returns (rows by id, errors, totals); totals['_complete'] says
    the whole list was read, totals['_blocked'] that the site refused us (nothing was bypassed)."""
    rows: dict[str, dict] = {}
    errors: list[str] = []
    totals: dict = {}
    seen_raw = 0
    try:
        payload = open_list(session)
        meta = list_meta(payload)
        pages = 0
        while payload is not None and pages < MAX_PAGES:
            pages += 1
            got = parse_list_payload(payload)
            seen_raw += len(_rows(payload, LIST_DS))
            for r in got:
                rows[r["id"]] = r
            meta = list_meta(payload)
            more = meta.get("total_count_suffix") == "+" or (meta.get("end_data_window") or 0) < (meta.get("rows_total") or 0)
            if not more:
                break
            payload = _next_page(session)
        total = meta.get("rows_total")
        totals["statewide open"] = total
        totals["_complete"] = bool(rows) and meta.get("total_count_suffix") != "+" and seen_raw >= (total or 0)
        if not rows:
            session.debug_dump("coloradovss-empty-list")
            errors.append("ColoradoVSS: 0 solicitations parsed from the public list (debug HTML saved)")
        elif not totals["_complete"]:
            errors.append(f"ColoradoVSS: read {seen_raw} of {total}{meta.get('total_count_suffix') or ''} listed rows")
    except Challenged as e:
        totals["_blocked"] = str(e)
        errors.append(f"ColoradoVSS BLOCKED: {e}")
    except Exception as e:  # noqa: BLE001
        errors.append(f"ColoradoVSS list: {type(e).__name__}: {' '.join(str(e).split())[:160]}")
    session._vss_on_list = bool(rows)
    return rows, errors, totals


def _find_link(session, sol: str):
    """The grid link for `sol`, re-opening the list / switching to 100 rows / paging as needed."""
    page = session.page
    exact = re.compile(rf"^\s*{re.escape(sol)}\s*$")

    def look():
        loc = page.locator(SEL_DOC_LINK, has_text=exact)
        return loc.first if loc.count() else None

    hit = look()
    if hit:
        return hit
    if not page.locator(SEL_100).count():  # not on the grid: back from a detail page, or start over
        back = page.locator(SEL_BACK)
        if back.count():
            _click_and_wait(session, back.first, LIST_DS, 30000)
        if not page.locator(SEL_100).count():
            open_list(session)
    _show_100(session)
    hit = look()
    pages = 0
    while not hit and pages < MAX_PAGES and _next_page(session) is not None:
        pages += 1
        hit = look()
    return hit


def enrich(session, bid: dict) -> dict:
    """Open the solicitation's detail (public) and read its schedule of events, instructions and attachments."""
    page = session.page
    sol = bid.get("sol") or bid["id"]
    link = _find_link(session, sol)
    if link is None:
        _check_blocked(page)
        raise LookupError(f"{sol} not on the public list any more")
    payload = _click_and_wait(session, link, DETAIL_DS, 60000)
    if payload is None:
        _check_blocked(page)
        raise TimeoutError(f"no detail data for {sol} after 60 s")
    d = parse_detail_payload(payload)
    try:  # back to the grid for the next bid (it comes back at 20 rows; _find_link switches to 100 again)
        back = page.locator(SEL_BACK)
        if back.count():
            _click_and_wait(session, back.first, LIST_DS, 30000)
    except Exception:  # noqa: BLE001 - the next _find_link re-opens the list
        pass
    return {**bid, **{k: v for k, v in d.items() if v not in (None, [], "")}, "detail_checked": True}


# ---------------------------------------------------------------- attachments (public, no login)

_now = time.monotonic  # one bid's download clock, looked up at call time so tests can replace it


def _safe_name(name: str) -> str:
    """The on-disk file name for an attachment name (the same characters bidnet.doc_path keeps)."""
    return re.sub(r"[^\w.\- ]", "_", _flat(name)).strip()


def _dest_dir(bid: dict, dest_dir=None) -> Path:
    """bids/_watch/downloads/coloradovss/<solicitation id, / and spaces replaced>/ unless `dest_dir` names a folder."""
    if dest_dir:
        return Path(dest_dir)
    folder = re.sub(r"[^\w.\-]+", "_", str(bid.get("id") or bid.get("sol") or "")).strip("_") or "unknown"
    return DOWNLOAD_DIR / "coloradovss" / folder


def doc_path(bid: dict, d: dict, dest_dir=None) -> Path | None:
    """Where download_docs saves attachment `d` of `bid` (None when the name is unusable). run.py uses it to say how
    many of a watched bid's documents are not on disk yet."""
    safe = _safe_name(d.get("name") or "")
    return (_dest_dir(bid, dest_dir) / safe) if safe else None


def _row_pattern(name: str) -> str:
    """The `text=/.../i` body that finds the attachment's row: the longest run of plain characters in the file name (the
    manual run matched rows by a part of the name), escaped for a JavaScript regex; a short run means the whole name."""
    parts = [p.strip() for p in re.findall(r"[\w .\-]+", name)]
    best = max(parts, key=len) if parts else name
    if len(best) < 6:
        best = name
    return re.sub(r"[.*+?^${}()|\[\]\\/]", lambda m: "\\" + m.group(0), best)


def _pick_row(rows, name: str):
    """Of the rows whose text holds part of the name, the one holding the whole name (Addendum 1 vs Addendum 10), else
    the first; None when there is no such row."""
    try:
        n = rows.count()
    except Exception:  # noqa: BLE001
        return None
    if not n:
        return None
    want = _flat(name).lower()
    for i in range(min(n, 20)):
        try:
            if want in _flat(rows.nth(i).inner_text()).lower():
                return rows.nth(i)
        except Exception:  # noqa: BLE001
            continue
    return rows.first


def _fetch(page, row, dest: Path, safe: str | None, skip_existing: bool = True) -> tuple[Path | None, str | None]:
    """Click `row` inside expect_download and save the file as dest/<safe> (or under the download's own sanitised name).
    Returns (path written, None), (None, None) when skip_existing and the same-size file is already there, or
    (None, why not). A click that starts no download raises (Playwright's TimeoutError) for the caller to record."""
    with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as dl:
        row.click()
    f = dl.value
    name = safe or _safe_name(getattr(f, "suggested_filename", "") or "") or "attachment"
    target, tmp = dest / name, dest / (name + ".part")
    f.save_as(tmp)
    size = tmp.stat().st_size if tmp.is_file() else 0
    if size == 0:
        tmp.unlink(missing_ok=True)
        return None, "empty download"
    if skip_existing and target.is_file() and target.stat().st_size == size:
        tmp.unlink()  # the same file is already on disk (the fallback path only learns the name from the download)
        return None, None
    tmp.replace(target)  # a different size under the same name is a revised attachment: replaced, reported as saved
    return target, None


def _detail_open(page) -> bool:
    try:
        return page.locator(SEL_ATTACH).count() > 0
    except Exception:  # noqa: BLE001
        return False


def _open_detail(session, bid: dict) -> bool:
    """The grid is showing (enrich went Back after reading the detail): open the solicitation's detail view again."""
    sol = bid.get("sol") or bid["id"]
    link = _find_link(session, sol)
    if link is None:
        return False
    return _click_and_wait(session, link, DETAIL_DS, 60000) is not None


def _back_to_grid(session) -> None:
    """Close the attachment panel (Escape) and press Back, the way enrich does; if this does not land on the grid the
    next _find_link re-opens the list itself."""
    page = session.page
    try:
        kb = getattr(page, "keyboard", None)
        if kb is not None:
            kb.press("Escape")
            page.wait_for_timeout(300)
    except Exception:  # noqa: BLE001
        pass
    try:
        back = page.locator(SEL_BACK)
        if back.count():
            _click_and_wait(session, back.first, LIST_DS, 30000)
    except Exception:  # noqa: BLE001
        pass


def _dump(session, tag: str) -> None:
    try:
        session.debug_dump(tag)
    except Exception:  # noqa: BLE001
        pass


def download_docs(session, bid: dict, dest_dir=None, skip_existing: bool = True) -> list[str]:
    """Public, no login. Saves the solicitation's attachments (the names enrich read into bid["documents"]) that are not
    on disk yet under bids/_watch/downloads/coloradovss/<id>/<sanitised name>, and returns the paths saved this call
    (the same shape as bidnet.download_docs, so run.py calls both the same way). Assumes the detail view is open; when
    the grid is showing (enrich goes Back after reading the detail) the detail is re-opened through _find_link.
    Per-file failures never raise: they are collected in bid["download_errors"] (one short line each) and the paths
    saved before them are still returned; at most MAX_DOCS files and DOWNLOAD_BUDGET_S seconds a bid. Only a site
    refusal (Challenged, from re-opening the list) propagates, so run.py stops the pass like it does for BidNet.
    Afterwards the page is put back on the grid so the next bid's _find_link works."""
    page = session.page
    docs = [d for d in (bid.get("documents") or []) if d.get("name")][:MAX_DOCS]
    saved: list[str] = []
    notes: list[str] = []
    bid.pop("download_errors", None)
    if not docs:
        return saved
    dest = _dest_dir(bid, dest_dir)
    todo: list[tuple[str, str]] = []
    for d in docs:
        safe = _safe_name(d["name"])
        if not safe:
            continue
        if skip_existing and (dest / safe).is_file() and (dest / safe).stat().st_size > 0:
            continue  # already in hand (same name, non-empty); a revised attachment arrives under a new name on VSS
        todo.append((d["name"], safe))
    if not todo:
        return saved
    dest.mkdir(parents=True, exist_ok=True)
    t0 = _now()

    def over_time() -> bool:
        return _now() - t0 > DOWNLOAD_BUDGET_S

    try:
        if not _detail_open(page) and not _open_detail(session, bid):
            notes.append("detail view could not be re-opened for the attachments")
        ctl = page.locator(SEL_ATTACH)
        if not notes and not ctl.count():
            _dump(session, "coloradovss-no-attachment-control")
            notes.append("no Attachment control on the detail view")
        if not notes:
            ctl.first.click()  # opens the panel; no download starts on this click
            page.wait_for_timeout(PANEL_WAIT_MS)
            unmatched: list[tuple[str, str]] = []
            for name, safe in todo:
                if over_time():
                    notes.append(f"time cap {DOWNLOAD_BUDGET_S} s reached: {name} and the rest wait for the next scan")
                    break
                row = _pick_row(page.locator(f"text=/{_row_pattern(name)}/i"), name)
                if row is None:
                    unmatched.append((name, safe))
                    continue
                try:
                    path, why = _fetch(page, row, dest, safe, skip_existing)
                except Exception as e:  # noqa: BLE001 - the row click started no download in time
                    notes.append(f"{name}: no download started ({type(e).__name__})")
                    continue
                if path:
                    saved.append(str(path))
                elif why:
                    notes.append(f"{name}: {why}")
            if unmatched and len(unmatched) == len(todo):
                # none of the payload's names is a row in the panel: take the first file-named rows by their own names
                rows = page.locator(SEL_FILE_ROW)
                n = min(rows.count(), len(todo))
                for i in range(n):
                    if over_time():
                        notes.append(f"time cap {DOWNLOAD_BUDGET_S} s reached after {i} fallback rows")
                        break
                    try:
                        path, why = _fetch(page, rows.nth(i), dest, None, skip_existing)
                    except Exception as e:  # noqa: BLE001
                        notes.append(f"fallback row {i + 1}: no download started ({type(e).__name__})")
                        continue
                    if path:
                        saved.append(str(path))
                    elif why:
                        notes.append(f"fallback row {i + 1}: {why}")
                if not n or not saved:
                    _dump(session, "coloradovss-attachments")
                    notes.append(f"{len(unmatched)} attachment name(s) not found in the Attachment panel: "
                                 + ", ".join(nm for nm, _ in unmatched)[:200])
            elif unmatched:
                notes += [f"{name}: no row in the Attachment panel" for name, _ in unmatched]
    except Challenged:
        raise
    except Exception as e:  # noqa: BLE001 - never into the scan; the note says what happened
        notes.append(f"attachments: {type(e).__name__}: {' '.join(str(e).split())[:120]}")
    finally:
        _back_to_grid(session)
    if notes:
        bid["download_errors"] = notes[:MAX_DOCS]
    return saved
