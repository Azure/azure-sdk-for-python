# Research — Sub-item 1: Unify decompression dispatch

Work item: supporting brotli in azure-core
(GitHub issue [#47186](https://github.com/Azure/azure-sdk-for-python/issues/47186))

Sub-item 1: **"Unify decompression dispatch" (Refactor) — optional/conditional.**

Scope of this research: only the unification of the duplicated `gzip`/`deflate`
decompression dispatch that exists in two aiohttp sites. This is a pure refactor:
externally observable behavior must not change. It does **not** add `br` decoding —
that is Sub-items 2 and 3. This document proposes no fix and contains no code.

This refactor is explicitly marked optional and conditional in
[assumptions.md](../assumptions.md): it should only proceed if maintainers lift the
current out-of-scope flag on this cleanup. See Decisions (Section 6).

**Hard gate.** Do not implement this sub-item unless maintainers explicitly approve the
refactor. If approval is not given, do not change any code under this sub-item: fix
Brotli directly in the two current sites (Sub-items 2 and 3), or keep this document as a
deferred observation only.

---

## 1. Delta from current state

### The two duplicated sites
Today the same `zlib`-based decompression dispatch is written out independently in two
places:

- **Buffered site** — `_aiohttp_body_helper` in
  `sdk/core/azure-core/azure/core/utils/_pipeline_transport_rest_shared.py`
  (lines 381-414). Decompresses the whole body in one call:
  ```
  402  enc = response.headers.get("Content-Encoding")
  403  if not enc:
  404      return response._content
  405  enc = enc.lower()
  406  if enc in ("gzip", "deflate"):
  407      import zlib
  408      zlib_mode = (16 + zlib.MAX_WBITS) if enc == "gzip" else -zlib.MAX_WBITS
  409      decompressor = zlib.decompressobj(wbits=zlib_mode)
  410      response._content = decompressor.decompress(response._content)
  411      response._decompressed_content = True
  412      return response._content
  413  return response._content
  ```

- **Streaming site** — `AioHttpStreamDownloadGenerator.__anext__` in
  `sdk/core/azure-core/azure/core/pipeline/transport/_aiohttp.py` (lines 450-469).
  Decompresses chunk-by-chunk with a decompressor kept on `self`:
  ```
  458  enc = internal_response.headers.get("Content-Encoding")
  459  if not enc:
  460      return chunk
  461  enc = enc.lower()
  462  if enc in ("gzip", "deflate"):
  463      if not self._decompressor:
  464          import zlib
  465          zlib_mode = (16 + zlib.MAX_WBITS) if enc == "gzip" else -zlib.MAX_WBITS
  466          self._decompressor = zlib.decompressobj(wbits=zlib_mode)
  467      chunk = self._decompressor.decompress(chunk)
  468  return chunk
  ```

### What the refactor would change
The refactor pulls the part that is genuinely identical into one shared place so the
two sites cannot drift apart. The truly common kernel is small:

- the encoding tuple `("gzip", "deflate")` and the membership test,
- the `enc.lower()` normalization,
- the `wbits` selection `(16 + zlib.MAX_WBITS) if enc == "gzip" else -zlib.MAX_WBITS`,
- the `zlib.decompressobj(wbits=...)` construction.

- Justification: the work item's refactor is exactly "remove the duplicated
  `("gzip", "deflate")` dispatch across the two sites," nothing wider.

### What must stay at each site (cannot be unified without changing behavior)
The two sites are not the same shape, and these differences must remain at the call
sites, not be folded into the shared kernel:

- **Lifecycle.** Buffered builds a throwaway decompressor and decodes once. Streaming
  builds the decompressor **once** and keeps it on `self._decompressor` across many
  `__anext__` calls. The shared kernel can build a decompressor, but the streaming site
  must still own when it is created and reused.
  - Justification: collapsing one-shot and stateful lifecycles into one abstraction is
    where a "pure" refactor could silently break multi-chunk streams.
- **State flag.** Buffered sets `response._decompressed_content = True` for idempotency;
  streaming has no such flag. This flag logic must stay buffered-only.
  - Justification: applying or dropping the flag in the wrong place changes
    double-read behavior.
- **Content mutation vs return.** Buffered mutates `response._content`; streaming
  returns a local `chunk`. These are site-specific.
  - Justification: the shared kernel should transform bytes, not own where they land.
- **Header source.** Buffered reads `response.headers`; streaming reads
  `internal_response.headers`. If the shared kernel took a response object it could read
  the wrong headers; passing the already-extracted header value avoids this.
  - Justification: a wrong header source would change which responses decode.

### Areas most sensitive to the change
- The streaming generator's stateful decompressor (`self._decompressor`) — highest
  sensitivity, because correctness depends on building it exactly once and reusing it.
  - Justification: the refactor edits the lines that create/reuse this object.
- The buffered idempotency flag (`_decompressed_content`) and the `_content`
  reassignment — second-most sensitive.
  - Justification: the refactor edits the lines around this flag.
- The unknown-encoding fall-through (`return response._content` / `return chunk`) which
  today returns raw bytes for any encoding not in the tuple (including `br`).
  - Justification: the refactor must preserve this exact silent fall-through, since the
    `br` decode is deliberately a different sub-item.

These are the only two manual `zlib` dispatch sites in azure-core; the sync
`requests`/`urllib3` transports do not decompress manually and are not touched.
- Justification: confirms the refactor's blast radius is exactly these two functions.

---

## 2. Behavioral risk

Behaviors that are implicit today and could change by accident during unification:

- **Multi-chunk streaming relies on one persistent decompressor.** A `zlib`
  decompressor carries state between chunks. If the shared kernel is called per chunk
  and (re)constructs the decompressor, a stream split across chunks would corrupt after
  the first chunk. The current single-construction guard (`if not self._decompressor`)
  must be preserved.
  - Justification: the refactor edits exactly this construction/reuse logic.
- **Buffered idempotency (double read).** A second `.body()` call must not
  double-decompress. This depends on `_decompressed_content` being set the first time
  and checked before dispatch. If unification moves or drops the flag, a double read
  could decode twice and corrupt.
  - Justification: the refactor edits the lines that set this flag.
- **Opt-out (`_decompress=False`).** Both sites return raw bytes before any dispatch
  when decompression is disabled. The guard ordering must stay before the shared call.
  - Justification: the refactor sits right after these guards.
- **Unknown / absent encoding fall-through.** With no `Content-Encoding`, or an
  encoding not in the tuple (today this includes `br`, `zstd`, `identity`), both sites
  return the bytes untouched and raise nothing. The refactor must reproduce this exact
  silent pass-through — it must not start raising or start handling `br`.
  - Justification: adding `br` here would smuggle Sub-item 2/3 into a refactor and turn
    it into a behavior change.
- **Header normalization.** `enc.lower()` and the case-insensitive header lookup must be
  preserved so `"GZIP"`, `"Deflate"`, etc. still match.
  - Justification: the refactor moves this normalization into shared code.
- **Lazy `import zlib` timing.** Both sites import `zlib` lazily, inside the decode
  branch. Moving the import to module top level is behavior-neutral for output but
  changes import timing and could affect import-time cost or any environment that
  inspects imports. Low risk, but it is a change from the current lazy pattern.
  - Justification: the refactor relocates the `import zlib` line.
- **`deflate` wbits sign.** The raw-deflate mode uses negative `wbits`
  (`-zlib.MAX_WBITS`); gzip uses `16 + zlib.MAX_WBITS`. A unified `wbits` helper must
  keep this exact branch, including the `enc == "gzip"` test rather than a looser check.
  - Justification: the refactor centralizes this exact computation.
- **Decompression error propagation.** Today invalid `gzip`/`deflate` data raises the
  underlying `zlib.error` in the buffered code, and the streaming path maps some aiohttp
  errors but not `zlib` errors. A shared helper must let these decompression errors
  propagate exactly as they do today. It must not add a broad `except`, swallow the
  error, or return a success-shaped fallback.
  - Justification: the refactor wraps the decode call where these errors are raised.

---

## 3. Test and verification gaps

What protects these behaviors today, and where the refactor is unguarded:

Existing coverage:
- Buffered gzip and deflate decode on aiohttp responses:
  `test_universal_http_async.py` constructs `AioHttpTransportResponse` and
  `RestAioHttpTransportResponse` directly and exercises decode
  (`tests/async_tests/test_universal_http_async.py`). These are the direct aiohttp
  decode tests that protect `_aiohttp_body_helper`.
- Buffered gzip on the legacy response plus a `_decompress=False` negative:
  `test_aiohttp_response_decompression` / `_negative`
  (`tests/async_tests/test_universal_http_async.py` L133-180).
- Streaming gzip decode (offline): `test_decompress_compressed_header_offline`
  (`tests/async_tests/test_streaming_async.py` L134-145), and a streaming
  `decompress=False` case (L40-49).

Gaps that leave this refactor under-protected:
- **No multi-chunk streaming decode test.** Every streaming test body is the 4-byte
  string `b"test"` (`test_routes/streams.py` `streaming_test` / `compressed_stream`),
  which fits in one chunk. The stateful cross-chunk decompressor — the exact thing this
  refactor is most likely to break — is never exercised. A useful characterization test
  must force the compressed payload to be read in multiple chunks: set a small
  `block_size` or use a route that yields several compressed byte chunks, then assert the
  final joined decoded bytes. Small decoded text like `b"test"` is not enough, because
  the test server often yields the whole compressed body at once. This directly protects
  the persistent `self._decompressor` behavior.
  - Justification: the refactor edits the stateful streaming decompressor; a single-chunk
    test would still pass even if cross-chunk reuse were broken.
- **No streaming `deflate` test.** Streaming tests only cover gzip. The negative-`wbits`
  deflate branch on the streaming side is uncovered, so a refactor that mishandles the
  deflate `wbits` for streaming would not be caught.
  - Justification: the refactor centralizes the `wbits` computation used by both
    encodings and both sites.
- **No buffered idempotency (double `.body()`) test.** Nothing asserts that a second
  buffered read returns the same decoded bytes without re-decompressing.
  - Justification: the refactor edits the `_decompressed_content` flag that guarantees
    this.
- **No explicit unknown-encoding pass-through test.** Nothing asserts that an encoding
  not in the tuple is returned raw and unraised. This is the behavior that keeps the
  refactor from accidentally swallowing or altering `br`.
  - Justification: the refactor must preserve this fall-through exactly.

Note: these gaps would normally argue for adding characterization tests *before*
refactoring, so the refactor can be proven behavior-preserving. Adding such tests is a
verification aid for this refactor, not a `br` feature.
- Justification: each suggested test pins an existing behavior the refactor touches; none
  adds new behavior.

---

## 4. Operational and non-functional risk

- **Startup / import cost.** If the shared kernel moves `import zlib` to module top
  level, `zlib` (a stdlib C module, already effectively always available) would import
  at module load instead of first decode. Negligible, but it is a real change from the
  current lazy import.
  - Justification: the refactor relocates the lazy `import zlib`.
- **Performance — buffered.** Whole-body decode is unchanged in cost; only the call
  shape changes. A risk only if the shared helper introduces an extra copy of
  `response._content`.
  - Justification: the refactor wraps the existing single `decompress` call.
- **Performance — streaming.** The streaming path is hot (per chunk). A shared helper
  adds one function call per chunk; trivial, *provided* it does not re-evaluate
  header/encoding parsing or re-create the decompressor each chunk. The current code
  parses the header every chunk already, so parity is the bar, not improvement.
  - Justification: the refactor sits in the per-chunk loop.
- **Memory.** No change expected; the refactor does not alter buffering strategy or hold
  extra references, as long as the streaming decompressor stays singular.
  - Justification: the refactor does not change what is buffered.
- **Observability / configuration / deployment.** None. No public API, no logging, no
  config, no dependency, no packaging change. The two functions are internal.
  - Justification: the refactor is internal code movement only.

---

## 5. Unknowns

- **U1. Is the refactor sanctioned?** assumptions.md marks it optional and "only if
  maintainers lift the current out-of-scope flag." Whether to do it at all is the gating
  unknown.
  - Justification: the work item itself labels this sub-item conditional.
- **U2. How much should be unified?** The lifecycle difference (one-shot vs stateful)
  means only a small kernel is safely shareable. Whether to unify just the
  `wbits`/decompressor construction, or attempt a fuller shared dispatch, needs a human
  call on the acceptable abstraction.
  - Justification: over-unifying risks turning a refactor into a behavior change.
- **U3. Ordering vs the `br` bug fix.** assumptions.md recommends refactor-first so the
  `br` branch is added once. But refactor-first means changing currently-correct code
  before the bug is fixed. Sequence needs confirmation.
  - Justification: ordering determines whether the `br` fix lands in one shared site or
    two.
- **U4. Where should the shared kernel live?** The buffered helper lives in
  `utils/_pipeline_transport_rest_shared.py`; the streaming generator in
  `pipeline/transport/_aiohttp.py`. The transport-to-utility dependency direction
  already exists: `_aiohttp.py` already imports `_aiohttp_body_helper` from
  `azure.core.utils._pipeline_transport_rest_shared`. Preferred option: put the small
  encoding/decompressor helper in `_pipeline_transport_rest_shared.py` unless maintainers
  object. This unknown is then only about the helper's name and exact shape, not the
  module direction.
  - Justification: placement affects import structure; the existing import direction
    makes the shared module the natural home.
- **U5. Are the two sites truly the complete set?** This research confirmed only these
  two manual `zlib` sites in azure-core (Section 1). This matches assumptions Q7, which
  is still listed as needing confirmation.
  - Justification: a missed third site would leave the duplication partially unsolved.

---

## 6. Decisions

These need your input. Alternatives are listed; please pick. Answers will be recorded
here.

- **D1 — Do the refactor at all?**
  - (a) Proceed now, before the `br` bug fix, so `br` is added in one shared place.
  - (b) Proceed but after the `br` bug fix (clean up the two sites once both decode `br`).
  - (c) Do not do it now; keep it as an out-of-scope observation and fix `br` in both
    sites directly.
  - (d) Do not implement this sub-item until maintainers approve the optional refactor.
    This is the default while the current out-of-scope flag remains.
  - **Your answer:** _pending_

- **D2 — How much to unify?**
  - (a) Minimal: extract only the `wbits` selection and `zlib.decompressobj`
    construction (and possibly the encoding-tuple/lowercase check); leave lifecycle,
    the `_decompressed_content` flag, and content/chunk handling at each site.
  - (b) Fuller: a single dispatch entry the two sites call, parameterized for one-shot
    vs stateful use.
  - **Recommendation:** (a) — lowest behavioral risk, matches "pure refactor." Preferred
    implementation shape: a small function that returns a decompressor for supported
    encodings or `None`; each call site keeps its own lifecycle, content mutation, flags,
    and return behavior. The helper must not own response objects, chunks, or
    `_decompressed_content`.
  - **Your answer:** _pending_

- **D3 — Add characterization tests first?**
  - (a) Add multi-chunk streaming, streaming-deflate, buffered idempotency, and
    unknown-encoding pass-through tests *before* refactoring, to prove behavior is
    preserved.
  - (b) Refactor first, rely on existing tests only.
  - **Recommendation:** split the tests into required and optional. Required: multi-chunk
    aiohttp streaming gzip, and explicit buffered idempotency if `_aiohttp_body_helper`
    is edited. Optional: unknown-encoding pass-through and streaming deflate, added only
    if the touched code warrants it. The most sensitive behavior (cross-chunk streaming)
    is currently untested and is the material test for this sub-item.
  - **Your answer:** _pending_

- **D4 — Strictly exclude `br`/`zstd` from this refactor?**
  - (a) Yes: this refactor keeps the encoding set exactly `("gzip", "deflate")` and
    preserves the silent fall-through; `br`/`zstd` are separate sub-items.
  - (b) No: fold `br` in here.
  - **Recommendation:** (a) — folding in `br` makes this a behavior change, not a
    refactor.
  - **Your answer:** _pending_

---

## Out-of-scope observations

Noticed while researching. Recorded so they are not lost. NOT part of Sub-item 1.

- The unknown-encoding fall-through silently returns raw bytes for `br`, `zstd`, and
  `identity` alike. Handling any of these is a separate sub-item (Sub-items 2/3 for
  `br`; `zstd` is assumptions Q4), not this refactor.
- The header is re-parsed on every streaming chunk in `__anext__`. It could be parsed
  once when the generator is created. That is a micro-optimization and a behavior-shape
  change, not part of unifying the duplicated dispatch.
- The `import zlib` is lazy at both sites. Whether to keep it lazy or hoist it is a
  style choice that should be settled inside D2, not expanded into a separate cleanup.
- The two sites read headers from different objects (`response.headers` vs
  `internal_response.headers`). This is correct today; noted only because a shared
  helper must not unify the header *source*.

---

## GAO fixes

Fixes applied from `docs/brotli.1.research.gao.md`. Only items marked Address were
applied. Items marked Defer were left unchanged.

- **G1** — Introduction (Section before Section 1). Added a "Hard gate" paragraph stating
  the sub-item must not be implemented unless maintainers explicitly approve the refactor,
  and that without approval the code is not changed (fix Brotli in the two current sites
  or keep this as a deferred observation).
- **G4** — Section 5, U4. Added the concrete preferred location: put the
  encoding/decompressor helper in `_pipeline_transport_rest_shared.py`, noting that
  `_aiohttp.py` already imports `_aiohttp_body_helper` from that module so the dependency
  direction already exists. Narrowed U4 to the helper's name and shape.
- **G6** — Section 2, behavioral risk. Added a risk item that decompression errors must
  propagate exactly as today, with no broad catch, no swallowing, and no success-shaped
  fallback.
- **G7** — Section 3, existing coverage. Replaced the inaccurate
  `test_rest_asyncio_transport.py` citation (which uses `AsyncioRequestsTransport`, not
  aiohttp) with the direct aiohttp coverage in `test_universal_http_async.py` that
  constructs `AioHttpTransportResponse` and `RestAioHttpTransportResponse`.
- **G9** — Section 3, "No multi-chunk streaming decode test." Specified that the
  characterization test must force the compressed payload into multiple chunks (small
  `block_size` or a route yielding several compressed chunks) and assert the final joined
  decoded bytes, noting `b"test"` is not enough.
- **G13** — Section 6, D1. Added option (d): do not implement this sub-item until
  maintainers approve the optional refactor, marked as the default while the out-of-scope
  flag remains.
- **G14** — Section 6, D2. Added the preferred implementation shape to the (a)
  recommendation: a small function returning a decompressor or `None`, with each call
  site keeping lifecycle, mutation, flags, and return behavior, and the helper not owning
  response objects, chunks, or `_decompressed_content`.
- **G15** — Section 6, D3. Split the tests into required (multi-chunk aiohttp streaming
  gzip, plus buffered idempotency if `_aiohttp_body_helper` is edited) and optional
  (unknown-encoding pass-through and streaming deflate).
