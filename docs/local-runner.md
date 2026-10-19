# Full-time portal connection via your own computer (works today, no cloud network change)

The cloud sandbox cannot reach BidNet, SAM.gov, or DIBBS. Your laptop or office PC can. So the scanners run
there on a schedule and push results into this repo; the hourly cloud Routine reads the repo and acts.
Result: new bids, addenda, DLA RFQs and downloaded documents show up here automatically, and you are not
in the loop after a one-time setup (about 20 minutes).

## One-time setup
1. Install Git and Python 3.11+ (python.org). Windows: tick "Add to PATH".
2. Clone the repo: `git clone https://github.com/lukemitchelladams/PioneerLeads.git` (rename pending), `cd` in.
3. `cp .env.example .env` (Windows: `copy .env.example .env`) and fill in `BIDNET_PASS` and `SAM_API_KEY`.
   `.env` is gitignored; it never leaves your machine.
4. Run once by hand to confirm:
   - Mac/Linux: `./scripts/local_runner.sh`
   - Windows: `powershell -ExecutionPolicy Bypass -File scripts\local_runner.ps1`
   First run installs Playwright + Chromium (a few minutes). Check `bids/_watch/REPORT.md`.
5. Git credentials: the push needs your GitHub login once (Git Credential Manager caches it).

## Schedule it (every 4 hours, 6am–8pm)
- **Windows Task Scheduler**: Create Task → Trigger: Daily, repeat every 4 hours for 14 hours starting 06:00 →
  Action: Program `powershell`, Arguments `-ExecutionPolicy Bypass -File C:\path\to\repo\scripts\local_runner.ps1`
  → tick "Run whether user is logged on or not" and "Wake the computer to run".
- **macOS**: `crontab -e` → `0 6-20/4 * * * /path/to/repo/scripts/local_runner.sh >> /tmp/brownbison-cron.log 2>&1`
  (System Settings → Energy: prevent sleep, or use an always-on machine).
- **Linux**: same crontab line.

## What happens after each run
- `bids/_watch/REPORT.md` headline: new/changed/closed BidNet solicitations (both company profiles), new DLA
  DIBBS RFQs for Jones Bearing, new SAM.gov notices for both companies.
- Documents for keyword matches land in `bids/_watch/downloads/<agency>/<solicitation>/`.
- The hourly cloud Routine pulls the repo, relays the headline to Luke, and opens a bid folder with a
  requirements matrix for every new keyword match.

## First-run reality
The BidNet and DIBBS extractors were built blind (sites blocked from the cloud). The first real run will
likely report "0 rows parsed; raw HTML saved". Commit and push that raw HTML (the runner does) and I fix the
selectors from it in one pass. Expect one or two iterations.

## Keep the cloud path too
When the cloud environment's Network access is widened, the same scripts run there on a Routine with no
local machine needed. Both paths write the same files; whichever runs first wins, the other sees no change.
