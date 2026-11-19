# BLM RFQ 140LL027Q0009, Paria River District HQ janitorial (Kanab UT): sub outreach

Opened 2026-11-18 (rule 0b: outreach starts the day the bid opens). Brown Bison is the bidder and prime. A Southern Utah
cleaning company is our sub, and we ask it for a monthly price. **Quote due Wed 2026-12-09 12:00 MST.** We plan to submit
early, the week of 2026-11-23, priced from the documents (`private/`). A sub's written price replaces ours by revised quote
before 12/09. Ask for prices by **Tue 2026-12-01**, 8 days before the deadline. No site visit is scheduled, and the
solicitation bars contact with any government staff other than the contracting office (Sol p.4 item 6), so no tour can be
offered. The crew has to live in Kanab or nearby (README; Technical Factor 1). No links in the email; files are attached.

**Email search rule:** a public business address on the firm's own website only, nothing guessed. The named mailboxes are
NOT in this tracked file. They are in the session scratchpad, `kanab/subs.json` (company, city, email, source_url). Prior-send
check 2026-11-18: none of these firms appears in any other `bids/*/sub-outreach.md`, and none is on the do-not-contact list
(Tidy Team, FACT/FCT Water).

## Firms with a public email on their own site (5)

| # | Company | City | Website | Where the email is published | Fit |
|---|---|---|---|---|---|
| 1 | Club Janitorial Services, LLC | St. George, UT (BBB also lists a Cedar City address) | clubjs.com | own home page (address shown through Cloudflare email protection; decoded 2026-11-18). Named mailbox | Commercial janitorial and office cleaning since 2014 (BBB). BBB category snippets list Kane County in its service area. Best fit on paper |
| 2 | Utah Cleaning | St. George, UT (Deseret Drive) | utcleaning.com | own contact page (role mailbox) | Family-owned since 2004; janitorial, commercial cleaning, floor maintenance; serves St. George, Hurricane, Cedar City (Kanab not named) |
| 3 | All Things Cleaning | St. George, UT | atc-utah.com | own home page (role mailbox) | Commercial, medical-facility, carpet and tile, vacation-rental cleaning; lists St. George, Hurricane, Cedar City |
| 4 | SaniClean Janitorial (866SaniClean) | St. George office (S Bluff St); site footer gives Tustin, CA | 866saniclean.com | own St. George page (role mailbox) | Recurring office janitorial; multi-state (California, Las Vegas, Washington County UT) |
| 5 | Alta Janitorial | "Local crews, St. George"; site footer gives Salt Lake City, UT | altajan.com | own St. George page and contact page (role mailbox, Cloudflare-protected, decoded) | Office, commercial and janitorial, floor care; regional firm |

Road distance to Kanab is about 80 miles from St. George or Cedar City and about 65 from Hurricane (approximate). Every firm
here would hire a Kanab-area crew. The email asks that directly.

## Found, but no public email (not emailed; no calls under the 11/06 rule)

| Company | City | Source | Note |
|---|---|---|---|
| Frosty's Cleaning Co. | Kane County (serves "Kane County, Garfield County") | its own Squarespace site; phone and social only | The only Kane-County-focused cleaner found; residential and commercial, carpet and tile. Web form or social message only |
| CleanPro | St. George (W 2710 S Circle) | cleanproutah.com | Commercial office cleaning; no business email on the site |
| Executive Cleaning Services | St. George page (national, woman-owned) | executive-clean.com | Toll-free number and web form only |
| SERVPRO of St. George / of Cedar City-Fillmore | St. George / Cedar City | servpro.com | Franchise; commercial janitorial listed; phone only |
| Quick and Clean Janitorial Service | Page, AZ | BBB listing | Janitor service; phone and PO Box only, no website |
| Frehner Cleaning Services, LLC | Hurricane, UT | Angi profile | Commercial and janitorial listed; no website found |
| Southern Utah Best Cleaning | Cedar City, UT | Care.com listing | Commercial and residential; phone only |
| Greater St. George Cleaning Services | St. George, UT | Superpages listing | Commercial; phone and PO Box only |

Not used: Cleaning Solutions & Restoration ("GP Clean Freaks"). It has a St. George landing page, but it is a Grants Pass,
Oregon carpet-cleaning firm. Jani-Serv, Inc. publishes an address, but it is based in Taylorsville (Salt Lake area), outside
the requested radius, and its site does not name Southern Utah. No janitorial firm with a website turned up in Kanab or
Fredonia.

## Draft pricing-request email (NOT sent; humanize gate PASS 2026-11-18)

To: the five mailboxes in the scratchpad `kanab/subs.json`, as one bcc group. Subject: **BLM Kanab office janitorial (RFQ
140LL027Q0009): sub pricing**. Attach (from `docs/`): the solicitation PDF (WD inside), Amendment 0001, Attachment 1 Bid
Schedule (blank original), Attachment 2 PWS, Attachment 4 Cleaning Schedule, Attachment 7 Photos. Optionally attach
Attachment 5 PRS. Never attach anything from `private/`.

    Hi Team,

    I'm Luke Adams with Brown Bison Holdings. We're quoting BLM's janitorial contract for the Paria River District office
    in Kanab (RFQ 140LL027Q0009). Brown Bison is the prime, and we want a local cleaning company as our sub.

    The building is about 13,000 square feet with 6 restrooms and a shower room. Cleaning is Monday, Wednesday and Friday
    outside business hours, and the contractor supplies paper, soap and liners. Service Contract Act wages apply.

    Can you send a monthly price for the routine cleaning, plus a price for each semi-annual and annual task on the Bid
    Schedule, by Tuesday, December 1? Please also tell me whether you can staff Kanab.

    The solicitation, amendment, PWS, Bid Schedule, cleaning calendar and photos are attached. No site visit is scheduled.

    Thanks Team,

    Luke Adams
    Operations Manager
    Brown Bison Holdings LLC
    luke@brownbisonco.com

Gate checks, 2026-11-18, both **PASS**. The only warning is "125 prose words (target under 90)", which is under the 150-word
hard cap.
- `python3 scripts/humanize_gate.py check <body ending at "Thanks Team,"> --subject "..."` (form for
  `scripts/send_outbox.py` / `gmail_api.py`, which append the signature)
- `python3 scripts/humanize_gate.py check <body + four-line signature> --signature --subject "..."` (form for the Gmail
  connector)

No phone number, no link, no call invite, no dollar figure. The four-line signature is exact. The wage determination number
and rates are in the attached solicitation, not in the email.

## What to ask a sub that says yes (by email, the same hour)

1. A monthly routine price plus a price for each Bid Schedule line 13-22, held for 60 days after 2026-12-09 and through the
   base year.
2. Confirmation that the price includes the WD wages and fringe: paid sick leave and twelve paid holidays, contractor-furnished
   paper, soap and liners, the FGS conditioner every two weeks, and the semi-annual scrubber pass.
3. Names of the Kanab lead, the janitor and the backup, or a hiring plan, plus a starting wage above the WD floor (for the
   retention plan; the figure goes in `private/` only).
4. Three small-town or rural janitorial accounts from the last 3 years, with fields a-f from Sol p.6. These go into Factor 2
   as the sub's own records.
5. Its timekeeping and photo-checklist method, and whether a credentialed regional cleaner can cover Kanab on a day's notice.
6. That it is small under NAICS 561720.

## Log
- 2026-11-18 (worker): list built; draft gate PASS; nothing sent. HQ sends today (rule 0b) and logs the Gmail message id here.
- 2026-11-18 15:36Z (HQ): first-touch pricing ask SENT, bcc 5 (St. George firms), msg 1a1ef4d6a52822be; Sol + Amd 0001 + PWS + Bid Schedule + cleaning calendar + photos attached; monthly price + periodic lines by Wed 11/25; asks whether each can staff Kanab.
- 2026-11-18 22:30Z: Utah Cleaning (St. George) DECLINED ("No thanks"). Club Janitorial, All Things Cleaning, SaniClean and Alta: no reply yet.
- 2026-11-18 22:5xZ (HQ, gate PASS): same pricing ask sent to Elevate Cleaning Systems (Colorado City AZ; Kanab chamber member serving Kanab and Hurricane; carpet/tile/restoration rather than janitorial; email from the Kanab chamber listing and its own site), msg 1a1f0d4ad99894da. Second search pass found no other Kanab/Cedar City/Page cleaner with a published email.
- 2026-11-19 01:2xZ (worker, read-only, no idle tick): 3 more regional leads from web search; **emails NOT verified** (the container's network refused their own sites, so nothing was read from them). HQ checks each site for a published mailbox before any send:
  - Jani-Serv, Inc. (janiservinc.com): says it serves Utah and Arizona; commercial janitorial, office cleaning, floor care; based in northern Utah (Salt Lake/Ogden chamber listings). Kanab coverage not stated.
  - Swept Out Cleaning Services: BBB lists it in the Kanab janitor category (A+), address in St. George. Website not confirmed.
  - Pinnacle Building Services (Flagstaff AZ, commercial janitorial since 1994, HomeAdvisor). Page AZ / Kanab coverage not stated.
  - Page AZ search found only Quick and Clean Janitorial (already listed, no email) and residential maid firms. Tidy shows up for Kanab but is on the do-not-contact list.
- 2026-11-19 01:5xZ (HQ): worker's leads checked. Jani-Serv (janiservinc.com) hides its email behind Cloudflare protection and lists only Salt Lake/Utah County and Phoenix; Pinnacle Building Services' domain is a for-sale page. No send. Swept Out (St. George) is residential with a BBB form only.
- 2026-11-19 01:4xZ (HQ check of the worker's 01:2xZ leads, per MEMORY): Jani-Serv's email is hidden behind Cloudflare and the site names no southern Utah coverage; Pinnacle Building Services' domain is for sale. Neither is usable. Swept Out is still unchecked.
