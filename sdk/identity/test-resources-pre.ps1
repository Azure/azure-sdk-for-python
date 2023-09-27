[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param (
    # Captures any arguments from eng/New-TestResources.ps1 not declared here (no parameter errors).
    [Parameter(ValueFromRemainingArguments = $true)]
    $RemainingArguments
)

if (!$CI) {
    # TODO: Remove this once auto-cloud config downloads are supported locally
    Write-Host "Skipping cert setup in local testing mode"
    return
}

if ($EnvironmentVariables -eq $null -or $EnvironmentVariables.Count -eq 0) {
    throw "EnvironmentVariables must be set in the calling script New-TestResources.ps1"
}

$tmp = $env:TEMP ? $env:TEMP : [System.IO.Path]::GetTempPath()
$pemPath = Join-Path $tmp "test.pem"
$pemPasswordProtectedPath = Join-Path $tmp "testPasswordProtected.pem"

Write-Host "Creating identity test files: $pemPath $pemPasswordProtectedPath"

$pemContent = $EnvironmentVariables['PEM_CONTENT'] -replace "\n","`n"
$pemContentPasswordProtected = $EnvironmentVariables['PEM_CONTENT_PASSWORD_PROTECTED'] -replace "\n","`n"

Set-Content -Path $pemPath -Value $pemContent
Set-Content -Path $pemPasswordProtectedPath -Value $pemContentPasswordProtected

# Set for pipeline
Write-Host "##vso[task.setvariable variable=IDENTITY_CERT_PEM;]$pemPath"
Write-Host "##vso[task.setvariable variable=IDENTITY_CERT_PEM_PASSWORD_PROTECTED;]$pemPasswordProtectedPath"
Write-Host "##vso[task.setvariable variable=CERTIFICATE_PASSWORD;]$($EnvironmentVariables['CERTIFICATE_PASSWORD'])"
Write-Host "##vso[task.setvariable variable=PFX_CONTENT;]$($EnvironmentVariables['PFX_CONTENT'])"
Write-Host "##vso[task.setvariable variable=PFX_CONTENT_PASSWORD_PROTECTED;]$($EnvironmentVariables['PFX_CONTENT_PASSWORD_PROTECTED'])"
# Set for local
$env:IDENTITY_CERT_PEM = $pemPath
$env:IDENTITY_CERT_PEM_PASSWORD_PROTECTED = $pemPasswordProtectedPath
$env:CERTIFICATE_PASSWORD = $EnvironmentVariables['CERTIFICATE_PASSWORD']
$env:PFX_CONTENT = $EnvironmentVariables['PFX_CONTENT']
$env:PFX_CONTENT_PASSWORD_PROTECTED = $EnvironmentVariables['PFX_CONTENT_PASSWORD_PROTECTED']
