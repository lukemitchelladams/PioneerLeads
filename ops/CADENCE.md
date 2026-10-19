# Operating cadence

How the orchestrator keeps the three ventures moving.

## Daily, weekdays (automated check-in)

A Routine fires into the orchestrator session each weekday morning, Mountain time. Each run:

0. Scans Luke's other Claude sessions first (list_sessions, then list_events on anything running or recently idle). Records every session waiting on Luke. Nudges an idle session with one instruction when its last message left a step Claude could take itself. Never messages a session Luke is typing in, and never sends an instruction that spends money, sends email, posts publicly or deletes anything.
1. Reads the live signals: SpeedRun Social health and billing endpoints, latest Vercel deploys, the open PR, and the last commits on both repos.
2. Checks each venture's top 3 in `PORTFOLIO.md` for progress since the last run.
3. Updates the scorecards with anything that changed and the date.
4. Surfaces exactly one next action per venture, and names anything that is waiting on Luke.
5. Says nothing if nothing moved, beyond a one-line "no change" note.

## Weekly, Monday (CEO brief)

- Rewrite the top 3 per venture for the coming week.
- Score last week: done, slipped, blocked, and why.
- Re-rank the ventures by where a week of Luke's time compounds most. Today that order is SpeedRun Social (billing is live, the funnel is the only thing between it and revenue), then government contracting (a time-boxed award window), then POE (steady client work with decisions parked on the client).
- Append any owner decision to `DECISIONS.md`.

## Rules the orchestrator follows

- No venture goes a week without a shipped change or a written reason.
- Owner-gated items are listed, dated, and re-raised until closed; they are never silently dropped.
- Every number in a scorecard has a source and a date. Estimates are marked as estimates.
- Work goes where it is accountable: product work in the venture's own repo, portfolio state in this folder.
- The orchestrator does not restart or widen scope on its own. New ventures or large pivots are a Luke decision recorded in `DECISIONS.md`.

## Where state lives

| Thing | Location |
| --- | --- |
| Portfolio brief and weekly top 3 | `ops/PORTFOLIO.md` |
| Scorecards | `ops/speedrun-social.md`, `ops/poe-radius.md`, `ops/govcon.md` |
| Decisions and open questions | `ops/DECISIONS.md` |
| SpeedRun Social product state | `autosocial-ai` repo: `.autonomy/`, `docs/research/`, `docs/sales/` |
| POE product state | `ROE` repo: `CLAUDE.md`, `docs/project-context.md`, `supabase/APPLIED.md` |
| Govcon documents | Google Drive (RFP) and this folder until a repo exists |
