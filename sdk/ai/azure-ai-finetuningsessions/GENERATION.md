# Reproducible preview SDK generation

## Reviewed fixes after the parity baseline

The independently reproducible exact public-API parity baseline is SDK commit
`39c2b3c882526897619785089074176b367099a6`, pinned to TypeSpec
`d912f0d0bc6af9e87e0c0833922dd85fa32abf97`. Subsequent review fixes are listed in
[review-deltas.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/review-deltas.json) and [REVIEW.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/REVIEW.md); the baseline
results below remain historical evidence, not a claim of zero behavior changes.

Current tests preserve all upstream cases, adapt two private heartbeat mocks to
the now-awaitable helper, and add lifecycle/protocol/header regressions. The
compatibility verifier checks those exact test hashes. Its only fixture changes
are explicitly expected direct-context headers on raw calls, widened
credential annotations for already-supported API keys, and multimodal input
annotations matching the already-supported image chunks; all other API, payload,
serialization, raw operation and convenience results remain exact.

Heartbeat shutdown is now awaited, default sync pipeline ownership is unified,
and creation/error waits are bounded. The security policy for remote API-key HTTP,
non-idempotent submission retry contract, and opt-in heartbeat redesign are
deliberately deferred for the reasons recorded in the review assessment.

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
public implementation preserves its customer API and behavior through supported
hooks; internal files and implementation locations are not byte-identical.

[loom-source.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/loom-source.json) remains the original 48-file reference
manifest, not a claim that current runtime hashes equal Loom. It covers 29
reference runtime files including Azure namespace parents, and 19 upstream test
files. [generation-provenance.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/generation-provenance.json) separately records
the local TypeSpec fingerprint, emitter pins, and actual generated runtime.

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
| [_client_options.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/azure/ai/finetuningsessions/_client_options.py) | API key/token selection, loopback-only HTTP policy, moniker, preserved private configuration imports |
| [_operation_compat.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/azure/ai/finetuningsessions/_operation_compat.py) | Legacy raw error/stream/result/continuation behavior using generated builders; one legacy sampling request builder |
| Exception/logging modules | Tested upstream implementation, changed only by emitter formatting |

The original training function bodies and exception/logging behavior were
AST-compared with Loom. Only client construction/export binding and supported
integration changed. The public-only awaited heartbeat shutdown fix is **not**
included: cancel-only shutdown remains until the subsequent review stage.

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

[emitter-package.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/emitter-package.json) and
[emitter-package-lock.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/emitter-package-lock.json) pin the isolated JavaScript
toolchain, including Python emitter `0.61.3`, `http-client-python` `0.28.3`,
TypeSpec compiler `1.11.0`, and TCGC `0.67.3`.
[generator-requirements.txt](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/generator-requirements.txt) records the Python backend
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

- [verify_generation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/verify_generation.py): emits twice from independent
  source snapshots with only maintained customizations pre-seeded; compares all
  **21 generated inventory entries** and the complete runtime. Missing, orphan,
  changed, or unstable files fail. It never updates the package.
- [verify_loom_snapshot.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/verify_loom_snapshot.py): verifies all immutable
  upstream Git blobs and exact name-normalized reference hashes. `--snapshot`
  optionally verifies an archived byte-identical reference, not this regenerated
  implementation.
- [verify_loom_compatibility.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/verify_loom_compatibility.py): verifies the exact
  19 upstream test files, materializes the immutable reference, runs the original
  **20 paired cases / 134 requests / 2,246 checks per SDK**, then invokes the
  complete public-surface/raw-operation check. No API additions are allowed.
- [verify_loom_surface.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/verify_loom_surface.py): isolated comparison of all
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

## Pinned source and next review stage

[tsp-location.yaml](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/tsp-location.yaml) pins public TypeSpec commit
`d912f0d0bc6af9e87e0c0833922dd85fa32abf97`, which contains the validated model
projection and client mappings. The source fingerprint is recorded separately
in [generation-provenance.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/generation-provenance.json). The preview-parity
baseline is committed separately from subsequent review fixes so it remains
independently reproducible.

Archived public-only tests remain in [review_tests/](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/review_tests/DEFERRED.md), and
the earlier implementation is recoverable at SDK commit `8ebc1ea5c9`. The heartbeat
regressions were reactivated with the separate tested review fixes.
No Loom checkout/index changes, deployment, or publication are part of this work.
