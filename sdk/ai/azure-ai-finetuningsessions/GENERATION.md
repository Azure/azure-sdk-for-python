# Reproducible preview SDK generation

## Current source pin and review validation

Use [tsp-location.yaml](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/tsp-location.yaml) for the TypeSpec repository, entry point,
additional source directories, and exact commit. Use
[eng/generation/provenance.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/eng/generation/provenance.json) for source,
toolchain, generated-output, and complete-runtime fingerprints. Historical SHAs
below are decision records, **not the current source pin**.

The combined SDK-first changes are pinned to committed TypeSpec source
`ace87c52c336cad1f6b777a0c23095d292982aa8`. Source, shared-toolchain,
generated-output, and complete-runtime fingerprints pass their checks. Two
independent emissions match the checked-in SDK. For subsequent source changes,
update these records together and repeat the strict generation check; do not
reuse earlier results when their inputs differ.

## Current SDK-first decisions

### Input-chunk contract

The canonical REST model owns the discriminator hierarchy; Python-scoped naming
and usage retain the established text/image names rather than copying models.

| Canonical REST definition | Python name | Current contract |
|---|---|---|
| `FineTuningInputChunk` | `InputChunk` | Base model with `@discriminator("type")`. |
| `FineTuningInputChunkType` | `InputChunkType` | Open union of `text`, `image`, and `string`; unknown explicit chunk tags remain extensible. |
| `FineTuningInputChunkText` | `ModelInputChunk` | Extends the base. Existing `ModelInputChunk(tokens=...)` and mapping calls remain valid; text now emits `type="text"`. |
| `FineTuningInputChunkImage` | `ImageChunk` | Extends the base. The maintained Python `ImageChunk` extends the generated image class and preserves the existing public calls and validation. |
| `FineTuningModelInput` | `ModelInput` | Reused directly, with `chunks: FineTuningInputChunk[]`, not an SDK-local model copy. The maintained hook adds the text tag to legacy token-only mappings only when `type` is absent; unknown explicit tags are left unchanged. |

Image bytes/base64 handling, the 10,000,000-byte limit, matching JPEG/PNG/WebP
signatures and formats, positive `expected_tokens`, and the 64-image limit per
example are preserved. Mapping inputs do not bypass these checks.

This is **SDK-first**, not a service parser migration. Tests use the actual
checked-out `loom_api.schemas`, compare tagged/untagged text model dumps and
domain conversion, and exercise direct handlers with an in-memory provider.
Both text forms are accepted; internal text remains `encoded_text`. These are
local offline checks, not live-deployment or GPU validation. Production parser,
API/authentication, routes, engine, APIM, and resource-provider behavior are
untouched. Strict discriminator enforcement is deferred to public preview
(PuPr); the compatibility policy for older clients must be decided then. SDK
extensibility is not a promise that the service accepts arbitrary future tags.

### Canonical reuse and intentional Python projections

The Python-only compatibility file now contains **18 aliases, 22 compatibility
models, and three compatibility unions**, compared with the earlier 17/23/4
snapshot. Canonical `ModelInput` reuse removes one local model. The duplicate
`FoundryFeaturesOptInKeys` union and its alternate mapping are removed; Python
name/usage customizations reuse the canonical closed union from the shared
Foundry service patterns. That underlying REST union is unchanged.

`FoundryFeaturesOptInKeys` retains all six existing names and values:
`EVALUATIONS_V1_PREVIEW`, `SCHEDULES_V1_PREVIEW`, `RED_TEAMS_V1_PREVIEW`,
`INSIGHTS_V1_PREVIEW`, `MEMORY_STORES_V1_PREVIEW`, and
`FINETUNING_SESSIONS_V1_PREVIEW`. It adds the seven canonical members
`AGENT_INSIGHTS_V1_PREVIEW`, `ROUTINES_V2_PREVIEW`, `SKILLS_V1_PREVIEW`,
`DATA_GENERATION_JOBS_V1_PREVIEW`, `MODELS_V1_PREVIEW`,
`AGENTS_OPTIMIZATION_V2_PREVIEW`, and `MODEL_ROUTER_CONTROLS_V1_PREVIEW`.
The fine-tuning preview header is unchanged; exposing these names does not opt
requests into other features.

The remaining definitions are intentional Python-only projections:

| Retained group | Why it is not replaced by the REST shape |
|---|---|
| `AdamParams`, `SamplingParams`, `SampleRequest`, `LossFnInputs` | Required Python constructor arguments differ from optional service defaults or derived inputs. |
| `LoRAConfig`, `CreateSessionRequest` | Configuration/rank remain required, but optional LoRA service defaults must not materialize client-side. Preserve SDK `ejectable` and maintained `FromCheckpoint` integration. |
| Response models, including checkpoints, session summaries, sampling, and heartbeat | Preserve field inventories, optionality, nullability, read-only metadata, and constructor requirements; these are not all wire-equivalent to REST. |
| `ForwardInput` | Preserve public inheritance from `ForwardBackwardInput`, while REST uses composition. |
| `OperationResult`, its derived results, `OperationStatus`, `OperationType` | Preserve legacy Python result classes and poller return types, not a claim that the service returns them instead of its request-status envelope. |
| `ApiError`, `ApiErrorResponse`, `SessionStatus` | Preserve existing error representation and exported status members; the open status union can represent `created` without adding a named member. |

These projections belong only in the Python entry point, not in REST. Source
reuse, Python API compatibility, and service wire conformance remain separate
checks. The two TypeSpec review comments are code-addressed, but no replies are
posted or threads resolved by this follow-up; see [REVIEW.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/REVIEW.md#typespec-follow-up-decisions).

### Generation evidence and limits

Discriminator generation preceded the shared-enum follow-up. Genuine generation
uses the SDK repository's shared emitter **0.63.8** and backend **0.37.3**.
The enum follow-up changes only the generated enum, API source metadata, and
sync/async operation docstrings. Operation executable ASTs are identical after
excluding docstrings, and all **28 runtime files** equal the genuine emitted
output. This does not claim that the earlier discriminator generation changed
only those files.

The combined discriminator and canonical-feature changes have the following
local validation results (2026-09-25), obtained before this documentation-only
record update:

| Check | Result |
|---|---|
| Public SDK source and installed wheel | **1,850 passed** on Python 3.13.14; all 28 wheel runtime files match source bytes. |
| Public SDK minimum Python | **1,849 passed, one expected eager-task test skipped** on Python 3.10.21. |
| Downstream Loom SDK | **1,869 source and 1,869 installed-wheel tests passed**; its extra master regressions are retained and all 28 runtime files match the public SDK. |
| Strict compatibility | **20 paired cases**, 134 requests and 2,246 checks per SDK; **49 public types**, all **336 original raw cases**, **328 additional probes**, and **97 mutation guards** pass. |
| SDK-to-service compatibility | **162 offline checks passed**, including 20 real SDK pipeline cases against unchanged checked-out API schemas and handlers. |
| Generation and quality | Two independent emissions match all 21 generated entries and 28 runtime files; Pylint, Mypy, Pyright, formatting, and strict Sphinx checks passed. |
| Spelling | **94 files checked, zero issues** before this final documentation update. |

These results do not certify a live deployment, GPU execution, remote CI, or
release approval. Remote CI for the delivery commits is a separate follow-up.

### Historical local validation (2026-09-24)

These results predate the current input-chunk and shared-enum changes and were
not rerun for this documentation update.

| Check | Recorded result |
|---|---|
| SDK tests | **1,637 passed on Python 3.13.14**; **1,636 passed and one Python-3.12-only eager-task test skipped on Python 3.10.21**. |
| Genuine generation | Only nine maintained hooks seeded before emission; two independent emissions match all 21 generated inventory entries and the complete 28-file runtime. |
| Convenience comparison | 20 cases, 134 requests, and 2,246 checks **per SDK**, with fixed reviewed contracts. |
| Public surface and raw operations | 47 exported model/enum names, including the identical sampling alias; all 336 original raw cases retained. The candidate adds exactly 28 polling GETs (308 reference requests, 336 candidate requests). |
| Additional service/security probes | 328 passed. |
| Review-contract guard suite | 38 passed using [scripts/check_review_contracts.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/scripts/check_review_contracts.py) with captured comparison artifacts. |
| Distribution | Source distribution and wheel built successfully; all 28 distributed runtime files match source bytes; the installed wheel passed all 1,637 tests. |
| Code quality | CI-pinned Pylint and Mypy passed; repository-configured Pyright passed. Strict Sphinx passed using sdist runtime/pages and the final README, with only external inventory downloads disabled locally. |

These are local offline results, not live GPU/service validation, remote SDK CI
success, other-language certification, or release approval. At that snapshot,
the main verifier's exact test-inventory and provenance gates also passed
against the then-finalized records, not the later combined changes above.

## Pinned generation tools

Generation uses the SDK repository's central
[../../../eng/emitter-package.json](https://github.com/Azure/azure-sdk-for-python/blob/main/eng/emitter-package.json) and
[../../../eng/emitter-package-lock.json](https://github.com/Azure/azure-sdk-for-python/blob/main/eng/emitter-package-lock.json).
The package-local emitter override has been removed. The validated shared lock
resolves Python emitter **0.63.8**, Python backend **0.37.3**, TypeSpec compiler
**1.16.0**, and TypeSpec client generator core (TCGC) **0.72.1**. Genuine
regeneration incorporates the upstream unused-import fix; generated imports
are not manually edited or exempted from CI checks.

[eng/generation/emitter-package.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/eng/generation/emitter-package.json) and
[eng/generation/emitter-package-lock.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/eng/generation/emitter-package-lock.json)
archive the shared pair for standalone verification, not an active per-package
toolchain. [eng/generation/requirements.txt](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/eng/generation/requirements.txt)
records the Python backend requirements; these belong in the emitter environment,
not the SDK runtime. The verifier resolves exact versions from the lock, rejects
mismatched installations, and checks both shared and archived input hashes.

## Source pipeline

1. The Python-specific TypeSpec entry point selects the existing shared Foundry
   service and REST operations. Python-scoped naming/location decorators retain
   the separate package, client, flat operation groups, and per-call API version.
2. Canonical type references and explicit compatibility models preserve reviewed
   Python constructors, exports, inheritance, and result types without inventing
   another REST service, route set, or HTTP success contract.
3. Seed **only** the five maintained patch modules and four helper modules below
   into clean output **before** emission. The official emitter preserves/formats
   these inputs and generates every other runtime file.
4. For the maintained package, use `generate-packaging-files=false` to preserve
   reviewed packaging. Clean standalone generation can generate packaging.
5. Compare two independent emissions with the checked-in generated inventory
   **and all 28 runtime files**, including hooks. Only CRLF-to-LF normalization
   is allowed for checkout comparisons. Missing, extra, changed, or unstable
   output fails; wheel byte-fidelity checks, when run, compare raw bytes.

Do not seed generated clients/models/operations, copy a finished SDK over an
emission, or rewrite generated output to manufacture a match. Model reuse,
SDK-to-SDK compatibility, and service conformance are separate checks.

### Maintained integration

| Maintained input | Responsibility |
|---|---|
| [azure/ai/finetuningsessions/_patch.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/azure/ai/finetuningsessions/_patch.py), [azure/ai/finetuningsessions/aio/_patch.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/azure/ai/finetuningsessions/aio/_patch.py) | Training conveniences, request-ID polling, chunking, recovery, identifiers, lifecycle, and exports. |
| [azure/ai/finetuningsessions/models/_patch.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/azure/ai/finetuningsessions/models/_patch.py) | Image/checkpoint helpers and reviewed model constructors, annotations, and aliases. |
| [azure/ai/finetuningsessions/operations/_patch.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/azure/ai/finetuningsessions/operations/_patch.py), [azure/ai/finetuningsessions/aio/operations/_patch.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/azure/ai/finetuningsessions/aio/operations/_patch.py) | Established raw signatures/overloads, JSON submission, and poller integration. |
| [azure/ai/finetuningsessions/_client_options.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/azure/ai/finetuningsessions/_client_options.py) | Credential transport/origin rules, scoped context headers, default POST-retry policy, and constructor compatibility. |
| [azure/ai/finetuningsessions/_operation_compat.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/azure/ai/finetuningsessions/_operation_compat.py) | Generated request builders, raw HTTP 200 request-ID polling, callbacks, custom polling/continuation, and the legacy sampling request shape. |
| [azure/ai/finetuningsessions/_exceptions.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/azure/ai/finetuningsessions/_exceptions.py), [azure/ai/finetuningsessions/_logging_setup.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/azure/ai/finetuningsessions/_logging_setup.py) | Typed errors, validated retry hints, and logging. |

### Verification commands

Run from the package root with the required Python/Node dependencies already
installed. Supply the TypeSpec checkout and an installation of the exact shared
manifest/lock. `--sdk-repo` selects the authoritative SDK checkout; it is normally
discovered automatically. Without `--toolchain`, the verifier uses dependencies
beside the selected manifest. Outside an SDK checkout, it uses the archived pair.

```text
python scripts/verify_generation.py --spec-repo <spec-repo> --sdk-repo <sdk-repo> --toolchain <shared-toolchain>
python scripts/verify_reference_snapshot.py --loom-repo <reference-repo>
python scripts/verify_compatibility.py --loom-repo <reference-repo> --artifacts <artifacts-dir>
python scripts/check_review_contracts.py --artifacts <artifacts-dir>
```

[scripts/verify_generation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/scripts/verify_generation.py) checks provenance
before emitting and never updates the package or installs tooling.
[scripts/verify_reference_snapshot.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/scripts/verify_reference_snapshot.py)
verifies the immutable Git blobs and manifest; `--snapshot` is only for an
archived exact reference, not the regenerated SDK.
[scripts/verify_compatibility.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/scripts/verify_compatibility.py) validates exact
test inventories/hashes, materializes the unchanged reference, captures both
convenience reports, and invokes [scripts/verify_surface.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/scripts/verify_surface.py)
for surface/raw-operation reports and service/security probes. Pass the same
artifact directory to the guard suite; it checks that unauthorized contract,
reference, candidate, and probe mutations are rejected, not runtime behavior.

## Customer artifact and compatibility target

The distribution is `azure-ai-finetuningsessions` version `1.0.0b1`, importing
`azure.ai.finetuningsessions`. Standard customer and generation guidance remain
at the package root; executable verifiers and engineering records are separated
into their directories above.

[eng/generation/reference.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/eng/generation/reference.json) preserves the
unchanged **48-file oracle** from source commit
`485774df502642879fdf3a53777be4a0d95155dc`: 29 reference runtime files (including
shared Azure namespace parents) and 19 upstream test files. Only the agreed
package/import rename and checkout newline normalization apply to that reference.
Its hashes are not claims that the current generated SDK is byte-identical.

The independently reproducible parity baseline is SDK commit
`39c2b3c882526897619785089074176b367099a6`, using TypeSpec
`d912f0d0bc6af9e87e0c0833922dd85fa32abf97`. Later intentional contracts are
recorded separately; never edit the oracle or learn expectations from candidate
output to make a comparison pass.

## Reviewed fixes after the parity baseline

[eng/generation/review-deltas.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/eng/generation/review-deltas.json) records
fixed, guarded contracts, exact test adaptations, and additions. The allowed
contracts are specific, not a general API or behavior allowlist:

| Contract | Permitted change |
|---|---|
| Existing review contracts | Scoped direct-context headers; key/token credential annotations; annotations for already-supported image inputs. |
| Training tier | One `TrainingType` export, exactly three existing wire values, and four specified annotation sites; strings and omission remain supported. |
| Required LoRA | Require `LoRAConfig.rank`, `CreateSessionRequest.lora_config`, and `lora_config` in `FineTuningSession.create`, `FineTuningSession.create_from_checkpoint`, `aio.FineTuningSessionClient.create_session`, and `aio.FineTuningSessionClient.create_session_from_checkpoint`. No inferred rank or configuration default. |
| Sampling format | Only optional `SamplingParams.response_format: Optional[Dict[str, Any]]`, default `None`; no unrelated field/default changes. |
| Sampling result alias | `SamplingOperationResult` is identical to `SampleOperationResult`; the old name remains exported. |
| Credential/direct-header security | Default API keys require the configured HTTPS origin, except explicit configured-loopback HTTP opt-in. SDK-default direct headers, including prepopulated defaults, are removed outside origin/path scope; distinct caller overrides remain. |
| Transport retries | Default sync/async policies never retry POST, including heartbeats. An explicit `retry_policy` is caller-owned; ordinary GET retry settings are retained. |
| Raw polling | Sync/async default `begin_*` use real HTTP 200 acceptance and session/request-ID GET polling, preserving `OperationResult`/`cls`. All 336 original raw cases remain; only the fixed contract observations and 28 additional polling GETs differ. |

Additional reviewed fixes cover non-object error JSON, finite/non-negative retry
hints, positional image mappings, bounded waits/chunk workers, payload-safe INFO
logging, and heartbeat shutdown ordering. See [REVIEW.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/REVIEW.md) for decisions.
Active tests retain upstream coverage with exact reviewed changes, not a blanket
claim that all active test files remain byte-identical to the oracle.

### Raw operations, security boundaries, and lifecycle

- Raw `sessions.create` returns submission JSON and does not poll or start a
  heartbeat. Default `sessions.begin_create` returns a sync/async poller;
  completion requires its result. Convenience create methods wait for
  initialization and then start the existing background heartbeat.
- Default raw pollers disable transport retries and redirects on POST and GET,
  surface errors without resubmitting, and resume their bound request locator
  with GET only. Custom polling, `NoPolling`/`AsyncNoPolling`, and their
  continuation behavior remain strategy-owned; no synthetic HTTP 202 is used.
- Raw signatures retain `body`, `operation_id`, and explicit `api_version`.
  Raw `operations.get` retains `OperationResult`. The legacy raw sampling
  signature still lacks a required checkpoint query argument; the REST contract
  requires it. Prefer convenience sampling with a completed sampler checkpoint.
- Custom policy lists/prebuilt pipelines remain caller-owned. Default transport
  protections do not certify arbitrary authentication policies or caller headers.
  Ordinary redirect handling and convenience-level recovery decisions remain
  unchanged; no deduplication or exactly-once service guarantee is implied.
- Automatic background-heartbeat startup is unchanged. Opt-in-only startup is
  still deferred, unlike the implemented security, POST-retry, and raw-polling fixes.

All routes remain `/fine_tuning/sessions`, with API version `v1` and
`Foundry-Features: FineTuningSessions=V1Preview`. Existing checkpoint URI schemes,
environment-variable names, and the `finetuning-sessions/1.0.0b1` user-agent
moniker are compatibility contracts, not terminology to rename in documentation.

## Historical decisions and evidence

The sections below preserve technical rationale and snapshot results. Their
commits, old tool versions, test totals, wheel results, and CI observations are
historical only; current guidance and limitations are above.

## Model reuse and training-tier review (2026-09-24)

Historical source snapshot: `22a790dd840b0898c800bd8a6014d1814ea52938`.
The three decisions were separately committed. The 17-alias/23-model/four-union
counts and decisions to retain `ModelInput` and `FoundryFeaturesOptInKeys` below
describe that snapshot; they are **superseded for current source** by the
SDK-first decisions above, not retroactively changed historical results.

| Review concern | Resolution | TypeSpec commit |
|---|---|---|
| Duplicated contracts | Replace 17 copied definitions with references to the authoritative REST types. Retain only explicitly explained preview compatibility shapes and correct copied documentation. | `382a34146c1` |
| String-only training tier | Generate Python `TrainingType` from the existing `FineTuningTrainingType` union, using Python-scoped naming. The SDK create model spreads the canonical `training_type` property rather than redeclaring its type, optionality, or documentation. | `154731972ec` |
| Legacy DeveloperTier description | Recommend explicit tier selection; otherwise leave selection to the service. Remove the legacy metadata mechanism from the public property description without falsely promising an unconditional default. | `22a790dd840` |

### One service contract, explicit compatibility exceptions

The REST entrypoint remains authoritative for HTTP routes, request/response
shapes, validation, and service defaults. The Python-only entrypoint imports
that contract; it never defines another service or another set of routes.
Aliases are references to the same TypeSpec type graph, not independent copies.
Python `clientName` and `usage` customizations preserve existing public names
and exports without changing REST or other-language naming.

The shared `Azure.AI.Projects` service and its `SessionFineTuning` namespace do
not make this package part of `azure.ai.projects`: Python namespace mappings
select the independent distribution. The existing public compatibility
namespace is retained for source compatibility, not used as customer branding.
Renaming it would be a separate source migration, not a prerequisite for reuse.

At that snapshot, the following 17 SDK definitions reused canonical types directly:
`CheckpointType`, `LossFn`, `SessionType`, `StopCriteria`, `TensorData`,
`ModelInputChunk`, `Cursor`, `LossFnConfig`, `Datum`, `ForwardBackwardInput`,
`ForwardBackwardRequest`, `ForwardRequest`, `OptimStepRequest`, `Session`,
`SessionList`, `CheckpointList`, and `SaveCheckpointRequest`. Their nested
types still use a compatibility mapping where that nested type differs.
`TrainingType` additionally reuses the existing service union rather than
introducing another list of training-tier values.

At that snapshot, the compatibility file was retained, reduced from 36 to 23
model declarations and from eight to four union declarations (the original
count includes `StopCriteria`). The retained groups had these reasons:

| Retained definitions | Compatibility requirement / service distinction |
|---|---|
| `AdamParams`, `SamplingParams`, `SampleRequest`, `LossFnInputs` | Existing Python constructors require fields the service can default or derive. Preserve constructor signatures and emitted values rather than silently changing defaults. |
| `LoRAConfig`, `CreateSessionRequest` | Retain preview fields such as `ejectable` and the maintained `FromCheckpoint` integration. The later required-LoRA contract now requires configuration/rank with no default; the original omission behavior is historical, not current guidance. |
| `Checkpoint`, `CheckpointInfo`, `SessionModelData`, `SessionSummary`, `SampledSequence`, `HeartbeatResponse` | Preserve existing field inventories, optional/nullable Python representations, and required heartbeat constructor arguments. REST exposes additional checkpoint metadata and may omit the heartbeat identifier; these differences are not erased or asserted to be wire-equivalent. |
| `ModelInput` | Then retained the generated token-only base used by the multimodal hook. **Superseded:** current source reuses canonical `ModelInput` and its generated chunk hierarchy, with maintained compatibility/validation hooks. |
| `ForwardInput` | Preserve its public inheritance from `ForwardBackwardInput`; the REST model uses composition. |
| `OperationResult` and its five derived results, `OperationStatus`, `OperationType` | Preserve public result classes, enums, and poller return types. The later raw-polling fix uses HTTP 200 request-ID envelopes without deleting these classes or caller-owned polling behavior. |
| `ApiError`, `ApiErrorResponse` | Preserve existing Python error names, recursive detail representation, optionality, and encoded additional/debug information. |
| `SessionStatus` | Preserve the previously exported named members. REST also names `created`; the Python union remains open and can represent that string without adding an unrelated enum member in this review. |
| `FoundryFeaturesOptInKeys` | Then retained the older enum inventory and open-string projection. **Superseded:** current source reuses the shared closed union, retaining the six old names/values and adding seven canonical members without changing REST. |

Deleting all remaining Python-only projections would change constructor signatures,
inheritance, public exports, or legacy results. That is a separate migration,
not a safe response to the duplication comment. Future reuse must preserve
existing calls or identify an explicit reviewed API change. Source reuse is
checked by generation; compatibility with the old SDK and conformance to the
service are distinct checks, not interchangeable claims.

The copied statements that rank is fixed server-side and can safely be omitted
were corrected. The sampling model now documents the service's actual
`topk_prompt_logprobs` default of zero, while retaining the old required Python
constructor argument. Legacy result documentation no longer advertises a
nonexistent operation-status route. None of these documentation corrections
changes constructor defaults or server behavior.

### Training tier: additive enum, unchanged wire behavior

The new enum has exactly `GLOBAL_STANDARD = "GlobalStandard"`,
`DATAZONE_STANDARD = "DatazoneStandard"`, and `DEVELOPER_TIER = "DeveloperTier"`.
Existing strings and unknown future strings still serialize unchanged. The
create model and sync/async creation helpers accept an optional string or enum;
omission stays omitted and does not inject a client-side default.

The service's legacy metadata fallback is deliberately not removed. Explicit
`training_type` takes precedence; omission leaves selection to the service,
including its existing compatibility behavior. Removing that backend fallback
would need a separate service migration.

### Historical validation scope

The reuse-only comparison had zero differences across 45 public types and 336
raw cases; executable AST excluding docstrings was unchanged. The separate
training-tier description edit changed only that text in four REST documents.
The enum snapshot passed 543 tests (501 existing plus 42 new), and actual
generation plus two independent emissions matched 21 generated entries and the
28-file runtime. At that stage, `training-type-enum` was the only new comparison
contract. Later required-LoRA, sampling, and security/polling changes are separate
contracts, not retroactive claims about that snapshot.

References: [TypeSpec aliases](https://typespec.io/docs/language-basics/alias/),
[model reuse](https://typespec.io/docs/language-basics/models/), and
[Python-scoped client customizations](https://azure.github.io/typespec-azure/docs/libraries/typespec-client-generator-core/reference/decorators/).

## Training-tier names and string constraints (2026-09-23)

The source pin for this earlier review was TypeSpec commit
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

That snapshot left all 21 generated entries and 28 runtime files unchanged from
SDK `96b410cbdb8567b1aae76677566ea300236613bf`. Two emissions and the then-current
501-test suites passed; wheels were not rebuilt for this unchanged-runtime review.

References: [named union variants](https://typespec.io/docs/language-basics/unions/#named-unions)
and [string minimum lengths](https://typespec.io/docs/standard-library/built-in-decorators/#@minLength).

## Foundry review batch (2026-09-23)

Historical source snapshot: `68b7f96fdabbeb966213596cc92ddfec207e52cc`.
The shared Foundry service and independent Python package were retained.
Related comments 3/4 and 6/8 share a commit.

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

At that snapshot, actual generation and two independent emissions matched the
21 generated entries and 28-file runtime. The maintained request hook preserved
API-version query ordering without rewriting builders or relaxing comparisons.
Both SDK copies then passed 501 tests; 17 lightweight cookbook checks passed,
excluding the heavyweight import test. These are historical local results.

## Operation coverage documentation (2026-09-23)

TypeSpec commit `ff3fe7d6edc892aed8079760ba41a7289f64eab1` expands only line
comments explaining the intentional exclusion of raw generated session deletion
and forward-only operations. The package README documents the existing sync
and async convenience entry points, including chunking, request-ID polling,
heartbeat shutdown, and deletion response handling. These maintained hooks are
included during regeneration; both REST operations remain defined.

This was comment-only, with no generated/runtime or comparison change. Adding
raw operation-group methods would be a separate additive API change.

## Shared Foundry feature opt-in review (2026-09-23)

Historical commit `b3d1b8bcfaddba25fc07188672a4a4d5c80cc501` removed the bare
`string` from `FoundryFeaturesOptInKeys`, retaining all 13 named keys. Its
declaration-scoped `no-closed-literal-union` suppression follows a specific
review decision, not a general exemption for input-only unions. The Python
compatibility projection remained unchanged **at that snapshot**; retaining it
is superseded by the current canonical reuse described above. Four REST outputs were
byte-identical; two emissions and 501 tests passed. Other shared client entry
points compiled, but their language packages were not regenerated or certified.

The separate earlier agent-definition review removed unrestricted `string`
from `AgentDefinitionOptInKeys` only, preserving names/version annotations and
changing only that schema's extensibility in four REST documents. Neither
historical opt-in review changed this SDK's runtime at those snapshots.

References: [TypeSpec suppression directives](https://typespec.io/docs/language-basics/directives/)
and [the extensible-union rule](https://azure.github.io/typespec-azure/docs/libraries/azure-core/rules/no-closed-literal-union/).

## Route-deduplication refactor (2026-09-23)

The public TypeSpec client customization was changed to reuse canonical service
operations instead of declaring routed SDK interfaces and operation aliases.
Python-scoped `@clientName` and `@clientLocation` retain the
root client and five flat groups. `@scope("!python")` excludes only the same two
raw operations omitted before: session deletion and forward-only training. The
handwritten convenience methods remain unchanged. Model mappings, required
per-call API version, method names, and legacy polling/pagination decorators
remain in the Python customization file. The operation-template migration is
separate from this historical refactor.

Baseline TypeSpec commit: `a170cb1188d5fc706a6433a0c95a13caf30c72fe`.
Baseline SDK commit: `df4b722725386974c26463fb375ba7e27f6511fb`.
The baseline and two independent candidates use the same pinned generator and
the same nine maintained hooks. All generated Python and the complete runtime
are unchanged, as are all four full REST OpenAPI outputs. The sole emitted
metadata delta is 26 APIView operation identifiers (13 methods in sync/async)
changing from alias identities to canonical service identities; package/model
identifiers and the customer API are unchanged.

Both source packages and the then-current installed wheel passed 501 tests and
the existing comparison. This is historical wheel evidence, not a test of the
current artifact. The refactor was committed at
`05c7c9af0f866ed349f9d7e0870eb7d2d849d1de`; no test or comparison exception changed.

## CI repair validation (2026-09-22)

This section records the **2026-09-22 snapshot only**:

- CI build `6867846` exposed Python 3.10's missing `typing.get_overloads`.
  AST inspection retained the assertions on all versions. That snapshot passed
  500 tests with one Python 3.12+ eager-task skip on Python 3.10, and 501 on 3.13.
- Local Pylint 4.0.4/Azure checker 0.5.7 passed with narrow documented exceptions
  for preview signatures, private hook integration, class aliases, actual Task
  return types, long names, and complex state machines; not an exception-free pass.
- Strict Sphinx 8.2 passed against that sdist using five namespace pages, with
  only offline intersphinx downloads disabled. README checks and an 84-file
  spelling check passed then, not a certification of later edits.
- Compiler 1.16 warnings-as-errors validation and canonical formatting passed.
  The REST delta was exactly three error-field descriptions. A standard-RPC
  trial was rejected for new path warnings; exact-node operation, legacy, and
  inheritance exceptions retained their compatibility rationale and human review.
  Fourteen C#-only `Content`/`Result` mappings did not certify other-language SDKs.
- Actual generation succeeded through maintained Python hooks. The earlier
  automatic customizer's `ManualInterventionRequired` result was not generation
  success; supported subclasses, `__all__`, and `patch_sdk()` supplied integration.

Historical infrastructure/reservation failures and review replies not posted are
described in [REVIEW.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/REVIEW.md). They are not current CI status assertions.

## Baseline acceptance checks (before review fixes)

The historical baseline used emitter `0.61.3`, backend `0.28.3`, compiler
`1.11.0`, and TCGC `0.67.3`; these are **not current generation instructions**.
It passed two emissions, 434 upstream tests on source and an installed wheel,
20 paired convenience cases, 45 exported types (38 models and seven enums),
76 model construction/serialization cases, and 336 raw cases. Its wheel held
27 namespace Python modules plus the typing marker, with exact source bytes
and no shared Azure initializers or tests. Four REST outputs were unchanged;
the recorded 29 REST/99 Python warnings belong to that old toolchain snapshot.

Archived superseded tests and their exclusion from active totals are explained
in [review_tests/DEFERRED.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/review_tests/DEFERRED.md). Historical exact parity
does not erase later reviewed fixes or establish current wheel/CI readiness.
