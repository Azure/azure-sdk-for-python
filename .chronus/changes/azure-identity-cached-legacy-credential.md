---
changeKind: fix
packages:
  - azure-identity
---

Fixed an issue where `DefaultAzureCredential.get_token_info` raised an `AttributeError` when a previously successful credential only implemented `get_token`. This affects both synchronous and asynchronous credentials.
