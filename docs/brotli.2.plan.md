# Implementation Plan — Sub-item 2: Decode `br` in the buffered helper (Bug fix)

Work item: supporting brotli in azure-core
(GitHub issue [#47186](https://github.com/Azure/azure-sdk-for-python/issues/47186))

Sub-item 2: **"Decode `br` in the buffered helper" (Bug fix) — primary.**

Inputs treated as facts (not re-evaluated here):
- `docs/brotli.2.research.md` (research)
- `docs/brotli.2.research.gao.md` (gaps and opportunities)
- `assumptions.md` (context)

Scope is the buffered helper `_aiohttp_body_helper` only. Streaming (`__anext__`)
and `zstd` are separate sub-items and are excluded.

---

## 1. Selected decisions and rationale (from research)

These come straight from the research and assumptions. They are settled.

- **D1 — Decode mechanism: reuse aiohttp's `HAS_BROTLI` / `BrotliDecompressor`.**
  No new azure-core dependency and no new pyproject extra. `br` is only advertised
  when a Brotli library is already importable, so reusing aiohttp's own support
  closes the bug without adding anything. (research D1; assumptions Section 0
  "Key implication".)
- **D1 detail — isolate aiohttp Brotli imports behind one private helper.**
  Any aiohttp version difference or import-path change stays in one place.
  (research D1, G2, G3.)
- **D1 header decision — do not "fix" this by only pinning `Accept-Encoding`.**
  That would not handle an unsolicited `Content-Encoding: br` (the Foundry case).
  We must actually decode. (research D1, G11.)
- **D2 — Missing-library behavior: raise `azure.core.exceptions.DecodeError`** with
  an actionable message that mentions `Content-Encoding: br` and installing Brotli
  support. Not silent raw bytes. (research D2, G9, G12.)
- **D3 — Scope: buffered helper only.** Structure the `br` dispatch so the streaming
  sub-item (Sub-item 3) can reuse the same private Brotli helper without duplicating
  the decision. Do not change streaming or `zstd` here. (research D3, G13, G15.)
- **Compatibility check first.** azure-core's async extra is `aiohttp>=3.0`. Before
  coding, confirm `HAS_BROTLI` and `BrotliDecompressor` are reachable at a stable
  import path across supported aiohttp versions; if not, the private helper absorbs
  the fallback. (research Section 1; G2.)
- **Idempotency must hold.** A `br` decode must set `_decompressed_content = True`
  so a second `.body()` call does not double-decompress, exactly as gzip/deflate do.
  (research Section 4 "No test asserts idempotency".)

---

## 2. Technical approach end-to-end (and how the fix will be proved)

This is a bug fix, so the proof obligation is twofold: (a) the `br` body now
round-trips, and (b) nothing else changed.

End-to-end approach:
- Add a single `br` branch to `_aiohttp_body_helper` in
  `azure/core/utils/_pipeline_transport_rest_shared.py`. The branch decodes using a
  new private Brotli helper, sets `response._content` to the decoded bytes, sets
  `response._decompressed_content = True`, and returns the decoded bytes. This mirrors
  the existing gzip/deflate branch.
- The new private helper wraps the aiohttp Brotli import (`HAS_BROTLI`,
  `BrotliDecompressor`) and the decode call. If Brotli support is unavailable, it
  raises `azure.core.exceptions.DecodeError` with an actionable message.
- All existing guard checks (`_content is None`, `_decompress`, `_decompressed_content`,
  empty `Content-Encoding`) and the gzip/deflate branch and the trailing fall-through
  are left untouched.

How the bug is proved fixed:
- A new test sends `Content-Encoding: br` over the buffered aiohttp read path and
  asserts `.body()` / `.read()` return the original bytes and `.text()` returns the
  original string with no `UnicodeDecodeError`. This directly verifies A8 / the
  reported failure mode.
- An idempotency test calls `.body()` twice on a `br` response and asserts the bytes
  are stable (no double-decompress), verifying the `_decompressed_content` path.
- A missing-library test asserts that receiving `br` with no Brotli support raises
  `DecodeError` whose message mentions `Content-Encoding: br` and installing Brotli
  support (D2), rather than raw bytes or an opaque `ModuleNotFoundError`.

How "nothing else changed" is proved:
- The existing azure-core async/transport test suite is run before and after. The
  gzip, deflate, and no-encoding cases (e.g. in `test_universal_http_async.py`) must
  stay green, proving A9 (existing behavior unchanged).
- The change is additive (one new branch + one private helper). The unknown-encoding
  fall-through at the end of the helper is not modified, so unknown encodings keep
  returning raw bytes exactly as before.

---

## 3. Step-by-step implementation plan

Ordered to minimize blast radius: confirm environment facts, add the contained
private helper, wire one branch, then add tests, then changelog.

**Step 0 — Confirm aiohttp Brotli import surface.**
- What/where: Inspect the supported aiohttp range (`aiohttp>=3.0`) and confirm the
  import path for `HAS_BROTLI` and `BrotliDecompressor` (e.g. `aiohttp.compression_utils`).
  No code change.
- Why: The whole fix depends on reusing these names; the path may vary by version.
- Expected outcome: A confirmed import path, or a documented need for a small fallback
  inside the private helper.
- Scope justification: research Section 1 / G2 require a compatibility check before
  implementation.

**Step 1 — Add a private Brotli decode helper.**
- What/where: New private function in
  `azure/core/utils/_pipeline_transport_rest_shared.py` (same module as
  `_aiohttp_body_helper`) that imports aiohttp's Brotli support, decodes a `bytes`
  input, and on missing support raises `azure.core.exceptions.DecodeError` with a
  message naming `Content-Encoding: br` and how to install Brotli support.
- Why: Isolates the aiohttp import and version handling in one place so the streaming
  sub-item can reuse it and any path change is contained.
- Expected outcome: A self-contained decode function with the agreed error contract.
- Scope justification: research D1/D2/D3, G3, G12, G13 (private helper, error contract,
  reuse-ready structure).

**Step 2 — Add the `br` branch to `_aiohttp_body_helper`.**
- What/where: In `_aiohttp_body_helper`, after the `("gzip", "deflate")` branch
  (around line 406-414), add `elif enc == "br":` that calls the Step 1 helper, assigns
  the result to `response._content`, sets `response._decompressed_content = True`, and
  returns it.
- Why: This is the named root cause — the missing encoding branch.
- Expected outcome: A `br` body is decoded and cached; second reads do not re-decode;
  gzip/deflate/no-encoding/unknown paths are byte-for-byte unchanged.
- Scope justification: research Section 2 "Most likely root cause"; assumptions A1, A2.

**Step 3 — Add a `/encoding/br` test server route.**
- What/where: Add a `br` route alongside `/encoding/gzip` and `/encoding/deflate` in
  `tests/testserver_tests/coretestserver/coretestserver/test_routes/encoding.py`,
  returning Brotli-compressed bytes with `Content-Encoding: br`. Keep any optional
  Brotli import local to this route/fixture.
- Why: There is no `br` route today, so the round-trip cannot be exercised.
- Expected outcome: A route that serves a known `br`-encoded body for tests.
- Scope justification: research Section 4 "no `/encoding/br` route"; G7, G8.

**Step 4 — Add buffered `br` round-trip and idempotency tests.**
- What/where: Add aiohttp buffered-helper tests (helper-level/legacy and REST response)
  in `tests/async_tests/test_universal_http_async.py` (and the aiohttp REST test file
  identified in Step 0/G7) that assert `.body()`/`.read()`/`.text()` round-trip a `br`
  body and that a second `.body()` call is stable. Skip when Brotli support is
  unavailable.
- Why: Proves A8 and the idempotency invariant; protects against regression.
- Expected outcome: Passing tests that fail on the pre-fix code.
- Scope justification: research Section 4 (round-trip and idempotency gaps); A8, A9; G7, G8.

**Step 5 — Add the missing-library `DecodeError` test.**
- What/where: A test that simulates Brotli support being unavailable and asserts a
  `br` response raises `azure.core.exceptions.DecodeError` with a message mentioning
  `Content-Encoding: br` and installing Brotli support.
- Why: Verifies decision D2; prevents silent raw bytes or opaque import errors.
- Expected outcome: Passing negative-path test matching the agreed error contract.
- Scope justification: research D2, Section 4 "No test for the missing-library case";
  G9, G12.

**Step 6 — Add CHANGELOG entry.**
- What/where: Add a new unreleased heading to `sdk/core/azure-core/CHANGELOG.md`
  (current top entry is the dated `1.41.0`) under "Bugs Fixed", noting `br`
  decompression in the buffered aiohttp path, referencing issue #47186.
- Why: Required release-note convention for a user-visible bug fix.
- Expected outcome: A correctly formatted unreleased changelog entry.
- Scope justification: research Section 5 "Still open" (changelog); G14.

---

## 4. Stop/go gates

- **Gate A (after Step 0).** If `HAS_BROTLI` / `BrotliDecompressor` are not reachable
  at a stable path across `aiohttp>=3.0`, stop and decide the fallback inside the
  private helper before writing the branch. Go only when the import contract is known.
- **Gate B (after Step 2).** Run the existing async/transport suite. Go only if gzip,
  deflate, no-encoding, and unknown-encoding behavior is unchanged (A9).
- **Gate C (after Steps 3-5).** Go only if the new `br` round-trip, idempotency, and
  missing-library tests pass, and they fail against the pre-fix helper (proving they
  actually guard the bug).
- **Gate D (before handoff/PR).** Go only if the full package check run is green and
  the CHANGELOG entry is present.

---

## 5. Validation plan

Tests to run (baseline before, and after each change):
- The azure-core async test suite, especially `tests/async_tests/test_universal_http_async.py`
  (existing gzip decode and `_decompress=False` negative case) and the aiohttp REST
  tests confirmed in Step 0 / G7.
- Package-level checks for azure-core (lint/type/format as already configured) to
  confirm the additive change introduces no new violations.

Tests to add:
- `br` round-trip via `.body()`, `.read()`, `.content`, and `.text()` on both
  `RestAioHttpTransportResponse` and legacy `AioHttpTransportResponse`.
- `br` idempotency: two `.body()` calls return identical bytes (no double-decompress).
- Missing-library: `br` response raises `DecodeError` with the agreed message.

Scenarios:
- Compliant server returns `br` with Brotli installed -> decoded transparently.
- Non-compliant/unsolicited `br` with Brotli not installed -> clear `DecodeError`.

Invariants:
- gzip/deflate/no-encoding/unknown-encoding outputs are byte-for-byte unchanged.
- After any successful decode, `_decompressed_content == True` and a re-read does not
  re-decompress.
- No new runtime dependency is added to azure-core; optional Brotli imports stay local
  to tests/fixtures.

Observability checks:
- The `DecodeError` message is human-actionable (names `br` and how to install Brotli).
- Tests skip cleanly (not error) when Brotli support is absent in the environment.

---

## 6. Rollout strategy

- This is a library source change in azure-core; "deployment" is a normal package
  release, not a service rollout.
- Sequencing: land Sub-item 2 (this buffered fix) as the primary fix. Sub-item 3
  (streaming) follows and reuses the Step 1 private helper. Sub-item 1 (refactor) and
  `zstd` remain separate and gated.
- Blast-radius containment: change is additive (one new branch + one private helper);
  only the async aiohttp buffered path is touched. Sync transports, `ContentDecodePolicy`,
  gzip/deflate, and unknown-encoding paths are untouched.
- Release vehicle: a new unreleased azure-core version (heading added in Step 6),
  shipped through the standard azure-core release process and CI gates.
- Monitoring window: after release, watch issue #47186 and azure-core bug intake for
  any `br`/decode regressions during the first release cycle.

---

## 7. Rollback plan

- Revert mechanism: the change is contained in one source file (helper + branch) plus
  test files and a changelog line. Reverting the source commit fully restores prior
  behavior; no migrations or data changes are involved.
- Preconditions for rollback: a confirmed regression in gzip/deflate/no-encoding/unknown
  paths, or an unexpected failure introduced by the `br` branch.
- Data considerations: none. The helper only transforms in-memory response bytes; there
  is no persisted state, schema, or wire-format change. Reverting cannot corrupt data.
- Partial rollback option: if only the error contract is wrong, the private helper
  (Step 1) can be adjusted without removing the `br` branch.

---

## 8. Risks and mitigations

- **R1 — aiohttp Brotli import path differs across `aiohttp>=3.0`.**
  Mitigation: Gate A / Step 0 confirms the path; Step 1 private helper contains any
  fallback. (G2, G3.)
- **R2 — Test environment has no Brotli library, so `br` tests error.**
  Mitigation: Steps 3-5 keep optional Brotli imports local and skip when unavailable.
  (G8.)
- **R3 — `br` branch regresses idempotency (double-decompress on second read).**
  Mitigation: Step 2 sets `_decompressed_content = True`; Step 4 idempotency test and
  Gate C guard it. (research Section 4.)
- **R4 — Missing-library path leaks an opaque error instead of `DecodeError`.**
  Mitigation: Step 1 error contract + Step 5 test assert the exact exception and message.
  (D2, G9, G12.)
- **R5 — Accidental change to gzip/deflate/unknown-encoding behavior.**
  Mitigation: additive `elif` only; Gate B re-runs existing suite to confirm A9.
- **R6 — Drift from the future streaming fix.**
  Mitigation: Step 1 single private helper is reuse-ready for Sub-item 3. (D3, G13.)

---

## 9. Definition of done

- `_aiohttp_body_helper` decodes `Content-Encoding: br` bodies; `.body()`, `.read()`,
  `.content`, and `.text()` return correct decoded content with no `UnicodeDecodeError`
  (A8).
- gzip, deflate, no-encoding, and unknown-encoding behavior is unchanged (A9), proven
  by the existing suite staying green (Gate B).
- A `br` response with no Brotli library raises `azure.core.exceptions.DecodeError`
  with a message naming `Content-Encoding: br` and how to install Brotli support (D2).
- New tests cover `br` round-trip, idempotency, and the missing-library case; they pass
  on the fixed code and fail on the pre-fix code (Gate C).
- No new azure-core runtime dependency or pyproject extra is added (D1).
- A correctly formatted unreleased CHANGELOG entry references issue #47186 (Step 6).
- Streaming and `zstd` remain untouched (D3).

---

## 10. Open questions

- **OQ1 — Exact aiohttp Brotli import path/version floor.** Resolved in Step 0 by
  inspecting supported aiohttp versions; if unstable, absorbed by the Step 1 fallback.
- **OQ2 — Exact `DecodeError` message wording.** Resolved during Step 1 by matching
  azure-core exception style while keeping aiohttp's actionable "install Brotli" intent;
  locked by the Step 5 test. (G9, G12.)
- **OQ3 — Target azure-core version number for the release.** Resolved at Step 6 with
  maintainers per normal release versioning (assumptions Q8). Does not block code.
- **OQ4 — Which aiohttp REST test file is the right home for REST-response `br` tests.**
  Resolved in Step 0 by confirming the aiohttp-specific test file from the G7 list.

---

## 11. Out-of-scope observations

Noticed in surrounding code. Recorded so they are not lost. NOT part of this sub-item
and NOT in any plan step above.

- The buffered helper and the streaming `__anext__` each independently hard-code
  `("gzip", "deflate")`. A shared encoding-dispatch helper would stop the `br` branch
  drifting between sites. That is Sub-item 1 (refactor), gated on maintainer approval.
- `zstd` has the identical gap: aiohttp advertises it when `HAS_ZSTD` is present and the
  buffered helper cannot decode it. Tracked separately (assumptions Q4).
- The issue text claims `brotli` is "a common transitive dependency via
  `aiohttp[speedups]`," but azure-core's async extra is plain `aiohttp>=3.0`
  (no guaranteed Brotli library). Worth flagging on the issue; not a code change here.
- The trailing `return response._content` is reached for both unknown encodings and the
  fall-through. Any future multi-encoding or `identity` handling, or multi-value
  `Content-Encoding` parsing, would live near here. Noted only. (G16.)
- The streaming aiohttp path (`__anext__`) is also wrong for `br` today. It is Sub-item 3,
  sequenced after this fix, and will reuse the Step 1 private helper.

---

## 12. Plan changes (recorded during implementation)

### PC1 — Update the Sub-item 1 unknown-encoding pass-through test to stop using `br`

- **What changed:** `tests/async_tests/test_universal_http_async.py::test_aiohttp_response_unknown_encoding_passthrough`
  (added by Sub-item 1) asserts that a `Content-Encoding: br` body passes through
  raw and raises nothing. Sub-item 2 intentionally changes `br` behavior: `br` is
  now decoded, or raises `DecodeError` when Brotli support is unavailable. In a
  test environment without a Brotli library that test would now fail (the body no
  longer passes through; it raises `DecodeError`).
- **Deviation:** The plan (Step 2, Gate B) requires the existing async/transport
  suite to stay green and treats `br` as no longer "unknown", but it did not
  anticipate that a Sub-item 1 characterization test had pinned `br` specifically
  as the unknown-encoding example.
- **Resolution / rationale:** Re-point that test's example encoding from `br` to
  `zstd` (still genuinely unsupported by the buffered helper: `_get_decompressor`
  returns `None` for it and there is no `br` branch match). This preserves the
  test's original intent — proving truly unknown encodings pass through raw — while
  removing the conflict with the new `br` behavior. No production behavior for
  `zstd` changes (it still falls through to raw). This is the minimal change needed
  to keep Gate B satisfiable; it is tied to Step 2.
