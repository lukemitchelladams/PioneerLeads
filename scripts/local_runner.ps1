# Brown Bison bid scan — Windows. Schedule with Task Scheduler every 4 hours:
#   powershell -ExecutionPolicy Bypass -File C:\path\to\repo\scripts\local_runner.ps1
$ErrorActionPreference = "Continue"
Set-Location (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
if (Test-Path .env) { Get-Content .env | ForEach-Object { if ($_ -match '^\s*([A-Z_]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2].Trim('"'), "Process") } } }
git pull --rebase --quiet origin (git rev-parse --abbrev-ref HEAD) 2>$null
if (-not (Test-Path .venv)) { python -m venv .venv }
.\.venv\Scripts\Activate.ps1
pip install --quiet -r requirements.txt
python -m playwright install chromium 2>$null | Out-Null
python scripts\scan_bids.py *> "$env:TEMP\brownbison-scan.log"
Get-Content "$env:TEMP\brownbison-scan.log" -Tail 5
git add bids\_watch memory 2>$null
$staged = git diff --cached --quiet; if ($LASTEXITCODE -ne 0) {
  $headline = (Select-String -Path bids\_watch\REPORT.md -Pattern '^\*\*Headline' | Select-Object -First 1).Line
  if ($headline.Length -gt 140) { $headline = $headline.Substring(0,140) }
  git -c user.name="BrownBison Scanner" -c user.email="luke@brownbisonco.com" commit -q -m "scan: $(Get-Date -Format u) $headline"
  foreach ($i in 1..4) { git push -q origin HEAD; if ($LASTEXITCODE -eq 0) { break }; Start-Sleep -Seconds ([math]::Pow(2,$i)) }
}
