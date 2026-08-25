# Release History

## 1.0.0b3 (2026-08-25)

### Bugs Fixed

- Fixed a bug in the challenge authentication policy where the authentication challenge was cached before the challenge resource was verified. The challenge is now cached only after resource verification succeeds [#48710](https://github.com/Azure/azure-sdk-for-python/pull/48710).

## 1.0.0b2 (2026-08-20)

### Features Added

- Added support for service API version `2025-07-01` [#46782](https://github.com/Azure/azure-sdk-for-python/pull/46782)

### Breaking Changes

- Renamed internal class "Error" to "KeyVaultErrorError" to align with other KeyVault SDKs.

### Bugs Fixed

- Fixed a replay bug in challenge authentication policy. The original request is now stored at the request level instead of the client level [#48636](https://github.com/Azure/azure-sdk-for-python/pull/48636).

### Other Changes

- Key Vault API version `2025-07-01` is now the default

## 1.0.0b1 (2025-05-07)

### Features Added

- Initial version
