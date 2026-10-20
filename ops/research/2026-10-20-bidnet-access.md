# BidNet Direct / RMEPS: official access paths (research agent, 2026-10-20)

- **Tiers:** Basic $0 = RMEPS member-agency bids (Colorado's ~400) + real-time email alerts; Local (1 state) $100/mo,
  Regional $200, National $330 (annual ~$599/$1,199/$1,999) add aggregated state & local bids (Colorado's ~184),
  advanced search, daily match summary; Federal add-on $399/yr. Sources: sovra.com/pricing-suppliers, Sovra FAQ/guide
  (12-2025), denvergov.org RMEPS flyer, civiciq.com.
- **Alerts:** member-agency matches are emailed in real time on FREE accounts, matched on NIGP Working Categories
  (3-digit prefixes work). Saved Searches (paid) send no email. Matching Profile: "Stay Ahead" (as it happens) or
  "Stay Efficient" (2x/day). Alerts go to the Personal Information email, not the username. Our inbox has had ZERO
  new-bid alerts since 10/19: Luke's categories/frequency/notification email need setting.
- **API/feeds:** none. Pages are server-rendered; tab fragments under /public/solicitations/<id>/abstract/
  (notice, docs-items, docs-request, history, Q&A), attachment-download, download/intercept; CSRF + AWS WAF.
- **Documents:** downloading any file makes us a document holder: auto-followed, emailed on addenda, date changes and
  Q&A answers. "Follow and receive Addendum" (documents by email) is selectable on the free account (untested).
- **Session:** no remember-me; auth cookies session-scoped; same credentials on multiple devices "can lock" the account;
  free accounts expire and need manual renewal. Code emails seem risk-based (none at the 10/20 04:24Z login).
- **Terms/risk:** /tsandcs not retrieved; read it. WAF robot check at ~3 full scans/15 min. Cadence: one browser,
  hourly, <=30 requests/5 min, jitter, stop at the first challenge, never solve or rotate. Ask support@bidnet.com in
  writing whether automated read access is allowed. Protect the account that submits bids.
- **Recommendation:** (a) new bids: email alerts are the primary feed (broad NIGP categories, Stay Ahead), parsed by the
  hourly Gmail check; backstop with one hourly "published today" search instead of 24-page walks. (b) documents: one
  logged-in fetch per watched bid when an addendum/date/Q&A email arrives; weekly audit.
