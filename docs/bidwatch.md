# Bid watcher: full visibility on every open and upcoming bid

`python3 scripts/bidwatch/run.py` scans every source, every time:

| Source | What it pulls | Login |
|---|---|---|
| BidNet Direct / Rocky Mountain E-Purchasing (all Colorado agencies on BidNet) | Statewide Colorado open-bids list (every page) + a search per profile keyword; detail page of every match and every watched bid: closing date, questions deadline, pre-bid / site walk (MANDATORY or not, with the quoted text), document list | `BIDNET_USER`, `BIDNET_PASS` (documents need it; lists are public) |
| Euna Procurement, formerly Bonfire (Town of Parker; add others in `watch_profiles.json` -> `bonfire_orgs`) | Open opportunities + each opportunity's Events table (questions, site visit, close) | `BONFIRE_USER`, `BONFIRE_PASS` (documents only) |
| SAM.gov (federal) | Everything still open in Colorado, all types: solicitations plus UPCOMING presolicitations, sources sought, special notices; Jones Bearing PSC codes nationwide | `SAM_API_KEY` |
| DLA DIBBS (Jones Bearing) | Open RFQs by FSC 3110/3130/3020/3910/3920 | none to view |

Each scan writes:
- `bids/_watch/REPORT.md`: headline, **source health table** (reachable? credentials set? logged in? how
  many open bids seen?), pre-bid walks in the next 7 days, NEW matching bids, CHANGES on watched bids
  (new documents = addenda, date changes), UPCOMING notices, and the full list of open matching bids.
- `bids/_watch/open_bids.json` (everything seen), `bids/_watch/health.json`.
- Watched-bid documents to `bids/_watch/downloads/<source>/<id>/` when logged in.

## Staying logged in
Sessions (cookies) are saved per portal in `~/.brownbison/sessions/` (outside the repo, mode 600). Every
scan first checks whether the saved session still works; if it timed out, it logs in again with the env
vars, retrying 3 times with backoff, and saves the new session. If a page bounces to the login screen
mid-scan, it re-logs in and re-reads. `--loop` keeps doing this forever:

    python3 scripts/bidwatch/run.py --loop --interval 30     # every 30 minutes, 24/7

A failed login or a page that parses to nothing saves a screenshot + HTML to `bids/_watch/debug/`
(gitignored) so the selectors can be fixed from the real page.

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
   `parkeronline.bonfirehub.com`, `www.dibbs.bsm.dla.mil`.
   Docs: https://code.claude.com/docs/en/cloud-environments#network-access
2. Same screen -> Environment variables: `BIDNET_USER`, `BIDNET_PASS`, `SAM_API_KEY`, `BONFIRE_USER`,
   `BONFIRE_PASS`. Type them there, never in chat. (Rotate any password that was ever pasted in chat.)
3. Say "go". The hourly check then runs the scanner live each hour.

**Or your own always-on computer:** copy `.env.example` to `.env`, fill it in, run
`./scripts/local_runner.sh` on a schedule (docs/local-runner.md). It pushes REPORT.md to the repo.

## Check it
    python3 scripts/bidwatch/run.py --health      # reachability + which credentials are set (never prints values)
    python3 tests/test_bidwatch.py                # 57 offline tests: real-page fixtures + a fake portal with login/expiry

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
| SAM.gov | Needs `SAM_API_KEY` (not set). |
| DLA DIBBS | Works without login. RFQ grid sorted by Return By descending and paged until expired; ~300 open RFQs across the Jones Bearing FSCs. Solicitation numbers are `SPE4A0-26-T-2395` style (3-char suffix after SPE: the old regex missed every row). |

Real-page fixtures for all of the above: `tests/fixtures/`, exercised by `python3 tests/test_bidwatch.py`.

## Honest limits
- List selectors are verified against the live sites (2026-10-20). The BidNet and Bonfire LOGIN flows are
  still only tested against the simulated site, because no credentials were set during the live run.
- A `--sources` run limited to some sources rewrites open_bids.json with only those sources; run all
  sources for the hourly check.
- SAM.gov caps API calls (about 10/day without an entity role, 1,000/day with one). The scanner tracks a
  daily budget (`SAM_DAILY_BUDGET`, default 900) and uses ~2-6 calls per scan.
- RTD (OpenGov) is not scraped yet; it is on the watchlist for the hourly GovTribe check.
- Automated access to BidNet is restricted by its terms; keep the cadence modest (30-60 min).
