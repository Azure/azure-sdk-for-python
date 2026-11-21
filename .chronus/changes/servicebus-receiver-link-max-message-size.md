---
changeKind: internal
packages:
  - azure-servicebus
---

The pyAMQP receiver link now sends a max message size of 0 (no limit) on its attach frame by default, matching the sender link. ([#42814](https://github.com/Azure/azure-sdk-for-python/issues/42814))
