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

REM Fix Sphinx issue in class ToolChoiceAllowed, in "tools" property doc string. Everything should be aligned including JSON example, like this:
REM """A list of tool definitions that the model should be allowed to call. For the Responses API, the
REM  list of tool definitions might look like:
REM  .. code-block:: json
REM  [
REM  { \"type\": \"function\", \"name\": \"get_weather\" },
REM  { \"type\": \"mcp\", \"server_label\": \"deepwiki\" },
REM  { \"type\": \"image_generation\" }
REM  ]. Required."""

REM Fix Sphinx issue: docstring of azure.ai.projects.models.WorkflowPreviewActionOutputItem.type:2: WARNING: Duplicate explicit target name: "learn more". [docutils]
REM Turns out this has nothing to do with doc string of class WorkflowPreviewActionOutputItem. Search for "learn more"
REM and change them to "learn more about ..." (e.g. "learn more about content safety").

REM Fix type annotations by replacing "_types.Filters" with proper union type to fix Pyright errors
REM powershell -Command "(Get-Content azure\ai\projects\models\_models.py) -replace '\"_types\.Filters\"', 'Union[\"_models.ComparisonFilter\", \"_models.CompoundFilter\"]' | Set-Content azure\ai\projects\models\_models.py"

REM Add additional pylint disables to the model_base.py file
REM powershell -Command "(Get-Content azure\ai\projects\_utils\model_base.py) -replace '# pylint: disable=protected-access, broad-except', '# pylint: disable=protected-access, broad-except, import-error, no-value-for-parameter' | Set-Content azure\ai\projects\_utils\model_base.py"

REM Add pyright ignore comment to created_by fields to suppress reportIncompatibleVariableOverride errors
REM powershell -Command "(Get-Content azure\ai\projects\models\_models.py) -replace 'created_by: Optional\[str\] = rest_field\(visibility=\[\"read\", \"create\", \"update\", \"delete\", \"query\"\]\)', 'created_by: Optional[str] = rest_field(visibility=[\"read\", \"create\", \"update\", \"delete\", \"query\"])  # pyright: ignore[reportIncompatibleVariableOverride]' | Set-Content azure\ai\projects\models\_models.py"

echo Now do these additional changes manually, if you want the "Generate docs" job to succeed in PR pipeline
REM Remove `generate_summary` from class `Reasoning`. It's deprecated but causes two types of errors. Consider removing it from TypeSpec.

REM Remove required 'foundry_features' from public API surface
copy agent-scripts\patch_foundry_features_args.py .
python patch_foundry_features_args.py
del patch_foundry_features_args.py

echo Finishing by running 'black' tool to format code. 
black --config ../../../eng/black-pyproject.toml .
