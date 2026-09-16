[CmdletBinding()]
param(
    [string]$PackageRoot = (Split-Path -Parent $PSScriptRoot)
)

$utilsFile = Join-Path $PackageRoot 'azure\ai\projects\_utils\utils.py'
$utilsContent = Get-Content $utilsFile -Raw
if ($utilsContent -notmatch '(?m)^from azure\.core import MatchConditions\r?$') {
    $matchConditionsImport = @('', 'from azure.core import MatchConditions', '') -join [Environment]::NewLine
    $utilsContent = $utilsContent -replace '(?m)^(from typing import[^\r\n]+\r?\n)', ('$1' + $matchConditionsImport)
}

$etagHelperNames = 'quote_etag', 'prep_if_match', 'prep_if_none_match'
$existingEtagHelperCount = 0
foreach ($helperName in $etagHelperNames) {
    if ($utilsContent -match "(?m)^def $helperName\(") {
        $existingEtagHelperCount++
    }
}
if ($existingEtagHelperCount -ne 0 -and $existingEtagHelperCount -ne $etagHelperNames.Count) {
    throw "Expected all generated ETag helpers or none, but found $existingEtagHelperCount of $($etagHelperNames.Count)."
}
if ($existingEtagHelperCount -eq 0) {
    $etagHelpers = @'
def quote_etag(etag: Optional[str]) -> Optional[str]:
    if not etag or etag == "*":
        return etag
    if etag.startswith("W/"):
        return etag
    if etag.startswith('"') and etag.endswith('"'):
        return etag
    if etag.startswith("'") and etag.endswith("'"):
        return etag
    return '"' + etag + '"'


def prep_if_match(etag: Optional[str], match_condition: Optional[MatchConditions]) -> Optional[str]:
    if match_condition == MatchConditions.IfNotModified:
        if_match = quote_etag(etag) if etag else None
        return if_match
    if match_condition == MatchConditions.IfPresent:
        return "*"
    return None


def prep_if_none_match(etag: Optional[str], match_condition: Optional[MatchConditions]) -> Optional[str]:
    if match_condition == MatchConditions.IfModified:
        if_none_match = quote_etag(etag) if etag else None
        return if_none_match
    if match_condition == MatchConditions.IfMissing:
        return "*"
    return None
'@
    $helperAnchor = '# file-like tuple could be'
    if ($utilsContent -notmatch [regex]::Escape($helperAnchor)) {
        throw "Could not find the ETag helper insertion point in $utilsFile."
    }
    $utilsContent = $utilsContent.Replace($helperAnchor, $etagHelpers + "`r`n`r`n" + $helperAnchor)
}
Set-Content $utilsFile $utilsContent -NoNewline

$operationFiles = @(
    @{
        Path = (Join-Path $PackageRoot 'azure\ai\projects\operations\_operations.py')
        IsAsync = $false
        ExpectedSignatures = 14
    },
    @{
        Path = (Join-Path $PackageRoot 'azure\ai\projects\aio\operations\_operations.py')
        IsAsync = $true
        ExpectedSignatures = 10
    }
)
foreach ($operationFile in $operationFiles) {
    $f = $operationFile.Path
    $c = Get-Content $f -Raw
    if ($operationFile.IsAsync) {
        $c = $c -replace 'from azure\.core import AsyncPipelineClient', 'from azure.core import AsyncPipelineClient, MatchConditions'
    }
    else {
        $c = $c -replace 'from azure\.core import PipelineClient', 'from azure.core import MatchConditions, PipelineClient'
        $c = $c -replace 'from \.\._utils\.utils import prepare_multipart_form_data', 'from .._utils.utils import prep_if_match, prep_if_none_match, prepare_multipart_form_data'
    }

    $c = [regex]::Replace(
        $c,
        'etag: str,(?!\s*match_condition:)',
        'etag: str, match_condition: MatchConditions = MatchConditions.IfNotModified,'
    )

    $lines = $c -split '\r?\n'
    $out = [System.Collections.Generic.List[string]]::new()
    for ($i = 0; $i -lt $lines.Length; $i++) {
        $line = $lines[$i]
        $out.Add($line)
        if ($line.Trim() -eq 'etag=etag,') {
            $nextLine = if ($i + 1 -lt $lines.Length) { $lines[$i + 1].Trim() } else { '' }
            if ($nextLine -ne 'match_condition=match_condition,') {
                $indent = ([regex]::Match($line, '^\s*')).Value
                $out.Add($indent + 'match_condition=match_condition,')
            }
        }
        if ($line.Trim() -eq ':paramtype etag: str') {
            $nextLine = if ($i + 1 -lt $lines.Length) { $lines[$i + 1].Trim() } else { '' }
            if ($nextLine -notmatch '^:keyword match_condition:') {
                $indent = ([regex]::Match($line, '^\s*')).Value
                $out.Add($indent + ':keyword match_condition: The match condition to use upon the etag. Default value is')
                $out.Add($indent + ' MatchConditions.IfNotModified.')
                $out.Add($indent + ':paramtype match_condition: ~azure.core.MatchConditions')
            }
        }
    }
    $c = $out -join "`r`n"

    $signatureCount = [regex]::Matches(
        $c,
        'match_condition: MatchConditions = MatchConditions\.IfNotModified'
    ).Count
    $argumentCount = [regex]::Matches($c, '(?m)^\s*match_condition=match_condition,\r?$').Count
    $docCount = [regex]::Matches($c, '(?m)^\s*:paramtype match_condition: ~azure\.core\.MatchConditions\r?$').Count
    if ($signatureCount -ne $operationFile.ExpectedSignatures -or $argumentCount -ne 4 -or $docCount -ne 10) {
        throw "Unexpected MatchConditions patch counts in ${f}: $signatureCount signatures, $argumentCount arguments, and $docCount docstrings."
    }
    Set-Content $f $c -NoNewline
}

$syncOperationsFile = Join-Path $PackageRoot 'azure\ai\projects\operations\_operations.py'
$syncOperations = Get-Content $syncOperationsFile -Raw
$ifMatchCount = [regex]::Matches($syncOperations, 'if_match = prep_if_match\(etag, match_condition\)').Count
if ($ifMatchCount -ne 4) {
    throw "Expected 4 generated prep_if_match blocks, but found $ifMatchCount."
}