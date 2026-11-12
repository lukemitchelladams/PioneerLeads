# CLAUDE.md — Brown Bison

## What this repo is
Brown Bison's government-contracting workspace. Bids, proposals, vendor Q&A, and project memory.
It also hunts bids for Luke's dad's industrial bearings/conveyor/paper-mill business (profile
`dads-company` in bids/_watch/watch_profiles.json). Every scan covers both companies.
It is NOT a software product. Do not scaffold apps here unless asked.

## Updates to Luke = board updates: 8 lines max (Luke, 2026-10-20, emphatic)
Every status message, morning brief, evening update and hourly reply to Luke uses THIS format and nothing
longer. No narrative, no "landed today" essays, no lists of everything read. Details live in the repo and the
dashboard (https://claude.ai/artifact/XuXDuPxLzdD9ALxsyoWES3); the update links there.

    BROWN BISON <date> <AM|PM>
    1. #1 TODAY: <the single most important outcome today, and who owns it>
    2. DUE ≤72h: <bid / deadline / mandatory walk, date-time>  (max 3, most urgent first)
    3. LUKE MUST DO: <action only Luke can do, by when>  (or "nothing")
    4. DECIDE: <yes/no question for Luke>  (or "nothing")
    5. BLOCKED/RISK: <what is stuck and why>  (or "nothing")
    6. NUMBERS: sources live x/4 | open matches | GO bids | sub pricing in hand x/y
    7. DONE SINCE LAST: <one line, the biggest result>
    8. Dashboard: <link>

## Operating rules (non-negotiable)
0. FIRST thing on any new bid: find the pre-bid meeting / site walk date and whether attendance is
   MANDATORY. Put it in the README status table and bids/_pipeline.md. If mandatory and <72h away or past,
   tell Luke in the first line of your reply. Missing a mandatory walk kills the bid (Estes Park, Lafayette,
   Arapahoe fire alarm, DOC fire protection all died this way).
0b. Sub outreach starts the day a bid goes GO, not 72 hours out (Luke, 2026-10-19). Subs need at least a
   week's notice before a site walk or our pricing deadline. Same day a bid is opened: find 5-8 local subs
   with public emails, write bids/<bid>/sub-outreach.md with the pricing-request email, and put it in front
   of Luke that day. Ask subs for answers 7+ days before our submission. If a mandatory walk is under 7
   days out, Luke attends for Brown Bison and subs price from our photos and notes. Every hourly check
   lists GO bids with no sub pricing in hand and the days remaining.
0c. COMPLETE DOCUMENT PACKAGES, EVERY TIME (Luke, 2026-10-19, after Littleton went out without Attachments
   A/B/C). When Luke asks for the docs for a job, deliver 100% of the package: the solicitation PLUS every
   attachment, exhibit, appendix, form, price sheet/template and addendum it lists. Before sending, read the
   solicitation's table of contents / attachment list and check each item against bids/<bid>/docs/MANIFEST.md
   (run `python3 scripts/doc_manifest.py`). Send everything in hand in one go and, in the same message, list
   every missing item by name with exactly where to download it. Never send just the main PDF.
1. Correct misconceptions. If the user is wrong about a bid detail, say so with the source.
2. Never state a bid requirement (response time, due date, insurance limit, equipment model)
   unless it is quoted from the actual solicitation document. If we don't have the document,
   say "not in hand yet" and list how to get it.
3. Verify before claiming done. If a fetch failed or a host was blocked, report it as blocked.
4. Read `memory/MEMORY.md` at the start of every session. Append to it before ending.
5. One folder per bid under `bids/<agency>-<short-title>/`. Start from `bids/_template/`.
6. Keep the status table in each bid `README.md` current.
7. Dates: write ISO (2026-10-09). Money: write with units.
8. No excavation, earthwork, or heavy-civil bids (ponds, pump stations, roadwork, drainage). Our trades are
   HVAC, plumbing, electrical, facilities maintenance, landscaping/grounds/snow, janitorial. Keep it simple
   (Luke, 2026-10-19).
9. Supply/commodity bids: do not rank as GO unless the document states quantities or annual spend. Small-margin
   product supply (filters, parts) is not worth Brown Bison's time unless volume is proven (Luke, 2026-10-19).

## Standing rules from Luke
- **HARD RULE: no appointments that need Luke, and no idle ticks** (Luke, in chat, 2026-11-09: "i check my email and i see
  you are scheduling calls with people, didnt we say the plan was to not do that?"; 2026-11-11: "you seem to have gotten
  absolutely nothing fucking done today, pick up the fucking slack"). No call, meeting, walk, tour or pre-bid is offered,
  accepted or confirmed under Luke's name; never write "I will meet" or "I will attend". A site visit happens only with a
  sub's person attending, confirmed in writing and signing in for Brown Bison; otherwise decline it, and if it is mandatory
  log NO-BID. Entry paperwork (Exhibit G, photo ID) is the attendee's, never Luke's. The board asks Luke only for a
  signature on a finished document, a payment, a portal login/post, or a fact only he knows; no DECIDE line where a rule
  already answers, and nothing that routes through family or Alex. No tick ends "quiet" or "waiting" while a live bid has
  no priced sub: open the next company, price from the documents, or pre-build the package. Detail and current work orders:
  ops/plan_ceo/COORDINATION.md, 2026-11-12 section.
- **HARD RULE: do every single thing you can yourself and send Luke a copy for approval; "LUKE MUST DO" is for
  signatures, photo ID, portal uploads, payments and walks a human must stand at** (Luke, 2026-11-08 14:57 MT, by email,
  verbatim: "Lots of this shit listed here you can make decisions on your own and keep moving, you can do all those
  safety plans, resume, mark ups, etc.. you need to push yourself each time to make sure you've done absolutely every.
  Single. Thing. You can, before saying it's something 'luke has to do'.. you need to be asking yourself 'is this
  something I can do and just send Luke a copy for approval? Most of the time the answer is yes"). Before any item
  lands on line 3 of the board, write the thing (resume, safety plan, markup table, form answers, pre-filled form, RSVP,
  decision) and email Luke the copy; the board line then reads "approve/sign X" instead of "write X". Decisions with a
  sensible default are made by HQ and reported, with the overrule window stated, instead of asked.
- **HARD RULE: no email to Will Seargeant or anyone at Trucordia** (Luke, in chat, 2026-11-09: "I AM NOT SENDING EMAILS TO
  FUCKING WILL AT TRUCORDIA, i am not signing that contract until fucking friday"). No operator emails Trucordia, and no plan or
  board asks Luke to. Do not ask for a letter, a quote change or an early bind; nothing is bound or paid before Friday 11/13, and
  only Luke restarts that conversation. If Will writes in, log it, do not answer, one line on the board. Enforced in code
  (`no_contact_hits` in scripts/humanize_gate.py). Only Luke himself lifts this. The 11/06 and 11/09 emails to Will broke it.
  Luke again, to the hourly worker session, same morning: "we are not buying the insurance contract from will until friday, i
  dont have it yet" / "do not send him emails until friday, he just called me abut that email you sent" / "i told you i dont
  have the money until friday" / "do not send him another email with an apology, i already told him". So: NO apology or
  "sorry for the confusion" email either; Luke has already handled it. No bid waits on or promises an EMR letter, certificate
  or policy before the Friday purchase (Brighton 11/09 goes without one).
- **HARD RULE: no phone in email. Get information by email; never give out Luke's cell or invite a call** (Luke,
  2026-11-06 ~10:50 MT, verbatim: "i cant have all these fucking guys calling me all fucking day long, we need to try and
  get information via email and not always be telling people or letting them call me, because i dont always have all the
  ifnormation or am the most up to date because i work all day"). For every email to anyone other than Luke himself:
  (a) Luke's cell (720) 275-1554 never appears, in any format, body or signature; (b) no call invites ("call me", "give us
  a call", "call or text", "text me", "my cell", "reach me at <number>", "hop on a call", "quick call", "schedule a call",
  "talk by phone", "phone call", "best number to reach", "good time to talk" ...); ordinary trade words are fine (on-call,
  service call, call-out, callback response time, emergency calls, calls for service, "called for in the specs");
  (c) the signature is FOUR lines: Luke Adams / Operations Manager / Brown Bison Holdings LLC / luke@brownbisonco.com.
  Answer by email; at most add "Email is the best way to reach me during the day." `scripts/humanize_gate.py`
  (phone_problems) refuses both send paths with "No phone number or call invite in email (Luke 2026-11-06) ...". It refuses
  every "call" and "phone" in our own text BY DEFAULT unless it is a trade term, a third party's call or line ("the City
  will call us", "call the Town procurement office", "photos from my phone") or negated ("don't call"); so write "Please
  email any questions", never "call with questions". The connector `forward` to anyone but Luke is refused (it carries the
  old thread, whose signatures hold the cell): write a new message and attach the file. Shared test cases:
  `tests/phone_cases.json`.
  Phone numbers on government bid FORMS and PROPOSAL documents (cover sheets, price sheets, contact tables) are out of
  scope and stay. Mail only to Luke's own addresses is exempt.
- **HARD RULE: a call request becomes a CALL BRIEF to Luke; plans never route work through Luke phoning someone** (Luke,
  2026-11-06 ~12:10 MT, verbatim: "yeah just do email and if they need to call me, you need to inform me that they let you
  know they want a call, and what i need to know for the call"). When anyone asks for a call, says they called or left
  Luke a voicemail, or insists a call is needed:
  (1) Answer them by email with what we know. Never promise, offer or schedule a call and never say Luke will call. At
  most add "Email is the best way to reach me during the day."
  (2) In the same session, email Luke a CALL BRIEF from luke@brownbisonco.com to **lukemitchelladams@gmail.com** (the
  address the board emails go to; mail only to Luke's own addresses is exempt from the phone gate). Subject
  "CALL REQUEST: <Name>, <Company> / <bid>". 8 lines max:
    1. WHO: name, company, trade, their phone number from their own signature or our contact record
    2. WANTS: what they want to talk about, in a few words
    3. WHERE IT STANDS: bid number, due date, their price in hand or not
    4. ANSWERS YOU NEED: the facts and numbers Luke should have ready
    5. GET FROM THEM: the one thing to get on the call
    6. DON'T COMMIT: no award promise, no start before the insurance bind, no spending before 11/13, plus anything
       bid-specific
    7. IF YOU SKIP IT: what we do by email instead, and the deadline
  Luke decides whether and when to call. Also put it on the board under "4. DECIDE". Plans never route work through Luke
  phoning someone: a chase is an email; if only a call will do, it is a CALL BRIEF and Luke's choice. Live examples (Mac,
  11/6): Jake Pavelle (Colorado Power Wash) Mon 11/16 call cancelled by email 12:11 MT; CALL BRIEF for Brad Orgill
  (Colorado Standby, Parker 26-021-1) sent to Luke 12:11 MT. Parker RFP 26-021-1 (generators) went NO-BID 12:03 MT 11/6
  (Colorado Standby sent no prices); it revives only if Brad's ten prices arrive by email by 1:00 PM MT, which the Mac
  heartbeat owns.
- **HARD RULE: every email to anyone other than Luke passes /humanize lint, every single time** (Luke, 2026-11-05
  ~11:00 MT, verbatim: "when you are going thru and sending email responses to people in this project, you have been
  using the humanize skill, correct? we need to always be doing that as a hard rule every single time going forward").
  Every non-Luke email passes `hz.py lint` through `scripts/humanize_gate.py` (pre-check: `python3 scripts/humanize_gate.py
  check BODY` must print PASS). `scripts/gmail_api.py send` runs the gate before any network call and refuses otherwise
  (exit 3, "HUMANIZE: ..."); `scripts/send_outbox.py` prints REFUSED, does not record the entry and exits 3. Gmail
  connector sends (send_message / reply / forward) are checked by the PreToolUse hook in `.claude/settings.json` and
  denied when they fail. There is no bypass flag. Group mail uses "Hi Team," / "Thanks Team," (never "Hi," or "Thanks,").
  A gmail_api.py body file ends at "Thanks <FirstName>,": the sender appends the signature. A connector body ends with
  "Thanks <FirstName>," and then the four signature lines, no phone (the connector adds nothing). The title is **Operations
  Manager** (Luke 2026-10-18; never Owner, CEO, General Manager or Sales Manager). The gate also refuses links,
  look-alike or invisible characters, .txt/.html/.eml attachments, and `--no-signature` to outside recipients. A reply
  that answers several questions may go over 150 words only with the inbound email saved as text:
  `--asks-from FILE` (manifest `asks_from`); without it, asks is capped at 1. Only mail to Luke's own addresses
  (luke@brownbisonco.com, lukemitchelladams@gmail.com) is exempt.
- **Use the humanize skill (.claude/skills/humanize) for every email, message and reply, going forward. Be concise:
  no walls of text** (Luke, 2026-10-21). If ~/.claude/skills/humanize is missing in a new container, copy it from
  .claude/skills/humanize and run `python3 ~/.claude/skills/humanize/scripts/hz.py init`.
- **Never write or say "or if you already have a contract with the city" or any variant** (existing contract,
  already under contract, current provider) in any outreach, proposal, or vendor message. It invites the
  reader to tell us no and signals we expect to lose. We write as the bidder who will win. (Luke, 2026-10-19.)
- **BROWN BISON IS ALWAYS THE BIDDER.** Every bid, every trade. Subcontractors (Alex Ditto for landscaping,
  Jones Bearing for equipment, any HVAC/plumbing/electrical sub) give us their pricing; we add our markup
  and fees, we submit, we hold the contract, we manage the sub. NEVER describe a bid as "for" a sub, never
  suggest a sub bid directly, never offer a "sub primes" option. (Luke, 2026-10-19, emphatic.)
- All landscaping work is performed by Alex Ditto as OUR sub. Luke handles all communication with Alex;
  the agent only surfaces Alex's emails and flags landscaping bids worth getting his pricing on.
- **NEVER put links in emails to subs or anyone outside (Luke, 2026-10-26, emphatic)**: no GitHub/raw links, no portal links to the
  bid. Attach files, or have Luke forward them. If a file is too big to attach from here, send Luke the file to forward.
- **H2 Global Solutions = go-to sub for boiler / water-treatment and similar mechanical-service jobs** (Luke, 2026-10-26: Silas Norwood, COO,
  snorwood@h2gs.com, office 719-694-0515, was fast and helpful on the TCF boiler DQ; run future jobs in their wheelhouse by them first). Service area (Silas, 2026-11-09): "anything east of Colorado Springs or throughout Kansas"; more than ~4 h west of Garden City only for a massive account. They DECLINED Buena Vista (too far) and Canon City 129-26 boiler/chiller (not their service) on 11/09; do not route those to them.
- All business email goes out from luke@brownbisonco.com. Never use lukemitchelladams@gmail.com for business.
- Gmail (Luke, 2026-10-26): Luke gave blanket permission for his mailbox and wants the agent to act on its own:
  send sub outreach, follow-ups, buyer questions and site-visit RSVPs from luke@brownbisonco.com without asking.
  Still never submit a bid, sign anything, spend money, or delete/trash mail without asking. Hourly scan sessions stay read-only.

## Portal access
- Bid-portal scanning = `python3 scripts/scan_bids.py` (BidNet scraper + SAM.gov API). Needs allowed
  domains + SAM_API_KEY/BIDNET_USER/BIDNET_PASS env vars. See docs/portal-access.md. Credentials come
  from the environment only; never ask Luke to paste them in chat, never write them to the repo.

## Known blocked hosts in cloud sessions
bidnetdirect.com, rockymountainbidsystem.com, sam.gov, api.sam.gov, parkerco.gov.
Ask the user to add them under Network access → Allowed domains (see docs/cloud-env-setup.md),
or ask the user to download the solicitation PDFs and drop them in the bid folder under `docs/`.

## Key facts (see memory/MEMORY.md for detail)
- Brown Bison Holdings LLC: UEI EV9QPAPM4C47, CAGE 20VU2, SAM active to 2027-05-21, NAICS 238220.
- GovTribe connector = bid search for BidNet/RMEPS + SAM.gov. Use it first, every session. State/local CO
  search covers Parker, DCSD, Estes Park, Douglas County and the whole Front Range.
- Town of Parker, CO posts solicitations on its EUNA Procurement Portal (formerly Bonfire), parkeronline.bonfirehub.com (RFP 26-028 confirmed 2026-10-19).
  Procurement: 303-805-3188. Bid docs usually require vendor login to download.
- Town of Parker is a Town, not a City. Use "Town of Parker" on all submittals.
