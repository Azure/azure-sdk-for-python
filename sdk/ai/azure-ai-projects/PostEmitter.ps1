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
$c = Get-Content $f -Raw
$c = $c -replace '    if_match = prep_if_match\(etag, match_condition\)\r?\n    if if_match is not None:\r?\n        _headers\["If-Match"\] = _SERIALIZER\.header\("if_match", if_match, "str"\)', "    if etag is not None:`r`n        _headers[`"If-Match`"] = _SERIALIZER.header(`"if_match`", etag, `"str`")"
Set-Content $f $c -NoNewline

# Regression guard: `_realtime.py` and `aio\_realtime.py` are hand-written files that are NOT
# `_patch.py`-named, so they aren't covered by the emitter's own "never touch _patch.py" guarantee --
# nothing in the TypeSpec emitter is aware these files exist. They carry the SDK client-identification
# fix ported from the azure-ai-voicelive PR #48848 (a User-Agent header and x-ms-client-sdk query
# parameter, both derived from `_USER_AGENT = UserAgentPolicy(sdk_moniker=...)`, with a case-insensitive
# guard so a caller-supplied extra_headers User-Agent of any casing is honored instead of duplicated).
# If a future `tsp-client update` ever starts generating (and thus silently overwriting) a file at either
# of these paths, this fix would be lost with no other signal until someone happens to run the realtime
# test suite. Fail the emit step immediately instead, right after regeneration, rather than relying on
# that eventual test run.
$realtimeFiles = @('azure\ai\projects\_realtime.py', 'azure\ai\projects\aio\_realtime.py')
foreach ($f in $realtimeFiles) {
    if (-not (Test-Path $f)) {
        throw "PostEmitter safety check failed: '$f' is missing. This hand-written file (not tracked by the TypeSpec emitter) carries the SDK client-identification fix from PR #48848; if the emitter deleted or renamed it, restore it from git history before continuing."
    }
    $c = Get-Content $f -Raw
    if ($c -notmatch 'UserAgentPolicy\(sdk_moniker=') {
        throw "PostEmitter safety check failed: '$f' no longer defines _USER_AGENT via UserAgentPolicy(sdk_moniker=...). The SDK client-identification fix from PR #48848 appears to have been overwritten -- reinstate the User-Agent header + x-ms-client-sdk query param wiring."
    }
    if ($c -notmatch '_has_header_case_insensitive') {
        throw "PostEmitter safety check failed: '$f' no longer guards the User-Agent header with _has_header_case_insensitive. A caller-supplied extra_headers User-Agent (in any casing) would be duplicated instead of honored -- reinstate the case-insensitive check."
    }
    if ($c -notmatch 'x-ms-client-sdk') {
        throw "PostEmitter safety check failed: '$f' no longer sends the x-ms-client-sdk query parameter alongside the User-Agent header -- reinstate it so service telemetry can still attribute traffic on paths that don't forward the header."
    }
}
Write-Host "PostEmitter safety check passed: SDK client-identification fix (PR #48848) is intact in both _realtime.py files."

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
