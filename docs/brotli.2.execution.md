# Execution Log — Sub-item 2: Decode `br` in the buffered helper (Bug fix)

Work item: supporting Brotli in azure-core
(GitHub issue [#47186](https://github.com/Azure/azure-sdk-for-python/issues/47186)).

Plan implemented: `docs/brotli.2.plan.md`.
Context document: `assumptions.md`.

This sub-item fixes the named bug: the buffered aiohttp helper
(`_aiohttp_body_helper`) did not decode `Content-Encoding: br` bodies. The fix
adds a contained private Brotli helper and one `br` branch, reusing aiohttp's
own Brotli support (no new azure-core dependency). Streaming and `zstd` are out
of scope.

Note on scope: Sub-item 1 (refactor) was already implemented and added
`_get_decompressor`; the `br` branch is layered on top of that helper. The
plan's Steps 3-5 explicitly call for tests, so they are implemented here,
consistent with the Sub-item 1 execution precedent.

---

## Change groups mapped to plan steps

### Group 0 — Confirm aiohttp Brotli import surface (Step 0, Gate A)
- No code change. Confirmed in the repo `venv` (aiohttp 3.13.5) that
  `aiohttp.compression_utils` exposes both `HAS_BROTLI` and `BrotliDecompressor`.
  In this version `BrotliDecompressor` exposes a synchronous `decompress_sync`
  (and an async `decompress`); older aiohttp exposes a synchronous `decompress`.
  The private helper absorbs this difference (prefers `decompress_sync`, falls
  back to `decompress`).

Scope justification: satisfies Step 0 / Gate A (confirm the import contract
before coding).

Verified: `from aiohttp.compression_utils import HAS_BROTLI, BrotliDecompressor`
resolves; round-trip of Brotli bytes via `decompress_sync` returns the original
payload.

### Group 1 — Private Brotli decode helper (Step 1)
File:
- `sdk/core/azure-core/azure/core/utils/_pipeline_transport_rest_shared.py`
  - Added `_decode_brotli_content(content: bytes) -> bytes`. It imports
    `HAS_BROTLI` / `BrotliDecompressor` from `aiohttp.compression_utils` (guarded
    by `try/except ImportError`). If Brotli support is unavailable it raises
    `azure.core.exceptions.DecodeError` (lazy import) with a message naming
    `'Content-Encoding: br'` and how to install Brotli support. Otherwise it
    instantiates `BrotliDecompressor` and decodes via `decompress_sync` (falling
    back to `decompress`). The aiohttp import and version handling are isolated
    here so Sub-item 3 (streaming) can reuse it.

Scope justification: satisfies Step 1 (private helper, D1/D2/D3 error contract,
reuse-ready structure).

Verified: helper imports cleanly; decodes Brotli `b"hello world"` bytes; raises
`DecodeError` when `HAS_BROTLI` is patched `False`.

### Group 2 — `br` branch in `_aiohttp_body_helper` (Step 2)
File:
- `sdk/core/azure-core/azure/core/utils/_pipeline_transport_rest_shared.py`
  - After the existing `_get_decompressor(enc)` (gzip/deflate) branch, added
    `if enc == "br":` which sets `response._content = _decode_brotli_content(...)`,
    sets `response._decompressed_content = True`, and returns the decoded bytes.
    All existing guards (`_content is None`, `_decompress`,
    `_decompressed_content`, empty `Content-Encoding`), the gzip/deflate branch,
    and the trailing raw fall-through are unchanged.

Scope justification: satisfies Step 2 (the named root cause — missing encoding
branch); preserves idempotency via `_decompressed_content`.

Verified: Gate B — `test_universal_http_async.py` (28 passed) including
gzip/deflate/no-encoding/unknown paths unchanged.

### Group 3 — `/encoding/br` test server route (Step 3)
File:
- `sdk/core/azure-core/tests/testserver_tests/coretestserver/coretestserver/test_routes/encoding.py`
  - Added a `/br` route alongside `/gzip` and `/deflate`, returning hard-coded
    Brotli-compressed bytes (`b"\x0b\x05\x80hello world\x03"` -> `b"hello world"`)
    with `Content-Encoding: br`. The server returns static bytes, so it needs no
    Brotli library installed.

Scope justification: satisfies Step 3 (no `br` route existed; needed to exercise
the round-trip).

Verified: REST buffered test below hits this route successfully.

### Group 4 — Buffered `br` round-trip and idempotency tests (Step 4)
Files:
- `sdk/core/azure-core/tests/async_tests/test_universal_http_async.py`
  - Added module-level `_HAS_BROTLI` probe (guarded import) and a shared
    `_BROTLI_HELLO_WORLD` fixture.
  - `test_aiohttp_response_brotli_decompression` (parametrized over
    `AIOHTTP_TRANSPORT_RESPONSES`): asserts `.body()` returns `b"hello world"`
    and `.text()` returns `"hello world"`.
  - `test_aiohttp_response_brotli_decompression_idempotent`: asserts a second
    `.body()` returns identical bytes and `_decompressed_content is True`.
  - Both skip via `skipif(not _HAS_BROTLI)`.
- `sdk/core/azure-core/tests/async_tests/test_rest_stream_responses_async.py`
  - Added guarded `_HAS_BROTLI` probe and
    `test_brotli_decompress_compressed_header`: drives the `client` fixture
    against `/encoding/br` and asserts `.read()`, `.content`, and `.text()`
    round-trip `b"hello world"`. Skips when Brotli is unavailable.

Scope justification: satisfies Step 4 (round-trip and idempotency; A8, A9).

Verified: 7 brotli tests pass on the fixed code; all 6 buffered brotli tests
fail on the pre-fix helper (Gate C evidence below).

### Group 5 — Missing-library `DecodeError` test (Step 5)
File:
- `sdk/core/azure-core/tests/async_tests/test_universal_http_async.py`
  - `test_aiohttp_response_brotli_missing_library` (parametrized): monkeypatches
    `aiohttp.compression_utils.HAS_BROTLI` to `False`, then asserts a `br`
    response raises `azure.core.exceptions.DecodeError` whose message mentions
    `Content-Encoding: br` and `Brotli`. Runs regardless of environment Brotli
    availability (it forces the unavailable path).

Scope justification: satisfies Step 5 (decision D2; negative path / error
contract).

Verified: passes on the fixed code; fails on the pre-fix helper (no branch ->
no `DecodeError`).

### Group 6 — CHANGELOG entry (Step 6)
File:
- `sdk/core/azure-core/CHANGELOG.md`
  - Added a new unreleased `## 1.42.0 (Unreleased)` heading above the dated
    `1.41.0`, with a `### Bugs Fixed` entry describing `br` decompression in the
    buffered aiohttp path and the `DecodeError` fallback, referencing #47186.

Scope justification: satisfies Step 6 (release-note convention).

Verified: heading present and correctly formatted; sits above the latest dated
release.

---

## Invariants held
- gzip/deflate/no-encoding behavior unchanged; truly unknown encodings (`zstd`,
  `identity`, absent) still pass through raw and raise nothing.
- After a `br` decode, `_decompressed_content == True` and a second `.body()`
  does not re-decompress (idempotency test).
- No new azure-core runtime dependency or pyproject extra; the optional Brotli
  import stays local to the private helper and to tests/fixtures.
- The aiohttp Brotli import and version differences are isolated in one private
  helper, reuse-ready for Sub-item 3.

## Gates
- Gate A (after Step 0): `HAS_BROTLI` / `BrotliDecompressor` confirmed reachable;
  version difference absorbed by the helper. CLEARED.
- Gate B (after Step 2): buffered suite green; gzip/deflate/no-encoding/unknown
  unchanged. CLEARED (28 passed).
- Gate C (after Steps 3-5): new `br` round-trip, idempotency, and missing-library
  tests pass on fixed code and fail on pre-fix code. CLEARED (7 pass on fix; 6
  buffered fail on pre-fix).
- Gate D (before PR): broader aiohttp async suite green; CHANGELOG present.
  CLEARED (117 passed, 2 skipped).

## Observability
- None added beyond the plan. The only user-facing signal added is the
  actionable `DecodeError` message defined in Step 1 (D2). No logging, metrics,
  config, or public API surface is added.

---

## Plan changes
- **PC1 — Re-point the Sub-item 1 unknown-encoding pass-through test off `br`.**
  Recorded in `docs/brotli.2.plan.md` Section 12. The Sub-item 1 test
  `test_aiohttp_response_unknown_encoding_passthrough` had pinned
  `Content-Encoding: br` as a raw pass-through. Sub-item 2 intentionally changes
  `br` behavior (decode, or `DecodeError` when Brotli is unavailable), so that
  assertion would now fail and block Gate B. Resolution: switch that test's
  example encoding from `br` to `zstd` (still genuinely unsupported by the
  buffered helper), preserving the test's original intent without conflicting
  with the new `br` behavior. Tied to Step 2.
  - File touched: `tests/async_tests/test_universal_http_async.py`
    (`test_aiohttp_response_unknown_encoding_passthrough` body now uses `zstd`).

---

## Test results

Environment: repo `venv` (Python 3.12, aiohttp 3.13.5). `Brotli` 1.2.0 was
installed locally so the round-trip tests run (without it they skip cleanly).
`coretestserver` is installed editable for the Flask test-server fixture.

- Gate B — `tests/async_tests/test_universal_http_async.py`: 28 passed.
- Gate C —
  - Brotli-only selection (`-k brotli`) across universal + REST: 7 passed.
  - Pre-fix verification (source helper temporarily reverted via `git stash`):
    the 6 buffered brotli tests FAILED (round-trip, idempotency, and
    missing-library), proving they guard the bug. Fix restored and confirmed
    byte-identical.
- Gate D — `test_universal_http_async.py`, `test_streaming_async.py`,
  `test_basic_transport_async.py`, `test_rest_stream_responses_async.py`:
  117 passed, 2 skipped.
- Formatting — `black --line-length 120 --check` on all changed source/test/
  fixture files: 4 files unchanged (pass).

Placeholder (to be filled by Exercise 5 / CI): formal CI run links and the full
azure-core async matrix across supported Python and aiohttp versions; explicit
"Brotli-not-installed" environment run to confirm the round-trip tests skip and
the missing-library test still passes.

## Verification evidence
- Local pytest output summarized above (28 / 7 / 117 passed across the gates;
  6 pre-fix failures confirming the tests fail without the fix).
- `git diff --stat` for `sdk/core/azure-core`: 5 files changed, +139 / -2
  (1 production file, 3 test/fixture files, 1 CHANGELOG).
- Source diff is additive: one new private helper (`_decode_brotli_content`) and
  one `elif`-style `br` branch in `_aiohttp_body_helper`; the gzip/deflate branch
  and raw fall-through are untouched.

Placeholder (to be filled later): CI pipeline run ID and pass/fail badges;
downstream package CI that depends on azure-core.

---

## PR description draft

Title: Decode `Content-Encoding: br` in the buffered aiohttp helper (azure-core bug fix)

Work item: #47186 (supporting Brotli in azure-core) — Sub-item 2.

### Scope
Bug fix in azure-core. The buffered aiohttp response path
(`_aiohttp_body_helper`) did not decode `Content-Encoding: br` bodies, which
could surface as a `UnicodeDecodeError` when reading text (the reported failure,
including the unsolicited-`br` Foundry case). This adds `br` decoding to the
buffered path only. Streaming (`__anext__`) and `zstd` are separate sub-items and
are not touched.

### Changes
- Add a private `_decode_brotli_content(content)` helper to
  `azure/core/utils/_pipeline_transport_rest_shared.py` that reuses aiohttp's own
  Brotli support (`HAS_BROTLI` / `BrotliDecompressor`). If Brotli support is
  unavailable it raises `azure.core.exceptions.DecodeError` with an actionable
  message naming `Content-Encoding: br` and how to install Brotli support. The
  aiohttp import and decompressor-API version differences are isolated here so the
  streaming sub-item can reuse it.
- Add a `br` branch to `_aiohttp_body_helper` that decodes via the helper, sets
  `_decompressed_content = True` (idempotency), and caches the decoded bytes.
- Add a `/encoding/br` test-server route and buffered `br` round-trip,
  idempotency, REST-response, and missing-library `DecodeError` tests (skipped
  when Brotli is unavailable).
- Update one Sub-item 1 characterization test to use `zstd` as its
  unknown-encoding example (see Plan changes / PC1).
- Add an unreleased `1.42.0` CHANGELOG `Bugs Fixed` entry referencing #47186.

No new azure-core runtime dependency or pyproject extra is added; `br` is only
advertised when a Brotli library is already importable.

### Rollout
Library source change shipped as a normal azure-core package release through the
standard CI gates. Additive blast radius: only the async aiohttp buffered path is
touched. Sync transports, `ContentDecodePolicy`, gzip/deflate, streaming, and
unknown-encoding fall-through are unchanged. Sequenced after Sub-item 1 (which
provided the shared `_get_decompressor`); Sub-item 3 (streaming) will reuse the
new `_decode_brotli_content` helper.

### Rollback
Straightforward `git revert` of this PR: remove the `br` branch and the private
helper, and revert the test/route/CHANGELOG changes. The helper only transforms
in-memory response bytes — no migration, persisted state, schema, or wire-format
change, so a revert cannot corrupt data. Partial rollback: if only the error
message/contract is wrong, adjust `_decode_brotli_content` without removing the
`br` branch.

### Monitoring signals
No production telemetry change. The monitoring surface is the azure-core CI gate,
the new `br` tests, and downstream package CI. After release, watch issue #47186
and azure-core bug intake for `br`/decode regressions (double-decompress on
re-read, or `DecodeError` raised when Brotli is in fact available) during the
first release cycle.

---

## Out-of-scope observations
Noticed while implementing; not acted on (recorded per execution rules).

- The streaming aiohttp path (`AioHttpStreamDownloadGenerator.__anext__`) still
  does not decode `br`. That is Sub-item 3 and will reuse `_decode_brotli_content`.
- `zstd` has the identical gap (aiohttp advertises it when `HAS_ZSTD` is present;
  the buffered helper cannot decode it). Tracked separately (assumptions Q4).
- The trailing `return response._content` still serves both truly unknown
  encodings and the fall-through. Any future `identity` handling or multi-value
  `Content-Encoding` parsing would live near here. Noted only.
- azure-core's async extra is plain `aiohttp>=3.0` (no guaranteed Brotli
  library), so the issue text's claim that `brotli` is a guaranteed transitive
  dependency is inaccurate. Worth flagging on the issue; not a code change here.
