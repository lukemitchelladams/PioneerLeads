# Bulletproof scanner architecture (opus research agent, 2026-10-20)

**First: the GitHub repo is PUBLIC** (verified: api.github.com/repos/lukemitchelladams/PioneerLeads -> "visibility":
"public"). MEMORY.md sub pricing, bid strategy and BidNet member documents are readable by anyone. Make it private.

## Ranking
1. **VPS primary + GitHub Actions failover + healthchecks.io dead-man switch; Claude triages only** (recommended,
   ~$12-15/mo, ~1 agent-day + 1-2 h of Luke).
2. VPS alone (DigitalOcean 2 GiB $12/mo; systemd timer with Persistent=true catches missed runs; persistent disk keeps
   one BidNet "device"). PaaS cron weaker (Render no disk, Fly fuzzy timing, Railway skips overlaps).
3. GitHub Actions alone (fresh Azure VM per run, session must ride in an encrypted cache; schedule lag/drops; private
   repo ~$30/mo for hourly).
4. Luke's PC (sleeps/updates; "residential IP clears Cloudflare" is unverified).
5. Claude cloud scheduled tasks (current): research preview, 1-hour minimum, counts against Luke's subscription limits,
   VM reclaim can lose the credential file, env vars visible to anyone using the environment.

## Target design
- Primary: VPS, systemd timer `OnCalendar=*:35`, `RandomizedDelaySec=4min`, `Persistent=true`, oneshot `run.py --push`.
- Failover: GitHub Actions cron `15 * * * *`, `concurrency: bidwatch`, exits unless origin health.json > 80 min old;
  restores a gpg-encrypted session from cache.
- Secrets: password manager is source of truth; VPS `LoadCredential=`; write deploy key; Actions secrets; Claude holds none.
- Device codes: Gmail API gmail.readonly (Internal OAuth app) or app password (mailcode.py).
- Monitoring: healthchecks.io free (scan, primary, bidnet-login, samgov, dibbs, bonfire, dashboard) + Pushover/email.
- Rate limits: <=1 BidNet scan/hour/IP, 1.5-4 s between pages, 2 h BidNet cool-down after a robot check.

## Code changes recommended
Per-source exit codes/pings (run.py exits 0 even when every source was blind because carried rows count);
code-needed marker expires after 6 h; run lock; `--only-if-stale`; `scanned_by`; robot cool-down; Gmail reader;
`$CREDENTIALS_DIRECTORY`; `storage_state(indexed_db=True)`; retire `--loop`.

## Migration checklist
1. Repo private; rotate BIDNET_PASS and SAM key (both pasted in chat). 2. healthchecks.io + Pushover + Gmail token;
code changes with tests. 3. Provision VPS from a repo script; one manual logged-in run. 4. Failover workflow + secrets;
test with VPS stopped. 5. Disable the :35 Claude scan; Claude does freshness checks; delete ~/.brownbison/env in HQ.
6. Game day: stop VPS, expire session, block a source, confirm alerts. 7. Optional: Luke's PC twice daily for
Bonfire/OpenGov details.

## Top risks
1. BidNet terms / robot checks / lockout (one session per account? scanner vs Luke's own Chrome may log each other
   out; track re-logins). 2. Silent blindness (per-source checks + failover + freshness check). 3. Secret exposure
   (private repo, encrypted session cache, single-repo keys, rotation runbook).
Sources: freedesktop systemd.timer, digitalocean.com/pricing, docs.github.com (actions billing/schedule/secrets),
render/fly/railway cron docs, developers.cloudflare.com/cloudflare-challenges, healthchecks.io docs,
developers.google.com/identity oauth2 expiration, docs.aws.amazon.com/waf rate-based rules, code.claude.com docs.
