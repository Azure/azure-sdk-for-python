# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)] [string] $StatePath,
    [Alias('ExplicitSubscriptionId')] [string] $SubscriptionId = '',
    [string] $TenantId = '',
    [string] $Location = '',
    [string] $SetName = '',
    [Alias('MiName', 'IdentityName')] [AllowNull()] [AllowEmptyString()] [string] $IdentityNamePattern = 'mi-azsdk-sample-{resource}-wus3',
    [string] $ExpectedCallerPrincipalId = '',
    [string] $PipelinePrincipalId = '',
    [string] $PipelineClientId = '',
    [switch] $Apply,
    [switch] $VerifyOnly
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'BootstrapHelpers.ps1')
. (Join-Path $PSScriptRoot 'IdentityNaming.ps1')
# This entry point never logs in, switches identity, repairs grants, or deploys workloads.
if ($Apply -and $VerifyOnly) { throw '-Apply and -VerifyOnly are mutually exclusive.' }
$StatePath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($StatePath)
$previous = $null
if (Test-Path -LiteralPath $StatePath) {
    try { $previous = Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json -AsHashtable -NoEnumerate -ErrorAction Stop }
    catch { throw 'Cannot parse bootstrap state; no request or write attempted.' }
    if ($previous -isnot [System.Collections.IDictionary]) { throw 'Invalid bootstrap state schema.' }
}
$schemaVersion = 3
if ($null -ne $previous) {
    if (($previous['schemaVersion'] -isnot [int] -and $previous['schemaVersion'] -isnot [long]) -or $previous['schemaVersion'] -notin @(1, 2, 3)) { throw 'Invalid bootstrap state schema.' }
    $schemaVersion = $previous['schemaVersion']
}
$legacy = $schemaVersion -eq 1
$readonlyLegacy = $schemaVersion -in @(1, 2)
if ($readonlyLegacy -and -not $VerifyOnly) {
    if ($schemaVersion -eq 2 -and $previous['status'] -ceq 'Previewed') { throw 'Obsolete schema 2 preview: the compiler contract changed. Preserve it and obtain a fresh reviewed schema 3 dry run at a new state path.' }
    throw "Legacy schema $schemaVersion is verification-only; an attempt is already recorded. No preview, apply, compilation or state upgrade is permitted."
}
if ($legacy) {
    # Compatibility ONLY for the explicitly selected legacy state; never discover
    # another state or infer an active account. These are the old environment inputs.
    if (-not $SubscriptionId) { $SubscriptionId = $env:AZURE_SUBSCRIPTION_ID }
    if (-not $TenantId) { $TenantId = $env:AZURE_TENANT_ID }
    if (($Location -and $Location -cne 'westus3') -or $SetName -or $IdentityNamePattern -cne 'mi-azsdk-sample-{resource}-wus3') { throw 'Legacy state has fixed westus3 CI names; generic inputs are not permitted.' }
    $Location = 'westus3'
    $identityGroup = 'rg-azsdk-sample-identities-wus3'; $namePrefix = 'mi-azsdk-sample'
} elseif ($schemaVersion -eq 2) {
    # The old compiler's exact names/parameters are used ONLY for an explicitly
    # selected immutable generation. The shared naming helper never infers legacy.
    if ($previous['setName'] -isnot [string] -or $previous['setName'] -cnotmatch '\A[a-z0-9](?:[a-z0-9-]{0,22}[a-z0-9])?\z' -or
        ($SetName -and $SetName -cne $previous['setName'])) { throw 'Legacy schema 2 set binding differs.' }
    $SetName = $previous['setName']
    $recordedPattern = "mi-azsdk-$SetName-{resource}-$Location"
    if ($PSBoundParameters.ContainsKey('IdentityNamePattern') -and $IdentityNamePattern -cne $recordedPattern) { throw 'Legacy schema 2 MI name pattern binding differs.' }
    $IdentityNamePattern = $recordedPattern
    $identityGroup = "rg-azsdk-identities-$SetName-$Location"; $namePrefix = "mi-azsdk-$SetName"
} else {
    if ($SetName) { throw 'SetName is a legacy verification input; supply an MI name pattern for new generations.' }
}
if ($Location -cnotmatch '\A[a-z][a-z0-9]{0,29}\z') { throw 'Supply an explicit canonical Location independently of the MI name pattern.' }
$naming = Resolve-IdentityNamePattern -IdentityNamePattern $IdentityNamePattern
$IdentityNamePattern = $naming.identityNamePattern
if (-not $readonlyLegacy) {
    $patternHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($IdentityNamePattern))).ToLowerInvariant().Substring(0, 12)
    $identityGroup = "rg-azsdk-identities-$patternHash-$Location"
}
foreach ($guid in @($SubscriptionId, $TenantId, $ExpectedCallerPrincipalId)) { Assert-BootstrapGuid -Value $guid }
if ([bool] $PipelinePrincipalId -ne [bool] $PipelineClientId) { throw 'PipelinePrincipalId and PipelineClientId must be supplied together.' }
if ($legacy -or $PipelinePrincipalId) { foreach ($guid in @($PipelinePrincipalId, $PipelineClientId)) { Assert-BootstrapGuid -Value $guid } }
$subscription = $SubscriptionId.ToLowerInvariant(); $tenant = $TenantId.ToLowerInvariant()
$PipelinePrincipalId = $PipelinePrincipalId.ToLowerInvariant(); $PipelineClientId = $PipelineClientId.ToLowerInvariant(); $ExpectedCallerPrincipalId = $ExpectedCallerPrincipalId.ToLowerInvariant()
$scope = '/subscriptions/' + $subscription; $identityGroupId = "$scope/resourceGroups/$identityGroup"; $expectedIds = @{}
foreach ($purpose in @('project', 'account', 'search', 'function')) { $expectedIds[$purpose] = "$identityGroupId/providers/Microsoft.ManagedIdentity/userAssignedIdentities/$($naming.names[$purpose])" }
$grants = @(Get-BootstrapGrantPlan)
if ($previous) {
    Assert-BootstrapState -State $previous
    if (-not $VerifyOnly -and $previous['status'] -cne 'Previewed') { throw 'A bootstrap attempt is already recorded. Use -VerifyOnly; never reapply, even if the RG is absent.' }
    if (-not $legacy -and $previous['pipelineMode'] -ceq 'Reuse') { $grants[6].roleAssignmentId = $previous['existingPipelineAssignmentId'] }
}
if ($VerifyOnly -and ($null -eq $previous -or $previous['status'] -ceq 'Previewed')) { throw 'Verification requires a recorded bootstrap attempt.' }
if ($Apply -and $null -eq $previous) { throw 'Save and review a separate dry run before using -Apply.' }
$tokenResponse = $null; $privateToken = $null; $claims = $null; $payload = $null; $compiledPath = $null; $script:bootstrapArmHeaders = $null
try {
    $account = Invoke-BootstrapAzure -Arguments @('account', 'show', '--subscription', $subscription) -Sensitive
    if ($account -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $account['id'] -Expected $subscription -IgnoreCase) -or
        -not (Test-BootstrapText -Value $account['tenantId'] -Expected $tenant -IgnoreCase) -or -not (Test-BootstrapText -Value $account['state'] -Expected 'Enabled') -or
        $account['user'] -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $account['user']['type'] -Expected 'user')) { throw 'Use the approved current administrator user in the explicit target tenant/subscription.' }
    $tokenResponse = Invoke-BootstrapAzure -Arguments @('account', 'get-access-token', '--subscription', $subscription, '--resource', 'https://management.azure.com/') -Sensitive
    try {
        $privateToken = $tokenResponse['accessToken']
        if ($privateToken -isnot [string] -or $privateToken.Split('.').Count -ne 3) { throw 'Invalid token.' }
        $payload = $privateToken.Split('.')[1].Replace('-', '+').Replace('_', '/'); $payload = $payload.PadRight($payload.Length + ((4 - $payload.Length % 4) % 4), '=')
        $claims = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($payload)) | ConvertFrom-Json -AsHashtable -ErrorAction Stop
        if ($claims -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $claims['tid'] -Expected $tenant -IgnoreCase) -or
            -not (Test-BootstrapText -Value $claims['oid'] -Expected $ExpectedCallerPrincipalId -IgnoreCase) -or
            $claims['scp'] -isnot [string] -or [string]::IsNullOrWhiteSpace($claims['scp'])) { throw 'Unexpected caller.' }
        $script:bootstrapArmHeaders = @{ Authorization = 'Bearer ' + $privateToken }
    } catch { throw 'Cannot verify the approved bootstrap caller; token suppressed.' }
    finally { $privateToken = $null; $tokenResponse = $null; $claims = $null; $payload = $null }
    if ($PipelinePrincipalId) {
        $application = Invoke-BootstrapAzure -Arguments @('ad', 'sp', 'show', '--id', $PipelinePrincipalId, '--query', '{id:id,appId:appId,accountEnabled:accountEnabled}') -Sensitive
        if ($application -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $application['id'] -Expected $PipelinePrincipalId -IgnoreCase) -or
            -not (Test-BootstrapText -Value $application['appId'] -Expected $PipelineClientId -IgnoreCase) -or $application['accountEnabled'] -isnot [bool] -or
            -not $application['accountEnabled']) { throw 'Cannot verify the approved pipeline service principal.' }
    }
    $exists = Get-BootstrapGroupExists
    if ($exists -and -not $VerifyOnly) { throw 'The identity RG already exists; refusing to adopt, retag, or replay it.' }
    if ($VerifyOnly) {
        if (-not $exists) { throw 'The recorded bootstrap identity RG does not exist; reapply remains forbidden.' }
        $group = Invoke-BootstrapAzure -Arguments @('group', 'show', '--name', $identityGroup, '--subscription', $subscription) -Sensitive
        if ($group -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $group['id'] -Expected $identityGroupId -IgnoreCase) -or
            -not (Test-BootstrapText -Value $group['location'] -Expected $Location) -or $group['tags'] -isnot [System.Collections.IDictionary] -or
            -not (Test-BootstrapText -Value $group['tags']['purpose'] -Expected 'azsdk-sample-identities') -or
            -not (Test-BootstrapText -Value $group['tags']['sample-ci-owner'] -Expected $previous.ownerToken) -or
            -not (Test-BootstrapText -Value $group['tags']['sample-ci-retention'] -Expected 'permanent')) { throw 'The identity RG does not match exact bootstrap ownership.' }
        $outputs = $previous['outputs']
        if (-not $previous.Contains('outputs')) {
            $deploymentId = "$scope/providers/Microsoft.Resources/deployments/$($previous.deploymentName)"
            $recorded = Invoke-BootstrapAzure -Arguments @('rest', '--method', 'get', '--subscription', $subscription, '--url', ('https://management.azure.com{0}?api-version=2022-09-01' -f $deploymentId)) -Sensitive
            if ($recorded -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $recorded['id'] -Expected $deploymentId -IgnoreCase) -or
                -not (Test-BootstrapText -Value $recorded['name'] -Expected $previous.deploymentName) -or
                -not (Test-BootstrapText -Value $recorded['type'] -Expected 'Microsoft.Resources/deployments' -IgnoreCase) -or
                $recorded['properties'] -isnot [System.Collections.IDictionary] -or
                -not (Test-BootstrapText -Value $recorded['properties']['provisioningState'] -Expected 'Succeeded') -or
                ($recorded['properties'].Contains('error') -and $null -ne $recorded['properties']['error'])) { throw 'The recorded deployment has no successful immutable output baseline; no retry is permitted.' }
            $parameters = if ($legacy) { @{ identityResourceGroup = @{ value = $identityGroup }; namePrefix = @{ value = $namePrefix };
                location = @{ value = 'westus3' }; ownerToken = @{ value = $previous.ownerToken }; pipelinePrincipalId = @{ value = $PipelinePrincipalId } } }
                else { $previous['parameters'] }
            Assert-BootstrapEqual -Actual $recorded['properties']['parameters'] -Expected $parameters
            $outputs = $recorded['properties']['outputs']
        }
        $identities = Assert-BootstrapOutputs -Outputs $outputs
        if ($previous.Contains('identities')) { Assert-BootstrapEqual -Actual $previous['identities'] -Expected $identities }
        foreach ($purpose in @('project', 'account', 'search', 'function')) {
            $identity = Invoke-BootstrapAzure -Arguments @('rest', '--method', 'get', '--subscription', $subscription, '--url', ('https://management.azure.com{0}?api-version=2023-01-31' -f $expectedIds[$purpose])) -Sensitive
            if ($identity -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $identity['id'] -Expected $expectedIds[$purpose] -IgnoreCase) -or
                -not (Test-BootstrapText -Value $identity['type'] -Expected 'Microsoft.ManagedIdentity/userAssignedIdentities' -IgnoreCase) -or
                -not (Test-BootstrapText -Value $identity['location'] -Expected $Location) -or $identity['properties'] -isnot [System.Collections.IDictionary] -or
                $identity['tags'] -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $identity['tags']['purpose'] -Expected 'azsdk-sample-identities') -or
                -not (Test-BootstrapText -Value $identity['tags']['sample-ci-owner'] -Expected $previous.ownerToken) -or
                -not (Test-BootstrapText -Value $identity['tags']['sample-ci-retention'] -Expected 'permanent') -or
                -not (Test-BootstrapText -Value $identity['tags']['sample-ci-identity'] -Expected $purpose)) { throw 'An identity does not match exact bootstrap ownership.' }
            foreach ($field in @('principalId', 'clientId', 'tenantId')) {
                Assert-BootstrapGuid -Value $identity['properties'][$field]
                if ($identity['properties'][$field] -ine $identities[$purpose][$field]) { throw 'An immutable identity binding changed; refusing a replacement identity.' }
            }
        }
        $assignments = @(Get-BootstrapAllAssignments -SubscriptionId $subscription)
        foreach ($purpose in @('project', 'account', 'search', 'function')) {
            $owned = @($assignments | Where-Object { $_.properties.principalId -ieq $identities[$purpose].principalId })
            $expectedCount = if ($purpose -ceq 'project') { 6 } else { 0 }
            if ($owned.Count -ne $expectedCount) { throw 'The exact identity grant set differs: project must have six assignments; reserved identities must have zero, including descendants and inherited grants.' }
            if ($purpose -ceq 'project') {
                foreach ($grant in $grants[0..5]) {
                    $matching = @($owned | Where-Object { $_.id -ieq $grant.roleAssignmentId })
                    if ($matching.Count -ne 1) { throw 'An approved project assignment ID is missing or duplicated.' }
                    Assert-BootstrapGrant -Assignment $matching[0] -Grant $grant -PrincipalId $identities.project.principalId
                }
            }
        }
        if ($PipelinePrincipalId) {
            $pipeline = @($assignments | Where-Object { $_.id -ieq $grants[6].roleAssignmentId -or
                ($_.properties.principalId -ieq $PipelinePrincipalId -and $_.properties.scope -ieq $scope -and $_.properties.roleDefinitionId -ieq $grants[6].roleDefinitionId) })
            if ($pipeline.Count -ne 1) { throw 'The exact approved pipeline Foundry User grant is missing or duplicated.' }
            Assert-BootstrapGrant -Assignment $pipeline[0] -Grant $grants[6] -PrincipalId $PipelinePrincipalId
        }
        if (-not $readonlyLegacy) {
            $previous['outputs'] = $outputs; $previous['identities'] = $identities; $previous['status'] = 'Verified'
            Save-BootstrapState -State $previous
        }
        [pscustomobject]@{ status = 'Verified'; legacyStateUnchanged = $readonlyLegacy; subscriptionId = $subscription; tenantId = $tenant; identityNamePattern = $IdentityNamePattern; identities = $identities;
            projectServiceGrants = 6; pipelineFoundryUserGrant = [bool] $PipelinePrincipalId; iamAdministrationGranted = $false } | ConvertTo-Json -Depth 8
        return
    }
    # Only schema-3 preview/apply may compile or validate a region. Never
    # register providers or accept display names / alternate regional fallbacks.
    $locations = Invoke-BootstrapAzure -Arguments @('account', 'list-locations', '--subscription', $subscription) -Sensitive
    if ($locations -isnot [System.Collections.IList] -or @($locations | Where-Object { $_ -is [System.Collections.IDictionary] -and (Test-BootstrapText -Value $_['name'] -Expected $Location) }).Count -ne 1) { throw 'Location is not a canonical region of the explicit subscription.' }
    $provider = Invoke-BootstrapAzure -Arguments @('provider', 'show', '--subscription', $subscription, '--namespace', 'Microsoft.ManagedIdentity', '--query', '{registrationState:registrationState}') -Sensitive
    if ($provider -isnot [System.Collections.IDictionary] -or -not (Test-BootstrapText -Value $provider['registrationState'] -Expected 'Registered')) { throw 'Microsoft.ManagedIdentity must already be registered.' }
    Assert-BootstrapIdentityNamesAbsent
    . (Join-Path $PSScriptRoot 'BootstrapTemplateContract.ps1')
    $compiled = Invoke-BootstrapAzure -Arguments @('bicep', 'build', '--file', (Join-Path $PSScriptRoot '../infra/bootstrap.bicep'), '--stdout') -Sensitive
    Assert-BootstrapTemplate -Compiled $compiled
    $compiledText = ConvertTo-BootstrapCanonicalValue -Value $compiled | ConvertTo-Json -Depth 100 -Compress
    $templateHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($compiledText))).ToLowerInvariant()
    if ($previous -and $previous['templateHash'] -cne $templateHash) { throw 'The compiled template changed after preview; a new reviewed dry run is required.' }
    $compiledPath = [IO.Path]::GetTempFileName(); [IO.File]::WriteAllText($compiledPath, $compiledText, [Text.UTF8Encoding]::new($false))
    $existingPipelineId = Get-BootstrapExistingPipelineGrant -Assignments @(Get-BootstrapAllAssignments -SubscriptionId $subscription)
    $pipelineMode = if (-not $PipelinePrincipalId) { 'None' } elseif ($existingPipelineId) { 'Reuse' } else { 'Create' }
    $pipelineGrantExists = $pipelineMode -ceq 'Reuse'
    if ($pipelineGrantExists) { $grants[6].roleAssignmentId = $existingPipelineId }
    $assignmentId = if ($PipelinePrincipalId) { $grants[6].roleAssignmentId } else { '' }
    $ownerToken = if ($previous) { $previous.ownerToken } else { [guid]::NewGuid().ToString('N') }
    $deploymentName = 'azsdk-identities-' + $ownerToken.Substring(0, 12)
    $parameters = Get-BootstrapParameters -OwnerToken $ownerToken -PipelineMode $pipelineMode -AssignmentId $assignmentId
    if ($previous) {
        Assert-BootstrapEqual -Actual $pipelineMode -Expected $previous['pipelineMode']
        Assert-BootstrapEqual -Actual $existingPipelineId -Expected $previous['existingPipelineAssignmentId']
        Assert-BootstrapEqual -Actual $parameters -Expected $previous['parameters']
    }
    $arguments = @('--name', $deploymentName, '--location', $Location, '--subscription', $subscription, '--template-file', $compiledPath, '--parameters')
    foreach ($name in @($parameters.Keys | Sort-Object -CaseSensitive)) {
        $value = $parameters[$name]['value']; if ($value -is [bool]) { $value = $value.ToString().ToLowerInvariant() }
        $arguments += "$name=$value"
    }
    $validation = Invoke-BootstrapAzure -Arguments (@('deployment', 'sub', 'validate') + $arguments) -Sensitive
    Assert-BootstrapValidation -Validation $validation
    $prediction = Invoke-BootstrapAzure -Arguments (@('deployment', 'sub', 'what-if') + $arguments + @('--no-pretty-print', '--result-format', 'FullResourcePayloads')) -Sensitive
    Assert-BootstrapPrediction -Prediction $prediction -Validation $validation -PipelineGrantExists $pipelineGrantExists
    if ($previous) { Assert-BootstrapEqual -Actual $prediction -Expected $previous['prediction'] }
    $state = @{ schemaVersion = 3; status = 'Previewed'; subscriptionId = $subscription; tenantId = $tenant; location = $Location; identityNamePattern = $IdentityNamePattern;
        identityResourceGroup = $identityGroup; ownerToken = $ownerToken; pipelinePrincipalId = $PipelinePrincipalId; pipelineClientId = $PipelineClientId;
        expectedCallerPrincipalId = $ExpectedCallerPrincipalId; deploymentName = $deploymentName; identityResourceIds = $expectedIds; templateHash = $templateHash;
        pipelineMode = $pipelineMode; existingPipelineAssignmentId = $existingPipelineId; parameters = $parameters; prediction = $prediction;
        validation = $(if ($previous) { $previous['validation'] } else { $validation }) }
    Save-BootstrapState -State $state
    [pscustomobject]@{ mode = 'DRY RUN'; subscriptionId = $subscription; tenantId = $tenant; location = $Location; identityNamePattern = $IdentityNamePattern;
        identityResourceGroup = $identityGroup; identities = $expectedIds; pipelineMode = $pipelineMode; parameters = $parameters; templateHash = $templateHash;
        changes = @($prediction['changes'] | ForEach-Object { @{ resourceId = $_.resourceId; type = $_['after']['type']; changeType = $_.changeType } });
        note = 'New RG, four UAMIs, six project service grants and optional pipeline Foundry User only; reuse is GET-only. No IAM administration, deletes, repairs or workloads.' } | ConvertTo-Json -Depth 10
    # Explicit human approval of this exact saved plan is an agent-level gate;
    # -Apply alone cannot manufacture a separate Previewed state.
    if (-not $Apply -or -not $PSCmdlet.ShouldProcess($scope, 'Create four permanent UAMIs and the exact reviewed service-role grants')) { return }
    if (Get-BootstrapGroupExists) { throw 'The identity RG appeared after preview; no create attempted.' }
    Assert-BootstrapIdentityNamesAbsent
    $latestPipelineId = Get-BootstrapExistingPipelineGrant -Assignments @(Get-BootstrapAllAssignments -SubscriptionId $subscription)
    if ($latestPipelineId -cne $existingPipelineId) { throw 'The pipeline grant changed after preview; no create attempted.' }
    $state['status'] = 'Applying'; Save-BootstrapState -State $state
    try {
        $created = Invoke-BootstrapAzure -Arguments (@('deployment', 'sub', 'create') + $arguments) -Sensitive
        if ($created -isnot [System.Collections.IDictionary] -or $created['properties'] -isnot [System.Collections.IDictionary] -or
            -not (Test-BootstrapText -Value $created['properties']['provisioningState'] -Expected 'Succeeded') -or
            ($created['properties'].Contains('error') -and $null -ne $created['properties']['error'])) { throw 'Bootstrap deployment did not succeed; reconcile the recorded attempt.' }
        $null = Assert-BootstrapOutputs -Outputs $created['properties']['outputs']
        $state['outputs'] = $created['properties']['outputs']; $state['status'] = 'Created'
    } catch { $state['status'] = 'Failed'; throw }
    finally { Save-BootstrapState -State $state }
    Write-Host 'Bootstrap deployment completed. Use -VerifyOnly; no reapply or automatic deletion is permitted.'
} finally {
    $script:bootstrapArmHeaders = $null; $privateToken = $null; $tokenResponse = $null; $claims = $null; $payload = $null
    if ($compiledPath -and [IO.File]::Exists($compiledPath)) { [IO.File]::Delete($compiledPath) }
}