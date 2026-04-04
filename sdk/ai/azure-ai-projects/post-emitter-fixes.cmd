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
REM Looks like this is no longer needed:
REM git restore azure\ai\projects\_version.py

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

REM exit /b

REM Remove required 'foundry_features' from public API surface, and instead set them internally in the relevant methods
copy agent-scripts\auto_set_foundry_features.py .
python auto_set_foundry_features.py
del auto_set_foundry_features.py

REM Finishing by running 'black' tool to format code. 
black --config ../../../eng/black-pyproject.toml .

REM No you have some more manual things to do..

REM Fix Sphinx issue in class ToolChoiceAllowed, in "tools" property doc string. Everything should be aligned including JSON example, like this:
REM """A list of tool definitions that the model should be allowed to call. For the Responses API, the
REM  list of tool definitions might look like:
REM  .. code-block:: json
REM  [
REM  { \"type\": \"function\", \"name\": \"get_weather\" },
REM  { \"type\": \"mcp\", \"server_label\": \"deepwiki\" },
REM  { \"type\": \"image_generation\" }
REM  ]. Required."""

REM Edit file azure/ai/projects/aio/operations/_operations.py and:
REM Add "_get_agent_definition_opt_in_keys," as the first line of: from ...operations._operations import (
REM Add:
REM _SERIALIZER = Serializer()
REM _SERIALIZER.client_side_validation = False
REM just before the definition of the class BetaOperations (the first class defined in the file)
    
