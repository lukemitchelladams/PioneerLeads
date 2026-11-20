# Thornton RFP 335-26 Speed Cushions On-Call: sub outreach (asphalt speed cushion installer)

Opened 2026-11-20 (CEO GO-IF 11/20 08:45 MT; HQ gate check = GO, no hard gate). **Drafted, nothing sent.** Two lines go
together (rule 0b: outreach starts the day the bid goes GO); line 3 is the backup if both are silent by Mon 11/30. No walk to
attend (none in the RFP). Brown Bison is the bidder and holds the General Service Agreement; the asphalt sub prices for us,
is listed on Exhibit B (Thornton's written consent, RFP IV.I.3) and does the work.

Ask: unit prices each for the three cushion types (material-only and all-other-costs lines, as Exhibit C splits them), removal
each per type, crew hourly rates regular/overtime for T&M, three public speed-cushion or street-asphalt jobs with a contact
each (RFP V.B.6 references), and a COI. Pricing by **Wed 2026-12-09** (9 days before the Fri 12/18 17:00 due date). Attach
docs/335-26-rfp.pdf (1.4 MB) to every email; no links.

Mailboxes are kept out of this public repo, in the operator's private sub list
(/tmp/claude-0/-home-user-PioneerLeads/9eba1390-a8c1-5755-a9f9-e6b40e48b070/scratchpad/thornton335-subs.json, not committed).
Each one is printed on the firm's own website (page named below).

| Line | Firm | City | Where the email is printed | Fit | Status |
|---|---|---|---|---|---|
| 1 | Colorado Asphalt Services, Inc. (CASI) | Commerce City, CO | its own site, home page ("Get an Estimate" button; "Get in Touch" block) | Asphalt paving incl. "Municipal Projects", milling, patching, striping; sells asphalt. Third-party listings name speed bumps, and a City of Westminster ROW permit "Install speed bumps" (BuildZoom) | not sent |
| 2 | Asphalt Specialties Co. | Front Range (9 locations, own plants) | its own site, home page ("Contact Us Today for a Free Quote") | "30 years in asphalt paving, patching, and milling"; municipal work; own plants for the City's MGPEC Form 9 mix | not sent |
| 3 (backup) | Colorado Paving and Concrete | Northglenn, CO | its own site, home page ("EMAIL US") | Paving and asphalt, roadway infrastructure, owns a milling machine; also on the Hyland Hills concrete list (separate email per bid) | send Mon 11/30 only if 1 and 2 are silent |

Checked, no email printed on their own site (2026-11-20): M5 Paving (Northglenn; address only in page metadata, contact is a
form), Foothills Paving & Maintenance, Colorado Pavement Solutions, Brannan Sand and Gravel, Black Top Construction. Use a web
form if a fourth line is needed; nobody phones them (CLAUDE.md call rule).

## Email (one firm at a time). Subject: Thornton speed cushion pricing, RFP 335-26

Body file for scripts/gmail_api.py: `bids/thornton-speed-cushions-335-26/sub-outreach-body.txt` (starts "Hi Team,", ends at
"Thanks Team,"; the sender adds the four-line signature). `python3 scripts/humanize_gate.py check sub-outreach-body.txt
--subject "Thornton speed cushion pricing, RFP 335-26"` = **PASS** (2026-11-20, no warnings). No phone, no links, no call invite.

```
Hi Team,

Brown Bison is bidding the City of Thornton's on-call speed cushion contract (RFP 335-26, due Fri 12/18) and needs an asphalt sub. RFP attached.

Work comes as task orders on City streets: install or remove hot-mix asphalt speed cushions, 3.25 inches tall, City mix design. Emergencies need a crew on site within 48 hours.

Sizes: Type 1 78 x 78, Type 2 120 x 78, Type 3 144 x 84 inches

Install: unit price each per type, with material and labor as two lines

Removal: unit price each per type

Labor: crew hourly rates, regular and overtime, for time and materials work

Experience: three public speed cushion or street asphalt jobs, with a contact for each

Can you send those and a COI by Wed 12/09?

Thanks Team,
```

Type 3 is written as Exhibit C prints it (144 x 84); the Exhibit 1 detail draws it 78 wide (vendor-questions.md Q4). If the City
answers before the subs reply, send the corrected size in the same thread.

## Log
- 2026-11-20 (HQ worker): 2 lines + 1 backup found (own-site emails), 5 form-only or no-email firms noted; body gate PASS;
  nothing sent. Sends belong to the Mac queue (HQ cloud Gmail writes hang on approval, COORDINATION 11/19 12:45).

- 2026-11-20 20:52Z (Mac send run): first touch to Colorado Asphalt Services (info@coloradoasphalt.com, 1a1fabbcf1c5c372) and Asphalt Specialties Co. (bid@asphaltspecialties.com, 1a1fabbf5eb984e8). **BOUNCE 20:53Z (1a1fabc051dda2e3): Asphalt Specialties "Message blocked"** by the receiving server. Live: Colorado Asphalt only; next: backup Colorado Paving and Concrete (note: its Enrique@ address also bounced today on Hyland Hills) or another mailbox from Asphalt Specialties' site.
