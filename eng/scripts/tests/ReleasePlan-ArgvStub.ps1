# Diagnostic branch only: capture argv; never query or write Azure DevOps.
[CmdletBinding()]
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$CliArgs)

Set-StrictMode -Version 4
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($env:RELEASE_PLAN_TEST_CAPTURE)) { throw 'Capture file was not configured.' }
ConvertTo-Json -InputObject @($CliArgs) -Compress | Add-Content -LiteralPath $env:RELEASE_PLAN_TEST_CAPTURE
$global:LASTEXITCODE = 0
return 'Captured arguments only. No release plan was updated.'
