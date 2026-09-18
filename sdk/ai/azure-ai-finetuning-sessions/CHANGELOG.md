# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial preview of interactive fine-tuning sessions with synchronous and asynchronous clients.
- Forward-only requests, checkpoint resume and deletion, JSON-valued session metadata, and training-tier selection.
- Multimodal image input, vision/projector LoRA settings, nullable prompt log-probabilities, and per-operation metrics.
- Bounded retries, preserved session identifiers, typed service errors, and operation progress logging.

### Breaking Changes

- Public requests use `/fine_tuning_sessions`. The gateway must support the canonical route family.
- Generated operations use the actual HTTP 200 submission and request-status protocol instead of Azure LRO polling.
- Generated create responses expose a string `session_id` and `request_id`; raw request statuses are `pending`, `completed`, and `failed`.
- The generated optimizer operation is `training.optimizer_step`; the convenience `optim_step` API remains available.

### Other Changes

- Regenerated from the public Foundry TypeSpec using pinned tooling and kept custom behavior in handwritten modules.
- Preserved explicit offset-page responses rather than introducing an incomplete generated iterator.
- Imported current SDK regressions and added raw sync/async contract tests.