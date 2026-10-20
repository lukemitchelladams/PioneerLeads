# Commercial bid aggregators vs. our scraper (research agent, 2026-10-20)

**Verdict:** no product verified gives Colorado local bids + full documents + an API within hours. BidNet/RMEPS
documents sit behind BidNet's login and there is no public BidNet API, so our logged-in scraper plus BidNet's own
alert emails stay primary.

- **GovTribe** ($1,900/seat/yr, credit-metered, MCP only, no REST): Colorado local feed in 2026 = Bonfire, OpenGov,
  CO VSS, Construction Bid Source. Of 363 Colorado records since 2026-07-01, **0 were BidNet-sourced**. Lag ~6 days.
  Excellent document backstop for Bonfire/OpenGov bids (Parker 26-028 files were byte-identical to ours).
- **HigherGov** ($500/yr one user, $2,500/10): REST + MCP API, 20-min refresh, 10K records/mo, DIBBS/NSN coverage;
  Colorado local coverage and state/local document timing ("request-based, 1 business day") UNPROVEN. Worth a free
  trial: time Parker 26-028, Estes Park HVAC, DCSD.
- **BidNet paid** (~$100/mo or ~$599/yr): adds a daily digest; the free tier already sends "real-time bid matches"
  on registered codes. No API.
- **Euna/Bonfire + OpenGov:** free same-day vendor emails; OpenGov "Follow" sends addenda; no API.
- **SAM.gov API** (10/day; 1,000/day with an entity role) and **USAspending** (awards, no key): keep.
- Skip: BidPrime ($4.6-9.5K/yr, doc caps), GovSpend ($8.5-25K/yr), GovWin IQ ($13-119K/yr), Periscope S2G (now part of
  SOVRA, BidNet's parent), DemandStar/PublicPurchase (no Colorado targets), FindRFP/Bidhits/RFPMart/GovDirections.

**Recommended stack:** our scraper for BidNet lists + logged-in documents ($0); free alerts to the monitored inbox
(BidNet broad codes, Parker Euna, OpenGov follows); GovTribe for documents/federal (have it); SAM API + DIBBS +
USAspending ($0); HigherGov Starter only if the trial proves Colorado coverage ($42/mo). New spend $0-42/mo.
Sources: see the agent transcript; key links: sovra.com/pricing-suppliers, highergov.com/pricing, docs.highergov.com,
govtribe.com/docs, periscopeholdings.com/s2g.
