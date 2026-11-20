# Sub outreach: NIST Boulder 1333ND27R0001 Central Utility Plant PM (Boulder campus + WWV Fort Collins)

Brown Bison is the bidder and prime; a Front Range commercial mechanical service firm prices the preventive maintenance as
our sub. Named mailboxes and the pages they were read from are kept in the HQ scratchpad (`nist-subs.json`), not in this
public file.

**SEND STATUS: HOLD.** The bid is NO-BID on the draft as written (README: Section L Factor 3 offeror experience minimum;
PWS 2 key personnel must be prime employees). Send only if the final RFP clears both. If it does, both lines go out the
same day (rule 0b), pricing asked by Mon 2026-11-30 or 7+ days before the final due date, whichever is later.

What a sub can and cannot do here (draft): PWS 2 bars subs from the key-personnel seats (project manager, project
engineer, stationary engineers, HVAC mechanics), so the 24/7 plant crew would be Brown Bison employees. Subs fit the PM
job plans outside the crew's reach (Fort Collins, which the on-duty crew may not leave Boulder to cover), specialty PM
(boiler tuning, cooling towers, generators), and the T&M repair line. Factory-certified York / Ingersoll Rand / Carrier /
Liebert PMs (PWS 3.1, 3.1.14, 4.1.6) go to the OEMs' own service arms.

No mandatory walk: the 2026-12-21 13:00 MT conference and site visit are optional (CAR 1352.270-71(d)) and fall after the
pricing date, so the email asks for no attendee. If the bid revives and a sub wants to attend, its person signs in for
Brown Bison, with full first/middle/last names sent to the Contract Specialist in advance (draft cover letter).

## Firms (public email printed on the firm's own website, read 2026-11-20)

| Line | Company | City | Fit (from its own site) | Small under 811310? |
|---|---|---|---|---|
| 1 | Rasmussen Mechanical Services (Rocky Mountain office) | Centennial; Boulder pages | Maintenance page lists *"Chillers and Cooling Towers"* and *"Boilers and Burners"*; *"commercial HVAC maintenance agreements in Denver"*; Boulder pages list chillers and boilers, *"tailored maintenance programs designed specifically for Boulder commercial facilities"* | Unknown (multi-state firm); asked |
| 2 | Mechanical Solutions, Inc. (MSI) | Englewood | Commercial, steam and hot water boilers; "Planned Services"; NREL and EPA in its client carousel | Unknown; asked |
| backup | UPM Mechanical, LLC | Denver | "HVAC/R Service & Maintenance"; industries "City & Government", "Data Centers"; no chiller or boiler wording | Likely (City of Denver MWBE per the DEN outreach 2026-11-17); asked |
| backup | Tolin Mechanical Systems | Denver; Timnath branch near Fort Collins | "Planned Maintenance"; industry "Government"; a Fort Collins-area branch for the WWV site | Unknown; asked |

Checked and not used: Timberline Mechanical (Boulder; strong local fit, but its contact page prints no address, form
only), Climate Engineering Inc (Denver; its site did not resolve from this session), Aether Mechanical (Aurora; residential
heavy, no chiller or commercial PM wording), ACCO Engineered Systems (large business, not similarly situated),
Standard Mechanical (Arvada; only a named mailbox, no general address). Incumbent: Peak Facility Solutions LLC (contract
1333ND21CNB190017); not contacted.

## Email body (not sent)
File: `sub-firsttouch-gmailapi.txt` for `scripts/gmail_api.py` / `send_outbox.py` (ends at "Thanks Team,"; the sender
appends the 4-line signature). `python3 scripts/humanize_gate.py check --subject "..."`: **PASS** (no warnings,
2026-11-20). One email per firm, bcc.

Subject: Pricing request: NIST Boulder central plant PM, solicitation 1333ND27R0001

```
Hi Team,

I'm Luke Adams with Brown Bison Holdings. We're pricing the NIST Boulder Central Utility Plant contract, solicitation 1333ND27R0001.

NIST posted a draft on November 19 and the final RFP follows. Brown Bison is the prime, and we want a Front Range mechanical firm as our sub for the preventive maintenance.

Equipment: 3 steam boilers, 4 York YZ 1500-ton chillers, 4 cooling towers, 71 pumps, AHUs and packaged units

Sites: NIST Boulder campus and the WWV field site in Fort Collins

Volume: about 940 work orders a year, monthly to annual job plans

Term: base year from February 25, 2027, plus 4 option years

Wages: Service Contract Act; the current crew works under an Operating Engineers Local 1 agreement

Site visit: optional, December 21, so please price from the documents

Attached: draft RFP, PWS, asset and PM list, job plans

Can you send per-visit or annual prices for the job plans you can cover by Monday, November 30? Please also tell us if your firm is a small business under NAICS 811310.

Thanks Team,
```

Facts in the body, with sources: 3 steam boilers BLR-C-017/018/019 (PWS Att 1); *"Four (4) York YZ 1500 ton capacity
each"* (PWS 3.1); 4 CUP cooling towers 42-CT-001..004 (Att 1); 71 pumps (Att 1 Summary, all sites); about 940 = 450 CUP +
322 other Boulder + 167 Fort Collins nested WOs/yr (Att 1 Summary); base from *"February 25, 2027"* plus Option Years I-IV
(CAR 1352.270-70); SCA (52.222-41) and the IUOE Local 1 CBA (WD placeholder); conference 2026-12-21 (CAR 1352.270-71).

Attachments (about 5.0 MB, one email): `docs/1333ND27R0001 DRAFT CUP 19NOV2026.pdf`, `docs/01 CUP PWS 11-05-2026.xlsx`,
`docs/02 PWS Attachments.zip`, `docs/03 CUP Job Plans.zip`. Add `docs/04 Safety Plan Checklist.pdf` and `docs/05 Boulder
General Contractor Requirements Rev D.pdf` once a firm says yes. No links.

## Log
- 2026-11-20 ~06:10Z (HQ worker): folder opened, 7/7 SAM files in hand, NO-BID on the draft; 2 lines + 2 backups found,
  first touch drafted, gate PASS, HOLD. Nothing sent.
