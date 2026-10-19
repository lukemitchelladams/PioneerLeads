# Portfolio brief

Owner: Luke Adams. Orchestrator: Claude (this session, plus the weekday check-in routine).
Updated: 2026-10-12 (Monday brief). One page. Read this first; the per-venture scorecards hold the detail.

## The three ventures

| Venture | What it is | Stage | North star | Status today |
| --- | --- | --- | --- | --- |
| [SpeedRun Social](speedrun-social.md) | AI social autopilot for small businesses (the Blaze.ai replica), Brown Bison LLC | Live, pre-revenue | Paying customers | Healthy, billing live, shipping daily again (#147 to #154 since Oct 14); seven free workspaces hit the paywall Oct 20 to 27; deploy lane blocked by Mac load |
| [POE](poe-radius.md) | Partner Orchestration Engine for Radius Channels (Cole), on top of HubSpot | v1 build, in production use | Booked Meaningful Meetings for Radius reps | Moved to Radius's main HubSpot portal Oct 9; ZoomInfo free enrichment on every account; System Map totals for Luke's map; 6 decisions still parked on Cole |
| [Brown Bison govcon](govcon.md) | Municipal HVAC and facilities contracts; Town of Parker HVAC on-call bid in progress; local CRM sending gov intro emails | Bidding | Awarded contracts | Active daily on Luke's Mac (CRM dashboard build, intro emails); Parker bid document still not in hand; Rich at York's two questions open since Oct 9 |

## Last week scored (Oct 5 to Oct 12)

| Venture | Done | Slipped | Blocked |
| --- | --- | --- | --- |
| SpeedRun Social | Nothing after Oct 5. | All three: converting the six first-post workspaces, upgrade surfaces, deploys off the laptop and PR #1. | Luke's time |
| POE | HubSpot moved from the sandbox to the main portal with ids re-matched by website and email (31 of 33 accounts, 175 of 176 reps). ZoomInfo free search now enriches every account and finds domains; the paid call is documented for later. One-upload lane. System Map read-only totals for Luke's map, behind a hashed key. | The six parked decisions, now 17 days old. M2 accuracy check. The 736 sandbox deals still need the Health sync and delete. | Cole's decisions |
| Govcon | Nothing. | Everything. | Luke's answers |

## This week's top 3 per venture (Oct 12 to Oct 19)

**SpeedRun Social**
1. One deploy this week, whatever it is. A week of silence on the revenue venture while POE got six commits is the wrong allocation.
2. Convert the six free workspaces that published: confirm the first-post-live email sent, and see who hit the cap.
3. Merge PR #1.

**POE**
1. Run the Health page deal sync against the main portal and delete the 736 sandbox deals.
2. Send Cole the six parked decisions. Seventeen days is too long.
3. M2 accuracy check on the re-matched data.

**Brown Bison govcon**
1. Get the Parker solicitation PDFs into the bid folder and answer Rich at York's two questions.
2. Commit the send_gov_intros.py import guard; finish the repo rename and make-private.
3. CRM dashboard, morning brief first.

## Blockers only the owner can clear

| Venture | Blocker | Why it matters |
| --- | --- | --- |
| SpeedRun Social | Zernio payment method (status unverified since Sept 3) | Every external signup hits a dead Connect button without it |
| SpeedRun Social | Google Ads on or off | $20 a day was the largest line item while the funnel was broken |
| SpeedRun Social | Vercel Pro (cron every 5 min vs once a day) | Scheduled posts only publish on the daily run |
| POE | Six decisions parked on 2026-09-25 (see scorecard) | Territory map, duplicate merge, CDW domains, naming, subject line |
| POE | Commercial terms with Radius | Not visible anywhere in the repo; needed to prioritise against the other two |
| Govcon | Entity name, bid status, bonding capacity, licenses | Cannot plan a pipeline without knowing who bids and what they can sign |

## Open questions for Luke

1. Was the Estes Park 2027 HVAC proposal submitted by Sept 24? When is the Parker bid due?
2. What are the terms with Radius for POE (hourly, fixed, equity, favour)?
3. Resolved Oct 19: these docs now live in `lukemitchelladams/PioneerLeads` under `ops/`, the Brown Bison workspace repo. The retired portfolio repo copy is frozen.

## Cadence

See [CADENCE.md](CADENCE.md). Short version: a weekday check-in updates the three scorecards and surfaces the single next action per venture; a Monday brief rewrites this page; every owner decision goes in [DECISIONS.md](DECISIONS.md).
