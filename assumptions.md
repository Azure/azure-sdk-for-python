# Assumptions — Brotli (`Content-Encoding: br`) decompression in azure-core

Work item: GitHub issue [#47186](https://github.com/Azure/azure-sdk-for-python/issues/47186)
— `_aiohttp_body_helper` does not decompress `Content-Encoding: br` (Brotli).

This file surfaces assumptions only. It does not propose a plan, a design, or
code changes. Each assumption has a one-line justification tied to the work item.
Resolve the open questions at the end before starting work.

---

## 0. Should this feature be added? (Evaluation)

> This section is evaluation, recommendation, and design direction — not assumptions.
> It is kept separate from the assumptions in Sections 1–5 so design choices are not
> mistaken for settled facts. Read it as follows:
> - Statements with a code citation (file and approximate line) are confirmed facts.
> - Verdicts, conclusions, and the recommendation are inferences that still need
>   maintainer confirmation; they are not decided.
> - Competing designs and scope choices remain open questions (see Section 6).
>
> Added after investigating how aiohttp and azure-core actually handle encodings.
> Verdict (inference, needs confirmation): reframe this as a correctness fix, not a
> new feature.

### Decisive finding
- azure-core deliberately **disables aiohttp's own decompression** — it creates the
  `ClientSession` with `auto_decompress=False`
  (`azure/core/pipeline/transport/_aiohttp.py`, ~L189–192) and re-implements
  decompression itself, but only for `gzip`/`deflate`.
- azure-core does **not** set `Accept-Encoding` itself and does **not** suppress
  aiohttp's auto-header (it only skips `Content-Type`, ~L346). So aiohttp fills in
  its default `Accept-Encoding`. Per aiohttp's `_gen_default_accept_encoding()`
  (`client_reqrep.py` ~L105–114), that default is `gzip, deflate` **plus `br`
  whenever a Brotli library is importable** (`HAS_BROTLI`), plus `zstd` if `HAS_ZSTD`.

### Why this means the fix should be added
- **The SDK already advertises `br`** to servers whenever a Brotli package is present
  (e.g. via `aiohttp[speedups]`, which the issue says is common). A compliant server
  is then entitled to reply `Content-Encoding: br`, and azure-core silently fails to
  decode it. **The SDK promises a capability it does not honor — a self-inflicted bug.**
- Fixing it restores parity with stock aiohttp, whose decode behavior azure-core
  overrode. The failure mode today is a hard `UnicodeDecodeError`, not graceful
  degradation.
- aiohttp already ships `HAS_BROTLI` and a `BrotliDecompressor`
  (`compression_utils.py` ~L288–297) and raises a clear "install Brotli" error when
  absent (`http_parser.py` ~L1020–1026).

### Key implication (resolves the dependency question)
- **`br` is only ever advertised when a Brotli library is already importable.** So a
  compliant server only sends `br` when the decode library is present. The clean
  implementation **reuses aiohttp's own `HAS_BROTLI` / `BrotliDecompressor`** —
  **no new azure-core dependency and no new `pyproject` extra.** When Brotli is not
  installed, raise the same actionable error aiohttp uses; that path only triggers for
  a non-compliant server (the Foundry case in the issue).
- This **resolves former open questions Q1–Q3** (now recorded under "Resolved items" in
  Section 6 for traceability): there is no package choice to make and no extra to add.

### Honest caveats / competing options
- **`zstd` has the identical gap.** aiohttp also advertises `zstd` when `HAS_ZSTD` is
  present and azure-core cannot decode it either. Fixing only `br` leaves a twin bug —
  decide `br`-only vs. `br`+`zstd` with maintainers.
- **Cheaper alternative:** azure-core could instead pin its own
  `Accept-Encoding: gzip, deflate` so servers never offer `br`/`zstd`. Less code, no
  dependency — but it would **not** fix the Foundry case (server sends `br`
  unsolicited) and reduces capability. Legitimate competing design to raise.
- **Sync `requests` transports are unaffected** — `urllib3` handles `br` itself; this
  is purely an aiohttp-transport issue.

### Recommendation
Proceed, treating it as a **bug fix that aligns decode behavior with the
already-advertised `Accept-Encoding`**, implemented by reusing aiohttp's
`HAS_BROTLI`/`BrotliDecompressor` (zero new dependency) in both the buffered helper
and the streaming path. Explicitly decide `br`-only vs. `br`+`zstd` since no spec or
target was provided.

---

## 1. Assumptions about the work item

### What it is asking for
- **A1. The core ask is to make azure-core decompress Brotli (`br`) response bodies the same way it already decompresses `gzip` and `deflate`.**
  - Justification: the issue title and root-cause point directly at the missing `br` branch.
- **A2. The primary fix site is the buffered helper `_aiohttp_body_helper` in `azure/core/utils/_pipeline_transport_rest_shared.py`.**
  - Justification: the issue names this function explicitly as the root cause.
- **A3. (Inferred scope assumption — pending reviewer confirmation, see Q6) The streaming aiohttp path (`__anext__` in `azure/core/pipeline/transport/_aiohttp.py`) is likely in scope for consistency, even though the issue did not name it.**
  - Justification: it contains a second `gzip`/`deflate`-only decompression branch that would leave streamed `br` responses broken. This is a scope decision, not a settled fact; Q6 still asks whether it is in scope now or a follow-up.
- **A4. The fix should be transparent — callers of `.body()` / `.text()` should get decoded bytes without changing their code.**
  - Justification: the issue's "Expected Behavior" says Brotli should be handled "transparently, matching gzip/deflate."

### What it is not asking for
- **A5. It is not asking to change `ContentDecodePolicy` or the sync `requests`-based transports.**
  - Justification: the issue is scoped to the aiohttp async transport; sync transports delegate decompression to the underlying `requests`/`urllib3` stack.
- **A6. It is not asking to fix `FoundryStorageProvider` in `azure-ai-agentserver-responses`.**
  - Justification: that package is only the reporter of symptoms; the requested fix is in azure-core.
- **A7. The issue text only names `br`; whether to also cover `zstd` is an open scope question (see Q4), not a settled out-of-scope decision.**
  - Justification: the issue only mentions Brotli, but Section 0 notes `zstd` has the identical gap, so the boundary is unresolved rather than fixed.

### Acceptance criteria (stated or inferred)
- **A8. A response with `Content-Encoding: br` returns correctly decompressed bytes from `.body()` and decoded text from `.text()` without raising `UnicodeDecodeError`.**
  - Justification: directly mirrors the reported failure mode.
- **A9. Existing `gzip`/`deflate`/no-encoding behavior is unchanged.**
  - Justification: the fix is additive; regressions here would break existing consumers.
- **A10. (Inferred acceptance criterion — needs confirmation, see Q3) When the Brotli library is not installed, the failure should be a clear, actionable error rather than an opaque `ModuleNotFoundError`.**
  - Justification: azure-core does not currently depend on a Brotli package (see A18). This is a design choice rather than a stated work-item requirement; Q3 still discusses what should happen when `br` is received without a Brotli library.

### Priority, deadline, stakeholders
- **A11. This is a customer-reported bug with no stated deadline; treat as normal-priority bug fix.**
  - Justification: issue labels are `customer-reported`, `needs-triage`, `question` — no severity or milestone set.
- **A12. Stakeholders are the azure-core maintainers (owners/reviewers) and the original reporter / Foundry Hosted Agent team.**
  - Justification: azure-core is the changed package; the reporter consumes it via `azure-ai-agentserver-responses`.

---

## 2. Assumptions about the codebase

### Areas likely affected
- **A13. `azure/core/utils/_pipeline_transport_rest_shared.py` (`_aiohttp_body_helper`) is an initial candidate main change site, pending confirmation of all `Content-Encoding` inspection points (see Q7).**
  - Justification: named root cause.
- **A14. `azure/core/pipeline/transport/_aiohttp.py` (streaming `__anext__`) is an initial candidate secondary change site, pending confirmation of all `Content-Encoding` inspection points (see Q7).**
  - Justification: holds the parallel streaming decompression branch (A3).
- **A15. `CHANGELOG.md` for azure-core needs a changelog entry for the user-visible behavior change.**
  - Justification: a user-visible behavior change normally requires a changelog entry.
- **A15a. No `pyproject.toml` dependency or extra update is expected, because Section 0 and A25 resolve that no Brotli dependency or extra is added.**
  - Justification: reusing aiohttp's `HAS_BROTLI` detection means azure-core declares no new dependency or extra.
- **A16. The test server route file `tests/.../test_routes/encoding.py` and related transport tests are the place to add `br` coverage.**
  - Justification: it already defines parallel `/gzip` and `/deflate` routes used by encoding tests.

### Areas out of scope
- **A17. Sync transports (`_requests_basic.py`, `_requests_asyncio.py`, `_requests_trio.py`) and `ContentDecodePolicy` (`_universal.py`) are initial candidate out-of-scope boundaries, pending confirmation of all `Content-Encoding` inspection points (see Q7).**
  - Justification: they do not perform the manual `zlib`-based decompression that the aiohttp path does (A5).

### Existing patterns / conventions
- **A18. `gzip`/`deflate` use the stdlib `zlib` and need no third-party dependency; `br` is the first encoding that would require an external package (`brotli`/`brotlicffi`).**
  - Justification: confirmed by reading both decompression branches.
- **A19. The async extra is declared as `aio = ["aiohttp>=3.0"]` (plain aiohttp, not `aiohttp[speedups]`), so a Brotli package is NOT guaranteed installed.**
  - Justification: confirmed in `pyproject.toml`; contradicts the issue's claim that brotli "is already a common transitive dependency."
  - Update: Section 0 resolves the consequence — reuse aiohttp's `HAS_BROTLI` detection instead of adding a dependency.
- **A20. Decompression is guarded by `_content`, `_decompress`, and `_decompressed_content` and gated on the lowercased `Content-Encoding` header; a new `br` branch must follow the same guard/flag pattern.**
  - Justification: confirmed by reading the helper; matching the pattern preserves idempotency.

---

## 3. Assumptions about behavior

### Current behavior
- **A21. Today a `br` response falls through the helper unchanged and raw compressed bytes reach `.text()`, raising `UnicodeDecodeError`.**
  - Justification: the helper's final `return response._content` with no `br` branch; matches the report.

### Expected behavior after the work
- **A22. After the fix, `br` responses are decompressed in place and the decompressed flag is set so a second `.body()` call does not double-decompress.**
  - Justification: required to match gzip/deflate semantics (A9).

### Behavior that must remain unchanged
- **A23. Responses with no `Content-Encoding`, or with `gzip`/`deflate`, behave exactly as before.**
  - Justification: additive fix; these paths protect existing consumers.
- **A24. When `_decompress=False`, raw bytes are still returned untouched regardless of encoding.**
  - Justification: the opt-out flag is checked before any branch and must keep working.

---

## 4. Assumptions about constraints

- **A25. No new Brotli dependency should be added at all; reuse aiohttp's existing `HAS_BROTLI`/`BrotliDecompressor`.**
  - Justification: Section 0 — `br` is only advertised when a Brotli lib is already importable, so azure-core need not declare one; this supersedes the earlier "optional dependency" framing.
- **A26. The fix must work across azure-core's supported Python versions and not assume `aiohttp[speedups]`.**
  - Justification: follows from A19 and the package's broad support matrix.
- **A27. Security/reliability: decompressing attacker-influenced Brotli bodies should not introduce new unbounded-memory ("decompression bomb") risk beyond what gzip/deflate already accept.**
  - Justification: the work adds a new decompression path and should not regress the existing risk posture.
- **A28. Backward compatibility: no public API signature changes; the change is internal to the transport.**
  - Justification: the issue asks for transparent behavior, implying no surface change for callers.

---

## 5. Assumptions about validation

- **A29. "Done" means a new test asserting a `br`-encoded response round-trips to the original text, plus existing gzip/deflate/no-encoding tests still pass.**
  - Justification: mirrors how `/gzip` and `/deflate` are already tested (A16).
- **A30. Evidence for the reviewer: the new `br` test, an unchanged-behavior test run, and a CHANGELOG entry.**
  - Justification: standard azure-core review expectations for a user-visible fix.
- **A31. Tests already protecting this area are the encoding routes (`/gzip`, `/deflate`) and the transport/universal-http tests that exercise `Content-Encoding`.**
  - Justification: confirmed these routes and tests exist.

---

## 6. Open questions and unknowns

> This section lists only unresolved items. Resolved traceability items are recorded
> separately at the end under "Resolved items".

### Unresolved factual unknowns
- **Q6. Is the streaming path (A3) in scope now or a follow-up?** Confirm with manager/reviewer.
- **Q7. Are the two aiohttp sites the complete set of `Content-Encoding` inspection points?**
  Needs confirmation.
- **Q8. Target azure-core version / CHANGELOG heading?** No spec or target was given;
  needs confirmation.

### Unresolved design alternatives
- **Q4. Fix `br` only, or also `zstd`?** aiohttp advertises and azure-core fails to decode
  both — decide scope with maintainers (Section 0 caveats).
- **Q5. Decode the encodings, or instead pin `Accept-Encoding: gzip, deflate`?** Competing
  design; the pin is cheaper but does not fix the unsolicited-`br` Foundry case (Section 0).

### Resolved items (for traceability)
> Q1–Q3 are resolved by Section 0 (reuse aiohttp's `HAS_BROTLI`/`BrotliDecompressor`;
> no new dependency or extra). They are recorded here, outside the open questions, for
> traceability only.

- **Q1. (RESOLVED) Which Brotli package — `brotli` vs `brotlicffi`?** Defer to aiohttp's
  `HAS_BROTLI` detection, which already supports both. No azure-core decision needed.
- **Q2. (RESOLVED) New extra vs. user-installed dependency?** Neither — reuse aiohttp's
  detection so no `pyproject` extra is added (Section 0).
- **Q3. (RESOLVED) `br` received but no Brotli library installed — error or fall through?**
  Raise the same clear "install Brotli" error aiohttp raises; this only happens for a
  non-compliant server, since `br` is otherwise not advertised (Section 0).

---

## Out-of-scope observations
> Noticed while reading the area. Recorded so they are not lost. NOT part of this work item.

- The decompression logic is duplicated between `_aiohttp_body_helper` (buffered) and `__anext__` (streaming); both list `("gzip", "deflate")` independently. A shared encoding-dispatch helper could reduce drift — but refactoring is out of scope here.
- The issue text asserts `brotli` "is already a common transitive dependency via `aiohttp[speedups]`," which does not match azure-core's actual `aio = ["aiohttp>=3.0"]` extra. Worth flagging back on the issue, but not a code change.

---

## GAO fixes

This section records the Gaps and Opportunities (GAO) items from `assumptions.gao.md`
marked Address, and the change made for each. Items marked Defer (G8–G12) were not
changed.

- **G1** — Section 0 (Evaluation): Added a preamble marking Section 0 as evaluation,
  recommendation, and design direction rather than assumptions, kept separate from the
  assumptions in Sections 1–5.
- **G2** — Section 0 (investigation note): Added a classification rule so each statement
  is read as a confirmed fact (with code citation), an inference needing confirmation,
  or an open question; softened the verdict to an inference needing confirmation.
- **G3** — Section 6 (Open questions): Moved resolved Q1–Q3 out of the open questions
  list into a separate "Resolved items (for traceability)" subsection, and updated the
  Section 0 wording from "supersedes open questions" to "resolves former open questions."
- **G4** — Section 1, A3: Recast A3 as an inferred scope assumption pending reviewer
  confirmation, cross-referencing Q6.
- **G5** — Section 1, A7: Changed A7 from a settled out-of-scope assumption into a
  statement that `zstd` scope is an open question, cross-referencing Q4.
- **G6** — Section 1, A10: Marked A10 as an inferred acceptance criterion needing
  confirmation, cross-referencing Q3.
- **G7** — Section 2, A15: Split the assumption into a changelog-only assumption (A15)
  and a separate assumption (A15a) stating no `pyproject.toml` dependency or extra
  update is expected; removed the obsolete dependency/extra wording.
- **G13** — Section 2, A13/A14/A17: Softened these to initial candidate change sites and
  out-of-scope boundaries pending confirmation of all `Content-Encoding` inspection
  points, cross-referencing Q7.
- **G14** — Section 6 (Open questions): Separated the section into unresolved factual
  unknowns (Q6–Q8), unresolved design alternatives (Q4–Q5), and resolved items (Q1–Q3).

---

## Classification

This section classifies the work item into the three buckets (bug fix, new feature,
refactor). It is based only on the assumptions above. It proposes no code changes.

### Which buckets the work item touches

**Bug fix — yes (primary).**
- Why: Section 0 establishes that the SDK already advertises `br` in its
  `Accept-Encoding` (via aiohttp's default header whenever a Brotli library is
  importable) but then fails to decode a `br` response, producing a hard
  `UnicodeDecodeError`. The SDK promises a capability it does not honor, so adding
  the `br` branch corrects existing wrong behavior rather than inventing new behavior.
- Specific parts: A1, A2, A8 (buffered `.body()`/`.text()` must round-trip `br`),
  A9/A23/A24 (existing gzip/deflate/no-encoding behavior unchanged), A21/A22, A10
  (clear, actionable error when no Brotli library is present). A3/A14 add the parallel
  streaming branch in `__anext__`, which is the same correctness gap in a second site.

**New feature — only if `zstd` is added.**
- Why: For `br` itself, the recommended framing is bug fix, not new feature (the
  capability is already advertised). The genuinely additive piece is `zstd`: aiohttp
  advertises `zstd` and azure-core also cannot decode it (Q4, Section 0 caveats).
  Deciding to also handle `zstd` adds behavior beyond what the issue reports, so that
  part belongs in the new-feature bucket. It is conditional on the Q4 scope decision.
- Specific parts: Q4 ("fix `br` only, or also `zstd`?"). Note the competing design in
  Q5 (pin `Accept-Encoding: gzip, deflate`) is a different approach, not a bucket.

**Refactor — optional, only if the duplicated logic is unified.**
- Why: The decompression dispatch is duplicated between `_aiohttp_body_helper`
  (buffered) and `__anext__` (streaming); both independently list `("gzip", "deflate")`.
  Extracting a shared encoding-dispatch helper changes internals without changing
  externally observable behavior. The assumptions file explicitly flags this as
  out-of-scope today (Out-of-scope observations), so it is optional and needs
  maintainer approval before inclusion.
- Specific parts: the first Out-of-scope observation (duplicated `("gzip", "deflate")`
  logic across the two sites).

### Verdict: the work item spans buckets — proposed split

The work item is not single-bucket. As scoped today it is primarily a bug fix across
two sites, with an optional refactor that would clean up the area first and a
conditional new-feature extension (`zstd`) gated on Q4.

**Sub-item 1 — "Unify decompression dispatch" (Refactor) — optional/conditional.**
- Bucket: Refactor.
- Acceptance criteria covered: none new; must preserve A9/A23/A24 (no externally
  observable change) and keep A29/A31 tests green.
- Condition: only if maintainers lift the current out-of-scope flag on this cleanup.
- Ordering: first, if undertaken. Cleaning up the duplicated branch into one helper
  means the `br` fix is applied once instead of twice and cannot drift between sites.

**Sub-item 2 — "Decode `br` in the buffered helper" (Bug fix) — primary.**
- Bucket: Bug fix.
- Acceptance criteria covered: A8 (buffered `.body()`/`.text()` round-trips `br`),
  A9/A23/A24 (unchanged paths), A22, A10 (actionable error when no Brotli library),
  A29/A30 (new `br` round-trip test plus CHANGELOG entry).
- Ordering: second. This is the named root cause (A2) and the minimum that closes the
  reported failure.

**Sub-item 3 — "Decode `br` in the streaming path" (Bug fix) — conditional on Q6.**
- Bucket: Bug fix.
- Acceptance criteria covered: A8 extended to streamed responses, A9 (streaming
  gzip/deflate unchanged); covered by A3/A14.
- Ordering: third (after Sub-item 2, or merged with it if Sub-item 1 unifies the
  sites). In scope now vs. follow-up is unresolved (Q6).

**Sub-item 4 — "Add `zstd` decoding" (New feature) — conditional on Q4.**
- Bucket: New feature.
- Acceptance criteria covered: none of the stated criteria; extends A8-style coverage
  to `zstd` and would need its own round-trip test and CHANGELOG note.
- Ordering: last. Build the new encoding on top of a clean, correct `br` base.

### Ordering recommendation (summary)

Refactor first (Sub-item 1, if approved) to remove duplication, then the bug fix
(Sub-items 2 then 3) to correct existing behavior, then the new feature (Sub-item 4,
if Q4 says yes). This follows the preferred refactor -> bug fix -> new feature order;
no deviation is warranted here.
