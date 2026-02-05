# TASK.md

## Now (active)

## Done

- [x] 2026-02-04 — Implement managed checkpoints feature
  - Files: core/checkpoints/ (new), agentframework/persistence/_foundry_checkpoint_*.py (new),
    agentframework/__init__.py (modified)
  - Added: FoundryCheckpointClient, FoundryCheckpointStorage, FoundryCheckpointRepository
  - Modified: from_agent_framework() with managed_checkpoints, foundry_endpoint, project_id params

- [x] 2026-01-30 — Attach agent server metadata to OpenAIResponse.metadata + header
  - Files: azure-ai-agentserver-core/azure/ai/agentserver/core/application/_metadata.py,
    azure-ai-agentserver-core/azure/ai/agentserver/core/application/__init__.py,
    azure-ai-agentserver-core/azure/ai/agentserver/core/server/_response_metadata.py,
    azure-ai-agentserver-core/azure/ai/agentserver/core/tools/client/_configuration.py,
    azure-ai-agentserver-core/tests/unit_tests/server/test_response_metadata.py
- [x] 2026-01-30 — Restore previous OTel context in streaming generator
  - Files: azure-ai-agentserver-core/azure/ai/agentserver/core/server/base.py,
    azure-ai-agentserver-core/tests/unit_tests/server/test_otel_context.py
- [x] 2026-01-29 — Create `AGENTS.md`, `PLANNING.md`, `TASK.md`.
