#!/usr/bin/env python3
"""SAM.gov opportunities watcher (federal only) with state diffing.

Env: SAM_API_KEY (free, from your SAM.gov account page). Network: api.sam.gov must be reachable.
Searches HVAC/mechanical-relevant notices with place of performance in Colorado, plus the NAICS
codes we can perform, and reports NEW notices and CHANGED response deadlines since the last run.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE_FILE = REPO / "bids" / "_watch" / "samgov_state.json"
API = "https://api.sam.gov/opportunities/v2/search"

QUERIES = [
    {"title": "HVAC", "state": "CO"},
    {"title": "chiller", "state": "CO"},
    {"title": "boiler", "state": "CO"},
    {"title": "mechanical", "state": "CO"},
    {"ncode": "238220", "state": "CO"},   # plumbing, heating, AC contractors
    {"ncode": "561210", "state": "CO"},   # facilities support services
    {"ncode": "561730", "state": "CO"},   # landscaping services
]


def fetch(params: dict, key: str, days: int) -> list[dict]:
    today = dt.date.today()
    q = {
        "api_key": key,
        "postedFrom": (today - dt.timedelta(days=days)).strftime("%m/%d/%Y"),
        "postedTo": today.strftime("%m/%d/%Y"),
        "limit": 100,
        "ptype": "o,k,p",
        **params,
    }
    url = f"{API}?{urllib.parse.urlencode(q)}"
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r).get("opportunitiesData", [])


def run(days: int = 45) -> dict:
    key = os.environ.get("SAM_API_KEY")
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {"notices": {}}
    prev = state["notices"]
    if not key:
        return {"now": now, "error": "SAM_API_KEY not set", "new": {}, "changed": {}, "all": prev}
    found: dict[str, dict] = {}
    errors = []
    for params in QUERIES:
        try:
            for o in fetch(params, key, days):
                nid = o.get("noticeId")
                if not nid:
                    continue
                found[nid] = {
                    "title": o.get("title"), "sol": o.get("solicitationNumber"),
                    "agency": o.get("fullParentPathName"), "posted": o.get("postedDate"),
                    "due": o.get("responseDeadLine"), "type": o.get("type"), "url": o.get("uiLink"),
                    "naics": o.get("naicsCode"), "seen": now,
                }
        except Exception as e:  # noqa: BLE001
            errors.append(f"{params}: {type(e).__name__}: {str(e)[:160]}")
    new = {k: v for k, v in found.items() if k not in prev}
    changed = {k: v for k, v in found.items() if k in prev and prev[k].get("due") != v.get("due")}
    state["notices"] = {**prev, **found}
    state["last_run"] = now
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))
    return {"now": now, "error": None, "errors": errors, "new": new, "changed": changed, "all": found}


def render(r: dict) -> str:
    out = [f"## SAM.gov (federal) — {r['now']}"]
    if r.get("error"):
        out.append(f"**Not run:** {r['error']}. Set SAM_API_KEY and allow api.sam.gov.")
        return "\n".join(out)
    for e in r.get("errors", []):
        out.append(f"- error: {e}")

    def table(title, items):
        if not items:
            return
        out.append(f"\n**{title}**\n")
        out.append("| Title | Sol # | Agency | Due | Link |")
        out.append("|---|---|---|---|---|")
        for v in items.values():
            out.append(f"| {v['title']} | {v['sol'] or ''} | {v['agency'] or ''} | {v['due'] or ''} | {v['url'] or ''} |")

    table("NEW notices", r["new"])
    table("CHANGED response deadline", r["changed"])
    out.append(f"\nOpen notices tracked: {len(r['all'])}.")
    return "\n".join(out)


if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 45
    print(render(run(days)))
