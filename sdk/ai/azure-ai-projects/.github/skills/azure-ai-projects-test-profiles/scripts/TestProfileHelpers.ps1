# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

function Get-TestProfileDigest {
    param([string]$Text)

    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { ([BitConverter]::ToString($algorithm.ComputeHash([Text.Encoding]::UTF8.GetBytes($Text)))).Replace('-', '').ToLowerInvariant() }
    finally { $algorithm.Dispose() }
}

function Get-TestProjectEndpointHash {
    param([string]$Endpoint)

    $uri = $null
    if ([string]::IsNullOrWhiteSpace($Endpoint) -or $Endpoint.Trim() -cne $Endpoint -or
        -not [Uri]::TryCreate($Endpoint, [UriKind]::Absolute, [ref]$uri) -or $uri.Scheme -ne 'https' -or
        $uri.UserInfo -or $uri.Query -or $uri.Fragment -or $uri.AbsolutePath -notmatch '^/api/projects/[^/]+/?$') {
        throw 'FOUNDRY_PROJECT_ENDPOINT must be an HTTPS /api/projects/<project> URL without credentials, query, or fragment.'
    }
    (Get-TestProfileDigest $uri.AbsoluteUri.TrimEnd('/')).Substring(0, 32)
}

function Assert-TestProfile {
    param([object]$TestProfile)

    if ($TestProfile -isnot [pscustomobject] -or $TestProfile.TestId -isnot [string] -or
        $TestProfile.TestId -cnotmatch '^tests/samples/[^:]+\.py::[^\r\n]+$' -or
        $TestProfile.TestId -match '\\|\$\(' -or
        $TestProfile.Enabled -isnot [bool] -or $TestProfile.Environment -isnot [array]) {
        throw 'A profile needs an exact package-relative pytest TestId, an Enabled boolean, and an Environment array.'
    }
    $testFile = $TestProfile.TestId.Split('::')[0]
    if ($testFile -match '[*?\[\]\\]' -or $testFile.Split('/') -contains '..' -or
        ($TestProfile.TestId -split '::', 2)[1].Split('[')[0] -match '[*?]') {
        throw 'TestId must identify one exact test, not a wildcard, absolute path, or parent traversal.'
    }
    if ($TestProfile.SamplePath -isnot [string] -or $TestProfile.SamplePath -cnotmatch '^samples/.+\.py$' -or
        $TestProfile.SamplePath -match '[*?\[\]\\\r\n]|\$\(' -or $TestProfile.SamplePath.Split('/') -contains '..') {
        throw 'SamplePath must be one exact package-relative Python sample path using forward slashes.'
    }
    $allowed = @('TestId', 'SamplePath', 'Enabled', 'Environment')
    if (@($TestProfile.PSObject.Properties | Where-Object { $_.Name -notin $allowed }).Count -gt 0) {
        throw 'Profiles contain test metadata only: no pipeline ID, endpoint value, secret value, or build prerequisite.'
    }
    $names = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $endpointCount = 0
    foreach ($binding in $TestProfile.Environment) {
        if ($binding -isnot [pscustomobject] -or $binding.Name -cnotmatch '^[A-Z][A-Z0-9_]*$' -or -not $names.Add($binding.Name)) {
            throw 'Environment names must be unique uppercase environment variable names.'
        }
        if ($binding.Name -in @('SYSTEM_ACCESSTOKEN', 'AZURE_DEVOPS_BEARER_TOKEN', 'AZURE_DEVOPS_EXT_PAT')) {
            throw 'Do not bind personal or pipeline ADO authentication tokens into test profiles.'
        }
        if ($binding.Name -match '^PYTEST_' -or $binding.Name -in @(
            'PATH', 'PYTHONPATH', 'PYTHONHOME', 'PYTHONSTARTUP', 'PYTHONINSPECT',
            'AZURE_TEST_RUN_LIVE', 'AZURE_SKIP_LIVE_RECORDING'
        )) {
            throw 'Profiles may configure sample inputs, not Python/pytest execution controls or recording mode.'
        }
        if ($binding.Name -eq 'FOUNDRY_PROJECT_ENDPOINT') {
            if ($binding.Source -cne 'ProjectEndpoint' -or @($binding.PSObject.Properties.Name).Count -ne 2) {
                throw 'FOUNDRY_PROJECT_ENDPOINT must inherit the authoritative ProjectEndpoint; profile overrides are forbidden.'
            }
            $endpointCount++
        } elseif ($binding.Source -cne 'Variable' -or $binding.Variable -cnotmatch '^[A-Z][A-Z0-9_]*$' -or
            @($binding.PSObject.Properties.Name).Count -ne 3 -or $binding.Variable -eq 'FOUNDRY_PROJECT_ENDPOINT') {
            throw 'Other environment entries must contain only Name, Source=Variable, and a Variable reference; never a value.'
        }
    }
    if ($endpointCount -ne 1) { throw 'Every profile must require FOUNDRY_PROJECT_ENDPOINT from ProjectEndpoint exactly once.' }
}

function ConvertFrom-TestProfileRegistry {
    param([string]$Json)

    try { $registry = $Json | ConvertFrom-Json -ErrorAction Stop } catch { throw 'The test-profile registry must be valid JSON.' }
    if ($registry -isnot [pscustomobject] -or $registry.Version -ne 1 -or $registry.Profiles -isnot [array] -or
        @($registry.PSObject.Properties).Count -ne 2) {
        throw 'The registry requires Version=1 and a Profiles array.'
    }
    $ids = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($testProfile in $registry.Profiles) {
        Assert-TestProfile $testProfile
        if (-not $ids.Add($testProfile.TestId)) { throw 'Only one profile is allowed per exact TestId.' }
    }
    $registry
}

function Invoke-TestProfileRequest {
    param([string]$Method, [string]$Uri, [string]$BearerToken, [object]$Body, [scriptblock]$RequestInvoker,
        [ValidateRange(1, 60)][int]$TimeoutSeconds = 60)

    if ([string]::IsNullOrWhiteSpace($BearerToken)) { throw 'An ADO bearer token must be supplied in process memory.' }
    $headers = @{ Authorization = "Bearer $BearerToken" }
    try {
        if ($RequestInvoker) { return & $RequestInvoker $Method $Uri $headers $Body $TimeoutSeconds }
        $arguments = @{ Method = $Method; Uri = $Uri; Headers = $headers; ErrorAction = 'Stop'; TimeoutSec = $TimeoutSeconds }
        if ($null -ne $Body) { $arguments.ContentType = 'application/json'; $arguments.Body = ConvertTo-Json -InputObject $Body -Depth 50 -Compress }
        Invoke-RestMethod @arguments -Verbose:$false -Debug:$false
    } catch { throw "ADO $Method request failed. Check access and inspect ADO before retrying; request/response details are suppressed." }
}

function Get-TestProfileRegistryGroup {
    param([object]$Group, [int]$GroupId)

    if (-not $Group -or $Group.id -ne $GroupId -or $Group.type -ne 'Vsts' -or -not $Group.variables) {
        throw 'The registry must be an existing ordinary ADO Library variable group.'
    }
    # This group stores metadata only. Never read-modify-write a group holding masked secrets.
    if (@($Group.variables.PSObject.Properties | Where-Object { $_.Value.isSecret }).Count -gt 0) {
        throw 'The registry group must be metadata-only; keep all secret values in separate endpoint variable groups.'
    }
    $entry = $Group.variables.SAMPLE_TEST_PROFILES_JSON
    if (-not $entry -or $entry.isSecret) { throw 'The registry group needs a non-secret SAMPLE_TEST_PROFILES_JSON variable.' }
    $null = ConvertFrom-TestProfileRegistry $entry.value
    [pscustomobject]@{
        Json = [string]$entry.value
        Digest = Get-TestProfileDigest ((ConvertTo-Json -InputObject $Group -Depth 50 -Compress))
    }
}

function ConvertTo-TestProfileMarkdown {
    param([string]$Text)

    [Net.WebUtility]::HtmlEncode($Text).Replace('|', '&#124;').Replace('`', '&#96;').Replace("`r", ' ').Replace("`n", ' ')
}

function Assert-TestProfileJUnitResult {
    param([string]$TestId, [string]$JUnitPath)

    if (-not (Test-Path -LiteralPath $JUnitPath -PathType Leaf)) {
        throw 'The test did not produce a new JUnit report.'
    }
    $reader = $null
    try {
        $settings = [Xml.XmlReaderSettings]::new()
        $settings.DtdProcessing = [Xml.DtdProcessing]::Prohibit
        $settings.XmlResolver = $null
        $reader = [Xml.XmlReader]::Create([IO.Path]::GetFullPath($JUnitPath), $settings)
        $document = [Xml.XmlDocument]::new()
        $document.XmlResolver = $null
        $document.Load($reader)
    } catch { throw 'The test produced an invalid JUnit report.' }
    finally { if ($reader) { $reader.Dispose() } }
    $cases = @($document.SelectNodes('//testcase'))
    if ($cases.Count -ne 1 -or $document.SelectNodes('//failure|//error|//skipped').Count -gt 0) {
        throw 'A profile requires exactly one executed, passed test case, not a skipped or collection-only result.'
    }
    foreach ($suite in $document.SelectNodes('//testsuite')) {
        if ([int]$suite.GetAttribute('errors') -gt 0 -or [int]$suite.GetAttribute('failures') -gt 0) {
            throw 'The JUnit suite contains failures or errors.'
        }
    }
    $parts = $TestId -split '::', 2
    $bracket = $parts[1].IndexOf('[')
    $baseName = if ($bracket -ge 0) { $parts[1].Substring(0, $bracket) } else { $parts[1] }
    $segments = $baseName -split '::'
    $expectedName = $segments[-1] + $(if ($bracket -ge 0) { $parts[1].Substring($bracket) } else { '' })
    $expectedClass = $parts[0].Substring(0, $parts[0].Length - 3).Replace('/', '.')
    if ($segments.Count -gt 1) { $expectedClass += '.' + ($segments[0..($segments.Count - 2)] -join '.') }
    $actualClass = $cases[0].GetAttribute('classname')
    if ($cases[0].GetAttribute('name') -cne $expectedName -or
        (-not $actualClass.Equals($expectedClass, [StringComparison]::Ordinal) -and
         -not $actualClass.EndsWith(".$expectedClass", [StringComparison]::Ordinal))) {
        throw 'The JUnit testcase does not match the exact assigned TestId.'
    }
}