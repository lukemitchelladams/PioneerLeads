# USFS RFQ 1240LP27Q0008 Pagosa Ranger District janitorial: sub outreach

Opened 2026-11-05. Brown Bison is the bidder; a local cleaning company is our sub. Ask: price the base year (calendar 2027)
by the Schedule of Items lines (daily 260/yr, weekly 52/yr, annual 1/yr) by **Mon 2026-11-16 12:00 MT**. Quote due
2026-11-19 10:00 MT. No site visit scheduled; tour on request through the Forest Service. No links in emails; files attached
(RFQ, PWS, Schedule of Items, Wage Determination, Facility Layout).

Email search rule: public address on the firm's own site or in a search snippet only; nothing guessed. Pagosa Springs itself
has few indexed commercial cleaners; most local firms are phone-only.

## Emailed 2026-11-05 (bcc, one message, key `pagosa` in ops/outbox/2026-11-05/)

| Company | City | Email | Source | Phone | Fit |
|---|---|---|---|---|---|
| CRC Janitorial Services, Inc. | Durango (PO Box 118, 81301) | rgonzalez@crcjanitorial.com | own contact page (crcjanitorial.com) | (970) 946-7162 | Commercial cleaning, floor care, window cleaning, construction clean-up; "fully insured, bonded and licensed" per listings. Best fit. ~60 mi from Pagosa |
| B&K Cleaning Services LLC | Durango | bandkcleaningcolorado@gmail.com | own site (bandkcleaningservices.com) | 970-844-4317 | Commercial clean, carpet cleaning, floor buffing; names Pagosa Springs in its service area. Good fit |
| Evergreen Cleaning LLC | Bayfield (PO Box 76) | cleaningevergreen@gmail.com | Facebook page snippet (search result) | (970) 442-0183 | Cleaning LLC ~45 mi from Pagosa; commercial vs residential mix not stated. Fit unknown |

## Phone-only (no public email found; Luke or the hourly check calls if no replies by Mon 2026-11-09)

| Company | City | Phone | Notes |
|---|---|---|---|
| Ralph & Son Enterprises | Pagosa Springs, 109 Wilderness Dr | (970) 731-4585 | Janitorial + chimney/dryer vent; "33 years in business" per directory; BBB A-. Closest firm to the site |
| AAA All Clean Janitorial, LLC | Pagosa Springs | not found | BBB A+, categories commercial cleaning / janitor service; no phone or site indexed |
| Quality Maintenance Inc | Durango, 27055 US Hwy 160 | 970-385-7676 | "over 50 years" commercial janitorial, office, window, carpet; no email on listing |
| Leo's Janitorial Services, Inc. | Durango, 21577 Hwy 160 | (970) 426-9061 | BBB A+; no site found |
| VIP Janitorial Services, Inc | Durango, 826 Kearney St | (970) 247-9557 | Directory only |
| Alpen Property Services | Durango, PO Box 1182 | 970-852-0800 | Janitorial + facility management, office/medical experience; web form only |
| Marley's Angels Cleaning Services | Bayfield / Durango | (970) 749-4094 | Residential + commercial since 1998; web form only |
| Shine to Shine Cleaning | Durango, 484 Turner Dr Bldg E Ste 101 | 970-759-4000 | Commercial janitorial (offices, hotels, industrial); site returned 503 twice |
| SERVPRO of Durango | Durango, 170 S Skylane Dr | (970) 259-6184 | Franchise; lists Pagosa Springs, Bayfield, Cortez in service area; "regular maintenance cleaning" for businesses |
| Elevated Cleaning Company LLC | Cortez | (970) 769-9998 | Facebook only; fit unknown |

Not used: Cowgirl Cleaning (Pagosa; residential/construction, email spelling inconsistent in the only snippet); Certified
Cleaning and Restoration (Cortez; restoration, no contact found); Best Cleaning & Disaster Restoration (Durango;
carpet/restoration, no email). Pagosa chamber directory (member.pagosachamber.com) returned 403 and
business.pagosachamber.com does not resolve from this session.

## Email sent (body in ops/outbox/2026-11-05/pagosa.txt; humanize gate PASS; sender appends the Operations Manager signature)

Subject: USDA Forest Service Pagosa Ranger District janitorial (RFQ 1240LP27Q0008): sub pricing

    Hi Team,

    I'm Luke Adams with Brown Bison Holdings. We're quoting USDA Forest Service RFQ 1240LP27Q0008, janitorial for the
    Pagosa Ranger District office in Pagosa Springs. We want a local cleaning company as our sub; Brown Bison submits the
    quote and holds the contract.

    One building, 5,437 square feet: 2 offices, 28 cubicles, 4 shared rooms, 2 restrooms. Daily cleaning Monday through
    Friday after 5 PM, weekly work on weekends, one annual deep clean. Service Contract Act wages apply: janitor $18.68 per
    hour plus $5.92 health and welfare.

    Can you price the base year (calendar 2027) by Monday, November 16 at noon? Use the daily, weekly and annual lines on
    the Schedule of Items. No site visit is scheduled; we can arrange a tour if you want one.

    Quotes are due November 19. RFQ, PWS, Schedule of Items, wage determination and floor plan attached.

    Thanks Team,

## Log
- 2026-11-05: prior-send check: no entry for any of these firms in ops/outbox/*/sent.json or any bids/*/sub-outreach.md
  (only Durango-area trades firms for La Plata County 26-053-1215; none are cleaners). Sent to the 3 firms above via
  scripts/send_outbox.py: Gmail message id 1a1ade55a73ca213, bcc 3, 5 attachments, humanize gate PASS (132 prose words,
  under the 150 cap). Replies land in luke@brownbisonco.com; hourly check watches for them.
