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
    python3 tests/test_bidwatch.py                # 38 offline tests incl. a fake portal with login/expiry

## Honest limits
- Selectors were built and tested against fixture pages and a simulated login site, because the real
  portals are blocked from the build environment. The first live run may need a selector fix; the debug
  dumps make that a quick job.
- SAM.gov caps API calls (about 10/day without an entity role, 1,000/day with one). The scanner tracks a
  daily budget (`SAM_DAILY_BUDGET`, default 900) and uses ~2-6 calls per scan.
- RTD (OpenGov) is not scraped yet; it is on the watchlist for the hourly GovTribe check.
- Automated access to BidNet is restricted by its terms; keep the cadence modest (30-60 min).
