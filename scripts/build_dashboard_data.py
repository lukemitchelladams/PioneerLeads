#!/usr/bin/env python3
"""Build the Bid Command dashboard's data files from the repo.

Inputs (all in bids/_watch/):
  pipeline.json      hand-maintained registry of tracked bids, key dates and document gaps
  open_bids.json     latest portal scan (scripts/bidwatch/run.py), optional
  health.json        latest source health (scripts/bidwatch/run.py), optional
  govtribe_ledger.json  GovTribe review ledger, optional

Outputs (bids/_watch/dashboard/*.json, each an array of flat row objects):
  bids.json       one row per tracked bid, with walk state and missing-document count
  events.json     every dated event for live bids (submissions, mandatory walks, questions, RSVPs)
  doc_gaps.json   every solicitation document we do not hold, and where to get it
  portal_feed.json  open portal bids that match a company profile (from the scanner)
  sources.json    one row per bid source: live / blocked / not logged in, counts, last success

Usage: python3 scripts/build_dashboard_data.py [--now 2026-10-20T08:00:00-06:00]
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WATCH = REPO / "bids" / "_watch"
OUT = WATCH / "dashboard"
MT = timezone(timedelta(hours=-6))
DEAD = {"NO"}


def load(name: str, default):
    p = WATCH / name
    return json.loads(p.read_text()) if p.exists() else default


def ts(s: str | None) -> datetime | None:
    if not s:
        return None
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=MT)


def walk_state(b: dict, now: datetime) -> str:
    when, mand = ts(b.get("prebid")), b.get("prebid_mandatory")
    if not when:
        return "None" if mand is False else "Unknown"
    label = "Mandatory" if mand else ("Optional" if mand is False else "Unclear")
    if when < now:
        return f"{label}, passed"
    hours = (when - now).total_seconds() / 3600
    return f"{label}, in {hours:.0f}h" if hours < 72 else f"{label}, upcoming"


def build(now: datetime) -> dict[str, list[dict]]:
    pipe = load("pipeline.json", {"bids": [], "events": [], "doc_gaps": []})
    by_id = {b["id"]: b for b in pipe["bids"]}
    gaps_by_bid: dict[str, int] = {}
    for g in pipe["doc_gaps"]:
        gaps_by_bid[g["bid"]] = gaps_by_bid.get(g["bid"], 0) + 1

    bids = []
    for b in pipe["bids"]:
        due = ts(b["due"])
        bids.append({
            "id": b["id"], "agency": b["agency"], "title": b["title"], "sol": b["sol"], "trade": b["trade"],
            "due": b["due"], "due_date": b["due"][:10], "due_source": b.get("due_source", "Solicitation"),
            "status": "Closed" if due and due < now else "Open",
            "days_left": round((due - now).total_seconds() / 86400, 1) if due else None,
            "portal": b["portal"], "decision": b["decision"], "decision_note": b["decision_note"],
            "prebid": b.get("prebid") or "", "walk": walk_state(b, now),
            "performer": b["performer"], "subs": b["subs"], "sub_pricing": b.get("sub_pricing", "Unknown"), "docs_missing": gaps_by_bid.get(b["id"], 0),
            "contact": b["contact"], "folder": b.get("folder") or "",
        })

    events = []
    for b in pipe["bids"]:
        if b["decision"] in DEAD:
            continue
        events.append({"bid": b["id"], "when": b["due"], "kind": "Submission", "note": b["portal"]})
        if b.get("prebid"):
            kind = "MANDATORY pre-bid" if b.get("prebid_mandatory") else "Pre-bid (optional)"
            if not any(e["bid"] == b["id"] and e["when"] == b["prebid"] for e in pipe["events"]):
                events.append({"bid": b["id"], "when": b["prebid"], "kind": kind, "note": ""})
    events += [e for e in pipe["events"] if by_id.get(e["bid"], {}).get("decision") not in DEAD]
    rows = []
    for e in events:
        b = by_id.get(e["bid"], {})
        when = ts(e["when"])
        rows.append({
            "key": f"{e['bid']}|{e['kind']}|{e['when']}", "bid": e["bid"], "when": e["when"],
            "date": e["when"][:10], "kind": e["kind"], "agency": b.get("agency", ""), "sol": b.get("sol", ""),
            "decision": b.get("decision", ""), "note": e.get("note", ""),
            "critical": e["kind"].startswith("MANDATORY") or e["kind"] == "Submission",
            "past": bool(when and when < now),
            "days_left": round((when - now).total_seconds() / 86400, 2) if when else None,
        })
    rows.sort(key=lambda r: ts(r["when"]))

    gaps = [{"key": f"{g['bid']}|{g['item']}", "bid": g["bid"], "agency": by_id.get(g["bid"], {}).get("agency", ""),
             "sol": by_id.get(g["bid"], {}).get("sol", ""), "due": by_id.get(g["bid"], {}).get("due", ""),
             "decision": by_id.get(g["bid"], {}).get("decision", ""), "item": g["item"], "where": g["where"]}
            for g in pipe["doc_gaps"]]

    scan = load("open_bids.json", {"bids": {}})
    feed = []
    for k, b in scan.get("bids", {}).items():
        if not b.get("profiles") and not b.get("watched"):
            continue
        pre = b.get("prebid") or {}
        first = ts(b.get("first_seen"))
        feed.append({
            "key": k, "source": b.get("source", ""), "agency": b.get("agency", ""), "title": b.get("title", ""),
            "sol": b.get("sol") or "", "closing": b.get("closing") or "", "posted": b.get("published") or "",
            "prebid_date": pre.get("date") or "" if isinstance(pre, dict) else "",
            "prebid_mandatory": {True: "Mandatory", False: "Optional"}.get(pre.get("mandatory") if isinstance(pre, dict) else None, ""),
            "profiles": ", ".join(b.get("profiles") or []), "watched": bool(b.get("watched")),
            "new_24h": bool(first and now - first < timedelta(hours=24)), "url": b.get("url", ""),
        })
    feed.sort(key=lambda r: (r["closing"] or "9999"))

    health = load("health.json", {})
    sources = []
    names = {"bidnet": "BidNet / RMEPS (Colorado)", "bonfire": "Euna / Bonfire (Town of Parker)",
             "samgov": "SAM.gov", "dibbs": "DLA DIBBS (Jones Bearing)"}
    for s, label in names.items():
        h = health.get("sources", {}).get(s)
        if not h:
            sources.append({"source": label, "status": "Not run", "detail": "Scanner has not run against this source yet",
                            "open_count": 0, "matches": 0, "last_success": ""})
            continue
        if not h.get("reachable"):
            status = "Blocked"
        elif h.get("count"):
            status = "Live" if (h.get("logged_in") or s in ("dibbs",)) else "Live (public, not logged in)"
        else:
            status = "Reachable, 0 parsed"
        sources.append({"source": label, "status": status,
                        "detail": "; ".join([h.get("login_note") or "", *(h.get("errors") or [])[:2]]).strip("; ")[:240],
                        "open_count": h.get("count", 0), "matches": h.get("matches", 0),
                        "last_success": h.get("last_success") or ""})
    led = load("govtribe_ledger.json", {})
    if led:
        sources.append({"source": "GovTribe (BidNet/Bonfire/OpenGov/SAM index)", "status": "Live (index lags)",
                        "detail": f"Newest posting indexed: {led.get('last_posted_reviewed')}. "
                                  f"{led.get('baseline_count')} open CO records reviewed {led.get('baseline_reviewed_at', '')[:16]}.",
                        "open_count": led.get("baseline_count", 0), "matches": len(led.get("triaged", {})),
                        "last_success": led.get("baseline_reviewed_at", "")})
    return {"bids": bids, "events": rows, "doc_gaps": gaps, "portal_feed": feed, "sources": sources}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--now", help="ISO time to compute walk states against (default: now)")
    a = ap.parse_args()
    now = ts(a.now) if a.now else datetime.now(MT)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows in build(now).items():
        (OUT / f"{name}.json").write_text(json.dumps(rows, indent=1) + "\n")
        print(f"{name}: {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
