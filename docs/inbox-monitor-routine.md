# Inbox monitor Routine

Luke's standing request (2026-10-19): be alerted whenever relevant bid email arrives.

## Current setup
- Routine "Brown Bison inbox check (hourly, this session)" fires every hour 06:00–20:00 Mountain into the
  original Brown Bison cloud session, which holds the Gmail connector for **luke@brownbisonco.com**.
- A first attempt as a fresh-session Routine was created then disabled: this org does not allow passing
  connectors to Routines created from a session, so fresh sessions have no Gmail tools.

## Limits (be honest with Luke about these)
- Only luke@brownbisonco.com is visible. lukemitchelladams@gmail.com is NOT connected. Historical vendor
  mail (Alex Ditto, Rich Carroll) lives there. Options: (a) connect that Gmail as a second connector,
  (b) in that Gmail's settings, auto-forward to luke@brownbisonco.com, or (c) in brownbisonco Gmail,
  Settings → Accounts → "Check mail from other accounts" to import it. Option (b) or (c) makes the monitor
  see everything with one setting change.
- Hourly is the tightest cadence. Per-email push does not exist.
- Push notifications are not available on a Routine that fires into an existing session. For push alerts
  with Gmail, Luke can recreate this Routine in the claude.ai Routines UI (which can attach connectors)
  using the prompt below.

## Prompt (paste into claude.ai Routines UI if recreating there)
Hourly inbox check for luke@brownbisonco.com. Gmail is READ-ONLY: never send, reply, forward, draft, trash,
label, or mark anything; never touch a bid portal; never email anyone.
1. Read memory/inbox-seen.json (processed Gmail message IDs; missing = empty).
2. Gmail search: newer_than:1d -in:sent -from:luke@brownbisonco.com -from:lukemitchelladams@gmail.com
   -from:mail-noreply@google.com. get_thread (PLAIN_TEXT) each; skip seen IDs.
3. RELEVANT = mentions Alex Ditto, Rich Carroll, York, Johnson Controls/JCI, DCSD, Douglas County School
   District, Town of Parker, Estes Park, BidNet, RMEPS, HVAC, chiller, bid, RFP, IFB, RFB, solicitation,
   addendum, landscaping.
4. Log relevant mail in memory/inbox-log.md; save attachments into the matching bids/<slug>/docs/; if a
   solicitation arrived, build bids/<slug>/requirements.md quoting the document.
5. Update memory/inbox-seen.json; commit; push to origin claude/zealous-cerf-el4iek.
6. Reply with the relevant items (<150 words) or exactly "Inbox check: nothing relevant."
