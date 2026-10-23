# Brown Bison government contracting scorecard

Entity: Brown Bison (Brown Bison Holdings LLC is the Stripe merchant name; confirm the legal name used on bids). Work lives on Luke's Mac at `/Users/thecreator/brown-bison-gov`, pushed to GitHub `lukemitchelladams/PioneerLeads` (repurposed, branch `claude/zealous-cerf-el4iek`; rename and make-private still a manual GitHub step). Output folder: `~/Downloads/BrownBison_GovRamp_2026-09-17/`. Updated 2026-10-19, 07:00 MDT.

Corrected on 2026-10-14: everything in the Oct 1 version of this file was inferred from a single Drive RFP. The facts below come from Luke's own sessions.

## What is known

| Signal | Value | Source |
| --- | --- | --- |
| This week's pipeline | From the bid loop's 06:08 MDT brief on Oct 19. (1) City of Colorado Springs Parks Maintenance On-Call, RFP R26-077MZ: a 5-year pool up to $3M a year across 17 categories; fit is Landscape Construction (Alex), Janitorial and Striping with subs; hourly rates are not scored, only the narrative, which is drafted at `bids/colorado-springs-parks-maintenance-on-call/proposal-draft.md`; due Tue Oct 20, 2pm on BidNet; Luke fills Exhibit 1, three references, Alex's rates plus markup in Appendix A, signs and uploads. (2) Westminster Public Schools: walk-through today Mon Oct 19, 2pm, Sherrelwood Elementary, 8095 Kalamath St; the late RSVP sits in Luke's Drafts. (3) Arapahoe County turfgrass: invite-only Teams meeting today 1:30pm, late-invite draft unsent; questions due Wed Oct 21 noon. (4) Adams County streetlights: mandatory walk Wed Oct 21, 10am, Colorado Air and Space Port, Watkins; needs an electrician sub's name. (5) Littleton: Q&A posts Tuesday. 7 plumbers emailed over the weekend. Nothing from Alex or Rich Carroll yet. | bid research session, Oct 19 |
| Live bid | Town of Parker, Colorado, HVAC on-call. Partner contact "Rich at York" has two open questions: chiller make, model and tonnage, and required response time. Neither is in hand; both are in the bid's equipment schedule and scope. | session "Brown Bison government contracting bid research", Oct 9 |
| Bid document | Not obtained. Cloud sessions are blocked from bidnetdirect.com, rockymountainbidsystem.com, parkerco.gov and sam.gov. BidNet downloads need the vendor login. Town procurement: 303-805-3188. | same |
| Bid folder | `bids/town-of-parker-hvac-on-call/` with checklist, equipment schedule and a fill-in reply for Rich at `vendor-questions-york.md` | same |
| Estes Park | No-bid, confirmed by Luke Oct 15: the mandatory Sept 8 pre-bid was missed. Marked in the repo. Worth one email to Robert Schumaker for the bid tabulation, the best competitor pricing intel available for a 19-site municipal PM contract. | bid research session, Oct 15 |
| DCSD bid | A Douglas County School District HVAC bid from Alex Ditto. Luke spoke with Alex on or before Oct 18; Alex sends the bid Monday Oct 19 (the bid session wrote "Mon 10/20", but Oct 20 is a Tuesday). Luke also emailed himself about it, which no session could read: Gmail is not connected in the cloud session and this session's Gmail tool fails to authenticate. Drive has nothing, HubSpot has no Alex Ditto. A `bids/dcsd-hvac/` playbook is built (price structure, fingerprinting under C.R.S. 22-32-109.8, E-Verify, scored narrative). Blocked on Luke. | same |
| Decision recorded | All landscaping work routes to Alex Ditto | same |
| Open question | On Oct 14 at 10:29 MDT Luke asked the loop session whether it ever replied to the Breckenridge summit company that their price felt high and looked for alternatives. The session was archived with that question unanswered. | loop session transcript |
| CRM | A local CRM: `data/crm_sync.py`, `data/crm_morning_brief.py` (daily brief docx and PDF), `data/crm_ingest_emails.py`, `data/send_gov_intros.py` sending intro emails through Mail.app. The send log held 288 lines on Oct 14. Eight drafts queued with an Army address fix. | session "Guard send_gov_intros.py", Oct 14 |
| Bid loop, new | The bid research session now runs as an hourly scheduled check (fired 06:05 MDT Oct 19): it reads Gmail (the BidNet notice and the GovTribe digest were read this morning, so Gmail is connected there now), searches GovTribe, runs a bid-watch script (BidNet public pages failed with tunnel errors; SAM.gov needs SAM_API_KEY), writes a 72-hour deadline brief and commits to PioneerLeads (5e0cb1a). | session events, Oct 19 |
| Live session, old | ARCHIVED Oct 14 at 10:29 MDT, so the daily reports asked for on Oct 14 will not arrive from it. Until Oct 14 it ran as an autonomous heartbeat loop on Luke's Mac (ticks every 20 to 40 minutes): sweeps Gmail and iMessage, runs the CRM queue, sends the morning brief to Gmail, keeps an Obsidian vault at `~/Documents/ClaudeOpsVault/Sessions/2026-09-17 Brown Bison gov-contracting ramp.md`, and spawns reviewer and research agents. Rule it runs under: only passwords, accounts, payments and signatures are Luke's. On Oct 14 Luke asked for the CRM dashboard at 10x scope. | session events, Oct 14 |
| CRM dashboard | CRM v2 live at https://crm.brownbisonco.com (passcode in CRM/CRM_ACCESS.txt): every bid's files, emails, due dates and plans. CRM v21 as of Oct 14 06:43; 11 Claude tasks open or doing. Adversarial review found 0 critical, 0 high, 3 medium, 5 low; fixes being applied. | same |
| Safety fix | `send_gov_intros.py` could send real email on import because two other scripts imported it; guarded Oct 14, uncommitted | same |
| Mailbox | brownbisonco.com mail is live on Google Workspace. Public DNS (Vercel nameservers) on Oct 18: MX `1 smtp.google.com`, `google-site-verification` TXT, SPF `include:_spf.google.com`, DKIM `google._domainkey` published, DMARC `p=none; rua=mailto:luke@brownbisonco.com`. DKIM only comes out of the Workspace Admin console, so the tenant exists, is verified and was set up by someone signed in as its admin. The admin login is the first user created at signup, `luke@brownbisonco.com`, a separate Google account from the personal Gmail. On Oct 18 Luke could not find the login; signed in as the personal Gmail, Google says the account cannot be upgraded to Workspace, which is expected: a Gmail account is never upgraded, the business tenant is its own login. No session holds the password (loop hard rule). The loop's heartbeat still listed this setup as "next" on Oct 14, so the signup happened between Oct 14 and Oct 18. | DNS lookup Oct 18; loop heartbeat Oct 14 |
| HubSpot | Has a bare "Town of Parker" company record, no contacts or notes | Oct 9 session |

## Unknowns still open

- Legal entity on the bids, UEI, CAGE, bonding capacity, who holds the mechanical license.
- Whether the Estes Park proposal was submitted.
- Where the Parker bid stands: due date, pre-bid date, whether the document has been downloaded locally yet.

## Orchestration

This venture already runs its own loop. The orchestrator does not duplicate it. On Oct 14 the loop session was asked to send this session one status a day and an immediate line on any bid due inside 7 days or a partner question unanswered for 2 days.

## Next actions, in order

0. Tuesday Oct 20, 2pm: Colorado Springs R26-077MZ submitted. Today: both RSVP drafts sent, Westminster walk at 2pm, Arapahoe meeting at 1:30pm. Wednesday 10am: Adams County walk.
0b. Monday Oct 19: when Alex Ditto's DCSD bid arrives, drop the files into `bids/dcsd-hvac/docs/` (or connect Gmail) and the bid research session builds the requirements matrix and pricing model the same day.
1. Get the Parker solicitation PDFs onto the Mac and into `bids/town-of-parker-hvac-on-call/docs/`, then answer Rich's two questions from the equipment schedule and scope. This has been open since Oct 9.
2. Commit the `send_gov_intros.py` guard. An uncommitted safety fix on a script that sends real email is a liability.
3. Finish the GitHub repo rename and make-private step so the bid workspace is not public under the PioneerLeads name.
4. Write the entity, registrations and bonding facts into this file.
5. Then the CRM dashboard, with the morning brief as its first screen.

## Targets

- Rich's two questions answered and the Parker bid submitted by its due date (date unknown; find it today).
- Entity and registrations recorded by 2026-10-21.
