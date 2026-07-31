# Gaps and Opportunities — brotli.3.research.md

Reviewed `docs/brotli.3.research.md` against GitHub issue
[#47186](https://github.com/Azure/azure-sdk-for-python/issues/47186), the
repository assumptions, and the current azure-core code.

## G1

- **Location:** Lines 8-13, "Q6 = in scope, sequenced after Sub-items 1 and 2."
- **Gap or opportunity description:** The research says Q6 has been resolved by the manager, but `assumptions.md` still lists Q6 as unresolved and says streaming is conditional. The GitHub issue names `_aiohttp_body_helper`, not streaming. This may make the plan look approved when the source-of-truth still says it needs confirmation.
- **Recommended action:** Update the source-of-truth work item or assumptions file to record the Q6 decision before treating streaming as required implementation scope.
- **Disposition:** Address

## G2

- **Location:** Lines 8-11, "sequenced after Sub-item 1 ... and Sub-item 2."
- **Gap or opportunity description:** The sequencing depends on Sub-item 1, but Sub-item 1 is optional and still has pending decisions in `brotli.1.research.md`. The streaming fix does not need to wait for an optional refactor if the refactor is not approved.
- **Recommended action:** State the fallback sequence: if Sub-item 1 is not approved, implement streaming `br` directly after the buffered helper.
- **Disposition:** Address

## G3

- **Location:** Lines 67-75, "iter_bytes() / iter_raw()"
- **Gap or opportunity description:** The research says `iter_raw()` receives raw Brotli chunks as wrong behavior. In the code, `AsyncHttpResponseImpl.iter_raw()` intentionally passes `decompress=False`, and its docstring says it will not decompress. Raw Brotli bytes are expected for `iter_raw()`, not a bug.
- **Recommended action:** Remove `iter_raw()` from the affected decoded-behavior list. Keep it only as an opt-out/raw behavior surface.
- **Disposition:** Address

## G4

- **Location:** Lines 138-140, "any caller of response.iter_bytes(), response.iter_raw(), or stream_download(...) ... receives raw Brotli chunks instead of decoded content."
- **Gap or opportunity description:** This repeats the `iter_raw()` overstatement and also treats all `stream_download(...)` calls the same. `stream_download(..., decompress=False)` is expected to return raw bytes.
- **Recommended action:** Split affected behavior into decoded surfaces (`iter_bytes()`, default `stream_download(..., decompress=True)`) and raw opt-out surfaces (`iter_raw()`, `decompress=False`).
- **Disposition:** Address

## G5

- **Location:** Section 1, "How callers hit it"
- **Gap or opportunity description:** The research does not mention `AsyncHttpResponseImpl.read()`. In the rest response implementation, `read()` builds cached content by iterating `iter_bytes()`. That means a streamed `br` gap can also affect async `.read()` when the body has not already been buffered.
- **Recommended action:** Add `read()` as an affected rest response path when it reaches `iter_bytes()`, or explain why the buffered helper owns that path instead.
- **Disposition:** Address

## G6

- **Location:** Section 1, "Difference from the buffered helper"
- **Gap or opportunity description:** The research correctly says streaming needs incremental decode, but it does not mention flush/finalization behavior. Incremental Brotli and zlib decompressors can hold trailing output until the stream ends. `__anext__` currently only returns `decompress(chunk)` and raises stop when no input remains.
- **Recommended action:** During implementation planning, verify whether aiohttp's `BrotliDecompressor` needs `flush()` or equivalent finalization when the stream ends, and add a test that would catch lost trailing bytes.
- **Disposition:** Address

## G7

- **Location:** Lines 80-85, "aiohttp then advertises br whenever a Brotli library is importable"
- **Gap or opportunity description:** The claim is consistent with `assumptions.md`, but the research does not cite aiohttp's default `Accept-Encoding` generation or confirm azure-core does not set `Accept-Encoding` for this path. The code citation only covers `auto_decompress=False`.
- **Recommended action:** Add a specific citation to the azure-core request creation path that does not pin `Accept-Encoding`, and to aiohttp's default header behavior if this claim is used to justify scope.
- **Disposition:** Defer

## G8

- **Location:** Lines 122-126, "sync requests/urllib3 streaming decodes br itself"
- **Gap or opportunity description:** This may be true in many installed environments, but the research does not prove it against azure-core's supported dependency range or optional Brotli availability. urllib3 Brotli support depends on installed extras/libraries.
- **Recommended action:** Soften the statement or cite the exact urllib3 behavior and dependency condition. The important conclusion is that this sub-item changes only aiohttp code.
- **Disposition:** Defer

## G9

- **Location:** Lines 157-159, "Only when a Brotli library is importable on the client"
- **Gap or opportunity description:** The next phrase says an unsolicited `br` from a non-compliant server is the Foundry case. The issue body only says Foundry returned `Content-Encoding: br`; it does not prove whether the server was non-compliant or whether the client advertised `br`.
- **Recommended action:** Reword as two cases: compliant server after client advertises `br`, and unsolicited `br` when no Brotli library is installed. Do not label the Foundry case non-compliant unless request headers prove it.
- **Disposition:** Defer

## G10

- **Location:** Section 4, "Test coverage gaps"
- **Gap or opportunity description:** The test gaps are good, but they do not mention a `read()` cache path test for async rest responses. Because `read()` joins `iter_bytes()` and stores `_content`, a broken streaming `br` path could also poison cached content.
- **Recommended action:** Add a test recommendation for `RestAioHttpTransportResponse.read()` or an equivalent rest response path that consumes `iter_bytes()` and then verifies cached content behavior.
- **Disposition:** Address

## G11

- **Location:** Lines 189-190, "multi-chunk br decode"
- **Gap or opportunity description:** The research asks for a multi-chunk test, but it does not define what must be split. Splitting the already-compressed byte stream is what exercises incremental decompressor state; splitting source text before compression may not.
- **Recommended action:** Specify that the test should split the compressed Brotli byte stream across multiple yielded chunks, including a chunk boundary inside compressed data.
- **Disposition:** Defer

## G12

- **Location:** Lines 197-200, "No test for the missing-library streamed case"
- **Gap or opportunity description:** This test may be hard to write reliably because the local test environment may have Brotli installed through aiohttp or other dependencies. The research does not say how to simulate `HAS_BROTLI=False` or an import failure without changing the environment.
- **Recommended action:** Recommend monkeypatching aiohttp's Brotli detection/decompressor entry point, or mark this as optional if it would make the test brittle.
- **Disposition:** Defer

## G13

- **Location:** Lines 218-226, "Reuse aiohttp's HAS_BROTLI / BrotliDecompressor"
- **Gap or opportunity description:** The decision is reasonable, but it assumes aiohttp's internal `BrotliDecompressor` is stable enough for azure-core to import. The research does not discuss whether this is public API, private API, or version-compatible with azure-core's `aiohttp>=3.0` lower bound.
- **Recommended action:** Verify the minimum aiohttp version that exposes `HAS_BROTLI` and `BrotliDecompressor`, and decide whether azure-core should import it directly, guard by version, or use a small compatibility wrapper.
- **Disposition:** Address

## G14

- **Location:** Lines 228-234, "Missing-library behavior for streamed br"
- **Gap or opportunity description:** Raising a clear error is a good outcome, but the research does not name the exception type. azure-core has existing exception patterns such as `DecodeError`; aiohttp may raise a different error. Leaving this unspecified can lead to inconsistent buffered and streaming behavior.
- **Recommended action:** Specify the intended exception type and message source, and keep buffered and streaming behavior consistent.
- **Disposition:** Address

## G15

- **Location:** Lines 236-240, "zstd in the streaming path"
- **Gap or opportunity description:** Keeping `zstd` separate is reasonable for the reported issue, but the research does not address the opportunity to structure the `br` fix so `zstd` can be added later without another duplicated branch.
- **Recommended action:** Keep `zstd` out of scope, but require the `br` implementation to avoid making future encoding support harder.
- **Disposition:** Defer

## G16

- **Location:** Lines 242-245, "Whether the two aiohttp sites are the complete set..."
- **Gap or opportunity description:** This open item materially affects confidence in the plan. The research says the streaming path is the second site but still carries Q7 as open. A missed `Content-Encoding` site would leave the work item incomplete.
- **Recommended action:** Before implementation, run and record a repository search for all `Content-Encoding`, `_decompress`, and decompression helper sites in azure-core.
- **Disposition:** Address

## G17

- **Location:** Section "Out-of-scope observations"
- **Gap or opportunity description:** The observation that both legacy and rest responses share one generator is useful, but it should be part of the affected-behavior evidence, not only out-of-scope. It supports why a single streaming fix covers both surfaces.
- **Recommended action:** Move or repeat this point in Section 1 so the implementation plan has a clear coverage statement.
- **Disposition:** Defer
