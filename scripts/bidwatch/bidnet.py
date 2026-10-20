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
CREDS = ("BIDNET_USER", "BIDNET_PASS")
MAX_PAGES = 40

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
    """Return (rows, next_page_url). Each row: id, title, url, agency, closing, published, context."""
    soup = BeautifulSoup(html, "lxml")
    rows, seen = [], set()
    for a in soup.find_all("a", href=True):
        m = SOL_HREF.search(a["href"])
        title = " ".join(a.get_text(" ").split())
        if not m or len(title) < 4 or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        # walk up to the row/card that holds the dates
        node, ctx = a, title
        for _ in range(6):
            node = node.parent
            if node is None:
                break
            ctx = " ".join(node.get_text(" ").split())
            if re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", ctx) and len(ctx) > len(title) + 5:
                break
        url = urljoin(base_url, a["href"])
        agency = _agency_from_url(url)
        closing = _labeled_date(ctx, r"clos\w*|due|deadline") or _last_date(ctx)
        published = _labeled_date(ctx, r"publi\w*|issued|posted")
        rows.append({"id": m.group(1), "title": title, "url": url, "agency": agency,
                     "closing": closing, "published": published, "context": ctx[:400]})
    nxt = None
    link = soup.find("a", attrs={"rel": "next"}) or soup.find("a", string=re.compile(r"^\s*(next|›|»)\s*$", re.I))
    if link and link.get("href"):
        nxt = urljoin(base_url, link["href"])
    return rows, nxt


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
        "login_required_for_docs": bool(re.search(r"(log ?in|register) to (view|download)", text, re.I)),
    }


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

def collect_open(session, keywords: list[str], max_pages: int = MAX_PAGES) -> tuple[dict, list[str]]:
    """Statewide Colorado list + keyword searches. Returns ({id: row}, errors)."""
    page, out, errors = session.page, {}, []
    starts = [CO_OPEN] + [f"{CO_OPEN}?{urlencode({'keywords': k})}" for k in keywords]
    for start in starts:
        url, n = start, 0
        while url and n < max_pages:
            n += 1
            try:
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(1200)
                rows, nxt = parse_listing(page.content(), url)
            except Exception as e:  # noqa: BLE001
                errors.append(f"BidNet list {url}: {type(e).__name__}: {str(e)[:150]}")
                break
            if not rows and n == 1:
                session.debug_dump("empty-list")
                errors.append(f"BidNet list parsed 0 rows: {url} (debug HTML saved)")
            for r in rows:
                out.setdefault(r["id"], {**r, "source": "bidnet"})
            url = nxt if nxt != url else None
    return out, errors


def enrich(session, bid: dict) -> dict:
    session.page.goto(bid["url"], wait_until="domcontentloaded")
    session.page.wait_for_timeout(1200)
    d = parse_detail(session.page.content(), bid["url"])
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
