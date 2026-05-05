# azure-search-documents — Testing

Tests use `pytest` plus the [Test Proxy](https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy) for recording and playback. All test files live flat in `tests/`. Always create sync and async versions together.

## Unit tests

Pure logic. No HTTP, no recordings, no service needed.

### File naming

`test_<name>.py` (sync), `test_<name>_async.py` (async).

### Run

```powershell
venv python -m pytest tests/ --ignore-glob="*_live*"
```

## Live tests

Make HTTP calls to Azure Search. Runs in playback by default; switch to live mode to record.

### File naming

`test_<name>_live.py` (sync), `test_<name>_live_async.py` (async).

### Run — playback

Replays existing recordings. Fast, offline.

```powershell
venv python -m pytest tests/ -k "live"
```

### Run — against the real service

Captures new recordings. Required for any new live test.

The [Test Proxy](https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy) records each HTTP exchange to a separate Azure SDK assets repo. `assets.json` (in the package root) is the pointer: it stores the tag/SHA of the recordings repo this package's tests should replay. Pushing recordings updates that tag.

Steps:

1. First time: create `scripts\set-live-env.ps1` (gitignored — never commit; it holds endpoints and may hold connection strings) setting `SEARCH_SERVICE_ENDPOINT`, `SEARCH_SERVICE_NAME`, `SEARCH_STORAGE_CONNECTION_STRING`, `SEARCH_STORAGE_CONTAINER_NAME`, and an `az login --tenant <id>` line.
2. Dot-source: `. .\.github\skills\azure-search-documents\scripts\set-live-env.ps1`
3. Run with `AZURE_TEST_RUN_LIVE=true`:
   ```powershell
   $env:AZURE_TEST_RUN_LIVE = "true"
   venv python -m pytest tests/ -k "live"
   ```

> All `venv` invocations in this file assume the alias is set as shown in `SKILL.md → Environment Setup`. Run from the package root.
4. Push recordings: `test-proxy push -a assets.json` (updates the SHA stored in `assets.json`).
5. Include the updated `assets.json` in your PR.
