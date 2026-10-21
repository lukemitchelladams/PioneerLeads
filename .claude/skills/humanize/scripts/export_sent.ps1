<#
export_sent.ps1 - export the user's own sent mail from Outlook so /humanize can learn their voice
and compare its drafts against what they actually sent. Windows + Outlook desktop only.

Reads Sent Items of every Outlook store over the last N days. For each message it keeps only the
text he wrote: the quoted thread (From:/Sent: block, Original Message, "On ... wrote:") is cut off.
Signature lines are removed later by hz.py (it finds lines repeated across many messages).

  & export_sent.ps1                    # last 120 days -> <data home>\data\sent.json
  & export_sent.ps1 -Days 30 -Max 200

Data home matches hz.py: $env:HZ_HOME, else the skill folder when it already holds data\, else
~\.claude\humanize. Also records the mailbox owner's name in <data home>\config.json
(signature_name) so hz.py can strip the signature block. Read-only against Outlook.
#>
param(
  [int]$Days = 120,
  [int]$Max = 600,
  [string]$Out = ''
)

$skill = Split-Path $PSScriptRoot
$home_ = if ($env:HZ_HOME) { $env:HZ_HOME } elseif (Test-Path (Join-Path $skill 'data')) { $skill } else { Join-Path $HOME '.claude\humanize' }
if (-not $Out) { $Out = Join-Path $home_ 'data\sent.json' }

$ol = New-Object -ComObject Outlook.Application
$ns = $ol.GetNamespace('MAPI')
$me = [string]$ns.CurrentUser.Name
$since = (Get-Date).AddDays(-$Days).ToString('g')

function Own-Text([string]$b) {
  if ($null -eq $b) { return '' }
  $b = $b -replace "`r`n", "`n"
  $cuts = @(
    '(?m)^\s*From:\s.+$',
    '(?m)^\s*-{2,}\s*Original Message\s*-{2,}',
    '(?m)^\s*On .{5,200}wrote:\s*$',
    '(?m)^\s*_{10,}\s*$',
    '(?m)^\s*Get Outlook for '
  )
  $end = $b.Length
  foreach ($c in $cuts) {
    $m = [regex]::Match($b, $c)
    if ($m.Success -and $m.Index -lt $end) { $end = $m.Index }
  }
  $t = $b.Substring(0, $end)
  $t = $t -replace '<(https?|mailto|tel):[^>]*>', ''
  $t = $t -replace '(?m)[ \t]+$', ''
  $t = $t -replace '(\n){3,}', "`n`n"
  $t.Trim()
}

$rows = New-Object System.Collections.Generic.List[object]
foreach ($store in $ns.Stores) {
  try { $sent = $store.GetDefaultFolder(5) } catch { continue }
  try { $items = $sent.Items.Restrict("[SentOn] >= '$since'") } catch { continue }
  $items.Sort('[SentOn]', $true)
  foreach ($m in $items) {
    if ($rows.Count -ge $Max) { break }
    if ($m.Class -ne 43) { continue }
    $own = Own-Text ([string]$m.Body)
    if ($own.Length -lt 2) { continue }
    $rows.Add([ordered]@{
      sent    = $m.SentOn.ToString('s')
      store   = [string]$store.DisplayName
      to      = [string]$m.To
      cc      = [string]$m.CC
      subject = [string]$m.Subject
      reply   = [bool]($m.Subject -match '^\s*(\[[^\]]*\]\s*)?(re|fw|fwd)\s*:')
      body    = $own
    })
  }
}

New-Item -ItemType Directory -Force -Path (Split-Path $Out) | Out-Null
$rows | ConvertTo-Json -Depth 3 | Set-Content -Path $Out -Encoding utf8

# record the signature name once, so hz.py can cut the signature block off each message
$cfgPath = Join-Path $home_ 'config.json'
$cfg = if (Test-Path $cfgPath) { Get-Content $cfgPath -Raw | ConvertFrom-Json } else { [pscustomobject]@{ require_closer = $true; signature_name = '' } }
if (-not $cfg.signature_name -and $me) {
  $cfg | Add-Member -NotePropertyName signature_name -NotePropertyValue $me -Force
  $cfg | ConvertTo-Json | Set-Content -Path $cfgPath -Encoding utf8
}
"Exported $($rows.Count) sent messages (last $Days days) to $Out"
