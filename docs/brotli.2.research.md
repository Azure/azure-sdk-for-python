# Research — Sub-item 2: Decode `br` in the buffered helper

Work item: supporting brotli in azure-core
(GitHub issue [#47186](https://github.com/Azure/azure-sdk-for-python/issues/47186))

Sub-item 2: **"Decode `br` in the buffered helper" (Bug fix) — primary.**

Scope of this research: the buffered helper `_aiohttp_body_helper` only. The
streaming path (`__anext__`) and `zstd` are tracked as separate sub-items and are
deliberately excluded here (confirmed with manager). This document researches the
bug only. It proposes no fix and contains no code.

---

## 1. How and where the bug manifests

### The failing site
`_aiohttp_body_helper` in
`sdk/core/azure-core/azure/core/utils/_pipeline_transport_rest_shared.py`
(lines 381-414) is the buffered decode helper. After guard checks it inspects the
`Content-Encoding` header and only handles `gzip` and `deflate`:

```
402  enc = response.headers.get("Content-Encoding")
403  if not enc:
404      return response._content
405  enc = enc.lower()
406  if enc in ("gzip", "deflate"):
407      import zlib
...
413      return response._content
414  return response._content          # <-- br falls through here, undecoded
```

When `Content-Encoding: br`, `enc` is `"br"`, the `("gzip", "deflate")` branch is
skipped, and line 414 returns the still-compressed bytes unchanged.

- Justification: this is the exact missing-branch the work item names as the root
  cause; `br` is not in the only encoding tuple that triggers decompression.

### How callers hit it
The helper is the single shared decode point for every aiohttp buffered read. It is
called from three consumer methods:

- `azure/core/rest/_aiohttp.py` — `RestAioHttpTransportResponse` `body()` (L170),
  the property/coroutine that backs `read()` (L214), and `read()` (L237).
- `azure/core/pipeline/transport/_aiohttp.py` — legacy `AioHttpTransportResponse`
  `body()` (L529), which `text()` (L531) then decodes to `str`.

So `.body()`, `.read()`, `.content`, and `.text()` all funnel through this one
helper. With a `br` body, `.body()`/`.read()` return raw Brotli bytes and
`.text()` then tries to UTF-8 decode them, producing the reported
`UnicodeDecodeError`.

- Justification: ties the single buffered defect to every buffered-read entry point
  the reporter could call.

### Why a `br` response reaches azure-core at all
azure-core creates the aiohttp `ClientSession` with `auto_decompress=False`
(`azure/core/pipeline/transport/_aiohttp.py` ~L192) and re-implements decompression
itself. It does not pin `Accept-Encoding`, so aiohttp inserts its default
`Accept-Encoding`, which includes `br` whenever a Brotli library is importable.
A compliant server may then legitimately answer `Content-Encoding: br`, which the
buffered helper cannot decode.

Before implementation, check the aiohttp versions supported by azure-core
(`aiohttp>=3.0`). Confirm whether `HAS_BROTLI` and `BrotliDecompressor` are
available at a stable import path. If the path is not stable, keep that version
handling inside a small private fallback wrapper.

- Justification: explains why this is a self-inflicted correctness gap (the SDK
  advertises `br` then fails to honor it), not an exotic server edge case.

---

## 2. Root cause and alternative hypotheses

### Most likely root cause (primary)
The encoding dispatch in `_aiohttp_body_helper` enumerates only
`("gzip", "deflate")` (line 406). `br` is unlisted, so the function returns the
compressed bytes untouched at the trailing `return response._content` (line 414).
The bug is a missing encoding branch in the buffered helper.

- Evidence: lines 406 and 414 above; there is no `br`, `brotli`, or `BrotliDecompressor`
  reference anywhere in the file.
- Implementation note: keep aiohttp Brotli imports behind a private helper. That
  contains any aiohttp version fallback or import-path change in one place.
- Justification: directly matches the work item's named root cause and the buffered
  scope of this sub-item.

### Alternative hypothesis A — decode disabled by a flag
Could the body simply be returned raw because decompression was opted out? The guards
at lines 398-401 (`_decompress`, `_decompressed_content`) would do that. Ruled out:
in the default path `_decompress` is `True` (set from `decompress=not auto_decompress`,
`_aiohttp.py` L369/L381/L443) and `_decompressed_content` starts `False`. So execution
reaches the encoding check and still skips `br`.

- Justification: rules out a configuration cause so the fix stays on the missing branch.

### Alternative hypothesis B — header casing / parsing
Could `br` be missed due to header name/value casing? Ruled out: `enc` is lowercased
at line 405, and aiohttp headers are case-insensitive on lookup, so `"br"` is matched
reliably; it is simply not in the tuple.

- Justification: confirms the defect is the tuple membership, not header handling.

### Alternative hypothesis C — wrong layer (should be fixed in a transport/policy)
Could the real fix belong in `ContentDecodePolicy` or the sync transports instead?
Ruled out for this sub-item: sync `requests`/`urllib3` transports decode `br`
themselves, and `ContentDecodePolicy` parses already-decoded text. The manual
`zlib`-based decode that omits `br` lives only in the aiohttp buffered helper.

- Justification: keeps the fix at the single layer that actually drops `br`.

---

## 3. Affected behavior and blast radius

Who sees wrong behavior today when a server returns `Content-Encoding: br` over the
async aiohttp transport:

- **Direct buffered reads** — any caller of `response.read()`, `response.body()`,
  or `response.content` on `RestAioHttpTransportResponse` or
  `AioHttpTransportResponse` gets raw Brotli bytes instead of decoded content.
  - Justification: these all route through the unmodified helper.
- **Text reads** — `response.text()` raises `UnicodeDecodeError` (the reported
  symptom) because it decodes still-compressed bytes.
  - Justification: matches the issue's stated failure mode.
- **JSON/model deserialization** — anything calling `.json()` or model
  deserialization on top of `.text()`/`.body()` fails the same way.
  - Justification: same single buffered byte source.
- **The original reporter** — `FoundryStorageProvider` in
  `azure-ai-agentserver-responses` surfaces the symptom; the defect is in azure-core.
  - Justification: confirms the symptom origin without widening scope.

Scope limits of the blast radius:
- **Only the async aiohttp transport** is affected. Sync `requests`-based transports
  (`_requests_basic.py`, `_requests_asyncio.py`, `_requests_trio.py`) are unaffected
  because `urllib3` decodes `br` itself.
  - Justification: bounds the blast radius to the buffered aiohttp path.
- **Only when a Brotli library is importable on the client** (otherwise aiohttp does
  not advertise `br`, so a compliant server will not send it; a non-compliant server
  sending unsolicited `br` is the Foundry case).
  - Justification: explains why not every user hits this and why the missing-library
    behavior matters.
- **The streaming path is also wrong today** but is out of scope for this sub-item;
  it is recorded as a separate sub-item.
  - Justification: noted for completeness without folding it into this bug fix.

---

## 4. Test coverage gaps

Existing coverage around the buffered helper:
- Server routes `/encoding/gzip` and `/encoding/deflate` exist
  (`tests/.../test_routes/encoding.py` L85-101); there is **no `/encoding/br` route**.
- Requests-based REST transport tests cover gzip/deflate in
  `tests/async_tests/test_rest_asyncio_transport.py` and
  `tests/async_tests/test_rest_trio_transport.py`; these do not cover the aiohttp
  buffered helper.
- More relevant aiohttp REST coverage belongs in
  `tests/async_tests/test_rest_stream_responses_async.py`, with helper-level legacy
  and REST coverage in `tests/async_tests/test_universal_http_async.py`.
- `tests/async_tests/test_universal_http_async.py` covers gzip decode and a negative
  (`_decompress=False`) case for the legacy response; **no `br` case.**

Gaps that leave this bug unprotected:
- **No test asserts a `br` body round-trips** to the original text/bytes through
  `.body()`/`.read()`/`.text()`.
  Tests should skip when Brotli support is unavailable, or use a local fixture that
  keeps the optional Brotli import inside the test or test server route.
  - Justification: the exact behavior the fix must guarantee (A8) is untested, and
    azure-core does not require a Brotli package by default.
- **No test asserts idempotency for `br`** — that a second `.body()` call after a
  `br` decode does not double-decompress (the `_decompressed_content` flag path).
  - Justification: gzip/deflate set this flag; an untested `br` path could regress it.
- **No test for the missing-library case** — that receiving `br` with no Brotli
  library raises a clear, actionable error rather than an opaque `ModuleNotFoundError`
  or silent raw bytes.
  Expected behavior should be `azure.core.exceptions.DecodeError` with a message
  that mentions `Content-Encoding: br` and installing Brotli support.
  - Justification: this is the decided behavior (Decision D2) and currently unverified.
- **No regression guard tying `Accept-Encoding`-advertised `br` to decode support** —
  nothing fails today when the SDK advertises `br` but cannot decode it.
  - Justification: this mismatch is the heart of the bug and is currently invisible to
    the suite.

---

## 5. Decisions

Decisions raised and answered with the manager (recorded for the fix phase):

- **D1 — Brotli decode mechanism.**
  Alternatives: (a) reuse aiohttp's `HAS_BROTLI` / `BrotliDecompressor` with no new
  azure-core dependency; (b) import a brotli package directly (`brotli`/`brotlicffi`);
  (c) add a new pyproject extra for Brotli; (d) only restrict or pin
  `Accept-Encoding`.
  **Answer: (a) Reuse aiohttp's `HAS_BROTLI` / `BrotliDecompressor` (no new dependency).**
  - Justification: `br` is only advertised when a Brotli lib is already importable, so
    reuse closes the bug without adding a dependency or extra.
  - Implementation detail: use a private helper for the aiohttp Brotli import and
    decode call. This keeps aiohttp compatibility handling contained.
  - Header decision: do not fix this only by changing `Accept-Encoding`. That would
    not handle unsolicited `Content-Encoding: br`, including the Foundry case.

- **D2 — Missing-library behavior.**
  Alternatives: (a) raise a clear, actionable "install Brotli" error matching aiohttp;
  (b) fall through and return raw compressed bytes (current behavior).
  **Answer: (a) Raise `azure.core.exceptions.DecodeError` with a clear, actionable
  message.** The message should mention `Content-Encoding: br` and installing Brotli
  support.
  - Justification: silent raw bytes reproduce the `UnicodeDecodeError`; an actionable
    azure-core decode error is the agreed acceptance behavior for the non-compliant-
    server case.

- **D3 — Scope boundary for this research.**
  Alternatives: (a) buffered helper only; (b) also streaming now; (c) also zstd now.
  **Answer: (a) Buffered helper only; streaming and zstd are separate sub-items.**
  - Justification: keeps this primary bug fix minimal and avoids folding adjacent gaps
    into it.
  - Implementation detail: structure the buffered `br` dispatch so a later streaming
    fix can reuse the same private Brotli helper instead of duplicating the decision.

Still open (carried to other sub-items / fix phase, not decided here):
- Streaming `__anext__` `br` decode — separate sub-item (assumptions Q6).
- `zstd` decode — separate sub-item / new feature (assumptions Q4).
- Target azure-core version and CHANGELOG heading (assumptions Q8); the current
  `CHANGELOG.md` top entry is a dated `1.41.0` release, so a new unreleased heading
  will be needed at fix time.

---

## Out-of-scope observations

Noticed while researching this area. Recorded so they are not lost. NOT part of
Sub-item 2.

- The buffered helper (`_aiohttp_body_helper`) and the streaming `__anext__` each
  independently hard-code `("gzip", "deflate")`; a shared encoding-dispatch helper
  would prevent the `br` branch from drifting between the two sites. Refactor, not
  this bug.
- The issue text claims `brotli` "is already a common transitive dependency via
  `aiohttp[speedups]`," but the azure-core async extra is `aio = ["aiohttp>=3.0"]`
  (`pyproject.toml` L32) — plain aiohttp, no guaranteed Brotli library. Worth flagging
  on the issue; not a code change here.
- `zstd` has the identical gap: aiohttp advertises it when `HAS_ZSTD` is present and
  the buffered helper cannot decode it either. Tracked separately (Q4); excluded here.
- The trailing `return response._content` at line 414 is reached both for unknown
  encodings and as the fall-through; any future multi-encoding or `identity` handling
  would live near here. Noted only; not in scope.

---

## GAO fixes

- **G2** — Section 1, "Why a `br` response reaches azure-core at all": added an
  implementation check for supported aiohttp versions and stable access to
  `HAS_BROTLI` / `BrotliDecompressor`, with fallback handling kept private.
- **G3** — Section 2, "Most likely root cause" and Section 5, "D1 - Brotli decode
  mechanism": added that aiohttp Brotli imports should be isolated behind a private
  helper.
- **G7** — Section 4, "Existing coverage around the buffered helper": corrected the
  test inventory to distinguish requests-based REST tests from aiohttp-specific and
  helper-level coverage.
- **G8** — Section 4, "No test asserts a `br` body round-trips": added that tests
  should skip when Brotli support is unavailable or keep optional Brotli imports local
  to the fixture.
- **G9** — Section 4, "No test for the missing-library case" and Section 5,
  "D2 - Missing-library behavior": defined the expected error as
  `azure.core.exceptions.DecodeError` with a message that mentions
  `Content-Encoding: br` and installing Brotli support.
- **G11** — Section 5, "D1 - Brotli decode mechanism": recorded why decoding `br`
  is required instead of only changing `Accept-Encoding`.
- **G12** — Section 5, "D2 - Missing-library behavior": tied the missing-library
  behavior to the azure-core `DecodeError` contract.
- **G13** — Section 5, "D3 - Scope boundary for this research": added that the
  buffered implementation should be structured for later reuse by the streaming
  sub-item without expanding this sub-item's scope.
