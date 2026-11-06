#!/usr/bin/env python3
"""Ship the saved BidNet session between machines, encrypted: Luke's Mac logs in, the cloud only reuses.

Why (2026-11-06): BidNet challenged 2 of 6 fresh password logins from the cloud with its robot check, and a session
idles out in under ~50 min while the container sleeps between hourly scans. So the Mac (residential IP, always on)
logs in and keeps the session warm (mac_session_feeder.py), and the cloud scanner, started with
BIDWATCH_BIDNET_NO_PASSWORD=1, never submits the form: it imports the session this script ships, or skips BidNet.

Scheme: the SAME `openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt -pass env:STATE_PASSPHRASE` the Actions
failover uses for its state.enc (.github/workflows/bidwatch-failover.yml), so a file either side writes the other can
read. The passphrase comes from STATE_PASSPHRASE (env or ~/.brownbison/env) and is never printed or written. The
plaintext is Playwright's storage state exactly as browser.py saves it (~/.brownbison/sessions/bidnet.json); it is
piped through openssl and never lands in the repo. The .enc is safe to commit to a PRIVATE branch or copy over scp.

    python3 scripts/bidwatch/session_sync.py export [OUT]   # default ops/session/bidnet-session.enc in this checkout
    python3 scripts/bidwatch/session_sync.py import IN      # decrypt, verify (JSON with cookies), install atomically, mode 600
    python3 scripts/bidwatch/session_sync.py status         # age, cookie count, longest-lived auth cookie, mode, last import
    python3 scripts/bidwatch/session_sync.py check          # open a browser with the saved session: alive / expired (never logs in)

The hourly scan calls import_if_new() before BidNet: BIDWATCH_SESSION_IMPORT=PATH (or run.py --import-session PATH) names
the file; in no-password mode the default path above is used when it exists. A file already imported (same bytes) is
left alone, so the locally refreshed cookies are not overwritten with an older copy.
macOS note: the system `openssl` is LibreSSL; if export fails with "unknown option" on -pbkdf2, `brew install openssl@3`
and set BIDWATCH_OPENSSL=$(brew --prefix openssl@3)/bin/openssl.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.bidwatch.common import (ENV_FILE, REPO, SESSION_DIR, STATE_HOME, bidnet_no_password,  # noqa: E402
                                     iso, load_env_file, load_json, save_json)

PASSPHRASE_ENV = "STATE_PASSPHRASE"
IMPORT_ENV = "BIDWATCH_SESSION_IMPORT"
ENC_ARGS = ["enc", "-aes-256-cbc", "-pbkdf2", "-iter", "200000"]  # identical to the failover workflow
MAGIC = b"Salted__"  # openssl enc -salt header: 8 bytes magic + 8 bytes salt, then the ciphertext
DEFAULT_ENC = REPO / "ops" / "session" / "bidnet-session.enc"
IMPORT_RECORD = STATE_HOME / "session_import.json"  # sha256 of the last file installed, when, how many cookies
# cookies that carry the login (BidNet: JSESSIONID, Shibboleth/SAML single sign-on, the AWS WAF token)
AUTH_COOKIE_RX = re.compile(r"sess|auth|token|login|shib|saml|idp|sso|remember", re.I)


class SyncError(RuntimeError):
    """Refused: the old saved session is untouched. The message never carries the passphrase or a cookie value."""


def session_path() -> Path:
    return SESSION_DIR / "bidnet.json"


def passphrase() -> str:
    load_env_file()
    pw = os.environ.get(PASSPHRASE_ENV)
    if not pw:
        raise SyncError(f"{PASSPHRASE_ENV} not set (environment or {ENV_FILE}); it never goes in the repo or in chat")
    return pw


def openssl_bin() -> str:
    return os.environ.get("BIDWATCH_OPENSSL") or "openssl"


def _openssl(args: list[str], data: bytes) -> bytes:
    """Run openssl enc with the passphrase passed through the environment (as the workflow does), data on stdin."""
    env = {**os.environ, PASSPHRASE_ENV: passphrase()}
    try:
        r = subprocess.run([openssl_bin(), *ENC_ARGS, *args, "-pass", f"env:{PASSPHRASE_ENV}"], input=data,
                           capture_output=True, env=env, timeout=120)
    except FileNotFoundError:
        raise SyncError(f"{openssl_bin()} not found: install openssl or set BIDWATCH_OPENSSL=/path/to/openssl") from None
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "ignore")
        lines = err.strip().splitlines()
        msg = " ".join((lines[-1] if lines else f"exit {r.returncode}").split())[:160]
        if "bad decrypt" in err:  # OpenSSL 3 prints a provider trace around it; the cause is the only useful part
            msg = "bad decrypt (wrong passphrase or a damaged file)"
        elif "unknown option" in err.lower() or "unrecognized" in err.lower():
            msg += " (macOS LibreSSL lacks -pbkdf2: brew install openssl@3 and set BIDWATCH_OPENSSL to its openssl)"
        raise SyncError(f"openssl failed: {msg}")
    return r.stdout


def encrypt(plain: bytes) -> bytes:
    return _openssl(["-salt"], plain)


def decrypt(blob: bytes) -> bytes:
    if not blob.startswith(MAGIC):
        raise SyncError("not an openssl enc file (no Salted__ header): garbage, truncated, or never encrypted")
    return _openssl(["-d"], blob)


def validate(plain: bytes) -> dict:
    """Accept only what Playwright saves: a JSON object with a non-empty cookies list. A wrong passphrase, a damaged
    file or any other document is refused before it can replace the saved session."""
    try:
        st = json.loads(plain.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        raise SyncError(f"decrypted data is not JSON ({type(e).__name__}): wrong passphrase or a damaged file") from None
    cookies = st.get("cookies") if isinstance(st, dict) else None
    if not isinstance(cookies, list) or not cookies or not all(isinstance(c, dict) and c.get("name") for c in cookies):
        raise SyncError("decrypted JSON is not a browser storage state with cookies")
    return st


def export(out: Path | None = None) -> Path:
    """Encrypt the saved session to `out` (atomic, mode 600). A torn or empty session file is never shipped."""
    src = session_path()
    if not src.is_file():
        raise SyncError(f"no saved BidNet session at {src}: nothing to export (log in or run the feeder first)")
    plain = src.read_bytes()
    validate(plain)
    out = Path(out) if out else DEFAULT_ENC
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + f".{os.getpid()}.tmp")
    tmp.write_bytes(encrypt(plain))
    os.chmod(tmp, 0o600)
    os.replace(tmp, out)
    return out


def import_(src: Path) -> dict:
    """Decrypt `src`, verify it, install it as the saved session (atomic, mode 600) and record what was installed.
    On any failure the old saved session stays as it was."""
    src = Path(src)
    if not src.is_file():
        raise SyncError(f"{src}: no such file")
    blob = src.read_bytes()
    plain = decrypt(blob)
    st = validate(plain)
    dst = session_path()
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(f".{os.getpid()}.tmp")  # same shape as PortalSession.save: never a torn file
    tmp.write_bytes(plain)
    os.chmod(tmp, 0o600)
    os.replace(tmp, dst)
    rec = {"imported_at": iso(), "source": str(src), "sha256": hashlib.sha256(blob).hexdigest(),
           "file_dated": iso(dt.datetime.fromtimestamp(src.stat().st_mtime, dt.timezone.utc)), "cookies": len(st["cookies"])}
    save_json(IMPORT_RECORD, rec)
    return rec


def import_source() -> Path | None:
    """The file the scan imports: BIDWATCH_SESSION_IMPORT, else (no-password mode only) the default when it exists."""
    p = os.environ.get(IMPORT_ENV)
    if p:
        return Path(p).expanduser()
    return DEFAULT_ENC if bidnet_no_password() and DEFAULT_ENC.is_file() else None


def import_if_new() -> str | None:
    """Called by the scan before BidNet. Installs the synced file when its bytes differ from the last import; returns a
    one-line note for the health table, or None when no file is configured. Never raises."""
    src = import_source()
    if src is None:
        return None
    try:
        if not src.is_file():
            return f"synced session file not found: {src}"
        digest = hashlib.sha256(src.read_bytes()).hexdigest()
        rec = load_json(IMPORT_RECORD, {})
        if rec.get("sha256") == digest:
            return f"synced session unchanged since its import at {rec.get('imported_at')} (file dated {rec.get('file_dated')})"
        rec = import_(src)
        return f"synced session imported: {rec['cookies']} cookies, file dated {rec['file_dated']}"
    except SyncError as e:
        return f"synced session REFUSED ({e}); the saved session is untouched"
    except Exception as e:  # noqa: BLE001 - a sync problem must never stop the scan
        return f"synced session import failed: {type(e).__name__}: {str(e)[:120]}"


def status() -> dict:
    """Facts about the saved session without opening a browser. Values only, never a cookie's content."""
    src = session_path()
    out: dict = {"session_file": str(src), "no_password_mode": "on" if bidnet_no_password() else "off",
                 "import_file": str(import_source() or "none configured")}
    if not src.is_file():
        out["saved"] = "no saved session"
        cookies: list = []
    else:
        out["saved_age_min"] = round((time.time() - src.stat().st_mtime) / 60)
        try:
            cookies = validate(src.read_bytes())["cookies"]
        except SyncError as e:
            out["problem"], cookies = str(e), []
    out["cookies"] = len(cookies)
    auth = [c for c in cookies if AUTH_COOKIE_RX.search(c.get("name") or "") and (c.get("expires") or -1) > 0]
    if auth:
        c = max(auth, key=lambda c: c["expires"])
        out["auth_cookie"] = c["name"]
        out["auth_cookie_expires"] = iso(dt.datetime.fromtimestamp(c["expires"], dt.timezone.utc))
    elif cookies:
        out["auth_cookie"] = "none with an expiry date (session cookies live as long as BidNet keeps the session)"
    rec = load_json(IMPORT_RECORD, {})
    if rec:
        out["last_import"] = f"{rec.get('imported_at')} from {rec.get('source')} ({rec.get('cookies')} cookies)"
    ka = load_json(STATE_HOME / "keepalive.json", {})
    if ka:
        out["keepalive"] = f"{ka.get('state')} at {ka.get('at')}"
    return out


def check() -> bool:
    """A real page load with the saved session; never a login. The refreshed cookies are saved when alive."""
    from scripts.bidwatch import keepalive  # browser only here, so status/export/import need none
    return keepalive.session_alive()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("export").add_argument("out", nargs="?", default=None)
    sub.add_parser("import").add_argument("src")
    sub.add_parser("status")
    sub.add_parser("check")
    a = ap.parse_args(argv)
    load_env_file()
    try:
        if a.cmd == "export":
            out = export(Path(a.out) if a.out else None)
            st = status()
            print(f"exported {st['cookies']} cookies (saved {st.get('saved_age_min', '?')} min ago) to {out}")
        elif a.cmd == "import":
            rec = import_(Path(a.src))
            print(f"installed {rec['cookies']} cookies into {session_path()} (file dated {rec['file_dated']})")
        elif a.cmd == "status":
            for k, v in status().items():
                print(f"{k}: {v}")
        elif a.cmd == "check":
            alive = check()
            print("alive: BidNet shows the saved session logged in (refreshed cookies saved)" if alive
                  else "expired: BidNet does not recognise the saved session (no login attempted)")
            return 0 if alive else 1
    except SyncError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 3 if a.cmd == "import" else 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
