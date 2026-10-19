#!/usr/bin/env python3
"""DLA DIBBS watcher: open RFQs by Federal Supply Class for the Jones Bearing profile.

DIBBS (https://www.dibbs.bsm.dla.mil) posts most DLA parts buys: mounted bearings, pulleys, conveyors,
material-handling gear. Viewing is public behind a DoD consent banner; quoting needs a CAGE + account.

For each FSC in watch_profiles.json -> profiles.jones-bearing.samgov ccode entries, this loads the RFQ
list page, extracts solicitation number, NSN, nomenclature, quantity, return-by date and link, keyword-
filters on the profile's bidnet_keywords, and diffs against bids/_watch/dibbs_state.json.

UNTESTED against the live site (blocked from the build environment). Page structure is inferred: the
extractor takes every table row that contains a solicitation-number pattern (SPE####-##-?-####) and
pulls the first NSN-looking token and date. On a parse miss it saves raw HTML next to the state file.
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

SOL_RX = re.compile(r"\bSPE[0-9A-Z]{4}-?\d{2}-[A-Z]-\d{4}\b|\bSP[0-9A-Z]{4}-?\d{2}-[A-Z]-\d{4}\b")
NSN_RX = re.compile(r"\b\d{4}-\d{2}-\d{3}-\d{4}\b")
DATE_RX = re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b")


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
    for sel in ["input[value='OK']", "button:has-text('OK')", "a:has-text('OK')", "input[type='submit']"]:
        try:
            if page.locator(sel).count():
                page.click(sel, timeout=5000)
                page.wait_for_load_state("domcontentloaded", timeout=30000)
                return
        except Exception:  # noqa: BLE001
            continue


def extract_rows(page) -> list[dict]:
    rows = page.evaluate(
        """() => Array.from(document.querySelectorAll('tr')).map(tr => ({
              text: (tr.innerText || '').replace(/\\s+/g, ' ').trim(),
              links: Array.from(tr.querySelectorAll('a[href]')).map(a => a.href)
           })).filter(r => /SP[0-9A-Z]{4}-?\\d{2}-[A-Z]-\\d{4}/.test(r.text))"""
    )
    out = []
    for r in rows:
        sol = SOL_RX.search(r["text"])
        nsn = NSN_RX.search(r["text"])
        dates = DATE_RX.findall(r["text"])
        if not sol:
            continue
        out.append({
            "sol": sol.group(0), "nsn": nsn.group(0) if nsn else None,
            "text": r["text"][:400], "return_by": dates[-1] if dates else None,
            "url": next((l for l in r["links"] if "RfqRec" in l or "rfq" in l.lower()), r["links"][0] if r["links"] else None),
        })
    return out


def run(fixture: str | None = None) -> dict:
    from playwright.sync_api import sync_playwright

    fscs, kws = load_profile()
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {"rfqs": {}}
    prev = state["rfqs"]
    found: dict[str, dict] = {}
    errors: list[str] = []
    targets = {f: FSC_URL.format(fsc=f) for f in fscs} if not fixture else {"FIXTURE": fixture}

    with sync_playwright() as p:
        exe = chromium_path()
        browser = p.chromium.launch(headless=True, executable_path=exe) if exe else p.chromium.launch(headless=True)
        page = browser.new_context(user_agent="BrownBison-BidWatch/1.0 (+luke@brownbisonco.com)").new_page()
        for fsc, url in targets.items():
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                if not fixture:
                    accept_banner(page)
                    if "RfqRecs" not in page.url:
                        page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(1000)
                rows = extract_rows(page)
                if not rows:
                    (STATE_DIR / f"raw-dibbs-{fsc}.html").write_text(page.content())
                    errors.append(f"FSC {fsc}: 0 rows parsed; raw HTML saved")
                for r in rows:
                    t = r["text"].lower()
                    found[r["sol"]] = {**r, "fsc": fsc, "match": any(k.search(t) for k in kws), "seen": now}
            except Exception as e:  # noqa: BLE001
                errors.append(f"FSC {fsc}: {type(e).__name__}: {str(e)[:160]}")
        browser.close()

    new = {k: v for k, v in found.items() if k not in prev}
    state["rfqs"] = {**prev, **found}
    state["last_run"] = now
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))
    return {"now": now, "new": new, "all": found, "errors": errors}


def render(r: dict) -> str:
    out = [f"## DLA DIBBS (Jones Bearing profile) — {r['now']}"]
    out += [f"- error: {e}" for e in r["errors"]]
    if r["new"]:
        out.append("\n**NEW RFQs**\n")
        out.append("| Match | FSC | Solicitation | NSN | Return by | Description | Link |")
        out.append("|---|---|---|---|---|---|---|")
        for v in sorted(r["new"].values(), key=lambda x: (not x["match"], x["fsc"])):
            out.append(f"| {'YES' if v['match'] else ''} | {v['fsc']} | {v['sol']} | {v['nsn'] or ''} | {v['return_by'] or ''} | {v['text'][:120]} | {v['url'] or ''} |")
    out.append(f"\nOpen RFQs listed: {len(r['all'])}; keyword matches: {sum(1 for v in r['all'].values() if v['match'])}.")
    return "\n".join(out)


if __name__ == "__main__":
    print(render(run(sys.argv[1] if len(sys.argv) > 1 else None)))
