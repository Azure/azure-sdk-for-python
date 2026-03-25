REM
REM To emit from TypeSpec, run this in the current folder: 
REM
REM   tsp-client update  --debug --local-spec-repo e:\src\azure-rest-api-specs\specification\ai-foundry\data-plane\Foundry
REM
REM (replace `e:\src\...` with the local folder containing up to date TypeSpec)
REM
REM Then run this script to "fix" the emitted code.
REM

REM Revert this, as we want to keep some edits to these file.
git restore pyproject.toml

REM Rename `"items_property": items`, to `"items": items` in search_memories and begin_update_memories methods. "items" is specified in TypeSpec, but Python emitter does not allow it.
powershell -Command "(Get-Content azure\ai\projects\aio\operations\_operations.py) -replace '\"items_property\": items', '\"items\": items' | Set-Content azure\ai\projects\aio\operations\_operations.py"
powershell -Command "(Get-Content azure\ai\projects\operations\_operations.py) -replace '\"items_property\": items', '\"items\": items' | Set-Content azure\ai\projects\operations\_operations.py"

REM Fix content type annotation: replace `content: Union[str, list[...]]` with `content: Union["str", list[...]]`. Otherwise serialization fails.
powershell -Command "(Get-Content azure\ai\projects\models\_models.py) -replace 'content: Union\[str, list\[\"_models\.InputContent\"\]\]', 'content: Union[\"str\", list[\"_models.InputContent\"]]' | Set-Content azure\ai\projects\models\_models.py"

REM Rename WEB_SEARCH_PREVIEW2025_03_11 enum member to WEB_SEARCH_PREVIEW_2025_03_11, to match actual string value
powershell -Command "(Get-Content azure\ai\projects\models\_enums.py) -replace 'WEB_SEARCH_PREVIEW2025_03_11', 'WEB_SEARCH_PREVIEW_2025_03_11' | Set-Content azure\ai\projects\models\_enums.py"
powershell -Command "(Get-Content azure\ai\projects\models\_models.py) -replace 'WEB_SEARCH_PREVIEW2025_03_11', 'WEB_SEARCH_PREVIEW_2025_03_11' | Set-Content azure\ai\projects\models\_models.py"

REM Rename DEFAULT2024_11_15 to DEFAULT_2024_11_15
powershell -Command "(Get-Content azure\ai\projects\models\_enums.py) -replace 'DEFAULT2024_11_15', 'DEFAULT_2024_11_15' | Set-Content azure\ai\projects\models\_enums.py"

REM Edit both _operations.py files to fix missing Foundry-Features HTTP request header in continued list paging calls. Add:
REM   headers=_headers
REM to the end of each of these lines in the BetaXxxOperations classes (do not do this in GA operations classes!)
REM   "GET", urllib.parse.urljoin(next_link, _parsed_next_link.path), params=_next_request_params
REM In emitted code, these first 7 of those lines are associated with GA operations, so start the replacement
REM from the 8th occurrence onward.
powershell -Command "$gaCount=7; $old=[char]34+'GET'+[char]34+', urllib.parse.urljoin(next_link, _parsed_next_link.path), params=_next_request_params'; $new=$old+', headers=_headers'; foreach ($f in 'azure\ai\projects\aio\operations\_operations.py','azure\ai\projects\operations\_operations.py') { $c=Get-Content $f -Raw; $parts=$c -split [regex]::Escape($old); $r=$parts[0]; for ($i=1; $i -lt $parts.Length; $i++) { if ($i -le $gaCount) { $r+=$old+$parts[$i] } else { $r+=$new+$parts[$i] } }; Set-Content $f $r -NoNewline }"

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

REM Finishing by running 'black' tool to format code. 
black --config ../../../eng/black-pyproject.toml .


