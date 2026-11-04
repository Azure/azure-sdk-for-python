---
changeKind: fix
packages:
  - sdk/agentserver/azure-ai-agentserver-core
---

Fixed steering acknowledgment leaks and duplicate turn dispatch when queue or
turn-state persistence fails.
