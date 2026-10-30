# POE scorecard

Client: Radius Channels (Cole). Product: Pipeline Orchestration Engine (Cole's word, Oct 29), a decision layer on top of HubSpot that turns vendor, partner and customer data into one evidence-backed next action per account.
Repo: `ColeRADIUS/ROE` (name retired; the product is POE). Stack: Next.js 16, Supabase, Claude API, Vercel. Updated 2026-10-30.

## Where it stands

| Signal | Value | Source |
| --- | --- | --- |
| Shipped Oct 29 | Fifteen commits from Cole's live feedback, 12:50 to 17:05 MDT: deals on partner cards, account answers and company pages fold behind their count ("7 deals with CDW", a Show deals box); the worklist's deal column is "Partner's deals here"; never-imported files are kept a year, not a day, before Health offers to delete them (18 files, none that old); a list downloads as POE read it (/upload/<id>/download, every row in POE's columns plus the sheet's unread columns); a list may be "Several partners", each row naming its own, and a list filed under one partner whose partner column names other partners on half its rows is split in two; a partner not on the roster can be added from the upload page (vendors stay locked, Cole's rule); HubSpot is saved for good: the company copy that stalled at 21:55 UTC finished all 48,823 companies once a dead GIN index was dropped, a fifth sync step saves every one of the portal's 133,708 contacts every four hours (POE held 6,600), and "copying" reads "saving". Cole also settled the name: POE is the Pipeline Orchestration Engine. | commits fd454a8 to 7fc4f39, Oct 29 |
| Shipped Oct 20 to 23 | Thirty commits from Cole's live feedback on his CDW list: account cells naming several companies are split, a rep named once above a block is carried down to every row, up to 50 sellers per partner list are looked up in HubSpot (short first names too; 34 of CDW's 42 found), found websites are shown as text not links at Cole's malware concern, low confidence is badged red and uncertain finds are medium, exact-name matches are high, websites found below high wait on the Review page by default, the upload lands on a plain confirmation page, "claim" reads "relationship" and "carries" reads "has sold", account boxes are titled Partner Relationships and Book the Meeting, a partner rep named with no email counts as Mapped with a disclaimer and half credit, "Email on file" sits beside the POE score and is not counted in it, Vercel functions moved to Portland beside the Oregon database after Cole asked why Upload was slow (about 70 ms per cross-country query), four duplicate accounts merged, 375 ZoomInfo namesake guesses recorded at low confidence. Before that, 2026-10-16: CDW LOGISTICS merged into CDW on Cole's decision, with HubSpot company 39253378680 and cdw.com (519 more reps saved; CDW claims with a rep 261 to 1,002); CDW's cdwg.com and cdw.ca claims (226) wait on a conversation, Cole: "don't worry about it we will talk about it". /mapping opens on a vendor's worklist ranked by one ladder (Ready to book, Find the rep, Worth a try, No route yet): Druva 9 ready, Illumio 31, Cloudflare 11. Signed-in pages went from 14.7 s to 0.16 s (MFA policy planner fix on 31 tables, cached ladder refreshed by pg_cron). Admin has a Teams and Invites sub menu at Cole's ask. The scheduled relink failed whole after the deal pass because of a bare DELETE; fixed and guarded by a test. Partners now answer to their spellings; 2,063 reps saved from evidence. Before that, 2026-10-15: Teams live. Everyone is on one vendor's team or is Leader / Admin, set on the Admin page; a team member never picks a vendor. Supabase Management credential is now a network secret on the cloud environment. Before that, 2026-10-14: partners matched to their HubSpot companies on their own when certain (66 linked, 26 to 92; 180 more deals reach a partner; 48 wait on a person); uploads no longer search the web for websites, at Cole's word, so the upload step costs nothing. Before that, 2026-10-12: HubSpot syncs run on their own every four hours from pg_cron (Cole's ask); deal sync pages by id past HubSpot's 10,000-result cap, since the main portal holds more deals than that; a page per person at /contacts; System Map served from a ten-minute cache after HTTP 500s on Luke's console; 15-second cap on every HubSpot call | commits 71f8ff03, e1111b7e, b60f7860, 3e7ec411 |
| Shipping model | Straight to main after lint, typecheck and build; no PRs, no issues | CLAUDE.md |
| Data in production | Main portal. First full deal pass finished Oct 13 (22:15 to 23:40 UTC, no errors): 12,131 of 15,736 deals have an account, across 6,013 accounts; 5,793 customer accounts created. 285 sandbox-era list rows re-matched: 95 more matched, 92 wait for review. One /review page now holds everything waiting on a person (871 found websites as of Oct 13). | commits 52114f84, 1c86817a, f88b6861 |
| Migrations | Applied directly by Claude with a scoped Supabase credential; `supabase/APPLIED.md` is the record | CLAUDE.md |
| v1 scope | Vendor Whitespace and Partner Path on one pilot vendor's real list. ICP Match and Signal Alert come after | CLAUDE.md |
| Commercial terms | Not recorded anywhere visible | gap |

## Parked since 2026-09-25, waiting on Cole

Decision 6 closed Oct 16: CDW LOGISTICS merged into CDW, Cole's call; the other CDW domains are open, not declined. Decision 5 closed Oct 29 (Pipeline Orchestration Engine) and decision 3 went moot the same day. Three remain, plus the CDW domains.

1. Druva's territory map: which AE covers which states. Entered on the vendor page.
2. Merge the 91 duplicate accounts (Health page, Database hygiene, Merge all). Safe; one click.
3. Moot Oct 29: Cole set the keep window for never-imported files to a year (18 files, none that old), so nothing is offered for deletion.
4. Outreach subject line: "Introduction:" or "Introduction," (one failing test in `test:scoring:whitespace`).
5. Done Oct 29: Pipeline Orchestration Engine, Cole's word; README and CLAUDE.md now agree with the masthead and deck.
6. Done Oct 16: CDW LOGISTICS merged into CDW. Still open: where `cdwg.com` and `cdw.ca` claims go (226 of them).

Plus one check that only Cole's next upload can trigger: the first live runs of the State, Vendor and Covers As Of columns and the website and state search.

## Next actions, in order

1. Send Cole the three remaining decisions as one message with a recommended default for each: "Introduction:", Merge all, and the territory map as a ten-minute form. He is answering daily in the product (15 decisions on Oct 29), so ask there.
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
