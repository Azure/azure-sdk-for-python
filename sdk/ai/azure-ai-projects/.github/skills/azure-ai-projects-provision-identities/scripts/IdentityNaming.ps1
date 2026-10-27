# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#Requires -Version 7.2

# Pure naming contract shared by bootstrap and live-test planning. No Azure calls,
# state discovery or expression evaluation belong in placeholder expansion.
function Resolve-IdentityNamePattern {
    param([AllowNull()] [AllowEmptyString()] [string] $IdentityNamePattern)

    if ([regex]::Matches([string] $IdentityNamePattern, '\{resource\}').Count -ne 1) {
        throw 'The MI name pattern must contain exactly one literal {resource} placeholder.'
    }
    $names = @{}
    foreach ($purpose in @('project', 'account', 'search', 'function')) {
        $names[$purpose] = $IdentityNamePattern.Replace('{resource}', $purpose)
        if ($names[$purpose] -cnotmatch '\A[A-Za-z0-9][A-Za-z0-9_-]{2,127}\z') {
            throw 'The MI name pattern must expand to valid 3-128 character Azure MI names using letters, digits, hyphens or underscores.'
        }
    }
    # Prefix/suffix, resource group and location have no naming convention.
    # Location is explicit for bootstrap and comes from Azure metadata for tests.
    return @{ identityNamePattern = $IdentityNamePattern; names = $names }
}

function ConvertTo-IdentityNamePattern {
    param([AllowNull()] [AllowEmptyString()] [string] $ProjectIdentityName)

    # Compatibility only for previously saved plans with a concrete project name.
    # Anchor the role at the end so a set name containing '-project-' is preserved.
    $pattern = [regex]::Replace([string] $ProjectIdentityName, '-project-(?<region>[a-z][a-z0-9]{0,29})\z', '-{resource}-${region}')
    $resolved = Resolve-IdentityNamePattern -IdentityNamePattern $pattern
    if ($resolved.names.project -cne $ProjectIdentityName) { throw 'Saved project MI name differs from its identity pattern.' }
    return $resolved.identityNamePattern
}