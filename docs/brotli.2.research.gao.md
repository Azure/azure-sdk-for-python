# Gaps and Opportunities - Sub-item 2 Research

Work item: supporting brotli in azure-core
Research document: `docs/brotli.2.research.md`

## Items

### G1

**Location:** Section 1, "How callers hit it"

**Gap or opportunity:** The section correctly identifies the buffered helper as the shared decode point for buffered aiohttp reads, but it does not clearly separate new REST responses from legacy responses. `RestAioHttpTransportResponse.read()`, `.content`, and `.body()` call `_aiohttp_body_helper` directly. Legacy `AioHttpTransportResponse.body()` and `.text()` call the helper after `load_body()` fills `_content`. This is a small accuracy gap because the public entry points are not identical across the two response types.

**Recommended action:** Clarify the caller list by response type: REST response `.read()`, `.content`, and `.body()`; legacy response `.body()` and `.text()` after `load_body()`.

**Disposition:** Defer

### G2

**Location:** Section 1, "Why a `br` response reaches azure-core at all"

**Gap or opportunity:** The claim that aiohttp inserts `Accept-Encoding: br` when Brotli is importable is reasonable, but the research does not cite the local aiohttp implementation path or note that azure-core supports broad aiohttp versions through `aiohttp>=3.0`. The fix plan may depend on whether the same helper names exist across supported aiohttp versions.

**Recommended action:** Add a compatibility check before implementation: confirm the target aiohttp versions expose `HAS_BROTLI` and `BrotliDecompressor` at a stable import path, or add a small fallback wrapper.

**Disposition:** Address

### G3

**Location:** Section 2, D1 also referenced in Section 5, "`HAS_BROTLI` / `BrotliDecompressor`"

**Gap or opportunity:** Reusing aiohttp's Brotli implementation is a good direction, but the research treats aiohttp internals as a settled implementation detail. These names are not part of azure-core's public surface and may not be stable across the full `aiohttp>=3.0` range.

**Recommended action:** In the plan, isolate aiohttp Brotli imports behind a private helper so any version fallback or import-path change is contained.

**Disposition:** Address

### G4

**Location:** Section 2, "Alternative hypothesis C - wrong layer"

**Gap or opportunity:** The conclusion that `ContentDecodePolicy` is not the right layer is supported by the code: it relies on `response.text()` after the transport has decoded bytes. The research could be more specific by citing that `deserialize_from_http_generics()` calls `response.text(encoding)` rather than decompressing `Content-Encoding`.

**Recommended action:** Add the `ContentDecodePolicy.deserialize_from_http_generics()` call path as supporting evidence if the research is revised.

**Disposition:** Defer

### G5

**Location:** Section 3, "Only the async aiohttp transport is affected"

**Gap or opportunity:** The statement that sync `requests` transports are unaffected is too absolute. The sync paths delegate to `requests` and urllib3, so they are outside this fix, but Brotli support there also depends on urllib3's available Brotli support and server behavior. This does not change the aiohttp bug, but it should be worded as a scope boundary instead of a universal capability claim.

**Recommended action:** Rephrase to: "Sync transports are out of scope because they delegate decompression to requests/urllib3 rather than azure-core's manual aiohttp helper."

**Disposition:** Defer

### G6

**Location:** Section 3, "Only when a Brotli library is importable on the client"

**Gap or opportunity:** The section correctly notes the compliant-server case and the Foundry unsolicited-`br` case, but it does not call out custom aiohttp sessions. A caller can provide a session with different `auto_decompress` or header behavior, which changes whether azure-core's helper is responsible for decompression.

**Recommended action:** Add a small note that the default azure-core-owned aiohttp session is the main path; custom sessions may differ based on their `auto_decompress` and request headers.

**Disposition:** Defer

### G7

**Location:** Section 4, "Existing coverage around the buffered helper"

**Gap or opportunity:** The test file references are partly inaccurate for aiohttp. `tests/async_tests/test_rest_asyncio_transport.py` uses `AsyncioRequestsTransport`, and `test_rest_trio_transport.py` uses `TrioRequestsTransport`. They test requests-based transports, not the aiohttp buffered helper. The more relevant aiohttp REST tests include `tests/async_tests/test_rest_stream_responses_async.py` and the helper-level coverage in `tests/async_tests/test_universal_http_async.py`.

**Recommended action:** Correct the test inventory before planning test changes. Add `br` coverage to aiohttp-specific REST tests and keep helper-level legacy/REST coverage in `test_universal_http_async.py`.

**Disposition:** Address

### G8

**Location:** Section 4, "No test asserts a `br` body round-trips"

**Gap or opportunity:** The research identifies the missing `br` route but does not address test environment constraints. `azure-core`'s async extra is plain `aiohttp>=3.0`, and the default interpreter in this workspace does not have a Brotli package installed. A `/encoding/br` route or fixture that imports Brotli unconditionally could make tests fail in environments without Brotli.

**Recommended action:** Design tests so they either skip when Brotli support is unavailable or use a local fixture strategy that does not require adding a new runtime dependency. Keep any optional import local to the test or test server route.

**Disposition:** Address

### G9

**Location:** Section 4, "No test for the missing-library case"

**Gap or opportunity:** The missing-library test is important, but the expected exception type and message are not specified. Without a concrete expected error, the test may only check that "something" fails and still allow an unclear error to reach users.

**Recommended action:** Define the exact exception class and message pattern for `Content-Encoding: br` when Brotli support is unavailable, then test that behavior directly.

**Disposition:** Address

### G10

**Location:** Section 4, "No regression guard tying `Accept-Encoding`-advertised `br` to decode support"

**Gap or opportunity:** This is a good gap, but it is not concrete enough to implement as written. A useful regression test needs a controlled aiohttp environment where Brotli support is importable and the outgoing request's `Accept-Encoding` can be observed.

**Recommended action:** Either make this a specific test plan item with controlled dependencies, or defer it and rely on direct `Content-Encoding: br` decode tests for this sub-item.

**Disposition:** Defer

### G11

**Location:** Section 5, "D1 - Brotli decode mechanism"

**Gap or opportunity:** The listed alternatives omit a lower-risk mitigation: explicitly setting or restricting `Accept-Encoding` for azure-core-owned aiohttp sessions. That option would not fix unsolicited `br` responses like the Foundry case, so it is not sufficient alone, but it is a reasonable decision point because the research frames the bug as "advertise then fail to honor."

**Recommended action:** Record why the implementation should decode `br` instead of only pinning `Accept-Encoding`, and decide whether any header change is out of scope.

**Disposition:** Address

### G12

**Location:** Section 5, "D2 - Missing-library behavior"

**Gap or opportunity:** The decision says to raise a clear, actionable error, but it does not say where that error should come from or how it should fit azure-core exception patterns. Directly exposing an aiohttp-internal exception or `RuntimeError` may be less consistent than wrapping it in an azure-core exception.

**Recommended action:** Decide the error contract before coding: direct aiohttp-style error, `DecodeError`, or another azure-core exception. Use the same contract in tests.

**Disposition:** Address

### G13

**Location:** Section 5, "D3 - Scope boundary for this research"

**Gap or opportunity:** The section correctly keeps streaming and zstd out of this sub-item, but the broader work item documents streaming as another in-scope sub-item. If the buffered fix adds a standalone `br` branch now, the streaming fix may duplicate the same decision and drift.

**Recommended action:** Keep Sub-item 2 focused on buffered behavior, but structure the buffered implementation so Sub-item 3 can reuse the same Brotli dispatch decision without duplicating code.

**Disposition:** Address

### G14

**Location:** Section 5, "Still open"

**Gap or opportunity:** The changelog note is useful but incomplete. The research says a new unreleased heading will be needed, but does not check the package's release-note convention or whether this bug fix should be under "Bugs Fixed".

**Recommended action:** During implementation, inspect the current `sdk/core/azure-core/CHANGELOG.md` format and add the entry under the appropriate heading.

**Disposition:** Defer

### G15

**Location:** Section 6, "Out-of-scope observations"

**Gap or opportunity:** The observation about `zstd` is useful, but it may distract from the `br` bug if it is not tied to a decision. Since `zstd` is explicitly separate, the implementation should avoid broadening the helper in a way that accidentally changes `zstd` behavior.

**Recommended action:** Keep `zstd` out of Sub-item 2 tests and code unless maintainers explicitly expand scope.

**Disposition:** Defer

### G16

**Location:** Section 6, "The trailing `return response._content`"

**Gap or opportunity:** The research notes unknown encodings and future multi-encoding handling, but it does not call out that HTTP `Content-Encoding` can contain multiple codings. The current code handles only a single lowercased value. This is outside the Brotli bug, but it is a real completeness gap for future decompression work.

**Recommended action:** Defer multi-encoding parsing unless the work item is expanded. Do not change unknown-encoding fall-through behavior in this sub-item.

**Disposition:** Defer
