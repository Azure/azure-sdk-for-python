---
changeKind: fix
packages:
  - sdk/agentserver/azure-ai-agentserver-responses
---

Include `tools` and `tool_choice` in response snapshots for strict OpenAI SDK validation, preserving explicit request and recovery-seed configuration.
