# CPW DQ1 PMAA 2027*0176 Alamosa heater replacement: sub outreach (mechanical + electrical)

Brown Bison bids and holds the PO; the sub removes 6 heating units, installs electric heaters with the electrical upgrades
and breakers, and adds a garage space heater. The sub's person must attend the MANDATORY pre-bid Wed 2026-11-18 10:00 MST at
6655 CR 106 South, Alamosa (registration with the buyer by Tue 11/17 17:00). Candidates: ops/research/2026-11-12-cpw-courthouse-subs.md.

## Log
- 2026-11-12 23:4xZ (16:4x MT, HQ): pricing + pre-bid attendance ask with the DQ attached, bcc group 1a1d21a9b4b05592: Husmann Plumbing & Heating (info@husmannplumbing.co), Surefire Heating and Cooling (surefirehvacr@gmail.com). Answer asked by Mon 11/16 12:00 MT. Torres P&H and Flow Right (tier B) held for Fri if both are silent.
- 2026-11-13 14:40Z: Husmann Plumbing & Heating DECLINED (Mario Rivera, thread 1a1d55a5ec86d07b: "WE DECLINE TO BID, THANKS FOR THE INVITE THOUGH"). No reply needed; do not re-ask. Surefire still silent.
- 2026-11-13 14:50Z (HQ): Friday 08:30 MT batch adjusted: Exhibit A, Scope of Work goes to Surefire only; Flow Right (dispatch@flowrightphi.com) gets the full ask with the DQ + Exhibit A. Torres P&H is next if both are silent by Mon 11/16 12:00 MT; no attendee by then = NO-BID (mandatory pre-bid 11/18 10:00).

- 2026-11-13 15:59Z (08:59 MT), HQ: Exhibit A Scope of Work to Surefire only (surefirehvacr@gmail.com), msg 1a1d5a2835ac51db; full ask + DQ + Exhibit A to Flow Right (dispatch@flowrightphi.com), msg 1a1d5a289f443c61. Husmann declined 14:40Z. Humanize gate PASS; sent via scripts/send_outbox.py (ops/outbox/2026-11-13/outbox-friday-batch.json).
- 2026-11-13 19:3xZ (worker): scope is mainly ELECTRICAL (Exhibit A), and the 11/12 sweep had only HVAC/plumbing firms. Electrical sweep in
  ops/research/2026-11-13-cpw-alamosa-electrical-subs.md: A tier Vemco (Center), Valley Electric (Alamosa), Billings Electric (Alamosa),
  Power Pro (Monte Vista). Ready-to-send manifest for HQ: ops/outbox/2026-11-13/outbox-cpw-electrical.json (bcc Vemco, Power Pro,
  C-Squared, Royal; HQ adds the Valley Electric and Billings named mailboxes privately; separate entry for Torres P&H, never asked).
  Humanize gate PASS. NOT sent by the worker (read-only).
- 2026-11-13 19:40Z (12:40 MT, HQ): ELECTRICAL sweep (Exhibit A makes the job mainly electrical; worker research ops/research/2026-11-13-cpw-alamosa-electrical-subs.md). bcc 6 (gate PASS, DQ + Exhibit A attached), msg 1a1d66c90745e1e0: Vemco Electrical (Center), Valley Electric (Alamosa), Billings Electric (Alamosa; may bounce), Power Pro Electric (Monte Vista), C-Squared Electric (Monte Vista), Royal Electrical Services (Pueblo; electrical + HVAC). Named mailboxes stay out of the repo (local manifest copy). Torres Plumbing & Heating (office@torrespandh.com) got the full mechanical + electrical ask, msg 1a1d66c96ac41789. Answer asked by Mon 11/16 12:00 MT; no attendee by then = NO-BID. Held for Mon if the A tier is silent: Alpine Electric & Solar, Morton Electric (named mailboxes, with HQ).
- 2026-11-13 20:2xZ (worker, Gmail read-only): 2 BOUNCES on the 19:40Z electrical bcc (thread 1a1d66c90745e1e0). Valley Electric (Alamosa, the
  best-fit A tier): named mailbox rejected "550 5.7.1 Relaying denied" by mx.myregisteredsite.com (msg 1a1d66cd39e290c7), so the mailbox is not
  hosted at that domain. Royal Electrical (Pueblo) office@royalelectrical.com: Microsoft 365 "550 5.4.1 Recipient address rejected: Access
  denied" (msg 1a1d66cf6614c5b7), so that mailbox does not exist. Delivered so far: Vemco, Power Pro, C-Squared, Billings, Torres. Worker is
  searching for verified alternate addresses for both.
- 2026-11-13 20:4xZ (worker): no alternate address exists for Valley Electric (its whole mail domain is inactive) or Royal (web form only).
  B-tier manifest ready for HQ: ops/outbox/2026-11-13/outbox-cpw-electrical-btier.json (bcc Pueblo Electrics, Mathews Brothers, Schrock,
  Timme, Redwing; same body, gate PASS, validated, NOT sent). Recommend sending today, not Monday, because the gate is Mon 12:00.
