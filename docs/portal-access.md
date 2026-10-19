# Always-on portal access: what exists, what I built, what Luke must do

## Luke's 10-minute setup (this is the whole hoop; after it, nothing needs you)
1. Cloud environment → Edit → Network access. Either pick the broader access level, or add Allowed domains:
   `www.bidnetdirect.com`, `bidnetdirect.com`, `www.rockymountainbidsystem.com`, `api.sam.gov`, `sam.gov`,
   `www.parkerco.gov`, `www.dcsdk12.org`, `estespark.colorado.gov`, `dms.estes.org`, `bouldercounty.gov`,
   `coloradosprings.gov`, `www.douglas.co.us`, `www.denvergov.org`, `www.arapahoegov.com`.
2. Same screen → Environment variables: `BIDNET_USER`, `BIDNET_PASS` (rotate the password first), `SAM_API_KEY`.
3. BidNet → vendor profile (login already luke@brownbisonco.com). Free accounts have NO "email me every
   bid" setting (Luke confirmed 2026-10-19). What exists: (a) NIGP commodity codes on the profile, which
   agencies use to send invitations; set HVAC (910-xx mechanical maintenance, 031 air conditioning),
   plumbing (910-xx), electrical (910-xx), landscaping/grounds (988), snow (968); (b) BidNet's PAID
   notification subscription, which emails matching bids automatically, price shown at checkout. Either
   buy (b), or rely on our scraper once step 1 is done. Addenda for bids you have downloaded are emailed
   automatically on any account.
Then tell me "go". I run the live scan, fix selectors against the real pages, and create the 4-hour
scan Routine. From then on: BidNet emails land in the monitored inbox within the hour, the scraper
cross-checks every 4 hours, new matches get a bid folder and a requirements matrix automatically, and
you get a headline, not a to-do.


Luke's requirement (2026-10-19): be logged into SAM.gov and BidNet at all times, scan for new bids, catch
addenda on bids we're pursuing, pull documents for subs, with 24/7 email access. No manual logins.

## Two companies, one scan
Dad's company is a **manufacturer** (Jones Bearing / American Pulley / ConveyMor, Pelham & Leeds, AL). We
hunt product-purchase solicitations for it, not service contracts. Primary federal source is **DLA DIBBS**
(dibbs.bsm.dla.mil), searchable by FSC 3110/3130/3020/3910 without login; quoting needs a CAGE code. Paper
mills are private buyers and never post on bid portals; that is sales prospecting via Apollo/HubSpot.
`bids/_watch/watch_profiles.json` holds a profile per company. `brownbison`: HVAC, plumbing, electrical,
landscaping, janitorial, facilities (CO for BidNet; federal via SAM.gov). `dads-company`: pillow-block
bearings, pulleys, conveyors, paper-mill power transmission (federal PSC/NAICS codes, nationwide until
Luke sets states). Add a profile = add a company. Every report row is tagged with the profile that matched.

## Reality check
| Source | API / connector? | What "always connected" looks like |
|---|---|---|
| **SAM.gov** (federal only) | Yes: public Opportunities API (free key from your SAM.gov account). Also **GovTribe** MCP connector in the claude.ai directory covers federal opportunities with no key. | `scripts/samgov_watch.py` on a Routine. Parker/DCSD/Estes Park are local and will **never** be on SAM.gov. |
| **BidNet Direct / RMEPS** (Parker, DCSD, Estes Park, Douglas County) | **No API, no MCP, nothing in the registry.** Login-gated vendor portal. | Two paths, use both: (1) BidNet already emails registered vendors every new match and every addendum. Register **luke@brownbisonco.com** as the vendor contact and the hourly inbox check sees everything. (2) `scripts/bidnet_watch.py`, our own Playwright scraper: public agency pages for new/changed/closed listings, plus logged-in document download when credentials are supplied. |
| **Email** | Gmail connector, connected to luke@brownbisonco.com | Hourly inbox check Routine (docs/inbox-monitor-routine.md). |

## What I built (in this repo)
- `scripts/bidnet_watch.py` — watches 6 Colorado agencies on BidNet, keyword-filters (HVAC, mechanical,
  chiller, boiler, landscaping, grounds, on-call, facilities...), diffs against last run, downloads documents
  when logged in. Extractor validated on a fixture page; **not yet validated against the live site** because
  bidnetdirect.com is blocked from the cloud environment. It saves raw HTML on a parse miss so selectors can
  be fixed from a real sample in one pass.
- `scripts/samgov_watch.py` — HVAC/chiller/boiler/mechanical + NAICS 238220/561210/561730 in Colorado,
  diffs by notice ID.
- `scripts/scan_bids.py` — runs both, writes `bids/_watch/REPORT.md` with a one-line headline.
- Session hook installs Playwright so a cloud session can run the scraper.

## What Luke must do (none of this can be done from inside a session)
1. **Network access** for the cloud environment (session title bar → cloud environment → Edit → Network
   access → Allowed domains). Add:
   `www.bidnetdirect.com`, `bidnetdirect.com`, `www.rockymountainbidsystem.com`, `api.sam.gov`, `sam.gov`,
   `www.parkerco.gov`, `www.dcsdk12.org`, `estespark.colorado.gov`, `dms.estes.org`.
2. **Secrets** in the same environment settings (Environment variables):
   `SAM_API_KEY` (SAM.gov → Account Details → API Key), `BIDNET_USER`, `BIDNET_PASS`.
   Never paste these in chat. The scripts read them from the environment only.
3. **BidNet vendor profile** (login now luke@brownbisonco.com, done 2026-10-19): confirm the contact/notification email also shows luke@brownbisonco.com, turn on email notifications,
   follow Town of Parker, DCSD RE-1, Town of Estes Park, Douglas County, and add commodity codes for HVAC
   (NIGP 031, 910-xx mechanical maintenance) and landscaping (988). This alone makes BidNet push to us.
4. Optional: connect **GovTribe** in claude.ai connectors for federal search without an API key.
5. Tell me when 1–3 are done. I will then run `scan_bids.py` live, fix the BidNet selectors from the real
   page, and create the scanning Routine (every 4 hours for BidNet, daily for SAM.gov).

## Risk Luke should know
BidNet's terms of use restrict automated access. Polling public pages a few times a day is low-risk.
Logged-in scraping with your credentials is your call; if BidNet objects, fall back to path (1), email
notifications, which is fully within their rules and catches the same events.

## Routine plan (create after steps 1–3)
- "Bid portal scan" every 4h 06:00–20:00 MT: `python3 scripts/scan_bids.py`, commit REPORT.md + state,
  reply with the headline only if there are NEW/CHANGED items; otherwise "Portal scan: no changes."
- On a NEW keyword match: create `bids/<agency>-<slug>/` from `bids/_template/`, drop downloaded docs in
  `docs/`, build `requirements.md`, and flag it to Luke.
