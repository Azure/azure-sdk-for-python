# Gaps and Opportunities Critique of assumptions.md

## Summary of what was reviewed

Reviewed `assumptions.md` at the repository root. The document describes assumptions for GitHub issue `#47186`, concerning Brotli (`Content-Encoding: br`) decompression in `azure-core`, especially the aiohttp transport path.

This critique evaluates the assumptions document against the requested rubric only. It does not verify the assumptions against the codebase and does not propose implementation changes.

## Gaps and Opportunities

### G1

- **Location:** `## 0. Should this feature be added? (Evaluation)`
- **Rubric category:** Scope
- **Gap or opportunity description:** This section goes beyond assumptions. It contains investigation findings, a verdict, implementation direction, dependency conclusions, competing designs, and a recommendation. Because later lab steps depend on this file, mixing assumptions with conclusions can make unresolved design choices appear already decided.
- **Recommended action:** Separate factual assumptions from evaluation, recommendation, and design direction. Keep only assumptions that later research can validate or falsify.
- **Disposition:** Address

### G2

- **Location:** `> Added after investigating how aiohttp and azure-core actually handle encodings.`
- **Rubric category:** Specificity
- **Gap or opportunity description:** The document states that investigation has already happened, but several conclusions are presented as settled facts without making clear which assumptions still need human verification. This weakens the document as an assumptions artifact because the reader may not know what is evidence, what is inference, and what remains unverified.
- **Recommended action:** Mark each investigation-derived statement as either an assumption to verify, a confirmed fact with citation, or an open question.
- **Disposition:** Address

### G3

- **Location:** `This supersedes open questions Q1–Q3`
- **Rubric category:** Open-question candidate
- **Gap or opportunity description:** Q1-Q3 are listed under open questions but are marked resolved by Section 0. If they are resolved, they are not open questions; if they are still subject to maintainer or human confirmation, they should not be treated as resolved.
- **Recommended action:** Move resolved items out of the open questions list, or keep them as open questions if the resolution still needs confirmation.
- **Disposition:** Address

### G4

- **Location:** `A3. The streaming aiohttp path (__anext__ in azure/core/pipeline/transport/_aiohttp.py) is also in scope for consistency, even though the issue did not name it.`
- **Rubric category:** Open-question candidate
- **Gap or opportunity description:** This is written as an assumption, but it is really a scope decision. The document later asks Q6, "Is the streaming path (A3) in scope now or a follow-up?", which directly contradicts treating A3 as settled.
- **Recommended action:** Recast A3 as an open question or explicitly label it as an inferred scope assumption pending reviewer confirmation.
- **Disposition:** Address

### G5

- **Location:** `A7. It is not asking to add zstd or any other encoding beyond br.`
- **Rubric category:** Open-question candidate
- **Gap or opportunity description:** A7 asserts that `zstd` is out of scope, but Section 0 says `zstd` has an identical gap and Q4 asks whether to fix `br` only or `br` plus `zstd`. This makes the scope boundary internally inconsistent.
- **Recommended action:** Treat `zstd` as an open scope question instead of a settled out-of-scope assumption.
- **Disposition:** Address

### G6

- **Location:** `A10. When the Brotli library is not installed, the failure is a clear, actionable error rather than an opaque ModuleNotFoundError.`
- **Rubric category:** Open-question candidate
- **Gap or opportunity description:** This describes desired behavior, but the document also says no Brotli dependency is guaranteed and Q3 discusses what should happen when `br` is received without a Brotli library. The error behavior appears to be a design choice rather than a known requirement from the work item.
- **Recommended action:** Move this to open questions or mark it as an inferred acceptance criterion that needs confirmation.
- **Disposition:** Address

### G7

- **Location:** `A15. pyproject.toml and CHANGELOG.md for azure-core may need updates (dependency/extra and changelog entry).`
- **Rubric category:** Specificity
- **Gap or opportunity description:** This assumption is partly obsolete within the same document. Section 0 and A25 say no dependency or extra should be added, while A15 still names dependency or extra updates as possible. This creates ambiguity about whether `pyproject.toml` is actually in scope.
- **Recommended action:** Split dependency, extra, and changelog updates into separate assumptions or questions, and remove the dependency/extra wording if the document intends to treat that decision as resolved.
- **Disposition:** Address

### G8

- **Location:** `A16. The test server route file tests/.../test_routes/encoding.py and related transport tests are the place to add br coverage.`
- **Rubric category:** Scope
- **Gap or opportunity description:** The file path uses an ellipsis, and "related transport tests" is broad. A reader cannot easily identify the exact files or boundaries this assumption applies to.
- **Recommended action:** Name the exact test route file and the specific test module or test family expected to own `br` coverage, or mark the test location as needing discovery.
- **Disposition:** Defer

### G9

- **Location:** `A23. Responses with no Content-Encoding, or with gzip/deflate, behave exactly as before.`
- **Rubric category:** Platitude
- **Gap or opportunity description:** This is directionally useful, but "behave exactly as before" is too broad and would be true of almost any safe bug fix. It does not define which observable behaviors must remain unchanged.
- **Recommended action:** State falsifiable behaviors, such as returned bytes, decoded text, flags, exceptions, header handling, and repeated `.body()` calls for each existing encoding path.
- **Disposition:** Defer

### G10

- **Location:** `A26. The fix must work across azure-core's supported Python versions and not assume aiohttp[speedups].`
- **Rubric category:** Platitude
- **Gap or opportunity description:** "Work across supported Python versions" is a general project requirement unless the document names a version-specific risk. The `aiohttp[speedups]` portion is useful, but the Python-version clause is not yet tied to a specific compatibility concern.
- **Recommended action:** Name the supported version boundary or the specific compatibility risk for Brotli/aiohttp imports; otherwise remove the generic compatibility statement.
- **Disposition:** Defer

### G11

- **Location:** `A27. Security/reliability: decompressing attacker-influenced Brotli bodies should not introduce new unbounded-memory ("decompression bomb") risk beyond what gzip/deflate already accept.`
- **Rubric category:** Specificity
- **Gap or opportunity description:** The risk is valid, but the assumption does not identify a falsifiable boundary. It does not say whether validation should compare limits, streaming behavior, buffering behavior, exception behavior, or parity with existing gzip/deflate handling.
- **Recommended action:** Define what would prove the assumption wrong, such as a code path that buffers unbounded Brotli output differently from existing encodings or bypasses an existing size/streaming safeguard.
- **Disposition:** Defer

### G12

- **Location:** `A30. Evidence for the reviewer: the new br test, an unchanged-behavior test run, and a CHANGELOG entry.`
- **Rubric category:** Coverage gap
- **Gap or opportunity description:** The validation section is useful but thin on exact verification expectations. "Unchanged-behavior test run" is not specific enough for an early-career developer to know which command, package boundary, or test target provides sufficient evidence.
- **Recommended action:** Identify the expected validation scope as an assumption to confirm, such as the package-level test target, the encoding test module, or whether both buffered and streaming paths require tests.
- **Disposition:** Defer

### G13

- **Location:** `Q7. Are the two aiohttp sites the complete set of Content-Encoding inspection points?`
- **Rubric category:** Coverage gap
- **Gap or opportunity description:** This is a strong open question, but its existence reveals a coverage gap in the codebase assumptions. A13, A14, and A17 are written as if the impacted code boundaries are known, while Q7 says the affected surface may be incomplete.
- **Recommended action:** Soften A13, A14, and A17 to indicate they are initial candidate boundaries pending confirmation of all `Content-Encoding` inspection points.
- **Disposition:** Address

### G14

- **Location:** `## 6. Open questions and unknowns`
- **Rubric category:** Coverage gap
- **Gap or opportunity description:** The open questions section mixes resolved traceability items, true unknowns, and design alternatives. This makes it harder to see what must be answered before implementation starts.
- **Recommended action:** Keep only unresolved questions in this section, and separate design alternatives from factual unknowns.
- **Disposition:** Address

## Summary of dispositions

- **G1:** Address
- **G2:** Address
- **G3:** Address
- **G4:** Address
- **G5:** Address
- **G6:** Address
- **G7:** Address
- **G8:** Defer
- **G9:** Defer
- **G10:** Defer
- **G11:** Defer
- **G12:** Defer
- **G13:** Address
- **G14:** Address
