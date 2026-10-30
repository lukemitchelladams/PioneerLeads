"""Shared plumbing for the Brown Bison bid watcher: paths, credentials, retries, matching, state.

Credentials come ONLY from environment variables (or an optional env file outside the repo,
~/.brownbison/env, one KEY=VALUE per line). Nothing secret is ever written to the repo or printed.
"""
from __future__ import annotations

import datetime as dt
import functools
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[2]
WATCH_DIR = REPO / "bids" / "_watch"
PROFILES_FILE = WATCH_DIR / "watch_profiles.json"
WATCHLIST_FILE = WATCH_DIR / "watchlist.json"
OPEN_BIDS_FILE = WATCH_DIR / "open_bids.json"
HEALTH_FILE = WATCH_DIR / "health.json"
REPORT_FILE = WATCH_DIR / "REPORT.md"
DOWNLOAD_DIR = WATCH_DIR / "downloads"
DEBUG_DIR = WATCH_DIR / "debug"  # gitignored: screenshots + raw HTML when a parse or login fails

# Browser sessions (cookies) live OUTSIDE the repo so they are never committed.
STATE_HOME = Path(os.environ.get("BB_STATE_DIR", Path.home() / ".brownbison"))
SESSION_DIR = STATE_HOME / "sessions"
ENV_FILE = STATE_HOME / "env"
# One-time code for a portal's "confirm this new device" step (BidNet emails one on the first login from a
# new container). An operator or a session with Gmail access writes the code here; login() uses it once.
CODE_FILE = STATE_HOME / "bidnet_code"
# Written when a login stalled on the code prompt and nobody supplied a code in time. While it exists the
# scanner makes NO further password logins (each one would email a fresh code). Delete it when someone is
# ready to supply the code within the wait window.
CODE_NEEDED_MARKER = STATE_HOME / "bidnet_code_needed"
CODE_MARKER_TTL_H = 6  # a stale "waiting for a code" marker expires so the scanner tries again (one email per 6 h max)
# After BidNet serves its AWS WAF robot check, skip BidNet until this time (ISO UTC) and keep the last good data.
BIDNET_COOLDOWN_FILE = STATE_HOME / "bidnet_cooldown_until"
BIDNET_COOLDOWN_H = 2
# Time (ISO UTC) of the last FRESH BidNet password login that worked; written only then (a reused session is not a
# login). Fresh logins close together trip the robot check (2026-10-30 06:37Z: the 4th in ~6 h; 2 h apart passed
# three times, 3 h apart passed), so no password is submitted until BIDWATCH_BIDNET_LOGIN_GAP_H hours (env, default
# below; 0 = no gap) have passed since then. A scan inside the gap whose saved session expired skips BidNet.
BIDNET_LAST_LOGIN_FILE = STATE_HOME / "bidnet_last_login"
BIDNET_LOGIN_GAP_H = 3.0
RUN_LOCK = STATE_HOME / "bidwatch.lock"  # one scan at a time on a machine


class LoginBlocked(RuntimeError):
    """Login cannot proceed without outside help (emailed confirmation code, robot check). Never retried,
    so a portal is not hit three times and three code emails are not sent."""


class LoginDeferred(LoginBlocked):
    """A fresh password login held back on purpose (too soon after the last one): a deliberate skip, like a robot-check
    cool-down, not a fault. Never retried; the scan keeps the portal's earlier rows."""


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso(t: dt.datetime | None = None) -> str:
    return (t or now_utc()).isoformat(timespec="seconds")


def load_env_file() -> None:
    """Optional: read ~/.brownbison/env so a local machine can hold creds without exporting them."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def cred(name: str) -> str | None:
    v = os.environ.get(name)
    return v if v else None


def cred_status(names: list[str]) -> dict[str, bool]:
    """Which credential env vars are set. Never returns values."""
    return {n: bool(cred(n)) for n in names}


def retry(times: int = 3, base_delay: float = 5.0, exceptions: tuple = (Exception,)) -> Callable:
    """Exponential backoff: 5 s, 10 s, 20 s ... Re-raises the last error."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*a, **kw):
            last: Exception | None = None
            for i in range(times):
                try:
                    return fn(*a, **kw)
                except exceptions as e:  # noqa: PERF203
                    last = e
                    if i < times - 1:
                        time.sleep(base_delay * (2 ** i))
            assert last is not None
            raise last
        return wrapper
    return deco


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True, default=str))
    tmp.replace(path)


def slug(s: str, n: int = 80) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:n]


# ---------- matching ----------

def load_profiles() -> dict:
    return load_json(PROFILES_FILE, {"profiles": {}})["profiles"]


def _rx(word: str) -> re.Pattern:
    return re.compile(r"\b" + re.escape(word.lower()))


def match_profiles(text: str, profiles: dict | None = None) -> list[str]:
    """Return profile names whose keywords hit `text` (word-start match, so 'tree' != 'street').
    A profile's `exclude_keywords` veto the match (e.g. 'excavation', 'engineering services')."""
    profiles = profiles if profiles is not None else load_profiles()
    t = (text or "").lower()
    hits = []
    for name, p in profiles.items():
        kws = p.get("bidnet_keywords", [])
        if any(_rx(k).search(t) for k in kws) and not any(_rx(x).search(t) for x in p.get("exclude_keywords", [])):
            hits.append(name)
    return hits


# ---------- date + pre-bid extraction (used on detail pages and documents) ----------

MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec"
DATE_PATTERNS = [
    re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b"),
    re.compile(rf"\b({MONTHS})[a-z]*\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})\b", re.I),
    re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"),
]
_MON = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def parse_date(text: str) -> str | None:
    """First date in `text` as ISO yyyy-mm-dd, or None."""
    if not text:
        return None
    for i, rx in enumerate(DATE_PATTERNS):
        m = rx.search(text)
        if not m:
            continue
        try:
            if i == 0:
                mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                y = y + 2000 if y < 100 else y
            elif i == 1:
                mo, d, y = _MON[m.group(1).lower()[:3]], int(m.group(2)), int(m.group(3))
            else:
                y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            return dt.date(y, mo, d).isoformat()
        except (ValueError, KeyError):
            continue
    return None


PREBID_RX = re.compile(
    r"(pre[- ]?(bid|proposal|submittal|quote)\s*(conference|meeting|walk[- ]?through|site visit)?|"
    r"site\s+(visit|walk|inspection|tour)|walk[- ]?through|job\s*walk)", re.I)
MANDATORY_RX = re.compile(r"\bmandatory\b|\bshall attend\b|\bmust attend\b|\brequired to attend\b", re.I)
NOT_MANDATORY_RX = re.compile(r"\bnon[- ]?mandatory\b|\bnot mandatory\b|\boptional\b|\bnot required\b", re.I)


NONE_AFTER_RX = re.compile(r"^\s*(?:meeting|conference|walk(?:through)?|visit)?\s*[:\-–—]?\s*(none|n/?a\b|not applicable|"
                           r"no pre[- ]?(bid|proposal)|will not be held|not scheduled|not required for this)", re.I)
_BOUNDARY = re.compile(r"[.!?;]\s")


def _scope(flat: str, start: int, end: int, date_at: int | None) -> str:
    """The sentence holding the pre-bid phrase plus the sentence that finishes its date/attendance clause.
    Keeping 'optional'/'mandatory' detection inside this scope stops a word elsewhere in the paragraph
    (e.g. 'questions are optional') from flipping a MANDATORY walk to optional, or the reverse."""
    a = max(0, start - 100)
    prev = [m.end() for m in _BOUNDARY.finditer(flat, a, start)]
    a = prev[-1] if prev else a
    anchor = max(end, date_at or end)
    b = min(len(flat), anchor + 220)
    bounds = [m.start() for m in _BOUNDARY.finditer(flat, anchor, b)]
    if len(bounds) >= 2:
        b = bounds[1] + 1
    return flat[a:b]


def extract_prebid(text: str) -> dict | None:
    """Find the pre-bid meeting / site walk in free text. Returns {date, mandatory, quote} or None.
    mandatory is True / False / None (unknown). The quote is kept so a human can verify it.
    A phrase followed by 'None' / 'N/A' / 'will not be held' is skipped so a later real walk is found;
    a candidate with a date beats one without."""
    if not text:
        return None
    flat = re.sub(r"\s+", " ", text)
    cands = []
    for m in PREBID_RX.finditer(flat):
        if NONE_AFTER_RX.search(flat[m.end(): m.end() + 60]):
            continue
        ahead = flat[m.start(): m.end() + 260]
        date = parse_date(ahead)
        date_at = None
        if date:
            dm = re.search(r"\d{1,2}/\d{1,2}/\d{2,4}|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}", ahead, re.I)
            date_at = m.start() + dm.start() if dm else None
        scope = _scope(flat, m.start(), m.end(), date_at)
        if NOT_MANDATORY_RX.search(scope):
            mand = False
        elif MANDATORY_RX.search(scope):
            mand = True
        else:
            mand = None
        cands.append({"date": date, "mandatory": mand, "quote": scope.strip()[:400]})
    if not cands:
        return None
    # Prefer a mention that carries a date AND says whether attendance is mandatory (portal pages often repeat
    # the walk in a structured "Pre-Bidding Events" block after a bare first mention); earliest mention wins ties.
    return max(cands, key=lambda c: (c["date"] is not None, c["mandatory"] is not None, -cands.index(c)))


def days_until(iso_date: str | None) -> int | None:
    if not iso_date:
        return None
    try:
        return (dt.date.fromisoformat(iso_date[:10]) - dt.date.today()).days
    except ValueError:
        return None
