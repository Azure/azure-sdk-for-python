# PR 47495 review assessment

Baseline: SDK `39c2b3c882526897619785089074176b367099a6`, TypeSpec
`d912f0d0bc6af9e87e0c0833922dd85fa32abf97`. The baseline was pushed before review
changes. Loom remains untouched. This assessment covers every original inline
thread (61), issue comment (12), and review summary (8) available at review start,
plus three new threads, one pipeline comment, and one review summary received
during validation (64 threads / 13 issue comments / 9 reviews total).
APIView comments were also retrieved through Azure SDK MCP; none were present.

## Decisions for every inline comment

Each identifier links to the original comment. Duplicate findings share a fix,
but each original thread is assessed individually. **All 64 individual replies
remain local drafts; none was publicly posted.** Public posting failed with
HTTP 403 because the authenticated account is an Enterprise Managed User (EMU).
The assessment and local drafts do not constitute posted replies, a posted
handoff, or resolved threads. No authentication bypass was attempted; posting
requires an authorized, supported account/workflow.

| Comment | Decision and evidence |
|---|---|
| [3411972237](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972237) | Already addressed: changelog uses `1.0.0b1 (Unreleased)`, not an epoch date. |
| [3411972287](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972287) | Already addressed: Prerequisites heading is correct. |
| [3411972312](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972312) | Addressed: valid Python example, consistent indentation, completed sampler arguments; no HTML inside Python. |
| [3411972329](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972329) | Added explicit build gates and Conda bundle opt-out. Did not copy a peer's `verifytypes=false`: missing configuration defaults checks on, so blindly copying that would weaken checks. |
| [3411972361](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972361) | Obsolete: no package-root executable smoke test. Historical superseded tests are archived outside active discovery. |
| [3411972399](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972399) | Obsolete test version: active sampling tests and paired workload supply the required checkpoint ID. |
| [3411972414](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972414) | Same obsolete sampling test; required checkpoint argument retained and exercised. |
| [3411972439](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972439) | Same obsolete sampling test; no public API weakening needed. |
| [3411972463](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972463) | Active serialization checks use `prompt_logprobs` and checkpoint IDs; old camel-case assertion is not active. |
| [3411972492](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972492) | Historical `poll_interval_sec` no longer exists. Current 408 polling waits are nonzero and now deadline-clamped; no obsolete parameter reintroduced. |
| [3411972523](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972523) | Already addressed by canonical-ID normalization; upstream tests cover canonical, legacy, and bare IDs. |
| [3411972551](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972551) | Deferred API/liveness decision: changing automatic heartbeat startup to opt-in changes tested behavior. Fixed shutdown races without changing startup defaults. |
| [3411972577](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972577) | Fixed: require a path or sampling-session ordinal before constructing a fallback checkpoint ID; zero ordinal is valid, no `ssNone` identifier. |
| [3411972606](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972606) | Fixed on supported public hooks: key/token union annotation and documentation; generated configuration source not edited. |
| [3411972633](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972633) | Same dual-auth public typing fix; runtime type-hint resolution tested. |
| [3411972656](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972656) | Obsolete root smoke test; active sampling paths supply checkpoint IDs. |
| [3411972691](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972691) | Already addressed; meaningful package description and no service-description placeholder. |
| [3411972735](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972735) | Retain current tested resource-ID mapping, not the suggested blanket canonical replacement. Legacy resources must use their server-returned ID; regression tests cover both. |
| [3411972768](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972768) | Historical fixture no longer active; new regressions use multi-line method bodies. |
| [3411972793](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972793) | Obsolete root smoke script; no runtime change needed. |
| [3415883733](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3415883733) | Already addressed: Python 3.14 classifier present. This does not claim all Python-version jobs have passed for the new head. |
| [3415889785](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3415889785) | Already addressed: repository URL deep-links to the correctly spelled current package directory. |
| [3415894599](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3415894599) | No root test file remains; normal tests live under tests, historical incompatible tests are archived. |
| [4049473537](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049473537) | Fixed: AI CI artifact entry and safe name added, using the existing service pipeline template. |
| [4049473646](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049473646) | Fixed default raw pipelines with endpoint/session-path-scoped context policy. Actual sync/async transport tests preserve overrides and avoid cross-origin policy-added header leakage. |
| [4049473726](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049473726) | Valid security concern, deferred security/compatibility decision. API-key policy does not enforce TLS; docs explicitly require HTTPS. No claim that VNet or API-key auth makes remote plaintext safe. |
| [4049473833](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049473833) | Same scoped context-header fix; custom policy lists/prebuilt pipelines remain caller-owned. |
| [4049473889](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049473889) | Fixed: remove second pipeline construction, so the policies keyword is passed once. Regression reproduced the prior TypeError. |
| [4049473959](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049473959) | Obsolete fallback: current convenience code omits absent LoRA rather than creating an empty LoRAConfig. Docs show an explicit rank; making an optional argument required is deferred API change. |
| [4049474025](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474025) | Fixed explicit non-batch fields, including user_metadata (which contains the substring data). Preserve legacy fieldless-413 fallback; regression proves batch/nonbatch distinction. |
| [4049474057](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474057) | Fixed shared empty-batch validation; no false success or HTTP submission for empty direct/post/async training calls. |
| [4049474086](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474086) | Fixed by single sync pipeline ownership, preserving injected transport ownership and normal context cleanup. |
| [4049474129](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474129) | Same obsolete empty-LoRA fallback. Service-required validation remains service-side; no breaking required public argument added. |
| [4049474193](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474193) | Fixed create and sync training polling: only pending/completed/failed accepted, malformed/unknown status fails immediately. |
| [4049474244](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474244) | Fixed creation Retry-After/pending/network waits: clamp to remaining deadline and fail at expiry. |
| [4049474318](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474318) | Same sampler-ID fix; examples now supply a valid ordinal or path. |
| [4049474375](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474375) | Fixed sync/async sustained-error waits: clamp to remaining armed budget, retaining unbounded healthy pending progress. |
| [4049474413](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474413) | Same obsolete async empty-LoRA fallback; omission semantics preserved and documented. |
| [4049474454](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474454) | Fixed async create unknown status with immediate protocol error. |
| [4049474495](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474495) | Fixed forward to await the existing cancellation-aware off-loop chunker. |
| [4049474534](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474534) | Fixed forward_post and therefore forward_async through the same off-loop helper. |
| [4049474583](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474583) | Fixed async close and context exit: drain tracked heartbeat tasks before HTTP transport closure. |
| [4049474641](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474641) | Generated API markdown/metadata with pinned official apistub plus repository exporters, not handwritten API declarations. |
| [4049474688](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474688) | Same single-pipeline lifecycle fix; private alias refers to the same owned pipeline, not a leaked second transport. |
| [4066580692](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580692) | Valid non-idempotency concern, deferred service-owner decision. No verified deduplication contract; bounded retry count alone does not make replay safe. No invented dedup key or silent retry-policy change. |
| [4066580727](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580727) | Same AI CI artifact registration. |
| [4066580748](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580748) | Partly inapplicable: AI directory already has CODEOWNERS/AI label/service owners. New specific ownership needs owner agreement; Conda release expansion is not implied by adding a PyPI preview. Added explicit in_bundle=false, no global release-policy change. |
| [4066580785](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580785) | Same official API baseline generation. |
| [4066580814](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580814) | Same single-pipeline ownership fix. |
| [4066580850](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580850) | Fixed malformed 503 hints: invalid, negative and non-finite values leave the typed error's retry hint unset. |
| [4066580877](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580877) | Fixed actual runtime imports and dual-auth union; type-hint regression plus mypy/Pyright. |
| [4066580904](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580904) | Fixed bounded create request-store 404 grace, no second POST; creation deadline still caps waits. |
| [4066580932](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580932) | Fixed sync/async delete rejects unhandled 3xx and preserves async resource mapping on failure. |
| [4066580951](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580951) | Reapplied after parity: shared shielded shutdown task, cancel once, await drain; 22 deterministic ordering/cancellation regressions reactivated. |
| [4066580978](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580978) | Same empty-batch rejection across shared/post helpers. |
| [4066581014](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066581014) | The stated counting premise is inapplicable: ImageChunk is maintained and base models implement Mapping, so the image-count test already covers them. A distinct mapping-validation bypass identified in review 5272424055 was reproduced and fixed by validating image mappings through ImageChunk. |
| [4066929810](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066929810) | Fixed both sync chunk executors with a fixed 32-worker ceiling, preserving ordered result aggregation. |
| [4066929847](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066929847) | Same CI registration; no standalone duplicate pipeline introduced. |
| [4066929882](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066929882) | Added actual raw heartbeat transport assertions, plus override and off-origin cleanup tests. |
| [4067553898](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4067553898) | Fixed sync create/complete INFO logs to identifiers only; private payload marker regression. |
| [4067553921](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4067553921) | Fixed async completion INFO log; explicit verbose-body opt-in remains unchanged and documented. |
| [4071314957](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4071314957) | Valid legacy API limitation; deferred redesign. Replacing/removing raw async LROs changes the explicitly preserved preview surface, continuation/custom polling and return behavior. Use the tested request-ID convenience methods; retaining 202 here is not a claim about the actual HTTP 200 REST contract. |
| [4071315018](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4071315018) | Covered by the awaited async client close/context fix, with lifecycle and cancellation regressions. |
| [4071315065](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4071315065) | Fixed ModelInput field and constructor overload to accept the existing supported text/image union; typing/serialization regression and static checks pass. |

## Issue comments and review summaries

- Human CI request [4711333779](https://github.com/Azure/azure-sdk-for-python/pull/47495#issuecomment-4711333779): addressed by package artifact registration.
- Human binary request [4711364910](https://github.com/Azure/azure-sdk-for-python/pull/47495#issuecomment-4711364910): no wheel/binary artifact is tracked in the PR; validation artifacts stay outside the repository.
- Human shared-lock request [4711371552](https://github.com/Azure/azure-sdk-for-python/pull/47495#issuecomment-4711371552): shared TypeSpec-client lock delta is already absent. The new package-local emitter lock is deliberate reproducibility input for the pinned old emitter, not unrelated shared dependency churn.
- Human spelling request [4711438302](https://github.com/Azure/azure-sdk-for-python/pull/47495#issuecomment-4711438302): package dictionary exists and now contains legitimate terms; CI explicitly loads the root configuration, so a package-scoped root override is necessary too. Tests are not broadly excluded to hide misspellings.
- Stale/closure notices [5365466456](https://github.com/Azure/azure-sdk-for-python/pull/47495#issuecomment-5365466456) and [5448718968](https://github.com/Azure/azure-sdk-for-python/pull/47495#issuecomment-5448718968): historical; PR is open and updated. No reopen/state mutation needed.
- Seven pipeline-analysis comments (5734582572, 5768011529, 5768551504, 5769203598, 5769685768, 5772655667, 5776391975): rechecked current code rather than trusting stale line numbers. README sections, spelling, real typing issues, payload-safe logs, malformed checkpoint docstrings and duplicate reason docs were addressed. Removed legacy modules/duplicate classes are obsolete findings. Intentional legacy parameter/model overrides retain narrow explained type exceptions rather than changing the customer API to match an internal generated base. The remaining Pylint style/complexity failures reported at that review stage are historical: the current local check passes with genuine fixes and explicit line/function exceptions detailed below, not wholesale refactoring or zero exceptions.
- All eight original review summaries and the additional review summary were read, including suppressed/previously-missed findings embedded only in their bodies. These additional findings are assessed below. Human changes-requested state remains for the reviewer; no automated approval or thread-resolution claim is made.

## Findings embedded in review summaries

| Review / finding | Decision |
|---|---|
| [5251142369](https://github.com/Azure/azure-sdk-for-python/pull/47495#pullrequestreview-5251142369): sync unknown poll status | Fixed the explicit pending/completed/failed check; duplicate of the current polling protocol work. |
| 5251142369: sync error-budget Retry-After | Fixed the remaining-budget clamp, with expiry checked at the deadline. |
| 5251142369: async creation Retry-After | Fixed creation deadline clamp and invalid-delay handling. |
| [5272424055](https://github.com/Azure/azure-sdk-for-python/pull/47495#pullrequestreview-5272424055): API markdown/metadata | Generated with the official parser/exporter from a clean wheel. |
| 5272424055: sync heartbeat join timeout | Reproduced: a timed-out join could discard a live thread. Heartbeat calls now request bounded I/O; lifecycle fails explicitly and retains the thread reference if it still has not stopped, rather than sending close/delete concurrently. |
| 5272424055: poll error-budget clamp | Addressed with the same sync/async budget fix. |
| 5272424055: async client heartbeat cleanup | Addressed with awaited client close and context exit. |
| 5272424055: image-mapping validation | Reproduced separately from T56's inaccurate class premise: Mapping-preserving ModelInputChunk could carry unchecked image fields. Image mappings now pass through the same ImageChunk validation before acceptance; invalid signatures/token counts are regression-tested. |
| [5272785483](https://github.com/Azure/azure-sdk-for-python/pull/47495#pullrequestreview-5272785483): lastResort format explanation | Corrected docs to Python's actual message-only default; no logging behavior changed. |
| [5273142018](https://github.com/Azure/azure-sdk-for-python/pull/47495#pullrequestreview-5273142018): pending creation backoff | Fixed the same creation deadline clamp for pending responses, not just Retry-After. |
| 5273142018: create request-store 404 | Fixed bounded grace without re-POSTing creation. |
| 5273142018: async client close | Fixed shared awaited cleanup before transport closure. |
| [5274881761](https://github.com/Azure/azure-sdk-for-python/pull/47495#pullrequestreview-5274881761): sync heartbeat race | Same fail-before-lifecycle fix; arbitrary transports cannot be forcibly interrupted safely. |
| 5274881761: Future returned where Task promised | Fixed completed-wave/multichunk branches to return a completed asyncio.Task, retaining the existing public annotation; Task-specific methods and result are tested. |

The first bot overview (4495594229), human review (4500291998, no body), and
overview 5272030241 add no body-only implementation request beyond their inline
comments. New overview 5277661196 reiterates the three new inline findings and
existing security/CI/lifecycle requests above. All remain in the response inventory.

## Validation and limitations

### Historical CI and current local repair snapshot (2026-09-22)

The baseline's acceptance results, earlier review-stage installed-wheel results,
and pinned mypy/Pyright passes remain historical evidence. They are not a final
validation of the in-progress CI-repair batch. No results or commit-link handoff
were posted publicly: the EMU HTTP 403 blocker above remains.

- **SDK baseline CI build `6867846`:** Python 3.10 failed when a surface test
	imported `typing.get_overloads`. The repair uses AST overload inspection on
	all Python versions. Current local tests: **Python 3.10, 500 passed and 1
	skipped** (the eager-task test requires Python 3.12+); **Python 3.13, 501
	passed**. Other supported-Python remote jobs are not certified by these runs.
- **Pylint 4.0.4 + Azure checker 0.5.7: local PASS.** Real helper documentation
	and dictionary-literal fixes address applicable findings. Explicit
	line/function-level exceptions retain the preview API parameter renames and
	private hook integration, 19 class-alias/constant false positives, actual
	`asyncio.Task` use required by the return contract, a long public name, and
	existing complex state machines. The pass is not exception-free and does not
	mean all findings were refactored away.
- **Strict Sphinx 8.2: local PASS against the actual sdist.** The repository
	documentation override supplies five namespace RST pages; all verification
	scripts remain in the sdist. Only external intersphinx inventory downloads
	were disabled for offline operation, not the strict content checks.
- **Actual MCP README check: PASS.** The last completed root-configuration
	CSpell run checked **84 files with 0 issues**. Neither result is a claim of
	full remote README/documentation or repository CI success.
- **TypeSpec compiler 1.16: local PASS with warnings treated as errors** for
	both full REST and Python entry points. All changed TypeSpec files pass formatting.
	Exact REST comparison permits only three expected error-field descriptions
	for `OpenAI.Error.details`, `additionalInfo`, and `debugInfo`; HTTP, structural
	schemas, and protocol are unchanged.
- **Compatibility exceptions remain reviewable:** the standard-RPC trial was
	rejected after introducing path warnings. There are 15 raw-operation plus 13
	facade `use-standard-operations` exceptions, 9 legacy-augment exceptions, and
	1 inheritance exception, each on its exact node with a known compatibility
	rationale. Human approval is still required. The 14 C#-only `clientName`
	`Content`/`Result` mappings address non-Python naming lint without changing
	Python or wire types; other languages still require CI validation.
- **Actual MCP SDK generation: PASS.** Clean output now enables
	`generate-packaging-files=true`; maintained-SDK generation explicitly uses
	`generate-packaging-files=false` to preserve its packaging. A separate pinned
	emission currently matches all 21 generated inventory entries, including the
	generated model documentation-only update. Final two-emission provenance
	validation and all paired API/behavior checks pass.

The baseline's original **434 tests** are not removed: two helper mocks are
adapted and new focused tests are added. Three original test files contain only
an added final newline; their exact hashes are explicitly recorded. The verifier permits only the exact
three fixture contracts listed in the review-delta manifest (direct headers,
dual-auth typing, and the already-supported multimodal input typing).

### Pending work and external blockers

Formatting and repeated generation/provenance checks pass locally. The final
source pointer is recorded in package provenance. Remote CI must rerun on the
pushed commits; local passes do not make the PR fully green.

- The PyPI package name is **not reserved**; reservation requires the approved
	pipeline, not a code-only change or direct publication.
- REST `api-doc-preview` is blocked by a missing repository script and an
	invalid infrastructure AAD client secret. These require infrastructure-owner
	repair, not a fabricated SDK/specification fix or authentication bypass.
- The 64 review replies remain local drafts because public posting failed with
	EMU HTTP 403. Human review, exception approval, and other-language CI remain
	outstanding.

No live GPU jobs, deployments, package publication, force-pushes, PR merges,
Loom edits, security-policy weakening, or invented server deduplication are used.
Repository-wide CI and reviewer approval are not implied by local passes.