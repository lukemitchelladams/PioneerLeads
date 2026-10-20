# BidNet endurance test (COMPLETE)

Started 2026-10-20T04:57:52+00:00; 12 of 12 checks run; **12/12 passed**. Each check = fresh browser from the saved session file, verify/restore login, poll page 1 of both statewide lists, open Littleton 21-26's Documents tab.

| # | At (UTC) | Forced expiry | Logged in | How | List rows | Docs | New bids | Seconds | Result |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 04:57:52 |  | yes | session reused | 50 | 4 | 0 | 13.5 | PASS |
| 2 | 05:03:52 |  | yes | session reused | 50 | 4 | 0 | 13.8 | PASS |
| 3 | 05:09:52 |  | yes | session reused | 50 | 4 | 0 | 13.0 | PASS |
| 4 | 05:15:52 | app (3 cookies) | yes | logged in (attempt 2) | 50 | 4 | 0 | 33.1 | PASS |
| 5 | 05:21:52 |  | yes | session reused | 50 | 4 | 0 | 13.0 | PASS |
| 6 | 05:27:52 |  | yes | session reused | 50 | 4 | 0 | 13.6 | PASS |
| 7 | 05:33:52 |  | yes | session reused | 50 | 4 | 0 | 13.6 | PASS |
| 8 | 05:39:52 | sso (6 cookies) | yes | logged in (attempt 2) | 50 | 4 | 0 | 32.7 | PASS |
| 9 | 05:45:52 |  | yes | session reused | 50 | 4 | 0 | 13.9 | PASS |
| 10 | 05:51:52 |  | yes | session reused | 50 | 4 | 0 | 14.0 | PASS |
| 11 | 05:57:52 |  | yes | session reused | 50 | 4 | 0 | 13.5 | PASS |
| 12 | 06:03:52 |  | yes | session reused | 50 | 4 | 0 | 14.8 | PASS |

## Notes (MAIN, 2026-10-20 07:02 UTC)

- Finished 06:04 UTC: 66 minutes, a new browser from the saved session file on every check, 12 of 12 passed.
- Check 4 deleted the site session cookies. Check 8 deleted every BidNet session cookie, including the
  single-sign-on session. Both recovered with no human input and no confirmation code.
- Checks 4 and 8 logged in on the second attempt. The first attempt read the page while BidNet was still
  redirecting through its sign-on server; the saved page shows it was already logged in. Fixed in commit
  fe4cbfc: the login now waits for the redirect chain to settle. A test reproduces the race; the old code
  fails it on all 3 attempts, the new code passes on the first.
- New bids on page 1 of the two statewide lists during the hour: 0.
