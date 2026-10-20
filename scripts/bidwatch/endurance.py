#!/usr/bin/env python3
"""BidNet stay-logged-in endurance test: proves the scanner keeps (or recovers) its login for an hour+.

    python3 scripts/bidwatch/endurance.py --minutes 66 --interval 6

Every check starts a NEW browser from the saved session file, exactly like each hourly production run:
  1. ensure_login(): reuse the saved session, or log in again with BIDNET_USER/BIDNET_PASS (code prompt handled
     by bidnet.login: BIDNET_CODE / ~/.brownbison/bidnet_code / IMAP when configured);
  2. new-bid poll: page 1 of the statewide BUYER and AGGREGATE lists (newest first); IDs not seen before = NEW;
  3. document access: open a watched bid's 'Documents & Items' tab and count the attachment links;
  4. save the session back to disk.
Forced expiries prove recovery: at check 4 the site session cookies are deleted (app-session timeout); at check 8
every BidNet session cookie incl. the Shibboleth IdP session is deleted (full SSO expiry -> password login).
A check PASSES when logged in, the list parsed rows, and the documents tab listed >= 1 attachment.
Results: bids/_watch/debug/endurance.jsonl (one line per check) and bids/_watch/ENDURANCE.md (summary,
rewritten after every check so a killed container still leaves evidence). Never prints credentials.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.bidwatch import bidnet  # noqa: E402
from scripts.bidwatch.browser import Browser, PortalSession  # noqa: E402
from scripts.bidwatch.common import (  # noqa: E402
    DEBUG_DIR, OPEN_BIDS_FILE, WATCH_DIR, iso, load_env_file, load_json,
)

LOG = DEBUG_DIR / "endurance.jsonl"
SUMMARY = WATCH_DIR / "ENDURANCE.md"
DOC_BID_URL = ("https://www.bidnetdirect.com/colorado/solicitations/open-bids/On-Call-Commercial-Plumbing-Services/"
               "0000438328?purchasingGroupId=8409951&origin=1")  # Littleton RFQ 21-26: 4 attachments
APP_SESSION = {("www.bidnetdirect.com", "JSESSIONID"), ("www.bidnetdirect.com", "mets.AuthenticationMode"),
               ("www.bidnetdirect.com", "_afl1")}
SSO_SESSION = APP_SESSION | {("idp.bidnetdirect.com", "JSESSIONID"), ("idp.bidnetdirect.com", "shib_idp_session"),
                             ("idp.bidnetdirect.com", "org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE")}


def expire(ses: PortalSession, which: set) -> int:
    """Delete the named cookies from the live context (simulates the server timing the session out)."""
    keep = [c for c in ses.ctx.cookies() if (c["domain"].lstrip("."), c["name"]) not in which
            and not (c["domain"].lstrip(".") == "idp.bidnetdirect.com" and which is SSO_SESSION
                     and c["name"].startswith("org.springframework"))]
    dropped = len(ses.ctx.cookies()) - len(keep)
    ses.ctx.clear_cookies()
    ses.ctx.add_cookies(keep)
    ses.save()
    return dropped


def one_check(n: int, seen: set, force: str | None) -> dict:
    rec: dict = {"check": n, "at": iso(), "forced": force}
    t0 = time.time()
    br = Browser()
    try:
        ses = PortalSession(br, "bidnet", bidnet.login, bidnet.is_logged_in, bidnet.CREDS)
        try:
            if force:
                ses.page.goto(bidnet.BASE + "/colorado", wait_until="domcontentloaded")
                rec["cookies_deleted"] = expire(ses, SSO_SESSION if force == "sso" else APP_SESSION)
            ok = ses.ensure_login()
            rec["logged_in"], rec["login_note"] = ok, ses.login_note
            # new-bid poll: page 1 of both statewide tabs, newest first
            new, rows_total = [], 0
            for tab in bidnet.CO_TABS:
                ses.page.goto(f"{bidnet.CO_OPEN}?selectedContent={tab}", wait_until="domcontentloaded")
                ses.page.wait_for_timeout(800)
                html = bidnet._content(ses.page)
                if bidnet.BOT_RX.search(html) and not bidnet.total_count(html):
                    rec["robot_check"] = True
                    break
                rows, _ = bidnet.parse_listing(html, ses.page.url)
                rows_total += len(rows)
                rec.setdefault("site_totals", {})[tab] = bidnet.total_count(html)
                for r in rows:
                    if r["id"] not in seen:
                        new.append({"id": r["id"], "title": r["title"][:90], "closing": r["closing"]})
                        seen.add(r["id"])
            rec["list_rows"], rec["new_bids"] = rows_total, new
            # document access on a watched bid
            if ok:
                d = bidnet.enrich(ses, {"id": "0000438328", "url": DOC_BID_URL, "source": "bidnet"})
                rec["docs"] = len(d.get("documents") or [])
                rec["sol"] = d.get("sol")
            # still logged in after all that?
            rec["still_logged_in"] = bool(ok and ses.page.locator(bidnet.LOGIN_FORM_SEL).count() == 0)
            ses.save()
        finally:
            ses.close()
    except Exception as e:  # noqa: BLE001 - a crashed check is a FAILED check, never a crashed test
        rec["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        rec["trace"] = traceback.format_exc()[-800:]
    finally:
        br.close()
    rec["seconds"] = round(time.time() - t0, 1)
    rec["passed"] = bool(rec.get("logged_in") and rec.get("list_rows") and (rec.get("docs") or 0) >= 1
                         and not rec.get("robot_check") and not rec.get("error"))
    return rec


def write_summary(run: list[dict], args, done: bool) -> None:
    passed = sum(1 for r in run if r["passed"])
    lines = [f"# BidNet endurance test {'(COMPLETE)' if done else '(IN PROGRESS)'}", "",
             f"Started {run[0]['at'] if run else '?'}; {len(run)} of {args.checks} checks run; "
             f"**{passed}/{len(run)} passed**. Each check = fresh browser from the saved session file, "
             f"verify/restore login, poll page 1 of both statewide lists, open Littleton 21-26's Documents tab.", "",
             "| # | At (UTC) | Forced expiry | Logged in | How | List rows | Docs | New bids | Seconds | Result |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in run:
        how = (r.get("login_note") or "")[:40]
        lines.append(f"| {r['check']} | {r['at'][11:19]} | {r.get('forced') or ''}"
                     f"{' (' + str(r.get('cookies_deleted')) + ' cookies)' if r.get('forced') else ''} | "
                     f"{'yes' if r.get('logged_in') else 'NO'} | {how} | {r.get('list_rows', 0)} | {r.get('docs', 0)} | "
                     f"{len(r.get('new_bids') or [])} | {r['seconds']} | "
                     f"{'PASS' if r['passed'] else 'FAIL: ' + (r.get('error') or ('robot check' if r.get('robot_check') else 'see log'))[:60]} |")
    newb = [b for r in run for b in (r.get("new_bids") or []) if r["check"] > 1]
    if newb:
        lines += ["", "## New bids that appeared during the test", ""]
        lines += [f"- {b['id']} {b['title']} (closes {b['closing']})" for b in newb]
    SUMMARY.write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=66)
    ap.add_argument("--interval", type=float, default=6)
    ap.add_argument("--run-id", default=time.strftime("%Y%m%dT%H%M", time.gmtime()))
    a = ap.parse_args()
    a.checks = int(a.minutes // a.interval) + 1
    load_env_file()
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    prior = [json.loads(l) for l in LOG.read_text().splitlines()] if LOG.exists() else []
    run = [r for r in prior if r.get("run_id") == a.run_id]  # resume after a container restart
    seen = set(load_json(OPEN_BIDS_FILE, {"bids": {}})["bids"].keys())
    seen = {k.split(":", 1)[1] for k in seen if k.startswith("bidnet:")}
    for r in run:
        seen |= {b["id"] for b in (r.get("new_bids") or [])}
    start = time.time() - (len(run) * a.interval * 60)
    for n in range(len(run) + 1, a.checks + 1):
        due = start + (n - 1) * a.interval * 60
        if time.time() < due:
            time.sleep(due - time.time())
        force = "app" if n == 4 else ("sso" if n == 8 else None)
        rec = {**one_check(n, seen, force), "run_id": a.run_id}
        with LOG.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        run.append(rec)
        write_summary(run, a, done=(n == a.checks))
        print(f"[{rec['at']}] check {n}/{a.checks}: {'PASS' if rec['passed'] else 'FAIL'} "
              f"login={rec.get('login_note')!r} rows={rec.get('list_rows')} docs={rec.get('docs')} "
              f"new={len(rec.get('new_bids') or [])} forced={force} err={rec.get('error', '')[:120]}", flush=True)
    passed = sum(1 for r in run if r["passed"])
    print(f"DONE {passed}/{len(run)} passed", flush=True)
    return 0 if passed == len(run) else 1


if __name__ == "__main__":
    sys.exit(main())
