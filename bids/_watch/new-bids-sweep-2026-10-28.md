# New bids sweep, 2026-10-28 (Brown Bison)

Scope: open Colorado bids in Brown Bison trades (HVAC, plumbing, electrical/low-voltage/fire alarm via sub, facilities/handyman,
generators, boilers/water treatment, doors, roofing, painting, flooring, janitorial, carpet, grounds/irrigation/tree, snow, pest,
window cleaning). Anything already in `bids/_watch/pipeline.json` was skipped (title and solicitation number checked).

## Source status
| Source | Status |
|---|---|
| GovTribe state/local | **BLOCKED**: `UPGRADE_REQUIRED` (state & local needs a Plus plan) |
| GovTribe federal | **BLOCKED**: `ACCOUNT_CANCELLED`. Subscription inactive since 2026-10-27; Luke has to restart it at govtribe.com/account |
| BidNet scraper (`open_bids.json`) | OK, scanned 2026-10-28 13:47Z: 604 BidNet + 106 SAM records reviewed |
| BidNet / SAM detail pages from this container | **BLOCKED** (HTTP 403 via curl and WebFetch). Records with no scraped detail show "not stated": the agency, pre-bid and docs are not in hand |
| Web mirrors | Used for USPS Denver P&DC (HigherGov) and the Reclamation SLV-CB roof (govcontractfinder) |

Prior hourly triage (govtribe_ledger.json) used a narrower trade list and marked roofing, doors and tree work "not our trade."
Those records are listed here because today's trade list includes them. The prior verdict is shown in the Note column.

## A. Mandatory walk within 10 days (act first)
| Agency | Title | Sol # | Due (MT) | Pre-bid / walk | Scope | Size | Link |
|---|---|---|---|---|---|---|---|
| Weld County | Jail 1 East Gym RTU Replacement | B2600111 | 2026-11-19 10:00 | **MANDATORY 2026-11-05 09:00**, 2110 O Street, Greeley. BidNet event: "Prebid Conference, Attendance Mandatory, Event date 11/05/2026 09:00 AM MST" | Replace the rooftop unit(s) on the Jail 1 East gym. Scope is from the title; Bid Specs.docx and Attachment 1 not downloaded | not stated | [BidNet 0000440763](https://www.bidnetdirect.com/colorado/solicitations/open-bids/Jail-1-East-Gym-RTU-Replacement/0000440763?purchasingGroupId=8409951&origin=1) |
| Mesa County | Storage Facility Fire Protection System (borderline trade) | RFP 2632-KY | 2026-11-19 14:00 | **MANDATORY 2026-11-03 10:00**, Fairgrounds Storage Bldg B, 2785 US Hwy 50, Grand Junction. BidNet event: "Onsite Visit, Attendance Mandatory, Event date 11/03/2026 10:00 AM MST" | Fire-protection (sprinkler) system for a county storage building. Needs a licensed sprinkler sub; Grand Junction is 4+ h away. Prior ledger verdict: NO | not stated | [BidNet 0000441227](https://www.bidnetdirect.com/colorado/solicitations/open-bids/Mesa-County-Storage-Facility-Fire-Protection-System/0000441227?purchasingGroupId=8409951&origin=1) |

Also time-critical: **Morgan County roof walk is TOMORROW, 2026-10-29 10:00** (optional, but "highly encouraged"; see row 11).

## B. New fits, sorted by due date
| # | Agency | Title | Sol # | Due (MT) | Pre-bid / walk (MANDATORY?) | Scope (one line) | Size | Link | Note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Jefferson County | Jail Door Slider Replacement | 26-17574TC-SO | 2026-11-02 11:00 | Job walk 2026-10-08 13:00, **not mandatory** ("Attendance Recommended"), passed | Replace jail slider-door hardware, Golden detention facility | not stated | [BidNet 0000438817](https://www.bidnetdirect.com/colorado/solicitations/open-bids/Jail-Door-Slider-Replacement/0000438817?purchasingGroupId=8409951&origin=1) | 5 days left. Specialty detention hardware. Prior verdict: NO |
| 2 | not stated | Biology Duct Insulation Damage | BidNet 0000439241 | 2026-11-02 | not stated | Repair damaged duct insulation in a biology building (title only) | not stated | [BidNet 0000439241](https://www.bidnetdirect.com/colorado/solicitations/open-bids/Biology-Duct-Insulation-Damage/0000439241?purchasingGroupId=8409951&origin=1) | 5 days left. Probably a campus job. Package not in hand |
| 3 | US Bureau of Reclamation, Eastern Colorado Area Office | EC-ECAO Exterior Door Replacement | 140RR027Q0011 | 2026-11-04 (time not in record) | not stated | Replace exterior doors (NAICS 238350), total small-business set-aside | not stated | [SAM](https://sam.gov/workspace/contract/opp/71ac218ba63c4668b2b3129557fcdeb5/view) | Loveland, per prior triage. Prior verdict: NO (doors) |
| 4 | not stated (Douglas County used this exact title for IFB 035-21 in 2021) | Semi-Annual Maintenance for Uninterruptible Power Supply | BidNet 0000440339 | 2026-11-04 | not stated | Twice-yearly UPS maintenance (electrical, via a UPS sub) | not stated | [BidNet 0000440339](https://www.bidnetdirect.com/colorado/solicitations/open-bids/Semi-Annual-Maintenance-for-Uninterruptible-Power-Supply/0000440339?purchasingGroupId=8409951&origin=1) | Agency unconfirmed |
| 5 | not stated | RFP 27-07 Fire Sprinkler System and Portable Extinguisher Services | RFP 27-07 | 2026-11-05 | not stated | Fire sprinkler and extinguisher inspection/service (via a fire-protection sub) | not stated | [BidNet 0000439622](https://www.bidnetdirect.com/colorado/solicitations/open-bids/RFP-27-07-Fire-Sprinkler-System-and-Portable-Extinguisher-Services/0000439622?purchasingGroupId=8409951&origin=1) | "27-xx" numbering looks like a school district |
| 6 | Pitkin County | 2027 Redstone Area Snow Removal Services | 124.26 | 2026-11-09 14:00 | not stated (no event in BidNet record) | Snow removal, Redstone area, 2027 season | not stated | [BidNet 0000439654](https://www.bidnetdirect.com/colorado/solicitations/open-bids/2027-Redstone-Area-Snow-Removal-Services/0000439654?purchasingGroupId=8409951&origin=1) | 3.5 h away; needs a local plow sub. Prior verdict: NO-likely |
| 7 | Fort Lewis College | Fire Alarm Inspection & Testing | 27201 | 2026-11-12 14:00 | Pre-bid 2026-10-20 14:00, **not mandatory** ("Attendance Recommended"), passed | Campus fire-alarm inspection and testing, Durango (via a NICET sub) | not stated | [BidNet 0000439558](https://www.bidnetdirect.com/colorado/solicitations/open-bids/Fire-Alarm-Inspection-Testing/0000439558?purchasingGroupId=8409951&origin=1) | Durango is far; needs a SW Colorado sub |
| 8 | Denver Public Schools (from title) | DPS Fire Suppression 2027 | BidNet 0000439933 | 2026-11-12 | not stated | Fire-suppression work at DPS sites, 2027 (via sub) | not stated | [BidNet 0000439933](https://www.bidnetdirect.com/colorado/solicitations/open-bids/DPS-Fire-Suppression-2027/0000439933?purchasingGroupId=8409951&origin=1) | **Risk:** sibling DPS BD2733 had a MANDATORY walk 2026-10-27. Check whether this one did too |
| 9 | not stated | Ash Tree Treatment | BidNet 0000441807 | 2026-11-13 | not stated | Ash tree (EAB) treatment; needs a licensed applicator/arborist sub | not stated | [BidNet 0000441807](https://www.bidnetdirect.com/colorado/solicitations/open-bids/Ash-Tree-Treatment/0000441807?purchasingGroupId=8409951&origin=1) | Posted 2026-10-27. Prior verdict: NO |
| 10 | not stated (paid aggregate notice) | Station One Janitorial Services | BidNet 444208178536 | 2026-11-13 (record says 17:00 EST) | not stated | Janitorial for "Station One" (probably a fire station) | not stated | [BidNet aggregate](https://www.bidnetdirect.com/private/supplier/interception/open-notice/444208178536?target=view) | Prior verdict: EVALUATE. Download folder is empty; needs a logged-in open |
| 11 | not stated (paid aggregate notice) | Snowmelt Boiler Plant | BidNet 444204005554 | 2026-11-15 | not stated | Boiler plant for a snowmelt system | not stated | [BidNet aggregate](https://www.bidnetdirect.com/private/supplier/interception/open-notice/444204005554?target=view) | Closing moved from 11/01 to 11/15 (REPORT.md) |
| 12 | Morgan County | Roof Replacement & Gutter Project, Multiple County Facilities | 2026-1119-001 | 2026-11-18 16:00 | **Walk 2026-10-29 10:00 (TOMORROW)**, Commissioners Bldg, 218 W Kiowa Ave, Fort Morgan. Not mandatory: "This meeting is not mandatory but highly encouraged. Responders who do not attend may be subject to contract term[s]…" (BidNet event, truncated) | Roof replacement and gutters at several county buildings | not stated | [BidNet 0000440968](https://www.bidnetdirect.com/colorado/solicitations/open-bids/2026-1119-001-Roof-Replacement-Gutter-Project-Multiple-County-Facilities/0000440968?purchasingGroupId=8409951&origin=1) | Prior verdict: NO (roofing) |
| 13 | not stated | Streetlight Materials & Installation | BidNet 0000441022 | 2026-11-20 | not stated | Supply and install streetlights (electrical) | not stated | [BidNet 0000441022](https://www.bidnetdirect.com/colorado/solicitations/open-bids/Streetlight-Materials-Installation/0000441022?purchasingGroupId=8409951&origin=1) | Check that it is not trenching/civil (rule 8) |
| 14 | not stated | Security Electronics Maintenance & Support Services | BidNet 0000441668 | 2026-11-25 | not stated | Maintenance/support of security electronics (low-voltage, via sub) | not stated | [BidNet 0000441668](https://www.bidnetdirect.com/colorado/solicitations/open-bids/Security-Electronics-Maintenance-Support-Services/0000441668?purchasingGroupId=8409951&origin=1) | Posted ~10/27 |
| 15 | not stated (possibly Arapahoe Park & Rec District; unconfirmed) | Spring Creek Park Pavilion Repairs | BidNet 0000440811 | 2026-11-30 | not stated | Repairs to a park pavilion (handyman/facilities) | not stated | [BidNet 0000440811](https://www.bidnetdirect.com/colorado/solicitations/open-bids/Spring-Creek-Park-Pavilion-Repairs/0000440811?purchasingGroupId=8409951&origin=1) | |
| 16 | not stated | Grandview Elementary Roof Project | BidNet 0000441189 | 2026-12-02 | not stated | School roof project | not stated | [BidNet 0000441189](https://www.bidnetdirect.com/colorado/solicitations/open-bids/Grandview-Elementary-Roof-Project/0000441189?purchasingGroupId=8409951&origin=1) | School roofs often have mandatory walks. Check soon |
| 17 | not stated (paid aggregate notice) | Staged System Upgrade of the Current HVAC System | BidNet 444196018422 | 2027-02-26 (record says 19:00 EST) | not stated | Phased HVAC system upgrade | not stated | [BidNet aggregate](https://www.bidnetdirect.com/private/supplier/interception/open-notice/444196018422?target=view) | Prior verdict: EVALUATE. DOC-HUNT says the whole package needs a BidNet login |

## C. Borderline (trade-adjacent or Luke's call)
| Agency | Title | Sol # | Due (MT) | Pre-bid / walk | Why borderline | Link |
|---|---|---|---|---|---|---|
| not stated (City of Boulder park) | Restroom / Pavilion Renovation at North Boulder Park | BidNet 0000438381 | 2026-11-02 | not stated | Plumbing-heavy, but it is a general-contractor renovation. Prior triage put GC renovations as NO | [BidNet 0000438381](https://www.bidnetdirect.com/colorado/solicitations/open-bids/Restroom-Pavilion-Renovation-at-North-Boulder-Park/0000438381?purchasingGroupId=8409951&origin=1) |
| not stated | High School Restroom Upgrades | BidNet 0000440970 | 2026-11-13 | not stated | Plumbing-heavy GC renovation | [BidNet 0000440970](https://www.bidnetdirect.com/colorado/solicitations/open-bids/High-School-Restroom-Upgrades/0000440970?purchasingGroupId=8409951&origin=1) |
| not stated (CU Boulder) | UCB001155 MULTI-Rooftop Safety (2024-113M23) | BidNet 0000440323 | 2026-11-16 | not stated | Roof fall-protection install, specialty. CU jobs often have mandatory pre-bids (UCB001284 did) | [BidNet 0000440323](https://www.bidnetdirect.com/colorado/solicitations/open-bids/CU-Boulder-UCB001155-MULTI-Rooftop-Safety-2024-113M23/0000440323?purchasingGroupId=8409951&origin=1) |
| Douglas County | HVAC Filters & Belts (IFB) | 042-26 | 2026-11-18 **15:00 per IFB page 1** ("NO LATER THAN NOVEMBER 18, 2026 3:00 PM"; BidNet says 2:00 PM) | none in IFB calendar; questions due 2026-11-02 15:00 | Supply. The IFB lists estimated annual usage (about 3,176 filters/yr by my count of the bid schedules, plus Exhibit A belts), but: "authorizes, but does not obligate, the County to order any minimum or maximum." Rule 9 = not GO. The belts may suit the dads-company profile | [BidNet 0000441328](https://www.bidnetdirect.com/colorado/solicitations/open-bids/HVAC-Filters-Belts/0000441328?purchasingGroupId=8409951&origin=1) |
| not stated (Aurora golf course) | Saddle Rock Golf Club Restroom Remodel | BidNet 0000441357 | 2026-11-18 | not stated | Plumbing-heavy GC remodel | [BidNet 0000441357](https://www.bidnetdirect.com/colorado/solicitations/open-bids/Saddle-Rock-Golf-Club-Restroom-Remodel/0000441357?purchasingGroupId=8409951&origin=1) |
| USPS | Denver P&DC Roof Replacement | 089495-27-A-0001 (K95856) | 2026-11-20 13:00 MT (3:00 p.m. EST) | Pre-proposal 2026-11-04 09:00 on site, **not mandatory** ("strongly recommended"; teleconference available) | Too big: "estimated cost of the work is between $12,000,000 and $13,000,000", about 470,000 sq ft, 540 days. Bonding is out of reach. Prior verdict: NO | [HigherGov mirror](https://www.highergov.com/contract-opportunity/denver-co-denver-p-dc-roof-replacement-k95856-089495-27-a-0001-o-ead75/) |

## D. Dead on arrival: in our trades, but the mandatory walk has already passed (not in pipeline.json)
| Agency | Title | Sol # | Due | Mandatory walk (missed) |
|---|---|---|---|---|
| US Bureau of Reclamation | SLV-CB Pumping Plant Roof, Mosca CO | 140R4026Q0141 | 2026-11-02 13:00 | 2026-10-14 (per bids/_pipeline.md line 86) |
| Arapahoe County | Fire Alarm Control Panel Replacement & Device Upgrade | RFP 26-51 | 2026-10-30 | 2026-10-16 10:00 |
| Colorado Convention Center | Annual Fire Alarm System Troubleshooting & Repair | RFP 2026-5075-1700633 | 2026-11-02 17:00 | 2026-10-15 13:00 |
| Colorado Convention Center | Roof Repair Services | RFP 2026-5375-1709717 | 2026-11-09 17:00 | 2026-10-21 11:00 |
| Denver Public Schools | Fire Alarm Replacement & Renovations 2027-2028 | BD2733 | 2026-11-19 10:00 | 2026-10-27 10:00 |

## E. Excluded after review (main reasons)
- CU Boulder UCB001622 NBC Irrigation & Landscape: the RFQ is "ARCHITECTURAL / ENGINEERING / CONSULTING SERVICES" (design, $2.5M-$4.0M project). Not a construction bid.
- Weld Nurses Station Renovation (B2600112), Adams Health Env. Health Renovation (RFPAR2026841), CU ECOT window replacement, Rifle Trades Center, Idea Forge: GC renovation or glazing/abatement.
- Out of state: Friant Dam HVAC (CA), NCAO fire alarm (CA), SACN fire alarm (WI), Hoover Dam janitorial (NV), plus all WY listings (Douglas WY painting, Paradise Valley pool, Teton library lighting, etc.).
- Supply: water-treatment chemicals, mechanical joint restraints, Highlands Ranch chemicals, can liners and tissue.
- Not our trades: elevators (DHA 26-019, COS Airport), fencing (DougCo, NREL design-build), PGMB security gate, encampment cleanup, hazmat response, parking lot sweeping, security film, mold remediation, Superior tank cover, Pueblo tank roof welding.
- Heavy civil / design (rule 8): pump stations, ponds, roads, sewer, engineering on-call.

## Next steps (for HQ / Luke)
1. **Weld RTU (B2600111):** the mandatory walk is 2026-11-05 09:00 in Greeley, 8 days out. Under rule 0b, start HVAC sub outreach today. If no sub can make 11/05, Luke attends.
2. **Morgan County roof:** the walk is tomorrow, 2026-10-29 10:00, in Fort Morgan. Luke decides whether to go.
3. **16 of the 23 rows in B and C have no scraped BidNet detail** (agency, pre-bid, docs). Each needs a logged-in BidNet open, from the VM scanner or by Luke. Do the three aggregate notices (Station One, Snowmelt Boiler, Staged HVAC) and DPS Fire Suppression first.
4. Restart GovTribe at govtribe.com/account (inactive since 2026-10-27).
