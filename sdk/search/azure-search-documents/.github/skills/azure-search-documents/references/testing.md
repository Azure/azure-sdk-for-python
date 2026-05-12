# azure-search-documents — Testing

Tests use `pytest` plus the [Test Proxy](https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy) for recording and playback. All test files live flat in `tests/`.

Run commands from `sdk/search/azure-search-documents/` using the `venv` alias from `SKILL.md`:

```powershell
cd sdk/search/azure-search-documents
venv python -m pytest tests
```

Use `python -m pytest` rather than bare `pytest` so tests run with the selected package venv.

## Unit tests

Pure logic. No HTTP, no recordings, no service needed.

### File naming

`test_<name>.py` (sync), `test_<name>_async.py` (async).

### Run unit tests

```powershell
venv python -m pytest tests/ --ignore-glob="*_live*"
```

## Live tests

Make HTTP calls to Azure AI Search. Runs in playback by default; switch to live mode to record.

### File naming

`test_<name>_live.py` (sync), `test_<name>_live_async.py` (async).

### Run live tests in playback

Replays existing recordings. Fast, offline.

```powershell
$env:AZURE_TEST_RUN_LIVE = "false"
venv python -m pytest tests/ -k "live"
```

### Record live tests

New live tests require new [Test Proxy](https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy) recordings. Pushing recordings updates the `Tag` in `assets.json`, which points to this package's recordings in `Azure/azure-sdk-assets`.

1. Copy `scripts\Set-LiveTestEnvironment.sample.ps1` to `scripts\Set-LiveTestEnvironment.ps1`, fill in local values, and dot-source it:
   ```powershell
   . .\.github\skills\azure-search-documents\scripts\Set-LiveTestEnvironment.ps1
   ```
2. Run live tests:
   ```powershell
   venv python -m pytest tests/ -k "live"
   ```
3. Push recordings:
   ```powershell
   test-proxy push -a assets.json
   ```
4. Keep the updated `assets.json` with your changes.

## Adding new tests

This checklist is mandatory for every test change. Do not add or update tests without checking each item below.

1. Start from current SDK source. Prioritize public behavior owned or customized by the Python SDK, especially `_patch.py` and other hand-written code paths.
2. Prefer unit tests whenever the behavior is SDK-owned and can be proven without HTTP. Use playback or live tests only when the service contract matters.
3. Place each test in the file that matches the public SDK surface and subject that owns the final assertion: unit `test_<surface_or_helper>.py`, async unit `test_<surface_or_helper>_async.py`, live `test_<public_surface>_<subject_family>_live.py`, async live `test_<public_surface>_<subject_family>_live_async.py`.
4. Name each test after the primary public SDK method or surface under test: `test_<method_or_surface>_<scenario_or_behavior>`. If a parametrized test covers a family of related methods, use a clear family name instead of listing every method.
5. Use deterministic fixtures in Python builders. Share repeated setup and keep scenario-specific setup in the test.
6. Add sync and async together when both public surfaces exist, with matching test names unless the public API differs.
