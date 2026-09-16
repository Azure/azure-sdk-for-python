---
changeKind: fix
packages:
  - azure-ai-agentserver-core
---

Prevented local `FoundryStateStore` transactions from overwriting concurrent changes made by cooperating processes using the same state root.
