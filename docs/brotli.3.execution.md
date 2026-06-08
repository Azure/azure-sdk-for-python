# Execution Log — Sub-item 3: Decode `br` in the streaming path (Bug fix)

Work item: supporting Brotli in azure-core
(GitHub issue [#47186](https://github.com/Azure/azure-sdk-for-python/issues/47186)).

Plan implemented: `docs/brotli.3.plan.md`.
Context document: `assumptions.md`.
Prior implementations: `docs/brotli.1.execution.md` (refactor),
`docs/brotli.2.execution.md` (buffered `br`).

This sub-item fixes the second site of the same defect: the async aiohttp
streaming generator (`AioHttpStreamDownloadGenerator.__anext__`) returned
`Content-Encoding: br` chunks still compressed. The fix adds one `br` branch that
decodes chunks incrementally using aiohttp's own Brotli support, reusing the
existing per-generator `self._decompressor` slot. No new azure-core dependency.

Note on scope: the plan's Steps 4-5 explicitly call for tests (test routes and
streaming tests). They are implemented here, consistent with the Sub-item 1 and
Sub-item 2 execution precedent (both implemented the plan's explicit test steps).
Tests are otherwise deferred to Exercise 5.

---

## Step 0 — Pre-implementation fact-finding (Gate A)

No code change. Findings recorded before any code was written.

- **(a) Q7 — complete set of `Content-Encoding` sites.** A search across
  `sdk/core/azure-core/azure/core` for `Content-Encoding` / `decompressobj` /
  `BrotliDecompressor` confirms exactly two manual dispatch sites: the buffered
  `_aiohttp_body_helper` and the streaming `AioHttpStreamDownloadGenerator.__anext__`.
  No third site. Gate A escalation not triggered.
- **(b) aiohttp version / symbol availability.** Installed aiohttp is 3.13.5;
  `aiohttp.compression_utils` exposes `HAS_BROTLI` and `BrotliDecompressor`. Against
  the `aiohttp>=3.0` lower bound, the guarded import (`try/except ImportError`,
  falling back to "unavailable") covers older versions that lack the symbols.
  Decision: **direct guarded import** (matching Sub-item 2), no version pin.
- **(c) Buffered missing-library error (to match).** Sub-item 2's
  `_decode_brotli_content` raises `azure.core.exceptions.DecodeError` with the exact
  message: "Received a response with 'Content-Encoding: br' but Brotli decompression
  is not available. Install Brotli support (for example, 'pip install Brotli') to
  decode this response." Streaming must raise the identical error. Resolved by PC1
  (single shared source of the message).
- **(d) Trailing-output investigation.** Empirically, aiohttp's incremental Brotli
  decompressor (backed by `brotli.Decompressor.process`) **caps output at roughly
  32 KB per `decompress_sync` call and holds the remainder**; a 60 KB payload fed in
  full returned only 32752 bytes on the first call. aiohttp's `flush()` is a **no-op**
  for the `Brotli` package (`brotli.Decompressor` has no `flush`). The correct pattern
  is to drain each chunk via repeated `decompress_sync(b"")` until it yields nothing;
  a verified drain loop round-trips a 60 KB payload split into 8-byte chunks exactly.
  Consequence: per-chunk draining emits the tail before stream end, so the conditional
  Step 3 (separate end-of-stream finalization) is **not needed** and is dropped (PC2).

Scope justification: satisfies Step 0 (a)-(d) and Gate A.

---

## Change groups mapped to plan steps

### Group 1 — Shared Brotli decompressor factory (Step 1 / PC1)
File:
- `sdk/core/azure-core/azure/core/utils/_pipeline_transport_rest_shared.py`
  - Added `_get_brotli_decompressor()`: guarded import of aiohttp's
    `HAS_BROTLI` / `BrotliDecompressor`; raises the identical `DecodeError` (same
    message as Sub-item 2) when Brotli is unavailable; otherwise returns a fresh
    incremental `BrotliDecompressor`.
  - Refactored Sub-item 2's `_decode_brotli_content` to delegate its import / guard /
    construction to `_get_brotli_decompressor()`. Its one-shot decode behavior is
    otherwise unchanged.

Scope justification: satisfies Step 1 and PC1 (single source of the missing-library
error so buffered and streaming errors are byte-identical — Gate D / R4).

Verified: Gate B buffered suite green (the existing Sub-item 2 buffered `br` tests,
including the missing-library test, still pass through the refactored helper).

### Group 2 — `br` decode branch in `__anext__` with per-chunk drain (Steps 1, 2, PC2)
File:
- `sdk/core/azure-core/azure/core/pipeline/transport/_aiohttp.py`
  - Imported `_get_brotli_decompressor`.
  - In `AioHttpStreamDownloadGenerator.__anext__`, after the existing
    `if enc in ("gzip", "deflate"):` branch, added `elif enc == "br":` that lazily
    initializes `self._decompressor` via `_get_brotli_decompressor()` (mirroring the
    gzip/deflate single-construction guard), resolves `decompress_sync` (falling back
    to `decompress`), decodes the chunk, and **drains** remaining buffered output via
    repeated `decompress(b"")` until empty before returning the decoded bytes.
  - The `if not self._decompress`, `if not enc`, `("gzip", "deflate")` branches, the
    end-of-stream `_ResponseStopIteration` path, and the raw fall-through are
    untouched. The missing-library `DecodeError` propagates through the generator's
    final `except Exception: ... raise` unchanged.

Scope justification: satisfies Step 1 (missing encoding branch — primary root cause),
Step 2 (missing-library `DecodeError`, D3), and PC2 (per-chunk drain replaces the
dropped Step 3).

Verified: Gate C — single-chunk and multi-chunk streamed `br` round-trip; missing
library raises `DecodeError`. Gate D — gzip/deflate/no-encoding streaming unchanged.

### Group 3 — `br` stream test route (Step 4)
File:
- `sdk/core/azure-core/tests/testserver_tests/coretestserver/coretestserver/test_routes/streams.py`
  - Added a `/streams/brotli_decompress_header` route (parallel to the gzip
    `/streams/decompress_header`) that streams hard-coded Brotli bytes
    (`b"\x8b\x01\x80test\x03"` -> `b"test"`) with `Content-Encoding: br`. Static bytes,
    so the test server needs no Brotli library.
  - (The `/encoding/br` route was already added by Sub-item 2; reused for the read
    cache-path test.)

Scope justification: satisfies Step 4 (no `br` stream route existed).

Verified: the live streaming round-trip test below hits this route successfully.

### Group 4 — Streaming `br` tests (Step 5, scenarios a-e)
Files:
- `sdk/core/azure-core/tests/async_tests/test_streaming_async.py`
  - Added a guarded `import brotli` / `_HAS_BROTLI` probe.
  - `test_streaming_decompress_singlechunk_brotli` (a): single-chunk hermetic mock
    round-trips to the original bytes.
  - `test_streaming_decompress_multichunk_brotli` (b): a 45 KB payload (exceeds the
    ~32 KB per-call output cap) split into 7-byte chunks reassembles exactly,
    exercising the stateful decompressor and the per-chunk drain loop.
  - `test_streaming_brotli_no_decompress` (c): `decompress=False` returns the raw
    Brotli chunks untouched.
  - `test_streaming_brotli_missing_library` (d): monkeypatches
    `aiohttp.compression_utils.HAS_BROTLI` to `False`; asserts `__anext__` raises
    `DecodeError` mentioning `Content-Encoding: br` and `Brotli`. Runs regardless of
    environment Brotli availability.
  - `test_decompress_brotli_header_offline` (live): drives `stream_download(..,
    decompress=True)` against `/streams/brotli_decompress_header` and asserts the
    decoded text equals "test".
  - The hermetic mocks (`_MockStreamContent`, `_MockInternalResponse`,
    `_MockStreamResponse`, `_split`) reuse the Sub-item 1 infrastructure.
- `sdk/core/azure-core/tests/async_tests/test_rest_stream_responses_async.py`
  - `test_brotli_decompress_compressed_header_stream` (e): requests `/encoding/br`
    with `stream=True`, then `await response.read()` and asserts `.read()`,
    `.content`, and `.text()` round-trip `b"hello world"` — the async `read()` cache
    path (`RestAioHttpTransportResponse.read()` -> `_aiohttp_body_helper`).

Scope justification: satisfies Step 5 gaps a-e (including GAO G10 read-cache path).

Verified: all five scenarios pass on the fixed code; the four decoded-surface
scenarios (a, b, d, live) fail on pre-fix code (Gate C evidence below); the
`decompress=False` opt-out (c) passes on both, confirming it is unaffected.

### Group 5 — CHANGELOG entry (Step 6)
File:
- `sdk/core/azure-core/CHANGELOG.md`
  - Added a `### Bugs Fixed` bullet under the existing unreleased
    `## 1.42.0 (Unreleased)` heading describing streamed `Content-Encoding: br`
    decoding over the async aiohttp transport and the `DecodeError` fallback,
    referencing #47186. (The heading itself was added by Sub-item 2.)

Scope justification: satisfies Step 6 (user-visible behavior change).

---

## Invariants held
- gzip/deflate/no-encoding streamed behavior is byte-for-byte unchanged (the existing
  streaming suite, including multi-chunk gzip/deflate, stays green).
- `decompress=False` returns raw Brotli chunks untouched (scenario c).
- The streaming decompressor is built once and reused across chunks (single-
  construction guard retained); a multi-chunk stream decodes correctly.
- No public API signature change; no new azure-core dependency or `pyproject` extra
  (`pyproject.toml` is unchanged — verified).
- Buffered and streaming missing-library errors are identical (single source via
  `_get_brotli_decompressor`).

## Gates
- Gate A (after Step 0): two `Content-Encoding` sites confirmed (no third);
  `HAS_BROTLI` / `BrotliDecompressor` reachable; buffered error identified;
  trailing-output question answered (per-chunk drain; no separate flush). CLEARED.
- Gate B (after Steps 1-2): existing async suite green; gzip/deflate/no-encoding and
  the Sub-item 2 buffered `br` tests unchanged. CLEARED (69 passed, 2 skipped).
- Gate C (after Steps 4-5): five new streaming scenarios pass on fixed code; the four
  decoded-surface scenarios fail on pre-fix code; opt-out unaffected. CLEARED.
- Gate D (before review): broader aiohttp async suite green; CHANGELOG present;
  `pyproject.toml` unchanged. CLEARED (124 passed, 2 skipped). Sequencing note: see
  "Verification evidence" — Sub-item 2 is present in the working tree (passing) but
  not yet committed; it must land with or before this change (Gate D consistency).

## Observability
- None added beyond the plan. The only user-facing signal is the actionable
  `DecodeError` message (defined once in `_get_brotli_decompressor`, shared with the
  buffered path). No logging, metrics, config, or public API surface is added.

---

## Plan changes

Both were recorded in `docs/brotli.3.plan.md` ("Plan changes" section) before the
corresponding code was written.

- **PC1 — Extract a shared `_get_brotli_decompressor()` factory and route the buffered
  helper through it.** Step 0(c), Gate D, and R4 require the streaming missing-library
  error to be byte-identical to the buffered one. A single shared source guarantees
  this with zero drift. Sub-item 2's `_decode_brotli_content` was refactored (3 lines)
  to delegate to the factory; its decode behavior is otherwise unchanged (verified by
  Sub-item 2's buffered `br` tests staying green at Gate B).
- **PC2 — Step 3 (separate end-of-stream finalization) dropped; per-chunk draining
  used instead.** Step 0(d) showed the incremental Brotli decompressor caps output
  (~32 KB) per call and holds the remainder, while aiohttp's `flush()` is a no-op for
  the `Brotli` package. The `br` branch drains each chunk fully via repeated
  `decompress_sync(b"")`, which emits the tail before stream end, so a distinct
  end-of-stream flush adds nothing. The plan explicitly permits dropping Step 3 when
  Step 0(d) shows it is unnecessary. Guarded by the multi-chunk round-trip test (R3).

---

## Test results

Environment: repo `venv` (Python 3.12, aiohttp 3.13.5). `Brotli` 1.2.0 installed so
the round-trip tests run (without it they skip cleanly). `coretestserver` installed
editable for the Flask test-server fixture.

- Gate B — `test_streaming_async.py`, `test_universal_http_async.py`,
  `test_rest_stream_responses_async.py` after Steps 1-2: 69 passed, 2 skipped.
- Gate C —
  - New `br` tests (`-k "brotli or br"`): 8 passed (6 in `test_streaming_async.py`
    after black, plus 2 buffered/read in `test_rest_stream_responses_async.py`).
  - Pre-fix verification (source files `_aiohttp.py` and
    `_pipeline_transport_rest_shared.py` temporarily reverted via `git stash`): the
    four decoded-surface streaming scenarios FAILED — single-chunk, multi-chunk,
    missing-library, and the live route (the live route failing with exactly
    `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8b`, the reported defect).
    The `decompress=False` opt-out PASSED pre-fix, confirming it does not depend on the
    fix. Source restored byte-identical afterwards.
- Gate D — `test_streaming_async.py`, `test_universal_http_async.py`,
  `test_basic_transport_async.py`, `test_rest_stream_responses_async.py`:
  124 passed, 2 skipped.
- Formatting — `black --line-length 120 --check` on all changed source/test/fixture
  files: all pass (one test file was reformatted by black, then re-verified green).

Placeholder (to be filled by Exercise 5 / CI): formal CI run links and the full
azure-core async matrix across supported Python and aiohttp versions; an explicit
"Brotli-not-installed" environment run to confirm the round-trip tests skip and the
missing-library test still passes; a run against the `aiohttp>=3.0` lower bound to
confirm the `decompress_sync` / `decompress` fallback and the drain loop.

## Verification evidence
- Local pytest output summarized above (69 / 8 / 124 passed across the gates; four
  decoded-surface streaming scenarios fail on pre-fix code).
- `git diff --stat --cached` for `sdk/core/azure-core`: 8 files changed, +278 / -2.
  Note: this staged set also includes the Sub-item 2 changes (`encoding.py`,
  `test_universal_http_async.py`, and the buffered `br` branch), which were present
  uncommitted in the working tree (HEAD is the "sub-item 1" commit). The Sub-item 3
  production changes are limited to `_aiohttp.py` (the `br` branch) and
  `_pipeline_transport_rest_shared.py` (the `_get_brotli_decompressor` factory plus the
  `_decode_brotli_content` delegation).
- Changes staged, not committed (per execution rules). Commit sequencing left to the
  reviewer; Gate D requires Sub-item 2 to land with or before this change.

Placeholder (to be filled later): CI pipeline run ID and pass/fail badges; downstream
package CI that depends on azure-core.

---

## PR description draft

Title: Decode `Content-Encoding: br` in the streamed aiohttp path (azure-core bug fix)

Work item: #47186 (supporting Brotli in azure-core) — Sub-item 3.

### Scope
Bug fix in azure-core. The async aiohttp streaming generator
(`AioHttpStreamDownloadGenerator.__anext__`) did not decode `Content-Encoding: br`
bodies, returning still-compressed chunks (which surface as corruption or a
`UnicodeDecodeError`, including the unsolicited-`br` Foundry case). This adds `br`
decoding to the streamed path only. Sync `requests`/`urllib3` transports,
`ContentDecodePolicy`, and gzip/deflate are untouched. `zstd` is a separate sub-item.

### Changes
- Add `_get_brotli_decompressor()` to
  `azure/core/utils/_pipeline_transport_rest_shared.py` — the single source of the
  guarded aiohttp Brotli import and the missing-library `DecodeError` message;
  returns a fresh incremental `BrotliDecompressor`. Sub-item 2's
  `_decode_brotli_content` now delegates to it so buffered and streaming errors are
  identical.
- Add a `br` branch to `AioHttpStreamDownloadGenerator.__anext__` that lazily builds
  the incremental decompressor into the existing `self._decompressor` slot, decodes
  each chunk, and drains the decompressor's held output per chunk (aiohttp's Brotli
  decompressor caps output ~32 KB per call). When no Brotli library is importable it
  raises the same actionable `DecodeError` as the buffered path.
- Add a `/streams/brotli_decompress_header` test route and streaming `br` tests:
  single-chunk and multi-chunk round-trip, `decompress=False` raw passthrough,
  missing-library `DecodeError`, and the async `read()` cache path (skipped when
  Brotli is unavailable).
- Add an unreleased `1.42.0` CHANGELOG `Bugs Fixed` entry referencing #47186.

No new azure-core runtime dependency or `pyproject` extra; `br` is only advertised
when a Brotli library is already importable. No public API signature change.

### Rollout
Library source change shipped as a normal azure-core package release through the
standard CI gates. Additive blast radius: a single new branch in one async generator
on the async aiohttp transport. Sequenced to land with or after Sub-item 2 (buffered),
so buffered and streaming `br` behavior ship coherently; this change reuses the shared
`_get_brotli_decompressor` factory.

### Rollback
Single self-contained `git revert`: remove the `__anext__` `br` branch and the
`_get_brotli_decompressor` factory (and re-inline the buffered guard), and revert the
test route, tests, and CHANGELOG entry. The change only transforms in-flight response
chunks — no migration, persisted state, schema, or wire-format change, so a revert
cannot corrupt data; it restores the prior compressed-passthrough behavior for `br`.
Because Step 3 was dropped, there is no separate end-of-stream finalization to revert.

### Monitoring signals
No production telemetry change. The monitoring surface is the azure-core CI gate, the
new streaming `br` tests, and downstream package CI. After release, watch issue #47186
and azure-core bug intake for regressions on streamed gzip/deflate (cross-chunk
corruption) or on `br` decode (dropped tail / `DecodeError` raised when Brotli is in
fact available) for the first release cycle.

---

## Out-of-scope observations
Noticed while implementing; not acted on (recorded per execution rules).

- **Buffered `br` truncates payloads larger than ~32 KB.** Sub-item 2's
  `_decode_brotli_content` does a single one-shot `decompress_sync(content)` and does
  not drain, so a 60 KB Brotli body decodes to only 32752 bytes (verified). This is a
  latent defect in the landed buffered path, not the streamed path fixed here; the
  streamed path drains correctly. Fixing the buffered path (drain or loop) is a
  separate change in Sub-item 2's scope.
- `zstd` has the identical gap in `__anext__`: aiohttp advertises it when `HAS_ZSTD`
  is present, and the streaming path cannot decode it. Separate sub-item / new feature
  (assumptions Q4).
- The `Content-Encoding` header is still re-parsed on every streamed chunk; a shared
  encoding-dispatch helper across the buffered and streaming sites would prevent
  future drift. Owned by Sub-item 1 / a refactor, not this bug.
- The issue text's claim that `brotli` is a guaranteed transitive dependency via
  `aiohttp[speedups]` does not match azure-core's actual `aio = ["aiohttp>=3.0"]`
  extra. Worth flagging on the issue; not a code change.
