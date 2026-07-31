# Implementation Plan — Sub-item 3: Decode `br` in the streaming path (Bug fix)

Work item: supporting brotli in azure-core (GitHub issue
[#47186](https://github.com/Azure/azure-sdk-for-python/issues/47186)).

Sub-item 3: Decode `Content-Encoding: br` in the async aiohttp streaming generator
(`AioHttpStreamDownloadGenerator.__anext__`).

Type: Bug fix (same missing-`br`-branch defect as the buffered helper, second site).

Sequencing (from research D1 / assumptions Q6 decision): in scope now, implemented after
Sub-item 1 (unify dispatch, if approved) and Sub-item 2 (buffered helper). If Sub-item 1
is not approved, implement directly after Sub-item 2. This plan does not depend on
Sub-item 1.

Inputs treated as fact: `docs/brotli.3.research.md`, `assumptions.md`. Decisions already
recorded there are not re-evaluated here.

---

## 1. Selected decisions and rationale (from research)

These are taken as settled. They are not re-decided.

- **D1 — Streaming `br` is in scope now, sequenced after Sub-items 1 and 2.**
  Rationale: `__anext__` carries the same missing-`br`-branch defect as the named
  buffered root cause; leaving it unfixed leaves streamed `br` responses broken.
  (research D1; resolves assumptions Q6.)

- **D2 — Decode mechanism: reuse aiohttp's `HAS_BROTLI` / `BrotliDecompressor`
  (incremental), no new azure-core dependency.**
  Rationale: `br` is only advertised when a Brotli library is already importable, and
  aiohttp's `BrotliDecompressor` supports incremental decode, matching the chunk-by-chunk
  streaming model. Consistent with Sub-item 2. (research D2; assumptions A25, A15a.)
  Open implementation note carried from research: confirm the minimum aiohttp version
  that exposes `HAS_BROTLI` / `BrotliDecompressor` against azure-core's `aiohttp>=3.0`
  lower bound, and decide direct import vs version guard vs compatibility wrapper.

- **D3 — Missing-library behavior: raise a clear, actionable "install Brotli" error.**
  Rationale: silent raw chunks reproduce the corruption / `UnicodeDecodeError`; an
  actionable error is the agreed behavior for the non-compliant-server (Foundry) case and
  is consistent with the buffered sub-item. (research D3; assumptions A10, Q3 resolved.)
  Open implementation note carried from research: specify the exact exception type and
  message source, and keep buffered and streaming missing-library errors identical.

- **D4 — `zstd` stays out of this sub-item.**
  Rationale: avoids folding the adjacent `zstd` gap (a new feature, assumptions Q4) into
  this `br` correctness fix. (research D4; assumptions Q4.)

- **Decode mechanism must be incremental and stateful**, reusing the existing
  per-generator decompressor field so a `br` stream spanning many chunks decodes
  correctly. (research section 1 "Difference from the buffered helper".)

---

## 2. Technical approach end-to-end (and how the fix will be proved)

### The defect
In `sdk/core/azure-core/azure/core/pipeline/transport/_aiohttp.py`,
`AioHttpStreamDownloadGenerator.__anext__` (verified lines 451-470) only decompresses
when `enc in ("gzip", "deflate")` (line 463). For `Content-Encoding: br`, the chunk is
returned still-compressed at line 470. The fix adds a `br` branch that decodes chunks
incrementally using aiohttp's Brotli decompressor, reusing the existing
`self._decompressor` slot already used for gzip/deflate.

### End-to-end approach
1. Add a `br` case to the encoding dispatch in `__anext__` that lazily initializes an
   incremental Brotli decompressor (via aiohttp's `HAS_BROTLI` / `BrotliDecompressor`)
   into the existing `self._decompressor` field, mirroring the gzip/deflate lazy-init
   pattern at lines 464-468.
2. When `br` is received and no Brotli library is importable, raise a clear, actionable
   error consistent with the buffered helper (D3), rather than returning raw chunks.
3. Resolve the trailing-output question: determine whether aiohttp's incremental Brotli
   decompressor can hold bytes back that are only flushed at stream end, and if so ensure
   `__anext__`'s end-of-stream handling emits any finalized bytes. (research section 1
   "Difference from the buffered helper" / GAO G6.)
4. Add streaming-specific tests (single-chunk, multi-chunk, `decompress=False`,
   missing-library, and the async `read()` cache path) that currently have no `br`
   equivalent.

### How the bug will be proved fixed, and nothing else changed
- **Bug fixed:** a new test streams a `br`-encoded body through `iter_bytes()` /
  `stream_download(..., decompress=True)` over the aiohttp transport and asserts the
  reassembled bytes/text equal the original. A multi-chunk variant proves incremental
  decode across `__anext__` calls. (research section 4 gaps 1-2.)
- **Nothing else changed:** the change adds one new branch and does not touch the
  existing `if not self._decompress`, `if not enc`, or `("gzip", "deflate")` branches.
  The full existing azure-core test suite (gzip/deflate stream decode, `decompress=False`,
  no-encoding) must pass unchanged. (assumptions A23, A24; research section 4.)
- **Opt-out preserved:** a `decompress=False` streamed `br` test asserts raw Brotli
  chunks are returned untouched. (research section 4 gap 3; assumptions A24.)

---

## 3. Step-by-step implementation plan

Ordered to minimize blast radius: confirm facts first, add the smallest behavior change,
then prove it with tests, then document. No step changes the buffered helper, sync
transports, or `ContentDecodePolicy`.

### Step 0 — Pre-implementation fact-finding (no code change)
- What: (a) Run and record a repository search for all `Content-Encoding`,
  `_decompress`, and decompression helper sites in azure-core to confirm the two aiohttp
  sites are the complete set. (b) Confirm the minimum aiohttp version exposing
  `HAS_BROTLI` / `BrotliDecompressor` against `aiohttp>=3.0`. (c) Confirm the exact
  exception type/message the buffered helper (Sub-item 2) uses for the missing-library
  case so streaming matches it. (d) Determine whether aiohttp's incremental Brotli
  decompressor holds trailing output requiring a flush at stream end.
- Where: search across `sdk/core/azure-core`; inspect installed aiohttp
  `compression_utils` / `http_parser`; read the landed Sub-item 2 change.
- Why this step exists: research "Still open" items and D2/D3 implementation notes require
  these confirmations before code is written; a missed site or version gap would leave the
  work incomplete.
- Expected outcome: written confirmation of (a)-(d); decision on direct import vs version
  guard vs wrapper; the exact error to reuse; and whether a flush call is needed.
- Scope justification: research section 5 "Still open" (Q7), D2 note, D3 note, and
  section 1 trailing-output note (GAO G6).

### Step 1 — Add the `br` decode branch to `__anext__`
- What: add a branch that, when `enc == "br"`, lazily initializes an incremental Brotli
  decompressor into the existing `self._decompressor` and decodes the chunk, mirroring the
  gzip/deflate lazy-init/decode pattern at lines 463-469.
- Where: `sdk/core/azure-core/azure/core/pipeline/transport/_aiohttp.py`,
  `AioHttpStreamDownloadGenerator.__anext__` (lines 459-470).
- Why this step exists: this is the missing encoding branch that is the root cause
  (research section 2 primary cause).
- Expected outcome: a streamed `br` body decodes chunk-by-chunk; gzip/deflate/no-encoding
  paths are untouched.
- Scope justification: research section 2 (primary root cause) and D2.

### Step 2 — Handle missing Brotli library on the streamed `br` path
- What: when `br` is received and no Brotli library is importable, raise the clear,
  actionable error identified in Step 0(c), matching the buffered helper.
- Where: same branch in `__anext__` as Step 1.
- Why this step exists: D3 requires an actionable error instead of silent raw chunks.
- Expected outcome: a streamed `br` body with no Brotli library raises the same error as
  the buffered path, not corrupt chunks.
- Scope justification: research D3; assumptions A10, Q3 (resolved).

### Step 3 — Finalize trailing output at stream end (only if Step 0(d) shows it is needed)
- What: if the incremental decompressor can hold bytes until stream end, emit any
  finalized output when input is exhausted, so no trailing bytes are lost.
- Where: end-of-stream handling in `__anext__` (around the `_ResponseStopIteration` /
  empty-chunk path, lines 455-456 / 471-473).
- Why this step exists: research flags that incremental decompressors can hold trailing
  output; without finalization a `br` stream could drop its tail.
- Expected outcome: a `br` stream's last bytes are returned; round-trip tests pass exactly.
- Scope justification: research section 1 "Difference from the buffered helper" (GAO G6).
- Note: conditional — included only if Step 0(d) confirms it is required; otherwise dropped.

### Step 4 — Add a `br` stream test route and fixtures
- What: add a `br` stream route (and any `br` encoding fixture) parallel to the existing
  gzip stream route, emitting `Content-Encoding: br` with a Brotli-compressed body.
- Where: `tests/.../test_routes/streams.py` (parallel to the gzip route at L65-94) and
  `tests/.../test_routes/encoding.py` (parallel to `/gzip`, `/deflate`).
- Why this step exists: research section 4 records there is no `br` stream route or
  encoding route to feed a streamed `br` test.
- Expected outcome: a server route that returns a streamed `br` body for tests to consume.
- Scope justification: research section 4 (coverage gaps); assumptions A16.

### Step 5 — Add streaming `br` tests
- What: add tests asserting (a) single-chunk streamed `br` round-trips through
  `iter_bytes()` / `stream_download(..., decompress=True)`; (b) multi-chunk streamed `br`
  reassembles correctly via the stateful decompressor; (c) `decompress=False` streamed
  `br` returns raw chunks untouched; (d) streamed `br` with no Brotli library raises the
  D3 error; (e) the async `read()` cache path
  (`RestAioHttpTransportResponse.read()` / `AsyncHttpResponseImpl.read()`) decodes a `br`
  body correctly.
- Where: `tests/async_tests/test_streaming_async.py` (parallel to
  `test_decompress_compressed_header_offline`, L134-145) and the rest async response
  tests.
- Why this step exists: research section 4 lists each of these as an explicit, currently
  uncovered gap that protects the fix.
- Expected outcome: all five scenarios pass on the fixed code; (a)-(e) fail on pre-fix code
  for the decoded surfaces.
- Scope justification: research section 4 gaps 1-5 (including GAO G10 read-cache path).

### Step 6 — CHANGELOG entry
- What: add a CHANGELOG entry under the unreleased azure-core heading noting that streamed
  `Content-Encoding: br` responses over the async aiohttp transport are now decoded.
- Where: `sdk/core/azure-core/CHANGELOG.md`.
- Why this step exists: a user-visible behavior change requires a changelog entry.
- Expected outcome: a reviewer-visible record of the behavior change.
- Scope justification: assumptions A15, A30; research section 5 open Q8 (heading).

---

## 4. Stop/go gates

- **Gate A (after Step 0):** do not write code until the repository search confirms the
  two aiohttp sites are complete (Q7), the aiohttp version/symbol availability is
  confirmed, the buffered missing-library error is identified, and the trailing-output
  question is answered. If a third `Content-Encoding` site is found, pause and escalate
  (may change scope).
- **Gate B (after Steps 1-3):** do not add tests until the full existing azure-core test
  suite still passes (no regression to gzip/deflate/no-encoding/opt-out).
- **Gate C (after Steps 4-5):** do not open for review until all five new streaming
  scenarios pass and the new decoded-surface tests are confirmed to fail on pre-fix code
  (proving they actually exercise the bug).
- **Gate D (before merge):** confirm Sub-item 2 (buffered helper) has landed and that
  buffered and streaming missing-library errors are identical (D3 consistency).

---

## 5. Validation plan

### Tests to run (existing — must stay green)
- Async streaming decode tests (gzip) in `tests/async_tests/test_streaming_async.py`.
- Sync streaming tests in `tests/test_streaming.py` (must be unaffected — sync transport).
- Encoding/transport tests exercising `Content-Encoding` (gzip/deflate/no-encoding).
  (assumptions A31; research section 4.)

### Tests to add (from research section 4)
1. Streamed `br` round-trips to original bytes/text via `iter_bytes()` /
   `stream_download(..., decompress=True)`.
2. Multi-chunk streamed `br` reassembles correctly across `__anext__` calls (stateful
   decompressor).
3. `decompress=False` streamed `br` returns raw Brotli chunks untouched.
4. Streamed `br` with no Brotli library raises the clear D3 error.
5. Async `read()` cache path decodes a `br` body correctly
   (`RestAioHttpTransportResponse.read()`).

### Invariants
- gzip/deflate/no-encoding streamed behavior is byte-for-byte unchanged (A23).
- `decompress=False` returns raw bytes for any encoding, including `br` (A24).
- A second consume of the same stream does not double-decompress (stateful decompressor
  reused, not re-created).
- No public API signature changes (A28).
- No new azure-core dependency or `pyproject` extra (A25, A15a) — verify `pyproject.toml`
  is unchanged.

### Observability checks
- Confirm the decoded-surface tests fail before the fix and pass after (proves the test
  exercises the defect).
- Confirm the missing-library error message is actionable and identical to the buffered
  path.

---

## 6. Rollout strategy

- This is a library source change to azure-core released as a versioned PyPI package;
  there is no live service deployment to sequence.
- Blast-radius containment: the change is a single new branch in one async generator on
  the async aiohttp transport only. Sync `requests`/`urllib3` transports, the buffered
  helper, and `ContentDecodePolicy` are untouched (research section 3 scope limits).
- Sequencing: merge only after Sub-item 2 has landed (Gate D), so buffered and streaming
  `br` behavior ship coherently.
- Monitoring window: after release, watch the originating issue (#47186) and azure-core
  issue intake for any regression reports on streamed gzip/deflate or on `br` decode for
  the first release cycle.

---

## 7. Rollback plan

- Revert is a single, self-contained source revert of the `__anext__` change plus the
  added tests, CHANGELOG entry, and test routes. No migrations, no persisted state.
- Preconditions to revert: a regression in streamed gzip/deflate/no-encoding or a broken
  `br` decode reported against the released version.
- Data considerations: none — the change only transforms in-flight response chunks; no
  stored data, schema, or config is affected. Reverting restores the prior (compressed
  passthrough for `br`) behavior exactly.
- If only the trailing-output finalization (Step 3) regresses gzip/deflate, that step can
  be reverted independently since it is conditional and isolated to end-of-stream
  handling.

---

## 8. Risks and mitigations (mapped to steps/gates)

- **R1 — A third `Content-Encoding` inspection site exists (Q7), leaving the work
  incomplete.** Mitigation: Step 0(a) repository search; Gate A escalation if found.
- **R2 — Target aiohttp version does not expose `HAS_BROTLI` / `BrotliDecompressor` at the
  `aiohttp>=3.0` lower bound.** Mitigation: Step 0(b) version confirmation; D2 fallback of
  version guard or compatibility wrapper; Gate A.
- **R3 — Trailing bytes lost because the incremental decompressor holds output until
  stream end.** Mitigation: Step 0(d) investigation, conditional Step 3 finalization, and
  multi-chunk round-trip test (Validation test 2); Gate C.
- **R4 — Buffered and streaming missing-library errors diverge.** Mitigation: Step 0(c)
  identifies the buffered error; Step 2 reuses it; Gate D consistency check.
- **R5 — Regression to gzip/deflate/opt-out paths.** Mitigation: branch is additive and
  does not touch existing branches (Step 1); Gate B full existing-suite run; invariants in
  section 5.
- **R6 — New test passes vacuously (does not actually exercise the bug).** Mitigation:
  Gate C requires the decoded-surface tests to fail on pre-fix code.
- **R7 — Accidental scope creep into `zstd` or a shared dispatch refactor.** Mitigation:
  D4 keeps `zstd` out; Sub-item 1 owns any unification; out-of-scope items parked in
  section 11.

---

## 9. Definition of done

- A streamed `br`-encoded body over the async aiohttp transport decodes correctly through
  `iter_bytes()` and `stream_download(..., decompress=True)`, single-chunk and multi-chunk
  (Validation tests 1-2).
- `decompress=False` streamed `br` returns raw chunks untouched (Validation test 3).
- Streamed `br` with no Brotli library raises the same clear, actionable error as the
  buffered helper (Validation test 4; D3).
- The async `read()` cache path decodes a `br` body correctly (Validation test 5).
- All pre-existing azure-core tests pass unchanged (no regression to
  gzip/deflate/no-encoding/opt-out).
- No new azure-core dependency or `pyproject` extra; no public API signature change.
- CHANGELOG entry added under the unreleased azure-core heading.
- The new decoded-surface tests are confirmed to fail on pre-fix code.

---

## 10. Open questions and how they will be closed

- **Q7 (complete set of `Content-Encoding` sites):** closed by the Step 0(a) repository
  search, recorded before coding; Gate A escalates if a new site is found.
- **aiohttp version exposing `HAS_BROTLI` / `BrotliDecompressor` (D2 note):** closed by
  Step 0(b) against the `aiohttp>=3.0` lower bound; resolved into direct import, version
  guard, or wrapper at Gate A.
- **Exact exception type/message for missing library (D3 note):** closed by Step 0(c)
  reading the landed Sub-item 2 change; enforced identical at Gate D.
- **Whether finalization/flush is needed at stream end (GAO G6):** closed by Step 0(d)
  investigation and the multi-chunk test; Step 3 included only if needed.
- **Target azure-core version / CHANGELOG heading (Q8):** closed at Step 6 by writing under
  the current unreleased heading at fix time.
- **Dependency on Sub-item 1:** none for this plan; if Sub-item 1 is approved and unifies
  dispatch first, this fix lands in the unified helper instead — confirmed at Gate A.

---

## Plan changes (recorded during implementation)

These deviations were recorded before the corresponding code was written, per the
execution rules. They resolve the plan's own open implementation notes (D2/D3 notes,
Step 0(c)/(d), and the conditional Step 3).

- **PC1 — Extract a shared `_get_brotli_decompressor()` factory and route the buffered
  helper through it.** Step 0(c), Gate D, and risk R4 require the streaming missing-library
  error to be byte-identical to the buffered one. To guarantee this with zero drift, a new
  module-level factory `_get_brotli_decompressor()` in
  `azure/core/utils/_pipeline_transport_rest_shared.py` becomes the single source of both
  the guarded aiohttp Brotli import and the missing-library `DecodeError` message, and
  returns a fresh incremental `BrotliDecompressor`. Sub-item 2's `_decode_brotli_content`
  is refactored (3 lines) to delegate its import/guard/construction to this factory; its
  decode behavior is otherwise unchanged. Rationale: the plan says Step 2 "reuses" the
  buffered error; a shared source is the faithful, drift-free implementation, and it is
  exactly the shared-helper observation the plan's own Section 11 flags. Verified by
  Sub-item 2's existing buffered `br` tests staying green (Gate B).

- **PC2 — Step 3 (separate end-of-stream finalization) is dropped; per-chunk draining is
  used instead.** Step 0(d) investigation (recorded in the execution log) shows aiohttp's
  incremental Brotli decompressor (backed by `brotli.Decompressor.process`) caps output at
  roughly 32 KB per `decompress_sync` call and holds the remainder, while aiohttp's
  `flush()` is a no-op for the `Brotli` package. The correct incremental pattern is to fully
  drain each chunk via repeated `decompress_sync(b"")` until it yields no more bytes. With
  per-chunk draining, the last network chunk's tail is emitted before the stream ends, so a
  distinct end-of-stream flush step adds nothing. The conditional Step 3 is therefore
  dropped (the plan explicitly allows this: "included only if Step 0(d) confirms it is
  required; otherwise dropped"). A multi-chunk round-trip test guards completeness (R3).

---

## 11. Out-of-scope observations

Noticed while planning. Recorded so they are not lost. NOT part of any plan step above.

- The streaming `__anext__` and the buffered `_aiohttp_body_helper` each independently
  hard-code `("gzip", "deflate")`; a shared encoding-dispatch helper would prevent the
  `br` branch from drifting between the two sites. (Sub-item 1 / assumptions; refactor,
  not this bug.)
- `zstd` has the identical gap in `__anext__`: aiohttp advertises it when `HAS_ZSTD` is
  present and the streaming path cannot decode it. (Assumptions Q4; separate sub-item /
  new feature.)
- `__anext__` lazily creates `self._decompressor` only inside the `("gzip", "deflate")`
  branch; any future encoding needs its own initialization guard near here. (Observation
  only.)
- The legacy `AioHttpTransportResponse` and the new `RestAioHttpTransportResponse` both
  reuse this one generator, so a single streaming `br` fix covers both surfaces.
  (Observation only; no change proposed.)
- The issue text claims `brotli` is "a common transitive dependency via
  `aiohttp[speedups]`," which does not match azure-core's actual `aio = ["aiohttp>=3.0"]`
  extra. Worth flagging on the issue; not a code change. (assumptions out-of-scope.)
