REM
REM To emit from TypeSpec, run this in the current folder: 
REM
REM   tsp-client update  --debug --local-spec-repo e:\src\azure-rest-api-specs-pr\specification\ai\Azure.AI.Projects
REM
REM (replace `e:\src\...` with the local folder containing up to date TypeSpec)
REM
REM Then run this script to "fix" the emitted code.
REM

REM Revert this, as we want to keep some edits to these file.
git restore pyproject.toml
git restore azure\ai\projects\_version.py

REM Rename "A2_A_PREVIEW" to "A2A_PREVIEW". Since this value is an extension to OpenAI.ToolType enum, we can't use @className in client.tsp to do the rename.
powershell -Command "(Get-Content azure\ai\projects\models\_models.py) -replace 'A2_A_PREVIEW', 'A2A_PREVIEW' | Set-Content azure\ai\projects\models\_models.py"
powershell -Command "(Get-Content azure\ai\projects\models\_enums.py) -replace 'A2_A_PREVIEW', 'A2A_PREVIEW' | Set-Content azure\ai\projects\models\_enums.py"

REM Rename `"items_property": items`, to `"items": items` in search_memories and begin_update_memories methods. "items" is specified in TypeSpec, but Python emitter does not allow it.
powershell -Command "(Get-Content azure\ai\projects\aio\operations\_operations.py) -replace '\"items_property\": items', '\"items\": items' | Set-Content azure\ai\projects\aio\operations\_operations.py"
powershell -Command "(Get-Content azure\ai\projects\operations\_operations.py) -replace '\"items_property\": items', '\"items\": items' | Set-Content azure\ai\projects\operations\_operations.py"

REM Fix type annotations by replacing "_types.Filters" with proper union type to fix Pyright errors
powershell -Command "(Get-Content azure\ai\projects\models\_models.py) -replace '\"_types\.Filters\"', 'Union[\"_models.ComparisonFilter\", \"_models.CompoundFilter\"]' | Set-Content azure\ai\projects\models\_models.py"

REM Add additional pylint disables to the model_base.py file
powershell -Command "(Get-Content azure\ai\projects\_utils\model_base.py) -replace '# pylint: disable=protected-access, broad-except', '# pylint: disable=protected-access, broad-except, import-error, no-value-for-parameter' | Set-Content azure\ai\projects\_utils\model_base.py"

echo Now do these additional changes manually, if you want the "Generate docs" job to succeed in PR pipeline
REM Remove `generate_summary` from class `Reasoning`. It's deprecated but causes two types of errors. Consider removing it from TypeSpec.
