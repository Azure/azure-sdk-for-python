# Plan — Sub-item 1: Unify decompression dispatch (Refactor)

Work item: supporting Brotli in azure-core
(GitHub issue [#47186](https://github.com/Azure/azure-sdk-for-python/issues/47186)).

Sub-item 1 is a **pure refactor**: extract the duplicated `gzip`/`deflate` decompressor
construction shared by the two aiohttp sites into one small helper, with no externally
observable change. It does **not** add `br` decoding (that is Sub-items 2 and 3).

Approval status used as a fact for this plan:
- D1 = (a): the refactor is approved and is done **before** the `br` bug fix, so the
  later `br` branch is added in one shared place instead of two.
- D2 = (a): minimal kernel — a small function that returns a decompressor or `None`.
- D3: required tests = multi-chunk aiohttp streaming gzip + explicit buffered idempotency;
  optional tests = unknown-encoding pass-through + streaming deflate.
- D4 = (a): the encoding set stays exactly `("gzip", "deflate")`; `br`/`zstd` excluded.

---

## 1. Selected decisions and rationale (from research)

- **D1 (a) — Do the refactor now, before the `br` fix.** Cleaning the duplicated branch
  into one helper first means the later `br` branch is applied once and cannot drift
  between the buffered and streaming sites. (research Section 6 D1; assumptions Sub-item 1
  ordering "first, if undertaken".)
- **D2 (a) — Minimal kernel only.** Extract only the encoding membership test, the
  `enc.lower()` normalization, the `wbits` selection, and the `zlib.decompressobj`
  construction into a helper that returns a decompressor for supported encodings or
  `None`. Each call site keeps its own lifecycle, content mutation, `_decompressed_content`
  flag, and return behavior. The helper must not own response objects, chunks, or the
  idempotency flag. Rationale: the two sites differ in lifecycle (one-shot vs stateful), so
  only a small kernel is safely shareable; a fuller abstraction risks turning a refactor
  into a behavior change. (research Section 6 D2 recommendation; Section 1 "What must stay
  at each site".)
- **D3 — Add the material characterization tests, kept proportional.** Required: a
  multi-chunk aiohttp streaming gzip test (the cross-chunk stateful decompressor is the
  thing most likely to break and is currently untested) and an explicit buffered
  idempotency test (because `_aiohttp_body_helper` is edited). Optional: unknown-encoding
  pass-through and streaming deflate. (research Section 3; Section 6 D3 recommendation.)
- **D4 (a) — Strictly exclude `br`/`zstd`.** The refactor keeps the encoding set exactly
  `("gzip", "deflate")` and preserves the silent fall-through for any other encoding.
  Folding `br` in would make this a behavior change, not a refactor. (research Section 6
  D4 recommendation; Section 2 "Unknown / absent encoding fall-through".)
- **Helper location.** Put the helper in
  `azure/core/utils/_pipeline_transport_rest_shared.py`. `_aiohttp.py` already imports
  `_aiohttp_body_helper` from that module, so the transport-to-utility dependency direction
  already exists. (research Section 5 U4; gao G4 Address.)
- **Keep `import zlib` lazy.** The helper keeps the `import zlib` inside the supported-
  encoding branch to preserve current import timing. (research Section 2 "Lazy import
  zlib timing"; gao G5.)
- **Errors propagate unchanged.** The helper must let `zlib`/decompression errors raise
  exactly as today — no broad `except`, no swallowing, no success-shaped fallback.
  (research Section 2 "Decompression error propagation"; gao G6 Address.)

---

## 2. Technical approach end-to-end (how behavior preservation will be proved)

This is a refactor, so the success criterion is: **externally observable behavior is
identical before and after.** The approach to prove it:

1. **Pin behavior first (characterization tests).** Before touching production code, add
   the required characterization tests against the *current* code and confirm they pass.
   These pin the behaviors the refactor is most likely to break: the persistent
   cross-chunk streaming decompressor and buffered idempotency. A test that passes on the
   old code and still passes on the new code is the proof of preservation.
2. **Extract a behavior-neutral kernel.** Introduce one helper that returns a decompressor
   (or `None`) for `("gzip", "deflate")`, preserving `enc.lower()`, the `wbits` branch,
   the lazy `import zlib`, and error propagation. The helper transforms nothing about
   lifecycle, content, flags, or headers.
3. **Re-point both sites to the helper** without changing their site-specific lifecycle,
   `_decompressed_content` flag, content mutation, return shape, or header source.
4. **Prove nothing else changed** by running the full existing aiohttp async test suite
   (buffered gzip/deflate decode, `_decompress=False` negatives, streaming gzip decode,
   streaming `decompress=False`) plus the new characterization tests, and confirming the
   public API surface and CHANGELOG are untouched (no behavior entry, since there is no
   externally observable change).

Invariant to hold throughout: the encoding set stays exactly `("gzip", "deflate")`; any
other encoding (including `br`, `zstd`, `identity`, absent) returns raw bytes and raises
nothing.

---

## 3. Step-by-step implementation plan

Ordered to minimize blast radius: tests that pin current behavior first, then the
lowest-risk extraction, then re-point the less sensitive site, then the most sensitive
site, then re-verify.

**Step 1 — Add required characterization tests against current code.**
- What: add (a) a multi-chunk aiohttp streaming gzip decode test that forces the compressed
  payload into several chunks (small `block_size` or a route yielding several compressed
  byte chunks) and asserts the final joined decoded bytes; (b) an explicit buffered
  idempotency test asserting a second `.body()` returns the same decoded bytes without
  re-decompressing.
- Where: `sdk/core/azure-core/tests/async_tests/test_streaming_async.py` (streaming) and
  `tests/async_tests/test_universal_http_async.py` (buffered), matching where existing
  aiohttp decode tests already live.
- Why this step: these behaviors are currently unguarded and are exactly what the refactor
  could silently break; pinning them first makes the refactor provable.
- Expected outcome: both tests pass on the unmodified code.
- Scope justification: research Section 3 "No multi-chunk streaming decode test" /
  "No buffered idempotency test" and Section 6 D3 required tests.

**Step 2 — Introduce the minimal shared helper.**
- What: add one small function in `_pipeline_transport_rest_shared.py` that takes the
  already-extracted, already-lowercased encoding value and returns a
  `zlib.decompressobj(...)` for `gzip`/`deflate` (with the existing `wbits` branch) or
  `None` for anything else. Keep `import zlib` lazy inside the supported-encoding branch.
  The helper does not touch response objects, chunks, flags, or headers, and adds no
  `except`.
- Where: `sdk/core/azure-core/azure/core/utils/_pipeline_transport_rest_shared.py`.
- Why this step: it creates the single source of truth for decompressor construction with
  zero call-site wiring yet, so it can be added with no behavior impact.
- Expected outcome: new helper exists and is unit-callable; no existing call sites changed
  yet; suite still green.
- Scope justification: research Section 6 D2(a) preferred shape; Section 5 U4 placement.

**Step 3 — Re-point the buffered site (`_aiohttp_body_helper`) to the helper.**
- What: replace the inline `wbits`/`decompressobj` construction (lines ~406-410) with a
  call to the helper; keep `enc = response.headers.get(...)`, the `enc.lower()`, the
  `_decompress`/`_decompressed_content` guards, the `response._content` mutation, the
  `_decompressed_content = True` set, and the final `return response._content`/raw
  fall-through exactly as today.
- Where: `sdk/core/azure-core/azure/core/utils/_pipeline_transport_rest_shared.py`
  (`_aiohttp_body_helper`).
- Why this step: the buffered site is one-shot and lower-sensitivity than streaming, so
  it is the safer of the two to convert first.
- Expected outcome: buffered gzip/deflate decode, `_decompress=False`, double-`.body()`
  idempotency, and unknown-encoding pass-through behave identically; suite + Step 1 buffered
  test green.
- Scope justification: assumptions Sub-item 1 ("unify duplicated `("gzip","deflate")`
  dispatch"); research Section 1 buffered site.

**Step 4 — Re-point the streaming site (`__anext__`) to the helper.**
- What: replace the inline `wbits`/`decompressobj` construction inside the
  `if not self._decompressor:` guard (lines ~464-468) with a call to the helper, assigning
  its result to `self._decompressor`. Preserve the single-construction guard, the
  per-chunk `self._decompressor.decompress(chunk)`, the `internal_response.headers` source,
  the `_decompress` opt-out, and the raw-chunk fall-through.
- Where: `sdk/core/azure-core/azure/core/pipeline/transport/_aiohttp.py`
  (`AioHttpStreamDownloadGenerator.__anext__`).
- Why this step: streaming is the highest-sensitivity path (stateful cross-chunk
  decompressor); converting it last, after the helper is proven by the buffered site,
  contains risk.
- Expected outcome: multi-chunk streaming gzip (Step 1 test) and existing streaming gzip /
  `decompress=False` tests pass; the decompressor is still built exactly once and reused.
- Scope justification: assumptions Sub-item 1; research Section 1 streaming site and
  Section 2 "Multi-chunk streaming relies on one persistent decompressor".

**Step 5 — Optional characterization tests (only if touched code warrants).**
- What: add unknown-encoding pass-through (assert a non-tuple encoding returns raw and
  raises nothing) and streaming `deflate` decode tests.
- Where: same async test modules as Step 1.
- Why this step: these pin the fall-through and the streaming negative-`wbits` deflate
  branch the helper now centralizes.
- Expected outcome: both pass on the refactored code.
- Scope justification: research Section 6 D3 optional tests.

**Step 6 — Full verification pass.**
- What: run the complete azure-core async aiohttp test suite plus all new tests; confirm
  no public API change and no CHANGELOG behavior entry is needed.
- Where: `sdk/core/azure-core`.
- Why this step: this is the proof that nothing else changed.
- Scope justification: assumptions Sub-item 1 acceptance ("preserve A9/A23/A24 — no
  externally observable change — and keep A29/A31 tests green").

---

## 4. Stop/go gates

- **Gate A (before Step 2).** Step 1 required tests must pass on unmodified code. If a
  characterization test cannot be made to pass on current code, stop: the behavior is not
  understood well enough to refactor safely.
- **Gate B (after Step 3).** Buffered suite + buffered idempotency test green. If any
  buffered behavior differs, stop and fix before touching the streaming site.
- **Gate C (after Step 4).** Multi-chunk streaming gzip and all existing streaming tests
  green. This is the highest-risk gate; do not proceed to merge if cross-chunk decode is
  not proven.
- **Gate D (after Step 6).** Full suite green, no API/CHANGELOG behavior change. Go/no-go
  for handing off to Sub-item 2 (`br` buffered fix).

---

## 5. Validation plan

Tests to run (existing):
- Buffered gzip/deflate decode on aiohttp responses (`test_universal_http_async.py`,
  including `test_aiohttp_response_decompression` / `_negative`).
- Streaming gzip decode offline and streaming `decompress=False`
  (`test_streaming_async.py`).

Tests to add:
- Required: multi-chunk aiohttp streaming gzip decode (force multiple compressed chunks,
  assert final joined decoded bytes); explicit buffered idempotency (second `.body()` ==
  first, no re-decompress).
- Optional: unknown-encoding pass-through (raw bytes, no raise); streaming `deflate` decode.

Invariants to assert:
- Encoding set remains exactly `("gzip", "deflate")`; `br`/`zstd`/`identity`/absent pass
  through raw and raise nothing.
- Streaming builds the decompressor once and reuses it across chunks.
- Buffered sets `_decompressed_content = True` once and does not double-decompress.
- `_decompress=False` returns raw bytes before any dispatch at both sites.
- `zlib` errors on invalid data propagate unchanged.

Observability checks:
- None required. This sub-item adds no logging, metrics, config, dependency, or public API.
  Verification is purely the test suite plus confirming the diff is internal-only.

---

## 6. Rollout strategy

- Single internal-only code change to azure-core; no public API, dependency, or packaging
  change, so rollout is the normal azure-core PR -> CI -> merge flow.
- Blast-radius containment: changes are limited to two private functions plus a new private
  helper in the same package; the encoding set and all guards are unchanged.
- Sequencing: land Sub-item 1 first (per D1=a), then build Sub-item 2 (`br` buffered) on
  the unified helper.
- Monitoring window: rely on the azure-core CI gate and the new characterization tests.
  No production telemetry change is introduced, so the monitoring surface is the test
  suite and downstream package CI that depends on azure-core.

---

## 7. Rollback plan

- Revert is a straightforward git revert of the single PR: re-inline the `wbits`/
  `decompressobj` construction at both sites and delete the helper. The two call sites
  return to their current independent form.
- Preconditions for safe revert: none beyond a clean revert; there is no migration, no
  persisted state, and no data format change.
- Data considerations: none. The change only affects in-memory decompression of response
  bytes; no stored data, recordings format, or wire format changes.
- Because the characterization tests are behavior pins (not new behavior), they can remain
  after a revert without failing; they describe pre-existing behavior.

---

## 8. Risks and mitigations

- **R1 — Cross-chunk streaming corruption** if the helper is called per chunk and rebuilds
  the decompressor. Mitigation: D2 keeps the `if not self._decompressor:` single-
  construction guard at the call site (Step 4); Gate C + multi-chunk test (Step 1) catch
  it. (research Section 2.)
- **R2 — Buffered double-decompress** if the `_decompressed_content` flag is moved into the
  helper. Mitigation: helper never owns the flag (D2); Step 3 keeps flag logic at the site;
  Gate B + idempotency test. (research Section 2.)
- **R3 — Accidentally handling `br`/`zstd` or starting to raise on unknown encodings.**
  Mitigation: D4 fixes the encoding tuple; optional unknown-encoding pass-through test
  (Step 5); invariant in Section 5. (research Section 6 D4.)
- **R4 — Swallowing or wrapping `zlib` errors** via a broad `except` in the helper.
  Mitigation: helper adds no `except` (D2/G6); errors propagate from the call-site
  `decompress` call as today. (research Section 2; gao G6.)
- **R5 — Wrong header source** if the helper reads from a response object. Mitigation:
  helper takes the already-extracted encoding string; each site keeps its own header source
  (`response.headers` vs `internal_response.headers`). (research Section 1.)
- **R6 — Import-timing change** if `import zlib` is hoisted to module top. Mitigation: keep
  it lazy inside the helper's supported-encoding branch (Step 2). (research Section 2; gao
  G5.)

---

## 9. Definition of done

- A single private helper in `_pipeline_transport_rest_shared.py` constructs the
  `gzip`/`deflate` decompressor; both `_aiohttp_body_helper` and
  `AioHttpStreamDownloadGenerator.__anext__` call it instead of inlining the construction.
- Encoding set is exactly `("gzip", "deflate")`; no `br`/`zstd` added; unknown encodings
  still pass through raw and raise nothing.
- Required characterization tests (multi-chunk streaming gzip, buffered idempotency) exist
  and pass; all pre-existing aiohttp async tests pass.
- No public API, dependency, packaging, logging, or config change; no CHANGELOG behavior
  entry (because there is no externally observable change).
- All four gates (A-D) cleared.

---

## 10. Open questions

- **OQ1 — Helper name and exact signature** (research U4/D2 residual). Close by picking a
  name and shape (encoding-in, decompressor-or-`None`-out) during Step 2 review; it does
  not affect behavior.
- **OQ2 — Optional tests inclusion** (research D3). Close during Step 5 by deciding whether
  the streaming-deflate and unknown-encoding tests are warranted by the final diff.
- **OQ3 — Whether the two aiohttp sites are the complete set of manual `zlib` dispatch
  points** (assumptions Q7 / research U5). Research confirmed only these two manual `zlib`
  sites; close by recording a repository search for `Content-Encoding` / `decompressobj`
  in azure-core before merge so the unification is known to be complete.

---

## 11. Out-of-scope observations

Noticed while planning. Recorded so they are not lost. NOT part of any plan step above.

- The unknown-encoding fall-through silently returns raw bytes for `br`, `zstd`, and
  `identity` alike. Decoding `br` is Sub-items 2/3; `zstd` is assumptions Q4. Not this
  refactor.
- The `Content-Encoding` header is re-parsed on every streaming chunk in `__anext__`. It
  could be parsed once at generator construction, but that is a behavior-shape change, not
  part of unifying the duplicated dispatch. (research Out-of-scope; gao G16 Defer.)
- Header normalization is exact-match lowercase only; it does not trim whitespace or handle
  comma-separated `Content-Encoding` values. Preserving the current simple behavior is in
  scope; expanding it is a separate decision. (gao G3 Defer.)
- The two sites read headers from different objects (`response.headers` vs
  `internal_response.headers`); correct today, noted only so the shared helper does not
  unify the header source.
- Sync `requests`/`urllib3` transports decompress via their own stack and are untouched;
  confirms the refactor's blast radius is the two aiohttp functions only.
