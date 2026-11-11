[CmdletBinding(DefaultParameterSetName = 'Folder')]
param(
    [Parameter(ParameterSetName = 'Folder', Position = 0)]
    [ValidateNotNullOrEmpty()]
    [string]$FolderPath = (Join-Path $PSScriptRoot 'tests\samples\assets'),

    [Parameter(ParameterSetName = 'Zip', Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$ZipPath
)

$ErrorActionPreference = 'Stop'

if ($PSCmdlet.ParameterSetName -eq 'Folder') {
    if (-not (Test-Path -LiteralPath $FolderPath -PathType Container)) {
        throw "Folder not found: $FolderPath"
    }
    $ZipPath = Join-Path $FolderPath 'basic-agent-prebuilt.zip'
}

if (-not (Test-Path -LiteralPath $ZipPath -PathType Leaf)) {
    throw "ZIP file not found: $ZipPath"
}

Add-Type -AssemblyName System.IO.Compression.FileSystem

$archive = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path -LiteralPath $ZipPath).Path)
try {
    $entry = $archive.GetEntry('packages/certifi/cacert.pem')
    if ($null -eq $entry) {
        throw "Certificate bundle packages/certifi/cacert.pem was not found in: $ZipPath"
    }

    $reader = [System.IO.StreamReader]::new($entry.Open())
    try {
        $bundle = $reader.ReadToEnd()
    }
    finally {
        $reader.Dispose()
    }

    $found = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($match in [regex]::Matches(
        $bundle,
        '(?s)-----BEGIN CERTIFICATE-----\s*(.*?)\s*-----END CERTIFICATE-----'
    )) {
        $cert = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new(
            [Convert]::FromBase64String($match.Groups[1].Value)
        )
        try {
            if ($cert.Subject -match 'CN=emSign (ECC )?Root CA - (G1|G3|C1|C3)(,|$)') {
                $commonName = $Matches[0] -replace '^CN=', '' -replace ',$', ''
                [void]$found.Add($commonName)
                Write-Output "Subject: $($cert.Subject)"
                Write-Output "Issuer:  $($cert.Issuer)"
                Write-Output "SHA-1 thumbprint: $($cert.Thumbprint)"
                Write-Output $match.Value
                Write-Output ''
            }
        }
        finally {
            $cert.Dispose()
        }
    }

    if ($found.Count -eq 0) {
        Write-Output 'No matching emSign root certificates found.'
    }
}
finally {
    $archive.Dispose()
}
