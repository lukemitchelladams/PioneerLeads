# Decision log

Newest first. Each entry: date, venture, decision, who decided, why.

## Open (waiting on Luke)

| Date raised | Venture | Decision needed | Orchestrator's recommendation |
| --- | --- | --- | --- |
| 2026-10-15 | Govcon | Get Alex Ditto's DCSD bid into the repo when it lands Monday Oct 19 (Luke confirmed with Alex, Oct 18) | Drop the files in `bids/dcsd-hvac/docs/`; connecting Gmail would also let every future emailed bid be read without a hand-off |
| 2026-10-15 | Govcon | The Breckenridge summit company price reply: was it sent? | Answer in the loop session or here; the loop was archived with the question open |
| 2026-10-15 | SpeedRun Social | Apple Pay failure on live Checkout | Read the Stripe check endpoint output and fix the wallet config |
| 2026-10-14 | SpeedRun Social | Set NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY in Vercel and redeploy | Do it; the card-in-dialog flow you asked for on Oct 13 is shipped but dark |
| 2026-10-14 | SpeedRun Social | Supabase storage quota, locked three times Oct 6 to 9 | Raise the plan; customers lost a week of media |
| 2026-10-05 | SpeedRun Social | Where deploys run (laptop vs always-on machine or CI) | Now urgent: the Mac froze Oct 18 under eight parallel build agents; #155 blocked Oct 16 by Mac load; #136 stalled in sleep Oct 2 |
| 2026-10-18 | SpeedRun Social | How many agents may build on the Mac at once | Two, with one shared `bun install`; the orchestrator asked the Blaze session for this on Oct 18 and it should be a rule in that session's CLAUDE.md |
| 2026-10-18 | Govcon | Recover the Workspace admin login `luke@brownbisonco.com` | Sign in with that address, not the Gmail; use Forgot password, which goes to the recovery phone or email given at signup. Then store it in a password manager. No session can do this |
| 2026-10-14 | Govcon | Commit the send_gov_intros.py import guard | Do it; uncommitted safety fix on a script that sends real mail |
| 2026-10-01 | Govcon | Parker bid due date | One line |
| 2026-10-01 | POE | Commercial terms with Radius | Write them down so the venture can be prioritised honestly |
| 2026-09-25 | POE | Six parked decisions (territory map, merge 91 duplicates, delete 9 files, subject line, Partner vs Pipeline, CDW domains) | Defaults in `poe-radius.md`; send to Cole as one message |
| 2026-09-18 | SpeedRun Social | Google Ads on or off | Off until a stranger can Connect |
| 2026-06-04 | SpeedRun Social | Vercel Pro for 5-minute cron | Upgrade once there is one paying customer |

## Closed

| Date | Venture | Decision | By | Why |
| --- | --- | --- | --- | --- |
| 2026-10-18 | Govcon | brownbisonco.com mail runs on Google Workspace, tenant verified and DKIM-signed | Luke (signup between Oct 14 and 18) | Public DNS shows MX smtp.google.com, verification TXT, SPF, DKIM, DMARC |
| 2026-10-19 | Portfolio | Ops docs live in `lukemitchelladams/PioneerLeads` under `ops/` | Orchestrator, on Luke's "get the push to work" | The portfolio repo was retired Sept 30; PioneerLeads is the Brown Bison workspace and writable |
| 2026-10-15 | Govcon | Estes Park is a no-bid | Luke | Mandatory pre-bid missed |
| 2026-10-15 | Govcon | Landscaping work routes to Alex Ditto | Luke | Recorded in the bid research session's memory |
| 2026-10-09 | POE | POE reads Radius's main HubSpot portal, not the sandbox | Cole | Service Key switched; ids re-matched |
| 2026-10-09 | POE | ZoomInfo free search in v1; paid details call out, documented for later | Cole (Oct 5 and 9) | Recorded in CLAUDE.md |
| 2026-10-06 | SpeedRun Social | Zernio payment method, closed as evidently done | Inferred | Six external workspaces published a first post by Oct 5 |
| 2026-10-01 | SpeedRun Social | Stripe switched to live mode | Luke | `/api/health` reports `billing: live`; checklist from 2026-09-18 |
| 2026-10-01 | Portfolio | Orchestrator stood up with weekday check-ins and this folder as the system of record | Luke (requested) | "Keep them on task and moving forward at all times" |
| 2026-09-23 | POE | Finished work goes straight to main without asking | Cole | Recorded in CLAUDE.md |
| 2026-09-16 | POE | Claude applies migrations directly with a scoped credential | Cole | Recorded in CLAUDE.md |
