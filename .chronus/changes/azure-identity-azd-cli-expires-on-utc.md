---
changeKind: fix
packages:
  - azure-identity
---

Fixed `AzureDeveloperCliCredential` reading the UTC `expiresOn` value from `azd auth token` as local time, which made the token's `expires_on` off by the local UTC offset.
