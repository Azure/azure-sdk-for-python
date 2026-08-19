# Release History

## 1.0.0b2 (Unreleased)

### Features Added

- Added support for service API version `2025-07-01` [#46782](https://github.com/Azure/azure-sdk-for-python/pull/46782)

### Breaking Changes

- Renamed internal class "Error" to "KeyVaultErrorError" to align with other KeyVault SDKs.

### Bugs Fixed

- Fixed a replay bug in the challenge authentication policy where a request copy stashed on the shared policy
  instance was never cleared, allowing one request's method, URL, and body to leak into a later, unrelated request
  made by the same client (for example, after an Entra ID Continuous Access Evaluation challenge). The original
  request is now stored per-request instead of on the policy instance. This mirrors the fix already applied to
  `azure-keyvault-secrets` and `azure-keyvault-certificates` in
  [#48537](https://github.com/Azure/azure-sdk-for-python/pull/48537).

### Other Changes

- Key Vault API version `2025-07-01` is now the default

## 1.0.0b1 (2025-05-07)

### Features Added

- Initial version
