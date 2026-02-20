# Contributing to azure-planetarycomputer

This guide covers the manual steps required after regenerating the SDK from TypeSpec, and how to validate your changes locally before pushing to CI.

For general Azure SDK for Python contribution guidance, see the [top-level CONTRIBUTING.md](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md).

---

## Regenerating the SDK from TypeSpec

### 1. Update `tsp-location.yaml`

Edit `tsp-location.yaml` to point to the desired spec commit and directory:

```yaml
directory: specification/orbital/Microsoft.PlanetaryComputer
commit: <new-commit-sha>
repo: Azure/azure-rest-api-specs
```

### 2. Run code generation

From the package root (`sdk/planetarycomputer/azure-planetarycomputer`):

```bash
npx tsp-client update
```

### 3. Clean up generated artifacts

The code generator creates `generated_samples/` and `generated_tests/` directories that should **not** be committed. Delete them:

```bash
rm -rf generated_samples/ generated_tests/
```

### 4. Restore hand-written tests and samples

The generator may overwrite files in `tests/` and `samples/`. Restore them from Git:

```bash
git checkout -- tests/ samples/
```

---

## Known Manual Fixes on Generated Code

The TypeSpec code generator does not emit certain comments or formatting that CI checks require. The following fixes must be **manually applied** after every regeneration.

### Pylint Suppressions

The code generator already produces a file-level suppression on line 1 of each `_operations.py`:
`# pylint: disable=line-too-long,useless-suppression,too-many-lines`

> **Warning:** Do **not** extend line 1 beyond ~70 characters. The Azure pylint `file-needs-copyright-header` check (`C4726`) reads only the first 200 bytes of the file. If line 1 is too long, it pushes the copyright header past the 200-byte boundary and the check fails.

#### `azure/planetarycomputer/operations/_operations.py`

| Location | Suppression | Reason |
|---|---|---|
| `from collections.abc import MutableMapping` | `# pylint: disable=import-error` | Not resolvable in the pylint virtualenv |
| `from .._utils.model_base import (` | `# pylint: disable=unused-import` | `_deserialize_xml` is imported but not always used; the suppression must go on the `from` line (Black reformats the import into multi-line) |
| `def build_data_get_mosaics_tile_request(` | `# pylint: disable=too-many-locals,too-many-branches,too-many-statements` | This function exceeds pylint complexity thresholds; use inline suppression (not file-level to avoid making line 1 too long) |

#### `azure/planetarycomputer/aio/operations/_operations.py`

| Location | Suppression | Reason |
|---|---|---|
| `from collections.abc import MutableMapping` | `# pylint: disable=import-error` | Not resolvable in the pylint virtualenv |
| `from ..._utils.model_base import (` | `# pylint: disable=unused-import` | Same as sync - suppression goes on the `from` line |

#### `azure/planetarycomputer/_utils/model_base.py`

| Location | Suppression | Reason |
|---|---|---|
| `from collections.abc import MutableMapping` | `# pylint: disable=import-error` | Not resolvable in the pylint virtualenv |
| `return super().__new__(cls)` (in `Model.__new__`) | `# pylint: disable=no-value-for-parameter` | False positive - pylint cannot resolve the MRO for `__new__` |

> **Critical: Run Black _before_ adding pylint suppressions.** Black reformats imports (turning single-line into multi-line), which changes where `# pylint: disable` comments must go. If you add suppressions first and then run Black, the comments may end up on the wrong line. The correct order is: (1) run `tox -e black`, (2) restore tests/samples, (3) add pylint suppressions.

> **Emitter version variability:** The emitter may add different inline suppressions to different functions. For example, `build_data_get_mosaics_tile_json_request` gets the full `too-many-locals,too-many-branches,too-many-statements`, while `build_data_get_mosaics_tile_request` only gets `too-many-locals`. Always check the pylint output to see if additional suppressions are needed beyond what the emitter provides.

### Sphinx Docstring Fixes

The code generator sometimes produces RST formatting bugs in docstrings (e.g., code block terminators merged with following text, incorrect bullet continuation indentation). These must be fixed in **both** sync and async `_operations.py`. Run `tox -e sphinx` after each regeneration — Sphinx treats warnings as errors, so any formatting issues will cause a build failure.

### Sample and Test Updates

If the TypeSpec renames or removes API operations, the hand-written samples under `samples/` and `samples/async/` must be updated to match. MyPy and Pyright (which also check samples) will catch these as type errors.

**Test updates require special care:**

- **Do NOT rename test methods** even if the SDK method they test was renamed. Test method names determine recording file paths. Renaming a test method breaks the recording lookup — only change the API call *inside* the test body.
- **Update type assertions** if an API's return type changes (e.g., from `dict` to a typed model). The test assertions must match the new return type.
- **Run tests in playback mode** (`pytest tests/ -v`) after all fixes to verify all tests pass.

---

## Local Validation

Run the following checks **from the package root** before pushing. All commands use the shared tox config:

```bash
cd sdk/planetarycomputer/azure-planetarycomputer
```

### Formatting (Black)

```bash
tox -e black -c ../../../eng/tox/tox.ini --root .
```

### Linting (Pylint)

```bash
tox -e pylint -c ../../../eng/tox/tox.ini --root .
```

### Type Checking (MyPy)

```bash
tox -e mypy -c ../../../eng/tox/tox.ini --root .
```

### Type Checking (Pyright)

```bash
tox -e pyright -c ../../../eng/tox/tox.ini --root .
```

### Documentation (Sphinx)

```bash
tox -e sphinx -c ../../../eng/tox/tox.ini --root .
```

### API Stub Generation

```bash
tox -e apistub -c ../../../eng/tox/tox.ini --root .
```

> **Tip:** Running `black`, `pylint`, `mypy`, `pyright`, and `sphinx` locally catches the vast majority of CI failures before you push.


---

## Testing

This package uses the [Azure SDK test proxy](https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy/README.md) with recorded HTTP sessions stored in the [azure-sdk-assets](https://github.com/Azure/azure-sdk-assets) repo. All commands below assume you are in the package root:

```bash
cd sdk/planetarycomputer/azure-planetarycomputer
```

### Environment setup

Create a `.env` file in the package root (this file is gitignored) with your live resource credentials:

```dotenv
PLANETARYCOMPUTER_ENDPOINT=https://<your-geocatalog>.geocatalog.spatio.azure.com
PLANETARYCOMPUTER_SUBSCRIPTION_ID=<subscription-id>
PLANETARYCOMPUTER_TENANT_ID=<tenant-id>
PLANETARYCOMPUTER_CLIENT_ID=<client-id>
PLANETARYCOMPUTER_CLIENT_SECRET=<client-secret>
PLANETARYCOMPUTER_COLLECTION_ID=<collection-id>
PLANETARYCOMPUTER_ITEM_ID=<item-id>
```

The `conftest.py` calls `load_dotenv()` so these are loaded automatically by pytest.

### Restoring recordings (first time / after pulling changes)

Before running tests in playback mode, you need to restore the recorded sessions from the assets repo. The test proxy does this automatically on the first playback run, but you can also restore explicitly:

```bash
test-proxy restore -a assets.json
```

This clones the tag referenced in `assets.json` into `.assets/` (a gitignored directory).

### Running tests in playback mode

Playback mode replays recorded HTTP sessions — no live Azure resources needed:

```bash
# PowerShell
$env:AZURE_TEST_RUN_LIVE="false"
pytest tests/ -v

# Bash
AZURE_TEST_RUN_LIVE=false pytest tests/ -v
```

You can also run a single test file:

```bash
pytest tests/test_planetary_computer_00_stac_collection.py -v
```

### Recording tests (live mode)

Recording mode runs tests against live Azure resources and captures all HTTP traffic for future playback. **Requires** the `.env` file to be set up with valid credentials.

```bash
# PowerShell
$env:AZURE_TEST_RUN_LIVE="true"
pytest tests/ -v

# Bash
AZURE_TEST_RUN_LIVE=true pytest tests/ -v
```

You can re-record individual test files:

```bash
$env:AZURE_TEST_RUN_LIVE="true"
pytest tests/test_planetary_computer_03_sas.py -v
pytest tests/test_planetary_computer_03_sas_async.py -v
```

> **Tip:** Always re-record **both** sync and async variants of a test file — they have separate recording files.

> **Tip:** After changing sanitizers in `conftest.py`, **all 16 test files** (8 sync + 8 async) must be re-recorded to ensure consistent sanitization across all recordings.

### Pushing recordings to the assets repo

After recording, the new sessions are stored locally in `.assets/`. Push them to the shared assets repo:

```bash
test-proxy push -a assets.json
```

This creates a new tag in `Azure/azure-sdk-assets` and **updates `assets.json` with the new tag automatically**. Verify the new tag:

```bash
cat assets.json
```

> **Important:** Commit the updated `assets.json` alongside your code changes so CI can find the correct recordings.

### Verifying playback after push

Always verify that playback still works after pushing recordings:

```bash
$env:AZURE_TEST_RUN_LIVE="false"
pytest tests/ -v
```

Expected result: **202 passed, 0 failed, 0 skipped**.

### Test file structure

| File | Tests | Description |
|---|---|---|
| `test_00_stac_collection` | 25 | STAC collection CRUD, thumbnail asset creation, metadata |
| `test_01_stac_items` | 19 | STAC item CRUD and querying |
| `test_02_stac_specification` | 13 | STAC API spec compliance (conformance, queryables) |
| `test_03_sas` | 5 | SAS token operations (get, sign, revoke, download) |
| `test_04_stac_item_tiler` | 19 | Tile rendering for individual STAC items |
| `test_05_mosaics_tiler` | 9 | Mosaic tile rendering and static images |
| `test_06_map_legends` | 5 | Map legend generation (continuous + classified) |
| `test_07_collection_lifecycle` | 6 | Full collection create → replace → delete lifecycle |

Each file has a sync and async variant (e.g., `test_00_stac_collection.py` and `test_00_stac_collection_async.py`).

### Key tips

- **Test ordering matters.** Tests within each file are numbered and run in order. For example, `test_10a_create_thumbnail_asset` in `test_00` creates the thumbnail that `test_11_get_collection_thumbnail` reads. Do not reorder or skip tests.
- **Sanitizers are session-scoped.** All sanitizers in `conftest.py` apply to every test. If you add or change a sanitizer, all recordings become stale and must be re-recorded.
- **`EnvironmentVariableLoader` interacts with sanitizers.** During playback, the `EnvironmentVariableLoader` (`PlanetaryComputerPreparer`) replaces real env var values with defaults (e.g., `naip-atl-2` → `naip-atl`). This happens *before* sanitizers run on the recording, so sanitizers must handle both original and post-replacement forms. See the secondary hash sanitizer in `conftest.py` for an example.
- **The `.assets/` directory is gitignored.** Never commit it. It's managed entirely by `test-proxy`.
- **SAS download timing.** `test_03`'s `test_04_signed_href_can_download_asset` uses `urlopen` to download via SAS URL. This occasionally gets 403 in live mode due to SAS delegation key timing when running in a full suite. It has retry logic (5 attempts, 15s delay). The download is skipped in playback mode, so it always passes in CI.
- **Default sanitizer removals.** `conftest.py` removes default Azure SDK sanitizers `AZSDK3493`, `AZSDK3430`, and `AZSDK2003` because collection IDs and item IDs are public STAC data, not secrets.

---

## Quick-Reference Checklist

After running `npx tsp-client update`:

- [ ] Delete `generated_samples/` and `generated_tests/`
- [ ] Restore `tests/` and `samples/` — `git checkout -- tests/ samples/`
- [ ] Run `tox -e black` — formatting (MUST be done before adding pylint suppressions)
- [ ] Restore `tests/` and `samples/` again if Black modified them
- [ ] Add inline `# pylint: disable=import-error` to `MutableMapping` imports (3 files)
- [ ] Add `# pylint: disable=unused-import` on the `from ... import (` line for `_deserialize_xml` (2 files)
- [ ] Add `# pylint: disable=too-many-locals,too-many-branches,too-many-statements` inline on `build_data_get_mosaics_tile_*` functions (check emitter output — may need to add missing suppressions)
- [ ] Add inline `# pylint: disable=no-value-for-parameter` to `Model.__new__` in `model_base.py`
- [ ] Fix any Sphinx docstring issues (both sync and async `_operations.py`) — check `tox -e sphinx` output
- [ ] Run `tox -e pylint` — linting (should score 10.00/10)
- [ ] Run `tox -e sphinx` — documentation (should build with 0 warnings)
- [ ] Run `tox -e mypy` and `tox -e pyright` — type checking (will catch renamed/removed APIs in samples)
- [ ] Update samples if any operations were renamed or removed
- [ ] Update tests: fix API calls (not method names!), update `isinstance` checks for changed return types
- [ ] Run `pytest tests/ -v` in playback mode — should be 202 passed
- [ ] Run `tox -e apistub` — API stub generation
- [ ] Re-record tests if HTTP request/response data changed (see Testing section)
- [ ] Update `CHANGELOG.md` with a release date if preparing a release