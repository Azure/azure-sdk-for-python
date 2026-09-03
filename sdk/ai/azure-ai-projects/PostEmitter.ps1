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

# `types.py` is a dead artifact of the `generate-typeddict: false` tspconfig setting: the emitter
# still rewrites this file's mtime on every run, but its TypedDict content has been byte-for-byte
# frozen/stale since the very first regeneration of this package, regardless of how much the spec's
# models have changed since (confirmed via `git diff --quiet` across multiple TypeSpec commits with
# substantial, unrelated model renames). Delete it outright rather than let it silently ship stale,
# misleading type shapes. The small number of hand-written call sites that referenced it
# (`_patch_agents.py`, `_patch_datasets.py`, `_patch_evaluators.py`, and their aio counterparts)
# now use the emitter's own `JSON` (= MutableMapping[str, Any]) alias instead, matching the same
# "raw JSON body" overload pattern the generated `_operations.py` already uses for these same jobs.
$typesFile = 'azure\ai\projects\types.py'
if (Test-Path $typesFile) {
    Remove-Item $typesFile -Force
}

# `_AgentDefinitionOptInKeys` is an internal implementation-detail enum (leading underscore) used
# only to build the `Foundry-Features` opt-in header value in hand-written `_patch.py`/`_realtime.py`
# customization code, which always imports it directly from `.models._enums` (or `..models._enums`) -
# never through the `models` package's public re-export. The emitter nonetheless includes it in
# `models/__init__.py`'s import list and `__all__`, which makes it part of the public API surface
# (and shows up in APIView) even though nothing needs it there. Strip it from both places.
$f = 'azure\ai\projects\models\__init__.py'
$lines = Get-Content $f
$out = New-Object System.Collections.Generic.List[string]
foreach ($line in $lines) {
    if ($line -match '^\s*_AgentDefinitionOptInKeys,\s*$') { continue }
    if ($line -match '^\s*"_AgentDefinitionOptInKeys",\s*$') { continue }
    $out.Add($line)
}
Set-Content $f $out

# Remove the generated `voice_agent_web_socket` operation group from the public surface entirely.
# The generated operation only performs a plain HTTP GET (no WebSocket upgrade handshake) and
# discards the connection - it's not a usable client and was never meant to be public (the real
# voice-agent WebSocket client is `.realtime`). This operation group has moved around in the
# generated output across regenerations (previously wired directly on the top-level client as
# `VoiceAgentWebSocketOperations`; now nested as `BetaVoiceAgentWebSocketOperations` under
# `BetaOperations.__init__` in `_operations.py`) - this fixup targets wherever it currently lives,
# matching either class name, so it keeps working if the spec relocates it again.
$files = 'azure\ai\projects\_client.py', 'azure\ai\projects\aio\_client.py', 'azure\ai\projects\operations\_operations.py', 'azure\ai\projects\aio\operations\_operations.py'
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
        if ($line -match '^\s*self\.voice_agent_web_socket = (Beta)?VoiceAgentWebSocketOperations\(\s*$') {
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
# argument 'stream'" (hit by samples calling get_session_log_stream(..., stream=True)). The popped
# value is discarded (not used to set _stream): this operation must always stream regardless of
# what the caller passes, otherwise a caller-supplied stream=False would make the generated method
# attempt normal deserialization of an open SSE response, which is invalid per its SSE contract.
$files = 'azure\ai\projects\operations\_operations.py', 'azure\ai\projects\aio\operations\_operations.py'
foreach ($f in $files) {
    $lines = Get-Content $f
    $out = New-Object System.Collections.Generic.List[string]
    $inFunc = $false
    foreach ($line in $lines) {
        if ($line -match '^\s*(async\s+)?def\s+get_session_log_stream\(') {
            $inFunc = $true
            $out.Add($line)
            continue
        }
        if ($inFunc -and $line -match '^\s*(async\s+)?def\s+\w+\(') {
            $inFunc = $false
        }
        if ($inFunc -and $line -match '^\s*_stream = (True|kwargs\.pop\(.+\))\s*$') {
            $indent = ([regex]::Match($line, '^\s*')).Value
            $out.Add($indent + 'kwargs.pop("stream", None)  # must always stream; discard any caller override')
            $out.Add($indent + '_stream = True')
            continue
        }
        $out.Add($line)
    }
    Set-Content $f $out
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
# NOTE: `types.py` used to be listed here too, but it is now deleted outright (see the fixup
# above) before this point would matter, since its TypedDict mirror of this same class no
# longer exists as a file at all.
$files = 'azure\ai\projects\models\_models.py'
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

# Fix Sphinx docutils "Bullet list ends without a blank line; unexpected unindent" warnings in
# RealtimeServerEventConversationItemAdded and RealtimeServerEventConversationItemCreated
# (models/_models.py). Same root cause and fix pattern as the VoiceAudioOutputConfig/
# VoiceConversationStatus fixup above: the emitter wraps long bullet-item lines without
# indenting the continuation lines to align with the bullet's text, and (for
# ConversationItemAdded) runs the trailing summary sentence straight into the last bullet with
# no blank line to end the list. See the NOTE above the VoiceAudioOutputConfig fix for why these
# use single-quoted @'...'@ here-strings (this text is full of literal Markdown backticks).
$f = 'azure\ai\projects\models\_models.py'
$c = Get-Content $f -Raw
$c = $c.Replace(
@'
    * When the client sends a `conversation.item.create` event.
    * When the input audio buffer is committed. In this case the item will be a user message
    containing the audio from the buffer.
    * When the model is generating a Response. In this case the `conversation.item.added` event
    will be sent when the model starts generating a specific Item, and thus it will not yet have
    any content (and `status` will be `in_progress`).
    The event will include the full content of the Item (except when model is generating a
    Response) except for audio data, which can be retrieved separately with a
    `conversation.item.retrieve` event if necessary.
'@,
@'
    * When the client sends a `conversation.item.create` event.
    * When the input audio buffer is committed. In this case the item will be a user message
      containing the audio from the buffer.
    * When the model is generating a Response. In this case the `conversation.item.added` event
      will be sent when the model starts generating a specific Item, and thus it will not yet have
      any content (and `status` will be `in_progress`).

    The event will include the full content of the Item (except when model is generating a
    Response) except for audio data, which can be retrieved separately with a
    `conversation.item.retrieve` event if necessary.
'@
)
$c = $c.Replace(
@'
    * The server is generating a Response, which if successful will produce
    either one or two Items, which will be of type `message`
    (role `assistant`) or type `function_call`.
    * The input audio buffer has been committed, either by the client or the
    server (in `server_vad` mode). The server will take the content of the
    input audio buffer and add it to a new user message Item.
    * The client has sent a `conversation.item.create` event to add a new Item
    to the Conversation.
'@,
@'
    * The server is generating a Response, which if successful will produce
      either one or two Items, which will be of type `message`
      (role `assistant`) or type `function_call`.
    * The input audio buffer has been committed, either by the client or the
      server (in `server_vad` mode). The server will take the content of the
      input audio buffer and add it to a new user message Item.
    * The client has sent a `conversation.item.create` event to add a new Item
      to the Conversation.
'@
)
Set-Content $f $c -NoNewline

# NOTE: a block of code in the implementation of "list_memories", in both sync and async
# _operations.py files, used to be emitted in the wrong place (inside the nested
# "prepare_request" function instead of the main method body, right after
# `error_map.update(kwargs.pop("error_map", {}) or {})`), causing a Pyright
# `reportUnboundVariable` failure and test failures. As of TypeSpec commit
# 1070c74ae519b6f86540bbd44ea295ff12642e60, the emitter now produces the correct shape
# directly (verified: `if body is _Unset: ...` appears in the main method body, before
# `def prepare_request(...)`, in both sync and async list_memories() overloads). The fixup
# that used to correct this has been removed since it's no longer needed. If this
# regresses in a future TypeSpec update (Pyright reports "body" is unbound, or this fixup's
# safety check throws because the old broken pattern reappears), reinstate a fixup here.


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

# VoiceResponse (formerly OmitPropertiesRealtimeResponse before an upstream TypeSpec rename) narrows
# its base class VoiceResponseBase's optional `id`/`conversation_id` (Optional[str]) to required
# `str`, per the TypeSpec spec's explicit "Required." docstrings -- an intentional Azure-specific
# tightening of OpenAI's generic realtime response template (a persisted voice response always has
# both set). Pyright's reportIncompatibleVariableOverride flags this because narrowing a *mutable*
# attribute's type in a subclass isn't sound in general, but it's safe here by construction (the
# service never omits these for a persisted response). This substitution matches on the field
# pattern itself (not the class name), so it keeps working across upstream class renames.
# NOTE: uses -replace with a \r?\n-tolerant regex (not .Replace() with a literal `n), since `n
# always resolves to a bare LF and can never match this file's real CRLF line endings -- the
# $1/$2 replacement backreferences preserve whatever newline the regex actually matched.
$f = 'azure\ai\projects\models\_models.py'
$c = Get-Content $f -Raw
$c = $c -replace '(id: str = rest_field\(visibility=\["read", "create", "update", "delete", "query"\]\))(\r?\n    """The unique id of the response\. Required\.""")', '$1  # type: ignore[reportIncompatibleVariableOverride]$2'
$c = $c -replace '(conversation_id: str = rest_field\(visibility=\["read", "create", "update", "delete", "query"\]\))(\r?\n    """The id of the conversation this response belongs to\. Required\.""")', '$1  # type: ignore[reportIncompatibleVariableOverride]$2'
Set-Content $f $c -NoNewline

# VoiceAgentSessionResponse/VoiceAgentSessionUpdate are single-member unions in TypeSpec (only
# VoiceAgentSessionResponseConfig / VoiceAgentSessionUpdateConfig respectively so far), hitting the
# exact same emitter bug as the GenerateAgentRequest case just above: a single-member union is
# recorded in `_unions.py` as a bare forward-reference *string* (e.g.
# `VoiceAgentSessionResponse = "_models.VoiceAgentSessionResponseConfig"`) rather than a real type
# alias, since `Union[X]` collapses to `X` and the emitter's union-alias codegen path isn't taken.
# Every place in `_models.py` that types a field/parameter as `"_unions.VoiceAgentSessionResponse"`
# or `"_unions.VoiceAgentSessionUpdate"` is therefore an invalid forward reference for mypy/pyright
# (`_unions.py`'s `VoiceAgentSessionResponse`/`VoiceAgentSessionUpdate` are plain `str` values at
# runtime, not resolvable types) -- a `[valid-type]` error every round. Fix by pointing the forward
# reference directly at the concrete model instead of routing through `_unions.py`.
$f = 'azure\ai\projects\models\_models.py'
$c = Get-Content $f -Raw
$c = $c.Replace('"_unions.VoiceAgentSessionResponse"', '"_models.VoiceAgentSessionResponseConfig"')
$c = $c.Replace('"_unions.VoiceAgentSessionUpdate"', '"_models.VoiceAgentSessionUpdateConfig"')
Set-Content $f $c -NoNewline

# Finishing by running 'black' tool to format code. 
pip install black
black --config ../../../eng/black-pyproject.toml .
