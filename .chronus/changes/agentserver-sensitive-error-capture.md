---
changeKind: fix
packages:
  - azure-ai-agentserver-core
  - azure-ai-agentserver-invocations
---

Respect sensitive-data capture settings for SDK exception spans and HTTP
invocation error logs. Preserve explicit observability configuration and
isolate host policies while retaining error status, non-sensitive metadata,
opt-in diagnostics, HTTP error responses, and streaming exception propagation.
