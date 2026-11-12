# Bid watcher: full visibility on every open and upcoming bid

`python3 scripts/bidwatch/run.py` scans every source, every time:

| Source | What it pulls | Login |
|---|---|---|
| BidNet Direct / Rocky Mountain E-Purchasing (all Colorado agencies on BidNet) | Statewide Colorado open-bids list (every page) + a search per profile keyword; detail page of every match and every watched bid: closing date, questions deadline, pre-bid / site walk (MANDATORY or not, with the quoted text), document list | `BIDNET_USER`, `BIDNET_PASS` (documents need it; lists are public) |
| Euna Procurement, formerly Bonfire (Town of Parker; add others in `watch_profiles.json` -> `bonfire_orgs`) | Open opportunities + each opportunity's Events table (questions, site visit, close) | `BONFIRE_USER`, `BONFIRE_PASS` (documents only) |
| SAM.gov (federal) | API: everything still open in Colorado, all types: solicitations plus UPCOMING presolicitations, sources sought, special notices; Jones Bearing PSC codes nationwide. Nightly bulk file (`samgov_bulk.py`, no key): adds notices with a blank place of performance and a Colorado buying office, and keeps SAM.gov discovery working when the API is down or the key is missing | `SAM_API_KEY` (API only) |
| DLA DIBBS (Jones Bearing) | Open RFQs by FSC 3110/3130/3020/3910/3920 | none to view |
| ColoradoVSS, State of Colorado Vendor Self Service (`coloradovss.py`; state agencies, CDOC, community colleges, AHEC, CDPHE) | The public "View Published Solicitations" list (100 rows a page, all pages); detail of every match and watched bid: Schedule of Events (pre-bid / site walk, MANDATORY or not, questions due), Solicitation Instructions text, attachment list. Sole-source and contractor-settlement notices are kept but never matched; RFIs count as UPCOMING. No deep link: open the portal, View Published Solicitations, search the `sol` | none: public pages only, never logs in; a captcha / bot check stops it as BLOCKED |

Each scan writes:
- `bids/_watch/REPORT.md`: headline, **source health table** (reachable? credentials set? logged in? how
  many open bids seen?), pre-bid walks in the next 7 days, NEW matching bids, CHANGES on watched bids
  (new documents = addenda, date changes), UPCOMING notices, and the full list of open matching bids.
- `bids/_watch/open_bids.json` (everything seen), `bids/_watch/health.json`.
- Watched-bid documents to `bids/_watch/downloads/<source>/<id>/` when logged in.
- `bids/_watch/LAST_SCAN.md`: the hourly operator's digest, read in one `cat` instead of grepping REPORT.md and diffing
  open_bids.json against a saved copy. A heading with the scan's UTC time, then six labelled lines, plain text, no tables:
  `Logged in:` (BidNet: `yes (attempt 1)`, `yes (session reused ...)`, `no: login deferred ...`, `no: COOL-DOWN ...`);
  `Counts:` open rows/matching per source, `bidnet | samgov | coloradovss | bonfire | total`, with `(BLIND, last good <UTC>)`
  after a source that returned nothing fresh and `(PARTIAL, ...)` after one whose list came back short; `New matching bids:`
  n, then one `  - <source> <id> | <title> | <agency> | closes <date> | <profiles> | watched yes/no` line per bid (new = a
  matching open bid whose key was not in the previous open_bids.json, exactly REPORT.md's NEW list); `Changes on watched
  bids:` n, then REPORT.md's change lines cut to 200 chars; `Documents downloaded:` n, then `  - <bid folder or source:id>:
  <file>`; `Errors:` `none` or per-source counts and the first error, then `exit code 0|2|3` (the code `run.py` returns:
  3 = a source was blind or carried forward). The same lines are printed to stdout after the cycle line, so a log tail
  shows them, and the file is in `--push`'s commit (PUSH_PATHS). A scan that crashes still writes it, with the crash in the
  Errors line, so the previous hour's digest is never mistaken for this hour's.

### BidNet Communication and Q & A tabs (watched bids)
A buyer can post a notice on a solicitation's **Communication** tab with no addendum and no document (2026-11-05
15:48 MST on 0000440322: "the walkthrough time has changed from 9 am to 10:30 am"), so the document diff never
sees it. For every watched bid, a logged-in scan therefore also clicks the detail page's Communication and Q & A
tabs (`a[href*='innerTabId=communication']`, `a[href*='innerTabId=questions-answers']`; the Communication tab only
exists once the buyer posted something) and stores `communications` (number, date as printed, text) and `qa`
(question acceptance deadline, each question with its answer and dates, and the pager's `total`) on the row in
`open_bids.json`. The report's "Changes on matching / watched bids" section then carries
`NEW COMMUNICATION No.<n> <date>: "<text>"`, `NEW Q&A: <n> answered` (a question is news again when its answer
arrives; `(n of N shown)` when BidNet paged the list, which it offers at 25/50/100 per page but served all 266
Custodial questions on one page) and `questions deadline <date>`, each once, the first scan that sees it. A tab
that fails to load, a blind scan or a robot check keeps last scan's entries, like documents, so nothing comes back
as NEW twice. Real tab pages: `tests/fixtures/bidnet_qa_*.html`, `bidnet_communication_0000440322.html`.

### Detail pass time budget (`BIDWATCH_DETAIL_BUDGET_S`, 2026-11-12)
The detail pass (detail pages, BidNet's documents / Communication / Q & A tabs, document downloads; BidNet, then
Bonfire, then ColoradoVSS) runs inside one wall-clock budget of `BIDWATCH_DETAIL_BUDGET_S` seconds (default 600;
`0` turns the cap off), measured from the first detail page of the scan and shared by every source. It opens
watched bids first, then the matches new this scan, then the rest, so the budget is spent on what matters. Once the
budget is spent, the remaining bids keep last scan's detail (documents, pre-bid, tabs) exactly as a bid whose page
failed to load does, so nothing comes back as a new addendum next scan; the source's health gets `detail_cut`
(`done`, `total`, `elapsed_s`, `budget_s`) and one note, `detail pass cut after 600 s: 23 of 85 bids enriched (BidNet
slow); the rest keep last scan's details`, which REPORT.md prints in its headline and Errors section and LAST_SCAN.md in
its Errors line; the run exits 3 (degraded, not failed) and still writes REPORT.md, LAST_SCAN.md and open_bids.json and
pushes. Why: on 2026-11-12 20:39Z BidNet's tabs hung on "Loading..." behind a site-wide service banner, the detail pass
waited `TAB_WAIT_MS` per tab per bid, and the outer `timeout 1500` killed the run before REPORT.md, losing the hour's
list scan and SAM.gov results. Tests: `tests/test_bidwatch.py`, "detail pass wall-clock budget".

## Staying logged in
Sessions (cookies) are saved per portal in `~/.brownbison/sessions/` (outside the repo, mode 600). Every
scan first checks whether the saved session still works; if it timed out, it logs in again with the env
vars, retrying 3 times with backoff, and saves the new session. If a page bounces to the login screen
mid-scan, it re-logs in and re-reads. `--loop` keeps doing this forever:

    python3 scripts/bidwatch/run.py --loop --interval 30     # every 30 minutes, 24/7

BidNet paces fresh password logins: fresh logins close together trip its robot check (the 4th in ~6 h did on
2026-10-30; 3 h apart passed). A saved session is reused at any time, but a new password login is submitted only
`BIDWATCH_BIDNET_LOGIN_GAP_H` hours (default 3; `0` turns the gap off) after the last one that worked
(`~/.brownbison/bidnet_last_login`). Inside the gap, a scan whose session expired skips BidNet like a robot-check
cool-down: the health note reads `login deferred: last fresh login <time>, next allowed after <time>`, earlier
rows are carried forward and none closed, and the run is not pinged as failed.

A failed login or a page that parses to nothing saves a screenshot + HTML to `bids/_watch/debug/`
(gitignored) so the selectors can be fixed from the real page.

### Mac-fed BidNet session (no-password mode, 2026-11-06)
BidNet challenged 2 of 6 fresh password logins from the cloud with its robot check, and a session idles out in under
~50 minutes while the cloud container sleeps between hourly scans, so each good login bought one scan. The fix: the
cloud scanner never logs in. Luke's Mac (residential IP, always on) logs in, keeps the session warm every 15 minutes
(`scripts/bidwatch/mac_session_feeder.py`) and ships its Playwright storage state encrypted
(`scripts/bidwatch/session_sync.py`); the cloud, started with `BIDWATCH_BIDNET_NO_PASSWORD=1`, only ever reuses it.

Encryption: `openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt` with `STATE_PASSPHRASE`, the same scheme and secret
as the Actions failover's `state.enc`, so one file works for the Mac, the cloud and the failover. The passphrase lives
in the environment or `~/.brownbison/env` on each machine, never in the repo or in chat. The plaintext session never
enters the repo (`.gitignore` keeps everything but `.enc` out of `ops/session/`); the `.enc` may be committed to the
PRIVATE branch or copied over scp.

**On Luke's Mac (once; it is the only machine that logs in):**

    cd ~/PioneerLeads                                    # the checkout the Mac already runs from
    python3 -m pip install -r requirements.txt && python3 -m playwright install chromium
    mkdir -p -m 700 ~/.brownbison && touch ~/.brownbison/env && chmod 600 ~/.brownbison/env
    # add to ~/.brownbison/env (one KEY=VALUE per line; type the values there, never in chat):
    #   BIDNET_USER=luke@brownbisonco.com
    #   BIDNET_PASS=...
    #   STATE_PASSPHRASE=...            a long random phrase; the SAME value goes in the cloud environment
    #   BIDNET_CODE_IMAP_PASS=...       optional Google app password: the feeder then reads BidNet's emailed code itself
    #   BIDWATCH_SESSION_PUSH_CMD=git add ops/session/bidnet-session.enc && git commit -qm "bidnet session" && git pull -q --rebase && git push -q
    python3 scripts/bidwatch/mac_session_feeder.py --once   # first login; if BidNet asks for its emailed code and no
                                                            # app password is set: python3 scripts/bidwatch/set_code.py <code>
                                                            # in a second terminal while the feeder waits (5 min)
    python3 scripts/bidwatch/session_sync.py status         # cookies, age, longest-lived auth cookie, last import

Then keep it ticking every 15 minutes. Quick way: `nohup python3 scripts/bidwatch/mac_session_feeder.py --every 900
>> ~/.brownbison/session_feeder.log 2>&1 &`. Durable way (survives a reboot and a closed terminal), a launchd agent
`~/Library/LaunchAgents/com.brownbison.session-feeder.plist`, then `launchctl load` it:

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0"><dict>
      <key>Label</key><string>com.brownbison.session-feeder</string>
      <key>ProgramArguments</key><array><string>/usr/bin/python3</string>
        <string>/Users/luke/PioneerLeads/scripts/bidwatch/mac_session_feeder.py</string><string>--every</string><string>900</string></array>
      <key>WorkingDirectory</key><string>/Users/luke/PioneerLeads</string>
      <key>RunAtLoad</key><true/><key>KeepAlive</key><true/>
      <key>StandardOutPath</key><string>/Users/luke/.brownbison/session_feeder.log</string>
      <key>StandardErrorPath</key><string>/Users/luke/.brownbison/session_feeder.log</string>
    </dict></plist>

Each tick: a logged-in page load with the saved session (the keep-alive, never a password); only when BidNet no longer
recognises it, one normal login (emailed code via the mailbox or `set_code.py`; a robot check starts the usual 2 h
cool-down and the tick ends; the 3 h fresh-login gap applies); the keep-alive probe itself still runs during a
cool-down (a session left unprobed for 2 h idles out, which is what forced the fresh login on 2026-11-06), skips only
when there is no saved session file, and a challenged probe is logged as `probe challenged (cool-down until ...)`
without starting or extending the cool-down, with no login until it ends; then `session_sync.py export` to
`ops/session/bidnet-session.enc` and the push command (`$BIDWATCH_SESSION_FILE` names the file). A commit every 15
minutes is a few KB and rebases cleanly against the hourly scan pushes. Status: `~/.brownbison/session_feeder.json`.
macOS ships LibreSSL as `openssl`; if export fails with `unknown option` on `-pbkdf2`, `brew install openssl@3` and set
`BIDWATCH_OPENSSL=$(brew --prefix openssl@3)/bin/openssl` in `~/.brownbison/env`.

**In the cloud environment (Network access / Environment variables screen):**

    BIDWATCH_BIDNET_NO_PASSWORD=1      # the scanner never submits the login form, whatever BIDNET_PASS says
    STATE_PASSPHRASE=<same as the Mac> # decrypts the shipped session

The hourly scan pulls the branch first (`run.py --push` does, via `git_sync`; a fresh container clones it, which is
enough), then `run.py` calls `session_sync.import_if_new()` before BidNet: `BIDWATCH_SESSION_IMPORT=PATH` or
`--import-session PATH` names the file; in no-password mode with neither set, `ops/session/bidnet-session.enc` is used
when it exists. The decrypted session lands at `~/.brownbison/sessions/bidnet.json` (mode 600, outside the repo), and
`~/.brownbison/session_import.json` keeps the sha256 of the last file installed so the same file is not re-installed
over cookies the scan has since refreshed. By hand: `python3 scripts/bidwatch/session_sync.py import
ops/session/bidnet-session.enc`; `session_sync.py check` opens a browser with the saved session and prints alive or
expired without ever logging in.

What the health table (REPORT.md, health.json) then says:
- good hour: `session reused (no-password mode: synced session); synced session imported: 14 cookies, file dated <UTC>`
  (or `... synced session unchanged since its import at <UTC>` when the Mac's last file is still the live one);
- the Mac stopped shipping: `no-password mode: saved session expired; waiting for a synced session; synced session
  unchanged since ...`. BidNet is then skipped exactly like a deferred login: earlier rows carried forward, none
  closed, exit 0, no `/fail` ping, no cool-down, and the headline reads `BLIND: bidnet (login deferred on purpose)`.
  The keepalive's status says `expired: no-password mode ... waiting for a session synced from the Mac`;
- a bad file (wrong passphrase, damaged, not a session): `synced session REFUSED (...); the saved session is untouched`.

The cloud's copy shares BidNet's server-side session with the Mac, so a file an hour old still works as long as the
Mac keeps ticking; when the Mac sleeps or stops, the cloud goes blind on BidNet within ~50 minutes and says so.

### New-device confirmation code (BidNet)
BidNet emails "Your BidNet Direct confirmation code" (noreply@bidnet.com, 6 digits) after a password login
from a device it has not seen (Luke's inbox got two on 2026-10-19), and shows a code prompt. Every password
login issues a NEW code, so a code is only good inside the browser session that asked for it. The scanner
therefore stays on the prompt and waits up to `BIDNET_CODE_WAIT` seconds (default 300) for the code:
`python3 scripts/bidwatch/set_code.py <code or pasted email text>` writes it to `~/.brownbison/bidnet_code`
(single use; `BIDNET_CODE` env var also works). If nobody supplies it in time, the health table shows
`login BLOCKED: ... confirmation code`, a screenshot lands in `bids/_watch/debug/`, and
`~/.brownbison/bidnet_code_needed` is written: while that marker exists the scanner makes NO further
password logins (each would email another code). Delete the marker when someone can supply the code within
the window; the confirmed-device cookie is then saved with the session, so this happens at most once per
container. The MAIN session has read-only Gmail and can do the whole exchange itself; fresh worker
sessions cannot, so the durable fix is one long-lived container running the loop below.

### Persistent loop with publishing
    nohup python3 scripts/bidwatch/run.py --loop --interval 60 --push > bids/_watch/debug/loop.log 2>&1 &

`--push` makes every cycle: `git rebase` onto the branch first, scan, rebuild `bids/_watch/dashboard/*.json`,
commit `bids/_watch/{REPORT.md,open_bids.json,health.json,dibbs_state.json,dashboard/,downloads/}` as
"bidwatch: live scan <UTC>", rebase again (our freshly generated files win a conflict), push with backoff.
Heartbeat: `bids/_watch/debug/loop.status` (pid, cycle, last sync/push result, login notes). The loop
dies with its container; the hourly WORKER scheduled task is the safety net that outlives it.

## What Luke sets up (once)
**Cloud (this Claude environment; runs 24/7, no computer needed):**
1. Session title bar -> environment menu -> Edit -> Network access. Choose the broader access level, or add
   these under Allowed domains:
   `bidnetdirect.com`, `www.bidnetdirect.com`, `www.rockymountainbidsystem.com`, `api.sam.gov`, `sam.gov`,
   `parkeronline.bonfirehub.com`, `www.dibbs.bsm.dla.mil`, `prd.co.cgiadvantage.com` (ColoradoVSS).
   Docs: https://code.claude.com/docs/en/cloud-environments#network-access
2. Same screen -> Environment variables: `BIDNET_USER`, `BIDNET_PASS`, `SAM_API_KEY`, `BONFIRE_USER`,
   `BONFIRE_PASS`. Type them there, never in chat. (Rotate any password that was ever pasted in chat.)
3. Say "go". The hourly check then runs the scanner live each hour.

**Or your own always-on computer:** copy `.env.example` to `.env`, fill it in, run
`./scripts/local_runner.sh` on a schedule (docs/local-runner.md). It pushes REPORT.md to the repo.

## Check it
    python3 scripts/bidwatch/run.py --health      # reachability + which credentials are set (never prints values)
    python3 tests/test_bidwatch.py                # 196 offline tests: real-page fixtures + a fake portal with login/expiry,
                                                  # no-password mode and the session sync (2026-11-06)

## DIBBS: only from Luke's own computer
DIBBS FAQ #45 (verified 2026-10-20): "the DIBBS and cFolders User Agreements prohibits the use of any service or device
that masks a user's access ... VPNs, proxy servers, TOR nodes, cloud hosting services, and other similar services or
devices ... are, therefore, prohibited." The cloud scanner therefore never reads DIBBS. On Luke's own machine set
`BIDWATCH_ALLOW_DIBBS=1` in `.env` (docs/local-runner.md). Better than page scraping there: the daily index file
`https://dibbs2.bsm.dla.mil/Downloads/RFQ/Archive/in{YYMMDD}.txt` (fixed-width, ~1,700 lines/day) plus RFQ PDFs at
`https://dibbs2.bsm.dla.mil/Downloads/RFQ/<last char of solicitation>/<SOL>.PDF`.

## Live status (verified 2026-10-20 from a cloud session with full network access, no portal logins)
| Source | Result |
|---|---|
| BidNet Colorado | Statewide list read completely: BUYER tab (RMEPS member agencies) 400 + AGGREGATE tab 184 = 584, equal to the counts the site prints. Pages are `/open-bids/page2?...` (25 rows), rows are `tr.mets-table-row`. Keyword searches (`?keywords=`) now run only if the statewide pass comes back short. |
| BidNet detail / documents | Public visitors see only location, publication date and closing date+time. Issuing org, solicitation #, description, **documents** and buyer contact are "Registered members only": BIDNET_USER/BIDNET_PASS are required for documents and pre-bid text. Without a login only watched bids' detail pages are opened. |
| Euna/Bonfire (Parker) | Open list read from `/PublicPortal/getOpenPublicOpportunitiesSectionData` (JSON, DateClose is UTC; converted to Mountain time). Opportunity pages (`/opportunities/<id>`) return a **Cloudflare bot challenge** to this network (HTTP 403, `cf-mitigated: challenge`); the scanner reports that instead of guessing. RTD's OpenGov portal does the same. |
| SAM.gov | API key set and working. Nightly bulk file verified 2026-10-20 05:28 UTC: 205 MB in 3 s, 14,033 open notices, 68 matching (17 Brown Bison, 51 Jones Bearing), 30 of them not found by the API path, e.g. a Rocky Mountain Regional VA radiant panel replacement with no stated place of performance. |
| DLA DIBBS | From Luke's own computer only (user agreement FAQ #45 prohibits cloud and proxy access). Works without login. RFQ grid sorted by Return By descending and paged until expired; ~300 open RFQs across the Jones Bearing FSCs. Solicitation numbers are `SPE4A0-26-T-2395` style (3-char suffix after SPE: the old regex missed every row). |

Real-page fixtures for all of the above: `tests/fixtures/`, exercised by `python3 tests/test_bidwatch.py`.

## Honest limits
- List selectors are verified against the live sites (2026-10-20). The BidNet login is verified live
  (2026-10-20: saved-session reuse, recovery after forced session expiry, documents on Littleton 21-26);
  the Bonfire login is still only tested against the simulated site.
- A `--sources` run limited to some sources keeps the other sources' last rows, marked NOT SCANNED THIS RUN.
- The SAM.gov bulk file has no attachments and lags by up to a day (rebuilt nightly around 03:30 UTC); the API
  stays first for same-day postings and documents.
- SAM.gov caps API calls (about 10/day without an entity role, 1,000/day with one). The scanner tracks a
  daily budget (`SAM_DAILY_BUDGET`, default 900) and uses ~2-6 calls per scan, plus the new-match brief: for up to
  `BIDWATCH_SAMGOV_BRIEF_MAX` (default 5; 0 disables) NEW SAM.gov matches per scan it reads the notice description
  (1 call) and looks up at most two CAGE codes it names (1 call each), and prints one `brief:` line under the notice in
  LAST_SCAN.md / REPORT.md (set-aside, NSN, quantities, OEM CAGE + name, authorized-distributor / no-drawings / ISO 9001
  flags); the line is kept on the record in open_bids.json. A failed brief changes nothing but adds an error note.
- RTD (OpenGov) is not scraped yet; it is on the watchlist for the hourly GovTribe check.
- Automated access to BidNet is restricted by its terms; keep the cadence modest (30-60 min).
