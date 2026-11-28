# azure-search-documents — Testing

Tests use `pytest` plus the [Test Proxy](https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy) for recording and playback. All test files live flat in `tests/`.

Run commands from `sdk/search/azure-search-documents/` using the `venv` alias from `SKILL.md`:

```powershell
cd sdk\search\azure-search-documents
$env:PYTHONPATH = (Get-Location).Path
venv python -m pytest tests
```

Use `python -m pytest` rather than bare `pytest` so tests run with the selected package venv.
Set `PYTHONPATH` as above so an older installed SDK does not shadow the current source.

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

Recordings must match the API version actually sent by the client. This branch defaults to
`2026-11-01-preview`. After an API version or recorded request changes, re-record the affected
scenarios; do not ignore or rewrite API-version differences to make playback pass. Testing clients
configured for `2026-10-01` requires matching GA recordings: preview playback alone does not
establish GA compatibility.

```powershell
$env:AZURE_TEST_RUN_LIVE = "false"
$env:AZURE_SKIP_LIVE_RECORDING = "false"
venv python -m pytest tests/ -k "live"
```

### Record live tests

New live tests require new [Test Proxy](https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy) recordings. Pushing recordings updates the `Tag` in `assets.json`, which points to this package's recordings in `Azure/azure-sdk-assets`.

Use a **dedicated, disposable Search service** that supports the API version and capabilities
under test. Live scenarios create, update, and delete resources. The current environment preparer
only supplies configuration; test helpers clean up their own named resources, not every resource
on the service. Check inventories before and after a run and investigate any leftovers. Do not
target production or assume that unrelated resources are safe to delete. Run scenarios serially
unless their resource naming and service limits have been verified for parallel execution.

The configured identity must be able to manage Search resources and read/write documents.
Knowledge retrieval needs semantic search and knowledge-base support in the target region.
Indexer tests need the configured Blob container and a usable storage connection string.
File knowledge-source tests additionally need the configured Azure OpenAI embedding deployment
and service identities/roles needed to use it. Keep real credentials in the untracked local
environment file; the committed template contains placeholders only.

1. Copy `.github\skills\azure-search-documents\scripts\Set-LiveTestEnvironment.sample.ps1` to the sibling `Set-LiveTestEnvironment.ps1`, fill in local values, and dot-source it:
   ```powershell
   . .\.github\skills\azure-search-documents\scripts\Set-LiveTestEnvironment.ps1
   ```
2. Enable recording and run the supported live scenarios:
   ```powershell
   $env:AZURE_TEST_RUN_LIVE = "true"
   $env:AZURE_SKIP_LIVE_RECORDING = "false"
   venv python -m pytest tests/ -k "live"
   ```
   Start with index CRUD/statistics, then document queries/indexing, knowledge retrieval
   (including native typed streaming), and finally storage/OpenAI-dependent scenarios.
   Index-statistics paging and name-based conditional deletes have sync/async scenarios.
   Retrieval checks that require references must seed documents and wait for indexing/source
   readiness; an empty response does not establish retrieval quality. Basic Blob indexer
   recordings do not establish permission-ingestion or permission-resync support, which needs
   a dedicated data-source scenario, ACL fixtures, and authorized identities.
   Running samples does not produce test-proxy recordings; use the corresponding recorded tests.
3. Review new recordings for credentials, authorization tokens, endpoints, and storage connection
   strings. Confirm that requests target the intended API version (`2026-11-01-preview` for the
   default November scenarios), then replay the newly recorded scenarios before pushing:
   ```powershell
   $env:AZURE_TEST_RUN_LIVE = "false"
   $env:AZURE_SKIP_LIVE_RECORDING = "false"
   venv python -m pytest tests/ -k "live"
   ```
4. Push recordings:
   ```powershell
   test-proxy push -a assets.json
   ```
5. Keep the updated `assets.json` with your changes.

### Validate live without replacing recordings

After configuring the same disposable service, use these flags for a validation-only run:

```powershell
$env:AZURE_TEST_RUN_LIVE = "true"
$env:AZURE_SKIP_LIVE_RECORDING = "true"
venv python -m pytest tests/ -k "live"
```

This contacts the service but does not refresh playback assets. Reset both flags to `"false"`
before running playback.

### Diagnosing live retrieval streaming

The sync and async retrieval live files each contain
`test_retrieve_stream_returns_typed_lifecycle_events`. They consume the stream and verify a typed
start event, exactly one completion event with status `200` or `206`, a typed completed response,
and no stream-error event. They currently collect the events before asserting; they do not log
each payload or its arrival time.

From the package directory in PowerShell, after configuring the live environment:

```powershell
$env:AZURE_TEST_RUN_LIVE = "true"
$env:AZURE_SKIP_LIVE_RECORDING = "true"
$env:PYTHONPATH = (Get-Location).Path
$streamTests = @(
    "tests\test_knowledge_base_retrieval_client_retrieve_live.py"
    "tests\test_knowledge_base_retrieval_client_retrieve_live_async.py"
)
venv python -m pytest @streamTests `
    -k "test_retrieve_stream_returns_typed_lifecycle_events" `
    -vv -s --log-cli-level=INFO --tb=long
```

Use `--log-cli-level=DEBUG` for more verbose library diagnostics, not as evidence of per-event
logging. For an arrival-time investigation, instrument the consuming `for` or `async for` loop
locally rather than logging only after collecting the entire stream. Do not read the raw response
body ahead of the SDK's SSE parser.

Keep diagnostic logs local and review them before sharing: console output is not sanitized by
the test proxy's recording sanitizers and may expose returned content or citation URLs. These
lifecycle tests do not establish answer-synthesis token-delta delivery, and event timings alone
do not prove that the service or a proxy delivered each event in a separate network chunk.
Re-record changed requests before using playback as service-contract evidence.

## Adding new tests

This checklist is mandatory for every test change. Do not add or update tests without checking each item below.

1. Start from current SDK source. Test SDK-owned behavior, especially `_patch.py` and other hand-written code paths. Do not add package tests solely for pure generated models, enums, or fields; validate generated exports through public API surface review instead.
2. Prefer unit tests whenever the behavior is SDK-owned and can be proven without HTTP. Use playback or live tests only when the service contract matters.
3. Place each test in the file that matches the public SDK surface and subject that owns the final assertion: unit `test_<surface_or_helper>.py`, async unit `test_<surface_or_helper>_async.py`, live `test_<public_surface>_<subject_family>_live.py`, async live `test_<public_surface>_<subject_family>_live_async.py`.
4. Name each test class after the public SDK surface or subject family it groups: `Test<SurfaceOrFamily>`.
5. Name each test after the primary public SDK method or surface under test: `test_<method_or_surface>_<scenario_or_behavior>`. If a parametrized test covers a family of related methods, use a clear family name instead of listing every method.
6. Use deterministic fixtures in Python builders. Share repeated setup and keep scenario-specific setup in the test.
7. Add sync and async together when both public surfaces exist, with matching test names and test class names unless the public API differs.

## Gating preview-only tests

1. Wrap each test scenario that depends on preview-only surfaces with `require_capability(...)`; pass every preview surface the scenario uses.
2. Register capabilities in `tests/_capabilities.py` at the narrowest public surface: new class, new method, method kwarg, model field, or enum member. Use dotted names that match the surface under test, for example `SearchClient.search.query_rewrites`; set `owner` to the public object that must exist and `kwargs` only for method kwargs, model fields, or enum members.
3. Avoid importing preview symbols at module load. Use strings, JSON, local imports, or `hasattr` checks when needed.
