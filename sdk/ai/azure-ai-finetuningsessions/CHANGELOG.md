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

- Includes upstream Loom handling of nested HTTP 503 error details while preserving flat-response compatibility.
- Includes upstream Loom mapping of `engine_dead` polling failures to `TrainingEngineError`, preserving error codes and diagnostic references without retrying lost engine state.

### Other Changes

- Regenerate the preview from pinned TypeSpec inputs and supported Python hooks, preserving the tested public API and behavior of Loom commit `485774df502642879fdf3a53777be4a0d95155dc`. Immutable reference hashes remain in `loom-source.json`; separate generation provenance records the local source inputs.
- Preserved Loom's `/fine_tuning/sessions` routes, generated signatures, models, authentication guards, retry behavior, and convenience APIs. The public-only `use_legacy_routes` option is not part of this snapshot.
- Verified two independent emissions, the complete customized runtime, all upstream tests, public types/signatures/serialization, and raw-operation parity. Authentication, exports, legacy operations, and non-emittable sampling annotations now survive regeneration without editing generated files.
- Deferred the public-only heartbeat shutdown correction and other review changes until after baseline parity. Their tests are preserved separately for follow-up rather than counted as passing baseline tests.