# Colorado procurement portals vs. our scanner (research agent, 2026-10-20)

**38 of the 47 Front Range buyers checked post on BidNet RMEPS**, so the statewide scan already sees them (per-buyer
rows: 2026-10-20-colorado-coverage-map.csv). BidNet's "aggregate" tab is ~96% federal (8 of 184 local).
GovTribe is not a backstop for BidNet: its 474 Colorado local records since 2026-09-01 came from
constructionbidsource (243), ColoradoVSS (197), OpenGov (21), Euna (13), BidNet (0); newest 2026-10-14.

| Portal | Buyers | Free alerts / feed | Docs; bot wall |
|---|---|---|---|
| BidNet RMEPS | Denver, DEN, Aurora, Lakewood, Arvada, Westminster, Thornton, Broomfield, Boulder, BVSD, Longmont, Loveland, Fort Collins, Greeley, Larimer, Weld, Adams, Arapahoe, Jeffco + schools, Douglas + DCSD, Castle Rock, Littleton, Centennial, Highlands Ranch, Colorado Springs, El Paso, D11, Denver Water, Metro Water, CU, CSU, Metro State, Mines, Cherry Creek, Adams 12, 27J | NIGP agency alerts free; no RSS/API | logged in (we have it); AWS WAF |
| ColoradoVSS (CGI Advantage) | most state agencies (DOC, CDHS, CDPS); Auraria dual-posts | free, email by NIGP code; no API | public browse; none seen |
| Euna (ex-Bonfire) | Boulder County, Parker (scanned) | free account, NIGP email; list JSON works | Cloudflare on details |
| OpenGov | RTD, Pueblo, Wheat Ridge (+Golden, Brighton, Adams, Pitkin per OEDIT) | free account, subscribe to agency | Cloudflare |
| Own site / unknown | DPS (JS challenge), Englewood (left RMEPS 2025-02-10), Westminster informal quotes, D11 facilities, 27J | none found | - |
| Public HTML lists | Colorado Springs, Longmont, Lakewood, Boulder County; email lists: Pueblo Notify Me, Larimer, Aurora weekly | informational | none |

**Gaps ranked by likely in-trade spend:** 1. state agencies on VSS; 2. DPS; 3. RTD (OpenGov); 4. Boulder County (Euna);
5. Pueblo, Wheat Ridge, Englewood; 6. pockets (Westminster informal quotes, D11 facilities, 27J, Jeffco).

**Add next:** 1. ColoradoVSS free registration + NIGP codes (HVAC, plumbing, electrical, janitorial, grounds, snow) to
luke@brownbisonco.com. 2. DPS: register via Strategic Sourcing; ask constructionbids@dpsk12.org to add Brown Bison.
3. OpenGov: free account, subscribe to RTD, Pueblo, Wheat Ridge (do not scrape). 4. Euna: add Boulder County to the
Parker module (list JSON). 5. Colorado Public Notice Smart Search keyword alerts ($75/30 days) as a catch-all.
Sources: osc.colorado.gov/spco/solicitations, publicsafety.colorado.gov, bouldercounty.gov procurement,
oedit.colorado.gov, pueblo.us, financialservices.dpsk12.org, englewoodco.gov, westminsterco.gov, d11.org,
coloradosprings.gov/solicitations, longmontcolorado.gov, denverwater.org, weld.gov, denvergov.org, cu.edu.
