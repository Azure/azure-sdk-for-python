<#
PostEmitter.ps1

Runs automatically after the TypeSpec code generation for
azure-mgmt-mysqlflexibleservers (see eng/tools/azure-sdk-tools/packaging_tools/
sdk_generator.py -> run_post_emitter_script).

Why this script exists
----------------------
In the swagger-based SDK, several LROs carried an explicit
`x-ms-long-running-operation-options` (final-state-via) that autorest turned
into `lro_options={'final-state-via': ...}` on the poller. The
http-client-python emitter does NOT emit `lro_options` at all, so after the
TypeSpec migration every generated LRO gets `_lro_options = None`, which breaks
tests/test_unit_compatibility.py for the operations that must keep their
original final-state-via.

This script re-injects the required `lro_options` into the generated
`ARMPolling(...)` / `AsyncARMPolling(...)` calls so the generated SDK stays
compatible with the previously released swagger-based SDK.

Operations that must stay `None` (the swagger directive deleted their options,
and the emitter already produces `None`) are intentionally left untouched.

To run manually:
  powershell -ExecutionPolicy Bypass -File PostEmitter.ps1
#>

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

# (OperationClass, begin-method) -> final-state-via value that the swagger SDK used.
$targets = @{
    'AdvancedThreatProtectionSettingsOperations::begin_update'     = 'location'
    'AdvancedThreatProtectionSettingsOperations::begin_update_put' = 'location'
    'AzureADAdministratorsOperations::begin_delete'                = 'location'
    'BackupAndExportOperations::begin_create'                      = 'location'
    'ConfigurationsOperations::begin_batch_update'                 = 'azure-async-operation'
    'LongRunningBackupOperations::begin_create'                    = 'azure-async-operation'
    'ServersMigrationOperations::begin_cutover_migration'          = 'azure-async-operation'
    'ServersOperations::begin_delete'                              = 'azure-async-operation'
    'ServersOperations::begin_detach_v_net'                        = 'azure-async-operation'
    'ServersOperations::begin_reset_gtid'                          = 'azure-async-operation'
}

$files = @(
    'azure\mgmt\mysqlflexibleservers\operations\_operations.py',
    'azure\mgmt\mysqlflexibleservers\aio\operations\_operations.py'
)

# One poller site is expected per targeted operation, in each of the two files.
$expected = $targets.Count * $files.Count
$totalInjected = 0

foreach ($rel in $files) {
    $path = Join-Path $root $rel
    if (-not (Test-Path -LiteralPath $path)) {
        throw "[PostEmitter] Generated file not found: $path"
    }

    $lines = Get-Content -LiteralPath $path
    $currentClass = ''
    $currentMethod = ''
    $resolved = 0

    for ($i = 0; $i -lt $lines.Length; $i++) {
        $line = $lines[$i]

        $mClass = [regex]::Match($line, '^class (\w+)')
        if ($mClass.Success) {
            $currentClass = $mClass.Groups[1].Value
            $currentMethod = ''
            continue
        }

        $mDef = [regex]::Match($line, '^\s*(?:async\s+)?def (begin_\w+)\s*\(')
        if ($mDef.Success) {
            $currentMethod = $mDef.Groups[1].Value
        }

        # Matches both `ARMPolling(...` and `AsyncARMPolling(...`, whether the call
        # is on one line (fresh generation) or already wrapped by black (re-run).
        if ($line -match 'ARMPolling\(') {
            $key = "$currentClass::$currentMethod"
            if ($targets.ContainsKey($key)) {
                $value = $targets[$key]
                # Only the fresh, single-line form needs injecting; an already
                # patched (black-wrapped) site is just counted as resolved.
                if ($line -match 'ARMPolling\(lro_delay, ' -and $line -notmatch 'lro_options=') {
                    $lines[$i] = $line -replace 'ARMPolling\(lro_delay, ', ("ARMPolling(lro_delay, lro_options={'final-state-via': '" + $value + "'}, ")
                }
                $resolved++
            }
        }
    }

    Set-Content -LiteralPath $path -Value $lines
    Write-Output "[PostEmitter] $rel : $resolved lro_options sites resolved"
    $totalInjected += $resolved
}

Write-Output "[PostEmitter] total resolved: $totalInjected (expected $expected)"
if ($totalInjected -ne $expected) {
    throw "[PostEmitter] Expected $expected targeted poller sites but found $totalInjected. The generated code shape may have changed."
}

# Re-format the files we edited so the injected (long) ARMPolling lines match
# the repo's formatting (line length 120). `python -m black` runs the Black
# installed in this interpreter's environment (no dependence on PATH/Scripts).
& python -m black --version *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Output "[PostEmitter] black not found; installing it with pip"
    & python -m pip install black -q
    if ($LASTEXITCODE -ne 0) {
        throw "[PostEmitter] Failed to install black"
    }
}
foreach ($rel in $files) {
    $path = Join-Path $root $rel
    Write-Output "[PostEmitter] formatting $rel with black"
    & python -m black $path -l 120
    if ($LASTEXITCODE -ne 0) {
        throw "[PostEmitter] black failed to format $path (exit code $LASTEXITCODE)"
    }
}
