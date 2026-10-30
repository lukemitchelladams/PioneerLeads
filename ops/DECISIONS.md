# Decision log

Newest first. Each entry: date, venture, decision, who decided, why.

## Open (waiting on Luke)

| Date raised | Venture | Decision needed | Orchestrator's recommendation |
| --- | --- | --- | --- |
| 2026-10-30 | Govcon | El Paso 26-074 water treatment: if FACT Water's number is not in hand by Mon Nov 2 noon, bid with Summit Laboratories as backup or drop it; the bid also needs $1M pollution liability Brown Bison does not carry | Drop unless FACT prices by Monday and Trucordia quotes the pollution cover; proposal due Wed Nov 4 14:00 |
| 2026-10-30 | Govcon | Call Will at Trucordia (720-484-3732) for the named-insured fix and the COI, and ask for the pollution liability quote | Today |
| 2026-10-30 | Govcon | Weld SD6 coiling grille, mandatory walk Mon Nov 2 10:00 at Franklin MS, Greeley: you attend, or a door sub does; none of the three emailed has replied | Plan to attend yourself unless a sub commits by Friday evening |
| 2026-10-30 | Govcon | Call Rock Solid Handyman (303-578-2218) for Brighton on-call pricing; paste the RTD questions into the worker session before Mon Nov 2 14:00 | Both today |
| 2026-10-30 | Govcon | Aurora ash B-4799: ask Alex whether YMS holds a Colorado QS pesticide licence; optional Teams pre-bid today 15:30 MDT | Skip the pre-bid unless the licence is confirmed |
| 2026-10-29 | Govcon | Make the PioneerLeads repo private today: the DCSD bid price, the EIN and a markup are still in its git history after the scrub, and the repo is public | Still public at 07:00 MDT Oct 30. Settings, Danger Zone, change visibility; these ops docs publish there too |
| 2026-10-28 | Govcon | Call the generator subs for Parker (due Nov 6) and Douglas 037-26 (due Nov 5); have one firm price both | Today, Fri Oct 30; both bids are inside a week |
| 2026-10-28 | Govcon | Littleton on-call doors: attend the Nov 3 garage walk and bid both pools, or drop both ($100k a year each, $100,000 bond, 2-hour response) | Bid only if a door sub and the bond are in hand by Nov 2; otherwise drop |
| 2026-10-28 | Govcon | Larimer jail fire alarm: a VESDA-certified sub by Mon Nov 3 or it goes NO | Drop unless a sub is found by Friday |
| 2026-10-27 | Govcon | Reactivate the GovTribe subscription (lapsed Oct 26 about 22:00 MT) | 80 hours dark on Oct 30; restart at govtribe.com/account, the loop's state feed is gone without it |
| 2026-10-27 | Govcon | Approve or deny the Gmail sends waiting in the HQ session; today's is the reply to Conor Parrish (FACT Water) on El Paso | Approve today: FACT is the only water-treatment sub engaged and the pricing date is Mon noon |
| 2026-10-27 | Govcon | Forward the Parker generator RFP PDF to Brad Orgill at Colorado Standby; answer Alex's RTD questions; get the H2 tech's photo ID to CDOC | All three are sends only you can make |
| 2026-10-27 | Govcon | 27J Brighton HS RRHS, walk Wed 10:00, no sub pricing | Drop it unless you can price it yourself today |
| 2026-10-27 | Govcon | What happened to Colorado Springs R26-077MZ, Westminster, Arapahoe, Adams County and DCSD | One line each so the record is complete |
| 2026-10-19 | Govcon | Submit Colorado Springs Parks Maintenance On-Call R26-077MZ by Tue Oct 20, 2pm | Outcome unknown as of Oct 27 |
| 2026-10-15 | Govcon | The Breckenridge summit company price reply: was it sent? | Answer in the loop session or here; the loop was archived with the question open |
| 2026-10-15 | SpeedRun Social | Apple Pay failure on live Checkout | Read the Stripe check endpoint output and fix the wallet config |
| 2026-10-14 | SpeedRun Social | Set NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY in Vercel and redeploy | Do it; the card-in-dialog flow you asked for on Oct 13 is shipped but dark |
| 2026-10-14 | SpeedRun Social | Supabase storage quota, locked three times Oct 6 to 9 | Raise the plan; customers lost a week of media |
| 2026-10-05 | SpeedRun Social | Where deploys run (laptop vs always-on machine or CI) | Move the gate off the laptop now. A 4-core cloud container installed, type-checked, linted and built the production branch in under five minutes on Oct 18 (proof session). Put the deploy secrets in the cloud environment and run new SpeedRun sessions there; the Mac froze Oct 18 under eight parallel build agents, #155 was blocked Oct 16, #136 stalled Oct 2 |
| 2026-10-18 | SpeedRun Social | Items the Blaze session is holding for Luke (its 20:21 report): "send" for the founder notes to ayurvedashri and admitly; decisions D1, D3, D4, D5 (E22 and E23 were decided Oct 26); the Supabase Micro upgrade; the Stripe and Vercel settings; whether Go Explore Iran (an Iran tour business) may appear in the showcase given sanctions exposure; whether Premier Home Services' June and July posts stay in the showcase | Answer in the Blaze session. Keep Go Explore Iran out of the showcase until a sanctions check says otherwise; ask Premier before showing their posts |
| 2026-10-18 | SpeedRun Social | How many agents may build on the Mac at once | Two, with one shared `bun install`; the orchestrator asked the Blaze session for this on Oct 18 and it should be a rule in that session's CLAUDE.md |
| 2026-10-18 | Govcon | Recover the Workspace admin login `luke@brownbisonco.com` | Sign in with that address, not the Gmail; use Forgot password, which goes to the recovery phone or email given at signup. Then store it in a password manager. No session can do this |
| 2026-10-14 | Govcon | Commit the send_gov_intros.py import guard | Do it; uncommitted safety fix on a script that sends real mail |
| 2026-10-01 | Govcon | Parker bid due date | One line |
| 2026-10-01 | POE | Commercial terms with Radius | Write them down so the venture can be prioritised honestly |
| 2026-09-25 | POE | Five parked decisions (territory map, merge 91 duplicates, delete 9 files, subject line, Partner vs Pipeline); CDW merge closed Oct 16 | Defaults in `poe-radius.md`; send to Cole as one message |
| 2026-09-18 | SpeedRun Social | Google Ads on or off | Off until a stranger can Connect |
| 2026-06-04 | SpeedRun Social | Vercel Pro for 5-minute cron | Upgrade once there is one paying customer |

## Closed

| Date | Venture | Decision | By | Why |
| --- | --- | --- | --- | --- |
| 2026-10-29 | Govcon | TCF boiler and water-treatment DQ 2027000037 submitted on BidNet; proposal copy sent to H2 at H2 pricing at 13:13 MDT | Luke, with H2 Global | HQ commit 5adc654; worker brief Oct 30 |
| 2026-10-29 | Govcon | El Paso 26-074 water scope routed to FACT Water after H2 declined and referred them; Summit Laboratories held as backup | HQ session, on Silas's referral | HQ commits 4bc80df, 5528907 |
| 2026-10-29 | POE | The name is Pipeline Orchestration Engine; never-imported files are kept a year, not a day, before Health offers to delete them | Cole | ROE commits b999a22, fab9895 |
| 2026-10-28 | Govcon | DCSD 003-27 mowing submitted; opens Oct 29 14:00 | Luke, with Alex Ditto | Worker brief Oct 28 |
| 2026-10-26 | SpeedRun Social | Free plan covers one connected social account; quiet free accounts are paused nightly; the Monday digest carries the $19 founding price | Luke | Blaze session, deploy #201 |
| 2026-10-16 | POE | CDW LOGISTICS merged into CDW; cdwg.com and cdw.ca left open | Cole | Commits 066e1b91 and a97baf38 |
| 2026-10-18 | SpeedRun Social | The green gate runs in a cloud container; the laptop is not required | Orchestrator proof session | Install, tsc, eslint and build all green on 4 cores; two real defects found (64 leaking tests, `.next/dev` corruption from the security-headers test) |
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
