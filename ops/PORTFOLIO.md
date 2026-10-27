# Portfolio brief

Owner: Luke Adams. Orchestrator: Claude (this session, plus the weekday check-in routine).
Updated: 2026-10-27 (weekly brief, a day late: the Oct 20 to Oct 26 check-ins did not fire; the Oct 20 one was delivered on Oct 27). One page. Read this first; the per-venture scorecards hold the detail.

## The three ventures

| Venture | What it is | Stage | North star | Status today |
| --- | --- | --- | --- | --- |
| [SpeedRun Social](speedrun-social.md) | AI social autopilot for small businesses (the Blaze.ai replica), Brown Bison LLC | Live, pre-revenue | Paying customers | 34 deploys in the week (#170 to #203). Free plan now covers one social account, a second connect opens the $19 founding price, quiet accounts are paused nightly, the Monday email carries the offer. Still 0 paying; 6 of 74 users signed in last week. CI moved to GitHub-hosted runners Oct 26; deploys still run on the Mac and were held four days while the lid was closed on battery |
| [POE](poe-radius.md) | Partner Orchestration Engine for Radius Channels (Cole), on top of HubSpot | v1 build, in production use | Booked Meaningful Meetings for Radius reps | 30 commits Oct 20 to 23, all from Cole's live feedback on the upload flow: confidence badges, split cells, reps carried down blocks, "relationship" wording, email on file beside the score, functions moved next to the database. Nothing since Oct 23. Five decisions still parked |
| [Brown Bison govcon](govcon.md) | Municipal HVAC, facilities and grounds contracts; hourly bid-watch loop with Gmail, BidNet login and a live dashboard | Bidding, 8 GO bids, sub pricing in hand on 0 of 8 | Awarded contracts | TCF boiler walk today 10am with H2 Global attending; 27J Brighton HS walk and Littleton 2126 walk tomorrow; TCF quote due Thu 5pm; Parker 26-028 rough pricing sent to Rich Oct 20; GovTribe subscription lapsed last night |

## Last week scored (Oct 19 to Oct 26)

| Venture | Done | Slipped | Blocked |
| --- | --- | --- | --- |
| SpeedRun Social | #170 to #203: founding price ($19) in the trial prompt, out-of-credits modal and Monday digest; free-plan wording fixed on about 150 pages and annual prices pulled from 89; Followers tile from real follower counts; connect-failure reasons captured after one customer failed Facebook five times; free plan limited to one connected account with an upgrade offer on the second; nightly release of quiet accounts (16 accounts in 11 workspaces on the first dry run); seven neutral-ranking test pages built, switch off; CI revived on GitHub-hosted runners. | First paying customer, for the second week. The seven paywall workspaces produced 0 upgrades. PR #1 merge. Stripe publishable key, Supabase upgrade, D1 to D5 as a set (E22 and E23 were decided Oct 26). | Four days of deploys held because the Mac lid was closed on battery (Oct 21 to 25) |
| POE | Upload flow rebuilt around Cole's CDW list: multi-company cells split, reps carried down blocks, 50 sellers looked up per list, websites shown as text not links, low confidence badged red, medium for uncertain, uploads confirm and ask nothing more, "claim" became "relationship", named rep with no email counts as Mapped with a disclaimer, email-on-file beside the POE score, server functions moved to Portland beside the database. | M2 accuracy check (was due Oct 22). Sandbox deal delete. The five parked decisions, now 32 days old. | Cole's decisions |
| Govcon | The venture now has a two-session loop: an HQ scanner that logs into BidNet and SAM.gov hourly, a worker that reads Gmail and GovTribe and writes a morning brief and a live dashboard. Parker 26-028 rough-draft pricing went to Rich on Oct 20 (visits without filters, filters at cost plus 15%). Exhibit G for the TCF boiler went to CDOC Oct 26. H2 Global lined up to attend the TCF walk. | Colorado Springs R26-077MZ, Westminster, Arapahoe, Adams County and DCSD no longer appear on the loop's board; their outcomes are not recorded anywhere I can read. Parker document and Rich's two questions still not closed. send_gov_intros guard still uncommitted. Sub pricing in hand on 0 of 8 GO bids. | GovTribe lapsed (payment is Luke's); Bonfire has no login so Parker 26-028 addenda are unseen; SAM.gov API erroring; the Brighton handyman outreach waits on a Gmail send approval in the HQ session |

## This week's top 3 per venture (Oct 26 to Nov 2)

Govcon stays first this week: three walks and a quote inside 72 hours, and the bid feed is dark until GovTribe is paid.

**Brown Bison govcon**
1. Today: TCF boiler walk at 10am (H2 Global attends; confirm Garvin got Exhibit G). Reactivate GovTribe. Forward the Parker generator RFP PDF to Brad Orgill at Colorado Standby. Decide 27J Brighton HS: drop, or price it yourself today with no sub.
2. Wednesday: 27J Brighton HS walk 10am and Littleton 2126 walk 2pm; Rich's approval on the Parker 26-028 pricing. Thursday 5pm: TCF quote in.
3. Get sub pricing on the 8 GO bids (0 of 8 today): the 7 plumbers and the Littleton trades have not replied; answer Alex's RTD questions so landscaping stays with him.

**SpeedRun Social**
1. Watch the first release sweep and the one-account rule for complaints; 16 accounts in 11 workspaces get paused, and grandfathered users have until Nov 9.
2. Decide D1, D3, D4 and D5 and set the Stripe publishable key; the founding price is now quoted in three places and the checkout behind it is still dark.
3. Keep the Mac on power and plugged in during gate windows, or move the gate to the GitHub runners now that CI runs there: four days of held deploys last week was the laptop, not the code.

**POE**
1. Send Cole the five parked decisions with defaults; he is giving decisions daily when asked in the product, so ask there.
2. Record the M2 accuracy number.
3. Delete the sandbox deals and re-match the leftovers.

## Blockers only the owner can clear

| Venture | Blocker | Why it matters |
| --- | --- | --- |
| Govcon | GovTribe subscription lapsed Oct 26 about 22:00 MT | The loop's state and federal feed is dark; the dashboard shows the source as BLOCKED |
| Govcon | Gmail send approval in the HQ session (Brighton handyman outreach), the Parker generator RFP forward, Alex's RTD questions, the H2 tech's photo ID | Every one is a send or a signature; no session may do them |
| Govcon | Bonfire login for Parker 26-028 | Addenda on the live Parker bid are unseen |
| SpeedRun Social | D1, D3, D4, D5; Stripe publishable key; Supabase Micro upgrade; Vercel settings | The $19 offer is live in copy and email, and the in-app checkout behind it is dark |
| SpeedRun Social | Deploys need the Mac awake and on power | Nine commits sat four days last week |
| POE | Five decisions parked since 2026-09-25 (see scorecard) | Territory map, duplicate merge, file delete, naming, subject line |
| POE | Commercial terms with Radius | Still not written anywhere |

## Open questions for Luke

1. What happened to Colorado Springs R26-077MZ (due Oct 20), Westminster, Arapahoe, Adams County and DCSD? None is on the loop's board now.
2. When is the Parker 26-028 bid due, and did Rich approve the pricing?
3. What are the terms with Radius for POE (hourly, fixed, equity, favour)?

## Cadence

See [CADENCE.md](CADENCE.md). Short version: a weekday check-in updates the three scorecards and surfaces the single next action per venture; a Monday brief rewrites this page; every owner decision goes in [DECISIONS.md](DECISIONS.md). The check-ins between Oct 20 and Oct 26 did not run; this brief covers the gap from the sessions and commits.
