# Arapahoe RFB 26-64 Courthouse 1 drywall/paint: sub outreach

Brown Bison bids and holds the contract; the sub removes wallpaper, repairs drywall and paints on after-hours shifts, passes
the County background check, and attends the MANDATORY pre-solicitation meeting Mon 2026-11-23 10:00 MST for Brown Bison.
Candidates: ops/research/2026-11-12-cpw-courthouse-subs.md.

## Log
- 2026-11-12 23:4xZ (16:4x MT, HQ): Wild Fox Painting (connect@wildfoxpainting.com) asked to attend 11/23 10:00 and price the painting scope, RFB attached, msg 1a1d21aa164e43dc; answer by Wed 11/18. Ceres (Monica Manzo) is asked Fri 11/13 08:30 MT (one email per company per day).

- 2026-11-13 15:59Z (08:59 MT), HQ: Ceres Construction (ceresconstruction@gmail.com) attend-and-price ask with RFB-26-64.pdf, msg 1a1d5a23ad50d6b9 (Wild Fox asked 11/12). Humanize gate PASS; sent via scripts/send_outbox.py (ops/outbox/2026-11-13/outbox-friday-batch.json).
- 2026-11-17 17:40Z (10:40 MT, HQ, gate PASS, send_outbox.py, skip-list 0): FIRST TOUCH to 6 south-metro painting/drywall firms with emails verified on their own sites (bcc, RFB-26-64.pdf attached, msg 1a1ea98c6af9ae73): Tri-Plex Painting (Littleton), LS Painting Inc (Littleton), A-Pro-Finish Drywall (Westminster; TI/occupied-building niche), The Colorado Painting Company (Wheat Ridge), That 1 Painter Denver-Aurora, Core3 Drywall (Castle Rock; drywall only). Ask (Luke 11/17 rule 7: attendee in the FIRST email): one person attends Mon 11/23 10:00 and signs in for Brown Bison, price by Fri 12/04, yes/no with the attendee's name by Thu 11/19. Held back: J&S Drywall Specialties (only a preview-site address), Littleton Paint Pros (weak fit). Rejected: One of a Kind Painting (courthouse work but phone only), Lovern's (no email, Colorado Springs), LIME, Colorado Facility Services, Denver Commercial Painters, CertaPro, Fresh Coat, others (form/phone only or no site). Gate: named attendee confirmed by Thu 11/19 (2 business days before the walk) or NO-BID on walk grounds.
- 2026-11-18 19:12Z (worker, read-only): **BOUNCE (temporary delay)** on the 11/17 first touch (thread 1a1ea98c6af9ae73): mailer-daemon msg 1a1f0139cf486fef, "There was a temporary problem delivering your message to" Core 3 Drywall's info@ mailbox; Gmail retries for 46 more hours. Treat Core 3 as unreached for the Thu attendee gate; the other 5 firms show no bounce. No replies yet from any of the 6.
- 2026-11-19 23:37Z (worker, read-only): second Gmail "Delivery Status Notification (Delay)" for the Core 3 Drywall mailbox (msg 1a1f62bc16345596): "Gmail will retry for 18 more hours." Final result due ~2026-11-20 17:37Z; treat Core 3 as unreached for the Fri 12:00 attendee ask.

- 2026-11-20 20:44-20:45Z (Mac send run, ~13:45 MT): second touch to Tri-Plex, LS Painting, A Pro Finish Drywall, The Colorado Painting Co, That 1 Painter (Denver/Aurora) + first touch to Paint EZ South Denver (threads 1a1fab3a3870773f .. 1a1fab5177ae2323). Attendee for the MANDATORY Mon 11/23 10:00 meeting asked by today 17:00 MT; NO-BID at 17:00 if none.

- 2026-11-20 21:51Z (14:51 MT): **Tri-Plex Painting DECLINED** (msg 1a1faf1b4ee05aed, thread 1a1fab3a3870773f): "No, sorry."
- 2026-11-20 22:18Z: **Core 3 Drywall FINAL BOUNCE** (msg 1a1fb0a856adc236): info@core3drywall.com "Message not delivered" (DNS error, domain's Outlook MX does not resolve; Status 4.4.3 failed). Address dead.
- Status 22:21Z: 0 attendees. Still open (no answer yet): LS Painting, A Pro Finish Drywall, The Colorado Painting Co, That 1 Painter, Paint EZ South Denver. NO-BID at 17:00 MT today if none names an attendee for the MANDATORY Mon 11/23 10:00 meeting.
