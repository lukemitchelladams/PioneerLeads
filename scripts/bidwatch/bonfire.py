"""Euna Procurement (formerly Bonfire) portals: Town of Parker and any other agency on <org>.bonfirehub.com.

Public: the open-opportunities list and each opportunity page (title, reference #, close date,
the "Events" table with question deadlines and any pre-bid / site visit) need no login.
Logged in (BONFIRE_USER / BONFIRE_PASS, the Euna vendor account): document downloads.

Orgs come from watch_profiles.json -> "bonfire_orgs" (default ["parkeronline"]).
List endpoint: Bonfire's portal page loads JSON from /PublicPortal/getOpenPublicOpportunitiesSectionData;
we read that JSON when present and fall back to scraping links to /opportunities/<id>.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

from .common import extract_prebid, parse_date

CREDS = ("BONFIRE_USER", "BONFIRE_PASS")
MT = ZoneInfo("America/Denver")
# Opportunity pages (/opportunities/<id>) sit behind a Cloudflare bot challenge for cloud/datacenter IPs
# (seen 2026-10-20: HTTP 403, cf-mitigated: challenge, title "Just a moment..."). The list JSON is not.
CHALLENGE_RX = re.compile(r"<title>\s*Just a moment|cf-challenge|challenge-platform|Performing security verification", re.I)


class Challenged(RuntimeError):
    pass


def utc_to_mt(s: str) -> tuple[str | None, str | None]:
    """Bonfire's DateClose is UTC ('2026-10-22 21:00:00'). Return (yyyy-mm-dd, 'yyyy-mm-dd HH:MM MT')."""
    try:
        t = dt.datetime.strptime(s.strip()[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc).astimezone(MT)
        return t.date().isoformat(), t.strftime("%Y-%m-%d %H:%M ") + (t.tzname() or "MT")
    except (ValueError, AttributeError):
        return parse_date(s or ""), None
OPP_HREF = re.compile(r"/opportunities/(\d+)")


ORG_NAMES = {"parkeronline": "Town of Parker"}


def base(org: str) -> str:
    return f"https://{org}.bonfirehub.com"


def login(page, user: str, pw: str, org: str = "parkeronline") -> None:
    page.goto(base(org) + "/login", wait_until="domcontentloaded")
    for s in ["input[type='email']", "input[name='email']", "#input-email"]:
        if page.locator(s).count():
            page.fill(s, user)
            break
    for s in ["button:has-text('Continue')", "button:has-text('Next')"]:  # some tenants split email/password
        if page.locator(s).count():
            page.click(s)
            page.wait_for_timeout(1500)
            break
    for s in ["input[type='password']", "input[name='password']"]:
        if page.locator(s).count():
            page.fill(s, pw)
            break
    for s in ["button[type='submit']", "button:has-text('Log In')", "button:has-text('Login')", "button:has-text('Sign In')"]:
        if page.locator(s).count():
            page.click(s)
            break
    page.wait_for_timeout(4000)


def is_logged_in(page, org: str = "parkeronline") -> bool:
    page.goto(base(org) + "/portal/?tab=openOpportunities", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    return bool(re.search(r"log ?out|sign ?out|my submissions", page.content(), re.I))


def parse_list_json(payload: dict, org: str) -> list[dict]:
    """Walk Bonfire's JSON for project objects (keys like ProjectID / ProjectName / DateClose)."""
    rows = []

    def walk(o):
        if isinstance(o, dict):
            pid = o.get("ProjectID") or o.get("projectID") or o.get("id")
            name = o.get("ProjectName") or o.get("projectName") or o.get("name")
            if pid and name and any(k in o for k in ("DateClose", "dateClose", "ReferenceID", "referenceID")):
                closing, closing_text = utc_to_mt(str(o.get("DateClose") or o.get("dateClose") or ""))
                rows.append({
                    "source": "bonfire", "org": org, "id": f"{org}-{pid}", "title": str(name).strip(),
                    "sol": o.get("ReferenceID") or o.get("referenceID"),
                    "closing": closing, "closing_text": closing_text,
                    "url": f"{base(org)}/opportunities/{pid}", "agency": ORG_NAMES.get(org, org),
                })
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(payload)
    depts = (payload.get("payload") or {}).get("departments") or {} if isinstance(payload, dict) else {}
    projects = (payload.get("payload") or {}).get("projects") or {} if isinstance(payload, dict) else {}
    for r in rows:
        p = projects.get(r["id"].split("-")[-1]) or {}
        r["department"] = (depts.get(str(p.get("DepartmentID"))) or {}).get("DepartmentName")
    return rows


def parse_list_html(html: str, org: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    rows, seen = [], set()
    for a in soup.find_all("a", href=True):
        m = OPP_HREF.search(a["href"])
        if not m or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        tr = a.find_parent("tr") or a.parent
        ctx = " ".join(tr.get_text(" ").split()) if tr else ""
        title = " ".join(a.get_text(" ").split()) or ctx[:120]
        rows.append({"source": "bonfire", "org": org, "id": f"{org}-{m.group(1)}", "title": title,
                     "closing": parse_date(ctx), "url": urljoin(base(org), a["href"]), "agency": org,
                     "context": ctx[:300]})
    return rows


def parse_detail(html: str) -> dict:
    if CHALLENGE_RX.search(html[:20000]):
        raise Challenged("Cloudflare bot challenge on the opportunity page; detail not readable from this network")
    soup = BeautifulSoup(html, "lxml")
    text = " ".join(soup.get_text(" ").split())
    events = []
    for tr in soup.find_all("tr"):
        cells = [" ".join(td.get_text(" ").split()) for td in tr.find_all(["td", "th"])]
        if len(cells) >= 2 and parse_date(" ".join(cells[1:])):
            events.append({"event": cells[0], "when": " ".join(cells[1:])[:120]})
    close = None
    m = re.search(r"Close Date\s*(.{0,40})", text)
    if m:
        close = parse_date(m.group(1))
    q = re.search(r"Questions? Due Date\s*(.{0,40})", text)
    return {
        "closing": close, "questions_due": parse_date(q.group(1)) if q else None,
        "events": events, "prebid": extract_prebid(" ".join(e["event"] + " " + e["when"] for e in events) or text),
        "sol": (re.search(r"Ref\.?\s*#\s*([A-Za-z0-9\-]+)", text) or [None, None])[1],
    }


def collect_open(session, org: str) -> tuple[dict, list[str]]:
    page, errors, rows = session.page, [], []
    captured = {}

    def on_response(resp):
        if "getOpenPublicOpportunitiesSectionData" in resp.url:
            try:
                captured["json"] = resp.json()
            except Exception:  # noqa: BLE001
                pass

    page.on("response", on_response)
    try:
        page.goto(base(org) + "/portal/?tab=openOpportunities", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        if "json" in captured:
            rows = parse_list_json(captured["json"], org)
        if not rows:
            try:
                resp = page.request.get(base(org) + "/PublicPortal/getOpenPublicOpportunitiesSectionData",
                                        headers={"X-Requested-With": "XMLHttpRequest"})
                rows = parse_list_json(json.loads(resp.text()), org)
            except Exception:  # noqa: BLE001
                pass
        if not rows:
            rows = parse_list_html(page.content(), org)
        if not rows:
            session.debug_dump(f"{org}-empty-list")
            errors.append(f"Bonfire {org}: 0 opportunities parsed (debug HTML saved)")
    except Exception as e:  # noqa: BLE001
        errors.append(f"Bonfire {org}: {type(e).__name__}: {str(e)[:150]}")
    finally:
        page.remove_listener("response", on_response)
    return {r["id"]: r for r in rows}, errors


def enrich(session, bid: dict) -> dict:
    session.page.goto(bid["url"], wait_until="domcontentloaded")
    session.page.wait_for_timeout(2500)
    d = parse_detail(session.page.content())
    return {**bid, **{k: v for k, v in d.items() if v not in (None, [])}, "detail_checked": True}
