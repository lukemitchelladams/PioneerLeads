#!/usr/bin/env python3
"""DLA DIBBS watcher: open RFQs by Federal Supply Class for the Jones Bearing profile.

DIBBS (https://www.dibbs.bsm.dla.mil) posts most DLA parts buys: mounted bearings, pulleys, conveyors,
material-handling gear. Viewing is public behind a DoD consent banner; quoting needs a CAGE + account.

For each FSC in watch_profiles.json -> profiles.jones-bearing.samgov ccode entries, this loads the RFQ
list page, extracts solicitation number, NSN, nomenclature, quantity, return-by date and link, keyword-
filters on the profile's bidnet_keywords, and diffs against bids/_watch/dibbs_state.json.

Verified against the live site 2026-10-20. The RFQ list (RfqRecs.aspx?category=fsc&Value=<fsc>) is an
ASP.NET GridView (id ctl00_cph1_grdRfqSearch) behind a DoD consent page (#butAgree). Each row has spans
ending _lblNsn, _lblNomenclature, _lblSolicitation (link to the RFQ PDF), _lblStatus, _lblPr ("<PR> QTY: n"),
_lblIssued, _lblReturnBy (mm-dd-yyyy). The list includes awarded/cancelled history (FSC 3110: ~2,700 rows)
and the "Open" status lingers past the return date, so we sort by Return By descending (two postbacks on
Sort$SORT_CLOSE_DTE) and page (Page$n postbacks) until rows fall before today.
Needs Playwright + Chromium (local: `pip install playwright && playwright install chromium`).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE_DIR = REPO / "bids" / "_watch"
STATE_FILE = STATE_DIR / "dibbs_state.json"
PROFILES_FILE = STATE_DIR / "watch_profiles.json"
PROFILE = "jones-bearing"

BASE = "https://www.dibbs.bsm.dla.mil"
# RFQ list by FSC. Parameter names inferred from DIBBS URL patterns; fix from a real session if needed.
FSC_URL = BASE + "/RFQ/RfqRecs.aspx?category=fsc&TypeSrch=cq&Value={fsc}"

GRID = "ctl00$cph1$grdRfqSearch"
MAX_PAGES = 40  # 25 rows each; open RFQs per FSC are usually well under 1,000
# DLA solicitation numbers: 6-char activity code + FY + type + serial, e.g. SPE4A0-26-T-2395, SPE7M1-26-U-1234
SOL_RX = re.compile(r"\b[A-Z][A-Z0-9]{5}-?\d{2}-?[A-Z]-?[A-Z0-9]{4}\b")
NSN_RX = re.compile(r"\b\d{4}-\d{2}-\d{3}-\d{4}\b")
DATE_RX = re.compile(r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b")


def chromium_path() -> str | None:
    for cand in [os.environ.get("BROWNBISON_CHROMIUM"), "/opt/pw-browsers/chromium"]:
        if cand and Path(cand).exists():
            return str(Path(cand).resolve())
    return None


def load_profile() -> tuple[list[str], list[re.Pattern]]:
    cfg = json.loads(PROFILES_FILE.read_text())["profiles"][PROFILE]
    fscs = [q["ccode"] for q in cfg["samgov"] if "ccode" in q]
    kws = [re.compile(r"\b" + re.escape(k.lower())) for k in cfg.get("bidnet_keywords", [])]
    return fscs, kws


def accept_banner(page) -> None:
    for sel in ["#butAgree", "input[name='butAgree']", "input[value='OK']", "button:has-text('OK')"]:
        try:
            if page.locator(sel).count():
                page.click(sel, timeout=10000)
                page.wait_for_load_state("domcontentloaded", timeout=30000)
                return
        except Exception:  # noqa: BLE001
            continue


def iso_date(s: str | None) -> str | None:
    m = DATE_RX.search(s or "")
    if not m:
        return None
    try:
        return dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2))).isoformat()
    except ValueError:
        return None


def parse_rows(html: str) -> list[dict]:
    """Rows of the DIBBS RFQ GridView. Pure function (tested against tests/fixtures/dibbs_rfq_3110.html)."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")

    def cell(tr, suffix):
        el = tr.find("span", id=re.compile(suffix + "$"))
        return (" ".join(el.get_text(" ").split()), el) if el else ("", None)

    out = []
    for tr in soup.find_all("tr"):
        if tr.find("tr"):  # outer layout rows contain the whole grid; only leaf rows are records
            continue
        sol_txt, sol_el = cell(tr, "_lblSolicitation")
        m = SOL_RX.search(sol_txt)
        if not m:
            continue
        nsn, _ = cell(tr, "_lblNsn")
        nomen, _ = cell(tr, "_lblNomenclature")
        status, _ = cell(tr, "_lblStatus")
        pr, _ = cell(tr, "_lblPr")
        issued, _ = cell(tr, "_lblIssued")
        ret, _ = cell(tr, "_lblReturnBy")
        links = {a.get("title", ""): a["href"] for a in sol_el.find_all("a", href=True)}
        qty = re.search(r"QTY:\s*([\d,]+)", pr)
        out.append({
            "sol": m.group(0), "nsn": (NSN_RX.search(nsn) or [None])[0] if NSN_RX.search(nsn) else nsn or None,
            "nomenclature": nomen, "status": status.replace(" uote", "").replace("Quote", "").strip(),
            "pr": pr.split(" ")[0] if pr else None, "qty": int(qty.group(1).replace(",", "")) if qty else None,
            "issued": iso_date(issued), "return_by": iso_date(ret),
            "pdf": links.get("RFQ document"), "url": links.get("Package View") or links.get("RFQ document"),
            "text": f"{nsn} {nomen} {sol_txt} {status} {pr} {issued} {ret}"[:400],
        })
    return out


def records_found(html: str) -> int | None:
    m = re.search(r"Records Found:\s*(?:<[^>]+>\s*)*([\d,]+)", html)
    return int(m.group(1).replace(",", "")) if m else None


def _postback(page, arg: str) -> None:
    with page.expect_navigation(wait_until="domcontentloaded", timeout=60000):
        page.evaluate(f"__doPostBack('{GRID}', '{arg}')")


def collect_fsc(page, url: str, today: str) -> tuple[list[dict], int | None]:
    """Open RFQs (return-by >= today) for one FSC list URL."""
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    accept_banner(page)
    if "rfqrecs" not in page.url.lower() or "value=" not in page.url.lower():
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
    total = records_found(page.content())
    if not total:
        return parse_rows(page.content()), total
    for _ in range(2):  # first click = ascending, second = descending
        _postback(page, "Sort$SORT_CLOSE_DTE")
        if "Return By Date Descending" in page.content():
            break
    rows: list[dict] = []
    for n in range(1, MAX_PAGES + 1):
        if n > 1:
            if f"Page${n}" not in page.content():
                break
            _postback(page, f"Page${n}")
        batch = parse_rows(page.content())
        rows += [r for r in batch if (r["return_by"] or "") >= today]
        if not batch or (batch[-1]["return_by"] or "") < today:
            break
    return rows, total


def run(fixture: str | None = None) -> dict:
    from playwright.sync_api import sync_playwright

    fscs, kws = load_profile()
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    today = dt.date.today().isoformat()
    state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {"rfqs": {}}
    prev = {k: v for k, v in state.get("rfqs", {}).items() if (v.get("return_by") or "") >= today}
    found: dict[str, dict] = {}
    errors: list[str] = []
    totals: dict[str, int | None] = {}
    if fixture:
        for r in parse_rows(Path(fixture).read_text()):
            found[r["sol"]] = {**r, "fsc": "FIXTURE", "match": any(k.search(r["text"].lower()) for k in kws), "seen": now}
        return {"now": now, "new": found, "all": found, "errors": errors, "totals": totals}

    with sync_playwright() as p:
        exe = chromium_path()
        kw = {"headless": True, **({"executable_path": exe} if exe else {})}
        browser = p.chromium.launch(**kw)
        page = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                   "(KHTML, like Gecko) Chrome/129.0 Safari/537.36 BrownBisonBidWatch/2.0").new_page()
        for fsc in fscs:
            try:
                rows, totals[fsc] = collect_fsc(page, FSC_URL.format(fsc=fsc), today)
                if totals[fsc] is None and not rows:
                    (STATE_DIR / f"raw-dibbs-{fsc}.html").write_text(page.content())
                    errors.append(f"FSC {fsc}: results grid not found; raw HTML saved")
                for r in rows:
                    key = f"{r['sol']}:{r['pr'] or r['nsn']}"  # one solicitation can carry several PRs/NSNs
                    found[key] = {**r, "fsc": fsc, "match": any(k.search(r["text"].lower()) for k in kws), "seen": now}
            except Exception as e:  # noqa: BLE001
                errors.append(f"FSC {fsc}: {type(e).__name__}: {str(e)[:160]}")
        browser.close()

    new = {k: v for k, v in found.items() if k not in prev}
    state["rfqs"] = {**prev, **found}
    state["last_run"] = now
    state["totals"] = totals
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))
    return {"now": now, "new": new, "all": found, "errors": errors, "totals": totals}


def render(r: dict) -> str:
    out = [f"## DLA DIBBS (Jones Bearing profile) — {r['now']}"]
    out += [f"- error: {e}" for e in r["errors"]]
    if r["new"]:
        out.append("\n**NEW RFQs**\n")
        out.append("| Match | FSC | Solicitation | NSN | Return by | Description | Link |")
        out.append("|---|---|---|---|---|---|---|")
        for v in sorted(r["new"].values(), key=lambda x: (not x["match"], x["fsc"])):
            out.append(f"| {'YES' if v['match'] else ''} | {v['fsc']} | {v['sol']} | {v['nsn'] or ''} | {v['return_by'] or ''} | {v.get('nomenclature') or v['text'][:120]} (qty {v.get('qty')}) | {v['url'] or ''} |")
    out.append(f"\nOpen RFQs listed: {len(r['all'])}; keyword matches: {sum(1 for v in r['all'].values() if v['match'])}.")
    return "\n".join(out)


if __name__ == "__main__":
    print(render(run(sys.argv[1] if len(sys.argv) > 1 else None)))
