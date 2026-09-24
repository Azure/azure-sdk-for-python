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

- Regenerate from the reviewed Foundry required-preview operation contract and updated schema defaults; preserve the existing Python API and request query ordering through supported customization hooks. Synchronize the Loom SDK runtime and reviewed regressions with this package.
- Regenerate the preview from pinned TypeSpec inputs and supported Python hooks, preserving the tested public API and behavior of Loom commit `485774df502642879fdf3a53777be4a0d95155dc`. Immutable reference hashes remain in `loom-source.json`; separate generation provenance records the local source inputs.
- Preserved Loom's `/fine_tuning/sessions` routes, generated signatures, models, authentication guards, retry behavior, and convenience APIs. The public-only `use_legacy_routes` option is not part of this snapshot.
- At the historical SDK parity baseline `39c2b3c882526897619785089074176b367099a6`, pinned to TypeSpec `d912f0d0bc6af9e87e0c0833922dd85fa32abf97`, verified two independent emissions, the complete customized runtime, all 434 upstream tests, public types/signatures/serialization, and raw-operation parity. Authentication, exports, legacy operations, and non-emittable sampling annotations survive regeneration without editing generated files; this is not final validation of later CI repairs.
- Preserve the separately committed Loom-equivalent baseline and document each intentional review delta. Security/retry-contract redesigns remain owner decisions; no service deduplication guarantee is implied.

#### CI repair snapshot (2026-09-22; local only)

- Repair the Python 3.10 overload-inspection failure from SDK baseline CI build `6867846` by using AST inspection on all Python versions instead of importing `typing.get_overloads`. Local tests: Python 3.10, 500 passed and 1 Python 3.12+ eager-task skip; Python 3.13, 501 passed.
- Pass local Pylint 4.0.4 with Azure checker 0.5.7 after helper documentation and dictionary-literal fixes, with explicit line/function exceptions for preview compatibility and existing state-machine complexity. This is not an exception-free pass or a full refactoring of all findings.
- Pass strict Sphinx 8.2 against the actual sdist with the repository override's five namespace RST pages and all verification scripts retained; only offline intersphinx downloads were disabled. The MCP README check passed; the last root CSpell run covered 84 files with 0 issues.
- Pass compiler 1.16 warnings-as-errors checks for REST and Python entry points. Only three expected error-field descriptions change in REST output; Python/wire types and HTTP/schema/protocol behavior remain unchanged. Exact-node compatibility exceptions still need human review, and 14 C#-only naming mappings still require other-language CI validation.
- Enable packaging generation for clean MCP output while maintained-SDK generation overrides `generate-packaging-files=false`. Actual MCP generation passed and a separate pinned emission matches all 21 generated inventory entries, including the model documentation-only update.
- Final formatter, repeated generation/provenance, source pointer, and repair commit/push work remain pending in the parent validation task; remote CI has not run these changes. The PyPI name still needs the approved reservation pipeline, REST documentation-preview infrastructure is blocked, and 64 review replies remain local after EMU HTTP 403. Detailed exceptions and limitations are recorded in [GENERATION.md](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/GENERATION.md) and [REVIEW.md](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/REVIEW.md).