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

Recordings must target the API version used by the generated client. After an API version change,
preview recordings cannot establish GA compatibility. Re-record the supported scenarios against
the GA API; do not ignore or rewrite API-version differences just to make playback pass.

```powershell
$env:AZURE_TEST_RUN_LIVE = "false"
venv python -m pytest tests/ -k "live"
```

### Record live tests

New live tests require new [Test Proxy](https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy) recordings. Pushing recordings updates the `Tag` in `assets.json`, which points to this package's recordings in `Azure/azure-sdk-assets`.

Use a **dedicated, disposable Search service** with the `2026-10-01` API enabled.
The live preparer deletes every index, alias, knowledge base, knowledge source, indexer,
data source, and skillset on the configured service before each test. Do not target a shared
or production service. Run these scenarios serially; parallel tests can delete one another's
resources. Do not configure pytest-xdist workers for the recording run.

The configured identity must be able to manage search resources and read/write documents.
Knowledge retrieval needs semantic search and knowledge-base support in the target region.
Indexer tests need the configured Blob container and a usable storage connection string.
File knowledge-source tests additionally need the configured Azure OpenAI embedding deployment
and the service identities/roles needed to use it. The environment template lists variable
names and placeholders only; never commit actual resource credentials.

1. Copy `scripts\Set-LiveTestEnvironment.sample.ps1` to `scripts\Set-LiveTestEnvironment.ps1`, fill in local values, and dot-source it:
   ```powershell
   . .\.github\skills\azure-search-documents\scripts\Set-LiveTestEnvironment.ps1
   ```
2. Ensure recording is enabled and run the supported live scenarios:
   ```powershell
   $env:AZURE_TEST_RUN_LIVE = "true"
   $env:AZURE_SKIP_LIVE_RECORDING = "false"
   venv python -m pytest tests/ -k "live"
   ```
   Samples run directly against the service; they do not produce test-proxy recordings.
   The corresponding recorded tests are the source of playback assets. The existing assets
   tag targets the prior preview and must be replaced with recordings of the GA requests.
   Start with index CRUD/statistics, then document queries/indexing, knowledge retrieval
   (including native typed streaming), and finally storage/OpenAI-dependent scenarios.
   Index-statistics summary paging and name-based conditional deletes have dedicated
   sync/async recording scenarios. Retrieval fixtures seed hotel documents before querying;
   retrieval tests require nonempty references and activity rather than accepting an empty index.
   Indexer `resync` live recording is blocked until a permission-ingestion data-source scenario
   is supplied. Its existing SDK-owned routing is covered by unit tests; the basic Blob fixture
   does not establish that the service accepts permission resync.
3. Review new recording diffs for credentials, authorization tokens, endpoints, and storage
   connection strings. Confirm the requests target `2026-10-01`; do not normalize the
   API-version difference away. Replay the newly recorded scenarios before pushing:
   ```powershell
   $env:AZURE_TEST_RUN_LIVE = "false"
   venv python -m pytest tests/ -k "live"
   ```
4. Push recordings:
   ```powershell
   test-proxy push -a assets.json
   ```
5. Keep the updated `assets.json` with your changes.

### Observing live retrieval streaming

The sync and async retrieval live files each contain
`test_retrieve_stream_returns_typed_lifecycle_events`. They consume and log each payload as it
arrives, rather than collecting the entire stream before logging. INFO logs show the HTTP status,
SSE content type, event number/type, elapsed time since the request started, and completion counts.
DEBUG logs additionally show the deserialized JSON body of every event, including reference lists
and the completed response. These are test diagnostics, not raw HTTP body reads: they do not consume
the response ahead of the SDK's SSE parser.

From the package directory in PowerShell, after configuring the live environment:

```powershell
$env:AZURE_TEST_RUN_LIVE = "true"
$env:AZURE_SKIP_LIVE_RECORDING = "false"
$env:PYTHONPATH = (Get-Location).Path
$streamTests = @(
    "tests/test_knowledge_base_retrieval_client_retrieve_live.py"
    "tests/test_knowledge_base_retrieval_client_retrieve_live_async.py"
)
./.venv/bin/python -m pytest @streamTests `
    -k "test_retrieve_stream_returns_typed_lifecycle_events" `
    -vv -s --log-cli-level=DEBUG --tb=long
```

Use `--log-cli-level=INFO` for progress without payload bodies. Keep DEBUG logs local and review them
before sharing: returned content and citation URLs are not sanitized by the test proxy's recording
sanitizers when printed to the console. The tests explicitly request reference source data from their
seeded hotel index and require intermediate activity/reference payloads plus nonempty response text.
They do not generate answer-synthesis token deltas, and event timings alone do not prove that the
service or a proxy delivered each event in a separate network chunk. Recordings must be regenerated
for the updated request before playback can establish service compatibility.

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
