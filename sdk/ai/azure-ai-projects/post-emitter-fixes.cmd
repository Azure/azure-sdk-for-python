REM
REM To emit from TypeSpec, run this in the current folder: 
REM
REM   tsp-client update  --debug --local-spec-repo e:\src\azure-rest-api-specs\specification\ai-foundry\data-plane\Foundry
REM
REM (replace `e:\src\...` with the local folder containing up to date TypeSpec)
REM
REM Then run this script to "fix" the emitted code.
REM

REM Revert emitted pyprojects.toml, since it overrides the following changes:
REM - We added "Programming Language :: Python :: 3.14". The emitter removes it.
REM - The emitter uses lower case "i" in "Ai". I want to keep it upper case in the description field: "Microsoft Corporation Azure AI Projects Client Library for Python".
REM - We want a vanity link for the "repository" value, deep linking to the SDK folder (not root of repo): https://aka.ms/azsdk/azure-ai-projects-v2/python/code
git restore pyproject.toml

REM Rename `"items_property": items`, to `"items": items` in search_memories and begin_update_memories methods. "items" is specified in TypeSpec, but Python emitter does not allow it.
powershell -Command "(Get-Content azure\ai\projects\aio\operations\_operations.py) -replace '\"items_property\": items', '\"items\": items' | Set-Content azure\ai\projects\aio\operations\_operations.py"
powershell -Command "(Get-Content azure\ai\projects\operations\_operations.py) -replace '\"items_property\": items', '\"items\": items' | Set-Content azure\ai\projects\operations\_operations.py"

REM Rename WEB_SEARCH_PREVIEW2025_03_11 enum member to WEB_SEARCH_PREVIEW_2025_03_11, to match actual string value
powershell -Command "(Get-Content azure\ai\projects\models\_enums.py) -replace 'WEB_SEARCH_PREVIEW2025_03_11', 'WEB_SEARCH_PREVIEW_2025_03_11' | Set-Content azure\ai\projects\models\_enums.py"
powershell -Command "(Get-Content azure\ai\projects\models\_models.py) -replace 'WEB_SEARCH_PREVIEW2025_03_11', 'WEB_SEARCH_PREVIEW_2025_03_11' | Set-Content azure\ai\projects\models\_models.py"

REM Rename DEFAULT2024_11_15 to DEFAULT_2024_11_15
powershell -Command "(Get-Content azure\ai\projects\models\_enums.py) -replace 'DEFAULT2024_11_15', 'DEFAULT_2024_11_15' | Set-Content azure\ai\projects\models\_enums.py"

REM Rename `A2_A` to `A2A` in enum class AgentEndpointProtocol in _enums.py
powershell -Command "(Get-Content azure\ai\projects\models\_enums.py) -replace 'A2_A', 'A2A' | Set-Content azure\ai\projects\models\_enums.py"

REM Edit both _operations.py files to fix missing Foundry-Features HTTP request header in continued list paging calls. Add:
REM   headers=_headers
REM to the end of each of these lines in the BetaXxxOperations classes (do not do this in GA operations classes!)
REM   "GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), params=_next_request_params
REM In emitted code, these first 7 of those lines are associated with GA operations, so start the replacement
REM from the 8th occurrence onward.
powershell -Command "$gaCount=7; $old=[char]34+'GET'+[char]34+', urllib.parse.urljoin(next_link, _parsed_next_link.path), params=_next_request_params'; $new=$old+', headers=_headers'; foreach ($f in 'azure\ai\projects\aio\operations\_operations.py','azure\ai\projects\operations\_operations.py') { $c=Get-Content $f -Raw; $parts=$c -split [regex]::Escape($old); $r=$parts[0]; for ($i=1; $i -lt $parts.Length; $i++) { if ($i -le $gaCount) { $r+=$old+$parts[$i] } else { $r+=$new+$parts[$i] } }; Set-Content $f $r -NoNewline }"

REM Force streaming in get_session_log_stream for both sync and async operations.
powershell -Command "$files='azure\ai\projects\operations\_operations.py','azure\ai\projects\aio\operations\_operations.py'; foreach ($f in $files) { $lines=Get-Content $f; $inFunc=$false; for ($i=0; $i -lt $lines.Length; $i++) { if ($lines[$i] -match '^\s*(async\s+)?def\s+get_session_log_stream\(') { $inFunc=$true; continue }; if ($inFunc -and $lines[$i] -match '^\s*(async\s+)?def\s+\w+\(') { $inFunc=$false }; if ($inFunc -and $lines[$i] -match 'kwargs\.pop\(.+stream.+False\)') { $indent=([regex]::Match($lines[$i], '^\s*')).Value; $lines[$i]=$indent + '_stream = True' } }; Set-Content $f $lines }"

REM Fix Sphinx issue in class ToolChoiceAllowed, in "tools" property doc string. The "Required" cannot come at the end of the code-block.
REM move it to the end of the text before the code block, and make sure there are no periods after "]".
REM     .. code-block:: json
REM
REM        [
REM          { "type": "function", "name": "get_weather" },
REM          { "type": "mcp", "server_label": "deepwiki" },
REM          { "type": "image_generation" }
REM        ]. Required.
powershell -Command "(Get-Content azure\ai\projects\models\_models.py) -replace 'Responses API, the list of tool definitions might look like:', 'Responses API, the list of tool definitions might look like the following. Required.' | Set-Content azure\ai\projects\models\_models.py"
powershell -Command "(Get-Content azure\ai\projects\models\_models.py) -replace 'list of tool definitions might look like:', 'list of tool definitions might look like the following. Required.' | Set-Content azure\ai\projects\models\_models.py"
powershell -Command "(Get-Content azure\ai\projects\models\_models.py) -replace '        \]\. Required\.', '        ]' | Set-Content azure\ai\projects\models\_models.py"

REM Fix Sphinx docutils warnings in class SessionLogEvent: the generated docstring wraps two long
REM ``data:`` JSON lines mid-string inside a ``.. code-block::`` section. The wrapped continuation
REM lines have wrong indentation (4 spaces instead of 7), causing "unexpected unindent" warnings.
REM Join each broken pair back into one line.
powershell -Command "$f='azure\ai\projects\models\_models.py'; $c=Get-Content $f -Raw; $c=$c -replace '(Starting server)\r?\n[ \t]+(on port 18080)', '$1 $2'; $c=$c -replace '(Successfully)\r?\n[ \t]+(connected to container\"})\.?', '$1 $2'; Set-Content $f $c -NoNewline; $lines=Get-Content $f; $out=@(); foreach ($line in $lines) { if ($line -match '^\s*on port 18080' -and $line -notmatch 'data:') { continue }; if ($line -match '^\s*connected to container' -and $line -notmatch 'data:') { continue }; if ($line -match '^\s*data: .*2026-03-10T09:33:17.121Z') { $out += ('       ' + $line.TrimStart()); continue }; if ($line -match '^\s*data: .*2026-03-10T09:34:52.714Z') { $out += ('       ' + $line.TrimStart()); continue }; $out += $line }; Set-Content $f $out"

REM Fix Sphinx docutils warnings in get_session_log_stream docstrings (sync + async).
REM The emitter wraps bullet/code-block lines with insufficient indentation.
powershell -Command "$files='azure\ai\projects\operations\_operations.py','azure\ai\projects\aio\operations\_operations.py'; foreach ($f in $files) { $c=Get-Content $f -Raw; $c=$c -replace 'schema\r?\n\s+is not contractual and may include additional keys or change format\r?\n\s+over time [^\r\n]*clients should treat it as an opaque string\)', 'schema is not contractual and may include additional keys or change format over time; clients should treat it as an opaque string)'; $c=$c -replace '(message\":\"Starting)\r?\n\s+(FoundryCBAgent server on port 8088\"})', '$1 $2'; $c=$c -replace '(message\":\"INFO: Application)\r?\n\s+(startup complete\.\"})', '$1 $2'; $c=$c -replace '(message\":\"Successfully)\r?\n\s+(connected to container\"})', '$1 $2'; $c=$c -replace '(message\":\"No logs since)\r?\n\s+(last 60 seconds\"})', '$1 $2'; Set-Content $f $c -NoNewline }"

REM Finishing by running 'black' tool to format code. 
black --config ../../../eng/black-pyproject.toml . || echo black not found, skipping formatting.


