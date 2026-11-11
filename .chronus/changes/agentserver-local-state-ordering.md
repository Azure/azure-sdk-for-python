---
changeKind: fix
packages:
  - sdk/agentserver/azure-ai-agentserver-core
---

Preserve local state-store creation order for items sharing a timestamp across reopen, updates, expiry, and recreation. Cursor paging now respects filtered-out cursor positions, returns the adjacent page when paging backward, and rejects invalid page sizes or sort orders. Recreated items receive a fresh opaque ID so old cursors do not bind to replacements. Existing local files retain their previous deterministic order and IDs.
