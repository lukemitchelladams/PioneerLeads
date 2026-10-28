# Portal expansion map: Colorado, Kansas, Wyoming (2026-10-28)

Research only. Nothing was registered, no one was emailed, `pipeline.json` was not touched, nothing was committed.
Scope: portals we do NOT already watch (we watch BidNet/RMEPS Colorado logged in, SAM.gov for Colorado, Euna/Bonfire for
Parker only, GovTribe). Trades: HVAC, plumbing, electrical, facilities maintenance, janitorial, grounds/snow, generators,
boiler/water treatment. Heavy civil, design, IT and pure supply are left out.

## Read this first

- **Two mandatory walks are tomorrow, 2026-10-29, on bids that came from a portal we do not watch (ColoradoVSS):**
  - **09:00 MT, Denver:** DPA Capitol Complex IH-25043, the State Parking Garage entrance remodel at 1350 Lincoln St
    (DQ1-AAHA-2027000145-1, $75,000 budget, quotes due 2026-11-06 14:00 MT). This one is not in our BidNet feed.
  - **15:00 MT, Pueblo:** Pueblo Community College, ADA Upgrades at the Davis Academic Building (IFB1-GJKA-2027000046-1,
    estimated $824,000, bids due 2026-12-03). Attendance is mandatory and you must sign in.
- **Correction on the OpenGov list:** DPS, Aurora, Fort Collins, Boulder County, Jefferson County, Adams County,
  Broomfield, Westminster, Thornton, Arvada, Lakewood, Longmont, Loveland, Greeley, Castle Rock and Colorado Springs are
  **not** OpenGov buyers. All of them except Boulder County (Euna) and DPS (its own site plus some BidNet posts) post
  formal bids on BidNet RMEPS. Each agency's own procurement page says so (Adams, Colorado Springs, Fort Collins and
  Westminster were re-checked today; the rest were checked 2026-10-20 in
  `ops/research/2026-10-20-colorado-coverage-map.csv`). Our logged-in scanner already reads BidNet RMEPS: 604 open
  statewide at 13:47Z today.
  The OpenGov buyers in our area are RTD, City of Golden, Wheat Ridge and City of Pueblo, plus Cheyenne, WY and
  Lawrence, KS.
- **Correction on Ionwave and Jaggaer:** Denver Water is on BidNet, and its own page names QuestCDN for downloads. CU
  posts on BidNet. Neither one posts bids on Ionwave. The Ionwave buyers we found are KU (kuebids) and Johnson County, KS
  (jocogov). Jaggaer did not show up as a bid board for any CO or KS buyer we checked.
- **GovTribe coverage check: BLOCKED.** `Search_State_And_Local_Contract_Opportunities` returned UPGRADE_REQUIRED today.
  The subscription has been inactive since 2026-10-27 04:23Z. The "GovTribe" column below therefore uses the 2026-10-20
  source sample: GovTribe indexed ColoradoVSS, OpenGov, Euna and constructionbidsource, with about a 6-day lag, and it
  indexed 0 BidNet records.
- **BidNet is the biggest coverage lever we already own.** Of today's 59 open ColoradoVSS solicitations, about 30 also
  show up in our BidNet aggregate feed (fuzzy title match). Of Boulder County's 11 Euna bids, 6 do. Each mirrored copy
  shows up late and without agency or keyword tags. Watching these portals directly gets same-day coverage and catches
  the other half.

## (A) Portal map, sorted by value (most Front Range facilities bids we are missing first)

"Public list" means the open-bid list was read today from this session without logging in. Times are local.

| # | Portal | Who posts there | Public bid list | Read without login? (2026-10-28) | Vendor registration | Already covered? | In-trade open today |
|---|---|---|---|---|---|---|---|
| 1 | **ColoradoVSS** (CGI Advantage, run by DPA/OSC) | State agencies: DPA Capitol Complex / Office of the State Architect, CDOC, CDHS, DMVA, CPW, CDPHE; community colleges (Red Rocks, Pikes Peak State, Pueblo CC, Otero, CCCS); AHEC also posts here | [colorado.gov/vss](https://prd.co.cgiadvantage.com/PRDVSS1X1/Advantage4), then **View Published Solicitations** | **YES.** 59 open listed. Detail tabs and attachment downloads work without an account. | Free. "Register Your Vendor Account" on the same page. Email notices go out by commodity code. Help: vsshelp@state.co.us | BidNet aggregate mirrors about 30/59, late. **SAM: no. GovTribe: indexed before 10-27 (197 CO VSS records 9/1-10/20).** CDOT and the universities (CU, CSU, Mines, UNC) post on RMEPS instead (OSC table). | 5 (B1, B2, B4, B5, B7) |
| 2 | **OpenGov Procurement** | RTD (`rtd-denver`), City of Golden (`cityofgolden`), Wheat Ridge (`wheatridgeco`), City of Pueblo (new; its own bid page shows 0 open), Cheyenne WY, Lawrence KS (`lawrenceks`) | `procurement.opengov.com/portal/<agency>` | **BLOCKED.** Cloudflare "Just a moment" challenge to this session; not bypassed. | Free, one account for every OpenGov agency. "Follow" each agency to get new-bid and addendum emails. | Not BidNet. GovTribe indexed it before 10-27 (21 CO records). RTD bus shelters (126DM016) is already in our pipeline. | Unknown (blocked) |
| 3 | **Euna Procurement (ex-Bonfire)**, Boulder County | Boulder County (Parker is already scanned) | [bouldercounty.bonfirehub.com](https://bouldercounty.bonfirehub.com/portal/?tab=openOpportunities); also an [informational county list](https://bouldercounty.gov/government/budget-and-finance/procurement/bid-opportunities/) | **YES for the list** (11 open). Opportunity pages: **BLOCKED** (Cloudflare), so pre-bid info is not readable. | Free. A portal-specific Euna account plus NIGP codes. "Registration is easy and free" (county page). | BidNet aggregate mirrors 6/11. Our Bonfire module only scans `parkeronline`. | 2 (B3, B6) |
| 4 | **Denver Public Schools** own site | DPS Strategic Sourcing | [financialservices.dpsk12.org/strategic-sourcing](https://financialservices.dpsk12.org/strategic-sourcing/) | **BLOCKED.** JavaScript "client challenge". | DPS supplier registration. Steps not readable from here. Construction notices go out by email from constructionbids@dpsk12.org (2026-10-20 research). | **Partly.** Some DPS RFPs reach BidNet (BD2733 fire alarm, "DPS Fire Suppression 2027" are in our feed). The rest is unknown. | Unknown |
| 5 | City of Englewood, new platform | Englewood | [englewoodco.gov solicitations](https://www.englewoodco.gov/government/city-departments/finance/solicitation-opportunities-awards) | **BLOCKED** (403). | Left RMEPS 2025-02-10. Vendors must register on the new, unnamed system. Purchasing: 303-762-2412. | No | Unknown |
| 6 | Colorado Public Notice (newspaper bid ads) | Catch-all for "advertisement for bids" statewide | [publicnoticecolorado.com](https://www.publicnoticecolorado.com/) | Site loads. Manual search is free; not run this pass. | Smart Search email alerts are paid ($75 per 30 days per the 2026-10-20 research) | Partly overlaps everything | Not run |
| 7 | QuestCDN | Denver Water (downloads), many town and district construction plan sets | questcdn.com | **BLOCKED** (403) | Free to browse; some plan sets charge a download fee | Denver Water bids are on BidNet | Mostly construction |
| 8 | **BidNet Kansas Purchasing Group** (same BidNet login we already have) | KS statewide aggregate: State of Kansas events, Wichita, KCK UG, KCK Public Schools, Manhattan, Ellsworth, KDOT lettings, others | [bidnetdirect.com/kansas](https://www.bidnetdirect.com/kansas) | **YES for titles and dates** (195 open). Agency and docs are members-only. Only one page was fetched, to keep BidNet's robot check away from the live scanner. | Free: add the Kansas group to Brown Bison's existing BidNet account | Scanner reads `/colorado` only. 0 KS rows. | B17 and more (agency not shown publicly) |
| 9 | Kansas eSupplier (state agencies; SMART/PeopleSoft) | KS Dept of Administration, KDOT, KHP, Revenue, KDWP, KDHE, etc. | [eSupplier bid solicitations](https://supplier.sok.ks.gov/psc/sokfsprdsup/SUPPLIER/ERP/c/SCP_PUBLIC_MENU_FL.SCP_PUB_BID_CMP_FL.GBL) | **YES.** 28 open. Event pages open without login. | Free bidder registration ([admin.ks.gov](https://admin.ks.gov/offices/procurement-contracts/bidding--contracts/bidder-registration)). Needs a US tax ID. Notices go out by category code. Bids@ks.gov, 785-296-2376. | Partly mirrored in BidNet KS | 4 (B13-B16) |
| 10 | City of Wichita (Euna/Bonfire) | Wichita | [wichita.bonfirehub.com](https://wichita.bonfirehub.com/portal/?tab=openOpportunities) | **YES for the list** (18 open). Details are Cloudflare-blocked. | Free (city says "free and easy") | Partly mirrored in BidNet KS | 3 (B8-B10) |
| 11 | Ionwave: KU eBids and Johnson County KS | University of Kansas; Johnson County + JCPRD | [kuebids.ionwave.net](https://kuebids.ionwave.net/SourcingEvents.aspx?SourceType=1), [jocogov.ionwave.net](https://jocogov.ionwave.net/SourcingEvents.aspx?SourceType=1) | **YES.** KU 4 open, JoCo 6 open. Event detail pages are public too. | Free. JoCo approves applicants after reviewing their documents. | No | 1 (B12) |
| 12 | KCK Unified Government eProcurement (own system) | Wyandotte County / Kansas City, KS | [purchasing.wycokck.org](https://purchasing.wycokck.org/eProcurement/Bid_Download.aspx) | **YES.** 7 open. | Vendor login on the same site (fee not stated) | Partly mirrored in BidNet KS | 0 (R43262 is wastewater/stormwater facility maintenance; excluded under rule 8) |
| 13 | Other Kansas buyers | Olathe (Bonfire, 1 open: fiber interconnect), K-State ([bidportal.ksu.edu](https://bidportal.ksu.edu/), bids&tenders, free, JavaScript table not pulled), KUMC ([HTML list](https://www.kumc.edu/finance/supply-chain/bid-opportunities.html), 1 open: vehicle), Topeka (e-Pro supplier portal via topeka.org/procurement, not read), Shawnee County (rpm365 portal, loads, list not parsed), Sedgwick County (platform not identified), Overland Park (purchasing URL 404, platform not identified), Lawrence (OpenGov, blocked) | see cell | Mixed | Mostly free | No | 0 found |
| 14 | SAM.gov for Kansas and Wyoming | Fort Riley, Fort Leavenworth, McConnell AFB (KSANG 184th), VA Leavenworth/Wichita, FAA KC District, F.E. Warren AFB (90 CONS), Cheyenne/Sheridan VA | sam.gov | **YES.** Read today from the API key in `~/.brownbison/env` (2 calls) and the 2026-10-28 nightly bulk file | Already registered (UEI EV9QPAPM4C47) | **Not scanned.** The `brownbison` profile has `"states": ["CO"]` only. | 3 (B18-B20) |
| 15 | Public Purchase | State of Wyoming A&I (`wyominggsd,wy`), WY State Construction Dept, Moffat County CO | [WY public page](https://www.publicpurchase.com/gems/wyominggsd,wy/buyer/public/home) | **NO.** "Please log in to view the open bids for this agency." | Free. Accounts can take up to 24 h to activate. Uses NAICS codes. | No | Unknown |
| 16 | City of Cheyenne, WY | Cheyenne | cheyennecity.org/Bids-and-Proposals → OpenGov | **BLOCKED** (403) | Free (OpenGov) | No | Unknown |
| 17 | University of Wyoming | UW | uwyo.edu/buy-wy | **BLOCKED** (host unreachable) | - | No | Unknown |
| 18 | Skip: BidExpress | CDOT and KDOT highway lettings | bidexpress.com | BLOCKED (403) | Paid per-bid/subscription | n/a | Heavy civil (rule 8) |
| 19 | Skip: DemandStar | No CO/KS target buyer found. Lawrence left it 2025-04-29. | demandstar.com | n/a | Free for 1 agency, paid beyond that | n/a | 0 |
| 20 | Skip: Periscope / BidSync | Folded into SOVRA (BidNet's parent). No CO/KS target buyer found. | bidsync.com | n/a | n/a | n/a | 0 |

**Already covered by our BidNet RMEPS scan, so no new registration is needed:** City and County of Denver (its bid page
says it joined RMEPS), Denver International Airport, Denver Housing Authority, Aurora, Fort Collins, City of Boulder,
Jefferson County, Adams County, Broomfield, Westminster (formal bids; an "E-Procurement Platform" for informal quotes is
unnamed), Thornton, Arvada, Lakewood, Longmont, Loveland, Greeley, Castle Rock, Colorado Springs + Colorado Springs
Utilities, El Paso County, Douglas County, DCSD, Larimer, Weld, Littleton, Centennial, Mesa County, Grand Junction, Denver
Water, Metro Water Recovery, CU (all campuses), CSU, Mines, MSU Denver/AHEC, CDOT (non-highway). School districts: Cherry
Creek, Jeffco, Adams 12, Boulder Valley, St. Vrain, Poudre, Academy 20 (its supplier page names BidNet), D11, Aurora
Public Schools, Littleton Public Schools (seen on BidNet), Westminster PS, 27J (only some bids; others go by email).
A "City Of Westminster" Euna portal also exists (`cityofwestminster.bonfirehub.com`, 0 open). We could not confirm
which Westminster runs it.

### Register now: free registrations for Luke today, ranked

1. **ColoradoVSS vendor account.** Go to colorado.gov/vss, choose "Register Your Vendor Account", and send notices to
   luke@brownbisonco.com. Add commodity codes for HVAC, plumbing, electrical, building maintenance/repair (912, 914xx),
   janitorial, grounds and snow. It's free. Biggest gap: state facilities in Denver metro, and half of it never reaches
   our BidNet feed. Tomorrow's two mandatory walks came from here.
2. **OpenGov Procurement vendor account (one login).** Follow RTD, City of Golden, Wheat Ridge and City of Pueblo. Add
   Cheyenne and Lawrence only if WY or KS work goes ahead. Free. This is the only way to see these from here, because
   the portals block cloud sessions.
3. **Boulder County Euna portal account** with NIGP codes. Free. Also set `BONFIRE_USER`/`BONFIRE_PASS` in the
   environment. Health shows "Bonfire no login" today, which means no Parker or Boulder County documents can be pulled.
4. **DPS supplier registration** through the Strategic Sourcing site (open it in a browser; it blocks cloud sessions).
   Then ask constructionbids@dpsk12.org to add Brown Bison to the construction notice list. Luke sends that email; we
   did not.
5. **Englewood's new solicitation system.** Call 303-762-2412 for the link, because the page blocks us.
6. **Kansas, only if Luke wants KS work (every KS bid needs a local sub and a site-walk person):**
   1. Add the Kansas Purchasing Group to the existing BidNet account. One step, and it covers 195 KS bids.
   2. Kansas eSupplier bidder registration.
   3. City of Wichita Euna account.
   4. KU Ionwave supplier account.
   5. Johnson County Ionwave supplier account.
7. Stretch, Wyoming: Public Purchase (State of Wyoming) account.

Scanner changes that need no login. These are recommendations for the scanner owner and were not made here:
- add a ColoradoVSS public-list reader to the scanner (Playwright, 100 rows a page, detail tabs and docs public);
- add `bouldercounty`, plus `wichita` and `olatheks` if Kansas is on, to `bonfire_orgs`;
- add `KS` (and `WY`) to the `brownbison` profile's SAM `states`;
- add `/kansas` to the BidNet statewide pass;
- add Ionwave public lists (kuebids, jocogov), the Kansas eSupplier public list and KCK `Bid_Download.aspx` (all plain
  HTML).

## (B) Open in-trade bids found on portals we can read without logging in

"In our feed?" means it already sits in `bids/_watch/open_bids.json` (BidNet/SAM scan at 13:47Z today). A pre-bid entry
is only given when it was read in the solicitation itself; otherwise it says why it is missing.

### Colorado (Front Range first, then by date)

| # | Agency | Title | Number | Due | Pre-bid / site walk | Portal | In our feed? | Link / note |
|---|---|---|---|---|---|---|---|---|
| B1 | DPA, Capitol Complex Facilities (Office of the State Architect) | IH-25043 State Parking Garage Single Entrance Remodel, 1350 Lincoln St, Denver: install a storefront entrance/exit | DQ1-AAHA-2027000145-1 | **2026-11-06 14:00 MT** (questions 2026-10-30 14:00) | **MANDATORY on-site pre-bid Thu 2026-10-29 09:00 MT**, 1350 Lincoln St, NW corner of Lincoln St & E 14th Ave (DQ sec. C.7). **Tomorrow.** | ColoradoVSS | **NO (new)** | Budget $75,000. Bid security of 5% applies at an estimated $50,000 or more (DQ F.5). Contact Richard Sartirana, 303-866-3983. Storefront/glazing plus electrical and security components; needs a storefront sub. Docs: Specifications, CDs, DQ (public in VSS). |
| B2 | Pueblo Community College | ADA Upgrades, Davis Academic Building (Project 2026-049M25), CSBV two-step | IFB1-GJKA-2027000046-1 | Quals 2026-11-24 14:00 MT; **bids 2026-12-03 14:00 MT** | **MANDATORY pre-bid conference and site tour Thu 2026-10-29 15:00 MDT**, Davis Academic Bldg, 900 W. Orman Ave, Pueblo, Room 210M. You must sign in. **Tomorrow.** | ColoradoVSS | Yes, as an untagged aggregate row ("ADA Upgrades"). It did not match our keywords. | Estimated $824,000 construction hard cost. GC-type ADA work, a weak fit for our trades. Listed because the walk is tomorrow. |
| B3 | Boulder County Public Works | Sheriffs Head Quarters Lighting Upgrades | BID-321-26 | 2026-11-05 14:00 MST | Not readable: the Euna opportunity page is Cloudflare-blocked, and the county list shows no meeting | Euna (Boulder County) | Yes (aggregate row, keyword match; not in `pipeline.json` or the watchlist) | [Euna list](https://bouldercounty.bonfirehub.com/portal/?tab=openOpportunities), opp id 258797. Electrical. Docs need a Euna login. |
| B4 | Pikes Peak State College | PPSC DQ 27-006 Operable Wall Partitions (replace operable wall, Downtown Studio Campus, Colorado Springs) | DQ1-GJJA-2027000129-2 | 2026-11-13 14:00 MST | None in the SOW (Exhibit D). Amendment #1 was not read. | ColoradoVSS | Yes (aggregate row, untagged) | Turnkey furnish/install partition system. Specialty installer; weak fit. |
| B5 | AHEC for MSU Denver | CAVEA Lighting | DQ1-GMAA-2027000142-1 (AHEC-27901-D) | 2026-11-16 14:00 MST | MANDATORY pre-bid conference and site tour 2026-11-04 14:30, Jordan Student Success Bldg Rm 420, 890 Auraria Pkwy | ColoradoVSS + BidNet | **Already WATCHED.** `_pipeline.md` says NO (theatrical DMX lighting; project minimums not met). | Listed only for completeness. |
| B6 | Boulder County (Climate / Sustainability) | Homeowner Association (HOA) Heat Pump Adoption Program | SP-325-26 | 2026-11-20 14:00 MST | Not readable (Euna page blocked) | Euna (Boulder County) | **NO (new)** | HVAC heat pumps. The county program page describes bulk purchasing and/or installation support for HOAs (program lead Andy Kadlec, akadlec@bouldercounty.gov). What the solicitation asks for is **not in hand yet**; docs need a Euna login. EVALUATE. |
| B7 | DMVA (Colorado Army National Guard) | Montrose Indoor Firing Range Lead Dust Remediation (Project 082411), design-build lump sum | RFP-OAAA-2027000078-1 | 2026-12-02 14:00 MST | **MANDATORY pre-proposal meeting 2026-11-05 11:00**, Montrose RC, 12147 6390 Road, Montrose (VSS instructions) | ColoradoVSS | **NO (new)** | Western Slope abatement. Weak fit; listed because the meeting is mandatory. Buyer Kimberlie Smith. |

Seen on ColoradoVSS and left out:
- TCF Boiler Chemicals DQ1-CAAA-2027000037-3: already in pursuit, due 2026-10-29 17:00.
- CTF DRDC Fire Protection IFB1-CBAA-2027000036-2: already dropped.
- Yampa SP Seasonal Housing RV Sites: sitework, rule 8.
- Otero JC sole-source intent to Trane: not biddable.
- GMYC laundry: not our trade.

Boulder County's other 9 Euna bids are outside our trades. Of those, BID-313-26 HVAC air filters was already killed by
Luke under rule 9. Parker's 2 open Euna bids are both engineering.

### Kansas (state, city, university; local sub needed for every one)

| # | Agency | Title | Number | Due | Pre-bid / site walk | Portal | Link / note |
|---|---|---|---|---|---|---|---|
| B8 | City of Wichita | Rooftop Electric HVAC Unit for Century II | 260261 | 2026-11-06 10:00 CST | Not readable (Bonfire page blocked) | Euna (Wichita) | [list](https://wichita.bonfirehub.com/portal/?tab=openOpportunities), opp 258870. It is **not in hand yet** whether this is an install or equipment only. If it is supply only, rule 9 applies. |
| B9 | City of Wichita | HVAC Replacement at Thirteen (13) Residential Sites | 260258 | 2026-10-30 10:00 CDT | **MANDATORY pre-bid was 2026-10-20 10:00 CT and has PASSED** (`_pipeline.md`) | Euna (Wichita) | Dead. Listed so nobody reopens it. |
| B10 | City of Wichita | Mowing and Haying of Floodway | 260250 | 2026-11-20 10:00 CST | Not readable | Euna (Wichita) | opp 256532. Grounds. |
| B11 | City of Wichita | Lincoln Street Dam Hydraulic System Maintenance | 260264 | 2026-11-13 10:00 CST | Not readable | Euna (Wichita) | opp 259242. Mechanical service on a dam; borderline under rule 8. |
| B12 | University of Kansas (Lawrence) | On-Call Snow Removal | RFP 3305201 | 2026-11-06 14:00 CT | Pre-proposal conference **Fri 2026-10-30 09:00 CT**, Teams by phone (785-864-5000, conf ID 739 929 752#). The RFP says "We encourage participating Bidders to attend"; it is **not stated as mandatory**. Questions closed 2026-10-22. | KU Ionwave | [event](https://kuebids.ionwave.net/PublicDetail.aspx?bidID=2889&SourceType=1). Pricing spreadsheet in attachments. Buyer Ramia Whitecotton, rmwcotton@ku.edu. |
| B13 | State of Kansas, Dept of Administration | Kitchen Hood Inspection (line: "Kitchen Hood Inspection and Cleaning") | EVT0010960 | 2026-11-03 14:00 CST | Not shown on the event page; it may be in the bid package (not opened) | KS eSupplier | Contact Ashley N Evans. |
| B14 | State of Kansas, Dept of Revenue | Janitorial Services - Manhattan DLEX | EVT0010962 | 2026-11-19 14:00 CST | Not shown on the event page | KS eSupplier | Already noted in memory 2026-10-18 as "plausible, needs local sub". |
| B15 | Kansas Highway Patrol | Lawn Care - Pleet & Patrol Hanger (sic) | EVT0010964 | 2026-11-24 14:00 CST | Not shown on the event page | KS eSupplier | Grounds. |
| B16 | KDOT | Bard HVAC Units | EVT0010972 | 2026-11-19 14:00 CST | Not shown | KS eSupplier | Probably an equipment purchase. Rule 9 applies unless the package shows installation and quantities. |
| B17 | Not shown publicly (BidNet KS members-only) | 2026-2027 GROUNDS BID | not shown | 2026-12-02 | Not shown | BidNet Kansas | Agency and docs become visible once the Kansas group is added to our BidNet account. |

### Federal, Kansas and Wyoming (SAM.gov; our scan covers Colorado only)

| # | Agency | Title | Number | Due | Pre-bid / site walk | Link / note |
|---|---|---|---|---|---|---|
| B18 | VA NCO 15, Dwight D. Eisenhower VAMC, Leavenworth KS | Fire, smoke and automatic door inspection, maintenance and repair (IDIQ, five 12-month periods) | 36C25526Q0617 | **2026-11-03 15:00 CT** (extended) | Site visit **was** 2026-10-15 09:00 CDT, with registration by 10-13. **Passed**; the notice does not call it mandatory. | [SAM](https://sam.gov/workspace/contract/opp/0abf28bc5f5c4bf69faa3f1da4a2e481/view). 100% small business, NAICS 541350. |
| B19 | FAA, Regional Acquisitions (697DCK) | Consolidated Weed Control, western side of Kansas City District facilities (Olathe KS) | 697DCK-26-R-00432 | **2026-11-06 17:00 ET** (Amendment 0003) | "Site Visits are optional." Schedule them with each site POC listed in the SOW. | [SAM](https://sam.gov/workspace/contract/opp/c4a32e87744b4dd287774759d7e5b502/view). Small business set-aside, NAICS 561730. CO Marshavia Clark. |
| B20 | Army MICC Fort Leavenworth | Underground Fuel Tank Testing and Repair Services (**sources sought**) | PANMCC-26-P-048611 | 2026-11-06 12:00 CT | n/a | [SAM](https://sam.gov/workspace/contract/opp/06f2837e447f4ab295600ddab63238d8/view). Market research only. |

Federal KS/WY seen and left out:
- KSANG 184th Wing (McConnell AFB) W50S7X27Q0001 "Switchgear Transformer Replacement": the description is a purchase of
  1 transformer and 3 fuses, so supply (rule 9).
- Fort Riley EAGLE W519TC26RA054: closed today at 12:00.
- 90 CONS F.E. Warren: furniture, musicians and battery maintenance.
- VA Sheridan lightning protection 666-27-102: already NO.
- Cheyenne VA PT addition: GC construction.
- Yellowstone, FLH and USFS road and water jobs: heavy civil.
- VA NCO 15 jobs with Missouri places of performance (Poplar Bluff HVAC, St. Louis grounds and roofs): out of area.

Wyoming local: nothing readable. The State of Wyoming is on Public Purchase (login required), and Cheyenne and the
University of Wyoming are blocked. The only WY facilities item we found, Teton County Library lighting retrofit (due
2026-11-16, Jackson), is already in our BidNet aggregate feed.

## Method and blocks (for the next session)
- **ColoradoVSS:** Playwright on the public "View Published Solicitations" grid (100 per page, 59 rows), with detail
  tabs and public attachment downloads. The PDFs were read from the scratchpad, not the repo.
- **Euna:** `/PublicPortal/getOpenPublicOpportunitiesSectionData`, the same public JSON our Parker module uses. Org
  subdomains were found by probing (CO/KS hits: `bouldercounty`, `parkeronline`, `wichita`, `olatheks`).
- **Ionwave:** `SourcingEvents.aspx?SourceType=1`.
- **Kansas eSupplier:** public `SCP_PUB_BID_CMP_FL` page.
- **SAM.gov:** API (2 calls today, KS and WY) plus the cached 2026-10-28 bulk CSV.
- **Blocked and not bypassed:** OpenGov, Euna opportunity pages, QuestCDN, BidExpress, Lawrence KS, Fort Collins and
  Englewood sites (403), Cheyenne (403), DPS (JavaScript challenge), uwyo.edu (unreachable), Public Purchase (login
  wall), and GovTribe (subscription).
- **BidNet:** one public `/kansas` page fetch only, to keep the live scanner clear of BidNet's robot check.
