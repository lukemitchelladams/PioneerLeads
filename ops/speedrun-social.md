# SpeedRun Social scorecard

Entity: Brown Bison LLC, Broomfield, Colorado. Product: AI social media on autopilot for small businesses, the Blaze.ai replacement.
Repo: `lukemitchelladams/autosocial-ai`. Live: https://www.speedrunsocial.com. Updated 2026-10-19, 07:00 MDT.

## Where it stands

| Signal | Value | Source |
| --- | --- | --- |
| Site | ok, db ok, billing live | `/api/health`, 2026-10-19 07:00 MDT |
| Scoreboard, Oct 18 | Signups 0 in 24h, 6 in 7 days, 45 in 30 days (sources: direct 3, ChatGPT 1, Google Ads 1, other search 1). 15 accounts connected. 2 posts published in 7 days. 6 active workspaces. 0 paying, $0 MRR, 0 packs. Break-even 0% of the $400 a month the loop counts as cost. First-party visit counter live since #163. | docs/ops/autonomy/scoreboard.md, commit 70c56169 |
| Deploy #169, Oct 19 06:10 MDT | Approving a post now adds every connected platform its format allows (22 review posts across 5 workspaces had sat on Facebook alone while Instagram was connected; ayurvedashri the live case). E8 closed as a no-op by design. The overnight loop ran this on the Mac after the Blaze session went idle. | commits d2b47e95, cb17c651 |
| Billing | **live** since Oct 1; annual prices not yet purchasable, copy now gated | `/api/health`; commit e8c7ebcb |
| Paying customers | 0 | Sept 18 audit; no later data |
| Funnel, 28 days to Oct 15 | 41 workspaces, 29 got posts, 12 empty (5 of those typed an unreadable site and left). Seven active free workspaces cross the 30-day light-use line between Oct 20 and Oct 27: the first paid customer comes from this group or not at all this month. The referral badge on free posts produced 0 signups from 43 posts. | commits ebfc9035, bf20f1ed, da7d2692 |
| Upgrade clicks | 0 ever | same |
| Search | 18 clicks, 11K impressions, CTR 0.2%, avg position 48.9 (28 days to Sept 15) | docs/research/2026-09-18-gsc-28d.md |
| Fixed cost | $46 a month core (Vercel 20, Supabase 25, KMS 1); Google Ads was $20 a day on top | docs/sales/2026-09-03-first-customers/burn-and-breakeven.md |
| Break-even | 2 Starter customers at $49.99 cover the core bill | same |
| Production branch | `overnight-overhaul-20260630` at cb17c651; `main` stale since June 3 | PR #1, open since Sept 9, still open Oct 19 |
| Deploys, Oct 18 evening | #163 to #168 landed between 19:14 and 20:18 MDT, all through the Mac gate (19,183 then 19,186 tests, 0 failures). #166 customer showcase: "Posts our customers published", 4 posts on the home page and 9 on /examples from 5 businesses, each labelled and linked, with an opt-out line. #167: 40 dead "View post" links (23 Instagram, 15 TikTok, 2 Facebook) now point at the real post, and the "your post is live" email no longer goes out without a link. #168: resuming a saved onboarding step threw React error #418 on 3 of 3 loads, now 0 of 3. Earlier in the batch: redirect fix, TikTok and YouTube in E7, engagement numbers from Zernio, visit counter, review-import and audit-log fixes, indexes, cron stagger, two live migrations. Session idle since 21:41 MDT. | Blaze session transcript, Oct 18 |
| Incident, found Oct 18 | On Sept 21 two Sealis posts were published to Crypto Deposit Tracker's Facebook page by the shared-connection bug fixed Sept 25; both still live there. No other page affected. Sealis's connection was cut that night; 9 approved Sealis posts wait on a reconnect. Luke typed "Send" at 21:37 MDT and two apology notes went out at 21:40 through the owner-note tool (replies land in Luke's Gmail). Crypto Deposit Tracker has to delete the two posts itself; no session deletes on a customer's page. | same |
| Deploys | #154 deployed Oct 15: onboarding routes a bare business name straight to the describe form; the soft trial prompt now says what ending means; the free-plan badge scales to read on a phone and avoids the headline. #155 (phone layout of the Approvals page, lazy video posters) is BLOCKED: the gate times out because CI and other sessions share the Mac. Before that, #150 to #153 on Oct 14: hero and pricing now say "Free to start" (the weekly-free claim was false for anyone who used it weekly after #144's light-use rule); a read-only Stripe check endpoint after the owner's Apple Pay payment failed on live Checkout while the typed card worked; six ranked lists linked a never-built page, fixed with redirects and a guard test. Earlier Oct 14, #147 and #148: 12 customer images remade after the storage lockout; Stripe embedded checkout inside the trial prompt, dark until the publishable key is set in Vercel | commits e2de8f26, 576f0156 |
| Incident | Supabase locked the project for its storage quota on Oct 6, 7 and 9. Media for Admitly's whole Oct 9 week (9 posts) and 3 of Artesana's failed and sat in review. Remade Oct 14 by an operator route. | commit dc4af506 |
| Customers named | Admitly and Artesana are live workspaces with weekly campaigns | commit dc4af506 |
| Activation | Six free workspaces had a first post publish in the 14 days to Oct 5, so Connect works for external users now. Correction to the Oct 1 scorecard. | commit 9dbfc435 |
| CI | GitHub CI red since June 3; the local green gate is the real gate and now audits dependencies (Next.js 16.3.6 for GHSA-vcvr-r3jv-pc5j) | GREEN_GATE.md, commit 5304b7f0 |
| Search pages | 70 of 75 ranked lists put SpeedRun Social first on a stated free-plan rule; 8 new pages from signup evidence | commits ce9a9fa5, 049cec07 |
| Cloud gate | Proven Oct 18 in a cloud container (4 cores, 15 GB RAM, environment "pioneer") on the production branch at acad1da: install 3s, tsc 70s clean, eslint 74s clean, next build 86s clean with 642 static pages. Two real defects surfaced, neither a missing secret: (1) `bun run test` fails 64 of 18,644 across safeFetchBinary, sendEmail, Zernio profiles, backfillPostTargets, reconcile-posting, postiz webhook and cron auth; every file passes alone, so it is cross-file state leakage inside a `bun test <dir>` group, same under bun 1.3.12 and 1.4.2; (2) the security-headers test spawns a real `next dev`, which writes corrupted `.next/dev/types/*.d.ts` that tsconfig includes, so a second gate run on a fresh clone fails type check until `.next/dev` is deleted. Read-only run, nothing committed or deployed. Caveat: the same evening the Mac gate passed 19,186 tests with 0 failures on the same code, so the 64 container failures are environment-sensitive; the leakage has to be understood before the cloud gate can replace the Mac gate for deploys. | session "Cloud gate proof for SpeedRun Social", Oct 18 |

## The diagnosis

Traffic is thin and activation is broken at two points. First, Connect: as of Sept 3 no external user had ever connected a social account because the Zernio account had no payment method. Second, Upgrade: the Sept 18 audit found almost no upgrade surface at moments of intent, a watermark that is never explained where it is seen, a silently charged second campaign, and an untracked funnel. Billing going live today removes a third wall, but it was never the first one hit.

## Next actions, in order

1. **Connect is proven** (six external first posts by Oct 5). Closed. Replace with: measure the six. Who are they, which of them hit the weekly cap, did any see an upgrade surface.
2. **Upgrade surfaces.** Implement the four audit findings: watermark explained at the point of view with a one-click remove; upgrade modal on the weekly campaign cap; an offer before charging the second weekly campaign; `upgrade_*` events on every surface so "nobody asked" and "nobody wanted" can be told apart.
3. **Merge PR #1.** Review by area, merge, and make `main` the branch that deploys. Then fix or delete the dead GitHub CI so a red badge stops being noise.
4. **Outreach.** Send the first 10 from `docs/sales/2026-09-03-first-customers/pipeline.csv` with four demo workspaces, exactly as the Sept 3 README prescribes. One at a time, by hand.
5. **Search.** Push the queries already on page 2 (chiropractic, law firm, landscaping, plumber, "ai for social media") with internal links and refreshed pages before building new ones.

## Owner-gated items

- Apple Pay failed on live Checkout on Oct 14. The new read-only Stripe check at /api/internal/stripe-recent will say why; read it, or a real customer's wallet payment fails invisibly.

- Set NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY in Vercel production and redeploy. Until then the in-dialog card form (#148) does nothing and Buy now still redirects to Stripe's hosted page.
- Supabase storage: the project hit its quota three times in a week. Raise the plan or prune media before it locks again mid-campaign.

- Zernio payment method: evidently in place (external posts are publishing). Confirm the per-account cost is being watched.
- Google Ads: off until Connect passes.
- Vercel Pro for the 5-minute cron (scheduled posts publish once a day on Hobby).
- Stripe live-mode naming: public business name should read SpeedRun Social, not the holding company (from the Sept 18 go-live checklist; verify it was done).

## Targets

- First paying customer by 2026-10-15.
- Five paying customers by 2026-10-31.
- Every external signup can connect a channel on day one.

## Watch list

- Deploys depend on a laptop. #136 stalled in sleep on Oct 2; #155 is blocked on Oct 16 because the gate times out under CI and other sessions on the same Mac. The deploy lane needs its own machine or CI.
- The Mac froze and rebooted at about 18:30 MDT on Oct 18. Cause, from the Blaze session transcript: after "keep moving, I don't want to see you sitting" at 18:19 MDT it ran eight engineer agents at once, each in its own worktree on the Mac running `bun install`, lint and tests, on top of the gate and the browser. At 18:33 MDT, two minutes after the reboot, it resumed all eight with `bun install --frozen-lockfile` each. The orchestrator sent that session a throttle note at 18:36 MDT: at most two engineers at a time, one shared install, `nice -n 19`, hold while load exceeds the core count. At 19:13 MDT the Mac's load averages were still 22, 26 and 24; the session then gated deploy #163 on load under 18 and started it at 19:14 under caffeinate, saying it would add no CPU load during the gate. No acknowledgement of the throttle note was found in its transcript through 19:15, and Luke did not paste the two-agent rule into the session (his only message after 19:15 was "Send" at 21:37). The session went idle at 21:41 after saying the overnight engineering loop would pick up E8, so the same pattern can recur in the morning. Oct 15 Luke had already opened a Mac performance session because the machine was slow.
- The week's output was SEO and comparison pages. None of the three funnel items moved. The page work is good but it feeds a funnel that still cannot connect a channel.

- The other lane's uncommitted work was shelved to branch wip/other-lane-2026-10-14 on Oct 14. No longer at risk; decide whether any of it is wanted.
- Migration 0066 (x to twitter key unification) is intentionally not applied until its code lands.
