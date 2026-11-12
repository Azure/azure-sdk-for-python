# Release History

## 1.0.0b2 (2026-11-12)

### Features Added

- Add opt-in text-only sampling with public conversation messages and function tools, plus reference-based training using opaque sample references and scalar advantages.
- Support optional model-specific text-only `reasoning_effort` values `low`, `medium`, and `high`. Omission or `None` preserves the model default.
- Add async `FineTuningSessionClient.attach_session(session_id)` to start a heartbeat for an existing session without creating or loading it.
- Add synchronous and asynchronous local checkpoint downloads. These prepare the export, validate the complete inventory, and stream files into an empty or absent destination with exact ETag and byte-count checks. Failures retain partial output without automatic resume, deletion, or overwrite; model eligibility and authorization remain enforced by the service.

### Breaking Changes

- Remove `FoundryFeaturesOptInKeys.AGENT_INSIGHTS_V1_PREVIEW` because Agent Insights no longer requires the obsolete preview opt-in. Remove explicit references to that constant. The fine-tuning preview header is unchanged.

### Bugs Fixed

- Provide actionable checkpoint-resume guidance for terminal training-engine interruptions while preserving error codes and diagnostic identifiers.
- Preserve out-of-memory and timeout guidance for nonterminal engine errors.
- Retry sampling responses missing `request_id` within a bounded fault budget, then raise `MalformedResponseError`.
- Improve polling budgets, sampling limits, heartbeat shutdown, and scalar serialization while preserving protected-training replay safeguards.
- Use canonical `/fine_tuning_sessions` routes in generated operations while retaining existing Python convenience APIs.

### Other Changes

- Clarify session lifecycle, service-selected training tiers, checkpoint preparation limits, and differences between raw operations and convenience methods.
- Improve generated request-model documentation without changing supported message roles, function-only tools, or request payloads.
- Restore the standard README sections and include public test sources in source distributions while keeping archived review material excluded.
- Synchronize generation metadata with the updated public TypeSpec source without changing the Python API or runtime.

## 1.0.0b1 (2026-09-24)

### Features Added

- Initial preview of interactive fine-tuning sessions with synchronous and asynchronous Python clients.
- Support forward/backward training, forward-only requests, sampling, optimizer steps, checkpoint save/resume, session unload and deletion.
- Support text/image input chunks, vision/projector LoRA configuration, JSON-valued session metadata, and training-tier selection.
- Add optional structured sampling responses, prompt log-probabilities, and read-only prompt-token counts when reported by the service.
- Add `SamplingOperationResult` as an alias for `SampleOperationResult`.
- Support the import-time `AZURE_AI_FINETUNING_MAX_CHUNK_BYTES` override for the approximate request chunk-size budget.

### Breaking Changes

- Require Python 3.10 or later.
- Use distribution name `azure-ai-finetuningsessions` and import namespace `azure.ai.finetuningsessions`. Uninstall the older `azure-ai-finetuning-sessions` distribution before migrating.
- Require explicit LoRA configuration, including `LoRAConfig.rank`, for session creation and checkpoint resume.
- Remove the obsolete `AGENTS_OPTIMIZATION_V2_PREVIEW` feature constant.

### Bugs Fixed

- Scope default credentials and request-context headers to the configured endpoint and preserve credential protections during redirects.
- Disable automatic POST transport retries by default and support HTTP 200 request-ID polling in raw `begin_*` operations.
- Drain async heartbeat tasks during shutdown and bound synchronous heartbeat cleanup.
- Validate empty batches, sampler identifiers, image content, malformed error responses, and retry hints before accepting results or replaying operations.
