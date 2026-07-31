# Brotli sub-items 1-3 — execution log

## Code GAO fixes

Fixes applied from `docs/brotli.1-3.code.gao.md` (items marked **Address** only).

- **G1 — Buffered `br` decode silently truncates bodies larger than ~32 KB**
  - File: `sdk/core/azure-core/azure/core/utils/_pipeline_transport_rest_shared.py`
  - Change: `_decode_brotli_content` now decodes through a shared draining helper
    (`_drain_brotli_decompress`) that feeds the content once and then loops
    `decompress(b"")` until empty, concatenating the held output instead of returning a
    single capped buffer.
  - Scope justification: Satisfies G1 (Address) — corrects the new large-body truncation
    defect so Sub-item 2's "buffered `br` round-trips, nothing else changed" success
    criterion holds.

- **G3 — Buffered and streamed `br` decode logic is duplicated and can drift**
  - Files: `sdk/core/azure-core/azure/core/utils/_pipeline_transport_rest_shared.py`,
    `sdk/core/azure-core/azure/core/pipeline/transport/_aiohttp.py`
  - Change: Added `_drain_brotli_decompress(decompressor, data)` in the shared module as
    the single source of truth for resolving `decompress_sync`/`decompress` and draining
    the held output. `_decode_brotli_content` (buffered) and the streamed `__anext__`
    `br` branch both call it; the inline drain loop in `_aiohttp.py` was removed and the
    helper imported.
  - Scope justification: Satisfies G3 (Address) — centralizes the decode so the buffered
    and streamed sites cannot diverge again, restoring Sub-item 1's single-source-of-truth
    intent.

- **G2 — Buffered `br` tests only exercise an 11-byte body, so G1 is not caught**
  - File: `sdk/core/azure-core/tests/async_tests/test_universal_http_async.py`
  - Change: Added `test_aiohttp_response_brotli_decompression_large`, which compresses a
    45 KB payload (`b"the quick brown fox jumps over the lazy dog. " * 1000`, the same body
    the streamed multi-chunk test uses) and asserts `res.body()` equals the original bytes.
    Added a guarded `import brotli as _brotli` to build the payload, with the test skipped
    when Brotli is unavailable.
  - Scope justification: Satisfies G2 (Address) — exercises a payload larger than the
    ~32 KB per-call cap; verified it fails before the G1 fix (one-shot decode yields 32,752
    of 45,000 bytes) and passes after.

### Verification

- `pytest tests/async_tests/test_universal_http_async.py -k brotli` — 8 passed.
- `pytest tests/async_tests/test_streaming_async.py -k "brotli or multichunk or decompress"` — 16 passed.
- Manual check confirmed aiohttp `BrotliDecompressor.decompress_sync` truncates the 45 KB
  payload to 32,752 bytes in a single call (the defect the new test now guards).

## Out-of-scope observations

None encountered while applying the above fixes. Items G4–G9, SC2 in the code GAO are
marked **Defer** and were intentionally left unchanged. SC1 (**Address**) — removing the
planning/research/execution markdown artifacts from the shippable PR — was not applied here
because it conflicts with the active instruction to maintain this execution log and is a
PR-composition decision deferred to the author (see session note); no code change is
involved.
