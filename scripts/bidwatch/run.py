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
import json
import os
import subprocess
import sys
import time
import traceback
import re
import hashlib
import shutil
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.bidwatch import bidnet, bonfire, samgov, samgov_bulk  # noqa: E402
from scripts.bidwatch.common import (  # noqa: E402
    DEBUG_DIR, HEALTH_FILE, RUN_LOCK, OPEN_BIDS_FILE, REPO, REPORT_FILE, WATCH_DIR, WATCHLIST_FILE, cred_status, days_until,
    iso, load_env_file, load_json, load_profiles, match_profiles, save_json,
)

SCANNED_BY = os.environ.get("BIDWATCH_HOST") or __import__("socket").gethostname()

HOSTS = {
    "bidnet": "https://www.bidnetdirect.com/",
    "samgov": "https://api.sam.gov/",
    "bonfire": "https://parkeronline.bonfirehub.com/",
    "dibbs": "https://www.dibbs.bsm.dla.mil/",
}
CRED_NAMES = {"bidnet": list(bidnet.CREDS), "samgov": ["SAM_API_KEY"], "bonfire": list(bonfire.CREDS), "dibbs": []}
ALL_SOURCES = ["bidnet", "bonfire", "samgov", "dibbs"]


def reachable(url: str, timeout: int = 30) -> tuple[bool, str]:
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
        self.by_id = {f"{w['source']}:{w['id']}": w for w in watch if w.get("id") and w.get("source")}
        self.ids = set(self.by_id)
        self.rx = [(w, re.compile(w["match"], re.I)) for w in watch if w.get("match")]
        self.hits: dict[str, str] = {}

    def entry(self, b: dict) -> dict | None:
        """The watchlist entry that covers bid `b` (an id match first), or None. Every pattern entry that matches is
        recorded as seen, so a bid listed twice (by id and by pattern) is never reported as 'not seen'."""
        k = f"{b['source']}:{b['id']}"
        first = self.by_id.get(k)
        # title + solicitation number only: matching the URL let "18863" (Jeffco 26-18863AP) hit BidNet's id
        # 444188638946 on an unrelated bid (2026-10-20)
        hay = f"{b.get('title', '')} {b.get('sol') or ''}"
        for w, rx in self.rx:
            if (not w.get("source") or w["source"] == b["source"]) and rx.search(hay):
                self.hits[w.get("name", w["match"])] = k
                first = first or w
        return first

    def check(self, b: dict) -> bool:
        return self.entry(b) is not None


def _is_open(b: dict) -> bool:
    """BidNet's AGGREGATE tab keeps some long-closed bids listed (a 2021 Pagosa Ranger District notice showed up
    as NEW on 2026-10-20): a past closing date is not open. No closing date counts as open."""
    d = days_until(b.get("closing"))
    return d is None or d >= 0


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
    if "bidnet" in browser_sources and bidnet.cooldown_until():
        # BidNet served its robot check recently: leave it alone, keep the last good data (carried forward below)
        browser_sources.remove("bidnet")
        health["bidnet"]["complete"] = False
        health["bidnet"]["login_note"] = f"COOL-DOWN after a robot check, until {bidnet.cooldown_until()}"

    br = None
    if browser_sources:
        from scripts.bidwatch.browser import Browser, PortalSession
        try:
            br = Browser()
        except Exception as e:  # noqa: BLE001 - Chromium missing or broken: SAM.gov still runs
            for s in browser_sources:
                health[s]["errors"].append(f"browser did not start: {type(e).__name__}: {str(e)[:150]}")
                health[s]["complete"] = False
    if br:
        try:
            if "bidnet" in browser_sources:
                h = health["bidnet"]
                ses = None
                try:
                    ses = PortalSession(br, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
                    ses.ensure_login()
                    h["logged_in"], h["login_note"] = ses.logged_in, ses.login_note
                    rows, errs, totals = bidnet.collect_open(ses, keywords)
                    # the lists are public, but documents are members-only: if the session lapsed during the list
                    # walk, log in again before the detail pass (the URL is no signal after a sign-on redirect)
                    if ses.creds() and ses.logged_in and not bidnet._page_logged_in(ses.page):
                        ses.logged_in = False
                        ses.ensure_login()
                        h["logged_in"] = ses.logged_in
                        h["login_note"] = ses.login_note if ses.login_note == "session reused" \
                            else f"{ses.login_note} (re-login mid-scan)"
                    h["errors"] += errs
                    h["site_totals"] = {k: v for k, v in totals.items() if k.startswith("statewide")}
                    h["complete"] = bool(totals.get("_complete"))
                    if totals.get("_bot_check"):
                        h["login_note"] = (h["login_note"] + "; " if h["login_note"] else "") + "ROBOT CHECK (rate-limited)"
                    for r in rows.values():
                        found[key(r)] = r
                    h["count"] = len(rows)
                    if totals.get("_bot_check"):
                        # BidNet is refusing pages: every detail page would be refused too (and prolong the block)
                        h["errors"].append("detail pages and downloads skipped: BidNet robot check this scan")
                        _restore_detail(found, prev, "bidnet")
                    else:
                        _enrich_and_download(ses, bidnet, found, "bidnet", profiles, watched_keys, prev,
                                             enrich_details, downloads, h)
                except Exception as e:  # noqa: BLE001 - one source failing must not cost the others their scan
                    h["errors"].append(f"BidNet scan stopped: {type(e).__name__}: {str(e)[:150]}")
                    h["complete"] = False
                    _restore_detail(found, prev, "bidnet")
                finally:
                    if ses:
                        ses.close()
            if "bonfire" in browser_sources:
                h = health["bonfire"]
                orgs = load_json(Path(__file__).resolve().parents[2] / "bids/_watch/watch_profiles.json", {}) \
                    .get("bonfire_orgs", ["parkeronline"])
                ses = None
                try:
                    ses = PortalSession(br, "bonfire", lambda p, u, pw: bonfire.login(p, u, pw, orgs[0]),
                                        lambda p: bonfire.is_logged_in(p, orgs[0]), bonfire.CREDS)
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
                except Exception as e:  # noqa: BLE001
                    h["errors"].append(f"Bonfire scan stopped: {type(e).__name__}: {str(e)[:150]}")
                    h["complete"] = False
                    _restore_detail(found, prev, "bonfire")
                finally:
                    if ses:
                        ses.close()
        finally:
            br.close()

    if "samgov" in sources and (health["samgov"]["reachable"] or health["samgov"]["creds"].get("SAM_API_KEY")):
        rows, errs = samgov.collect(profiles)
        health["samgov"]["errors"] += errs
        health["samgov"]["count"] = len(rows)
        health["samgov"]["logged_in"] = bool(rows) or not errs
        health["samgov"]["login_note"] = "API key" if health["samgov"]["creds"]["SAM_API_KEY"] else "SAM_API_KEY not set"
        for r in rows.values():
            found[key(r)] = r
    if "samgov" in sources:
        _merge_sam_bulk(found, prev, health["samgov"], profiles)
    if "samgov" in sources and health["samgov"]["count"] == 0:
        # never a silent zero: say why (no key, probe/API down) so a reader does not mistake it for 'no bids'
        h = health["samgov"]
        h["login_note"] = h["login_note"] or ("API key" if h["creds"].get("SAM_API_KEY") else "SAM_API_KEY not set")
        if not h["errors"]:
            h["errors"].append(f"SAM.gov returned no rows: reachability {h['reach_note']}; "
                               f"key {'set' if h['creds'].get('SAM_API_KEY') else 'NOT set'}")

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
        if b.get("carried_forward") and b.get("last_seen"):
            continue  # not seen this run; keep the real last_seen
        b.pop("carried_forward", None)
        b["last_seen"] = started
    for s in sources:
        health[s]["matches"] = sum(1 for b in found.values() if b["source"] == s and b["profiles"])

    # A source whose list came back incomplete (BidNet robot check, short statewide list) must not make
    # bids look closed: carry its previous open bids forward, flagged, and skip closed-detection for it.
    incomplete = {s for s in sources if health[s].get("complete") is False
                  or (health[s]["count"] == 0 and (not health[s]["reachable"] or health[s]["errors"]))}
    for k, v in prev.items():
        if v.get("source") in incomplete and k not in found and (days_until(v.get("closing")) or 0) >= 0:
            found[k] = {**v, "carried_forward": True}
    for s in incomplete:
        health[s]["carried_forward"] = True
        health[s]["errors"].append(f"{s} list incomplete this scan: previous open bids carried forward, none marked closed")
    # a source that was unreachable keeps its previous rows: count them so the report is not misread as empty
    for s in incomplete:
        if health[s]["count"] == 0:
            health[s]["blind"] = True  # nothing fresh at all this run (vs. a partial list): last_success stays old
            health[s]["count"] = sum(1 for b in found.values() if b["source"] == s)
            health[s]["matches"] = sum(1 for b in found.values() if b["source"] == s and b["profiles"])
    # Sources not scanned this run (a --sources subset, e.g. a SAM.gov-only pull) keep their last results,
    # so open_bids.json and the dashboard never lose the BidNet/DIBBS rows because one source was refreshed.
    for k, v in prev.items():
        if v.get("source") not in sources and k not in found and (days_until(v.get("closing")) or 0) >= 0:
            found[k] = {**v, "carried_forward": True}
    scanned_sources = {s for s in sources if health[s]["count"] > 0 and s not in incomplete}
    new = {k: v for k, v in found.items() if k not in prev and v["profiles"] and _is_open(v)}
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
    prev_health = load_json(HEALTH_FILE, {}).get("sources", {})
    for s in sources:
        if health[s]["count"] and not health[s].get("blind"):
            health[s]["last_success"] = started
        else:
            health[s]["last_success"] = prev_health.get(s, {}).get("last_success")
    # health.json keeps the last known state of sources that were not part of this run
    health_all = {**{s: {**v, "not_scanned_this_run": True} for s, v in prev_health.items() if s not in health},
                  **health}
    save_json(HEALTH_FILE, {"checked_at": started, "scanned_by": SCANNED_BY, "sources": health_all})
    filed = _file_watched_docs(downloads, found, watched_keys)
    result = {"started": started, "health": health_all, "found": found, "new": new, "changed": changed,
              "closed": closed, "downloads": downloads, "missing_watch": missing_watch, "filed": filed}
    REPORT_FILE.write_text(render(result))
    return result


def _sha1(p: Path) -> str:
    return hashlib.sha1(p.read_bytes()).hexdigest()


def _file_watched_docs(downloads: dict, found: dict, watched_keys) -> list[str]:
    """Copy each watched bid's newly downloaded documents into its bid folder's docs/ (the watchlist entry's
    `folder`), skipping files whose content is already there under any name, then refresh that folder's
    MANIFEST.md (CLAUDE.md rule 0c: complete packages). Returns repo-relative paths written, for the push."""
    out: list[str] = []
    for k, paths in downloads.items():
        b = found.get(k)
        w = watched_keys.entry(b) if b else None
        folder = (w or {}).get("folder")
        if not folder or not (REPO / folder).is_dir():
            continue  # no bid folder yet: the files stay in bids/_watch/downloads/<source>/<id>/
        dest = REPO / folder / "docs"
        dest.mkdir(exist_ok=True)
        have = {}
        for f in dest.iterdir():
            if f.is_file():
                have.setdefault(f.stat().st_size, []).append(f)
        wrote = False
        for p in map(Path, paths):
            if not p.is_file():
                continue
            if any(_sha1(f) == _sha1(p) for f in have.get(p.stat().st_size, [])):
                continue  # same bytes already filed (perhaps under the name a person gave it)
            tgt = dest / p.name
            if tgt.exists():  # same name, different bytes: a revised document; keep both
                tgt = dest / f"{p.stem} (rev {iso()[:10]}){p.suffix}"
            shutil.copy2(p, tgt)
            have.setdefault(tgt.stat().st_size, []).append(tgt)
            out.append(str(tgt.relative_to(REPO)))
            wrote = True
        if wrote:
            try:
                subprocess.run([sys.executable, str(REPO / "scripts/doc_manifest.py"), Path(folder).name], cwd=REPO,
                               capture_output=True, text=True, timeout=300)
                if (dest / "MANIFEST.md").exists():
                    out.append(str((dest / "MANIFEST.md").relative_to(REPO)))
            except Exception:  # noqa: BLE001 - a manifest refresh never fails the scan
                pass
    return out


def _merge_sam_bulk(found: dict, prev: dict, h: dict, profiles: dict) -> None:
    """Add the nightly SAM.gov bulk file's matches (no API key needed; samgov_bulk.py) under the API's rows.
    The API stays first: it has attachments and today's postings. The file adds notices the API's state query
    cannot see (blank place of performance, Colorado buying office) and keeps SAM.gov alive without the API."""
    api_rows = [b for b in found.values() if b["source"] == "samgov"]
    api_ok = bool(api_rows) and not h["errors"]
    for b in api_rows:
        b.setdefault("via", "api")
    bulk, note = samgov_bulk.collect(profiles)
    h["bulk_note"] = note
    added = 0
    for r in bulk.values():
        k = key(r)
        if k in found:
            found[k]["via"] = "api+bulk"
        else:
            found[k] = r
            added += 1
    h["bulk_added"] = added
    if bulk:
        h["count"] += added
        if not api_ok:  # last night's file lacks today's postings: keep the API's earlier rows, close nothing
            h["complete"] = False
        h["login_note"] = "; ".join(x for x in (h.get("login_note"), f"+{added} from the nightly bulk file") if x)
        return
    h["errors"].append(note)
    for k, v in prev.items():  # file unavailable: keep the rows only it had found instead of reading them as closed
        if v.get("source") == "samgov" and v.get("via") == "bulk" and k not in found \
                and (days_until(v.get("closing")) or 0) >= 0:
            found[k] = {**v, "carried_forward": True}


def profile_hits(b: dict, profiles: dict) -> list[str]:
    """Keyword match, minus profiles tied to states the bid is not in (BidNet's list mixes in Wyoming)."""
    hits = match_profiles(f"{b.get('title', '')} {b.get('agency', '')}", profiles)
    st = b.get("state")
    return [n for n in hits if not (st and profiles[n].get("states") and st not in profiles[n]["states"])]


DETAIL_FIELDS = ("documents", "prebid", "sol", "agency", "closing_text", "items_text", "description")


def _keep_detail(row: dict, old: dict) -> dict:
    """The listing row's fresh facts over an earlier detail read, without letting the row's blanks (agency "",
    no documents) erase what a detail page said."""
    out = {**{f: v for f, v in old.items() if f != "last_seen"}, **row}
    for f in DETAIL_FIELDS:
        if not row.get(f) and old.get(f):
            out[f] = old[f]
    return out


def _restore_detail(found: dict, prev: dict, source: str) -> None:
    """After a skipped or broken detail pass, give each listed bid back the detail an earlier scan read."""
    for k, b in list(found.items()):
        if b.get("source") == source and k in prev and not b.get("detail_at"):
            found[k] = _keep_detail(b, prev[k])


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
            found[k] = _keep_detail(b, old)
            continue
        try:
            got = mod.enrich(ses, b)
            # a detail page that came back thin (documents tab did not load, members-only fields hidden after a
            # session expiry) must not erase what an earlier scan read, or the next scan reports every document
            # as a new addendum
            for f in DETAIL_FIELDS:
                if not got.get(f) and old.get(f):
                    got[f] = old[f]
            found[k] = {**got, "detail_at": iso()}
        except Exception as e:  # noqa: BLE001
            found[k] = _keep_detail(b, old)
            if type(e).__name__ == "Challenged":  # robot check / Cloudflare: every other page will fail the same way
                blocked = str(e)
                h["errors"].append(f"detail pages blocked: {e}")
                continue
            h["errors"].append(f"detail {b.get('title', '')[:60]}: {type(e).__name__}: {str(e)[:120]}")
        if is_w and ses.logged_in and hasattr(mod, "download_docs"):
            try:
                got = mod.download_docs(ses, found[k])  # only files not already on disk
            except Exception as e:  # noqa: BLE001
                got = []
                if type(e).__name__ == "Challenged":
                    blocked = str(e)
                    h["errors"].append(f"downloads stopped: {e}")
                else:
                    h["errors"].append(f"download {b.get('title', '')[:60]}: {type(e).__name__}: {str(e)[:120]}")
            if got:
                downloads[k] = got
            if hasattr(mod, "doc_path"):
                docs = (found[k].get("documents") or [])[:60]
                missing = [d for d in docs if not ((pth := mod.doc_path(found[k], d)) and pth.is_file())]
                if missing:
                    h["errors"].append(f"{b.get('title', '')[:60]}: {len(missing)} of {len(docs)} documents not "
                                       "downloaded yet (tried again next scan)")


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
    where = ""
    if b.get("source") == "samgov" and not b.get("state") and b.get("office_state"):
        where = f" (place of performance not stated; {b['office_state']} buying office)"
    return (f"| {','.join(b.get('profiles', []))}{' WATCHED' if b.get('watched') else ''} | {b['source']} | "
            f"{(b.get('agency') or '')[:40]} | {(b.get('title') or '')[:90]}{where} | {due} | {walk} | {b.get('url') or ''} |")


HDR = "| Profile | Source | Agency | Title | Due | Pre-bid / walk | Link |\n|---|---|---|---|---|---|---|"


def render(r: dict) -> str:
    h = r["health"]
    lines = [f"# Bid watch report — {r['started']}", ""]
    blind = [s for s, v in h.items() if not v.get("not_scanned_this_run")
             and (not v["reachable"] or v.get("blind") or (not v["count"] and s != "dibbs"))]
    carried = [s for s, v in h.items() if v.get("not_scanned_this_run")]
    head = []
    if r["new"]:
        head.append(f"{len(r['new'])} NEW matching bids")
    if r["changed"]:
        head.append(f"{len(r['changed'])} changed (addenda/dates)")
    if blind:
        head.append("BLIND: " + ", ".join(blind))
    if carried:
        head.append("not scanned this run (previous results kept): " + ", ".join(carried))
    lines.append("**Headline:** " + ("; ".join(head) if head else "all sources scanned, no changes") + "\n")

    lines.append("## Source health\n")
    lines.append("| Source | Reachable | Credentials set | Logged in | Open bids seen | Site says | Matches | Last success | Errors |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for s, v in h.items():
        creds = ", ".join(f"{k}={'yes' if ok else 'NO'}" for k, ok in v["creds"].items()) or "n/a"
        tot = ", ".join(f"{k.replace('statewide ', '')} {n}" for k, n in (v.get("site_totals") or {}).items() if n is not None)
        note = ("NOT SCANNED THIS RUN; " if v.get("not_scanned_this_run") else "") \
            + ((f"BLIND this run, showing last good data from {v.get('last_success') or 'never'}; " if v.get("blind")
                else "PARTIAL this run (part of the source failed): earlier rows kept, none closed; ")
               if v.get("carried_forward") else "") \
            + (v['login_note'] or ('yes' if v['logged_in'] else 'no'))
        lines.append(f"| {s} | {'yes' if v['reachable'] else 'NO (' + v['reach_note'] + ')'} | {creds} | "
                     f"{note} | {v['count']} | {tot} | {v['matches']} | "
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
    open_m = [b for b in r["found"].values() if b.get("profiles") and not b.get("upcoming") and b["source"] != "dibbs"
              and _is_open(b)]
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
    if r.get("filed"):
        lines += ["", "## Filed into bid folders", ""] + [f"- {f}" for f in r["filed"]]
    errs = [(s, e) for s, v in h.items() for e in v["errors"]]
    if errs:
        lines += ["", "## Errors", ""] + [f"- {s}: {e}" for s, e in errs[:60]]
    return "\n".join(lines) + "\n"


# ---------------- --push: publish each cycle's results to the repo branch ----------------

PUSH_PATHS = ["bids/_watch/REPORT.md", "bids/_watch/open_bids.json", "bids/_watch/health.json",
              "bids/_watch/dibbs_state.json", "bids/_watch/dashboard", "bids/_watch/downloads"]
STATUS_FILE = DEBUG_DIR / "loop.status"  # gitignored heartbeat: pid, last cycle, last push result


def _git(*args: str, check: bool = True, timeout: int = 120) -> subprocess.CompletedProcess:
    """git in the repo; a held index.lock (another session committing at the same moment) is retried."""
    for i in range(6):
        r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0 or "index.lock" not in (r.stderr or ""):
            break
        time.sleep(3 * (i + 1))
    if check and r.returncode != 0:
        raise subprocess.CalledProcessError(r.returncode, r.args, r.stdout, r.stderr)
    return r


def _branch() -> str:
    return _git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def git_sync(note: str = "") -> str:
    """Before a cycle: bring in what the hourly workers pushed. Regenerated files that conflict resolve to
    upstream (ours are rebuilt right after). Never raises."""
    try:
        _git("fetch", "-q", "origin", _branch())
        _git("rebase", "-q", "-X", "ours", f"origin/{_branch()}")
        return "synced"
    except subprocess.CalledProcessError as e:
        try:
            _git("rebase", "--abort", check=False)
        except Exception:  # noqa: BLE001
            pass
        return f"sync failed: {(e.stderr or e.stdout)[-200:]}"
    except Exception as e:  # noqa: BLE001
        return f"sync failed: {type(e).__name__}"


MAX_PUSH_BYTES = 95 * 1024 * 1024  # GitHub refuses files over 100 MB, and one such commit would block every push


def _hold_back_large() -> list[str]:
    """Unstage any staged file over MAX_PUSH_BYTES (a huge drawing set, say): it stays on disk, the push goes on."""
    held = []
    for n in filter(None, _git("diff", "--cached", "--name-only", "-z", check=False).stdout.split("\0")):
        p = REPO / n
        if p.is_file() and p.stat().st_size > MAX_PUSH_BYTES:
            _git("reset", "-q", "--", n, check=False)
            held.append(n)
    return held


def git_push_results(when: str, extra_paths: list[str] | None = None) -> str:
    """After a cycle: rebuild dashboard data, commit the generated files, rebase onto upstream keeping OUR
    freshly generated versions on conflict, push with backoff. Returns a one-line result. Never raises."""
    try:
        subprocess.run([sys.executable, str(REPO / "scripts/build_dashboard_data.py")], cwd=REPO,
                       capture_output=True, text=True, timeout=300)
        _git("add", "-A", "--", *PUSH_PATHS, *(extra_paths or []))
        held = _hold_back_large()
        if _git("diff", "--cached", "--quiet", check=False).returncode == 0:
            return "nothing new to push" + (f" (held back {len(held)} file(s) over 95 MB: {held[:3]})" if held else "")
        trailer = os.environ.get("BIDWATCH_COMMIT_TRAILER", "Co-Authored-By: Claude <noreply@anthropic.com>").replace("\\n", "\n")
        _git("commit", "-q", "-m", f"bidwatch: live scan {when}\n\n{trailer}")
        br = _branch()
        last = ""
        for i in range(4):
            try:
                _git("fetch", "-q", "origin", br)
                # rebase: "theirs" = the commit being replayed = our regenerated files
                _git("rebase", "-q", "-X", "theirs", f"origin/{br}")
                _git("push", "-q", "origin", br)
                return f"pushed {_git('rev-parse', '--short', 'HEAD').stdout.strip()}" + \
                    (f" (held back {len(held)} file(s) over 95 MB: {held[:3]})" if held else "")
            except subprocess.CalledProcessError as e:
                last = (e.stderr or e.stdout or "")[-200:]
                _git("rebase", "--abort", check=False)
                time.sleep(2 ** (i + 1))
        return f"push FAILED after 4 tries: {last}"
    except Exception as e:  # noqa: BLE001
        return f"push FAILED: {type(e).__name__}: {str(e)[:150]}"


def ping(name: str, suffix: str = "", note: str = "") -> None:
    """Dead-man-switch ping (healthchecks.io style): env HC_PING_<NAME> holds the check URL. suffix "" = success,
    "/start", "/fail". Silent no-op when not configured; never raises."""
    url = os.environ.get(f"HC_PING_{name.upper()}")
    if not url:
        return
    try:
        req = urllib.request.Request(url.rstrip("/") + suffix, data=note[:9000].encode() or None,
                                     headers={"User-Agent": "BrownBisonBidWatch/2.0"})
        urllib.request.urlopen(req, timeout=10).read()
    except Exception:  # noqa: BLE001
        pass


def origin_health_age_min() -> float | None:
    """Minutes since the scan whose health.json is on origin (used by a failover host to stay idle while the
    primary is healthy)."""
    try:
        _git("fetch", "-q", "origin", _branch())
        raw = _git("show", f"origin/{_branch()}:bids/_watch/health.json").stdout
        import datetime as _dt
        t = _dt.datetime.fromisoformat(json.loads(raw)["checked_at"])
        return (_dt.datetime.now(_dt.timezone.utc) - t).total_seconds() / 60
    except Exception:  # noqa: BLE001
        return None


def _heartbeat(**kw) -> None:
    try:
        DEBUG_DIR.mkdir(parents=True, exist_ok=True)
        cur = load_json(STATUS_FILE, {})
        cur.update(kw, pid=os.getpid(), updated_at=iso())
        save_json(STATUS_FILE, cur)
    except Exception:  # noqa: BLE001
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval", type=int, default=60, help="minutes between scans in --loop")
    ap.add_argument("--sources", default=",".join(ALL_SOURCES))
    ap.add_argument("--health", action="store_true")
    ap.add_argument("--no-detail", action="store_true")
    ap.add_argument("--push", action="store_true",
                    help="after each scan: rebuild dashboard data, commit the generated files, rebase, push")
    ap.add_argument("--only-if-stale", type=int, default=0, metavar="MIN",
                    help="failover mode: do nothing unless origin's health.json is older than MIN minutes")
    ap.add_argument("--start-in", type=int, default=0,
                    help="minutes to wait before the first scan (space a restarted loop away from the hourly worker)")
    a = ap.parse_args()
    sources = [s for s in a.sources.split(",") if s in ALL_SOURCES]
    load_env_file()
    if "dibbs" in sources and not os.environ.get("BIDWATCH_ALLOW_DIBBS"):
        # DIBBS FAQ #45 (verified 2026-10-20): "VPNs, proxy servers, TOR nodes, cloud hosting services, and other
        # similar services or devices, mask the user's IP address and are, therefore, prohibited." DIBBS is read
        # ONLY from Luke's own machine (BIDWATCH_ALLOW_DIBBS=1 in its .env). Elsewhere its last rows are kept and
        # marked NOT SCANNED THIS RUN; SAM.gov carries part of DLA's RFQs meanwhile.
        sources.remove("dibbs")
        print("DIBBS skipped: cloud/proxy access is prohibited by the DIBBS user agreement (FAQ #45); "
              "set BIDWATCH_ALLOW_DIBBS=1 only on Luke's own computer", flush=True)
    if a.only_if_stale:
        age = origin_health_age_min()
        if age is not None and age < a.only_if_stale:
            print(f"[{iso()}] primary is healthy (last scan {age:.0f} min ago < {a.only_if_stale}); failover idle", flush=True)
            return 0
        print(f"[{iso()}] last scan {'unknown' if age is None else f'{age:.0f} min'} ago: failover scanning", flush=True)
    if a.health:
        load_env_file()
        for s, v in health_check(sources).items():
            print(f"{s:8} reachable={v['reachable']} ({v['reach_note']}) creds={v['creds']}")
        return 0
    if a.start_in > 0:
        print(f"[{iso()}] first scan in {a.start_in} min", flush=True)
        _heartbeat(cycle=0, next_at=iso(), interval_min=a.interval, note=f"first scan in {a.start_in} min")
        time.sleep(a.start_in * 60)
    import fcntl
    RUN_LOCK.parent.mkdir(parents=True, exist_ok=True)
    lock = open(RUN_LOCK, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print(f"[{iso()}] another scan holds {RUN_LOCK}; not starting a second one", flush=True)
        return 4
    cycle = 0
    while True:
        cycle += 1
        started = iso()
        sync = git_sync() if a.push else "no sync (--push not set)"
        ping("scan", "/start")
        try:
            filed = []
            r = scan(sources, enrich_details=not a.no_detail)
            filed = r.get("filed", [])
            print(REPORT_FILE.read_text().split("## Source health")[0].strip())
            ok = any(v["count"] for v in r["health"].values())
            # sources that returned nothing fresh this run (blind, carried forward, cool-down): exit 3 so a
            # scheduler/monitor sees a degraded run instead of a green one
            degraded = [s for s, v in r["health"].items() if not v.get("not_scanned_this_run")
                        and (v.get("carried_forward") or not v["reachable"] or (not v["count"] and s != "dibbs"))]
            logins = {s: v.get("login_note") for s, v in r["health"].items()}
        except Exception:  # noqa: BLE001 - never let the loop die
            traceback.print_exc()
            ok, logins, degraded = False, {}, ["scan crashed"]
        push = git_push_results(started, filed) if a.push else "not pushed (--push not set)"
        print(f"[{iso()}] cycle {cycle}: ok={ok} degraded={degraded} sync={sync} push={push} logins={logins}", flush=True)
        summary = f"ok={ok} degraded={degraded} push={push} logins={logins}"
        ping("scan", "" if ok and not degraded and not str(push).startswith("push FAILED") else "/fail", summary)
        for src in ("bidnet", "samgov", "bonfire", "dibbs"):
            if src in sources and ok and src not in degraded:
                ping(src, "", summary)
        _heartbeat(cycle=cycle, started=started, ok=ok, sync=sync, push=push, logins=logins,
                   next_at=iso() if not a.loop else None, interval_min=a.interval)
        if not a.loop:
            return (0 if not degraded else 3) if ok else 2
        time.sleep(max(5, a.interval) * 60)


if __name__ == "__main__":
    sys.exit(main())
