---
changeKind: fix
packages:
  - azure-identity
---

Fixed an issue where `SharedTokenCacheCredential` could return a cached access token issued for a different tenant than the one requested via the `tenant_id` keyword argument, when the cache held tokens for the same account across multiple tenants.
