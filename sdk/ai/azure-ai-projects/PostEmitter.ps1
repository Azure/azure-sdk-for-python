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

# A block of code in the implementation of "list_memories", in both sync 
# and async _operations.py files, needs to be moved up. It's emitted in the wrong place,
# in the inline function named "prepare_request". Instead it should be moved up into the
# main body of the "list_memories" method, right after the line `error_map.update(kwargs.pop("error_map", {}) or {})`.
# If you don't do this, the PR pipeline will show failures in Pyright (`error: "body" is unbound (reportUnboundVariable)`)
# and some tests will fail. This is the block of code that needs to move up:
#            if body is _Unset:
#                if scope is _Unset:
#                    raise TypeError("missing required argument: scope")
#                body = {"scope": scope}
#                body = {k: v for k, v in body.items() if v is not None}
# The block inside prepare_request has 12-space indentation; after moving to the main function body it needs 8-space indentation.
# Strategy: Find the last list_memories method, then do a targeted string replacement that moves the block right after error_map.update.
$oldPattern = @"
        error_map.update(kwargs.pop("error_map", {}) or {})
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        def prepare_request(_continuation_token=None):
            if body is _Unset:
                if scope is _Unset:
                    raise TypeError("missing required argument: scope")
                body = {"scope": scope}
                body = {k: v for k, v in body.items() if v is not None}

            _request = build_beta_memory_stores_list_memories_request(
"@
$newPattern = @"
        error_map.update(kwargs.pop("error_map", {}) or {})
        if body is _Unset:
            if scope is _Unset:
                raise TypeError("missing required argument: scope")
            body = {"scope": scope}
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        def prepare_request(_continuation_token=None):
            _request = build_beta_memory_stores_list_memories_request(
"@
$files = 'azure\ai\projects\operations\_operations.py', 'azure\ai\projects\aio\operations\_operations.py'
foreach ($f in $files) {
    $c = Get-Content $f -Raw
    # Find all occurrences of "def list_memories(" and get the index of the last one
    $methodMatches = [regex]::Matches($c, 'def list_memories\(')
    if ($methodMatches.Count -eq 0) { continue }
    $lastMethodStart = $methodMatches[$methodMatches.Count - 1].Index
    
    # Find the pattern to replace - first occurrence after the last list_memories method
    $patternEscaped = [regex]::Escape($oldPattern)
    $patternMatches = [regex]::Matches($c, $patternEscaped)
    $matchToReplace = $null
    foreach ($m in $patternMatches) {
        if ($m.Index -gt $lastMethodStart) {
            $matchToReplace = $m
            break
        }
    }
    if ($matchToReplace -eq $null) { continue }
    
    # Replace only that specific occurrence
    $c = $c.Substring(0, $matchToReplace.Index) + $newPattern + $c.Substring($matchToReplace.Index + $matchToReplace.Length)
    
    Set-Content $f $c -NoNewline
}


# Fix pyright reportIncompatibleVariableOverride errors: VoiceResponse narrows the inherited
# optional `id`/`conversation_id` fields (from OmitPropertiesRealtimeResponse) to required `str`,
# which pyright flags as an incompatible override since the base type is `Optional[str]`. This is
# an intentional, spec-driven narrowing (the fields are always present on a persisted voice
# response), so silence the two specific lines rather than widen the type.
$f = 'azure\ai\projects\models\_models.py'
$lines = Get-Content $f
$inVoiceResponse = $false
for ($i = 0; $i -lt $lines.Length; $i++) {
    if ($lines[$i] -match '^class VoiceResponse\(OmitPropertiesRealtimeResponse\)') {
        $inVoiceResponse = $true
        continue
    }
    if ($inVoiceResponse -and $lines[$i] -match '^class \w+') {
        $inVoiceResponse = $false
    }
    if ($inVoiceResponse -and $lines[$i] -match '^\s*id: str = rest_field\(' -and $lines[$i] -notmatch '# type: ignore') {
        $lines[$i] = $lines[$i] + '  # type: ignore[reportIncompatibleVariableOverride]'
    }
    if ($inVoiceResponse -and $lines[$i] -match '^\s*conversation_id: str = rest_field\(' -and $lines[$i] -notmatch '# type: ignore') {
        $lines[$i] = $lines[$i] + '  # type: ignore[reportIncompatibleVariableOverride]'
    }
}
Set-Content $f $lines

# Fix pyright errors on generate_agent caused by a known typespec-python emitter bug: when a
# discriminated union has exactly one member, the emitter emits `GenerateAgentRequest =
# "_models.GenerateVoiceAgentRequest"` in _unions.py (a bare string, not wrapped in Union[...] like
# every other alias in that file), and generates only a single @overload for generate_agent instead
# of 0 or 2+. Confirmed present in both @azure-tools/typespec-python 0.63.4-dev.11 and 0.64.0-dev.6
# (latest mirrored builds as of 2026-08-19) - a real upstream codegen bug, not fixable here at the
# TypeSpec/source level. Silence the two resulting pyright errors rather than hand-restructure
# generated code.
$files = 'azure\ai\projects\operations\_operations.py', 'azure\ai\projects\aio\operations\_operations.py'
foreach ($f in $files) {
    $lines = Get-Content $f
    $out = New-Object System.Collections.Generic.List[string]
    for ($i = 0; $i -lt $lines.Length; $i++) {
        # Drop the redundant lone @overload stub for generate_agent (invalid: pyright/mypy both
        # require 0 or 2+ overloads, never exactly 1). This exists because the "use union
        # generation request" TypeSpec commit made GenerateAgentRequest a union of exactly one
        # member, and the emitter doesn't collapse that back to a plain (non-overloaded) method.
        if ($lines[$i] -match '^\s*@overload\s*$' -and $lines[$i + 1] -match '(async )?def generate_agent\(') {
            # Skip past the docstring's closing triple-quote (find the second occurrence of a
            # lone closing-quote line after the opening one).
            $quoteCount = 0
            $j = $i
            while ($quoteCount -lt 2) {
                if ($lines[$j] -match '"""') { $quoteCount++ }
                $j++
            }
            # Skip the blank line separating the stub from the concrete implementation.
            while ($lines[$j].Trim() -eq '') { $j++ }
            $i = $j - 1
            continue
        }
        $out.Add($lines[$i])
    }
    Set-Content $f $out
}
foreach ($f in $files) {
    $c = Get-Content $f -Raw
    $c = $c -replace '(def generate_agent\(self, body: )"_unions\.GenerateAgentRequest"', '${1}_models.GenerateVoiceAgentRequest'
    Set-Content $f $c -NoNewline
}

# Remove the generated `voice_agent_web_socket` operation group from the client's public surface
# entirely (import, docstring, and __init__ assignment), instead of deleting the instance attribute
# at runtime in _patch.py/aio/_patch.py. The generated operation only performs a plain HTTP GET (no
# WebSocket upgrade handshake) and discards the connection - it's not a usable client and was never
# meant to be public (the real voice-agent WebSocket client is `.realtime`). Deleting it only at
# runtime left a static/runtime mismatch: pyright/mypy still saw `voice_agent_web_socket:
# VoiceAgentWebSocketOperations` as always present (it's an unconditional generated __init__
# assignment), so callers' code type-checked fine but raised AttributeError at runtime. Stripping it
# here removes the mismatch at its source.
$files = 'azure\ai\projects\_client.py', 'azure\ai\projects\aio\_client.py'
foreach ($f in $files) {
    $c = Get-Content $f -Raw
    $c = $c -replace '(?m)^    :ivar voice_agent_web_socket: VoiceAgentWebSocketOperations operations\r?\n    :vartype voice_agent_web_socket: [^\r\n]*\r?\n', ''
    $c = $c -replace '(?m)^        self\.voice_agent_web_socket = VoiceAgentWebSocketOperations\(\r?\n            self\._client, self\._config, self\._serialize, self\._deserialize\r?\n        \)\r?\n', ''
    $c = $c -replace '(?m)^\s*VoiceAgentWebSocketOperations,\r?\n', ''
    Set-Content $f $c -NoNewline
}

# Fix Sphinx docutils "Bullet list ends without a blank line; unexpected unindent" errors (the
# `-W` sphinx flag turns these into build failures) in VoiceAudioOutputConfig (_models.py and its
# TypedDict twin in types.py) and VoiceConversationStatus (_enums.py). The emitter wraps long
# bullet-list items across multiple physical lines without indenting the continuation under the
# bullet's text, which docutils doesn't recognize as part of the same list item. Join each
# wrapped item back into one physical line; VoiceAudioOutputConfig also needs a blank line
# inserted before its trailing non-bulleted closing sentence to properly terminate the list.
$files = 'azure\ai\projects\models\_models.py', 'azure\ai\projects\types.py'
foreach ($f in $files) {
    $c = Get-Content $f -Raw
    $c = $c -replace '(`voice_temperature`,)\r?\n    (`custom_lexicon_url`,)\r?\n    (`custom_text_normalization_url`)', '$1 $2 $3'
    $c = $c -replace '(plus)\r?\n    (`personal_voice_model`; the voice name is derived from the avatar\.)', '$1 $2'
    $c = $c -replace '(\* `azure-realtime-native`: `voice` and `speed`\.)\r?\n    (`format` and `output_audio_timestamp_types` apply to every voice type\.)', "`$1`r`n`r`n    `$2"
    Set-Content $f $c -NoNewline
}
$f = 'azure\ai\projects\models\_enums.py'
$c = Get-Content $f -Raw
$c = $c -replace '(is)\r?\n    (pending\.)', '$1 $2'
$c = $c -replace '(a)\r?\n    (max-duration `1001`)\r?\n    (close, or a client or network disconnect that the service can still finalize\.)', '$1 $2 $3'
$c = $c -replace '(prevented)\r?\n    (finalization\.)', '$1 $2'
Set-Content $f $c -NoNewline

# Fix get_session_log_stream hardcoding `_stream = True` instead of popping it from kwargs like
# every other streaming operation in this file does (`kwargs.pop("stream", True/False)`). Since it
# never pops "stream" out of kwargs, a caller passing stream=True (as the SSE-streaming contract of
# this operation invites) collides with the explicit `stream=_stream` kwarg forwarded to
# `self._client._pipeline.run()`, raising "got multiple values for keyword argument 'stream'".
$files = 'azure\ai\projects\operations\_operations.py', 'azure\ai\projects\aio\operations\_operations.py'
foreach ($f in $files) {
    $c = Get-Content $f -Raw
    $c = $c -replace '(_decompress = kwargs\.pop\("decompress", True\)\r?\n        )_stream = True(\r?\n        pipeline_response: PipelineResponse = (?:await )?self\._client\._pipeline\.run)', '${1}_stream = kwargs.pop("stream", True)$2'
    Set-Content $f $c -NoNewline
}

# Finishing by running 'black' tool to format code. 
pip install black
black --config ../../../eng/black-pyproject.toml .
