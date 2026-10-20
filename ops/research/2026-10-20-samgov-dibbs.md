# SAM.gov + DLA DIBBS: efficient, rule-abiding federal data (research agent, 2026-10-20)

**DIBBS rule (verified verbatim, DIBBS FAQ #45):** "VPNs, proxy servers, TOR nodes, cloud hosting services, and other
similar services or devices, mask the user's IP address and are, therefore, prohibited." -> the cloud scanner no longer
reads DIBBS (run.py gate, BIDWATCH_ALLOW_DIBBS=1 only on Luke's own computer).

## SAM.gov
- API key limits: personal key without an entity role 10/day; with a role on an entity 1,000/day; non-federal system
  account 1,000. Luke as Brown Bison registrant likely already has a role. Keys rotate every 90 days (replacement shows
  15 days early; remind at day 75). Key at sam.gov/workspace/profile/account-details.
- Opportunities API v2: postedFrom/postedTo required, limit 1000. state=CO and ccode filters leak (place-of-performance
  state blank on 71-86% of solicitations; DLA notices carry 2-digit PSC groups). Best: same-day sweep
  (postedFrom=postedTo=today, ~1,350 notices = 2 calls) and filter locally.
- **Bulk CSV, no key, verified:** https://sam.gov/api/prod/fileextractservices/v1/api/download/Contract%20Opportunities/datagov/ContractOpportunitiesFullCSV.csv?privacy=Public
  (303 to S3; ~205 MB; ~71,000 active notices; rebuilt nightly ~03:30 UTC). Has NAICS, PSC, place of performance,
  office state, description; no attachments. Replaces the API for discovery.
- Saved searches (Actions > Save, Actions > Notify): daily email with links, no attachments.

## DIBBS (from Luke's own IP only)
- No API. Daily files at https://dibbs2.bsm.dla.mil/Downloads/RFQ/Archive/: in{YYMMDD}.txt (140-char fixed-width index;
  ~1,700 lines/day, ~31/day in our FSCs), bq{YYMMDD}.zip (batch quote + approved-source CAGEs), ca{YYMMDD}.zip (all PDFs,
  ~418 MB, skip). RFQ PDF: https://dibbs2.bsm.dla.mil/Downloads/RFQ/<last char of solicitation>/<SOL>.PDF.
- SAM mirrors only ~22% of DIBBS solicitations (9 of 31 in our FSCs on 2026-10-19).
- Vendor Directed Solicitation Notification by FSC (needs DIBBS registration + CAGE).

## Design
Daily 06:00 MT: (a) SAM CSV, one GET, diff NoticeId/deadline, keep CO + NAICS/keywords (Brown Bison) and PSC groups
30/31/39/46 + keywords (Jones Bearing); (b) DIBBS in-file of the prior business day from Luke's machine, keep our FSCs,
fetch those PDFs (~35 requests/day); (c) SAM API (role-tier key) <15 calls/day for same-day sweeps and shortlisted
notice lookups. Backups: SAM saved searches; DIBBS FSC notifications.
Sources: open.gsa.gov (entity + opportunities API docs), DoD System Account User Guide, gsascheduleservices.com,
dibbs.bsm.dla.mil RfqFileDefs + RFQDates + FAQ.
