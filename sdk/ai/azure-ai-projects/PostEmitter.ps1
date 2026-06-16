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
git restore pyproject.toml


# Edit both _operations.py files to fix missing Foundry-Features HTTP request header in continued list paging calls. Add:
#   headers=_headers
# to the end of each of these lines in the BetaXxxOperations classes (do not do this in GA operations classes!)
#   "GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), params=_next_request_params
# In emitted code, these first 7 of those lines are associated with GA operations, so start the replacement
# from the 8th occurrence onward.
$gaCount = 7
$old = [char]34 + 'GET' + [char]34 + ', urllib.parse.urljoin(next_link, _parsed_next_link.path), params=_next_request_params'
$new = $old + ', headers=_headers'
foreach ($f in 'azure\ai\projects\aio\operations\_operations.py', 'azure\ai\projects\operations\_operations.py') {
    $c = Get-Content $f -Raw
    $parts = $c -split [regex]::Escape($old)
    $r = $parts[0]
    for ($i = 1; $i -lt $parts.Length; $i++) {
        if ($i -le $gaCount) {
            $r += $old + $parts[$i]
        } else {
            $r += $new + $parts[$i]
        }
    }
    Set-Content $f $r -NoNewline
}

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

# Fix Sphinx issue in class ToolChoiceAllowed, in "tools" property doc string. The "Required" cannot come at the end of the code-block.
# move it to the end of the text before the code block, and make sure there are no periods after "]".
#     .. code-block:: json
#
#        [
#          { "type": "function", "name": "get_weather" },
#          { "type": "mcp", "server_label": "deepwiki" },
#          { "type": "image_generation" }
#        ]. Required.
(Get-Content azure\ai\projects\models\_models.py) -replace 'Responses API, the list of tool definitions might look like:', 'Responses API, the list of tool definitions might look like the following. Required.' | Set-Content azure\ai\projects\models\_models.py
(Get-Content azure\ai\projects\models\_models.py) -replace 'list of tool definitions might look like:', 'list of tool definitions might look like the following. Required.' | Set-Content azure\ai\projects\models\_models.py
(Get-Content azure\ai\projects\models\_models.py) -replace '        \]\. Required\.', '        ]' | Set-Content azure\ai\projects\models\_models.py

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
# main body of the "list_memories" method, just before the line "error_map.update(kwargs.pop("error_map", {}) or {})".
# If you don't do this, the PR pipeline will show failures in Pyright (`error: "body" is unbound (reportUnboundVariable)`)
# and some tests will fail. This is the block of code that needs to move up:
#            if body is _Unset:
#                if scope is _Unset:
#                    raise TypeError("missing required argument: scope")
#                body = {"scope": scope}
#                body = {k: v for k, v in body.items() if v is not None}


# Finishing by running 'black' tool to format code. 
pip install black
black --config ../../../eng/black-pyproject.toml .
