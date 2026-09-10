#
# To emit from TypeSpec, run this in the current folder: 
#
#  tsp-client update --debug  ==> to use the commit mentioned in the local tsp-location.yaml to generate
#  tsp-client update --debug --save-inputs"  ==> To save the local folder TempTypeSpecFiles
#  tsp-client update --debug --local-spec-repo <path>" ==> to use your local TypeSpec folder. Path is like:
#       D:\src\azure-rest-api-specs\specification\ai-foundry\data-plane\Foundry\src\sdk-python-js-azure-ai-projects
#
# Then run this script to "fix" the emitted code:
#  powershell -ExecutionPolicy Bypass -File PostEmitter.ps1
#

# Revert emitted pyprojects.toml, since it overrides the following changes:
# - We added "Programming Language :: Python :: 3.14". The emitter removes it.
# - The emitter uses lower case "i" in "Ai". I want to keep it upper case in the description field: "Microsoft Corporation Azure AI Projects Client Library for Python".
# - We want a vanity link for the "repository" value, deep linking to the SDK folder (not root of repo): https://aka.ms/azsdk/azure-ai-projects-v2/python/code
# See GitHub issue: https://github.com/microsoft/typespec/issues/10311
git restore pyproject.toml

# Revert emitted MANIFEST.in, since it overrides changes I need to get the dist package (*.tar.gz) with required files.
# I would like to keep these two lines, since I have test and sample data files I need:
#   recursive-include tests *
#   recursive-include samples *
# But the emitter keeps changing it back to only include *.py and *.md files:
#   recursive-include tests *.py
#   recursive-include samples *.py *.md
git restore MANIFEST.in

# Force streaming in get_session_log_stream for both sync and async operations.
$files = 'azure\ai\projects\operations\_operations.py', 'azure\ai\projects\aio\operations\_operations.py'
foreach ($f in $files) {
    $lines = Get-Content $f
    $inFunc = $false
    for ($i = 0; $i -lt $lines.Length; $i++) {
        if ($lines[$i] -match '^\s*(async\s+)?def\s+get_session_log_stream\(') {
            $inFunc = $true
            continue
        }
        if ($inFunc -and $lines[$i] -match '^\s*(async\s+)?def\s+\w+\(') {
            $inFunc = $false
        }
        if ($inFunc -and $lines[$i] -match 'kwargs\.pop\(.+stream.+False\)') {
            $indent = ([regex]::Match($lines[$i], '^\s*')).Value
            $lines[$i] = $indent + '_stream = True'
        }
    }
    Set-Content $f $lines
}

# Fix Sphinx docutils warnings in class SessionLogEvent: the generated docstring wraps two long
# ``data:`` JSON lines mid-string inside a ``.. code-block::`` section. The wrapped continuation
# lines have wrong indentation (4 spaces instead of 7), causing "unexpected unindent" warnings.
# Join each broken pair back into one line.
$f = 'azure\ai\projects\models\_models.py'
$c = Get-Content $f -Raw
$c = $c -replace '(Starting server)\r?\n[ \t]+(on port 18080)', '$1 $2'
$c = $c -replace '(Successfully)\r?\n[ \t]+(connected to container\"})\.?', '$1 $2'
Set-Content $f $c -NoNewline
$lines = Get-Content $f
$out = @()
foreach ($line in $lines) {
    if ($line -match '^\s*on port 18080' -and $line -notmatch 'data:') { continue }
    if ($line -match '^\s*connected to container' -and $line -notmatch 'data:') { continue }
    if ($line -match '^\s*data: .*2026-03-10T09:33:17.121Z') {
        $out += ('       ' + $line.TrimStart())
        continue
    }
    if ($line -match '^\s*data: .*2026-03-10T09:34:52.714Z') {
        $out += ('       ' + $line.TrimStart())
        continue
    }
    $out += $line
}
Set-Content $f $out

# Normalize generated reStructuredText bullet lists in model and enum docstrings.
# Join wrapped list text while preserving blank separators and closing docstring delimiters.
$files = 'azure\ai\projects\models\_models.py', 'azure\ai\projects\models\_enums.py'
foreach ($f in $files) {
    $lines = Get-Content $f
    $out = @()
    $inDocstring = $false
    $inBulletList = $false
    for ($i = 0; $i -lt $lines.Length; $i++) {
        $line = $lines[$i]
        $trimmed = $line.TrimStart()
        $quoteCount = ([regex]::Matches($line, '"""')).Count
        $isClosingQuote = $trimmed -eq '"""'
        $isContinuation = $trimmed -match '^[a-z0-9`(]'
        if ($inDocstring -and $inBulletList -and $isContinuation -and $line -match '^\s{4}\S') {
            while ($out.Count -gt 0 -and -not $out[-1].Trim()) { $out = $out[0..($out.Count - 2)] }
            if ($out.Count -gt 0) {
                $out[-1] = $out[-1].TrimEnd() + ' ' + $trimmed
                continue
            }
        }
        if ($inDocstring -and $inBulletList -and $trimmed -match '^\:') {
            if ($out.Count -gt 0 -and $out[-1].Trim()) { $out += '' }
            $inBulletList = $false
        }
        $out += $line
        if ($trimmed -match '^\*\s') { $inBulletList = $true }
        if ($quoteCount % 2 -eq 1 -and -not $isClosingQuote) { $inDocstring = -not $inDocstring }
        if ($isClosingQuote) { $inDocstring = $false; $inBulletList = $false }
    }
    Set-Content $f $out
}

# Fix Sphinx docutils warnings in get_session_log_stream docstrings (sync + async).
# The emitter wraps bullet/code-block lines with insufficient indentation.
$files = 'azure\ai\projects\operations\_operations.py', 'azure\ai\projects\aio\operations\_operations.py'
foreach ($f in $files) {
    $c = Get-Content $f -Raw
    $c = $c -replace 'schema\r?\n\s+is not contractual and may include additional keys or change format\r?\n\s+over time [^\r\n]*clients should treat it as an opaque string\)', 'schema is not contractual and may include additional keys or change format over time; clients should treat it as an opaque string)'
    $c = $c -replace '(message\":\"Starting)\r?\n\s+(FoundryCBAgent server on port 8088\"})', '$1 $2'
    $c = $c -replace '(message\":\"INFO: Application)\r?\n\s+(startup complete\.\"})', '$1 $2'
    $c = $c -replace '(message\":\"Successfully)\r?\n\s+(connected to container\"})', '$1 $2'
    $c = $c -replace '(message\":\"No logs since)\r?\n\s+(last 60 seconds\"})', '$1 $2'
    Set-Content $f $c -NoNewline
}

# Wrap forward-reference-only aliases in Union so they are valid runtime type aliases.
$f = 'azure\ai\projects\_unions.py'
$c = Get-Content $f -Raw
$c = $c -replace '(?m)^([A-Za-z_][A-Za-z0-9_]*\s*=\s*)"([^"\r\n]+)"\s*$', '$1Union["$2"]'
# Remove the duplicate VoiceAgentToolChoice alias emitted by some TypeSpec versions.
$duplicateVoiceAgentToolChoice = '(?ms)\r?\nVoiceAgentToolChoice = Union\[\r?\n    Literal\["none"\], Literal\["auto"\], Literal\["required"\], "_models\.ToolChoiceFunction", "_models\.ToolChoiceMCP"\r?\n\]'
$firstVoiceAgentToolChoice = [regex]::Match($c, $duplicateVoiceAgentToolChoice)
if ($firstVoiceAgentToolChoice.Success) {
    $secondStart = $firstVoiceAgentToolChoice.Index + $firstVoiceAgentToolChoice.Length
    $second = [regex]::Match($c.Substring($secondStart), $duplicateVoiceAgentToolChoice)
    if ($second.Success) {
        $removeStart = $secondStart + $second.Index
        $c = $c.Remove($removeStart, $second.Length)
    }
}
Set-Content $f $c -NoNewline

# Remove invalid single overload stubs for BetaAgentsOperations.generate.
$files = 'azure\ai\projects\operations\_operations.py', 'azure\ai\projects\aio\operations\_operations.py'
foreach ($f in $files) {
    $c = Get-Content $f -Raw
    $c = $c -replace '(?ms)\r?\n    @overload\r?\n    (?:async )?def generate\(\r?\n        self, body: _models\.GenerateVoiceAgentRequest, \*, content_type: str = "application/json", \*\*kwargs: Any\r?\n    \) -> _models\.AgentDetails:\r?\n        """Generate an agent\..*?        """\r?\n\r?\n(?=    @distributed_trace)', "`r`n"
    $c = $c -replace '(?ms)\r?\n    @overload\r?\n    async def generate\(\r?\n        self, body: _models\.GenerateVoiceAgentRequest, \*, content_type: str = "application/json", \*\*kwargs: Any\r?\n    \) -> _models\.AgentDetails:\r?\n        """Generate an agent\..*?        """\r?\n\r?\n(?=    @distributed_trace_async)', "`r`n"
    Set-Content $f $c -NoNewline
}

# Fix generated If-Match headers for TypeSpec Azure.Core.eTag parameters.
# The emitter generates prep_if_match(etag, match_condition), but this package's
# public methods expose only the etag keyword and do not emit the helper/import.
$f = 'azure\ai\projects\operations\_operations.py'
$lines = Get-Content $f
$matchCount = 0
for ($i = 0; $i -lt $lines.Length - 2; $i++) {
    if (
        $lines[$i].Trim() -eq 'if_match = prep_if_match(etag, match_condition)' -and
        $lines[$i + 1].Trim() -eq 'if if_match is not None:' -and
        $lines[$i + 2].Trim() -eq '_headers["If-Match"] = _SERIALIZER.header("if_match", if_match, "str")'
    ) {
        $indent = ([regex]::Match($lines[$i], '^\s*')).Value
        $lines[$i] = $indent + 'if etag is not None:'
        $lines[$i + 1] = $indent + '    _headers["If-Match"] = _SERIALIZER.header("if_match", etag, "str")'
        $lines[$i + 2] = ''
        $matchCount++
        $i += 2
    }
}
if ($matchCount -ne 4) {
    throw "Expected to repair 4 generated If-Match blocks, but repaired $matchCount."
}
Set-Content $f $lines

# Finishing by running 'black' tool to format code. 
pip install black
black --config ../../../eng/black-pyproject.toml .

# Regenerate API review artifacts and the public method inventory.
azpysdk apistub .
$apiStubExitCode = $LASTEXITCODE
.\GeneratePublicMethods.ps1
if ($apiStubExitCode -ne 0) {
    throw "API stub generation failed with exit code $apiStubExitCode."
}
