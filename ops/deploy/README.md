# Always-on bid scanner: one-time setup (about 20 minutes)

**Status 2026-10-20: built and tested, NOT deployed.** It needs Luke's yes on the cost (about $12/month).

Why: a cloud Claude session is reclaimed when idle, so the scanner should not live in one. A small server runs
the logged-in scan every hour at :35, pushes the results to this repo, and alerts Luke by email when a scan
fails or does not happen. A free GitHub Actions backup takes over by itself if the server misses 80+ minutes.

| Piece | What it does | Cost |
|---|---|---|
| VPS, `ops/deploy/vps/` | hourly systemd timer runs `scripts/bidwatch/run.py --push`; catches up after a reboot | about $12/month |
| healthchecks.io | emails Luke when a scan fails, is degraded, or is missing | free tier |
| GitHub Actions, `.github/workflows/bidwatch-failover.yml` | idle unless the last pushed scan is 80+ min old | about 1 runner minute per idle hour; inside the free tier |

## Steps

1. **Make this repo private.** GitHub, repo Settings, General, Danger Zone, Change visibility. Do this first:
   on a public repo the Actions logs and caches are public too.
2. **Create the server.** DigitalOcean, Create, Droplets: Ubuntu 24.04, Basic, Regular, 2 GB RAM / 1 CPU, any US
   region. Add your SSH key. Note the IP address.
3. **Run the setup script** from a computer that has this repo:
   ```
   scp ops/deploy/vps/provision.sh root@<server-ip>:
   ssh -t root@<server-ip> bash provision.sh
   ```
   - It prints a deploy key. In GitHub: repo Settings, Deploy keys, Add deploy key, paste it, tick
     **Allow write access**, Add. Then press Enter in the terminal.
   - It asks for the BidNet email, BidNet password and SAM.gov API key. Typing is hidden. They are stored only
     on the server in root-only files under `/etc/brownbison/creds/`.
   - It asks for an optional Google app password for luke@brownbisonco.com. With it, the scanner reads BidNet's
     emailed login code itself (read-only). Press Enter to skip.
4. **Turn on alerts.** At healthchecks.io create a check named `bidwatch scan`, period 1 hour, grace 30 minutes.
   Copy its ping URL, then on the server:
   ```
   echo 'HC_PING_SCAN=https://hc-ping.com/<your-check-uuid>' >> /etc/brownbison/bidwatch.env
   ```
5. **First scan.**
   ```
   systemctl start bidwatch.service; journalctl -u bidwatch -n 80 --no-pager
   ```
   If BidNet asks for a confirmation code on this first login and you skipped the app password, run this within
   5 minutes with the 6-digit code from the email:
   ```
   sudo -u bidwatch python3 /opt/bidwatch/repo/scripts/bidwatch/set_code.py 123456
   ```
   The confirmed device is remembered in the saved session after that.
6. **Tell the MAIN Claude session the server is live.** It then retires the cloud hourly scan, so the two do not
   double the BidNet traffic.
7. **Optional backup.** GitHub repo Settings, Secrets and variables, Actions.
   - Secrets: `BIDNET_USER`, `BIDNET_PASS`, `SAM_API_KEY`, `STATE_PASSPHRASE` (any long random phrase; it encrypts
     the saved BidNet session in the Actions cache), optionally `BIDNET_CODE_IMAP_PASS`.
   - Variables: `BIDWATCH_FAILOVER` = `on`, optionally `HC_PING_SCAN`.

## Day to day

- Results land in `bids/_watch/REPORT.md`, `open_bids.json` and `health.json` on branch `claude/zealous-cerf-el4iek`.
- Server status: `systemctl list-timers bidwatch.timer` and `journalctl -u bidwatch --since today`.
- Exit codes: 0 = all sources fresh, 3 = degraded (a source blind, last good rows kept), 2 = nothing scanned,
  4 = another scan was already running.
- DLA DIBBS is never read from the server or from GitHub: its user agreement (FAQ #45) prohibits cloud hosting
  and proxies. Only Luke's own computer may set `BIDWATCH_ALLOW_DIBBS=1`.
- Never commit a credential. The scanner reads secrets from the environment only.
