REM
REM To emit from typespec, run this in the current folder: 
REM
REM   tsp-client update --local-spec-repo e:\src\azure-rest-api-specs-pr\specification\ai\Azure.AI.Projects
REM
REM (replace `e:\src\...` with the local folder containing up to date TypeSpec)
REM
REM Then run this script to "fix" the emitted code.
REM

REM Revert this, as we want to keep some edits to these file.
git restore pyproject.toml
git restore azure\ai\projects\_version.py

REM We don't use auto-generated tests. Can this TypeSpec be change to no generate them?
rmdir /s /q generated_tests
