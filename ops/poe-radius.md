# POE scorecard

Client: Radius Channels (Cole). Product: Partner Orchestration Engine, a decision layer on top of HubSpot that turns vendor, partner and customer data into one evidence-backed next action per account.
Repo: `ColeRADIUS/ROE` (name retired; the product is POE). Stack: Next.js 16, Supabase, Claude API, Vercel. Updated 2026-10-16.

## Where it stands

| Signal | Value | Source |
| --- | --- | --- |
| Last shipped | 2026-10-15: Teams live. Everyone is on one vendor's team or is Leader / Admin, set on the Admin page; a team member never picks a vendor. Supabase Management credential is now a network secret on the cloud environment. Before that, 2026-10-14: partners matched to their HubSpot companies on their own when certain (66 linked, 26 to 92; 180 more deals reach a partner; 48 wait on a person); uploads no longer search the web for websites, at Cole's word, so the upload step costs nothing. Before that, 2026-10-12: HubSpot syncs run on their own every four hours from pg_cron (Cole's ask); deal sync pages by id past HubSpot's 10,000-result cap, since the main portal holds more deals than that; a page per person at /contacts; System Map served from a ten-minute cache after HTTP 500s on Luke's console; 15-second cap on every HubSpot call | commits 71f8ff03, e1111b7e, b60f7860, 3e7ec411 |
| Shipping model | Straight to main after lint, typecheck and build; no PRs, no issues | CLAUDE.md |
| Data in production | Main portal. First full deal pass finished Oct 13 (22:15 to 23:40 UTC, no errors): 12,131 of 15,736 deals have an account, across 6,013 accounts; 5,793 customer accounts created. 285 sandbox-era list rows re-matched: 95 more matched, 92 wait for review. One /review page now holds everything waiting on a person (871 found websites as of Oct 13). | commits 52114f84, 1c86817a, f88b6861 |
| Migrations | Applied directly by Claude with a scoped Supabase credential; `supabase/APPLIED.md` is the record | CLAUDE.md |
| v1 scope | Vendor Whitespace and Partner Path on one pilot vendor's real list. ICP Match and Signal Alert come after | CLAUDE.md |
| Commercial terms | Not recorded anywhere visible | gap |

## Parked since 2026-09-25, waiting on Cole

1. Druva's territory map: which AE covers which states. Entered on the vendor page.
2. Merge the 91 duplicate accounts (Health page, Database hygiene, Merge all). Safe; one click.
3. Delete the 9 never-imported files older than a day. Same section.
4. Outreach subject line: "Introduction:" or "Introduction," (one failing test in `test:scoring:whitespace`).
5. Partner Orchestration Engine or Pipeline Orchestration Engine. Code and deck disagree.
6. CDW's domains: merge CDW LOGISTICS into CDW, or move `cdw.com` and `cdwg.com`.

Plus one check that only Cole's next upload can trigger: the first live runs of the State, Vendor and Covers As Of columns and the website and state search.

## Next actions, in order

1. Send Cole the six decisions above as one message with a recommended default for each. Recommendation: Partner Orchestration Engine (matches CLAUDE.md), "Introduction:", merge CDW LOGISTICS into CDW, Merge all, delete the 9 files.
2. Done Oct 9: POE reads the main portal. Remaining: Health page deal sync, then delete the sandbox deal rows, then re-match the 2 accounts, 6 partners and 1 rep left for a person.
3. M2: the 500-account accuracy check. Record precision and recall against a human-labelled sample.
4. M3: the eight-section brief and Excel export. This is the deliverable the build plan calls the MVP.
5. Then, and only then, ICP Match and Signal Alert.

## Risks

- ZoomInfo: the free company search is in v1 and used everywhere; the paid details call was removed Oct 5 at Cole's word and documented for restoration. CLAUDE.md now records both. Resolved.

- Climb order and transaction history: API access still unconfirmed. Biggest open risk from the build plan.
- ZoomInfo entitlements unconfirmed; cut from v1 by design.
- Planned move from Vercel to Cloudflare Workers is unscheduled; the xlsx parser and long-running Server Actions need checking before it happens.
- No written commercial terms. Decide what this venture is worth per week of Luke's time.

## Targets

- All six parked decisions closed by 2026-10-08.
- Live HubSpot portal by 2026-10-15.
- M2 accuracy number recorded by 2026-10-22.
