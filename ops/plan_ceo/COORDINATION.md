# CLOUD HQ BACK ON (Luke, 2026-11-05 ~11:00 MT, in the HQ chat: "4x the work on both projects ... maxing out our credit allotments")

Luke's word in HQ wins (rule below). Together with his 2026-11-03 standing order ("sessions act without asking ...
stop only at a password, 2FA code or CAPTCHA", ops/DECISIONS.md on claude/portfolio-ops), this ends the 10/30
stand-down. As of 2026-11-05 18:15Z the cloud HQ session scans hourly, triages, runs sub outreach and follow-ups
from luke@brownbisonco.com through scripts/gmail_api.py, and sends Luke the 8-line board; the daily CEO plan and
the WORKER hourly routine are re-enabled.

Facts at the switch-back: the local Mac heartbeat crashed 2026-10-30 17:46 MDT (7 h after taking over), restarted
11/03, stalled twice 11/04 and had no stamp for ~20 h on 11/05 (its own watchdog email). On 11/03 it closed nine
bids and released nine subs on an "insurance drop default" (policy binds 11/13) and Luke skipped El Paso 26-074
after FACT Water delivered pricing + SOQ. No portal scan ran anywhere 10/30 14:37Z to 11/05 18:15Z.

Rules to avoid double-sends with the local operator: both sides `git pull` before any send; every send is logged in
ops/outbox/<date>/sent.json and in the bid's sub-outreach.md; search Sent for the subject before sending; the
local operator does not re-send anything already in Sent. If Luke says "local only" again, record it here first.

# STAND DOWN: Brown Bison runs from the local Mac operator only (Luke, 2026-10-30 ~10:05 MT)

Luke's decision, given to the Claude desktop master session that holds CEO authority over Brown
Bison since 2026-10-30: **"Local only."** The local heartbeat session on his Mac (repo
`~/brown-bison-gov`, CRM at crm.brownbisonco.com) is the single Brown Bison operator: outreach,
sub replies, buyer questions, scans, pricing, packages, the CRM of record, and every update to Luke.

## What this cloud workspace (HQ and the hourly WORKER) does now
- Nothing that sends: no email from luke@brownbisonco.com, no outreach, follow-ups, RSVPs or
  buyer questions.
- No scans, no pipeline edits, no dashboard refresh. Read-only, and only if Luke himself asks here.
- Leave the repo as it is. The local operator has pulled what it needs from this branch (El Paso
  26-074 technical draft and vendor questions, RTD questions, sub-outreach files, today's outbox
  `ops/outbox/2026-10-30/sent.json`, `bids/_pipeline.md`, `memory/MEMORY.md`, `CLAUDE.md`).
- If Luke changes his mind in his chat with HQ, his word wins; record it here first.

## Open threads the local operator now owns (state at hand-over, 2026-10-30 15:24Z)
- El Paso 26-074 water treatment: FACT Water (Conor Parrish) prices + 3 references + tech bio by
  Mon 11/02 noon; County due Wed 11/04 2:00 PM, two envelopes, RMEPS; H2 Global declined.
- Douglas County UPS 039-26: 10 firms asked, RESA declined; prices by Mon noon; due Wed 11/04 3:00 PM.
- Metro Water B-26-019 switchgear: RESA (Vitor Teixeira) has the package, pricing by Thu 11/05.
- COS R26-080JW on-call janitorial: EC Company (Ryan Steinseifer) engaged, pricing by Mon 11/16.
- Weld SD6 Franklin MS coiling grille: 6 door firms asked, 0 replied; MANDATORY walk Mon 11/02
  10:00 Greeley (a sub stands there or the bid is dropped); bid by email Tue 11/10 2:00 PM.
- Parker 26-021-1 generators: Colorado Standby has the RFP and Town price sheet, numbers by Tue
  11/03; due Fri 11/06 2:00 PM.
- Weld County Jail RTU B2600111: AccuTemp (Nick Yaw) covers the Thu 11/05 9:00 walk; pricing 11/12.
- RTD 126DM016: questions close Mon 11/02 2:00 PM (`bids/rtd-bus-shelter-maintenance/questions-for-rtd.md`).
- Douglas County generator 037-26: local call is no-go (own-employee technician rule).
- CDOC Trinidad DQ 2027000037: withdrawn 10/30.

Luke's standing rules in `CLAUDE.md` here (8-line board updates, no links in outside email, H2
Global first for water treatment, no heavy civil, humanize every email, complete packages) now live
in the local operator's `docs/ops/orchestration.md` as well.
