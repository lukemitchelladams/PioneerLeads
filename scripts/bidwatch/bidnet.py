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

import datetime as dt
import os
import time

from . import mailcode
from .common import (BIDNET_COOLDOWN_FILE, BIDNET_COOLDOWN_H, CODE_FILE, CODE_MARKER_TTL_H, CODE_NEEDED_MARKER,
                     DOWNLOAD_DIR, LoginBlocked, extract_prebid, iso, parse_date)

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
# After a few full scans in a short time BidNet answers with a JavaScript robot check instead of the list
# (seen 2026-10-20 on the 3rd scan in ~15 min). We stop and report it; we do not try to get around it.
BOT_RX = re.compile(r"verify that you.re not a robot|JavaScript is disabled", re.I)
LOCKED_RX = re.compile(r"registered members only|log ?in to (view|download)|register to (view|download)", re.I)

OPEN_NOTICE_HREF = re.compile(r"/open-notice/(\d{6,})(?:[/?#]|$)")
SOL_HREF = re.compile(r"/solicitations/[^?#]*?/(\d{5,})(?:[/?#]|$)")
FILE_HREF = re.compile(r"\.(pdf|docx?|xlsx?|zip|dwg)(\?|$)|/document|/download|attachment", re.I)


# ---------------- login ----------------

# Every public BidNet page carries the login window (form#loginWindowForm, verified 2026-10-20):
#   input#loginBox_j_username (name=j_username), input#loginBox_j_password (name=j_password),
#   hidden _csrf, button#loginWindowButton -> POST /public/authentication/login.
# A GET of that URL answers 202/302 (not a page), so we submit the window on the home page instead.
LOGIN_USER_SEL = ["#loginBox_j_username", "input[name='j_username']", "input[name='username']", "input#username",
                  "input[type='email']", "input[name='email']"]
LOGIN_PASS_SEL = ["#loginBox_j_password", "input[name='j_password']", "input[name='password']", "input#password",
                  "input[type='password']"]
LOGIN_BTN_SEL = ["#loginWindowButton", "#loginWindowForm button[type='submit']", "button[type='submit']",
                 "input[type='submit']", "button:has-text('Login')", "button:has-text('Log in')"]
LOGIN_FORM_SEL = "input[name='j_username']"
# Logged-in pages carry a#supplier_logout_link (href /public/authentication/logout) and a filled
# input[name=session_username]; logged-out pages carry the login window instead (verified 2026-10-20).
LOGGED_IN_SEL = "#supplier_logout_link, a[href*='authentication/logout'], a[href*='logout' i]"


def _page_logged_in(page) -> bool:
    """Decide from the page itself, never from the URL: after a single-sign-on restore the URL can still
    contain authentication/login while the page is fully logged in (seen 2026-10-20 04:55, endurance check 4)."""
    try:
        return page.locator(LOGGED_IN_SEL).count() > 0 and page.locator(LOGIN_FORM_SEL).count() == 0
    except Exception:  # noqa: BLE001
        return False
# New-device check (confirmed 2026-10-20 from the inbox): after a password login from a device BidNet has not
# seen, it emails "Your BidNet Direct confirmation code" (noreply@bidnet.com, 6 digits) and shows a code
# prompt. EVERY password login issues a NEW code, so the code is only good inside the browser session that
# triggered it. We therefore stay on the prompt and wait up to BIDNET_CODE_WAIT seconds (default 300) for
# ~/.brownbison/bidnet_code (scripts/bidwatch/set_code.py) or BIDNET_CODE. If nobody supplies it, we write
# CODE_NEEDED_MARKER and make no further password logins until it is deleted, so Luke is not emailed a code
# every cycle. The confirmed-device cookie is saved with the session, so this happens once per container.
CODE_PROMPT_RX = re.compile(r"confirmation code|verification code|security code|one[- ]time (code|passcode)|"
                            r"code (we |that was |was )?(sent|emailed)|enter the code", re.I)
CODE_INPUT_SEL = ["input[autocomplete='one-time-code']", "input[name*='code' i]", "input[id*='code' i]",
                  "input[name*='token' i]", "input[type='tel']", "form input[type='text']"]
CODE_BTN_SEL = ["form:has(input[name*='code' i]) button[type='submit']", "button:has-text('Confirm')",
                "button:has-text('Verify')", "button:has-text('Submit')", "button:has-text('Continue')",
                "button[type='submit']", "input[type='submit']"]


def _home() -> str:
    return BASE + "/colorado"  # derived at call time so tests can point BASE at a fake portal


def _marker_expired() -> bool:
    try:
        return time.time() - CODE_NEEDED_MARKER.stat().st_mtime > CODE_MARKER_TTL_H * 3600
    except FileNotFoundError:
        return False


def cooldown_until() -> str | None:
    """ISO time BidNet is on cool-down until (after a robot check), or None."""
    try:
        until = BIDNET_COOLDOWN_FILE.read_text().strip()
    except FileNotFoundError:
        return None
    return until if until > iso() else None


def start_cooldown() -> str:
    import datetime as _dt
    until = (_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(hours=BIDNET_COOLDOWN_H)).isoformat(timespec="seconds")
    try:
        BIDNET_COOLDOWN_FILE.parent.mkdir(parents=True, exist_ok=True)
        BIDNET_COOLDOWN_FILE.write_text(until)
    except OSError:
        pass
    return until


def login(page, user: str, pw: str) -> None:
    if _marker_expired():
        CODE_NEEDED_MARKER.unlink(missing_ok=True)  # stale: allow one fresh attempt (at most one code email per 6 h)
    if CODE_NEEDED_MARKER.exists():
        raise LoginBlocked("waiting for the emailed confirmation code since "
                           f"{CODE_NEEDED_MARKER.read_text().strip() or '?'}: no new login attempted (each one emails a new "
                           "code). When ready to supply the code within the wait window, delete ~/.brownbison/bidnet_code_needed")
    clear_code()  # any code on disk predates this login and is therefore dead
    page.goto(_home(), wait_until="domcontentloaded")
    page.wait_for_timeout(1000)
    html = _content(page)
    if BOT_RX.search(html) and not total_count(html):
        raise RuntimeError("BidNet robot check served on the login page; try again later")
    if _page_logged_in(page):
        return  # single sign-on already restored the session (IdP session still alive): nothing to type
    started = dt.datetime.now(dt.timezone.utc)  # only a code emailed after this moment belongs to this login
    _submit_login_window(page, user, pw)
    html = _settle_after_submit(page)
    if BOT_RX.search(html) and not total_count(html):
        raise LoginBlocked("BidNet robot check right after the login form; try again later")
    if CODE_PROMPT_RX.search(visible_text(html)):
        code = wait_for_code(float(os.environ.get("BIDNET_CODE_WAIT", "300")), since=started)
        if not code:
            try:
                CODE_NEEDED_MARKER.parent.mkdir(parents=True, exist_ok=True)
                CODE_NEEDED_MARKER.write_text(iso())
            except OSError:
                pass  # still BLOCKED below; never let a filesystem hiccup turn into a retried login
            raise LoginBlocked("BidNet asked for an emailed confirmation code (new device) and none was supplied in "
                               f"{os.environ.get('BIDNET_CODE_WAIT', '300')} s. No further logins until "
                               "~/.brownbison/bidnet_code_needed is deleted; then supply the code from the next "
                               "'Your BidNet Direct confirmation code' email with scripts/bidwatch/set_code.py while the "
                               "scanner waits on the prompt")
        _fill_first(page, CODE_INPUT_SEL, code)
        _click_first(page, CODE_BTN_SEL)
        html = _settle_after_submit(page, code_prompt_is_final=False)
        clear_code()
        if CODE_PROMPT_RX.search(visible_text(html)):
            raise LoginBlocked("BidNet rejected the confirmation code (expired or mistyped); get a fresh one")


def _settle_after_submit(page, timeout_s: float = 25.0, code_prompt_is_final: bool = True) -> str:
    """After the login (or code) POST, BidNet hops www -> idp -> SAML post back -> www: several navigations,
    some started by script after a page has loaded. A fixed 3 s wait read the page mid-hop (2026-10-20 05:16,
    endurance E3 check 4: attempt 1 failed although its saved page was already logged in). Wait for a final
    state instead: logged in, the code prompt (when it counts as final), or a robot check. At the deadline,
    return whatever is there and let the caller decide."""
    deadline = time.time() + timeout_s
    html = ""
    while True:
        try:
            page.wait_for_load_state("load", timeout=5000)
            html = page.content()
        except Exception:  # noqa: BLE001 - still navigating; look again
            html = ""
        if html:
            if _page_logged_in(page):
                return html
            if code_prompt_is_final and CODE_PROMPT_RX.search(visible_text(html)):
                return html
            if BOT_RX.search(html) and not total_count(html):
                return html
        if time.time() >= deadline:
            return html
        page.wait_for_timeout(1000)


LOGIN_TOGGLE_SEL = ["#header_btnLogin", "#loginLinkCustom", "button.loginButton", "a[href='/public/authentication/login']"]


def _submit_login_window(page, user: str, pw: str) -> None:
    """The login window (div#loginWindow) is collapsed until the header Login button opens it (seen
    2026-10-20: filling the hidden fields timed out and nothing was submitted). Open it and fill; if the
    fields still are not visible, set the values and submit the form from JavaScript (same POST, same _csrf)."""
    for sel in LOGIN_TOGGLE_SEL:
        try:
            if page.locator(sel).count():
                page.click(sel, timeout=5000)
                page.wait_for_timeout(1200)
                break
        except Exception:  # noqa: BLE001
            continue
    try:
        page.wait_for_selector("#loginBox_j_username, input[name='j_username']", state="visible", timeout=5000)
        _fill_first(page, LOGIN_USER_SEL, user)
        _fill_first(page, LOGIN_PASS_SEL, pw)
        _click_first(page, LOGIN_BTN_SEL)
        return
    except Exception:  # noqa: BLE001 - fall back to a scripted submit of the same form
        pass
    page.evaluate(
        """([u, p]) => {
            const f = document.getElementById('loginWindowForm') || document.querySelector("form[action*='authentication/login']");
            if (!f) throw new Error('login form not found');
            const uf = f.querySelector("input[name='j_username']"), pf = f.querySelector("input[name='j_password']");
            if (!uf || !pf) throw new Error('login fields not found');
            uf.value = u; pf.value = p;
            if (typeof f.requestSubmit === 'function') f.requestSubmit(); else f.submit();
        }""", [user, pw])


def visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    return " ".join(soup.get_text(" ").split())


def wait_for_code(timeout: float, since: dt.datetime | None = None) -> str | None:
    """Poll for a code while the browser sits on the prompt (the code is only valid in this session).
    Sources, in order: BIDNET_CODE env, ~/.brownbison/bidnet_code (set_code.py), and the inbox over IMAP
    (mailcode.py, when BIDNET_CODE_IMAP_PASS is set) for a code emailed after `since`."""
    deadline = time.time() + max(0.0, timeout)
    since = since or dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=2)
    next_mail_check = 0.0
    while True:
        code = read_code()
        if not code and mailcode.configured() and time.time() >= next_mail_check:
            next_mail_check = time.time() + 10
            try:
                code = mailcode.fetch_code(since)
            except Exception:  # noqa: BLE001 - a mailbox hiccup must not abandon the login window
                code = None
        if code or time.time() >= deadline:
            return code
        time.sleep(2)


def read_code() -> str | None:
    code = os.environ.get("BIDNET_CODE", "").strip()
    if not code and CODE_FILE.exists():
        code = CODE_FILE.read_text().strip()
    return re.sub(r"\s+", "", code) or None


def clear_code() -> None:
    os.environ.pop("BIDNET_CODE", None)
    try:
        CODE_FILE.unlink()
    except FileNotFoundError:
        pass


def is_logged_in(page) -> bool:
    """Logged in = a normal BidNet page showing the logout link and no login window. (Text like 'my account'
    is useless: the logged-out page has aria-label="my account" on the mobile avatar button; the URL is
    useless after an SSO redirect.)"""
    page.goto(_home(), wait_until="domcontentloaded")
    page.wait_for_timeout(1500)
    html = _content(page)
    if BOT_RX.search(html) and not total_count(html):
        return False
    if "bidnet" not in (page.title() or "").lower():
        return False  # not a BidNet page at all (blank, error, proxy page)
    return _page_logged_in(page)


def _fill_first(page, sels, value):
    for s in sels:
        if page.locator(s).count():
            page.fill(s, value, timeout=8000)
            return
    raise RuntimeError(f"no field matched {sels[0]}…")


def _click_first(page, sels):
    for s in sels:
        if page.locator(s).count():
            page.click(s, timeout=8000)
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
        # public rows link /solicitations/.../<id>; LOGGED-IN aggregate rows link
        # /private/supplier/interception/open-notice/<id>?target=view (same id, also on a@id), seen 2026-10-20
        m = (SOL_HREF.search(a["href"]) or OPEN_NOTICE_HREF.search(a["href"])) if a else None
        sid = m.group(1) if m else ((a.get("id") or "") if a is not None and (a.get("id") or "").isdigit() else "")
        if not sid or sid in seen:
            continue
        seen.add(sid)
        region = _txt(tr.select_one(".sol-region-item"))
        # keyword-search pages wrap hits in <span class="iris-highlight">; joining with " " would turn
        # "On-<span>Call</span>" into "On - Call", so join without a separator
        title = " ".join(a.get_text().split())
        rows.append({"id": sid, "title": title, "url": urljoin(base_url, a["href"]),
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
    r"Title|Source ID|Reference Number|Purchase Type|Piggyback Contract|Details|" \
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


def _content(page, tries: int = 4) -> str:
    """page.content() fails with 'page is navigating' when BidNet's scripts reload the page right after
    load (seen 2026-10-20 03:01 on the statewide list). Wait for the navigation to settle and retry."""
    last: Exception | None = None
    for i in range(tries):
        try:
            page.wait_for_load_state("load", timeout=20000)
            return page.content()
        except Exception as e:  # noqa: BLE001
            last = e
            page.wait_for_timeout(1500 * (i + 1))
    assert last is not None
    raise last


def _walk(session, name: str, start: str, out: dict, errors: list, totals: dict, max_pages: int) -> None:
    page, url, n = session.page, start, 0
    while url and n < max_pages:
        n += 1
        try:
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(800)
            html = _content(page)
            rows, nxt = parse_listing(html, url)
        except Exception as e:  # noqa: BLE001
            errors.append(f"BidNet list {url}: {type(e).__name__}: {str(e)[:150]}")
            totals.setdefault(name, None)  # this list did not finish: the scan is incomplete
            totals.setdefault("_failed", []).append(name)
            return
        if not rows and BOT_RX.search(html) and not total_count(html):
            totals["_bot_check"] = True
            totals["_cooldown_until"] = start_cooldown()
            session.debug_dump("bot-check")
            errors.append(f"BidNet robot check (rate limit) on {url}: scan stopped; previous BidNet results kept")
            return
        if n == 1:
            totals[name] = total_count(html)
            if not rows and totals[name] != 0:  # not a list page at all (error page, redirect, WAF interstitial)
                session.debug_dump("empty-list")
                errors.append(f"BidNet list parsed 0 rows: {url} (debug HTML saved)")
                totals.setdefault("_failed", []).append(name)
                return
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
        if not totals.get("_bot_check"):
            _walk(session, f"statewide {t}", f"{CO_OPEN}?{urlencode({'selectedContent': t})}", out, errors, totals, max_pages)
    statewide = {k: v for k, v in totals.items() if k.startswith("statewide")}
    expected = sum(v for v in statewide.values() if v)
    # complete only when EVERY statewide tab reported its total and we read at least that many rows;
    # a tab that errored out (total None) means the previous results must be carried forward
    totals["_complete"] = (len(statewide) == len(CO_TABS) and all(v is not None for v in statewide.values())
                           and bool(expected) and len(out) >= expected and not totals.get("_bot_check"))
    if totals.get("_bot_check"):
        return out, errors, totals
    if force_keywords or not expected or len(out) < expected:
        if not force_keywords:
            errors.append(f"BidNet statewide list short ({len(out)} of {expected or '?'}); ran keyword searches")
        for k in keywords:
            if totals.get("_bot_check"):
                break
            _walk(session, f"kw {k}", f"{CO_OPEN}?{urlencode({'keywords': k})}", out, errors, totals, max_pages)
    return out, errors, totals


DOCS_TAB_SEL = "a[href*='innerTabId=docs-items']"
ATTACH_SEL = "a[id^='attachmentDownloadLnk_']"


def parse_docs_tab(html: str, url: str = "") -> dict:
    """The logged-in 'Documents & Items' tab (verified 2026-10-20 on Littleton 0000438328): one
    a#attachmentDownloadLnk_<id> per file, href .../abstract/docs-items/<id>/attachment-download, and an Items
    list (the RMEPS pricing lines bidders fill in). Loaded by XHR only after the tab is clicked."""
    soup = BeautifulSoup(html, "lxml")
    docs = [{"name": _txt(a), "url": urljoin(url or BASE, a["href"])} for a in soup.select(ATTACH_SEL + "[href]")]
    text = " ".join(soup.get_text(" ").split())
    i = text.find("Items No Description")
    items = None
    if i >= 0:
        j = min(k for k in (text.find("There are no items", i), text.find("Print Options", i), len(text)) if k > i)
        items = text[i:j].strip()[:3000]
    return {"documents": docs, "items_text": items}


def enrich(session, bid: dict) -> dict:
    """Detail page. Public visitors see only location + publication/closing date (and closing time);
    issuing org, solicitation #, description, documents and buyer contact are 'Registered members only'.
    Logged in, the documents live on the 'Documents & Items' tab, which loads only when clicked."""
    page = session.page
    page.goto(bid["url"], wait_until="domcontentloaded")
    page.wait_for_timeout(1200)
    d = parse_detail(_content(page), bid["url"])
    if d.get("login_required_for_docs") and not session.logged_in:
        d["prebid"] = None  # the description is locked, so any 'pre-bid' hit came from page chrome
    if session.logged_in:
        try:
            if page.locator(DOCS_TAB_SEL).count():
                page.locator(DOCS_TAB_SEL).first.click()
                try:  # attachments arrive by XHR; a bid with no files never shows one, so time out quietly
                    page.wait_for_selector(ATTACH_SEL, timeout=15000)
                except Exception:  # noqa: BLE001
                    pass
                page.wait_for_timeout(800)
                t = parse_docs_tab(_content(page), bid["url"])
                if t["documents"]:
                    d["documents"] = t["documents"]
                if t["items_text"]:
                    d["items_text"] = t["items_text"]
        except Exception:  # noqa: BLE001 - keep the main-tab facts even if the docs tab misbehaves
            session.debug_dump("docs-tab")
    return {**bid, **{k: v for k, v in d.items() if v not in (None, [])}, "detail_checked": True}


def download_docs(session, bid: dict, skip_existing: bool = True) -> list[str]:
    """Logged-in only. Saves each document not already on disk; returns the paths saved this call. Checking the
    disk (not the previous scan's document list) also fetches the files of a bid that became watched after its
    documents were first listed, and any addendum."""
    saved = []
    dest = DOWNLOAD_DIR / "bidnet" / bid["id"]
    dest.mkdir(parents=True, exist_ok=True)
    for d in bid.get("documents", [])[:60]:
        safe = re.sub(r"[^\w.\- ]", "_", d.get("name") or "").strip()
        if skip_existing and safe and (dest / safe).is_file() and (dest / safe).stat().st_size > 0:
            continue
        try:
            with session.page.expect_download(timeout=45000) as dl:
                try:
                    session.page.goto(d["url"])
                except Exception:  # noqa: BLE001 - Chromium aborts navigation when a download starts
                    pass
            f = dl.value
            target = dest / (safe or f.suggested_filename)
            f.save_as(target)
            saved.append(str(target))
            continue
        except Exception:  # noqa: BLE001 - fall back to a plain GET with the same logged-in cookies
            pass
        try:
            r = session.ctx.request.get(d["url"], timeout=60000)
            body = r.body()
            ctype = (r.headers.get("content-type") or "").lower()
            if r.ok and body and "text/html" not in ctype:
                target = dest / (safe or d["url"].rstrip("/").rsplit("/", 1)[-1])
                target.write_bytes(body)
                saved.append(str(target))
        except Exception:  # noqa: BLE001
            continue
    return saved
