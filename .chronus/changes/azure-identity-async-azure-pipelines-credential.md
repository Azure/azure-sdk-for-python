---
changeKind: fix
packages:
  - sdk/identity/azure-identity
---

Fixed asynchronous `AzurePipelinesCredential` blocking the event loop during OIDC-token requests and using synchronous transport lifecycle methods. The asynchronous `ClientAssertionCredential` now supports awaitable assertion callbacks while remaining compatible with callbacks that return strings.
