# Portfolio brief

Owner: Luke Adams. Orchestrator: Claude (this session, plus the weekday check-in routine).
Updated: 2026-10-19 (Monday brief). One page. Read this first; the per-venture scorecards hold the detail.

## The three ventures

| Venture | What it is | Stage | North star | Status today |
| --- | --- | --- | --- | --- |
| [SpeedRun Social](speedrun-social.md) | AI social autopilot for small businesses (the Blaze.ai replica), Brown Bison LLC | Live, pre-revenue | Paying customers | Billing live; 23 deploys since Oct 14 (#147 to #169); scoreboard Oct 18: 45 signups in 30 days, 15 accounts connected, 6 active, 0 paying. Seven free workspaces cross the paywall Oct 20 to 27. The Mac froze Oct 18 under eight build agents; the gate is proven in a cloud container |
| [POE](poe-radius.md) | Partner Orchestration Engine for Radius Channels (Cole), on top of HubSpot | v1 build, in production use | Booked Meaningful Meetings for Radius reps | Oct 16: CDW merged on Cole's call, mapping worklist ranked per vendor, signed-in pages 14.7 s to 0.16 s, Admin sub menu. Nothing since Oct 16. Five decisions still parked on Cole |
| [Brown Bison govcon](govcon.md) | Municipal HVAC, facilities and grounds contracts; local CRM; now an hourly bid-watch loop with Gmail | Bidding, five live this week | Awarded contracts | Colorado Springs parks on-call due Tue 2pm; Westminster walk today 2pm; Arapahoe turfgrass meeting today 1:30pm; Adams County streetlights walk Wed 10am; DCSD from Alex; Parker still has no document |

## Last week scored (Oct 12 to Oct 19)

| Venture | Done | Slipped | Blocked |
| --- | --- | --- | --- |
| SpeedRun Social | 23 deploys: Stripe embedded checkout, "Free to start" copy, upgrade pop-up, onboarding connect step, customer showcase, 40 dead post links repaired, engagement numbers from Zernio, first-party visit counter, approve path adds connected platforms. Sealis cross-post found and both customers told. Cloud gate proven. | First paying customer (target was Oct 15). PR #1 merge. Stripe publishable key. Supabase plan. | Owner items: D1 to D5, Stripe key, Supabase, showcase calls |
| POE | Partners matched to HubSpot companies on their own; Teams live; CDW LOGISTICS merged into CDW; mapping worklist ranked (Druva 9 ready to book, Illumio 31, Cloudflare 11); scheduled relink fixed; Admin sub menu. | M2 accuracy check (due Oct 22). Sandbox deal delete. The five remaining decisions, now 24 days old. | Cole's decisions; CDW's other domains "we will talk about it" |
| Govcon | Estes Park no-bid decided; DCSD playbook built; the loop rebuilt as an hourly bid watch that reads Gmail and GovTribe and commits to PioneerLeads; Colorado Springs narrative drafted; 7 plumbers emailed. | Parker document and Rich's two questions, open since Oct 9. send_gov_intros guard still uncommitted. | Luke's RSVPs, references, rates, signatures and uploads |

## This week's top 3 per venture (Oct 19 to Oct 26)

This week only, govcon ranks first: four dated deadlines inside 72 hours. SpeedRun Social is still where a week of Luke's time compounds most after those pass.

**Brown Bison govcon**
1. Submit Colorado Springs Parks Maintenance On-Call (R26-077MZ) by Tuesday 2pm on BidNet: Exhibit 1, three references, Alex's rates plus markup in Appendix A, sign, upload. The narrative is drafted. About three hours.
2. Show up: send the two RSVP drafts now, then Westminster Public Schools at 2pm today and the Arapahoe turfgrass Teams meeting at 1:30pm today; Adams County streetlights walk Wednesday 10am with an electrician sub's name.
3. DCSD files from Alex into `bids/dcsd-hvac/docs/`; Parker document and Rich's two questions, open since Oct 9.

**SpeedRun Social**
1. Convert the seven free workspaces that hit the paywall this week: answer D1 to D5 in the Blaze session and set the Stripe publishable key so in-app checkout works before they do.
2. Builds off the Mac: start new SpeedRun sessions in the cloud environment, two agents at most on the Mac, and have the Blaze session fix the 64-test leakage so the cloud gate can deploy.
3. Merge PR #1 (overnight-overhaul to main) and make main the deploy branch.

**POE**
1. Send Cole the five remaining decisions as one message with defaults.
2. Record the M2 accuracy number by Oct 22.
3. Delete the sandbox deals and re-match the 2 accounts, 6 partners and 1 rep left for a person.

## Blockers only the owner can clear

| Venture | Blocker | Why it matters |
| --- | --- | --- |
| Govcon | Every submission, RSVP and signature this week | Five bids are in motion and none can be sent by a session |
| SpeedRun Social | D1 to D5, Stripe publishable key, Supabase Micro upgrade, Vercel settings | The in-app checkout is dark and the database reported Unhealthy |
| SpeedRun Social | Showcase calls: Go Explore Iran (sanctions), Premier Home Services (consent) | Both held out until Luke decides |
| POE | Five decisions parked since 2026-09-25 (see scorecard) | Territory map, duplicate merge, file delete, naming, subject line |
| POE | Commercial terms with Radius | Not visible anywhere in the repo; needed to prioritise against the other two |
| Govcon | Entity name, UEI, CAGE, bonding capacity, licenses | Cannot plan a pipeline without knowing who bids and what they can sign |

## Open questions for Luke

1. When is the Parker bid due, and is the Westminster RFP a separate submission after today's walk?
2. What are the terms with Radius for POE (hourly, fixed, equity, favour)?
3. Resolved Oct 19: these docs now live in `lukemitchelladams/PioneerLeads` under `ops/`, the Brown Bison workspace repo. The retired portfolio repo copy is frozen.

## Cadence

See [CADENCE.md](CADENCE.md). Short version: a weekday check-in updates the three scorecards and surfaces the single next action per venture; a Monday brief rewrites this page; every owner decision goes in [DECISIONS.md](DECISIONS.md).
