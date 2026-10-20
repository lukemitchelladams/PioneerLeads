"""BidNet Direct (incl. Rocky Mountain E-Purchasing System) — Colorado open bids, logged in.

What it collects every run
  1. Statewide Colorado open-bids list (every page), plus a keyword search per profile keyword.
  2. Detail page for every bid that matches a profile or is on the watchlist: closing date,
     pre-bid / site-walk text (mandatory or not, quoted), document list.
  3. Watchlist bids: diff the document list and dates against last run -> ADDENDUM / DATE CHANGE.
  4. When logged in, downloads documents for watched bids into bids/_watch/downloads/bidnet/<id>/.

Parsing works on raw HTML with BeautifulSoup so it can be tested offline against saved pages
(tests/test_bidwatch.py). Selectors are generic on purpose: any link to /solicitations/.../<digits>.
When a page parses to nothing, the HTML + screenshot go to bids/_watch/debug/ for a selector fix.
"""
from __future__ import annotations

import re
from urllib.parse import urlencode, urljoin

from bs4 import BeautifulSoup

from .common import DOWNLOAD_DIR, extract_prebid, parse_date

BASE = "https://www.bidnetdirect.com"
LOGIN_URL = BASE + "/public/authentication/login"
CO_OPEN = BASE + "/colorado/solicitations/open-bids"
# The statewide list has two tabs: BUYER = bids posted on Rocky Mountain E-Purchasing by member agencies
# (~400, the ones we can actually respond to through BidNet), AGGREGATE = bids BidNet copied from other
# agency sites (~180). Pages are /open-bids/page2, /page3 ... 25 rows each; ?keywords= filters both.
CO_TABS = ["BUYER", "AGGREGATE"]
CREDS = ("BIDNET_USER", "BIDNET_PASS")
MAX_PAGES = 40
REGION_STATE = {"colorado": "CO", "wyoming": "WY"}
LOCKED_RX = re.compile(r"registered members only|log ?in to (view|download)|register to (view|download)", re.I)

SOL_HREF = re.compile(r"/solicitations/[^?#]*?/(\d{5,})(?:[/?#]|$)")
FILE_HREF = re.compile(r"\.(pdf|docx?|xlsx?|zip|dwg)(\?|$)|/document|/download|attachment", re.I)


# ---------------- login ----------------

def login(page, user: str, pw: str) -> None:
    page.goto(LOGIN_URL, wait_until="domcontentloaded")
    _fill_first(page, ["input[name='j_username']", "input[name='username']", "input#username",
                       "input[type='email']", "input[name='email']"], user)
    _fill_first(page, ["input[name='j_password']", "input[name='password']", "input#password",
                       "input[type='password']"], pw)
    _click_first(page, ["button[type='submit']", "input[type='submit']", "button:has-text('Log in')",
                        "button:has-text('Login')", "button:has-text('Sign in')"])
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)


def is_logged_in(page) -> bool:
    page.goto(BASE + "/colorado", wait_until="domcontentloaded")
    page.wait_for_timeout(1500)
    html = page.content().lower()
    if re.search(r"log ?out|sign ?out|my account|my profile", html) and "authentication/login" not in page.url:
        return True
    return False


def _fill_first(page, sels, value):
    for s in sels:
        if page.locator(s).count():
            page.fill(s, value)
            return
    raise RuntimeError(f"no field matched {sels[0]}…")


def _click_first(page, sels):
    for s in sels:
        if page.locator(s).count():
            page.click(s)
            return
    raise RuntimeError(f"no button matched {sels[0]}…")


# ---------------- parsing (pure functions, testable offline) ----------------

def parse_listing(html: str, base_url: str = BASE) -> tuple[list[dict], str | None]:
    """Return (rows, next_page_url). Each row: id, title, url, region, state, closing, published, context.

    Real page (2026-10-20): <tr class="mets-table-row"> with a.solicitation-link, .sol-region-item,
    .sol-publication-date .date-value, .sol-closing-date .date-value; next page = <a class="next">.
    Falls back to any link to /solicitations/.../<digits> so a markup change degrades gracefully."""
    soup = BeautifulSoup(html, "lxml")
    rows, seen = [], set()
    for tr in soup.select("tr.mets-table-row"):
        a = tr.select_one("a.solicitation-link[href]")
        m = SOL_HREF.search(a["href"]) if a else None
        if not m or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        region = _txt(tr.select_one(".sol-region-item"))
        rows.append({"id": m.group(1), "title": _txt(a), "url": urljoin(base_url, a["href"]),
                     "agency": "", "region": region, "state": REGION_STATE.get(region.lower()),
                     "closing": parse_date(_txt(tr.select_one(".sol-closing-date .date-value"))),
                     "published": parse_date(_txt(tr.select_one(".sol-publication-date .date-value"))),
                     "context": _txt(tr)[:400]})
    if not rows:
        rows = _parse_listing_generic(soup, base_url, seen)
    nxt = None
    link = soup.select_one("a.next[href]") or soup.find("a", attrs={"rel": "next"}) \
        or soup.find("a", string=re.compile(r"^\s*(next|›|»)\s*$", re.I))
    if link and link.get("href"):
        nxt = urljoin(base_url, link["href"])
    return rows, nxt


def total_count(html: str) -> int | None:
    """'400 Open Solicitations' header on the list page."""
    text = BeautifulSoup(html, "lxml").get_text(" ")
    if re.search(r"can.t find any current bids", text, re.I):
        return 0
    m = re.search(r"([\d,]+)\s+Open Solicitations", text)
    return int(m.group(1).replace(",", "")) if m else None


def _txt(node) -> str:
    return " ".join(node.get_text(" ").split()) if node is not None else ""


def _parse_listing_generic(soup, base_url: str, seen: set) -> list[dict]:
    rows = []
    for a in soup.find_all("a", href=True):
        m = SOL_HREF.search(a["href"])
        title = _txt(a)
        if not m or len(title) < 4 or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        node, ctx = a, title
        for _ in range(6):
            node = node.parent
            if node is None:
                break
            ctx = _txt(node)
            if re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", ctx) and len(ctx) > len(title) + 5:
                break
        url = urljoin(base_url, a["href"])
        rows.append({"id": m.group(1), "title": title, "url": url, "agency": _agency_from_url(url),
                     "closing": _labeled_date(ctx, r"clos\w*|due|deadline") or _last_date(ctx),
                     "published": _labeled_date(ctx, r"publi\w*|issued|posted"), "context": ctx[:400]})
    return rows


def parse_detail(html: str, url: str = "") -> dict:
    soup = BeautifulSoup(html, "lxml")
    text = " ".join(soup.get_text(" ").split())
    docs = []
    for a in soup.find_all("a", href=True):
        name = " ".join(a.get_text(" ").split())
        if FILE_HREF.search(a["href"]) or re.search(r"\.(pdf|docx?|xlsx?|zip)\b", name, re.I):
            docs.append({"name": name or a["href"].rsplit("/", 1)[-1], "url": urljoin(url or BASE, a["href"])})
    # de-dup by name
    uniq = {d["name"]: d for d in docs}
    return {
        "closing": _labeled_date(text, r"closing date|clos\w* date|due date|submission deadline|bid due"),
        "published": _labeled_date(text, r"publication date|published|issue date|posted"),
        "questions_due": _labeled_date(text, r"question\w* (due|deadline)|deadline for questions"),
        "prebid": extract_prebid(text),
        "documents": sorted(uniq.values(), key=lambda d: d["name"]),
        "closing_text": _labeled_text(text, r"Closing Date", r"\d{1,2}/\d{1,2}/\d{4}(?: \d{1,2}:\d{2} [AP]M(?: [A-Z]{3})?)?"),
        "agency": _field(text, "Issuing Organization"),
        "sol": _field(text, "Solicitation Number"),
        "login_required_for_docs": bool(LOCKED_RX.search(text)),
    }


_FIELDS = r"Location|Publication Date|Closing Date|Issuing Organization|Owner Organization|Solicitation Number|" \
    r"Solicitation Type|Description|Bid Documents|Buyer Contact|Get instant access"


def _field(text: str, label: str) -> str | None:
    """Value after a detail-page label, or None when it is 'Locked Registered members only'."""
    m = re.search(rf"{label}\s+(.{{1,160}}?)\s+(?:{_FIELDS})\b", text)
    if not m or LOCKED_RX.search(m.group(1)) or m.group(1).startswith("Locked"):
        return None
    return m.group(1).strip()


def _labeled_text(text: str, label: str, val_rx: str) -> str | None:
    m = re.search(rf"{label}\s*[:\-]?\s*({val_rx})", text)
    return m.group(1) if m else None


def _labeled_date(text: str, label_rx: str) -> str | None:
    m = re.search(rf"(?:{label_rx})\s*[:\-]?\s*(?P<val>.{{0,40}})", text, re.I)
    return parse_date(m.group("val")) if m else None


def _last_date(text: str) -> str | None:
    dates = re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}", text)
    return parse_date(dates[-1]) if dates else None


def _agency_from_url(url: str) -> str:
    m = re.search(r"/colorado/([^/]+)/solicitations/", url)
    return m.group(1).replace("-", " ").title() if m else ""


# ---------------- collection (needs a browser) ----------------

def page_url(start: str, n: int) -> str:
    """Page n of a list URL: /open-bids?x=y -> /open-bids/page2?x=y."""
    if n <= 1:
        return start
    path, _, q = start.partition("?")
    return f"{path}/page{n}" + (f"?{q}" if q else "")


def _walk(session, name: str, start: str, out: dict, errors: list, totals: dict, max_pages: int) -> None:
    page, url, n = session.page, start, 0
    while url and n < max_pages:
        n += 1
        try:
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(800)
            html = page.content()
            rows, nxt = parse_listing(html, url)
        except Exception as e:  # noqa: BLE001
            errors.append(f"BidNet list {url}: {type(e).__name__}: {str(e)[:150]}")
            return
        if n == 1:
            totals[name] = total_count(html)
            if not rows and totals[name] != 0:
                session.debug_dump("empty-list")
                errors.append(f"BidNet list parsed 0 rows: {url} (debug HTML saved)")
        for r in rows:
            r["list"] = "aggregate" if "AGGREGATE" in name else "rmeps"
            out.setdefault(r["id"], {**r, "source": "bidnet"})
        # the next link carries no query string; keep ours so the tab/keyword filter sticks
        url = page_url(start, n + 1) if (nxt and rows) else None


def collect_open(session, keywords: list[str], max_pages: int = MAX_PAGES,
                 force_keywords: bool = False) -> tuple[dict, list[str], dict]:
    """Statewide Colorado list, both tabs, every page. That list is complete (every open bid, verified
    2026-10-20: the oldest 75 sit inside the newest 400), so keyword searches only run as a fallback
    when it comes back short of the totals the site reports, or when force_keywords is set.
    Returns ({id: row}, errors, {list name: count the site reports})."""
    out, errors, totals = {}, [], {}
    for t in CO_TABS:
        _walk(session, f"statewide {t}", f"{CO_OPEN}?{urlencode({'selectedContent': t})}", out, errors, totals, max_pages)
    expected = sum(v for k, v in totals.items() if v)
    if force_keywords or not expected or len(out) < expected:
        if not force_keywords:
            errors.append(f"BidNet statewide list short ({len(out)} of {expected or '?'}); ran keyword searches")
        for k in keywords:
            _walk(session, f"kw {k}", f"{CO_OPEN}?{urlencode({'keywords': k})}", out, errors, totals, max_pages)
    return out, errors, totals


def enrich(session, bid: dict) -> dict:
    """Detail page. Public visitors see only location + publication/closing date (and closing time);
    issuing org, solicitation #, description, documents and buyer contact are 'Registered members only'."""
    session.page.goto(bid["url"], wait_until="domcontentloaded")
    session.page.wait_for_timeout(1200)
    d = parse_detail(session.page.content(), bid["url"])
    if d.get("login_required_for_docs") and not session.logged_in:
        d["prebid"] = None  # the description is locked, so any 'pre-bid' hit came from page chrome
    return {**bid, **{k: v for k, v in d.items() if v not in (None, [])}, "detail_checked": True}


def download_docs(session, bid: dict) -> list[str]:
    """Logged-in only. Saves each document; returns repo-relative paths."""
    saved = []
    dest = DOWNLOAD_DIR / "bidnet" / bid["id"]
    dest.mkdir(parents=True, exist_ok=True)
    for d in bid.get("documents", [])[:60]:
        try:
            with session.page.expect_download(timeout=45000) as dl:
                try:
                    session.page.goto(d["url"])
                except Exception:  # noqa: BLE001 - Chromium aborts navigation when a download starts
                    pass
            f = dl.value
            target = dest / f.suggested_filename
            f.save_as(target)
            saved.append(str(target))
        except Exception:  # noqa: BLE001
            continue
    return saved
