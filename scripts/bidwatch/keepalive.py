#!/usr/bin/env python3
"""Keep the saved BidNet session warm between hourly scans, so scans reuse it instead of logging in again.

Why: BidNet drops an idle session in under an hour, so almost every hourly scan had to submit the login form,
and fresh logins are what trip BidNet's robot check (2026-10-28 23:36Z, 2026-10-29 16:37Z, 2026-10-30 06:37Z).
A logged-in page load every ~15 minutes keeps the session alive with no login at all.

Rules it keeps:
  * never submits the login form or a password: if the session has expired it only records that, and the
    next scan logs in, or skips BidNet until BIDWATCH_BIDNET_LOGIN_GAP_H hours (default 3) have passed since
    the last fresh login (the status then says until when); in no-password mode (BIDWATCH_BIDNET_NO_PASSWORD=1)
    no scan logs in either: the status says it waits for a session synced from Luke's Mac (session_sync.py);
  * skips a tick while a scan holds the run lock, and never holds that lock itself (a held lock would make
    the hourly scan skip its whole run);
  * probes through a robot-check cool-down (reuse only, never a login): a saved session left alone for the 2 h
    cool-down idles out, and the next scan then needs the fresh login that trips the robot check (2026-11-06
    15:41Z, a watched bid's tab was challenged mid-scan). It skips only when there is no saved session file at
    all, and a challenged probe is logged as "probe challenged (cool-down until ...)" without starting or
    extending a cool-down from here.

    python3 scripts/bidwatch/keepalive.py --once        # one check, prints the result
    python3 scripts/bidwatch/keepalive.py --ensure      # start the background keeper if it is not running
    python3 scripts/bidwatch/keepalive.py --every 900   # run in the foreground, one check every 900 s
Status: ~/.brownbison/keepalive.json (last check, state). PID: ~/.brownbison/keepalive.pid.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.bidwatch import bidnet  # noqa: E402
from scripts.bidwatch.browser import Browser, PortalSession  # noqa: E402
from scripts.bidwatch.common import RUN_LOCK, SESSION_DIR, STATE_HOME, bidnet_no_password, iso  # noqa: E402

PID_FILE = STATE_HOME / "keepalive.pid"
STATUS_FILE = STATE_HOME / "keepalive.json"
LOG_FILE = STATE_HOME / "keepalive.log"
SESSION_FILE = SESSION_DIR / "bidnet.json"  # the saved session PortalSession(br, "bidnet") reuses


def _scan_running() -> bool:
    RUN_LOCK.parent.mkdir(parents=True, exist_ok=True)
    with open(RUN_LOCK, "a") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return True
        fcntl.flock(f, fcntl.LOCK_UN)
    return False


def _status(state: str, **extra) -> dict:
    st = {"at": iso(), "state": state, **extra}
    try:
        old = json.loads(STATUS_FILE.read_text())
    except (OSError, ValueError):
        old = {}
    if state == "alive":
        st["last_alive"] = st["at"]
    elif old.get("last_alive"):
        st["last_alive"] = old["last_alive"]
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(st, indent=1))
    return st


def _challenged(page) -> bool:
    """The page the probe landed on is BidNet's robot check, not a BidNet page."""
    try:
        html = bidnet._content(page)
    except Exception:  # noqa: BLE001
        return False
    return bool(bidnet.BOT_RX.search(html)) and not bidnet.total_count(html)


def probe() -> str:
    """One page load with the saved BidNet session and no login function (this process can never submit a password):
    "alive" when BidNet still shows us logged in (the refreshed cookies are saved then; that is the keep-alive),
    "expired" when it shows the login window, "challenged" when it served its robot check instead of a page. A
    challenged probe starts no cool-down: that is the scan's call, and this was a page load, not a login."""
    br = Browser()
    try:
        ses = PortalSession(br, "bidnet")
        try:
            try:
                alive = bidnet.is_logged_in(ses.page)
            except bidnet.Challenged:
                return "challenged"
            if alive:
                ses.logged_in = True  # close() then saves the refreshed cookies
                return "alive"
            return "challenged" if _challenged(ses.page) else "expired"
        finally:
            ses.close()
    finally:
        br.close()


def session_alive() -> bool:
    """True when the saved session is still logged in (one probe, never a login). Also behind session_sync.py check."""
    return probe() == "alive"


def expired_state() -> str:
    """What happens next after an expired session, for the status line."""
    if bidnet_no_password():
        return "expired: no-password mode, no scan logs in; waiting for a session synced from the Mac (session_sync.py import)"
    until = bidnet.login_deferred_until()
    return f"expired: fresh login deferred until {until}" if until else "expired: next scan logs in"


def check_once() -> dict:
    until = bidnet.cooldown_until()
    if until and not SESSION_FILE.exists():
        return _status("skipped: robot-check cool-down and no saved session to keep warm", until=until)
    if _scan_running():
        return _status("skipped: scan running")
    try:
        state = probe()
    except Exception as e:  # noqa: BLE001
        return _status("error", note=" ".join(f"{type(e).__name__}: {e}".split())[:160])
    if state == "alive":
        return _status("alive")
    if state == "challenged":
        # BidNet's robot check instead of the page: never start or extend a cool-down from here (a probe is not a
        # login, and a cool-down that stops the probes is what let the session idle out on 2026-11-06)
        until = bidnet.cooldown_until()
        if until:
            return _status(f"probe challenged (cool-down until {until})", until=until)
        return _status("probe challenged (no cool-down started here)")
    return _status(expired_state())


def running_pid() -> int | None:
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)
        return pid
    except (OSError, ValueError):
        return None


def ensure(every: int) -> int:
    pid = running_pid()
    if pid:
        print(f"keepalive already running (pid {pid})")
        return 0
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log = open(LOG_FILE, "a")
    p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--every", str(every)],
                         stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                         start_new_session=True, cwd=str(Path(__file__).resolve().parents[2]))
    print(f"keepalive started (pid {p.pid}, every {every}s)")
    return 0


def loop(every: int) -> int:
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))
    try:
        while True:
            try:
                st = check_once()
            except Exception as e:  # noqa: BLE001 - a bad tick must never end the keeper
                st = _status("error", note=" ".join(f"{type(e).__name__}: {e}".split())[:160])
            print(f"[{st['at']}] {st['state']}", flush=True)
            time.sleep(every)
    finally:
        try:
            if PID_FILE.read_text().strip() == str(os.getpid()):
                PID_FILE.unlink()
        except OSError:
            pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--ensure", action="store_true")
    ap.add_argument("--every", type=int, default=900)
    a = ap.parse_args()
    if a.once:
        print(json.dumps(check_once()))
        return 0
    if a.ensure:
        return ensure(a.every)
    return loop(a.every)


if __name__ == "__main__":
    sys.exit(main())
