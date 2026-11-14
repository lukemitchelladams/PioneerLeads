# Mon 2026-11-16 08:30 MT chase batch (worker draft, nothing sent)

Four bids have a Mon 11/16 12:00 MT sub gate and no yes yet. Bodies below pass `python3 scripts/humanize_gate.py check` (body ends at the
closer; gmail_api.py adds the signature). HQ builds the manifest from its own sent records (named mailboxes stay out of tracked files),
skips any firm that has replied or declined by then, and respects each firm's touch count. Reply in the original thread where one exists.

| Body | Bid | Original sends to chase (thread / msg ids) | Skip |
|---|---|---|---|
| chase-cpw.txt | CPW DQ1-PMAA-2027000176 (Alamosa heater) | electrical bcc 1a1d66c90745e1e0 (delivered: Vemco, Power Pro, C-Squared, Billings); B tier 1a1d699c3400df4e; Torres 1a1d66c96ac41789; Surefire 1a1d5a2835ac51db; Flow Right 1a1d5a289f443c61 | Husmann (declined); Valley Electric, Royal (dead addresses) |
| chase-bgndrf.txt | Reclamation RFQ 140RR027Q0001 (Alamogordo custodial) | 1a1d6d8ae5a21e18 (delivered: SL Cleaning, Pristine, Chase N Dirt, L&L, Alamo); B tier 1a1d708c7a8ea2ad; Tigua retry 1a1d708ce49026c8 | K Clean (dead domain) |
| chase-pagosa.txt | USFS RFQ 1240LP27Q0008 (Pagosa janitorial) | 1a1ccfdb5b42ad67 (sweep group); 1a1ccfdadfba4085 (CRC, Evergreen) | B&K (declined); Tidy Team (DO NOT CONTACT) |
| chase-bvcc.txt | CDOC DQ27-0132 (BVCC boiler chemicals) | tier 3 1a1d5a24d06ac325 (RK Water, Chem-Aqua, ISI); Hydrite + WEI 1a1d17a67fa91fb1 | TRS, Aqua-Chem (touch limit); H2GS, Summit, Reaction Eng. (declined) |

Facts used, all from the bid files: CPW pre-bid "Nov 18, 2026 10:00 AM MST", registration "Nov 17, 2026 5:00 PM MST" (DQ); BGNDRF monthly
price asked by 2026-11-25 in the 11/13 ask; Pagosa quotes due "11/19/2026 1000 MT" (SF-1449 block 8); BVCC "10:00am, Wednesday, November 18,
2026" mandatory, Exhibit G + photo ID per attendee (DQ sec. 4; README says by Mon 11/16).
