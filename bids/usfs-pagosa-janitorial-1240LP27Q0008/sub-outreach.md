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

## Phone-only (no public email found; nobody phones them: Luke's 2026-11-06 call-brief rule. If no sub replies by Mon 2026-11-09, use web forms where a firm has one; if only a call will do, email Luke a CALL BRIEF and whether to call is his choice)

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
- 2026-11-06 02:57Z (Gmail date): **B&K Cleaning Services LLC** (bandkcleaningcolorado@gmail.com) replied on the thread (msg 1a1ae4ecc8bc88f0): interested in quoting the Pagosa Ranger District office; will review the attached documents and send pricing. No price yet. Asked-by date for pricing is Mon 2026-11-16 12:00.

- 2026-11-06 02:57Z: B&K Cleaning Services (Brandon Sorrells Sr, CEO, Durango, office 970-844-4317) REPLIED: interested; base-year pricing by Mon 11/16; wants a walkthrough, available 11/09 or 11/13.
- 2026-11-06 ~03:00Z (HQ): tour requested from the District (brandon.caley@usda.gov, msg 1a1ae7fe9e5da862) for 11/09 or 11/13, two attendees (Luke + B&K); B&K told (msg 1a1ae7feda06d803). CRC Janitorial and Evergreen Cleaning: no reply yet.
- 2026-11-09 15:13Z: **District confirmed the tour for TODAY Mon 11/09 3:00 PM MT** (Brandon Caley, msg 1a1c0dec5b91105c; our 11/05 email had gone to his spam folder). Check in at the front desk; Doug lets him know. Not mandatory. Worker flagged it to HQ 15:3xZ (Luke is tied up with Brighton 14:00; B&K in Durango said 11/09 works). HQ to confirm attendee with Caley and tell B&K, or ask for Fri 11/13.
- 2026-11-09 15:30Z (08:30 MT, HQ): Caley (USFS) confirmed the tour TODAY 15:00 MT at 180 Pagosa St (msg 1a1c0dec5b91105c). HQ decision (Luke held by Brighton 14:00): B&K walks it for Brown Bison. Replied to Caley (1a1c0ec083ed4ef6) and asked B&K to attend, photos + notes, answer by 11:00 MT or we ask for Fri 11/13 (1a1c0ec0cea85a94).
- 2026-11-09 19:43Z (12:43 MT, HQ): B&K never confirmed today's 15:00 tour (asked by 11:00 MT). Asked Caley to move it to Fri 11/13 15:00 or his time (1a1c1d51e85c9b40) and told B&K to hold for Friday (1a1c1d5234a66771).
- 2026-11-09 20:15Z: Brandon Caley (msg 1a1c1f35726c93e2) agrees to move the tour to **Fri 11/13, available 1:00 PM MT** (HQ had asked 3:00 PM), for Brandon Sorrells or any representative. He warns that flood damage to the **Piedra River Bridge has cut US 160 between Pagosa Springs and Durango**; the detour runs through New Mexico and adds ~3.5 h. B&K is in Durango: confirm B&K can still make it (or price from our photos/notes), then confirm time + attendee to Caley by Thu 11/12.
- 2026-11-09 20:45Z (13:45 MT, HQ): Caley confirmed Fri 11/13 13:00 (msg 1a1c1f35726c93e2) and warned that flood damage closed the Piedra River Bridge on US 160 between Pagosa and Durango (detour via New Mexico, ~3.5 h added). HQ confirmed Friday 13:00 with Caley (1a1c20c5f289fee1) and asked B&K (Durango) whether he can still attend and how the closure affects staffing, answer by Wed (1a1c20c62c9e278d). Risk: a Durango sub may not work while US 160 is closed; Pagosa-local cleaners in the list are phone-only.
- 2026-11-11 (Gmail date header 2026-11-12 01:36Z; the sender's clock runs ahead, arrived after 22:53Z): **B&K Cleaning DECLINED** (msg 1a1cceae4d9b994f), replying to HQ's 15:42Z tour chase: "At this time we are not interested. Thank you". No sub left: CRC Janitorial and Evergreen Cleaning never answered the 11/05 request. Worker running a sweep for Pagosa-local / east-of-the-Piedra-bridge commercial cleaners with published emails (results below). HQ decides: send a new pricing request (Mon 11/16 12:00) or NO-BID; tell Caley by Thu 12:00 whether anyone attends Fri 13:00.

## Replacement sweep 2026-11-11 23:3xZ (worker; B&K declined, CRC + Evergreen silent)

Four search angles: Pagosa local, east of Wolf Creek Pass (SLV), northern NM via US 84, and federal/regional firms. 14 hits, 13 distinct
firms. **None could be checked on the live page.** facebook.com, yelp.com, bbb.org, the Pagosa chamber, pagosasun.com, callmw.com, usaspending
and GovTribe (account cancelled) are all blocked or unavailable from the cloud, so every address below comes from a search-index snippet of the
firm's own site or page. That is the same standard as the 11/05 list ("own site or search snippet only, nothing guessed"). Expect some
bounces; log any mailer-daemon here. None of these firms is in ops/outbox sent.json. Not one is a proven SCA/federal performer. A Pagosa-local
or Pagosa-listed firm is the real fit for nightly Mon-Fri after-5 PM service.

**A: send first (commercial fit, no Piedra bridge on the way)**

| Company | Base | Email | Snippet source | Fit / route |
|---|---|---|---|---|
| Mountain West Cleaning Services ("Mountain West Commercial Services", Pagosa Chamber member) | South Fork; Pagosa chamber address 105 Hot Springs Blvd | contact@callmw.com | callmw.com/contact-us/ (index ~2 yrs old) | Strongest: office, school and commercial cleaning. About 1 h over Wolf Creek Pass, or in town if the Pagosa address is live. Site carries leftover template text (a ccc365.net address on its Terms page): use contact@callmw.com. Posted hours are Mon-Sat 8-5, so ask whether they can staff after 5 PM. |
| 4 Ever Cleaning LLC (women-owned) | Del Norte | info@4evercleaners.com | 4evercleaners.com | Offices, retail, business facilities. About 1 h 10 min over Wolf Creek Pass. |
| Performance Maintenance, Inc. (PMI Janitorial / PMI Green Solutions) | Española NM | order@pmigogreen.com | PMI Facebook page | Full commercial janitorial contractor since 1994, about 80-100 staff. About 2.5 h via US 84, so it would have to staff locally. "order@" may be its supplies inbox. |
| Clean Rite Janitorial Services LLC | Farmington NM | info@cleanritenm.com | cleanritenm.com/contact/ | Commercial janitorial, 20+ years. About 3 h bridge-free via US 64 / Dulce / US 84, so it would have to staff locally. |

**B: worth including**

| Company | Base | Email | Snippet source | Fit / route |
|---|---|---|---|---|
| Pagosa Cleaning Co (Pagosa Moving and Labor LLC) | Pagosa Springs | pagosacleaningco@gmail.com | its Facebook page | LOCAL. Move-out, deep-clean and vacation-home work. Office work not stated, so ask. |
| Tidy Team LLC | Alamosa | tidyteamcollc@gmail.com | its Facebook page | Lists commercial cleaning and janitorial, but its core is pressure washing. About 1 h 45 min. |
| RE Cleaning Services LLC | Alamosa | personal-name gmail on recleaningservice.com (not written to this public repo; HQ has it by session message) | recleaningservice.com | "Commercial cleaning services in Alamosa". Small firm. About 1 h 45 min. |

**C: low (residential, far, or bounce risk):**
- Cowgirl Cleaning (Pagosa): personal hotmail address, spelled two ways on its own page, so high bounce risk.
- Pure Shine Cleaning (Pagosa): personal gmail; services unstated.
- All the Way Cleaning (Farmington): personal gmail; claims commercial work; about 3 h.
- Mean Clean Solutions (Costilla NM; meancleansolutions.llc@gmail.com): about 3 h.
- Epic Cleans LLC (Aztec; epiccleans4you@gmail.com): residential.

**Specialty:** Mark's Carpet Cleaning (South Fork; markcleans308@gmail.com) says it serves Pagosa. It covers the carpet part of the annual
clean only.

Phone-only, no published email (no calls, per the 11/06 rule):
- Pagosa: Ralph & Son, AAA All Clean, Native Cleaning & Property Maintenance, Premium Peak, Choice Cleaning, Summit Cleaning, Cleaning
  Obsession, Peachy Clean, Redtail Property Care, Tony's Home and Commercial, Simple Life, Frontier Cleaning, Jay's Cleaning.
- San Luis Valley: Clean As A Whistle (Alamosa), Cleaning Solutions SLV (Alamosa), Better Cleaning Services (Alamosa), White Glove
  Janitorial (Monte Vista).
- Española: NAM Janitorial, Alpine Cleaning Solutions.

No janitorial firm turned up in Chama, Tierra Amarilla or Dulce.

Next (HQ): send the 11/05 body (ops/outbox/2026-11-05/pagosa.txt) to the A and B rows. Ask for base-year pricing by **Mon 11/16 12:00 MT** and
say the Fri 11/13 13:00 tour at 180 Pagosa St is open to them. Note the closed US 160 Piedra bridge and the after-5 PM daily hours. Run it
through the humanize gate. If nobody has said yes by Fri 17:00, take the NO-BID default (RFQ due Thu 11/19 10:00).
