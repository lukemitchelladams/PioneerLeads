# 2026-11-13 off-scanner portal sweep (worker, workflow wtnqd0o29: 4 finders + 4 triage/verify agents)

Question: are open Colorado bids in our trades sitting on portals the scanner does not read (OpenGov, Bonfire, DemandStar /
Public Purchase / legal notices, agency-run pages)? Evidence is search snippets only (WebFetch and curl to these hosts are
blocked from the cloud). Nothing was contacted.

**Answer: almost nothing new.** Every in-trade, open hit was already tracked from BidNet/RMEPS: Colorado Springs R26-099MZ parks
irrigation (12/02), R26-080JW janitorial (11/23), R26-082JW snow (11/23), CU Boulder UCB001011 restroom renovations (12/10),
Fort Collins ITB 10366 overhead doors (12/02), PSD hoods (11/20), BidNet 0000441729 PA/intercom RFI (12/18).

New, all unverified (ledgered):
- City of Englewood on-call HVAC repair/install/PM (aggregator only; Englewood left RMEPS 2025-02-10): EVALUATE, probably closed ~10/20.
- DPA IH-24051 Boiler Replacement, 1881 Pierce St (sources sought, samsearch shows due 12/03): EVALUATE; not on the VSS open list.
- Pueblo Hunter Education SAA HVAC design-build (dates conflict 11/03 vs 12/10): EVALUATE; not on the VSS open list.
- DPA IH-26012 SSB cooling tower refurbish: NO (not open).

Coverage notes:
- Only three Colorado agencies show up on OpenGov Procurement in the search index: **RTD (portal/rtd-denver), City of Pueblo
  (portal/pueblo), City of Wheat Ridge (portal/wheatridgeco)**. Each has a public embed list
  (procurement.opengov.com/portal/embed/<slug>/project-list?departmentId=all&status=all). Allowing procurement.opengov.com would let
  the scanner read all three; today none of them is scanned.
- Englewood runs its own post-RMEPS platform: not scanned.
- Closed, don't chase: Englewood CATS boiler/chiller (10/29), COS parks maintenance on-call R26-077MZ (10/20), DHA on-call snow
  (8/19), DEN HVAC filter/coil PM (8/14), Clear Creek RE-1 night custodial (7/02).

Flag for HQ: the pipeline row cos-oncall-janitorial lists Environment Control as pricing by Mon 11/16, but its note also says
"Mac stood EC down 11/03 (crime/master-key)". Reconcile which janitorial subs are actually pricing R26-080JW (due Mon 11/23 14:30 MST).
