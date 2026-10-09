# Cloud session setup for this repo

## Network access (required to pull bid documents from a cloud session)

The default network policy blocks the procurement portals. In the Claude Code cloud environment
settings (session title bar → cloud environment menu → Edit → Network access), either choose a
broader access level or add these under **Allowed domains** (leave "Allow package managers" on):

```
bidnetdirect.com
www.bidnetdirect.com
rockymountainbidsystem.com
www.rockymountainbidsystem.com
sam.gov
api.sam.gov
parkerco.gov
www.parkerco.gov
```

Docs: https://code.claude.com/docs/en/cloud-environments#network-access

BidNet document downloads are login-gated. Even with network access, the agent cannot log in
for you. The reliable path is: download the PDFs on your machine, commit them to
`bids/<bid>/docs/`, and let the cloud session read them from the repo.

## SAM.gov API key (optional, federal bids only)
Add `SAM_API_KEY` as an environment variable in the cloud environment settings so
`scripts/samgov_search.py` works.

## SessionStart hook
`.claude/hooks/session-start.sh` runs on every cloud session start. It only checks tooling
(Python, PDF text extraction) and prints the memory file so the agent starts with context.
