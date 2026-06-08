# Research — Sub-item 3: Decode `br` in the streaming path

Work item: supporting brotli in azure-core
(GitHub issue [#47186](https://github.com/Azure/azure-sdk-for-python/issues/47186))

Sub-item 3: **"Decode `br` in the streaming path" (Bug fix) — conditional on Q6.**

Scope decision (recorded with manager): **Q6 = in scope, sequenced after Sub-items 1
and 2.** This sub-item is confirmed as in scope for this work item — not a deferred
follow-up — and is to be done **after** Sub-item 1 (unify decompression dispatch, if
approved) and Sub-item 2 (decode `br` in the buffered helper). This document researches
the streaming `br` gap fully — its manifestation, root cause, blast radius, and test
gaps — so it can be implemented immediately after the buffered fix lands. It proposes no
fix and contains no code.

Note on the source-of-truth: `assumptions.md` still records Q6 as unresolved and
streaming as conditional. That source-of-truth must be updated to record this Q6
decision before streaming is treated as approved implementation scope.

Fallback sequence: Sub-item 1 (unify decompression dispatch) is optional and still has
pending decisions. If Sub-item 1 is not approved, implement streaming `br` directly after
the buffered helper (Sub-item 2). The streaming fix does not need to wait for the optional
refactor.

The buffered helper is the primary fix (Sub-item 2, see
[brotli.2.research.md](brotli.2.research.md)) and is researched separately. The
streaming path is the second site with the same missing-branch defect and is fixed in
the same work item, right after the buffered helper.

---

## 1. How and where the bug manifests

### The failing site
The streaming decode lives in `AioHttpStreamDownloadGenerator.__anext__` in
`sdk/core/azure-core/azure/core/pipeline/transport/_aiohttp.py` (lines 450-469).
For each chunk it reads, it inspects `Content-Encoding` and only handles `gzip` and
`deflate`:

```
458  enc = internal_response.headers.get("Content-Encoding")
459  if not enc:
460      return chunk
461  enc = enc.lower()
462  if enc in ("gzip", "deflate"):
463      if not self._decompressor:
464          import zlib
465
466          zlib_mode = (16 + zlib.MAX_WBITS) if enc == "gzip" else -zlib.MAX_WBITS
467          self._decompressor = zlib.decompressobj(wbits=zlib_mode)
468      chunk = self._decompressor.decompress(chunk)
469  return chunk
```

When `Content-Encoding: br`, `enc` is `"br"`, the `("gzip", "deflate")` branch is
skipped, and line 469 returns the still-compressed Brotli chunk unchanged.

- Justification: this is the same missing-branch defect named in the work item, in the
  streaming site rather than the buffered helper; `br` is not in the only encoding
  tuple that triggers decompression.

### Difference from the buffered helper (why this is a distinct site)
The buffered helper (`_aiohttp_body_helper`) decompresses the whole body in one call.
The streaming generator decompresses chunk-by-chunk and keeps a **stateful**
`self._decompressor` (a `zlib.decompressobj`) across `__anext__` calls so a stream
spanning many chunks decodes correctly. Any `br` handling here must be incremental in
the same way, which is why fixing the buffered helper does not also fix this path.

Incremental decompressors can also hold trailing output until the stream ends. Today
`__anext__` only returns `decompress(chunk)` and raises stop when no input remains.
During implementation planning, verify whether aiohttp's `BrotliDecompressor` needs a
`flush()` or equivalent finalization call when the stream ends, and add a test that would
catch lost trailing bytes.

- Justification: confirms Sub-item 3 is a genuinely separate fix site, not a duplicate
  of Sub-item 2, tying the streaming gap to the work item's `br` correctness goal.

### How callers hit it
`__anext__` backs the public async streaming surface. The generator is wired in two
ways:

- Legacy transport: `AioHttpTransportResponse.stream_download` returns
  `AioHttpStreamDownloadGenerator` (`_aiohttp.py` L600).
- New `rest` transport: `RestAioHttpTransportResponse` passes
  `stream_download_generator=AioHttpStreamDownloadGenerator` (`rest/_aiohttp.py` L191),
  which backs `iter_bytes()` on the response. `iter_raw()` is the raw opt-out surface: it
  intentionally passes `decompress=False` and is expected to return raw Brotli bytes, so
  it is not part of the decoded-behavior defect.

`AsyncHttpResponseImpl.read()` also reaches this path: it builds cached content by
iterating `iter_bytes()`. So a streamed `br` gap can also affect async `.read()` when the
body has not already been buffered.

So any consumer iterating a streamed response (`async for chunk in
response.iter_bytes()`, `stream_download(...)`, or `b"".join([...])`) over the async
aiohttp transport receives raw Brotli chunks for a `br` body.

- Justification: ties the single streaming defect to every async streaming entry point
  the reporter could call, matching the work item's "transparent decode" expectation.

### Why a `br` response reaches azure-core at all
Same root condition as the buffered case: azure-core creates the aiohttp
`ClientSession` with `auto_decompress=False` (`_aiohttp.py` ~L192) and re-implements
decompression itself, but does not pin `Accept-Encoding`. aiohttp then advertises `br`
whenever a Brotli library is importable, so a compliant server may legitimately answer
`Content-Encoding: br` — which the streaming path cannot decode.

- Justification: confirms this is the same self-inflicted correctness gap (the SDK
  advertises `br` then fails to honor it) on the streaming surface.

---

## 2. Root cause and alternative hypotheses

### Most likely root cause (primary)
The encoding dispatch in `__anext__` enumerates only `("gzip", "deflate")` (line 462).
`br` is unlisted, so the chunk is returned compressed at line 469. The bug is a missing
encoding branch in the streaming generator, mirroring the buffered helper.

- Evidence: lines 462 and 469 above; there is no `br`, `brotli`, or `BrotliDecompressor`
  reference anywhere in `_aiohttp.py`.
- Justification: directly matches the work item's named root cause, applied to the
  streaming site.

### Alternative hypothesis A — decode disabled by the `decompress` flag
Could chunks be returned raw because streaming was opted out? The guard at lines
456-457 (`if not self._decompress: return chunk`) does exactly that. Ruled out for the
default path: `stream_download` defaults `decompress=True` (`_aiohttp.py` L588/L600),
and the value flows from `decompress=not auto_decompress`. With the default session
(`auto_decompress=False`), `_decompress` is `True`, so execution reaches the encoding
check and still skips `br`.

- Justification: rules out a configuration cause so the fix stays on the missing
  branch.

### Alternative hypothesis B — header casing / parsing
Could `br` be missed due to header name/value casing? Ruled out: `enc` is lowercased at
line 461 and aiohttp headers are case-insensitive on lookup, so `"br"` is matched
reliably; it is simply not in the tuple.

- Justification: confirms the defect is tuple membership, not header handling.

### Alternative hypothesis C — wrong layer (should be fixed in a transport/policy)
Could the real fix belong in `ContentDecodePolicy` or the sync transports? Ruled out:
sync `requests`/`urllib3` streaming decodes `br` itself, and `ContentDecodePolicy`
operates on already-decoded content. The manual `zlib`-based chunk decode that omits
`br` lives only in this aiohttp streaming generator.

- Justification: keeps the fix at the single layer that actually drops streamed
  `br`.

---

## 3. Affected behavior and blast radius

Who sees wrong behavior today when a server returns `Content-Encoding: br` over the
async aiohttp transport and the response is **streamed**:

- **Streamed byte reads (decoded surfaces)** — any caller of `response.iter_bytes()` or
  the default `stream_download(..., decompress=True)` on `RestAioHttpTransportResponse` or
  `AioHttpTransportResponse` receives raw Brotli chunks instead of decoded content.
  - Justification: these decoded surfaces route through the unmodified `__anext__`.
- **Raw opt-out surfaces (not a defect)** — `response.iter_raw()` and
  `stream_download(..., decompress=False)` are expected to return raw Brotli bytes; raw
  chunks here are the documented opt-out behavior, not the bug.
  - Justification: separates the decoded surfaces that must change from the opt-out
    surfaces that are already correct.
- **Streamed text / accumulation** — code that joins streamed chunks and decodes them
  (`b"".join([...]).decode("utf-8")`) raises `UnicodeDecodeError`, the same symptom as
  the buffered case.
  - Justification: matches the issue's stated failure mode, on the streaming surface.
- **Large-download consumers** — streaming is the path used for large payloads
  precisely to avoid buffering; those consumers silently get corrupt (still-compressed)
  data per chunk.
  - Justification: identifies the consumers most likely to rely on streaming and thus
    most exposed to the streamed `br` gap.

Scope limits of the blast radius:
- **Only the async aiohttp transport** is affected. Sync `requests`-based streaming
  generators (`StreamDownloadGenerator`, `AsyncioStreamDownloadGenerator`) are
  unaffected because `urllib3` decodes `br` itself.
  - Justification: bounds the blast radius to the streaming aiohttp path.
- **Only when a Brotli library is importable on the client** (otherwise aiohttp does
  not advertise `br`, so a compliant server will not send it; an unsolicited `br` from a
  non-compliant server is the Foundry case).
  - Justification: explains why not every user hits this and why the missing-library
    behavior matters.
- **The buffered helper is also wrong today** and is the separate primary sub-item
  (Sub-item 2), fixed first; not folded in here.
  - Justification: noted for completeness without widening this sub-item.

---

## 4. Test coverage gaps

Existing coverage around the streaming aiohttp path:
- Server stream routes `/streams/decompress_header` and related gzip routes exist
  (`tests/.../test_routes/streams.py` L65-94); they emit only `Content-Encoding: gzip`.
  There is **no `br` stream route**.
- Async streaming decode is asserted for gzip via the aiohttp transport in
  `tests/async_tests/test_streaming_async.py`
  (`test_decompress_compressed_header_offline`, L134-145); there is **no `br`
  equivalent**.
- The encoding routes file (`tests/.../test_routes/encoding.py`) defines `/gzip` and
  `/deflate` but **no `/br`** route that could feed a streamed `br` test.
- Sync streaming tests in `tests/test_streaming.py` cover gzip/deflate stream decode
  and `decompress=False`; **no `br`** case and, regardless, they exercise the sync
  transport, not `__anext__`.

Gaps that leave this streaming bug unprotected:
- **No test asserts a streamed `br` body round-trips** to the original bytes/text
  through `iter_bytes()` / `stream_download(...)` over the aiohttp transport.
  - Justification: the exact streaming behavior the fix must guarantee is
    untested.
- **No test asserts multi-chunk `br` decode** — that a `br` stream split across several
  `__anext__` chunks reassembles correctly using the stateful decompressor.
  - Justification: the streaming path's defining behavior (incremental decode) is the
    most likely place a `br` fix could go wrong and is currently uncovered.
- **No test for the `decompress=False` streamed `br` case** — that raw Brotli chunks
  are returned untouched when decode is opted out.
  - Justification: gzip/deflate have this negative test; the `br` equivalent is needed
    to protect the opt-out path.
- **No test for the missing-library streamed case** — that receiving a `br` stream with
  no Brotli library raises a clear, actionable error rather than opaque corrupt chunks.
  - Justification: this is the decided behavior (Decision D3) and is currently
    unverified for streaming.
- **No test for the async `read()` cache path** — `AsyncHttpResponseImpl.read()` joins
  `iter_bytes()` and stores `_content`, so a broken streaming `br` path could also poison
  cached content. A test for `RestAioHttpTransportResponse.read()` (or an equivalent rest
  response path that consumes `iter_bytes()`) should verify cached content decodes
  correctly for a `br` body.
  - Justification: the cache path reuses the streaming generator and is currently
    uncovered for `br`.

---

## 5. Decisions

Decisions raised and answered with the manager (recorded for the implementation phase):

- **D1 — Is streaming `br` in scope now or a follow-up? (resolves assumptions Q6)**
  Alternatives: (a) in scope now, sequenced after Sub-items 1 and 2; (b) follow-up only.
  **Answer: (a) In scope, sequenced after Sub-items 1 and 2.** This is part of the
  current work item — fixed right after Sub-item 1 (unify dispatch, if approved) and
  Sub-item 2 (buffered helper), not deferred.
  - Justification: the streaming `__anext__` carries the same missing-`br`-branch defect
    as the named buffered root cause, so leaving it unfixed would leave streamed `br`
    responses broken; sequencing it after Sub-items 1 and 2 lets the buffered fix (and
    any unified dispatch) land first.

- **D2 — Brotli decode mechanism for the streaming path.**
  Alternatives: (a) reuse aiohttp's `HAS_BROTLI` / `BrotliDecompressor` (incremental),
  no new azure-core dependency; (b) import a brotli package directly
  (`brotli`/`brotlicffi`); (c) add a new pyproject extra for Brotli.
  **Answer: (a) Reuse aiohttp's `HAS_BROTLI` / `BrotliDecompressor` (no new
  dependency).**
  - Justification: `br` is only advertised when a Brotli lib is already importable, and
    aiohttp's `BrotliDecompressor` supports incremental decode, matching the streaming
    path's chunk-by-chunk model; consistent with Sub-item 2.
  - Implementation note: verify the minimum aiohttp version that exposes `HAS_BROTLI` and
    `BrotliDecompressor` against azure-core's `aiohttp>=3.0` lower bound, and decide
    whether azure-core should import it directly, guard by version, or use a small
    compatibility wrapper.

- **D3 — Missing-library behavior for streamed `br`.**
  Alternatives: (a) raise a clear, actionable "install Brotli" error matching aiohttp
  and Sub-item 2; (b) fall through and return raw compressed chunks (current behavior).
  **Answer: (a) Raise a clear, actionable error.**
  - Justification: silent raw chunks reproduce the corruption / `UnicodeDecodeError`;
    an actionable error is the agreed behavior for the non-compliant-server case and is
    consistent with the buffered sub-item.
  - Implementation note: specify the intended exception type and message source (for
    example, azure-core's existing `DecodeError` versus whatever aiohttp would raise), and
    keep the buffered and streaming missing-library behavior consistent so both paths
    raise the same error.

- **D4 — `zstd` in the streaming path.**
  Alternatives: (a) keep `zstd` separate (`br` only here); (b) include `zstd` now.
  **Answer: (a) Keep `zstd` separate.**
  - Justification: avoids folding the adjacent `zstd` gap (a new feature, assumptions
    Q4) into this `br` correctness fix.

Still open (carried to other sub-items, not decided here):
- `zstd` streaming decode — separate sub-item / new feature (assumptions Q4).
- Whether the two aiohttp sites are the complete set of `Content-Encoding` inspection
  points (assumptions Q7) — relevant if Sub-item 1 unifies the dispatch. Before
  implementation, run and record a repository search for all `Content-Encoding`,
  `_decompress`, and decompression helper sites in azure-core; a missed site would leave
  the work item incomplete.
- Target azure-core version and CHANGELOG heading (assumptions Q8); needs an unreleased
  heading at fix time.

---

## Out-of-scope observations

Noticed while researching this area. Recorded so they are not lost. NOT part of
Sub-item 3.

- The streaming `__anext__` and the buffered `_aiohttp_body_helper` each independently
  hard-code `("gzip", "deflate")`; a shared encoding-dispatch helper would prevent the
  `br` branch from drifting between the two sites. Refactor (assumptions Sub-item 1),
  not this bug.
- `zstd` has the identical gap in `__anext__`: aiohttp advertises it when `HAS_ZSTD` is
  present and the streaming path cannot decode it either. Tracked separately
  (assumptions Q4); excluded here.
- `__anext__` lazily creates `self._decompressor` only inside the `("gzip", "deflate")`
  branch; any future encoding (including `br`) needs its own initialization guard near
  here. Noted only; not in scope.
- The legacy `AioHttpTransportResponse` and the new `RestAioHttpTransportResponse` both
  reuse this one generator, so a single streaming `br` fix would cover both surfaces.
  Observation only; no change proposed here.

---

## GAO fixes

This section summarizes the fixes applied from `docs/brotli.3.research.gao.md`. Only items
marked Address were applied. Items marked Defer were left unchanged.

- **G1** — Section: header scope decision (top of document). Change: added a note that
  `assumptions.md` still records Q6 as unresolved and that the source-of-truth must be
  updated to record the Q6 decision before streaming is treated as approved scope.
- **G2** — Section: header scope decision (top of document). Change: added a fallback
  sequence stating that if Sub-item 1 is not approved, streaming `br` is implemented
  directly after the buffered helper and does not need to wait for the optional refactor.
- **G3** — Section: 1, "How callers hit it". Change: clarified that `iter_raw()` is the
  raw opt-out surface that intentionally returns raw Brotli bytes, and removed it from the
  decoded-behavior description.
- **G4** — Section: 3, "Affected behavior and blast radius". Change: split the streamed
  byte reads bullet into decoded surfaces (`iter_bytes()`, default
  `stream_download(..., decompress=True)`) and raw opt-out surfaces (`iter_raw()`,
  `decompress=False`) noted as not a defect.
- **G5** — Section: 1, "How callers hit it". Change: added `AsyncHttpResponseImpl.read()`
  as an affected rest response path because it builds cached content by iterating
  `iter_bytes()`.
- **G6** — Section: 1, "Difference from the buffered helper". Change: added a note that
  incremental decompressors can hold trailing output, and to verify whether aiohttp's
  `BrotliDecompressor` needs `flush()`/finalization, plus a test to catch lost trailing
  bytes.
- **G10** — Section: 4, "Test coverage gaps". Change: added a test recommendation for the
  async `read()` cache path on `RestAioHttpTransportResponse` that consumes `iter_bytes()`
  and verifies cached content.
- **G13** — Section: 5, Decision D2. Change: added an implementation note to verify the
  minimum aiohttp version exposing `HAS_BROTLI` / `BrotliDecompressor` against azure-core's
  `aiohttp>=3.0` lower bound and decide on direct import, version guard, or compatibility
  wrapper.
- **G14** — Section: 5, Decision D3. Change: added an implementation note to specify the
  intended exception type and message source and to keep buffered and streaming
  missing-library behavior consistent.
- **G16** — Section: 5, "Still open" (Q7). Change: added a requirement to run and record a
  repository search for all `Content-Encoding`, `_decompress`, and decompression helper
  sites in azure-core before implementation.

Deferred (not changed): G7, G8, G9, G11, G12, G15, G17.
