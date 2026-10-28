# H2 filtration-equipment scan: CO + KS (2026-10-28)

Brown Bison Holdings LLC is the prime on every row. H2 Global Solutions is the sub.
Scope searched: design, supply and install (or replacement) of facility water filtration equipment. That covers RO, multimedia,
sand, greensand and carbon filters, UF, large or duplex softeners, cooling-tower side-stream filters, boiler makeup pretreatment,
iron/manganese, arsenic and nitrate packages, lab/dialysis RO, pool filtration and wash-water reclaim.
Excluded: municipal plant expansions and new plants (heavy civil), engineering/design-only RFPs, chemical supply, lab testing,
and routine monthly chemical treatment (tracked in `h2-fit-scan-2026-10-28.md`).
Scan run 2026-10-28, 20:40Z to 21:31Z. Nobody was contacted, and `pipeline.json` was not touched.

## Result: no open or forecast fit in Colorado or Kansas

| # | Agency | Title | Solicitation # | State | Due | Pre-bid / site visit (mandatory?) | Scope | Est. value | Link |
|---|---|---|---|---|---|---|---|---|---|
| - | none found | | | | | | | | |

Every filtration, RO, softener and pool-filter solicitation found for CO or KS in 2026 is closed, awarded or sole-sourced
(see "Recompete intel" below). No federal forecast or sources-sought notice for this scope turned up for the CO/KS installations.

## Near-misses (open, excluded)

| Agency | Title / # | State | Due | Why not |
|---|---|---|---|---|
| Not shown in feed (Aztlan Center is a Greeley facility; not verified from the listing) | Aztlan Outdoor Pool Replacement CM/GC (BidNet 0000437685) | CO | 2026-11-05 | This hires a CM/GC to rebuild the whole outdoor pool. That is construction management, not a filtration package. Pool filtration would be one trade package under the CM/GC later. |
| CDPHE | NCC WTP Operations and Maintenance (RFP-FAAA-2027000059, ColoradoVSS, posted 10/28) | CO | 2026-12-21 14:00 MST | Five-year plant operations contract (service 2027-04-01 to 2032-03-31): "conduct site-wide operations and maintenance at the North Clear Creek Water Treatment Plant" (mine drainage). It is an operator contract, not equipment install. |
| City of Lafayette (per web listings; agency not shown in feed) | Baseline Water Treatment Plant Pretreatment Train No. 1 Replacement (BidNet 0000439587) | CO | 2026-10-29 | Municipal water-plant process work, which is excluded, and it is due tomorrow. |
| City of Aurora | CAPSTC Fire Water Recycle Pond Improvements (BidNet 0000440078) | CO | 2026-11-02 | Already triaged NO on 2026-10-19 as pond/heavy civil (rule 8). The scope and any filtration content are not readable here because BidNet is blocked. |
| KDWP | Pratt Water System Improvements (EVT0010965, KS eSupplier) | KS | 2026-11-10 14:00 CST | Water-system construction, not facility filtration. The bid package was not opened. |

## Recompete intel (closed; worth watching)
- **VA Eastern Colorado HCS (Rocky Mountain Regional VAMC, Aurora; NCO 19)** keeps buying water-purification work:
  - 36C25926Q0297 / 36C25926Q0392, sand filtration media repair and refurbishment. Sources sought 2026-03, RFQ closed 2026-04-24.
  - 36C25926Q0485 / 36C25926Q0563, water filtration repair and maintenance. Notices 2026-06.
  - 36C25926Q0810, SPS RO upgrade install. Sole-sourced to Evoqua (Centennial, CO) on 2026-09-02, with the loop plumbing "to be done by others".
  - 36C25927P0006, RODI maintenance and service. Award posted 2026-10-16.
  - Next cycle: watch NCO 19 for J046/H146 notices.
- **NPS (Mesa Verde + Rocky Mountain NP)**, 140P1226Q0044, replace GAC filter media. Closed 2026-08-27, awarded.
- **Fort Leavenworth, KS**, Grant Pool Repairs, which included two sand filtration systems (W91QF4IFB2026Pool). Closed 2026-08-26, awarded as W91QF426CA008.
- **USAF Academy**, autoclave + RO system. RFI closed 2026-06-18, then a sole-source notice closed 2026-08-07.
- **Coffey County, KS**, Law Enforcement Center quad-plex water softener. Closed 2026-07-10 per a BidNet KS abstract found by web search.
- **City of Lafayette, CO**, Great Outdoors Water Park lap-pool filter replacement. Closed per an aggregator listing.

## Coverage and blockers
- **GovTribe: BLOCKED.** It returned UPGRADE_REQUIRED ("State & local contract opportunities isn't available with your current GovTribe plan"), so this scan has no GovTribe results.
- **Scraper feed** `open_bids.json` (scanned 2026-10-28 20:36Z): 723 rows (602 BidNet incl. 511 CO, 106 SAM, 13 DIBBS, 2 Bonfire). Titles and context were grepped for every requested term plus pool, aquatic, purification, deionized, UV, greensand, backwash, reclaim and similar. Hits were all municipal plant work, chemicals, HVAC air filters or out-of-state notices. **0 KS rows** in the feed.
- **SAM.gov:** used the nightly bulk CSV (72,060 rows, postings through 2026-10-27 23:07). It was filtered by CO/KS place of performance, CO/KS contracting offices (VA NCO 15 and 19, Army/AF bases), water PSCs (4610/4620/4630, J046, N046, H146 and others) and keywords. Today's postings were covered with about 20 keyword queries on SAM's public search endpoint. No open CO/KS fit.
- **ColoradoVSS:** fresh public pull at 21:26Z, 59 open. No filtration fit; the only new item is the NCC WTP O&M above.
- **Kansas, read directly:**
  - State eSupplier: 26 open.
  - KU IonWave: 4 open.
  - Johnson County IonWave: 6 open.
  - K-State bids&tenders: 0 open.
  - KUMC: 1 open.
  - KCK UG: 7 open.
  - Wichita Euna: 19 open.
  - Olathe Euna: 1 open.
  - Dodge City, Emporia, Junction City and Hays city bid pages: none fit.
  - None of the above is a filtration fit.
- **Other CO read directly:** Boulder County Euna (11 open) and Town of Parker Euna (1 open). None fit.
- **Blocked or not covered:**
  - BidNet Kansas group returned 403 to WebFetch. It was not retried from the container, to keep the live BidNet scanner clear of the robot check.
  - BidNet detail pages are blocked.
  - Wichita State: Incapsula challenge.
  - Overland Park: the bid list is a JS module.
  - Lenexa and Salina: 403.
  - Sedgwick County, USD 259 and Topeka: bid pages not found.
  - OpenGov agencies (Lawrence KS, RTD, Golden, Wheat Ridge): Cloudflare, not retried.
  - VA and Acquisition Gateway forecast tools: not checked.
- **Web searches** (Oct 2026 CO/KS water filtration, RO, softener, pool filter, side-stream, lab/prison DI/RO, base forecasts) turned up only closed or out-of-state items.
