"""SAM.gov federal opportunities via the official Opportunities API (no browser login needed).

Pulls EVERYTHING still open (response deadline >= today) for:
  * place of performance in each profile state (Colorado for Brown Bison), all types:
    o = solicitation, k = combined synopsis/solicitation, p = presolicitation (UPCOMING),
    r = sources sought (UPCOMING), s = special notice;
  * each profile's PSC codes nationwide (Jones Bearing product buys).
Then filters locally by NAICS / PSC / keywords, so we spend few API calls.

Rate limits: SAM.gov allows ~10 requests/day for a personal key with no role and ~1,000/day for a
user with an entity role (Luke's account has the Brown Bison entity, so it should get 1,000). The
budget is tracked in bids/_watch/samgov_budget.json; set SAM_DAILY_BUDGET to override (default 900).
Env: SAM_API_KEY. Network: api.sam.gov.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from .common import WATCH_DIR, load_json, match_profiles, save_json

API = "https://api.sam.gov/opportunities/v2/search"
BUDGET_FILE = WATCH_DIR / "samgov_budget.json"
TYPES = "o,k,p,r,s"
UPCOMING_TYPES = {"Presolicitation", "Sources Sought", "Special Notice"}


class BudgetExhausted(RuntimeError):
    pass


def _spend(n: int = 1) -> None:
    cap = int(os.environ.get("SAM_DAILY_BUDGET", "900"))
    b = load_json(BUDGET_FILE, {})
    today = dt.date.today().isoformat()
    used = b.get(today, 0)
    if used + n > cap:
        raise BudgetExhausted(f"SAM.gov daily request budget reached ({used}/{cap})")
    save_json(BUDGET_FILE, {today: used + n})


def _get(params: dict, key: str) -> dict:
    _spend()
    url = f"{API}?{urllib.parse.urlencode({'api_key': key, **params})}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def fetch_open(key: str, extra: dict, max_records: int = 3000) -> list[dict]:
    today = dt.date.today()
    base = {
        "postedFrom": (today - dt.timedelta(days=364)).strftime("%m/%d/%Y"),
        "postedTo": today.strftime("%m/%d/%Y"),
        "rdlfrom": today.strftime("%m/%d/%Y"),
        "ptype": TYPES, "limit": 1000, **extra,
    }
    out, offset = [], 0
    while offset < max_records:
        data = _get({**base, "offset": offset}, key)
        batch = data.get("opportunitiesData", []) or []
        out += batch
        total = int(data.get("totalRecords") or 0)
        offset += len(batch)
        if not batch or offset >= total:
            break
    return out


def normalize(o: dict) -> dict:
    pop = o.get("placeOfPerformance") or {}
    return {
        "source": "samgov", "id": o.get("noticeId"), "title": o.get("title") or "",
        "sol": o.get("solicitationNumber"), "agency": o.get("fullParentPathName") or "",
        "type": o.get("type"), "upcoming": o.get("type") in UPCOMING_TYPES,
        "published": (o.get("postedDate") or "")[:10], "closing": (o.get("responseDeadLine") or "")[:10] or None,
        "naics": o.get("naicsCode"), "psc": o.get("classificationCode"),
        "set_aside": o.get("typeOfSetAsideDescription"),
        "state": (pop.get("state") or {}).get("code"), "city": (pop.get("city") or {}).get("name"),
        "url": o.get("uiLink"), "description_url": o.get("description"),
        "documents": [{"name": u.rsplit("/", 1)[-1], "url": u} for u in (o.get("resourceLinks") or [])],
    }


def _keep(rec: dict, prof: dict) -> bool:
    naics = {q["ncode"] for q in prof.get("samgov", []) if "ncode" in q}
    psc = {q["ccode"] for q in prof.get("samgov", []) if "ccode" in q}
    if rec.get("naics") in naics:
        return True
    if rec.get("psc") and any(str(rec["psc"]).startswith(p) for p in psc):
        return True
    return bool(match_profiles(rec["title"], {"x": prof}))


def collect(profiles: dict) -> tuple[dict, list[str]]:
    key = os.environ.get("SAM_API_KEY")
    if not key:
        return {}, ["SAM_API_KEY not set"]
    found, errors = {}, []
    for name, prof in profiles.items():
        queries = [{"state": s} for s in (prof.get("states") or [])]
        if not prof.get("states"):  # nationwide product profile: query by PSC
            queries = [{"ccode": q["ccode"]} for q in prof.get("samgov", []) if "ccode" in q]
        for q in queries:
            try:
                for o in fetch_open(key, q):
                    rec = normalize(o)
                    if not rec["id"] or not _keep(rec, prof):
                        continue
                    cur = found.setdefault(rec["id"], {**rec, "profiles": []})
                    if name not in cur["profiles"]:
                        cur["profiles"].append(name)
            except BudgetExhausted as e:
                errors.append(str(e))
                return found, errors
            except urllib.error.HTTPError as e:
                try:  # SAM.gov explains rejected parameters and rate limits in the JSON body (no key in it)
                    body = e.read(400).decode("utf-8", "ignore")
                except Exception:  # noqa: BLE001
                    body = ""
                errors.append(f"SAM.gov {q}: HTTP {e.code} {e.reason} {body.strip()[:200]}")
            except Exception as e:  # noqa: BLE001
                errors.append(f"SAM.gov {q}: {type(e).__name__}: {str(e)[:150]}")
    return found, errors


def check_notice(key: str, notice_id: str) -> dict | None:
    """Re-pull one watched notice (amendments change postedDate / deadline / resourceLinks)."""
    today = dt.date.today()
    data = _get({"noticeid": notice_id, "limit": 1,
                 "postedFrom": (today - dt.timedelta(days=364)).strftime("%m/%d/%Y"),
                 "postedTo": today.strftime("%m/%d/%Y")}, key)
    items = data.get("opportunitiesData") or []
    return normalize(items[0]) if items else None
