# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial preview of interactive fine-tuning sessions with synchronous and asynchronous clients.
- Forward-only requests, checkpoint resume and deletion, JSON-valued session metadata, and training-tier selection.
- Multimodal image input, vision/projector LoRA settings, nullable prompt log-probabilities, and per-operation metrics.
- Bounded retries, preserved session identifiers, typed service errors, and operation progress logging.

### Breaking Changes

- The distribution is named `azure-ai-finetuningsessions` and Python imports now use `azure.ai.finetuningsessions`. Remove older preview installations and update imports/dependency files before installing this build.
- The preview baseline now matches the tested Loom SDK instead of the earlier public-only regenerated surface. Public-only raw models, extra operation methods, keyword adapters, and request-ID poller replacements are not included in this baseline.

### Bugs Fixed

- Drain async heartbeat tasks before session/client shutdown, including concurrent cancellation; share the sync client's pipeline so custom policies work and all transports close normally.
- Bound creation and sustained-error retry sleeps; tolerate bounded request-store propagation after creation and reject unexpected polling states immediately.
- Reject empty training batches and incomplete sampler identifiers; bound synchronous chunk workers and offload async forward chunking.
- Preserve generic handling for explicit non-batch payload limits and typed errors for malformed capacity retry hints; reject unhandled redirects during deletion.
- Propagate direct-route context headers through default raw-operation pipelines with endpoint scoping and caller overrides; omit response payloads from normal INFO logs.
- Preserve the sync heartbeat thread when shutdown has not completed, validate mapping-form image inputs, and return actual completed Tasks from async multichunk/wave methods as documented.
- Includes upstream Loom handling of nested HTTP 503 error details while preserving flat-response compatibility.
- Includes upstream Loom mapping of `engine_dead` polling failures to `TrainingEngineError`, preserving error codes and diagnostic references without retrying lost engine state.

### Other Changes

- Regenerate the preview from pinned TypeSpec inputs and supported Python hooks, preserving the tested public API and behavior of Loom commit `485774df502642879fdf3a53777be4a0d95155dc`. Immutable reference hashes remain in `loom-source.json`; separate generation provenance records the local source inputs.
- Preserved Loom's `/fine_tuning/sessions` routes, generated signatures, models, authentication guards, retry behavior, and convenience APIs. The public-only `use_legacy_routes` option is not part of this snapshot.
- Verified two independent emissions, the complete customized runtime, all upstream tests, public types/signatures/serialization, and raw-operation parity. Authentication, exports, legacy operations, and non-emittable sampling annotations now survive regeneration without editing generated files.
- Preserve the separately committed Loom-equivalent baseline and document each intentional review delta. Security/retry-contract redesigns remain owner decisions; no service deduplication guarantee is implied.