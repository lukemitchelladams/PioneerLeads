# Sub outreach: VA RFQ 36C25927Q0048 radiant heating panel replacement (RMR VAMC, Aurora CO)

Brown Bison is the bidder and prime; a Denver-area plumbing/hydronic contractor performs as our sub and gives us its price.
Named mailboxes and their source pages are kept in the HQ scratchpad (`va-subs.json`), not in this public file.

Rule 0: the only walk is the **optional** VA site visit **today, Fri 2026-11-20 11:00 AM** (Amd 0001). A sub attendee is asked
for only in the pre-09:30 MT body; nobody attends under Luke's name.

## Firms (public email printed on the firm's own website, checked 2026-11-20)

| Line | Company | City | Fit (from its own site) | Open questions |
|---|---|---|---|---|
| 1 | Simply Mechanical AC Furnace & Boiler | Littleton | Commercial heating page: commercial boiler repair, boiler installation, steam boilers; its system quiz lists "Boiler: Radiators or in-floor heat". Earlier repo record (St. Vrain boiler folder): replaced a hydronic boiler in a 32-unit Lakewood building | Panel radiator installs with start-up/commissioning? Small under NAICS 238220? |
| 2 | Kerwin Plumbing & Heating | Broomfield | Commercial Services menu (commercial boilers, pumps, tanks), Commercial Construction page: "We work with architects, engineers, and contractors to design and install top-quality plumbing systems." | Hydronic panel experience not stated on the site; ask |
| 3 | Cardom Plumbing & Heating | Arvada | "We provide dependable commercial plumbing services for offices, restaurants, healthcare facilities, and more." "We offer professional boiler repair, maintenance, and installation." | Hydronic panel experience not stated; ask |

Checked, no public email on an own site (not used): Advanced Boilers & Hydronic Heating (Denver; site prints a phone only),
Square A Mechanical Systems (Aurora; hot water, steam and radiant; no own website found), Custom Heating, Plumbing & Air
Conditioning Services (Aurora; contact form only), Freund Plumbing & Heating (Aurora; its domain redirects to an unrelated
site), Colorado Boiler Inc. (Broomfield; no email, boiler rooms), Advanced Hydronics Inc. and Ball Mechanical (Denver; no own
website found). Tolin Mechanical declined the DEN job on 11/18 and is large: not used.

## Ask
- A lump-sum price by **Mon 2026-11-23 17:00 MT** (2-day turnaround, said plainly in the email), 2-3 similar jobs as
  references (Volume III and the PWS sec. 5 experience line), and whether the firm is small under NAICS 238220 (keeps us
  compliant on limitations on subcontracting if 13 CFR 125.6 is ever applied).
- All three lines go out in the same send, one email per firm (no shared cc).
- Attach: `36C25927Q0048 - Description.docx`, `36C25927Q0048 0001.docx`, `WD - 2015-5419 Adams-Arapahoe-Denver.pdf` and the six
  `docs/photos/*.png` (2.9 MB in all). Do **not** attach the VAAR form (dropped by Amd 0001) or any `.txt` file (the gate
  refuses text attachments). No links.

## Email body (not sent)
Subject: Radiant heating panel replacement pricing, VA RFQ 36C25927Q0048

- `sub-firsttouch-gmailapi.txt`: use **only if sent before 09:30 MT Fri 11/20** (asks for a site-visit attendee).
  `python3 scripts/humanize_gate.py check ... --subject "..."` **PASS** (with the advisory 90-word warning; 127 words, cap 150).
- `sub-firsttouch-after-walk-gmailapi.txt`: same body without the visit paragraph, for any later send. **PASS** (95 words).
- Both end at "Thanks Team,"; `scripts/gmail_api.py` appends the four-line signature.

```
Hi Team,

I'm Luke Adams with Brown Bison Holdings. We're quoting a VA job at the Rocky Mountain Regional VA Medical Center in Aurora, RFQ 36C25927Q0048. Brown Bison is the prime, and we want a Denver-area hydronic contractor as our sub.

Scope: replace about 238 feet of failed hydronic panel radiators at 5 entrance areas, same length and connections

Panels: VA lists Model PRF, 74 PSIG, 1/2 inch NPT supply and return, 1/8 inch NPT air vents, brackets included

Testing: drain down, refill, pressure test, leak check and full operation restored

Hours: weekdays 7:30 AM to 4:00 PM, shutdowns booked with VA 2 weeks ahead

Wages: Service Contract Act, wage determination 2015-5419

Experience: VA wants proof of past panel installs with start-up and commissioning

Can you send a lump sum price by Monday, November 23 at 5:00 PM MT? That is a 2-day turnaround, because the VA quote is due Thursday, November 26.

Please include 2 or 3 similar jobs for references, and tell me if you are a small business under NAICS 238220.

VA holds an optional site visit today, Friday, November 20 at 11:00 AM. If someone from your team can attend for Brown Bison, reply with their name by 9:30 AM so I can register them.

The solicitation, amendment, panel photos and wage determination are attached.

Thanks Team,
```

## If a sub names an attendee before 10:00 MT
Send `co-site-visit-rsvp.txt` to the CO from Luke's business mailbox with ATTENDEE_NAME and SUB_COMPANY filled in (gate **PASS**
as written; re-run after filling). Subject: "Site visit attendee, RFQ 36C25927Q0048". The attendee signs in for Brown Bison and
sends photos of every run, the panel nameplate/label, bracket type and connection details.

## Log
- 2026-11-20 ~15:0xZ (HQ agent, read-only): folder opened, 4/4 documents in hand, 3 firms found, bodies drafted and gated.
  Nothing sent.

- 2026-11-20 20:45Z (Mac send run, after-walk first touch, docs + photos + WD attached): Simply Mechanical (1a1fab544e908955), Kerwin Plumbing & Heating (1a1fab570bec99a1), Cardom Plumbing & Heating (1a1fab5a2737cccc); lump sum asked by Mon 11/23 17:00 MT. **20:56Z Cardom DECLINED (msg 1a1fabedfd49575b): "At this time we are too busy to take on this job."** Live: Simply Mechanical, Kerwin. Quote still goes from documents if neither prices.
