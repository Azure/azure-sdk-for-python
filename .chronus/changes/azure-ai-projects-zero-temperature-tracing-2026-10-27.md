---
changeKind: fix
packages:
  - sdk/ai/azure-ai-projects
---

Fixed agent creation tracing to record the `gen_ai.request.temperature` and `gen_ai.request.top_p` span attributes when their value is `0`.
