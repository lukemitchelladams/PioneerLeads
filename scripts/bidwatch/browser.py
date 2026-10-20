"""Logged-in browser sessions that survive between runs and re-login when they expire.

Each portal gets a PortalSession. It:
  * loads saved cookies from ~/.brownbison/sessions/<portal>.json (outside the repo),
  * checks whether the session is still logged in (portal-specific check),
  * logs in again with env-var credentials when it is not, retrying with backoff,
  * saves the refreshed cookies after every successful login and at close,
  * on any failure, saves a screenshot + HTML to bids/_watch/debug/ so selectors can be fixed.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

from .common import DEBUG_DIR, SESSION_DIR, LoginBlocked, iso, slug

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36 BrownBisonBidWatch/2.0"


def chromium_path() -> str | None:
    for cand in [os.environ.get("BROWNBISON_CHROMIUM"), "/opt/pw-browsers/chromium"]:
        if cand and Path(cand).exists():
            return str(Path(cand).resolve())
    return None


def _scrub(text: str, secrets) -> str:
    """Mask credential values that an error message might echo (the login note is committed in health.json)."""
    for v in secrets or ():
        if v and len(v) >= 4:
            text = text.replace(v, "***")
    return text


class Browser:
    """One Chromium for the whole scan; each portal gets its own context (cookie jar)."""

    def __init__(self, headless: bool = True):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        exe = chromium_path()
        kw = {"headless": headless}
        if exe:
            kw["executable_path"] = exe
        self.browser = self._pw.chromium.launch(**kw)

    def close(self) -> None:
        try:
            self.browser.close()
        finally:
            self._pw.stop()


class PortalSession:
    def __init__(self, browser: Browser, name: str,
                 login_fn: Callable | None = None, is_logged_in_fn: Callable | None = None,
                 cred_names: tuple[str, str] | None = None):
        self.name = name
        self.state_path = SESSION_DIR / f"{slug(name)}.json"
        kw = {"user_agent": UA, "accept_downloads": True, "viewport": {"width": 1400, "height": 1000}}
        if self.state_path.exists():
            kw["storage_state"] = str(self.state_path)
        try:
            self.ctx = browser.browser.new_context(**kw)
        except Exception:  # noqa: BLE001 - unreadable/corrupt saved session: start clean, ensure_login re-logs
            kw.pop("storage_state", None)
            self.ctx = browser.browser.new_context(**kw)
        self.ctx.set_default_timeout(45000)
        self.page = self.ctx.new_page()
        self.login_fn = login_fn
        self.is_logged_in_fn = is_logged_in_fn
        self.cred_names = cred_names
        self.logged_in = False
        self.login_note = "no login configured"

    # -- credentials --
    def creds(self) -> tuple[str, str] | None:
        if not self.cred_names:
            return None
        u, p = os.environ.get(self.cred_names[0]), os.environ.get(self.cred_names[1])
        return (u, p) if u and p else None

    def ensure_login(self, attempts: int = 3) -> bool:
        """Reuse the saved session if it is still valid; otherwise log in again (with retries)."""
        if not self.login_fn:
            return False
        creds = self.creds()
        if not creds:
            self.login_note = f"{self.cred_names[0]}/{self.cred_names[1]} not set" if self.cred_names else "no creds"
            return False
        try:
            if self.is_logged_in_fn and self.is_logged_in_fn(self.page):
                self.logged_in, self.login_note = True, "session reused"
                return True
        except Exception:  # noqa: BLE001 - a failed check just means we log in again
            pass
        import time
        last = ""
        for i in range(attempts):
            try:
                self.login_fn(self.page, *creds)
                if not self.is_logged_in_fn or self.is_logged_in_fn(self.page):
                    self.logged_in = True
                    self.login_note = f"logged in (attempt {i + 1})" + (f"; previous attempt: {last}" if last else "")
                    self.save()
                    return True
                last = "login submitted but logged-in check failed"
            except LoginBlocked as e:
                self.debug_dump("login-blocked")
                self.logged_in, self.login_note = False, f"login BLOCKED: {e}"
                return False
            except Exception as e:  # noqa: BLE001
                # the note lands in health.json (committed): never let a credential ride along in an error text
                last = _scrub(f"{type(e).__name__}: {e}", creds)[:160]
            self.debug_dump(f"login-fail-{i + 1}")
            time.sleep(5 * (2 ** i))
        self.logged_in, self.login_note = False, f"login FAILED after {attempts} tries: {last}"
        return False

    def save(self) -> None:
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        try:
            # atomic: two runs (hourly scan + a test) can save at the same moment; never leave a torn file
            tmp = self.state_path.with_suffix(f".{os.getpid()}.tmp")
            self.ctx.storage_state(path=str(tmp))
            os.chmod(tmp, 0o600)
            os.replace(tmp, self.state_path)
        except Exception:  # noqa: BLE001
            pass

    def debug_dump(self, tag: str) -> str | None:
        try:
            DEBUG_DIR.mkdir(parents=True, exist_ok=True)
            base = DEBUG_DIR / f"{slug(self.name)}-{tag}-{iso().replace(':', '')}"
            self.page.screenshot(path=str(base) + ".png", full_page=True)
            Path(str(base) + ".html").write_text(self.page.content())
            return str(base)
        except Exception:  # noqa: BLE001
            return None

    def close(self) -> None:
        if self.logged_in:
            self.save()
        self.ctx.close()
