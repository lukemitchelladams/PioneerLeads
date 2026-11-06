# 2026-11-06 ~10:50 MT: NO PHONE IN EMAIL (Luke's hard rule; both operators)

Luke: "i cant have all these fucking guys calling me all fucking day long, we need to try and get information via email and
not always be telling people or letting them call me, because i dont always have all the ifnormation or am the most up to
date because i work all day". From now on, every email to anyone but Luke: no (720) 275-1554 in any format, no call invites
("call me", "give us a call", "call or text", "my cell", "hop on a call", "schedule a call", "best number to reach" ...), and
the four-line signature Luke Adams / Operations Manager / Brown Bison Holdings LLC / luke@brownbisonco.com. Get answers by
email; chase by email (ops/plan_ceo/2026-11-06.md says "the chase is a call": that conflicts, so email unless Luke says
otherwise). Trade words pass
(on-call, service call, call-out, callback response time, emergency calls). Phone numbers on bid forms and proposal documents
stay. The cloud gate (`scripts/humanize_gate.py` phone_problems, both send paths) refuses with "No phone number or call
invite in email (Luke 2026-11-06): answer by email; at most add 'Email is the best way to reach me during the day.'" It
refuses every "call" / "phone" in our own text by default (trade terms, third parties, photos and negations pass), and the
connector `forward` to anyone but Luke. The Mac already has the four-line signature (brown-bison-gov data/brand.py) and its own
check (data/phone_gate.py, commit b277275), but that check is narrower: run against the shared cases in
tests/phone_cases.json (2026-11-06) it misses 68 of 176 invites (e.g. "Can we talk Monday?", "Talk to you soon.", "Would a
call be easier?"), refuses 11 of 143 trade lines, and misses 6 cell forms ("720-275-l554", "12 275-1554"). tests/test_send_gate.py::test_mac_phone_gate_parity_report
prints the list on the Mac. Until the Mac check is brought up to the same cases, write Mac mail to the cloud rule.

# 2026-11-06 08:45 MT: the Mac heartbeat is RUNNING again (15:35Z). Parker, Brighton and FCC Florence go back to the Mac; the cloud stops touching those threads. Note for the Mac: Ceres sent its Brighton hourly rate 07:43 MT (rate lives in private/, not here) and the Mac's 08:33 MT reply asked Ceres to clear its Secretary of State delinquency; the cloud's 06:46 MT chase to Ceres and the Will Seargeant ask (EMR letter by Mon 09:00; what he needs from Luke to bind Travelers at $295 down) are logged in ops/outbox/2026-11-06/sent.json. Do not re-send either.

# 2026-11-06 06:50 MT: the Mac heartbeat session has been BLOCKED since 02:28Z ("Approve or deny Bash"). Until it is unblocked, the cloud HQ also covers the Mac's threads: Parker (package build from Brad's numbers), Brighton (Ceres, Will's EMR letter, fee schedule), FCC Florence (Wind River/Arrowhead). Same rules: pull first, check Sent, log every send.

# DIVISION OF LABOR, both operators live (HQ, 2026-11-05 21:40Z)

The Mac heartbeat came back ~15:46Z on 11/05 (Sent shows it on the Wind River / FCC Florence, Colorado Power Wash,
Ceres/Brighton, Parker/Brad and HOODZ/PSD threads). The cloud HQ is also live (Luke, 11/05: "4x the work"). To stop
double-sends from the one mailbox, the split from now on:

- **Mac operator (Luke's live threads):** Parker generators (Brad Orgill) and the Fri 11/06 14:00 submission on Bonfire +
  RMEPS; FCC Florence grease (Wind River, Arrowhead) and the Mon 11/09 quote; Brighton (Ceres rates, Mon 11/09 14:00
  submission; HQ pre-built the package under bids/brighton-as-needed-construction/proposal/); PSD hoods (HOODZ, walk
  11/10 13:30); Colorado Power Wash (call 11/16 10:00); the CRM at crm.brownbisonco.com; every board email to Luke's
  gmail. Anything Luke replies to by hand.
- **Cloud HQ (this session):** the hourly logged-in scan + triage of NEW matches; sub outreach and chases on bids with
  no live Mac thread (today: Jeffco chiller, Carbon Valley, Metro Water non-RESA, Fort Collins doors); package pre-builds
  (Parker + Brighton drafts are in each bid's proposal/); the revival list (bids/_watch/revival-audit-2026-11-05.md);
  Jones Bearing / federal product quotes; buyer questions on cloud-owned bids (Weld jail second walk, USCG AK017);
  the 8-line board in Luke's HQ chat.
- **Re-engaging the subs stood down 11/03** (RESA, EC, WOW, Colorado Power Wash for RTD, Sergeant Suds, Accutemp, Peak,
  Platinum): waits for Luke's answer; HQ's default is to re-engage Fri 11/06 08:00 MT unless Luke says no, and HQ
  will do it in the existing threads (Re:), one email each, logged in sent.json.
- Both: `git pull` before any send; check Sent for the subject + recipient first; log every send in
  ops/outbox/<date>/sent.json and the bid's sub-outreach.md. Do not re-send what the other side already sent.

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

# 2026-11-05: the humanize gate now guards the cloud sender (set by the Mac CEO session)

Luke's hard rule (2026-11-05 ~11:00 MT): every email to anyone other than Luke passes /humanize `hz.py lint`, every
time. `scripts/humanize_gate.py` now guards both cloud send paths. It is a self-contained, STRICTER port of the Mac's
brown-bison-gov/data/humanize_gate.py, not the same gate; its docstring lists the differences.
- `scripts/gmail_api.py send` runs the gate on the body, subject and attachment types before any token or network call
  and refuses on a FAIL (exit 3, "HUMANIZE: ..."). `call()` refuses a POST to the send endpoints that send() did not
  build. `scripts/send_outbox.py` runs the gmail_api.py beside it, validates each manifest entry, prints "REFUSED
  <key>" or "FAILED <key>", leaves those entries out of sent.json and exits 3 (refused) or 1 (failed).
- Gmail connector send_message / reply / forward go through a PreToolUse hook in `.claude/settings.json`
  (`humanize_gate.py hook`, fail-closed). The hook also denies draftId sends, htmlBody and includeSignature.
- Body shape: "Hi <FirstName>," ("Hi Team,"), the message, "Thanks <FirstName>," ("Thanks Team,"). Every closer name must
  appear in the greeting. A gmail_api.py body file stops at the closer, because the sender appends the Operations Manager
  signature. A connector body carries the four signature lines after the closer (five until 2026-11-06; the phone line
  is gone, see the 2026-11-06 section at the top).
- Refused even when hz.py only warns: more than 150 words by the gate's own count, more than 12 "Label: value" lines,
  links, look-alike or invisible characters, .txt/.html/.eml attachments, and `--no-signature` to outsiders.
- asks above 1 needs the inbound email saved as text (`--asks-from FILE`, manifest `asks_from`). asks = min(declared,
  its '?' count), up to 20. There is no --long and no approvals file.
- Only the repo's copy of hz.py runs.
- Pre-check: `python3 scripts/humanize_gate.py check BODY [--asks-from INBOUND] [--subject S] [--signature]`.
- Today's weld-second-walk.txt went out with "Hi," / "Thanks," and a lint FAIL. The gate now refuses that.
