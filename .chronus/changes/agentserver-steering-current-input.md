---
changeKind: fix
packages:
  - sdk/agentserver/azure-ai-agentserver-core
---

Fixed queued steering turns being skipped by Responses ownership checks by atomically persisting the promoted turn as the current task input before execution. Attachment-backed inputs retain the existing input offload behavior.
