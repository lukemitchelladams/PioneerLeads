#!/usr/bin/env python3
"""Luke's Mac feeds the cloud scanner its BidNet session: log in HERE (residential IP), keep it warm, ship it.

Why (2026-11-06): BidNet's robot check hits fresh password logins from the cloud, and a session idles out in under
~50 min while the cloud container sleeps. From Luke's own Mac a login passes, and a logged-in page load every
15 minutes keeps the session alive. The cloud scanner runs with BIDWATCH_BIDNET_NO_PASSWORD=1 and only reuses what
this loop ships (session_sync.py). Documented in docs/bidwatch.md, "Mac-fed BidNet session". Not for cloud use.

Every tick (default 900 s):
  1. keepalive.check_once(): a logged-in page load with the saved session, never a password. Skipped while a scan on
     this Mac holds the run lock or BidNet is in a robot-check cool-down.
  2. Expired: a normal PortalSession login with BIDNET_USER/BIDNET_PASS (env or ~/.brownbison/env). BidNet's emailed
     confirmation code is read from the mailbox (BIDNET_CODE_IMAP_PASS) or from `set_code.py <code>` run in another
     terminal while the browser waits on the prompt; a robot check starts the usual cool-down and the tick ends; the
     fresh-login gap (BIDWATCH_BIDNET_LOGIN_GAP_H) applies here as everywhere.
  3. Alive or just logged in: session_sync.py export -> OUT (default ops/session/bidnet-session.enc in this checkout),
     then BIDWATCH_SESSION_PUSH_CMD, a shell command run in the repo with $BIDWATCH_SESSION_FILE = OUT, e.g.
       git add ops/session/bidnet-session.enc && git commit -qm "bidnet session" && git pull -q --rebase && git push -q
       scp -p "$BIDWATCH_SESSION_FILE" user@host:.brownbison/sessions/bidnet-session.enc

    python3 scripts/bidwatch/mac_session_feeder.py --once
    python3 scripts/bidwatch/mac_session_feeder.py --every 900 [--out PATH]      # foreground loop (launchd / nohup)
Status: ~/.brownbison/session_feeder.json (last tick, state, export, push result).
Refuses to start with BIDWATCH_BIDNET_NO_PASSWORD set: that flag belongs on the machines this one feeds.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.bidwatch import bidnet, keepalive, session_sync  # noqa: E402
from scripts.bidwatch.browser import Browser, PortalSession  # noqa: E402
from scripts.bidwatch.common import NO_PASSWORD_ENV, REPO, STATE_HOME, bidnet_no_password, iso, load_env_file  # noqa: E402

STATUS_FILE = STATE_HOME / "session_feeder.json"
PUSH_CMD_ENV = "BIDWATCH_SESSION_PUSH_CMD"


def _status(state: str, **extra) -> dict:
    st = {"at": iso(), "state": state, **extra}
    try:
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATUS_FILE.write_text(json.dumps(st, indent=1))
    except OSError:
        pass
    return st


def login_fresh() -> tuple[bool, str]:
    """The ordinary login path (saved session first, then the password with the code and robot-check handling)."""
    br = Browser()
    try:
        ses = PortalSession(br, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
        try:
            return ses.ensure_login(), ses.login_note
        finally:
            ses.close()  # saves the session when logged in
    finally:
        br.close()


def push(out: Path) -> str:
    cmd = os.environ.get(PUSH_CMD_ENV)
    if not cmd:
        return f"exported only ({PUSH_CMD_ENV} not set)"
    try:
        r = subprocess.run(cmd, shell=True, cwd=REPO, env={**os.environ, "BIDWATCH_SESSION_FILE": str(out)},
                           capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return "push FAILED: timed out after 300 s"
    tail = " ".join((r.stdout + r.stderr).split())[-200:]
    return "pushed" if r.returncode == 0 else f"push FAILED (exit {r.returncode}): {tail}"


def tick(out: Path | None = None) -> dict:
    ka = keepalive.check_once()
    state = ka["state"]
    if state.startswith("skipped") or state == "error":
        return _status(state, note=ka.get("note") or ka.get("until") or "")
    note = ""
    if state != "alive":
        ok, note = login_fresh()
        if not ok:
            return _status(f"not logged in: {note}")  # BLOCKED / deferred: nothing shipped, next tick tries again
        state = "logged in"
    try:
        path = session_sync.export(out)
    except session_sync.SyncError as e:
        return _status(f"{state}; export REFUSED: {e}")
    return _status(f"{state}; exported", exported=str(path), push=push(path), note=note)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--every", type=int, default=900, help="seconds between ticks (default 900 = 15 min)")
    ap.add_argument("--out", default=None, help=f"encrypted file to write (default {session_sync.DEFAULT_ENC})")
    a = ap.parse_args(argv)
    load_env_file()
    if bidnet_no_password():
        print(f"{NO_PASSWORD_ENV} is set: this machine would never log in. Unset it here; it belongs on the cloud scanner.")
        return 2
    if not (os.environ.get(bidnet.CREDS[0]) and os.environ.get(bidnet.CREDS[1])):
        print(f"{bidnet.CREDS[0]}/{bidnet.CREDS[1]} not set (environment or ~/.brownbison/env)")
        return 2
    try:
        session_sync.passphrase()
    except session_sync.SyncError as e:
        print(str(e))
        return 2
    out = Path(a.out).expanduser() if a.out else None
    while True:
        try:
            st = tick(out)
        except Exception as e:  # noqa: BLE001 - a bad tick must never end the feeder
            st = _status("error", note=" ".join(f"{type(e).__name__}: {e}".split())[:160])
        print(f"[{st['at']}] {st['state']}" + (f" | {st['push']}" if st.get("push") else ""), flush=True)
        if a.once:
            return 0 if st["state"].endswith("exported") else 1
        time.sleep(max(60, a.every))


if __name__ == "__main__":
    sys.exit(main())
