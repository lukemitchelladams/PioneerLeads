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
from zoneinfo import ZoneInfo

from .bidnet import RSVP_BY_RX, RSVP_RX
from .common import MANDATORY_RX, NOT_MANDATORY_RX, PREBID_RX, extract_prebid, parse_date

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


def open_list(session) -> dict:
    """Home page -> View Published Solicitations -> 100 rows a page. Returns the first page's list payload."""
    page = session.page
    g = _grab(session)
    n = len(g.payloads)
    resp = page.goto(BASE, wait_until="domcontentloaded")
    status = resp.status if resp else None
    link = page.locator(SEL_OPEN_LIST)
    try:
        link.first.wait_for(state="visible", timeout=60000)
    except Exception:  # noqa: BLE001
        _check_blocked(page, status)
        session.debug_dump("coloradovss-no-list-link")
        raise RuntimeError(f"'View Published Solicitations' not found on the home page (HTTP {status})")
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
