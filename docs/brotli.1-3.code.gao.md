# Code GAO — Brotli work item (Sub-items 1-3)

Work item: supporting Brotli in azure-core (GitHub issue
[#47186](https://github.com/Azure/azure-sdk-for-python/issues/47186)).

Scope of this review: the diff between branch `brotli` and `main`, covering the three
implemented sub-items:

- Sub-item 1 — unify the gzip/deflate decompressor dispatch (Refactor).
  Success criterion: no externally observable behavior change.
- Sub-item 2 — decode `br` in the buffered helper `_aiohttp_body_helper` (Bug fix).
  Success criterion: the defect is corrected and no other behavior changed.
- Sub-item 3 — decode `br` in the streamed path `AioHttpStreamDownloadGenerator.__anext__`
  (Bug fix). Success criterion: the defect is corrected and no other behavior changed.

Inputs used as context: `docs/brotli.{1,2,3}.plan.md`,
`docs/brotli.{1,2,3}.execution.md`, `assumptions.md`.

Verification performed for this review: installed aiohttp `BrotliDecompressor` source was
inspected across aiohttp 3.13.2 / 3.13.3 / 3.13.5, and the buffered decode path was run
directly against a 90 KB payload to confirm the truncation finding below.

No code was changed by this review.

---

## Summary

The streaming fix (Sub-item 3) is correct and well guarded: it drains the incremental
Brotli decompressor per chunk and round-trips large payloads. The refactor (Sub-item 1)
is behavior-neutral and matches its plan.

The buffered fix (Sub-item 2) does **not** fully meet its success criterion. It corrects
the original `br` failure for small bodies but introduces a **new** defect: bodies larger
than roughly 32 KB are silently truncated. The existing buffered tests only use an
11-byte body, so the truncation is not caught. This is the one blocker.

A separate "Scope creep" group at the end flags the planning/research/execution markdown
artifacts that are committed in this diff and are not part of the azure-core code change.

---

## Gaps and Opportunities

### G1 — Buffered `br` decode silently truncates bodies larger than ~32 KB

- **Location:** `sdk/core/azure-core/azure/core/utils/_pipeline_transport_rest_shared.py`,
  `_decode_brotli_content` (lines ~433-450), specifically:
  ```python
  decompressor = _get_brotli_decompressor()
  decompress = getattr(decompressor, "decompress_sync", None) or decompressor.decompress
  return decompress(content)
  ```
  Reached from `_aiohttp_body_helper` (line ~485) for every buffered `.body()` /
  `.read()` / `.text()` call on a `Content-Encoding: br` response.
- **Severity:** Blocker
- **Gap or opportunity:** aiohttp's `BrotliDecompressor.decompress_sync` (aiohttp 3.13.3
  and later) calls `brotli.Decompressor.decompress(data, max_length)` with
  `max_length = ZLIB_MAX_LENGTH_UNLIMITED`, which is `0`. The Brotli package does not treat
  `0` as unlimited here; it returns only one internal output buffer (about 32 KB) and holds
  the remainder. The buffered helper calls `decompress(content)` once and does not drain the
  held output, so a large body is silently truncated. Direct reproduction in this repo's
  `venv` (aiohttp 3.13.5, Brotli 1.2.0): a 90,000-byte payload decoded to only 32,752 bytes
  and the round-trip assertion failed. The streamed path (Sub-item 3) added a drain loop for
  exactly this reason; the buffered path was left as a single one-shot call. This breaks the
  Sub-item 2 success criterion: the fix corrects the small-body case but creates a new
  large-body corruption defect. Note this is aiohttp-version-dependent — on aiohttp earlier
  than 3.13.3, `decompress_sync(data)` takes no `max_length` and returns everything, so the
  truncation only appears on newer aiohttp.
- **Recommended action:** Make the buffered decode drain the decompressor the same way the
  streamed branch does — call the decompress function once with the content, then loop
  `decompress(b"")` until it returns empty, concatenating the output. Better, extract a
  single shared draining decode used by both the buffered helper and the streamed branch so
  the two paths cannot diverge again (see G4). Add a buffered round-trip test with a payload
  larger than ~32 KB (see G2).
- **Disposition:** Address

### G2 — Buffered `br` tests only exercise an 11-byte body, so G1 is not caught

- **Location:**
  `sdk/core/azure-core/tests/async_tests/test_universal_http_async.py`
  (`test_aiohttp_response_brotli_decompression`,
  `test_aiohttp_response_brotli_decompression_idempotent`, using
  `_BROTLI_HELLO_WORLD = b"\x0b\x05\x80hello world\x03"`) and the `/encoding/br` route in
  `tests/.../test_routes/encoding.py` (also `b"hello world"`).
- **Severity:** Major
- **Gap or opportunity:** Every buffered `br` test uses an 11-byte payload, which fits in a
  single Brotli output buffer and therefore never exercises the truncation in G1. The
  streamed tests do use a >32 KB payload (`* 1000`) and catch the cap; the buffered tests do
  not. The buffered success criterion is therefore not actually proven for realistic JSON
  responses (the originating issue is about non-trivial bodies).
- **Recommended action:** Add a buffered `br` round-trip test with a payload larger than the
  per-call cap (for example the same `"...lazy dog. " * 1000` body used by the streamed
  multi-chunk test) and assert exact equality. This test should fail before the G1 fix and
  pass after.
- **Disposition:** Address

### G3 — Buffered and streamed `br` decode logic is duplicated and can drift

- **Location:** streamed branch in
  `sdk/core/azure-core/azure/core/pipeline/transport/_aiohttp.py` (lines ~470-483, including
  the drain loop) versus `_decode_brotli_content` in
  `_pipeline_transport_rest_shared.py` (lines ~433-450, no drain loop).
- **Severity:** Major
- **Gap or opportunity:** The two sites independently resolve `decompress_sync`/`decompress`
  and then handle the held output differently — the streamed site drains, the buffered site
  does not. This divergence is the direct cause of G1. Sub-item 1's stated goal was to stop
  the decode logic drifting between the two aiohttp sites; the `br` decode reintroduced exactly
  that drift.
- **Recommended action:** Centralize a single draining Brotli decode (bytes in, fully
  decoded bytes out) in `_pipeline_transport_rest_shared.py` and call it from both the
  buffered helper and the streamed branch. This both fixes G1 and restores the
  single-source-of-truth intent of Sub-item 1.
- **Disposition:** Address

### G4 — Dead fallback `or self._decompressor.decompress`

- **Location:** `sdk/core/azure-core/azure/core/pipeline/transport/_aiohttp.py` line ~474
  and `_pipeline_transport_rest_shared.py` line ~448:
  `getattr(decompressor, "decompress_sync", None) or decompressor.decompress`.
- **Severity:** Nit
- **Gap or opportunity:** aiohttp's `BrotliDecompressor` exposes `decompress_sync` on all
  inspected versions (3.13.2, 3.13.3, 3.13.5), so `getattr` always returns it and the
  `or ... .decompress` branch is unreachable. `BrotliDecompressor` has no `decompress`
  method, so if the fallback ever did run it would raise `AttributeError` rather than decode.
  The comment ("older versions expose a synchronous `decompress`") is not supported by the
  inspected aiohttp source.
- **Recommended action:** Either remove the fallback and call `decompress_sync` directly, or,
  if a real older-aiohttp shape is intended, confirm that shape against the actual minimum
  supported aiohttp and adjust the comment to match. Keep this together with the G3
  consolidation.
- **Disposition:** Defer

### G5 — Synchronous decode runs on the event loop for large streamed bodies

- **Location:** streamed `br` branch in `_aiohttp.py` (lines ~470-483); also the existing
  gzip/deflate `self._decompressor.decompress(chunk)` at line ~468.
- **Severity:** Minor
- **Gap or opportunity:** `decompress_sync` is called directly inside the async generator, so
  decoding (including the drain loop) runs synchronously on the event loop. For large bodies
  this can block the loop. This matches the pre-existing gzip/deflate behavior, so it is not a
  regression introduced by this work, and aiohttp itself offers an executor path that is not
  used here.
- **Recommended action:** Leave as-is for this work item to preserve parity with gzip/deflate.
  If event-loop blocking on large downloads becomes a concern, handle gzip, deflate, and
  brotli together in a follow-up rather than singling out brotli.
- **Disposition:** Defer

### G6 — `Content-Encoding` is re-read and re-lowered on every streamed chunk

- **Location:** `_aiohttp.py` `__anext__`, lines ~461-465 (`enc = internal_response.headers
  .get("Content-Encoding")` then `enc = enc.lower()` on each iteration).
- **Severity:** Nit
- **Gap or opportunity:** The encoding is parsed once per chunk rather than once per stream.
  This is pre-existing and was explicitly parked as out-of-scope in the Sub-item 1 and 3
  plans. Noted only so it is not lost.
- **Recommended action:** None for this work item. Consider parsing the encoding once at
  generator construction in a future refactor.
- **Disposition:** Defer

### G7 — CHANGELOG uses a minor version bump for a bug-fix-only change

- **Location:** `sdk/core/azure-core/CHANGELOG.md` lines 3-10
  (`## 1.42.0 (Unreleased)` with only a `### Bugs Fixed` section).
- **Severity:** Nit
- **Gap or opportunity:** The new heading is `1.42.0` (a minor bump) but the entries are
  bug fixes only. Whether this should be `1.41.1` (patch) or fold into an existing planned
  `1.42.0` is a release-management decision, not a correctness one.
- **Recommended action:** Confirm the intended next version with the azure-core maintainers
  at release time; adjust the heading if a patch release is preferred.
- **Disposition:** Defer

### G8 — `zstd` remains undecoded at both sites

- **Location:** buffered `_aiohttp_body_helper` (lines ~479-487) and streamed `__anext__`
  (lines ~465-484); neither handles `zstd`.
- **Severity:** Minor
- **Gap or opportunity:** aiohttp can advertise `zstd` when `HAS_ZSTD` is present, and both
  azure-core paths will return raw (or, depending on the response surface, fail to decode) a
  `Content-Encoding: zstd` body, mirroring the original `br` gap. The plans correctly scoped
  `zstd` out (assumptions Q4), so this is not a defect in the delivered work — it is a known,
  adjacent gap recorded so it is tracked.
- **Recommended action:** Track `zstd` as a separate follow-up work item (new feature), not
  part of this branch.
- **Disposition:** Defer

### G9 — Sub-items 2 and 3 landed in a single commit, against the planned sequencing

- **Location:** branch history — commit `7ba4bfff3a` "item 2 and 3 initial" contains both
  the buffered and streamed `br` changes; Sub-item 1 is a separate earlier commit.
- **Severity:** Minor
- **Gap or opportunity:** Both plans (Sub-item 2 Step 6 / Sub-item 3 Gate D) call for the
  buffered fix to land with or before the streamed fix, and for the two missing-library
  error paths to be verified identical at integration. Combining them in one commit is
  consistent with shipping a single coherent PR, but it removes the staged checkpoint the
  plans described and makes a clean partial revert of just one sub-item harder.
- **Recommended action:** Acceptable if this ships as one PR. If independent revertability of
  the buffered vs streamed fix matters, split into two commits. No code change required.
- **Disposition:** Defer

---

## Scope creep

Changes in the diff that cannot be tied to a specific code step of the work item or to a
specific item in the issue. Treated as Major by default. Surface so they can be reverted or
moved to a follow-up.

### SC1 — Planning, research, and execution markdown artifacts committed to the repo

- **Location:** `assumptions.md`, `assumptions.gao.md`, and all of
  `docs/brotli.1.plan.md`, `docs/brotli.1.execution.md`, `docs/brotli.1.research.md`,
  `docs/brotli.1.research.gao.md`, `docs/brotli.2.plan.md`, `docs/brotli.2.execution.md`,
  `docs/brotli.2.research.md`, `docs/brotli.2.research.gao.md`, `docs/brotli.3.plan.md`,
  `docs/brotli.3.execution.md`, `docs/brotli.3.research.md`, `docs/brotli.3.research.gao.md`
  (about 3,800 of the ~4,250 added lines in the diff).
- **Severity:** Major
- **Gap or opportunity:** These are process/working artifacts for the implementation effort,
  not part of the azure-core source change. They are not referenced by any code, package, or
  build step and do not belong to a step in the work item itself. Shipping them in the same
  diff as the azure-core fix inflates the change surface and would commit internal planning
  docs into the public SDK repo.
- **Recommended action:** Remove these from the PR that ships the azure-core fix (keep them
  in the working branch or a separate location). The shippable diff should be limited to
  `sdk/core/azure-core/` source, tests, test routes, and `CHANGELOG.md`.
- **Disposition:** Address

### SC2 — gzip/deflate idempotency and multi-chunk characterization tests

- **Location:**
  `tests/async_tests/test_universal_http_async.py::test_aiohttp_response_decompression_idempotent`,
  `test_aiohttp_response_unknown_encoding_passthrough`, and
  `tests/async_tests/test_streaming_async.py::test_streaming_decompress_multichunk_gzip` /
  `test_streaming_decompress_multichunk_deflate`.
- **Severity:** Minor (not true scope creep — tied to Sub-item 1)
- **Gap or opportunity:** These tests are not part of the `br` bug fixes, but they are
  explicitly called for by Sub-item 1's plan (Steps 1 and 5: pin gzip/deflate streaming and
  buffered idempotency before the refactor). They are correctly attributable to an approved
  plan step, so they are listed here only to confirm they were reviewed and are in scope, not
  to flag them for removal.
- **Recommended action:** Keep. No action.
- **Disposition:** Defer

---

## Success-criterion verdict

- Sub-item 1 (Refactor): met. The dispatch is unified into `_get_decompressor`, the encoding
  set stays `("gzip", "deflate")`, and behavior is preserved with added characterization
  tests.
- Sub-item 2 (Bug fix, buffered `br`): not met. The small-body defect is fixed, but G1
  introduces silent truncation for bodies larger than ~32 KB, and G2 shows the tests do not
  cover that case. Address G1 and G2 before this can be considered correct.
- Sub-item 3 (Bug fix, streamed `br`): met. The drain loop decodes large multi-chunk bodies
  correctly, the `decompress=False` opt-out is preserved, and the missing-library error is
  shared with the buffered path.
