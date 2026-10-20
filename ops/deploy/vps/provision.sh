#!/usr/bin/env bash
# One-time setup on a fresh Ubuntu 24.04 VPS (2 GiB RAM, US region), run as root:
#   scp provision.sh root@<server>:  &&  ssh -t root@<server> bash provision.sh
# (The repo is meant to be private, so copy this file over rather than curl it.)
# It contains and prints no secret. It asks for the secrets at the end, reading from the keyboard (/dev/tty).
# Safe to re-run: the existing deploy key, clone and secrets are kept.
set -euo pipefail
REPO_SSH="${REPO_SSH:-git@github.com:lukemitchelladams/PioneerLeads.git}"
BRANCH="${BRANCH:-claude/zealous-cerf-el4iek}"
TTY=/dev/tty

apt-get update -y && apt-get install -y python3 python3-pip python3-venv git
id bidwatch >/dev/null 2>&1 || useradd --system --create-home --home-dir /opt/bidwatch --shell /usr/sbin/nologin bidwatch
install -d -o bidwatch -g bidwatch /opt/bidwatch

# deploy key for pushes: add the PUBLIC key to GitHub (repo Settings -> Deploy keys -> Add -> Allow write access)
if [ ! -f /opt/bidwatch/.ssh/id_ed25519 ]; then
  sudo -u bidwatch mkdir -p -m 0700 /opt/bidwatch/.ssh
  sudo -u bidwatch ssh-keygen -q -t ed25519 -N "" -C "bidwatch-vps" -f /opt/bidwatch/.ssh/id_ed25519
  echo; echo "ADD THIS DEPLOY KEY (tick 'Allow write access') TO THE GITHUB REPO, then press Enter:"
  cat /opt/bidwatch/.ssh/id_ed25519.pub
  read -r _ < "$TTY"
fi
sudo -u bidwatch bash -c "ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null"
[ -d /opt/bidwatch/repo/.git ] || sudo -u bidwatch git clone -b "$BRANCH" "$REPO_SSH" /opt/bidwatch/repo
sudo -u bidwatch git -C /opt/bidwatch/repo config user.name "Brown Bison bidwatch (VPS)"
sudo -u bidwatch git -C /opt/bidwatch/repo config user.email "bidwatch-vps@users.noreply.github.com"

pip3 install --break-system-packages -r /opt/bidwatch/repo/requirements.txt
PLAYWRIGHT_BROWSERS_PATH=/opt/bidwatch/pw-browsers python3 -m playwright install --with-deps chromium
chown -R bidwatch:bidwatch /opt/bidwatch/pw-browsers

# secrets: one root-only file each; systemd hands them to the service at run time (LoadCredential)
install -d -m 0700 /etc/brownbison/creds
ask() {  # name, prompt; keeps an existing non-empty value
  local f="/etc/brownbison/creds/$1" v
  if [ -s "$f" ]; then echo "$1: already set, kept"; return; fi
  read -r -s -p "$2: " v < "$TTY"; echo
  printf '%s' "$v" > "$f"
}
ask BIDNET_USER "BidNet login email"
ask BIDNET_PASS "BidNet password"
ask SAM_API_KEY "SAM.gov API key"
ask BIDNET_CODE_IMAP_PASS "Google app password for luke@brownbisonco.com, lets the scanner read BidNet's login code (Enter = skip)"
chmod 0600 /etc/brownbison/creds/*

# non-secret settings (one per line), e.g. HC_PING_SCAN=https://hc-ping.com/<uuid>. BIDWATCH_ALLOW_DIBBS stays OFF here.
touch /etc/brownbison/bidwatch.env
install -m 0755 /opt/bidwatch/repo/ops/deploy/vps/run-scan.sh /opt/bidwatch/run-scan.sh
install -m 0644 /opt/bidwatch/repo/ops/deploy/vps/bidwatch.service /etc/systemd/system/bidwatch.service
install -m 0644 /opt/bidwatch/repo/ops/deploy/vps/bidwatch.timer /etc/systemd/system/bidwatch.timer
systemctl daemon-reload && systemctl enable --now bidwatch.timer
echo "Installed. First scan now (watch it):  systemctl start bidwatch.service; journalctl -u bidwatch -n 80 --no-pager"
