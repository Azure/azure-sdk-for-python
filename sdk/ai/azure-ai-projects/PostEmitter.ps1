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

# Remove the generated `voice_agent_web_socket` operation group from the client's public surface
# entirely (import, docstring, and __init__ assignment). The generated operation only performs a
# plain HTTP GET (no WebSocket upgrade handshake) and discards the connection - it's not a usable
# client and was never meant to be public (the real voice-agent WebSocket client is `.realtime`).
$files = 'azure\ai\projects\_client.py', 'azure\ai\projects\aio\_client.py'
foreach ($f in $files) {
    $lines = Get-Content $f
    $out = New-Object System.Collections.Generic.List[string]
    $skipUntilCloseParen = $false
    foreach ($line in $lines) {
        if ($skipUntilCloseParen) {
            if ($line -match '^\s*\)\s*$') { $skipUntilCloseParen = $false }
            continue
        }
        if ($line -match '^\s*VoiceAgentWebSocketOperations,\s*$') { continue }
        if ($line -match '^\s*:ivar voice_agent_web_socket:') { continue }
        if ($line -match '^\s*:vartype voice_agent_web_socket:') { continue }
        if ($line -match '^\s*self\.voice_agent_web_socket = VoiceAgentWebSocketOperations\(\s*$') {
            $skipUntilCloseParen = $true
            continue
        }
        $out.Add($line)
    }
    Set-Content $f $out
}

# get_session_log_stream must always treat the response as an SSE stream, but must still pop any
# caller-supplied stream= kwarg first -- otherwise it collides with the explicit stream=_stream
# argument passed to self._client._pipeline.run(), raising "got multiple values for keyword
# argument 'stream'" (hit by samples calling get_session_log_stream(..., stream=True)).
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
        if ($inFunc -and $lines[$i] -match '^\s*_stream = (True|kwargs\.pop\(.+\))\s*$') {
            $indent = ([regex]::Match($lines[$i], '^\s*')).Value
            $lines[$i] = $indent + '_stream = kwargs.pop("stream", True)'
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

# Fix Sphinx docutils "Bullet list ends without a blank line; unexpected unindent" warnings in
# VoiceAudioOutputConfig (types.py + models/_models.py) and VoiceConversationStatus
# (models/_enums.py). The emitter wraps long bullet-item lines without indenting the
# continuation lines to align with the bullet's text, and (for VoiceAudioOutputConfig) runs the
# trailing summary sentence straight into the last bullet with no blank line to end the list.
#
# NOTE: these here-strings use single-quoted @'...'@ delimiters (not @"..."@) on purpose.
# Double-quoted here-strings still process backtick escape sequences, and since this text is
# full of literal Markdown backticks (`` `azure-standard` ``, etc.), any backtick not immediately
# followed by a recognized escape letter (n, r, t, 0, a, b, f, v, e, #, ', ", `) gets silently
# DROPPED by the PowerShell parser -- with no error or warning. That corrupts $oldVoiceAudioOutputConfig
# so it can never match the real (backtick-containing) generated file content, and .Replace() then
# just silently no-ops. Single-quoted here-strings disable all escape/interpolation processing, so
# the backticks survive exactly as written.
$oldVoiceAudioOutputConfig = @'
    * `azure-standard`: `voice`, `voice_locale`, `speed`, `voice_temperature`,
    `custom_lexicon_url`,
    `custom_text_normalization_url`, `prefer_locales`, `style`, `pitch`, and `volume`.
    * `azure-custom`: all `azure-standard` fields except `style`, plus `custom_voice_endpoint_id`.
    * `azure-personal`: all `azure-standard` fields except `style`, plus `personal_voice_model`.
    * `avatar-voice-sync`: all `azure-standard` fields except `voice` and `style`, plus
    `personal_voice_model`; the voice name is derived from the avatar.
    * `azure-realtime-native`: `voice` and `speed`.
    `format` and `output_audio_timestamp_types` apply to every voice type.
'@
$newVoiceAudioOutputConfig = @'
    * `azure-standard`: `voice`, `voice_locale`, `speed`, `voice_temperature`,
      `custom_lexicon_url`,
      `custom_text_normalization_url`, `prefer_locales`, `style`, `pitch`, and `volume`.
    * `azure-custom`: all `azure-standard` fields except `style`, plus `custom_voice_endpoint_id`.
    * `azure-personal`: all `azure-standard` fields except `style`, plus `personal_voice_model`.
    * `avatar-voice-sync`: all `azure-standard` fields except `voice` and `style`, plus
      `personal_voice_model`; the voice name is derived from the avatar.
    * `azure-realtime-native`: `voice` and `speed`.

    `format` and `output_audio_timestamp_types` apply to every voice type.
'@
$files = 'azure\ai\projects\types.py', 'azure\ai\projects\models\_models.py'
foreach ($f in $files) {
    $c = Get-Content $f -Raw
    $c = $c.Replace($oldVoiceAudioOutputConfig, $newVoiceAudioOutputConfig)
    Set-Content $f $c -NoNewline
}

$f = 'azure\ai\projects\models\_enums.py'
$c = Get-Content $f -Raw
# NOTE: single-quoted @'...'@ here-strings -- see comment above the VoiceAudioOutputConfig fix for why.
$c = $c.Replace(
@'
    * `in_progress`: the live session is active, or post-session persistence finalization is
    pending.
    * `completed`: finalization succeeded after normal or client close, `end_conversation`, a
    max-duration `1001`
    close, or a client or network disconnect that the service can still finalize.
    * `failed`: a terminal service, bridge, storage, or unrecoverable transport failure prevented
    finalization.
'@,
@'
    * `in_progress`: the live session is active, or post-session persistence finalization is
      pending.
    * `completed`: finalization succeeded after normal or client close, `end_conversation`, a
      max-duration `1001`
      close, or a client or network disconnect that the service can still finalize.
    * `failed`: a terminal service, bridge, storage, or unrecoverable transport failure prevented
      finalization.
'@
)
Set-Content $f $c -NoNewline

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


# GenerateAgentRequest is a single-member union in TypeSpec (only GenerateVoiceAgentRequest so
# far), which makes the emitter produce exactly ONE @overload stub for generate_agent. That
# triggers two pyright errors in both sync and async _operations.py:
#   - reportInconsistentOverload: a function needs 0 or 2+ @overloads, never exactly 1.
#   - reportInvalidTypeForm: the real impl's body param is typed as the bare forward-reference
#     string "_unions.GenerateAgentRequest", which isn't a proper importable type (single-member
#     unions are emitted as a plain runtime alias, not a type pyright can resolve).
# Fix: drop the redundant single @overload stub entirely, and retype the real implementation's
# body parameter with the concrete model type (matching the overload stub's own type). Add a new
# @overload here (making it 2+) if a second voice/agent kind is ever added upstream instead.
$oldPatternSync = @"
    @overload
    def generate_agent(
        self, body: _models.GenerateVoiceAgentRequest, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.AgentDetails:
        """Generate an agent.

        Generates and creates an agent from kind-specific high-level inputs. The generated definition
        remains fully editable through the standard agent versioning operations.

        :param body: The kind-specific inputs for generating and creating an agent. Required.
        :type body: ~azure.ai.projects.models.GenerateVoiceAgentRequest
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AgentDetails. The AgentDetails is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.AgentDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def generate_agent(self, body: "_unions.GenerateAgentRequest", **kwargs: Any) -> _models.AgentDetails:
"@
$newPatternSync = @"
    @distributed_trace
    def generate_agent(self, body: _models.GenerateVoiceAgentRequest, **kwargs: Any) -> _models.AgentDetails:
"@
$oldPatternAsync = @"
    @overload
    async def generate_agent(
        self, body: _models.GenerateVoiceAgentRequest, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.AgentDetails:
        """Generate an agent.

        Generates and creates an agent from kind-specific high-level inputs. The generated definition
        remains fully editable through the standard agent versioning operations.

        :param body: The kind-specific inputs for generating and creating an agent. Required.
        :type body: ~azure.ai.projects.models.GenerateVoiceAgentRequest
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AgentDetails. The AgentDetails is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.AgentDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def generate_agent(self, body: "_unions.GenerateAgentRequest", **kwargs: Any) -> _models.AgentDetails:
"@
$newPatternAsync = @"
    @distributed_trace_async
    async def generate_agent(self, body: _models.GenerateVoiceAgentRequest, **kwargs: Any) -> _models.AgentDetails:
"@
$f = 'azure\ai\projects\operations\_operations.py'
$c = Get-Content $f -Raw
$c = $c.Replace($oldPatternSync, $newPatternSync)
Set-Content $f $c -NoNewline
$f = 'azure\ai\projects\aio\operations\_operations.py'
$c = Get-Content $f -Raw
$c = $c.Replace($oldPatternAsync, $newPatternAsync)
Set-Content $f $c -NoNewline

# VoiceResponse narrows OmitPropertiesRealtimeResponse's optional `id`/`conversation_id`
# (Optional[str]) to required `str`, per the TypeSpec spec's explicit "Required." docstrings --
# an intentional Azure-specific tightening of OpenAI's generic realtime response template (a
# persisted voice response always has both set). Pyright's reportIncompatibleVariableOverride
# flags this because narrowing a *mutable* attribute's type in a subclass isn't sound in general,
# but it's safe here by construction (the service never omits these for a persisted response).
# NOTE: uses -replace with a \r?\n-tolerant regex (not .Replace() with a literal `n), since `n
# always resolves to a bare LF and can never match this file's real CRLF line endings -- the
# $1/$2 replacement backreferences preserve whatever newline the regex actually matched.
$f = 'azure\ai\projects\models\_models.py'
$c = Get-Content $f -Raw
$c = $c -replace '(id: str = rest_field\(visibility=\["read", "create", "update", "delete", "query"\]\))(\r?\n    """The unique id of the response\. Required\.""")', '$1  # type: ignore[reportIncompatibleVariableOverride]$2'
$c = $c -replace '(conversation_id: str = rest_field\(visibility=\["read", "create", "update", "delete", "query"\]\))(\r?\n    """The id of the conversation this response belongs to\. Required\.""")', '$1  # type: ignore[reportIncompatibleVariableOverride]$2'
Set-Content $f $c -NoNewline

# Finishing by running 'black' tool to format code. 
pip install black
black --config ../../../eng/black-pyproject.toml .
