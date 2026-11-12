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
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from .common import WATCH_DIR, load_json, match_profiles, save_json

API = "https://api.sam.gov/opportunities/v2/search"
# the notice's full description text (the search API only links to it) and the entity register, both for the
# one-line brief of a NEW match (describe_notice / lookup_cage / brief_line below)
NOTICE_DESC_API = "https://api.sam.gov/prod/opportunities/v1/noticedesc"
ENTITY_API = "https://api.sam.gov/entity-information/v3/entities"
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


def _doc_name(url: str) -> str:
    """SAM.gov resource links end in '/<fileId>/download', so the last segment is 'download' for every file;
    naming documents by it made new amendments invisible to the diff. Use the file id instead."""
    parts = [p for p in url.rstrip("/").split("/") if p]
    if len(parts) >= 2 and parts[-1].lower() in ("download", "view"):
        return parts[-2]
    return parts[-1] if parts else url


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
        "documents": [{"name": _doc_name(u), "url": u} for u in (o.get("resourceLinks") or [])],
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
                    if q.get("state") and rec.get("state") and rec["state"] != q["state"]:
                        continue  # the API's state filter is loose; a profile state query keeps only that state
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


# ---------- one-line brief of a NEW match (2026-11-12: DLA SPRMM126QMJ99 "BEARING,BALL AND RO" took three manual API
# calls to learn what it was; the scanner now does that itself for new SAM.gov matches, see run.py) ----------

SET_ASIDES = [  # canonical phrase -> tolerant pattern; the earliest hit in the text wins
    ("TOTAL SMALL BUSINESS SET-ASIDE", r"TOTAL\s+SMALL\s+BUSINESS\s+SET[\s-]*ASIDE"),
    ("SERVICE-DISABLED VETERAN", r"SERVICE[\s-]*DISABLED\s+VETERAN"),
    ("8(A)", r"\b8\s*\(\s*A\s*\)"),
    ("HUBZONE", r"\bHUB\s*ZONE\b"),
    ("WOMEN-OWNED", r"\bWOM[AE]N[\s-]*OWNED\b"),
    ("UNRESTRICTED", r"\bUNRESTRICTED\b"),
]
NSN_RX = re.compile(r"\b(\d{4})-?(\d{2})-?(\d{3})-?(\d{4})\b")  # 3910-00-243-5401, also DLA's undashed 3910002435401
# "Cage _______ ref. no. ;70508 80080 PIECE 3X4X33X34;" : CAGE = 5 alnum after the ';', ref = the rest up to the next ';'
CAGE_REF_RX = re.compile(r"\bCAGE\b[^;]{0,60};\s*([A-Z0-9]{5})\s+([^;]+?)\s*;", re.I)
QTY_RX = re.compile(r"\b(\d[\d,]*)\s*(?:UI\s+)?EA\b")
NO_DRAWINGS_RX = re.compile(r"technical data (?:is|are) not available|drawings?\b[^.;]{0,80}?\bnot available", re.I)
QUALITY_RX = re.compile(r"(ISO[\s-]*9001)(?:[:\s-]*\d{4})?|(MIL-I-45208)[A-Z]?", re.I)
TAG_RX = re.compile(r"<[^>]+>")


def _redact(msg: str, key: str | None) -> str:
    return msg.replace(key, "***") if key else msg


def _note(errors: list | None, msg: str) -> None:
    """The module's error pattern (collect): one line into the caller's list; stderr when there is no list."""
    if errors is not None:
        errors.append(msg)
    else:
        print(f"SAM.gov: {msg}", file=sys.stderr, flush=True)


def _fetch_text(url: str, timeout: int = 60) -> str:
    """Default `fetch` for describe_notice / lookup_cage: one budgeted GET, the body as text."""
    _spend()
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")


def _err_text(e: Exception) -> str:
    if isinstance(e, urllib.error.HTTPError):
        try:  # SAM.gov explains the refusal in the JSON body (no key in it)
            body = e.read(400).decode("utf-8", "ignore")
        except Exception:  # noqa: BLE001
            body = ""
        return f"HTTP {e.code} {e.reason} {body.strip()[:200]}".strip()
    return f"{type(e).__name__}: {str(e)[:150]}"


def _clean_html(raw) -> str:
    """Tags out, entities decoded, whitespace collapsed. Accepts the noticedesc JSON ({"description": html}),
    an already-parsed dict, or bare HTML/text."""
    text = raw
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", "ignore")
    if isinstance(raw, str):
        text = raw
        try:
            data = json.loads(raw)
        except ValueError:
            data = None
        if isinstance(data, dict):
            raw = data
    if isinstance(raw, dict):
        text = raw.get("description") or ""
        if isinstance(text, dict):
            text = text.get("body") or text.get("text") or json.dumps(text)
    text = TAG_RX.sub(" ", re.sub(r"(?i)<\s*(br|/p|/div|/li|/tr)\s*/?>", "\n", str(text or "")))
    return " ".join(html.unescape(text).split())


def _title_words(s: str) -> str:
    keep = {"LLC", "LP", "LLP", "USA", "US", "DBA", "L.L.C.", "II", "III"}
    return " ".join(w if w.upper() in keep else w.capitalize() for w in (s or "").split())


def describe_notice(key: str, notice_id: str, fetch=None, errors: list | None = None) -> dict | None:
    """What a notice is, read from its description text (the noticedesc endpoint; one budgeted request).
    `fetch(url) -> str` replaces the default GET (tests). Returns None on any failure, never raises: a missing
    brief must not touch the scan. The failure goes to `errors` in collect()'s format (or stderr without a list)."""
    try:
        url = f"{NOTICE_DESC_API}?{urllib.parse.urlencode({'noticeid': notice_id, 'api_key': key})}"
        text = _clean_html((fetch or _fetch_text)(url))
        if not text:
            _note(errors, f"SAM.gov noticedesc {notice_id}: empty description")
            return None
        hits = [(m.start(), i, phrase) for i, (phrase, rx) in enumerate(SET_ASIDES)
                if (m := re.search(rx, text, re.I))]
        set_aside = min(hits)[2] if hits else None
        nsns, cage_refs, seen = [], [], set()
        for m in NSN_RX.finditer(text):
            n = "-".join(m.groups())
            if n not in seen:
                seen.add(n)
                nsns.append(n)
        for m in CAGE_REF_RX.finditer(text):
            pair = (m.group(1).upper(), " ".join(m.group(2).split()))
            if pair not in cage_refs:
                cage_refs.append(pair)
        qtys = []
        for m in QTY_RX.finditer(text):
            digits = m.group(1).replace(",", "")
            qtys.append(f"{int(digits):,} EA" if digits.isdigit() else f"{m.group(1)} EA")
            if len(qtys) == 5:
                break
        q = QUALITY_RX.search(text)
        quality = None
        if q:
            quality = "ISO 9001" if q.group(1) else "MIL-I-45208"
        return {
            "set_aside": set_aside, "nsns": nsns, "cage_refs": cage_refs, "quantities": qtys,
            "authorized_distributor_only": bool(re.search(r"authori[sz]ed\s+distributor", text, re.I)),
            "no_drawings": bool(NO_DRAWINGS_RX.search(text)),
            "higher_level_quality": quality, "excerpt": text[:300],
        }
    except Exception as e:  # noqa: BLE001 - best effort, never into the scan
        _note(errors, _redact(f"SAM.gov noticedesc {notice_id}: {_err_text(e)}", key))
        return None


def lookup_cage(key: str, cage: str, fetch=None, errors: list | None = None) -> dict | None:
    """Who a CAGE code is: {legal_name, city, state} from the entity register (one budgeted request), or None."""
    try:
        url = f"{ENTITY_API}?{urllib.parse.urlencode({'cageCode': cage, 'api_key': key})}"
        raw = (fetch or _fetch_text)(url)
        data = json.loads(raw) if isinstance(raw, (str, bytes, bytearray)) else raw
        ents = (data or {}).get("entityData") or []
        if not ents:
            _note(errors, f"SAM.gov entity {cage}: no registration found")
            return None
        reg = ents[0].get("entityRegistration") or {}
        addr = (ents[0].get("coreData") or {}).get("physicalAddress") or {}
        name = reg.get("legalBusinessName")
        if not name:
            _note(errors, f"SAM.gov entity {cage}: no legal name in the record")
            return None
        return {"legal_name": name, "city": addr.get("city"),
                "state": addr.get("stateOrProvinceCode") or addr.get("state")}
    except Exception as e:  # noqa: BLE001
        _note(errors, _redact(f"SAM.gov entity {cage}: {_err_text(e)}", key))
        return None


def brief_line(desc: dict | None, cages: dict | None = None) -> str:
    """One line for the operator, empty parts left out, e.g.
    "set-aside: total small business | NSN 3910-00-243-5401 | qty 334 EA, 1 EA | OEM CAGE 70508 American Metal
    Bearing Co (Garden Grove CA) ref 80080 PIECE 3X4X33X34 | authorized distributors only | no drawings | ISO 9001".
    `cages` = {cage: lookup_cage() result or None}."""
    desc, cages = desc or {}, cages or {}
    parts = []
    if desc.get("set_aside"):
        parts.append("set-aside: " + re.sub(r"\s*set-aside$", "", desc["set_aside"].lower()))
    if desc.get("nsns"):
        parts.append("NSN " + ", ".join(desc["nsns"]))
    if desc.get("quantities"):
        parts.append("qty " + ", ".join(desc["quantities"]))
    refs: dict[str, list[str]] = {}
    for cage, ref in desc.get("cage_refs") or []:
        refs.setdefault(cage, [])
        if ref and ref not in refs[cage]:
            refs[cage].append(ref)
    for cage, rs in refs.items():
        seg = f"OEM CAGE {cage}"
        ent = cages.get(cage) or {}
        if ent.get("legal_name"):
            seg += " " + _title_words(ent["legal_name"])
            where = " ".join(x for x in (_title_words(ent.get("city") or ""), (ent.get("state") or "").upper()) if x)
            if where:
                seg += f" ({where})"
        if rs:
            seg += " ref " + ", ".join(rs)
        parts.append(seg)
    if desc.get("authorized_distributor_only"):
        parts.append("authorized distributors only")
    if desc.get("no_drawings"):
        parts.append("no drawings")
    if desc.get("higher_level_quality"):
        parts.append(desc["higher_level_quality"])
    return " | ".join(parts)
