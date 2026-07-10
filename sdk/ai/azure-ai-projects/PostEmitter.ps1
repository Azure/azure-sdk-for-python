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

# Fix generated multipart upload operations. The emitter currently generates
# JSON builders for multipart endpoints and retains a runtime-model as_dict()
# path even though Projects now uses TypedDict payloads for these request bodies.
$syncOperationsFile = 'azure\ai\projects\operations\_operations.py'
$c = Get-Content $syncOperationsFile -Raw
$c = $c -replace 'from \.\._utils\.utils import prepare_multipart_form_data', 'from .._utils.utils import FileType, prepare_multipart_form_data'
$c = $c -replace 'agent_name: str, \*, code_zip_sha256: str, json: _types\._CreateAgentVersionFromCodeContent, \*\*kwargs: Any', 'agent_name: str, *, code_zip_sha256: str, files: list[FileType], **kwargs: Any'
$c = $c -replace 'name: str, \*, json: _types\.CreateSkillVersionFromFilesBody, \*\*kwargs: Any', 'name: str, *, files: list[FileType], **kwargs: Any'
$c = [regex]::Replace($c, '(?s)(def build_agents_create_version_from_code_request.*?return HttpRequest\(method="POST", url=_url, params=_params, headers=_headers, )json=json(, \*\*kwargs\))', '$1files=files$2', 1)
$c = [regex]::Replace($c, '(?s)(def build_beta_skills_create_from_files_request.*?return HttpRequest\(method="POST", url=_url, params=_params, headers=_headers, )json=json(, \*\*kwargs\))', '$1files=files$2', 1)
Set-Content $syncOperationsFile $c -NoNewline

$files = 'azure\ai\projects\operations\_operations.py', 'azure\ai\projects\aio\operations\_operations.py'
$typedDictMultipartBody = @"
        if not isinstance(content, MutableMapping):
            raise TypeError("content must be a mapping")
        _body = content

"@
foreach ($f in $files) {
    $c = Get-Content $f -Raw
    $c = $c -replace '        _body = content\.as_dict\(\) if isinstance\(content, _Model\) else content\r?\n', $typedDictMultipartBody
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

# Generate shared TypedDict model contracts directly into azure-ai-extensions-openai
# and leave local azure.ai.projects files as compatibility re-export shims.
python ..\azure-ai-extensions-openai\_scripts\generate_shared_models.py projects
python _scripts\write_extension_type_shims.py

# Keep public model exports limited to models/enums defined by generated modules.
# Star imports from generated _models.py otherwise pull helper imports like
# datetime, Any, FileType, rest_field, Enum, and CaseInsensitiveEnumMeta into
# azure.ai.projects.models and APIView.
@'
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) Python Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import

from . import _enums as _enums_module
from . import _models as _models_module
from ._models import *  # type: ignore # noqa: F401,F403
from ._enums import *  # type: ignore # noqa: F401,F403
from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    name
    for module in (_models_module, _enums_module)
    for name, value in vars(module).items()
    if not name.startswith("_") and isinstance(value, type) and getattr(value, "__module__", None) == module.__name__
]  # pyright: ignore
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
for _name in list(globals()):
    if not _name.startswith("_") and _name not in __all__:
        del globals()[_name]
_patch_sdk()
'@ | Set-Content 'azure\ai\projects\models\__init__.py' -NoNewline


# Finishing by running 'black' tool to format code. 
pip install black
black --config ../../../eng/black-pyproject.toml .
