# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial preview of interactive fine-tuning sessions with synchronous and asynchronous clients.
- Forward-only requests, checkpoint resume and deletion, JSON-valued session metadata, and training-tier selection.
- Multimodal image input, vision/projector LoRA settings, nullable prompt log-probabilities, and per-operation metrics.
- Bounded retries, preserved session identifiers, typed service errors, and operation progress logging.

### Breaking Changes

- The distribution is named `azure-ai-finetuningsessions` and Python imports now use `azure.ai.finetuningsessions`. Remove older preview installations and update imports/dependency files before installing this build.
- Public requests use `/fine_tuning_sessions` by default. Existing Loom endpoints can be selected explicitly with `use_legacy_routes=True`; there is no automatic route fallback.
- Generated operations use the actual HTTP 200 submission and request-status protocol instead of Azure LRO polling.
- Generated create responses expose a string `session_id` and `request_id`; raw request statuses are `pending`, `completed`, and `failed`.
- The generated optimizer operation is `training.optimizer_step`; the convenience `optim_step` API remains available.

### Other Changes

- Regenerated from the public Foundry TypeSpec using pinned tooling and kept custom behavior in handwritten modules.
- Preserved explicit offset-page responses rather than introducing an incomplete generated iterator.
- Imported current SDK regressions and added raw sync/async contract tests.
- Preserved legacy `body`, `operation_id`, and per-call `api_version` keywords through handwritten adapters without changing shared client configuration.
- Restored `ApiError` and `ApiErrorResponse` exports through TypeSpec and preserved omitted-LoRA request serialization and the convenience heartbeat's `v1` default.
- Added legacy `begin_*` pollers over the actual HTTP 200/request-ID protocol, with no automatic resubmission, custom polling strategy, continuation token, or streaming support.
- Added an offline side-by-side Loom comparison of convenience behavior, selected generated reads, public exports, request payloads, and typed errors.