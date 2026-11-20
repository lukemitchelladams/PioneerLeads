# Sub outreach: IHS RFQ 75H70727Q00003 fire door inspection, assessment and repair (Albuquerque, Santa Fe, Taos, Mescalero NM)

Brown Bison is the bidder and prime; a New Mexico commercial door contractor performs as our sub and gives us its price.
Named mailboxes and their source pages are kept in the HQ scratchpad (`ihs-subs.json`), not in this public file.

No mandatory walk: the optional site visits close Thu 11/19 12:00 MST (PWS 6.12; notice), so the email asks for no attendee.

## Firms (public email on the firm's own website, found 2026-11-19)

| Line | Company | City | Fit (from its own site) | Open questions |
|---|---|---|---|---|
| 1 | American Door, LLC | Albuquerque (2nd Street SW) | Hollow metal doors and frames for fire-rated openings, fire-rated glass, commercial door hardware, hollow metal door inspections, hospital doors; serves all of New Mexico | IQP/FDAI inspector? Davis-Bacon certified payroll? |
| 2 | Door Doctor | Albuquerque | Commercial, residential and industrial door installation and repair, 40+ years; door closers, exit hardware, fire doors | IQP/FDAI? Service area on its site is the Albuquerque metro; Santa Fe, Taos and Mescalero travel to confirm |
| materials | Grant's Steel | Albuquerque (First St NW) | In-house hollow metal door and frame fabrication, wood doors, architectural and security hardware; serves contractors | Supplier: price labeled doors/frames/hardware behind the replacement lines; installation not stated |

Checked, no public email on an own site: DH Pace / Overhead Door Company of Albuquerque (did the 2025 AIHC FireCheck
inspection; site blocks automated reads; likely competitor), Fairway Inc. (hollow metal and wood doors; directory listings
only), Commercial Door & Hardware Inc. (directory only), Pat's Doors Inc. (directory only), Medley Company Albuquerque (dock
and industrial doors, no email). The Lock Shop (Albuquerque) prints an email, but its site is automotive/residential
locksmith work: not used.

## Ask
- Unit prices per site on the IHS Bid Schedule by **Mon 2026-11-23 12:00 MT** (signable copy to Luke Mon 15:00; due Wed
  11/25 15:00 MST), plus the lead inspector's IQP or FDAI certification.
- Both lines go out in the same send (11/18 rule: 2 parallel sub lines); there is no time for a 48-hour stagger.
- Attach every file in `docs/` (see `docs/MANIFEST.md`). Attachment A goes as the 3.4 MB compressed copy; the as-builts
  (20.4 MB) and Attachment B (13.9 MB) need their own emails. No links.

## Email body (not sent)
Files: `sub-firsttouch-gmailapi.txt` for `scripts/gmail_api.py` / `send_outbox.py` (ends at "Thanks Team,"; the sender
appends the signature): `python3 scripts/humanize_gate.py check` **PASS**. `sub-firsttouch.txt` for a connector send (4
signature lines after the closer): `python3 scripts/humanize_gate.py check --signature` **PASS**.

Subject: Fire door inspection and repair pricing, IHS RFQ 75H70727Q00003

```
Hi Team,

I'm Luke Adams with Brown Bison Holdings. We're quoting an Indian Health Service fire door job, RFQ 75H70727Q00003. Brown Bison is the prime, and we want a New Mexico door contractor as our sub.

Sites: Albuquerque 21, Santa Fe 18, Taos-Picuris 11, Mescalero 14 fire door assemblies (approximate)

Scope: NFPA 80 inspection and repair report, approved repairs or replacements, final passing inspection

Schedule: report within 15 days, all work done within 90 days of notice to proceed

Inspector: the lead inspector must hold IQP or DHI FDAI certification

Wages: SCA for inspection and minor repair, Davis-Bacon for replacements, certified payroll

Asbestos: no disturbance, IHS handles any abatement under its own contract

Can you send unit prices for each site on the attached IHS bid schedule by Monday, November 23 at 12:00 PM MT? Please include your lead inspector's certification with the price.

The solicitation, both amendments, bid schedule, door schedules, photos and wage determinations are attached.

Thanks Team,
Luke Adams
Operations Manager
Brown Bison Holdings LLC
luke@brownbisonco.com
```

## Log
- 2026-11-19 ~16:00Z (HQ worker, read-only): folder opened, 27/27 documents in hand, 3 firms found (2 installers + 1
  supplier), first-touch drafted and gated. Nothing sent.

- 2026-11-20 20:48Z (Mac send run): bond question to Contract Specialist Stephanie Begay (msg 1a1fab7d735fae04) + sub first touch to Door Doctor (doordoc99@yahoo.com, 1a1fabc5b4d88fc0). **20:52Z REPLY (msg 1a1fabbb38fd0c7e): "RFQ 75H70727Q00003 was cancelled."** Bid is dead; no further sub outreach. Door Doctor needs a one-line stand-down (Mac).
