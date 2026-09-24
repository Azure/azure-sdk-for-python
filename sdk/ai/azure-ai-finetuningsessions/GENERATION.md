# Reproducible preview SDK generation

## Training-tier names and string constraints (2026-09-23)

The current source pin is TypeSpec commit
`3bf298e19180ed0829e922c81b3dbd99146b859e`. These two follow-up changes are
committed separately and do not change the Python API or runtime:

- `449e55c8714` renames only the `FineTuningTrainingType` member identifiers to
  `global_standard`, `datazone_standard`, and `developer_tier`. The wire values
  remain `GlobalStandard`, `DatazoneStandard`, and `DeveloperTier`; the union
  remains open to other strings. This rename leaves all four REST outputs
  byte-identical. No service work item was created.
- `3bf298e1918` adds `@minLength(1)` to 11 response identifier declarations and
  16 route parameters: 13 session paths, one checkpoint path, the checkpoint
  query, and one request path. The four previously constrained checkpoint
  save/reference fields retain their existing patterns and length limits.
  Model spreading produces 12 response-property constraints per OpenAPI
  document. These 12 additions and 16 parameter constraints are the only REST
  output changes; requiredness, nullability, routes, headers, request bodies,
  response codes, and wire values are unchanged.

The audit was checked against service validation and identifier production.
Session/request identifiers are service-produced; checkpoint names are
validated on save or generated for sampler checkpoints. Empty identities do
not identify a valid session, checkpoint, or request. Free-form text, errors,
messages, metadata, stop strings, and extensible string variants remain
unconstrained. No minimum was inferred for `base_model` or `model_name`:
model-catalog validation can be skipped in development/test configurations.
Optional `sampling_session_id` also remains unconstrained because its current
schema permits an empty string when `seq_id` is supplied. The optional
heartbeat response identifier remains optional; its minimum applies only
when the service includes it.

Actual SDK generation into clean staging, seeded with only the nine maintained
hooks, matches two independent pinned emissions: all 21 generated inventory
entries and the complete 28-file runtime are unchanged from public SDK
`96b410cbdb8567b1aae76677566ea300236613bf`. The public and Loom runtimes remain
byte-identical. Only the source pin, provenance, and generation documentation
are updated; no generated source, hook, test, or comparison rule is rewritten.

Both existing Python 3.13 source suites pass all 501 tests. The unchanged
immutable-reference gate passes 20 paired convenience cases, 134 requests and
2,246 checks per SDK, plus 45 public types and 336 raw-operation cases using
only the previously reviewed contracts. The current public/Loom surface
comparison has zero differences and requires no exceptions. REST and Python
entrypoints compile with warnings treated as errors; TypeSpec validation and
canonical formatting pass. Wheels were not rebuilt for this runtime-unchanged
follow-up; earlier wheel results below remain historical, not new test runs.
No live-service validation, release, or remote-CI success is claimed.

References: [named union variants](https://typespec.io/docs/language-basics/unions/#named-unions)
and [string minimum lengths](https://typespec.io/docs/standard-library/built-in-decorators/#@minLength).

## Foundry review batch (2026-09-23)

The source pin for this review batch was TypeSpec commit
`68b7f96fdabbeb966213596cc92ddfec207e52cc`. The shared Foundry service namespace
and the independent `azure-ai-finetuningsessions` Python package are unchanged.
The following decisions address the numbered review comments. Related comments
3/4 and 6/8 share a commit rather than duplicating the same change.

| Comments | Decision and reason | TypeSpec commit |
|---|---|---|
| 1 | Retain `utcDateTime` and document RFC 3339 strings. The current service serializes these timestamps as strings; adopting Unix-encoded `FoundryTimestamp` would require a coordinated wire-format migration. | `f328f6f7237` |
| 2 | Add `@minLength(1)` to all four checkpoint/reference properties whose existing anchored `+` patterns already reject empty strings. Do not impose unverified restrictions on free-form strings. | `d1c79498f12` |
| 3, 4 | Use the existing extensible `FineTuningSessionType` in the create response, matching the request and session resource while retaining future string values. | `eef0597d330` |
| 5 | Add the actual `created` initial status to the extensible REST union. The Python preview projection remains unchanged. | `08bcdccafd3` |
| 6, 8 | Omit redundant deletion/heartbeat identity markers from the REST models; neither is a union discriminator. Make heartbeat `session_id` optional because existing service responses can omit it. Existing additional wire fields and Python compatibility models are retained, not removed from deployed services. | `3f912750975` |
| 7 | Retain and explain meaningful session-category, image-input, and sampler-command `type` properties. Renaming existing request keys would change the wire contract. | `38b003f6c2e` |
| 9 | Use `FoundryDataPlaneRequiredPreviewOperation` with the shared API-version parameter and `ApiErrorResponse`. Retain the optional `x-ms-error-code` response header and required preview opt-in. | `64c55f134a2` |
| 10 | Remove the redundant service-import file and import shared dependencies directly. Service identity and generated REST output are preserved. | `68b7f96fdab` |

Earlier pending comments were committed separately: the input-chunk union move
in `f99783d5ff3`, and explicit fixed defaults plus consistent service-default
wording in `5228c5cd596`. Rank, random seeds, derived weights, and conditional
training-tier defaults were not replaced with invented constants.

The operation-template comparison covers both REST versions: all 13 paths and
15 methods retain their request bodies, HTTP 200 success responses, required
API-version query, and required preview header. Parameter ordering changes and
the shared API-version parameter no longer declares the old `minLength: 1`;
the 4XX/5XX body references now use the shared error model. These are explicit
metadata changes, not a claim that the OpenAPI files are byte-identical.

Actual Azure SDK MCP generation agrees with independent pinned emission.
The final nine maintained hooks reproduce all 21 generated inventory entries
and the complete 28-file runtime in two clean emissions with no diagnostics.
The maintained request hook preserves the previous API-version query ordering
without rewriting generated builders or relaxing compatibility checks.

The synchronized Loom runtime has the same 28 files, byte-for-byte, as this
public package. Its tests retain every original assertion, adapt the two
private heartbeat mocks to the already-reviewed async cleanup, and include
the public regression tests. Source validation passes 501 SDK tests in each
repository and 17 lightweight cookbook contract checks; the heavyweight
cookbook import test is not included. The current public/Loom comparison has
zero differences across 20 convenience cases, 45 public types, and 336 raw
operation cases. The immutable upstream reference remains separate and uses
only the existing reviewed contracts, with no new exceptions.

These are local reproducibility and offline compatibility results, not live
service/GPU validation, a package release, or a claim that remote CI is green.
All older validation sections below describe their stated historical snapshots.

## Operation coverage documentation (2026-09-23)

TypeSpec commit `ff3fe7d6edc892aed8079760ba41a7289f64eab1` expands only line
comments explaining the intentional exclusion of raw generated session deletion
and forward-only operations. The package README documents the existing sync
and async convenience entry points, including chunking, request-ID polling,
heartbeat shutdown, and deletion response handling. These maintained hooks are
included during regeneration; both REST operations remain defined.

That source pin and its source/client fingerprints include this comment-only
change. Operation scopes, the generated API and metadata, runtime code, tests,
generator pins, and compatibility expectations are unchanged. Adding raw
operation-group methods would be a separate additive API change.

## Shared Foundry feature opt-in review (2026-09-23)

The shared `FoundryFeaturesOptInKeys` union now omits the bare `string` variant
and retains all 13 named feature keys. API review requested a declaration-scoped
`no-closed-literal-union` suppression, matching the agent-definition opt-in
contract. This is a specific reviewed exception to the general extensible-union
rule, not an automatic exemption for all input-only unions. The SDK-only Loom
model projection and all route/client customizations remain unchanged.

This review was validated at TypeSpec `b3d1b8bcfaddba25fc07188672a4a4d5c80cc501`:

- Full Foundry and fine-tuning Python entrypoints compile with warnings treated
  as errors; TypeSpec validation and the canonical formatting check pass.
- The shared Java agents, Java projects, and Python/JavaScript projects client
  entrypoints also compile with warnings treated as errors. Their language
  packages were not regenerated or certified unchanged.
- All four independently regenerated REST OpenAPI files are byte-identical to
  the committed outputs, so no tracked OpenAPI update is needed.
- The unchanged generation verifier matches all 21 generated inventory entries
  and the complete customized runtime in two independent pinned emissions,
  without diagnostics. All 501 existing Python 3.13 tests pass.
- No runtime, API metadata, test, verifier, or comparison exception changed.

The reviewed TypeSpec change was pushed at
`b3d1b8bcfaddba25fc07188672a4a4d5c80cc501`. The operation-coverage documentation
above advances the current source pin without changing this reviewed contract
or SDK runtime. The generation and test results in this section describe the
feature opt-in review snapshot.

References: [TypeSpec suppression directives](https://typespec.io/docs/language-basics/directives/)
and [the extensible-union rule](https://azure.github.io/typespec-azure/docs/libraries/azure-core/rules/no-closed-literal-union/).

## Route-deduplication refactor (2026-09-23)

The public TypeSpec client customization now reuses the service operations in
`session-finetuning/routes.tsp` instead of declaring routed SDK interfaces and
operation aliases. Python-scoped `@clientName` and `@clientLocation` retain the
root client and five flat groups. `@scope("!python")` excludes only the same two
raw operations omitted before: session deletion and forward-only training. The
handwritten convenience methods remain unchanged. Model mappings, required
per-call API version, method names, and legacy polling/pagination decorators
remain in the Python customization file. The operation-template migration is
not included.

Baseline TypeSpec commit: `a170cb1188d5fc706a6433a0c95a13caf30c72fe`.
Baseline SDK commit: `df4b722725386974c26463fb375ba7e27f6511fb`.
The baseline and two independent candidates use the same pinned generator and
the same nine maintained hooks. All generated Python and the complete runtime
are unchanged, as are all four full REST OpenAPI outputs. The sole emitted
metadata delta is 26 APIView operation identifiers (13 methods in sync/async)
changing from alias identities to canonical service identities; package/model
identifiers and the customer API are unchanged.

Both isolated source packages pass all 501 tests and the existing full Loom
comparison (20 paired cases, 45 exported types, 76 model cases, 336 raw cases).
The installed candidate wheel passes the same tests and compatibility checks.
No test, verifier, or approved comparison exception was changed.

The TypeSpec refactor was pushed at
`05c7c9af0f866ed349f9d7e0870eb7d2d849d1de`, with committed inputs matching the
validated working-tree hashes. The later reviews above advance
the current source pin without changing this refactor. The starting commits
above remain the comparison baselines.

## Reviewed fixes after the parity baseline

The independently reproducible exact public-API parity baseline is SDK commit
`39c2b3c882526897619785089074176b367099a6`, pinned to TypeSpec
`d912f0d0bc6af9e87e0c0833922dd85fa32abf97`. Subsequent review fixes are listed in
[review-deltas.json](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/review-deltas.json) and [REVIEW.md](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/REVIEW.md); the baseline
results below remain historical evidence, not a claim of zero behavior changes.

Current tests preserve all upstream cases, adapt two private heartbeat mocks to
the now-awaitable helper, and add lifecycle/protocol/header regressions. Three
upstream test files have only a final newline added by the generation formatter;
their exact hashes and reasons are recorded separately from behavior changes. The
compatibility verifier checks those exact test hashes. Its only fixture changes
are explicitly expected direct-context headers on raw calls, widened
credential annotations for already-supported API keys, and multimodal input
annotations matching the already-supported image chunks; all other API, payload,
serialization, raw operation and convenience results remain exact.

Heartbeat shutdown is now awaited, default sync pipeline ownership is unified,
and creation/error waits are bounded. The security policy for remote API-key HTTP,
non-idempotent submission retry contract, and opt-in heartbeat redesign are
deliberately deferred for the reasons recorded in the review assessment.

## CI repair validation (2026-09-22)

These results describe local validation of the CI fixes, not a green remote CI
run. The parity-baseline results and immutable commits above and below remain
historical evidence.

### Historical SDK CI failure and current local checks

- SDK baseline CI build `6867846` failed on Python 3.10 because the surface test
  imported `typing.get_overloads`, which is unavailable there. Overload checks
  now use AST inspection on every Python version, not a version-specific bypass.
  Local Python 3.10: **500 passed, 1 skipped**; the eager-task test requires
  Python 3.12 or later. Local Python 3.13: **501 passed**. These are not results
  for every supported-Python remote job.
- **Pylint 4.0.4 with Azure checker 0.5.7 passes locally.** Helper documentation
  and dictionary literals were genuinely fixed. Explicit line/function-level
  exceptions remain for preserved preview API parameter renames, private hook
  integration, 19 class aliases misclassified as constants, actual `asyncio.Task`
  use required by the return contract, a long public name, and existing complex
  state machines. This is neither zero exceptions nor a claim that every finding
  was refactored away. Earlier reports of remaining Pylint failures are historical.
- **Strict Sphinx 8.2 passes against the actual sdist**, using the repository
  documentation override with five namespace RST pages. All verification scripts
  remain in the sdist. Only external intersphinx inventory downloads were disabled
  for the offline build; strict documentation checks were retained.
- The actual MCP README check passed. The last completed spelling check using
  the root CSpell configuration covered **84 files with 0 issues**. These local
  checks do not establish full repository CI success.

### TypeSpec, contract, and generation checks

- With compiler **1.16**, the full Foundry REST entry point and the Python entry
  point both pass compilation with warnings treated as errors. All changed
  TypeSpec files pass the canonical formatter check. This is distinct from the pinned
  legacy emission toolchain documented below.
- Exact REST output comparison proves that only three expected error-field
  descriptions changed: `OpenAI.Error.details`, `additionalInfo`, and
  `debugInfo`. No HTTP, structural schema, or protocol change was introduced.
- A standard-RPC trial was rejected because it introduced new path warnings.
  Retained exact-node compatibility exceptions comprise **15 raw-operation and
  13 facade `use-standard-operations` exceptions**, **9 legacy-augment
  exceptions**, and **1 inheritance exception**. Their known compatibility
  rationales must remain explicit and require human review; a local compiler
  pass does not approve them.
- **14 C#-only `clientName` mappings** apply `Content`/`Result` names to raw
  types to address non-Python naming lint. Python names/types and wire types are
  unchanged. Other-language SDKs still require their own CI validation.
- The TypeSpec default `generate-packaging-files=true` addresses clean MCP
  output missing [pyproject.toml](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/pyproject.toml).
  Maintained-SDK generation deliberately overrides this with
  `generate-packaging-files=false` to preserve the reviewed packaging inputs.
- **Actual MCP SDK generation passed.** A separate pinned emission currently
  matches all **21 generated inventory entries**, including the generated model
  documentation-only change. This is distinct from the historical automatic
  customizer's `ManualInterventionRequired` result. Two independent emissions
  reproduce all generated files and the complete customized runtime. The exact
  provenance gate and complete API/behavior comparison also pass.

### Pending handoff and external blockers

Final repeated generation/provenance results and the TypeSpec source pointer
are recorded in the package provenance. Remote CI must rerun on the pushed
commits; local passes do not establish remote success.

The PyPI package name is **not reserved** and requires the approved reservation
pipeline. REST `api-doc-preview` is blocked by a missing repository script and an
invalid AAD client secret in its infrastructure. Neither is a missing SDK code
fix; no fabricated code workaround or authentication bypass is appropriate.

## Customer artifact and compatibility target

This package is generated from the Python-specific TypeSpec entry point in the
public `Azure/azure-rest-api-specs` repository, plus supported maintained Python
customizations. The resulting public package builds the customer wheel
`azure-ai-finetuningsessions` version `1.0.0b1`, importing
`azure.ai.finetuningsessions`.

The compatibility oracle is the tested Loom SDK at immutable commit
`485774df502642879fdf3a53777be4a0d95155dc` (last SDK change `770f7e0d23`). It
includes the upstream nested HTTP 503 and typed `engine_dead` fixes. The agreed
rename is the only transformation applied to that **reference**. The regenerated
parity baseline preserves its customer API and behavior through supported hooks;
subsequent review deltas are tracked separately. Internal files and implementation
locations are not byte-identical.

[loom-source.json](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/loom-source.json) remains the original 48-file reference
manifest, not a claim that current runtime hashes equal Loom. It covers 29
reference runtime files including Azure namespace parents, and 19 upstream test
files. [generation-provenance.json](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/generation-provenance.json) separately records
the TypeSpec fingerprint, emitter pins, and generated runtime for this validated
CI-repair batch.

## Source pipeline

1. The SDK-only `client.tsp` selects the shared Foundry service and existing REST
   operations. Python-scoped decorators retain the client/group names, per-call
   `api_version`, `optim_step`, explicit lists, and legacy `begin_*` surface.
2. SDK-only `loom-models.tsp` defines the tested preview model shapes. Supported
   `@alternateType` mappings keep those shapes separate from real REST schemas.
3. The pinned emitter produces clients, operations, models, enums, helpers,
   package initializers, metadata, and the cross-language API map.
4. Maintained `_patch.py` modules supply the tested training conveniences and
   operation/model overrides. Private custom modules provide auth, errors,
   logging, and legacy raw operation integration. These are inputs, not output
   copied from a finished target SDK.
5. The wheel is built normally with setuptools from the public SDK package.

No unified-diff rewriting or arbitrary generated-file mutation is required.
When generating into a clean directory, seed **only** the five maintained patch
modules and four explicitly maintained helper modules before emission. The
emitter preserves them, applying its pinned formatting. Never seed generated
clients/models/operations or copy the frozen SDK over the result.

### Maintained integration

| Location | Responsibility |
|---|---|
| Root and aio patch modules | Original Loom training, request-ID polling, retries, chunking, IDs, lifecycle, logging/exports; supported client subclasses |
| Model patch module | Existing images/checkpoint helpers; exact nested nullable sampling tuple annotations and checkpoint `Dict` overload |
| Sync/async operation patch modules | Exact public raw signatures and all overloads; JSON create and legacy pollers |
| [_client_options.py](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/azure/ai/finetuningsessions/_client_options.py) | API key/token selection, loopback-only HTTP policy, moniker, preserved private configuration imports |
| [_operation_compat.py](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/azure/ai/finetuningsessions/_operation_compat.py) | Legacy raw error/stream/result/continuation behavior using generated builders; one legacy sampling request builder |
| Exception/logging modules | Tested upstream implementation at parity baseline; later reviewed exception fixes and documentation changes tracked separately |

At the parity baseline, the original training function bodies and
exception/logging behavior were AST-compared with Loom. Only client
construction/export binding and supported integration changed. That baseline
excluded the public-only awaited heartbeat shutdown fix and retained cancel-only
shutdown. The subsequent review stage added the awaited shutdown described above;
the historical comparison is not a claim that current review fixes are absent.

### Known legacy behavior retained

- Actual training conveniences submit HTTP 200 and poll request IDs.
- Synchronous raw `begin_*` helpers accept HTTP 200; asynchronous raw `begin_*`
  helpers retain the older HTTP 202 expectation. Their Azure polling/result
  envelope, continuation/custom-polling behavior, and rejected streaming options
  are preserved, not corrected by claiming a different REST contract.
- Raw `sessions.create` returns JSON, and raw `operations.get` returns
  `OperationResult`, as before. Legacy raw sampling has no required checkpoint
  query argument; the actual REST operation still requires it.
- The route is `/fine_tuning/sessions`, API version `v1`, with
  `Foundry-Features: FineTuningSessions=V1Preview` and the original
  `finetuning-sessions/1.0.0b1` user-agent moniker.

## Pinned generation tools

[emitter-package.json](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/emitter-package.json) and
[emitter-package-lock.json](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/emitter-package-lock.json) pin the isolated JavaScript
toolchain, including Python emitter `0.61.3`, `http-client-python` `0.28.3`,
TypeSpec compiler `1.11.0`, and TCGC `0.67.3`.
[generator-requirements.txt](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/generator-requirements.txt) records the Python backend
versions. The normal emitter bootstrap/local `pygen` package is still required;
the requirements file does not add SDK runtime dependencies. Validation used the
existing Node 24.14.1 and Python 3.13 tool environments.

Use the standard SDK generation workflow with the package-local emitter manifest
and the local TypeSpec source. The checked-in verifier accepts `--spec-repo` and
`--toolchain`, so it can use a separate pinned installation without changing
shared repository dependencies. This package's toolchain intentionally differs
from the current full Foundry REST compiler.

Azure SDK MCP was used for ambiguity and customization guidance. Its automatic
customizer classified the substantial handwritten integration as
`ManualInterventionRequired`; it did not perform or validate this implementation.
The documented Python subclass/`__all__`/`patch_sdk()` workflow was used instead.

## Baseline acceptance checks (before review fixes)

- [verify_generation.py](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/verify_generation.py): emits twice from independent
  source snapshots with only maintained customizations pre-seeded; compares all
  **21 generated inventory entries** and the complete runtime. Missing, orphan,
  changed, or unstable files fail. It never updates the package.
- [verify_loom_snapshot.py](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/verify_loom_snapshot.py): verifies all immutable
  upstream Git blobs and exact name-normalized reference hashes. `--snapshot`
  optionally verifies an archived byte-identical reference, not this regenerated
  implementation.
- [verify_loom_compatibility.py](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/verify_loom_compatibility.py): verifies the exact
  19 upstream test files, materializes the immutable reference, runs the original
  **20 paired cases / 134 requests / 2,246 checks per SDK**, then invokes the
  complete public-surface/raw-operation check. No API additions are allowed.
- [verify_loom_surface.py](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/verify_loom_surface.py): isolated comparison of all
  **45 exported types (38 models and 7 enums)**, every field/visibility/type,
  constructor and method signature/overload, 11 exception types, **76 model
  construction/serialization cases**, and **336 raw-operation cases**. Includes
  sync/async errors, streams, binary bodies, default/custom polling, and custom
  continuation; tests use blocked-network fake transports.
- The unchanged **434 upstream tests** pass on generated source and an isolated
  installed wheel. No deferred public-only tests are counted as passing.
- The wheel contains **27 namespace Python modules plus `py.typed`**, with exact
  source bytes, valid metadata/CRC, and no shared Azure initializers, tests,
  old namespace, or build leftovers. The original model/serialization helpers
  and `_types.py` are byte-identical after newline normalization to Loom.
- Complete Foundry REST compilation before/after: all **four OpenAPI files
  byte-identical**, 29 warnings. Pinned Python emission: 99 warnings, zero errors.

These checks establish local reproducibility and offline compatibility, not
live GPU/service validation, review approval, all supported-Python CI, or
cross-language SDK readiness.

## Current source pin and review validation

[tsp-location.yaml](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/tsp-location.yaml) pins public TypeSpec commit
`68b7f96fdabbeb966213596cc92ddfec207e52cc`, which contains the validated model
projection, route-deduplicated client customization, CI repairs, and closed
agent-definition and shared Foundry feature opt-in unions. It also documents
the maintained forward-only and deletion entry points and includes the review
decisions listed in the current batch above. Its source fingerprint
and remote-generation status are recorded separately
in [generation-provenance.json](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/generation-provenance.json). The preview-parity
baseline is committed separately from subsequent review fixes so it remains
independently reproducible. Two independent emissions verified these exact
inputs, and the source pin now names their pushed TypeSpec commit.

The [agent opt-in review](https://github.com/Azure/azure-rest-api-specs/pull/43961#discussion_r4073849886)
removes the unrestricted `string` member from `AgentDefinitionOptInKeys` only.
All named values and version annotations remain, and `FoundryFeaturesOptInKeys`
is unchanged. All four REST outputs change only that schema's extensibility.
Regeneration leaves all 21 generated entries and the complete fine-tuning SDK
runtime unchanged; no client, model, serialization, or handwritten-code fix is
needed. This source-pin update records the reviewed shared TypeSpec input.

Archived public-only tests remain in [review_tests/](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/review_tests/DEFERRED.md), and
the earlier implementation is recoverable at SDK commit `8ebc1ea5c9`. The heartbeat
regressions were reactivated with the separate tested review fixes.
The current batch synchronizes Loom's SDK runtime and tests; the earlier
baseline validation did not change that checkout. No service deployment or
package publication is part of this work.
