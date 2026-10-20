#!/usr/bin/env python3
"""Brown Bison bid watcher — one command for full visibility.

  python3 scripts/bidwatch/run.py                 # one full scan, writes bids/_watch/REPORT.md
  python3 scripts/bidwatch/run.py --loop          # scan forever, every 60 min, re-login as needed
  python3 scripts/bidwatch/run.py --loop --interval 30
  python3 scripts/bidwatch/run.py --health        # only check hosts + credentials, no scraping
  python3 scripts/bidwatch/run.py --sources samgov,bidnet

Every cycle:
  1. Source health: is each host reachable, are credentials set, did login work.
  2. Pull ALL open bids from every reachable source (BidNet Colorado statewide + keyword searches,
     Euna/Bonfire portals, SAM.gov open + upcoming, DLA DIBBS for Jones Bearing).
  3. Match each against the company profiles; open the detail page of every match and every
     watched bid to read closing date, questions deadline, pre-bid/site walk (mandatory or not).
  4. Diff against the last run: NEW, CHANGED (dates, pre-bid, documents = addenda), CLOSED.
  5. Re-check every bid in bids/_watch/watchlist.json; download its documents when logged in.
  6. Write REPORT.md, open_bids.json, health.json. A session that expired is re-logged-in next cycle
     (and mid-cycle if a page bounces to a login screen).
Credentials: env vars only (see docs/bidwatch.md). Nothing secret is printed or committed.
"""
from __future__ import annotations

import argparse
import sys
import time
import traceback
import re
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.bidwatch import bidnet, bonfire, samgov  # noqa: E402
from scripts.bidwatch.common import (  # noqa: E402
    HEALTH_FILE, OPEN_BIDS_FILE, REPORT_FILE, WATCHLIST_FILE, cred_status, days_until, iso, load_env_file,
    load_json, load_profiles, match_profiles, save_json,
)

HOSTS = {
    "bidnet": "https://www.bidnetdirect.com/",
    "samgov": "https://api.sam.gov/",
    "bonfire": "https://parkeronline.bonfirehub.com/",
    "dibbs": "https://www.dibbs.bsm.dla.mil/",
}
CRED_NAMES = {"bidnet": list(bidnet.CREDS), "samgov": ["SAM_API_KEY"], "bonfire": list(bonfire.CREDS), "dibbs": []}
ALL_SOURCES = ["bidnet", "bonfire", "samgov", "dibbs"]


def reachable(url: str, timeout: int = 15) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BrownBisonBidWatch/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return True, f"HTTP {r.status}"
    except urllib.error.HTTPError as e:  # a 403/404 still proves the host is reachable
        return (e.code < 500 and e.code != 407), f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:80]}"


def health_check(sources: list[str]) -> dict:
    out = {}
    for s in sources:
        ok, note = reachable(HOSTS[s])
        out[s] = {"reachable": ok, "reach_note": note, "creds": cred_status(CRED_NAMES[s]),
                  "logged_in": False, "login_note": "", "count": 0, "matches": 0, "errors": []}
    return out


class _WatchSet:
    """A bid is watched if its source:id is listed, or its title / solicitation # / URL matches an
    entry's `match` regex (we usually know the solicitation number, not the portal's internal id)."""

    def __init__(self, watch: list[dict]):
        self.ids = {f"{w['source']}:{w['id']}" for w in watch if w.get("id") and w.get("source")}
        self.rx = [(w, re.compile(w["match"], re.I)) for w in watch if w.get("match")]
        self.hits: dict[str, str] = {}

    def check(self, b: dict) -> bool:
        k = f"{b['source']}:{b['id']}"
        if k in self.ids:
            return True
        hay = f"{b.get('title', '')} {b.get('sol') or ''} {b.get('url') or ''}"
        for w, rx in self.rx:
            if (not w.get("source") or w["source"] == b["source"]) and rx.search(hay):
                self.hits[w.get("name", w["match"])] = k
                return True
        return False


def key(b: dict) -> str:
    return f"{b['source']}:{b['id']}"


def scan(sources: list[str], enrich_details: bool = True) -> dict:
    load_env_file()
    profiles = load_profiles()
    started = iso()
    health = health_check(sources)
    watch = load_json(WATCHLIST_FILE, {"bids": []})["bids"]
    watched_keys = _WatchSet(watch)
    prev = load_json(OPEN_BIDS_FILE, {"bids": {}})["bids"]
    found: dict[str, dict] = {}
    downloads: dict[str, list[str]] = {}

    keywords = sorted({k for p in profiles.values() for k in p.get("bidnet_keywords", [])})
    browser_sources = [s for s in ("bidnet", "bonfire") if s in sources and health[s]["reachable"]]

    if browser_sources:
        from scripts.bidwatch.browser import Browser, PortalSession
        br = Browser()
        try:
            if "bidnet" in browser_sources:
                h = health["bidnet"]
                ses = PortalSession(br, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
                try:
                    ses.ensure_login()
                    h["logged_in"], h["login_note"] = ses.logged_in, ses.login_note
                    rows, errs, totals = bidnet.collect_open(ses, keywords)
                    if ses.creds() and "authentication/login" in ses.page.url:  # bounced mid-scan
                        ses.ensure_login()
                        rows2, errs2, _ = bidnet.collect_open(ses, keywords)
                        rows.update(rows2)
                        errs += errs2
                    h["errors"] += errs
                    h["site_totals"] = {k: v for k, v in totals.items() if k.startswith("statewide")}
                    for r in rows.values():
                        found[key(r)] = r
                    h["count"] = len(rows)
                    _enrich_and_download(ses, bidnet, found, "bidnet", profiles, watched_keys, prev,
                                         enrich_details, downloads, h)
                finally:
                    ses.close()
            if "bonfire" in browser_sources:
                h = health["bonfire"]
                orgs = load_json(Path(__file__).resolve().parents[2] / "bids/_watch/watch_profiles.json", {}) \
                    .get("bonfire_orgs", ["parkeronline"])
                ses = PortalSession(br, "bonfire", lambda p, u, pw: bonfire.login(p, u, pw, orgs[0]),
                                    lambda p: bonfire.is_logged_in(p, orgs[0]), bonfire.CREDS)
                try:
                    ses.ensure_login()
                    h["logged_in"], h["login_note"] = ses.logged_in, ses.login_note
                    for org in orgs:
                        rows, errs = bonfire.collect_open(ses, org)
                        h["errors"] += errs
                        h["count"] += len(rows)
                        for r in rows.values():
                            found[key(r)] = r
                    _enrich_and_download(ses, bonfire, found, "bonfire", profiles, watched_keys, prev,
                                         enrich_details, downloads, h)
                finally:
                    ses.close()
        finally:
            br.close()

    if "samgov" in sources and health["samgov"]["reachable"]:
        rows, errs = samgov.collect(profiles)
        health["samgov"]["errors"] += errs
        health["samgov"]["count"] = len(rows)
        health["samgov"]["logged_in"] = bool(rows) or not errs
        health["samgov"]["login_note"] = "API key" if health["samgov"]["creds"]["SAM_API_KEY"] else "SAM_API_KEY not set"
        for r in rows.values():
            found[key(r)] = r

    if "dibbs" in sources and health["dibbs"]["reachable"]:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
            import dibbs_watch  # existing watcher, keeps its own state file
            d = dibbs_watch.run()
            health["dibbs"]["errors"] += d.get("errors", [])
            health["dibbs"]["site_totals"] = d.get("totals", {})
            for k, v in d.get("all", {}).items():
                found[f"dibbs:{k}"] = {"source": "dibbs", "id": k,
                                       "title": f"{v.get('nomenclature') or v.get('text', '')[:80]} (NSN {v.get('nsn')}, qty {v.get('qty')})",
                                       "closing": v.get("return_by"), "published": v.get("issued"),
                                       "url": v.get("url"), "pdf": v.get("pdf"), "sol": v.get("sol"), "fsc": v.get("fsc"),
                                       "nsn": v.get("nsn"), "qty": v.get("qty"),
                                       "agency": "DLA", "profiles": ["jones-bearing"] if v.get("match") else []}
            health["dibbs"]["count"] = len(d.get("all", {}))
        except Exception as e:  # noqa: BLE001
            health["dibbs"]["errors"].append(f"DIBBS: {type(e).__name__}: {str(e)[:150]}")

    # profile matching for anything not yet tagged
    for b in found.values():
        if "profiles" not in b or not b["profiles"]:
            b["profiles"] = profile_hits(b, profiles)
        b["watched"] = watched_keys.check(b)
        b.setdefault("first_seen", prev.get(key(b), {}).get("first_seen", started))
        b["last_seen"] = started
    for s in sources:
        health[s]["matches"] = sum(1 for b in found.values() if b["source"] == s and b["profiles"])

    scanned_sources = {s for s in sources if health[s]["count"] > 0}
    new = {k: v for k, v in found.items() if k not in prev and v["profiles"]}
    changed = {}
    for k, v in found.items():
        if k in prev:
            diffs = _diff(prev[k], v)
            if diffs and (v["profiles"] or v["watched"]):
                changed[k] = {**v, "diffs": diffs}
    closed = {k: v for k, v in prev.items() if k not in found and v.get("source") in scanned_sources
              and (v.get("profiles") or v.get("watched"))}
    missing_watch = [w for w in watch if w.get("name", w.get("match")) not in watched_keys.hits
                     and f"{w.get('source')}:{w.get('id')}" not in found
                     and (not w.get("source") or w["source"] in scanned_sources)]

    save_json(OPEN_BIDS_FILE, {"scanned_at": started, "bids": found})
    for s in sources:
        if health[s]["count"]:
            health[s]["last_success"] = started
        else:
            health[s]["last_success"] = load_json(HEALTH_FILE, {}).get("sources", {}).get(s, {}).get("last_success")
    save_json(HEALTH_FILE, {"checked_at": started, "sources": health})
    result = {"started": started, "health": health, "found": found, "new": new, "changed": changed,
              "closed": closed, "downloads": downloads, "missing_watch": missing_watch}
    REPORT_FILE.write_text(render(result))
    return result


def profile_hits(b: dict, profiles: dict) -> list[str]:
    """Keyword match, minus profiles tied to states the bid is not in (BidNet's list mixes in Wyoming)."""
    hits = match_profiles(f"{b.get('title', '')} {b.get('agency', '')}", profiles)
    st = b.get("state")
    return [n for n in hits if not (st and profiles[n].get("states") and st not in profiles[n]["states"])]


def _enrich_and_download(ses, mod, found, source, profiles, watched_keys, prev, enrich_details, downloads, h):
    if not enrich_details:
        return
    blocked = None
    for k, b in list(found.items()):
        if b["source"] != source:
            continue
        b["profiles"] = profile_hits(b, profiles)
        old = prev.get(k, {})
        is_w = watched_keys.check(b)
        recently = old.get("detail_checked") and old.get("closing") == b.get("closing") and not is_w \
            and old.get("detail_at", "")[:10] == iso()[:10]
        if not (b["profiles"] or is_w):
            continue
        # Public BidNet detail pages add nothing but the closing time (everything else is members-only),
        # so without a login only watched bids get opened.
        if source == "bidnet" and not ses.logged_in and not is_w:
            continue
        if recently or blocked:
            found[k] = {**{f: v for f, v in old.items() if f not in ("last_seen",)}, **b}
            continue
        try:
            found[k] = {**mod.enrich(ses, b), "detail_at": iso()}
        except Exception as e:  # noqa: BLE001
            if type(e).__name__ == "Challenged":  # Cloudflare: every other detail page will fail the same way
                blocked = str(e)
                h["errors"].append(f"detail pages blocked: {e}")
                continue
            h["errors"].append(f"detail {b.get('title', '')[:60]}: {type(e).__name__}: {str(e)[:120]}")
        if is_w and ses.logged_in and hasattr(mod, "download_docs"):
            new_docs = {d["name"] for d in found[k].get("documents", [])} - {d["name"] for d in old.get("documents", [])}
            if new_docs or not old:
                downloads[k] = mod.download_docs(ses, found[k])


def _diff(old: dict, new: dict) -> list[str]:
    out = []
    for f, label in [("closing", "closing date"), ("questions_due", "questions deadline")]:
        if new.get(f) and old.get(f) and new[f] != old[f]:
            out.append(f"{label} {old[f]} -> {new[f]}")
    op, np_ = (old.get("prebid") or {}), (new.get("prebid") or {})
    if np_ and (np_.get("date") != op.get("date") or np_.get("mandatory") != op.get("mandatory")):
        out.append(f"pre-bid now {np_.get('date')} mandatory={np_.get('mandatory')}")
    od = {d["name"] for d in old.get("documents", [])}
    nd = {d["name"] for d in new.get("documents", [])}
    if old.get("documents") is not None and nd - od:
        out.append("NEW DOCUMENTS (addendum?): " + ", ".join(sorted(nd - od))[:300])
    if new.get("title") and old.get("title") and new["title"] != old["title"]:
        out.append(f"title changed: {new['title'][:80]}")
    return out


def _row(b: dict) -> str:
    pb = b.get("prebid") or {}
    walk = ""
    if pb:
        walk = f"{pb.get('date') or '?'} {'MANDATORY' if pb.get('mandatory') else ('optional' if pb.get('mandatory') is False else 'check')}"
    d = days_until(b.get("closing"))
    due = f"{b.get('closing') or '?'}" + (f" ({d}d)" if d is not None else "")
    return (f"| {','.join(b.get('profiles', []))}{' WATCHED' if b.get('watched') else ''} | {b['source']} | "
            f"{(b.get('agency') or '')[:40]} | {(b.get('title') or '')[:90]} | {due} | {walk} | {b.get('url') or ''} |")


HDR = "| Profile | Source | Agency | Title | Due | Pre-bid / walk | Link |\n|---|---|---|---|---|---|---|"


def render(r: dict) -> str:
    h = r["health"]
    lines = [f"# Bid watch report — {r['started']}", ""]
    blind = [s for s, v in h.items() if not v["reachable"] or (not v["count"] and s != "dibbs")]
    head = []
    if r["new"]:
        head.append(f"{len(r['new'])} NEW matching bids")
    if r["changed"]:
        head.append(f"{len(r['changed'])} changed (addenda/dates)")
    if blind:
        head.append("BLIND: " + ", ".join(blind))
    lines.append("**Headline:** " + ("; ".join(head) if head else "all sources scanned, no changes") + "\n")

    lines.append("## Source health\n")
    lines.append("| Source | Reachable | Credentials set | Logged in | Open bids seen | Site says | Matches | Last success | Errors |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for s, v in h.items():
        creds = ", ".join(f"{k}={'yes' if ok else 'NO'}" for k, ok in v["creds"].items()) or "n/a"
        tot = ", ".join(f"{k.replace('statewide ', '')} {n}" for k, n in (v.get("site_totals") or {}).items() if n is not None)
        lines.append(f"| {s} | {'yes' if v['reachable'] else 'NO (' + v['reach_note'] + ')'} | {creds} | "
                     f"{v['login_note'] or ('yes' if v['logged_in'] else 'no')} | {v['count']} | {tot} | {v['matches']} | "
                     f"{v.get('last_success') or 'never'} | {len(v['errors'])} |")
    if "dibbs" in h and h["dibbs"].get("site_totals"):
        lines.append("\nDIBBS 'Site says' = all RFQ records listed per FSC, including awarded/cancelled history; "
                     "'Open bids seen' = RFQs with a return-by date today or later.")

    walks = [b for b in r["found"].values() if (b.get("profiles") or b.get("watched")) and (b.get("prebid") or {}).get("date")
             and (days_until(b["prebid"]["date"]) or 99) <= 7 and (days_until(b["prebid"]["date"]) or -1) >= 0]
    if walks:
        lines += ["", "## Pre-bid meetings / site walks in the next 7 days", "", HDR] + [_row(b) for b in sorted(walks, key=lambda x: x["prebid"]["date"])]
    if r["new"]:
        lines += ["", "## NEW matching bids since last scan", "", HDR] + [_row(b) for b in sorted(r["new"].values(), key=lambda x: x.get("closing") or "9")]
    if r["changed"]:
        lines += ["", "## Changes on matching / watched bids (addenda, dates)", ""]
        for b in r["changed"].values():
            lines.append(f"- **{b.get('title', '')[:90]}** ({b['source']}): " + "; ".join(b["diffs"]) + f" — {b.get('url', '')}")
    if r["missing_watch"]:
        lines += ["", "## Watched bids NOT seen this scan (closed, moved, or source blind)", ""]
        lines += [f"- {w.get('name', w.get('id'))} ({w.get('source')})" for w in r["missing_watch"]]
    if r["closed"]:
        lines += ["", "## No longer listed (closed/awarded)", ""]
        lines += [f"- {v.get('title', '')[:90]} ({v['source']}, due {v.get('closing')})" for v in r["closed"].values()]
    upcoming = [b for b in r["found"].values() if b.get("upcoming") and b.get("profiles")]
    if upcoming:
        lines += ["", "## UPCOMING (presolicitations, sources sought, special notices)", "", HDR]
        lines += [_row(b) for b in sorted(upcoming, key=lambda x: x.get("closing") or "9")]
    # BidNet's AGGREGATE tab occasionally keeps long-closed bids listed; a past closing date is not open
    open_m = [b for b in r["found"].values() if b.get("profiles") and not b.get("upcoming") and b["source"] != "dibbs"
              and (days_until(b.get("closing")) is None or days_until(b.get("closing")) >= 0)]
    lines += ["", f"## All open matching bids, excluding DIBBS parts RFQs ({len(open_m)})", "", HDR]
    lines += [_row(b) for b in sorted(open_m, key=lambda x: x.get("closing") or "9")]
    dib = sorted((b for b in r["found"].values() if b["source"] == "dibbs"),
                 key=lambda x: (-(x.get("qty") or 0), x.get("closing") or "9"))
    if dib:
        by_fsc: dict[str, int] = {}
        for b in dib:
            by_fsc[b.get("fsc") or "?"] = by_fsc.get(b.get("fsc") or "?", 0) + 1
        lines += ["", f"## DLA DIBBS open RFQs for Jones Bearing FSCs ({len(dib)}; "
                  + ", ".join(f"FSC {f}: {n}" for f, n in sorted(by_fsc.items())) + ")", "",
                  "Largest quantities first, top 60. Quoting needs a CAGE code + DIBBS account (Jones Bearing has neither yet).", "",
                  "| FSC | Solicitation | Item | Qty | Return by | Link |", "|---|---|---|---|---|---|"]
        lines += [f"| {b.get('fsc')} | {b.get('sol')} | {(b.get('title') or '')[:70]} | {b.get('qty')} | {b.get('closing')} | {b.get('url')} |"
                  for b in dib[:60]]
    if r["downloads"]:
        lines += ["", "## Documents downloaded", ""]
        for k, files in r["downloads"].items():
            lines += [f"- {k}: {f}" for f in files]
    errs = [(s, e) for s, v in h.items() for e in v["errors"]]
    if errs:
        lines += ["", "## Errors", ""] + [f"- {s}: {e}" for s, e in errs[:60]]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval", type=int, default=60, help="minutes between scans in --loop")
    ap.add_argument("--sources", default=",".join(ALL_SOURCES))
    ap.add_argument("--health", action="store_true")
    ap.add_argument("--no-detail", action="store_true")
    a = ap.parse_args()
    sources = [s for s in a.sources.split(",") if s in ALL_SOURCES]
    if a.health:
        load_env_file()
        for s, v in health_check(sources).items():
            print(f"{s:8} reachable={v['reachable']} ({v['reach_note']}) creds={v['creds']}")
        return 0
    while True:
        try:
            r = scan(sources, enrich_details=not a.no_detail)
            print(REPORT_FILE.read_text().split("## Source health")[0].strip())
            ok = any(v["count"] for v in r["health"].values())
        except Exception:  # noqa: BLE001 - never let the loop die
            traceback.print_exc()
            ok = False
        if not a.loop:
            return 0 if ok else 2
        time.sleep(max(5, a.interval) * 60)


if __name__ == "__main__":
    sys.exit(main())
