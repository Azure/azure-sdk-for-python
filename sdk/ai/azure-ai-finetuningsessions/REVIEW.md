# PR 47495 review assessment

## Current review status

Source pins and fingerprints are authoritative in [tsp-location.yaml](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/tsp-location.yaml)
and [eng/generation/provenance.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/eng/generation/provenance.json), not historical
SHAs in this assessment. [GENERATION.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/GENERATION.md) documents genuine shared
emission with only nine seeded hooks and exact comparison of the 28-file runtime.
The shared toolchain is emitter **0.63.8**, backend **0.37.3**, compiler **1.16.0**,
and TCGC **0.72.1**. Regeneration includes the upstream unused-import CI fix,
without handwritten generated-source repairs or a package-local emitter override.

Previously deferred API-key transport/origin protection, default no-POST
transport retries, and raw HTTP 200 request-ID polling are now implemented.
Required LoRA configuration/rank, optional `SamplingParams.response_format`, and
the identical `SamplingOperationResult` alias are explicit reviewed contracts in
[eng/generation/review-deltas.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/eng/generation/review-deltas.json).
Non-object error bodies, finite/non-negative retry hints, and positional image
mappings also have focused regression coverage. **Opt-in-only heartbeat startup
remains unimplemented**; convenience creation still starts background heartbeats.

Historical local results (2026-09-24), before the input-chunk/shared-enum work:
**1,637 SDK tests passed on Python 3.13.14**; 20 paired
cases with 134 requests/2,246 checks per SDK; 47 public type names and all 336
original raw cases retained, with 28 extra candidate polling GETs; 328 additional
service/security probes and a 38-case review-contract guard suite passed. The
immutable 48-file oracle at `485774df502642879fdf3a53777be4a0d95155dc` is unchanged.
The main verifier still requires exact finalized inventory/provenance records;
independent comparison results do not waive those checks.

The combined discriminator/enum changes have separate validation on 2026-09-25:
**1,850 public source and installed-wheel tests passed**, plus **1,849 passed
and one expected skip on Python 3.10**. The synchronized Loom SDK passed
**1,869 source and installed-wheel tests** with its master regressions retained.
Exact source/generated/runtime provenance checks pass. The strict comparison
retains all 336 original raw cases and passes 20 paired cases, 328 additional
probes, and 97 mutation guards; all 162 offline API compatibility checks pass.
No live-service, remote CI, publication, or review-approval claim is made.
Custom pipelines/policies remain caller-owned, and no service deduplication
guarantee is implied.

## TypeSpec follow-up decisions

Both comments below are **code-addressed in current source**, not publicly
replied to or resolved. They are separate from the historical SDK review
inventory below.

| Comment | Current decision |
|---|---|
| [4099598821: why an SDK model file?](https://github.com/Azure/azure-rest-api-specs/pull/43961#discussion_r4099598821) | Reuse canonical models where compatible, now including `ModelInput`. The Python-only file has 18 aliases, 22 compatibility models, and three compatibility unions. Retain only intentional constructor/default, optionality/nullability/read-only, inheritance, error, and legacy-result projections; moving these into REST would misstate the service contract. |
| [4099604743: duplicate opt-in union](https://github.com/Azure/azure-rest-api-specs/pull/43961#discussion_r4099604743) | Remove the local `FoundryFeaturesOptInKeys` union and alternate mapping; use Python name/usage customizations on the canonical closed shared union. Preserve the six old names/values and add seven canonical names, without changing the underlying REST union or fine-tuning header. |

The SDK-first input-chunk contract uses canonical `@discriminator("type")`
models, exposed as `InputChunk`, `InputChunkType`, `ModelInputChunk`, and
`ImageChunk`. Existing text keyword/mapping calls remain valid and now emit
`type="text"`. The maintained image subclass retains bytes/base64, size,
signature/format, token-count, and 64-image validation. Canonical `ModelInput`
reuse retains the hook that tags only legacy token mappings without an explicit
`type`; unknown tags stay extensible. The [current contract tables](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/GENERATION.md#current-sdk-first-decisions)
list exact names and remaining projection reasons, including keeping optional
LoRA service defaults off the client and retaining SDK `ejectable`/`FromCheckpoint`.

Local offline evidence uses the actual checked-out `loom_api.schemas`, comparing
tagged/untagged text model dumps and domain conversion, plus direct handlers
with an in-memory provider. Internal text remains `encoded_text`. No production
parser, API/authentication, routes, engine, APIM, or resource-provider change is
part of this SDK-first work, and no live-deployment/GPU result is claimed.
Strict discriminator enforcement and the compatibility policy for older clients
are deferred to public preview (PuPr).

Genuine shared-emitter `0.63.8`/backend `0.37.3` generation of the enum follow-up
changes only the enum, API source metadata, and sync/async operation docstrings;
non-docstring operation executable ASTs are identical and the complete 28-file
runtime matches emitted output. This is separate from the earlier discriminator
generation and is not a final combined test or CI result.

## Historical review inventory

The assessment began at SDK `39c2b3c882526897619785089074176b367099a6` and TypeSpec
`d912f0d0bc6af9e87e0c0833922dd85fa32abf97`. It covered 61 initial inline threads,
12 issue comments, and eight review summaries, then three new threads, one issue
comment, and one review summary: **64 threads / 13 issue comments / nine reviews**.
No APIView comments were present in that retrieval. These are historical inventory
counts, not a fresh remote review or CI query.

## Decisions for every inline comment

Each identifier links to the original comment. Duplicate findings share a fix,
but each original thread is assessed individually. **All 64 replies were local
drafts at that review snapshot; none was publicly posted.** Public posting failed with
HTTP 403 because the authenticated account is an Enterprise Managed User (EMU).
The assessment and local drafts do not constitute posted replies, a posted
handoff, or resolved threads. No authentication bypass was attempted; posting
requires an authorized, supported account/workflow. This documentation update
does not post replies or change thread status.

| Comment | Decision and evidence |
|---|---|
| [3411972237](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r3411972237) | Addressed: changelog uses `1.0.0b1 (2026-09-24)`, not an epoch date. The date is not a publication claim. |
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
| [4049473726](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049473726) | Implemented: default API-key authentication requires HTTPS and the configured origin. Explicit local HTTP opt-in is restricted to that configured loopback origin; cross-origin redirects cannot retain SDK key authentication. Caller-owned pipelines remain outside this guarantee. |
| [4049473833](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049473833) | Same scoped context-header fix; custom policy lists/prebuilt pipelines remain caller-owned. |
| [4049473889](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049473889) | Fixed: remove second pipeline construction, so the policies keyword is passed once. Regression reproduced the prior TypeError. |
| [4049473959](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049473959) | Superseded by the explicit required-LoRA contract: configuration/rank are required in both models and all four sync/async create/resume methods. No empty configuration or inferred rank is supplied. |
| [4049474025](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474025) | Fixed explicit non-batch fields, including user_metadata (which contains the substring data). Preserve legacy fieldless-413 fallback; regression proves batch/nonbatch distinction. |
| [4049474057](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474057) | Fixed shared empty-batch validation; no false success or HTTP submission for empty direct/post/async training calls. |
| [4049474086](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474086) | Fixed by single sync pipeline ownership, preserving injected transport ownership and normal context cleanup. |
| [4049474129](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474129) | Same required-LoRA contract; the intentional required-argument change is documented rather than described as optional compatibility behavior. |
| [4049474193](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474193) | Fixed create and sync training polling: only pending/completed/failed accepted, malformed/unknown status fails immediately. |
| [4049474244](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474244) | Fixed creation Retry-After/pending/network waits: clamp to remaining deadline and fail at expiry. |
| [4049474318](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474318) | Same sampler-ID fix; examples now supply a valid ordinal or path. |
| [4049474375](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474375) | Fixed sync/async sustained-error waits: clamp to remaining armed budget, retaining unbounded healthy pending progress. |
| [4049474413](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474413) | Same required-LoRA contract in async create and checkpoint resume; missing configuration/rank is not a supported default. |
| [4049474454](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474454) | Fixed async create unknown status with immediate protocol error. |
| [4049474495](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474495) | Fixed forward to await the existing cancellation-aware off-loop chunker. |
| [4049474534](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474534) | Fixed forward_post and therefore forward_async through the same off-loop helper. |
| [4049474583](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474583) | Fixed async close and context exit: drain tracked heartbeat tasks before HTTP transport closure. |
| [4049474641](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474641) | Generated API markdown/metadata with pinned official apistub plus repository exporters, not handwritten API declarations. |
| [4049474688](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4049474688) | Same single-pipeline lifecycle fix; private alias refers to the same owned pipeline, not a leaked second transport. |
| [4066580692](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580692) | Implemented default transport policy: no POST retries, including heartbeats, regardless of retry-count/method overrides. Explicit retry policies remain caller-owned. Convenience recovery and ordinary redirects are separate; no server deduplication or exactly-once guarantee is invented. |
| [4066580727](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580727) | Same AI CI artifact registration. |
| [4066580748](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580748) | Partly inapplicable: AI directory already has CODEOWNERS/AI label/service owners. New specific ownership needs owner agreement; Conda release expansion is not implied by adding a PyPI preview. Added explicit in_bundle=false, no global release-policy change. |
| [4066580785](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580785) | Same official API baseline generation. |
| [4066580814](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580814) | Same single-pipeline ownership fix. |
| [4066580850](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580850) | Fixed HTTP and polling hints: invalid, negative, and non-finite values leave typed retry hints unset; non-object error JSON does not cause an attribute error. |
| [4066580877](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580877) | Fixed actual runtime imports and dual-auth union; type-hint regression plus mypy/Pyright. |
| [4066580904](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580904) | Fixed bounded create request-store 404 grace, no second POST; creation deadline still caps waits. |
| [4066580932](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580932) | Fixed sync/async delete rejects unhandled 3xx and preserves async resource mapping on failure. |
| [4066580951](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580951) | Reapplied after parity: shared shielded shutdown task, cancel once, await drain; 22 deterministic ordering/cancellation regressions reactivated. |
| [4066580978](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066580978) | Same empty-batch rejection across shared/post helpers. |
| [4066581014](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066581014) | The stated counting premise is inapplicable: ImageChunk is maintained and base models implement Mapping, so the image-count test already covers them. A distinct mapping-validation bypass identified in review 5272424055 was reproduced and fixed by validating image mappings through ImageChunk. |
| [4066929810](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066929810) | Fixed both sync chunk executors with a fixed 32-worker ceiling, preserving ordered result aggregation. |
| [4066929847](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066929847) | Same CI registration; no standalone duplicate pipeline introduced. |
| [4066929882](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4066929882) | Added raw heartbeat transport and off-origin cleanup coverage. Prepopulated SDK-default direct headers are also scoped; distinct caller overrides remain caller-owned. An identical explicit value is conservatively treated as a default. |
| [4067553898](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4067553898) | Fixed sync create/complete INFO logs to identifiers only; private payload marker regression. |
| [4067553921](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4067553921) | Fixed async completion INFO log; explicit verbose-body opt-in remains unchanged and documented. |
| [4071314957](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4071314957) | Implemented without removing the raw API: sync/async default pollers accept HTTP 200 and GET the session/request ID to completion, with no POST replay, retry, or redirect. Preserve `OperationResult`/`cls`, custom polling, no-polling, and strategy-owned continuation; no synthetic HTTP 202. |
| [4071315018](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4071315018) | Covered by the awaited async client close/context fix, with lifecycle and cancellation regressions. |
| [4071315065](https://github.com/Azure/azure-sdk-for-python/pull/47495#discussion_r4071315065) | Fixed ModelInput field and constructor overload to accept the existing supported text/image union; typing/serialization regression and static checks pass. |

## Issue comments and review summaries

- Human CI request [4711333779](https://github.com/Azure/azure-sdk-for-python/pull/47495#issuecomment-4711333779): addressed by package artifact registration.
- Human binary request [4711364910](https://github.com/Azure/azure-sdk-for-python/pull/47495#issuecomment-4711364910): no wheel/binary artifact is tracked in the PR; validation artifacts stay outside the repository.
- Human shared-lock request [4711371552](https://github.com/Azure/azure-sdk-for-python/pull/47495#issuecomment-4711371552): generation now uses the central shared emitter manifest/lock. The package override is removed; [eng/generation/emitter-package.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/eng/generation/emitter-package.json) and [eng/generation/emitter-package-lock.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/eng/generation/emitter-package-lock.json) are standalone archives of that pair, not a separate old-emitter pin.
- Human spelling request [4711438302](https://github.com/Azure/azure-sdk-for-python/pull/47495#issuecomment-4711438302): package dictionary exists and now contains legitimate terms; CI explicitly loads the root configuration, so a package-scoped root override is necessary too. Tests are not broadly excluded to hide misspellings.
- Stale/closure notices [5365466456](https://github.com/Azure/azure-sdk-for-python/pull/47495#issuecomment-5365466456) and [5448718968](https://github.com/Azure/azure-sdk-for-python/pull/47495#issuecomment-5448718968): historical; the PR had been reopened at the review snapshot. This document does not assert a freshly queried PR state.
- Seven pipeline-analysis comments (5734582572, 5768011529, 5768551504, 5769203598, 5769685768, 5772655667, 5776391975): code was checked rather than trusting stale line numbers. README sections, spelling, typing, payload-safe logs, checkpoint docstrings, and duplicate reason docs were addressed. Removed legacy modules/duplicate classes were obsolete findings. Narrow exceptions preserve intentional preview signatures and hook integration; the historical local lint pass was not exception-free. The new shared emitter incorporates the upstream unused-import fix through generation, not blanket suppression. None of these local results establishes current remote CI success.
- All eight original review summaries and the additional review summary were read, including suppressed/previously-missed findings embedded only in their bodies. These additional findings are assessed below. Human changes-requested state remains for the reviewer; no automated approval or thread-resolution claim is made.

## Findings embedded in review summaries

| Review / finding | Decision |
|---|---|
| [5251142369](https://github.com/Azure/azure-sdk-for-python/pull/47495#pullrequestreview-5251142369): sync unknown poll status | Fixed the explicit pending/completed/failed check; duplicate of the current polling protocol work. |
| 5251142369: sync error-budget Retry-After | Fixed the remaining-budget clamp, with expiry checked at the deadline. |
| 5251142369: async creation Retry-After | Fixed creation deadline clamp and invalid-delay handling. |
| [5272424055](https://github.com/Azure/azure-sdk-for-python/pull/47495#pullrequestreview-5272424055): API markdown/metadata | At that historical snapshot, generated with the official parser/exporter from a clean wheel; not evidence of a new final-wheel validation. |
| 5272424055: sync heartbeat join timeout | Reproduced: a timed-out join could discard a live thread. Heartbeat calls now request bounded I/O; lifecycle fails explicitly and retains the thread reference if it still has not stopped, rather than sending close/delete concurrently. |
| 5272424055: poll error-budget clamp | Addressed with the same sync/async budget fix. |
| 5272424055: async client heartbeat cleanup | Addressed with awaited client close and context exit. |
| 5272424055: image-mapping validation | Reproduced separately from T56's inaccurate class premise. Mapping-form and positional image input now use the same ImageChunk validation as keyword input, including image signatures/token counts. |
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

### Historical CI repair snapshot (2026-09-22)

The old CI build `6867846` failed on Python 3.10's missing `typing.get_overloads`.
AST inspection repaired it without bypassing assertions: that snapshot passed
500 tests with one eager-task skip on Python 3.10, and 501 on Python 3.13.
Its local lint, type, strict Sphinx, README, spelling, and installed-wheel results
remain historical evidence only. Technical exceptions and generation rationale
are retained in [GENERATION.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/GENERATION.md#ci-repair-validation-2026-09-22),
not repeated as current passes.

The original 434-test baseline remains the comparison foundation. Later exact
adaptations and additions are recorded independently; the 48-file source oracle
is not rewritten. The old three-fixture allowance has been superseded by the
specific training-tier and service/security contracts above, not a blanket waiver.

### Merge and release limits

Finalize source pins, test hashes, and provenance through the generation workflow,
then require the main verifier and remote CI to validate those exact commits.
Local passes and documentation updates do not make a PR green or approved.

Earlier runs reported package-name reservation, REST documentation-preview
infrastructure, and EMU comment-posting blockers. Those are historical observations,
not freshly verified statuses; owners must confirm current reservation,
infrastructure, review, and CI state. No authentication bypass or fabricated
SDK fix substitutes for those checks.

No release, deployment, PR merge, public reply, or thread resolution is claimed
by this assessment. Automatic heartbeat startup remains the sole deferred
lifecycle change described here; implemented security/retry/polling fixes should
not be presented as pending design work.