#!/usr/bin/env python3
"""BidNet Direct / Rocky Mountain E-Purchasing watcher for Brown Bison.

What it does
  1. Loads each agency page in AGENCIES (public, no login) and extracts the open solicitations
     (title, closing date, URL). Public pages list titles/dates; documents need a login.
  2. Keyword-filters them (HVAC, mechanical, landscaping, ...) and diffs against the last run
     (bids/_watch/bidnet_state.json) -> NEW / CHANGED / CLOSED.
  3. If BIDNET_USER and BIDNET_PASS are set in the environment, logs in and downloads the document
     list + files for every matching solicitation into bids/_watch/downloads/<agency>/<slug>/.
  4. Writes a Markdown report section to stdout; scan_bids.py assembles the full REPORT.md.

Needs: network access to www.bidnetdirect.com (blocked in the cloud env until allowlisted) and
Playwright with Chromium (pre-installed at /opt/pw-browsers in cloud sessions).

Caveats, read these:
  - BidNet's terms restrict automated access. Public-page polling at a gentle cadence (hourly or
    less) is low-risk; logged-in document scraping is a judgment call Luke makes. Keep cadence low.
  - Page structure is inferred, not confirmed (site is blocked from the build environment). The
    extractor is deliberately generic (any link under /solicitations/ plus nearby date text) and
    saves raw HTML to the state dir when it finds nothing, so it can be fixed from a real sample.
  - Never commit credentials. They come from env vars only.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

REPO = Path(__file__).resolve().parents[1]
STATE_DIR = REPO / "bids" / "_watch"
STATE_FILE = STATE_DIR / "bidnet_state.json"
DOWNLOAD_DIR = STATE_DIR / "downloads"

AGENCIES = {
    "Town of Parker": "https://www.bidnetdirect.com/colorado/town-of-parker",
    "Douglas County School District RE-1": "https://www.bidnetdirect.com/colorado/douglas-county-school-district-re-1",
    "Town of Estes Park": "https://www.bidnetdirect.com/colorado/town-of-estes-park",
    "Douglas County": "https://www.bidnetdirect.com/colorado/douglas-county",
    "Town of Castle Rock": "https://www.bidnetdirect.com/colorado/town-of-castle-rock",
    "City of Lone Tree": "https://www.bidnetdirect.com/colorado/city-of-lone-tree",
}

PROFILES_FILE = STATE_DIR / "watch_profiles.json"


def load_keyword_profiles() -> dict[str, list[re.Pattern]]:
    cfg = json.loads(PROFILES_FILE.read_text())
    return {
        name: [re.compile(r"\b" + re.escape(k.lower())) for k in prof.get("bidnet_keywords", [])]
        for name, prof in cfg["profiles"].items()
    }


KEYWORD_PROFILES = load_keyword_profiles()

LOGIN_URL = "https://www.bidnetdirect.com/public/authentication/login"
DATE_RX = re.compile(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b")


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:80]


def keyword_profiles_hit(title: str) -> list[str]:
    """Word-start matching ("trees" does not match "Street"). Returns the profile names that match."""
    t = title.lower()
    return [name for name, rxs in KEYWORD_PROFILES.items() if any(rx.search(t) for rx in rxs)]


def keyword_hit(title: str) -> bool:
    return bool(keyword_profiles_hit(title))


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"solicitations": {}, "last_run": None}


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))


def extract_solicitations(page, base_url: str) -> list[dict]:
    """Generic extraction: every link whose href contains /solicitations/ is a candidate.
    Closing date = first mm/dd/yyyy found in the link's row/container text."""
    rows = page.evaluate(
        """() => {
          const out = [];
          const seen = new Set();
          for (const a of document.querySelectorAll('a[href*="/solicitations/"]')) {
            const href = a.getAttribute('href') || '';
            const title = (a.textContent || '').trim().replace(/\\s+/g, ' ');
            if (!title || title.length < 6) continue;
            if (/awarded-bids|closed-bids|open-bids$/.test(href)) continue;
            if (seen.has(href)) continue;
            seen.add(href);
            let node = a; let ctx = '';
            for (let i = 0; i < 5 && node; i++) {
              ctx = (node.textContent || '').replace(/\\s+/g, ' ');
              if (/\\d{1,2}\\/\\d{1,2}\\/\\d{2,4}/.test(ctx)) break;
              node = node.parentElement;
            }
            out.push({href, title, ctx});
          }
          return out;
        }"""
    )
    result = []
    for r in rows:
        dates = DATE_RX.findall(r["ctx"])
        result.append({
            "title": r["title"],
            "url": urljoin(base_url, r["href"]),
            "closing": dates[-1] if dates else None,
            "context": r["ctx"][:300],
        })
    return result


def login(page) -> bool:
    user, pw = os.environ.get("BIDNET_USER"), os.environ.get("BIDNET_PASS")
    if not (user and pw):
        return False
    page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
    # Field names are inferred; adjust from a real page if login fails.
    for sel in ["input[name='j_username']", "input[name='username']", "input[type='email']", "#username"]:
        if page.locator(sel).count():
            page.fill(sel, user)
            break
    for sel in ["input[name='j_password']", "input[name='password']", "input[type='password']", "#password"]:
        if page.locator(sel).count():
            page.fill(sel, pw)
            break
    for sel in ["button[type='submit']", "input[type='submit']", "button:has-text('Log in')", "button:has-text('Login')"]:
        if page.locator(sel).count():
            page.click(sel)
            break
    page.wait_for_load_state("networkidle", timeout=60000)
    return "login" not in page.url.lower()


def download_documents(page, sol: dict, agency: str) -> list[str]:
    """Best-effort: open the solicitation page, click into documents, save every file link."""
    saved = []
    dest = DOWNLOAD_DIR / slug(agency) / slug(sol["title"])
    dest.mkdir(parents=True, exist_ok=True)
    page.goto(sol["url"], wait_until="domcontentloaded", timeout=60000)
    links = page.evaluate(
        """() => Array.from(document.querySelectorAll('a[href]'))
              .map(a => ({href: a.href, text: (a.textContent||'').trim()}))
              .filter(x => /\\.(pdf|docx?|xlsx?|zip)(\\?|$)/i.test(x.href) || /download|document|attachment/i.test(x.text))"""
    )
    for l in links[:40]:
        try:
            with page.expect_download(timeout=30000) as dl:
                page.goto(l["href"])
            d = dl.value
            target = dest / d.suggested_filename
            d.save_as(target)
            saved.append(str(target.relative_to(REPO)))
        except Exception:  # noqa: BLE001
            continue
    return saved


def chromium_path() -> str | None:
    """Use a pre-installed Chromium when the pip Playwright build does not match (cloud sessions
    ship /opt/pw-browsers/chromium). Override with BROWNBISON_CHROMIUM."""
    for cand in [os.environ.get("BROWNBISON_CHROMIUM"), "/opt/pw-browsers/chromium"]:
        if cand and Path(cand).exists():
            return str(Path(cand).resolve())
    return None


def run(fixture: str | None = None) -> dict:
    from playwright.sync_api import sync_playwright

    state = load_state()
    prev = state["solicitations"]
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    found: dict[str, dict] = {}
    errors: list[str] = []
    downloaded: dict[str, list[str]] = {}

    agencies = AGENCIES if not fixture else {"FIXTURE": fixture}

    with sync_playwright() as p:
        exe = chromium_path()
        browser = p.chromium.launch(headless=True, executable_path=exe) if exe else p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent="BrownBison-BidWatch/1.0 (+luke@brownbisonco.com)")
        page = ctx.new_page()
        logged_in = False
        if not fixture:
            try:
                logged_in = login(page)
            except Exception as e:  # noqa: BLE001
                errors.append(f"login failed: {e}")

        for agency, url in agencies.items():
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(1500)
                sols = extract_solicitations(page, url)
                if not sols:
                    STATE_DIR.mkdir(parents=True, exist_ok=True)
                    (STATE_DIR / f"raw-{slug(agency)}.html").write_text(page.content())
                    errors.append(f"{agency}: 0 solicitations parsed; raw HTML saved for selector fixes")
                for s in sols:
                    key = s["url"]
                    profiles = keyword_profiles_hit(s["title"])
                    found[key] = {**s, "agency": agency, "match": bool(profiles), "profiles": profiles, "seen": now}
            except Exception as e:  # noqa: BLE001
                errors.append(f"{agency}: {type(e).__name__}: {str(e)[:200]}")

        if logged_in:
            for key, s in found.items():
                if s["match"] and key not in prev:
                    try:
                        downloaded[key] = download_documents(page, s, s["agency"])
                    except Exception as e:  # noqa: BLE001
                        errors.append(f"download {s['title']}: {e}")
        browser.close()

    new = {k: v for k, v in found.items() if k not in prev}
    changed = {k: v for k, v in found.items() if k in prev and prev[k].get("closing") != v.get("closing")}
    closed = {k: v for k, v in prev.items() if k not in found and not errors}

    merged = {**prev, **found}
    for k in closed:
        merged[k] = {**merged[k], "closed_seen": now}
    state["solicitations"] = merged
    state["last_run"] = now
    save_state(state)

    return {"now": now, "new": new, "changed": changed, "closed": closed, "all": found,
            "errors": errors, "downloaded": downloaded, "logged_in": logged_in}


def render(r: dict) -> str:
    out = [f"## BidNet Direct — {r['now']}"]
    out.append(f"Login: {'yes' if r['logged_in'] else 'no (public pages only)'}")
    if r["errors"]:
        out.append("\n**Errors**")
        out += [f"- {e}" for e in r["errors"]]

    def table(title, items):
        if not items:
            return
        out.append(f"\n**{title}**\n")
        out.append("| Match (profile) | Agency | Title | Closing | Link |")
        out.append("|---|---|---|---|---|")
        for v in sorted(items.values(), key=lambda x: (not x.get("match"), x.get("agency", ""))):
            out.append(f"| {','.join(v.get('profiles', [])) if v.get('match') else ''} | {v.get('agency','')} | {v['title']} | {v.get('closing') or ''} | {v['url']} |")

    table("NEW since last run", r["new"])
    table("CHANGED closing date", r["changed"])
    table("No longer listed (closed/awarded?)", r["closed"])
    if r["downloaded"]:
        out.append("\n**Documents downloaded**")
        for k, files in r["downloaded"].items():
            out += [f"- {f}" for f in files]
    matches = {k: v for k, v in r["all"].items() if v.get("match")}
    out.append(f"\nOpen keyword matches across watched agencies: {len(matches)} of {len(r['all'])} listed.")
    return "\n".join(out)


if __name__ == "__main__":
    fixture = sys.argv[1] if len(sys.argv) > 1 else None
    print(render(run(fixture)))
