# Release History

## 1.0.0b1 (2026-09-24)

### Features Added

- Add the generated `InputChunk` hierarchy and `InputChunkType`. Existing `ModelInputChunk` keyword/mapping calls remain valid and now emit `type="text"`; image inputs retain their existing serialization and validation.
- Reuse the current 12-member canonical shared `FoundryFeaturesOptInKeys`, preserving six original member names/values with six canonical additions. The fine-tuning preview header is unchanged.
- Add optional `SamplingParams.response_format` for compatible sampling providers and the friendly `SamplingOperationResult` alias for `SampleOperationResult`.
- Include Loom's maintained read-only `SampleOperationResult.prompt_tokens: Optional[int]` for backend-reported evidence, counted once per prompt. Accept only exact non-negative integers; missing or invalid evidence is `None`, with no boolean/float/string coercion or inferred counts. The identical `SamplingOperationResult` alias and existing constructor keywords/overloads are unchanged.
- Support `AZURE_AI_FINETUNING_MAX_CHUNK_BYTES` as an import-time positive-integer override for the approximate request chunk-size budget. Unset or invalid values keep the 5,000,000-byte default; invalid values log a warning. Service-side limits are unchanged.
- Add the string-backed `TrainingType` enum, reusing the REST training-tier definition. Existing string inputs and omission behavior remain supported.
- Initial preview of interactive fine-tuning sessions with synchronous and asynchronous clients.
- Forward-only requests, checkpoint resume and deletion, JSON-valued session metadata, and training-tier selection.
- Multimodal image input, vision/projector LoRA settings, nullable prompt log-probabilities, and per-operation metrics.
- Bounded retries, preserved session identifiers, typed service errors, and operation progress logging.

### Breaking Changes

- Require Python 3.10 or later; Python 3.9 is no longer supported.
- Remove `AGENTS_OPTIMIZATION_V2_PREVIEW` from the historical 13-member enum snapshot to follow its removal from the upstream canonical definition; the six original fine-tuning SDK members remain available.
- Require an explicit `lora_config` with `LoRAConfig.rank` in session creation and checkpoint-resume methods, and in `CreateSessionRequest`. No implicit rank or empty configuration is supplied.
- The distribution is named `azure-ai-finetuningsessions` and Python imports now use `azure.ai.finetuningsessions`. Remove older preview installations and update imports/dependency files before installing this build.
- The preview baseline replaces the earlier regenerated-only surface with the established preview API plus explicitly documented contract changes. Callers of earlier raw models, operation methods, or keyword adapters should check the current signatures when migrating.

### Bugs Fixed

- Preserve credential redirect protections with the declared minimum Azure Core 1.37.0 as well as current versions; handle the cleanup flag location change in Azure Core 1.38.3.
- Drain async heartbeat tasks before session/client shutdown, including concurrent cancellation; share the sync client's pipeline so custom policies work and all transports close normally.
- Bound creation and sustained-error retry sleeps; tolerate bounded request-store propagation after creation and reject unexpected polling states immediately.
- Reject empty training batches and incomplete sampler identifiers; bound synchronous chunk workers and offload async forward chunking.
- Preserve generic handling for explicit non-batch payload limits and typed errors for malformed capacity retry hints; reject unhandled redirects during deletion.
- Propagate direct-route context headers through default raw-operation pipelines with endpoint scoping and caller overrides; omit response payloads from normal INFO logs.
- Preserve the sync heartbeat thread when shutdown has not completed, validate mapping-form image inputs, and return actual completed Tasks from async multichunk/wave methods as documented.
- Handle nested HTTP 503 error details while preserving flat-response compatibility.
- Map `engine_dead` polling failures to `TrainingEngineError`, preserving error codes and diagnostic references without retrying lost engine state.
- Handle non-object error bodies safely, ignore invalid or non-finite retry hints, and validate positional image mappings consistently with keyword inputs.
- Require HTTPS and configured-origin scoping for default API-key authentication, with explicit configured-loopback HTTP opt-in only. Remove SDK-default direct-route headers outside their origin/path scope, including prepopulated defaults, while preserving distinct caller overrides.
- Disable automatic POST transport retries in default sync/async policies, including heartbeats. Explicit retry policies remain caller-owned; this does not guarantee deduplication or change convenience-level recovery decisions.
- Make default raw `begin_*` pollers use HTTP 200 acceptance and session/request-ID GET polling in both clients, without POST replay or synthetic HTTP 202. Preserve result callbacks, custom polling, no-polling, and strategy-specific continuation behavior.

### Other Changes

- Reuse 18 canonical TypeSpec aliases, including `ModelInput`, while retaining 22 compatibility models and three compatibility unions for intentional Python-only contracts. Correct LoRA, sampling, and training-tier documentation without changing service behavior.
- Move Python-only TypeSpec compatibility definitions to [session-finetuning/models-custom-code.tsp](https://github.com/Azure/azure-rest-api-specs/blob/main/specification/ai-foundry/data-plane/Foundry/src/session-finetuning/models-custom-code.tsp), imported only by SDK generation. Retain the existing SDK namespace, public types, and generated type identities; the move does not add these projections to REST.
- Keep the input-chunk migration SDK-first: normalize legacy token-only `ModelInput` mappings only when `type` is absent and preserve unknown explicit tags. Production service behavior is unchanged; strict discriminator enforcement and compatibility policy are deferred to public preview (PuPr).
- Refresh TypeSpec provenance after snake_case training-tier member naming and service-grounded identifier minimum lengths; training-tier wire values are unchanged.
- Use the Foundry required-preview operation contract and documented schema defaults with supported Python customization hooks for request query ordering and established convenience behavior.
- Use the repository's shared Python emitter `0.63.8`, backend `0.38.0`, compiler `1.16.0`, and client generator core `0.72.2`. Genuine regeneration incorporates the upstream unused-import fix; generated files are not manually patched to pass CI.
- Remove the package-local emitter override. Keep standalone tooling archives and validation records under the package's engineering directory, and verification commands under its scripts directory; standard README and generation guidance remain at the package root.
- Record the unchanged 48-file historical oracle at source commit `485774df502642879fdf3a53777be4a0d95155dc` in [eng/generation/reference.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/eng/generation/reference.json). See [GENERATION.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/GENERATION.md) for current guidance, exact reviewed contracts, and historical evidence.
- Retain `/fine_tuning/sessions` routes and established convenience APIs. The earlier `use_legacy_routes` option is not included in this preview.
- Use AST overload inspection on all supported Python versions rather than importing Python 3.11-only `typing.get_overloads`; retain the assertions on Python 3.10.
- Correct the spelling pipeline failure on Python's global-namespace keyword in the surface verifier without changing runtime behavior or weakening validation.
- Preserve the separately committed preview baseline and record intentional changes in [eng/generation/review-deltas.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/eng/generation/review-deltas.json). Background heartbeat startup remains unchanged; opt-in-only startup is still deferred.

The current refresh has two matching isolated emissions and a passing public
source-test run. Final test totals and gate outcomes must come from final
validation records; final Loom, installed-wheel, and public CI results are not
yet verified. No commands or builds were run for this documentation-only update.

Historical local validation, before the input-chunk and shared-enum changes:
**1,637 SDK tests passed on Python 3.13.14**. The
comparison and negative-guard counts, generation method, and limitations are in
[GENERATION.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/GENERATION.md). These results do not validate the final combined changes or claim a new final-wheel run,
validation of the new tests on Python 3.10, remote CI success, or release approval.