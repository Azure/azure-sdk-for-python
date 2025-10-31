REM
REM To emit from TypeSpec, run this in the current folder: 
REM
REM   tsp-client update  --debug --local-spec-repo e:\src\azure-rest-api-specs-pr\specification\ai\Azure.AI.Projects
REM
REM (replace `e:\src\...` with the local folder containing up to date TypeSpec)
REM
REM Then run this script to "fix" the emitted code.
REM

REM Restore hand-written files that were deleted. Remove this once the emitter is fixed to go back to old behavior
git restore azure/ai/projects/aio/operations/_patch_connections_async.py
git restore azure/ai/projects/aio/operations/_patch_datasets_async.py
git restore azure/ai/projects/aio/operations/_patch_telemetry_async.py
git restore azure/ai/projects/operations/_patch_connections.py
git restore azure/ai/projects/operations/_patch_datasets.py
git restore azure/ai/projects/operations/_patch_telemetry.py
git restore azure/ai/projects/telemetry/__init__.py
git restore azure/ai/projects/telemetry/_ai_project_instrumentor.py
git restore azure/ai/projects/telemetry/_trace_function.py
git restore azure/ai/projects/telemetry/_utils.py

REM Revert this, as we want to keep some edits to these file.
git restore pyproject.toml
git restore azure\ai\projects\_version.py

REM We don't use auto-generated tests. Can this TypeSpec be change to no generate them?
REM rmdir /s /q generated_tests

REM Add quotation marks around "str" in the expression:   content: Union[str, list["_models.ItemContent"]] = rest_field(
REM This fixes the serialization of this expression: item_param: ItemParam = ResponsesUserMessageItemParam(content="my text")
powershell -Command "(Get-Content azure\ai\projects\models\_models.py) -replace 'Union\[str, list\[\"_models\.ItemContent\"\]\] = rest_field\(', 'Union[\"str\", list[\"_models.ItemContent\"]] = rest_field(' | Set-Content azure\ai\projects\models\_models.py"

REM Fix type annotations by replacing "_types.Filters" with proper union type to fix Pyright errors
powershell -Command "(Get-Content azure\ai\projects\models\_models.py) -replace '\"_types\.Filters\"', 'Union[\"_models.ComparisonFilter\", \"_models.CompoundFilter\"]' | Set-Content azure\ai\projects\models\_models.py"

REM Add additional pylint disables to the model_base.py file
powershell -Command "(Get-Content azure\ai\projects\_utils\model_base.py) -replace '# pylint: disable=protected-access, broad-except', '# pylint: disable=protected-access, broad-except, import-error, no-value-for-parameter' | Set-Content azure\ai\projects\_utils\model_base.py"

REM Disable the version validation
REM No longer needed, since the service now supports api-version "2025-11-15-preview"
REM powershell -Command "(Get-Content azure\ai\projects\_validation.py) -replace 'if _index_with_default\(method_added_on\) > _index_with_default\(client_api_version\):', 'if False:  # pylint: disable=using-constant-test' | Set-Content azure\ai\projects\_validation.py"
REM powershell -Command "(Get-Content azure\ai\projects\_validation.py) -replace 'if unsupported:', 'if False:  # pylint: disable=using-constant-test' | Set-Content azure\ai\projects\_validation.py"

echo Now do these additional changes manually, if you want the "Generate docs" job to succeed in PR pipeline
REM 1. Remove `generate_summary` from class `Reasoning`. It's deprecated but causes two types of errors. Consider removing it from TypeSpec.
