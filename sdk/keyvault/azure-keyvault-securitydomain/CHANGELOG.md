# Release History

## 1.0.0b3 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

- Hardened challenge cache reuse as a follow-up to [#48710](https://github.com/Azure/azure-sdk-for-python/pull/48710).
  Cached challenges are now verified before token use, and stale entries are cleared when challenge parsing or resource verification fails.
  Request replay and existing CAE scope/tenant precedence are preserved when concurrent requests invalidate the shared cache.
- Preserved redirect header cleanup and header updates when restoring request bodies during authentication.
- Reject request URLs containing backslashes in the authority before authentication.
- Clear cached challenges when a 401 response omits `WWW-Authenticate`, returning that response without an authentication retry.
  The next request rediscovers the challenge, which can add an unauthenticated request even when resource verification is disabled.

- Fixed a bug in the challenge authentication policy where the authentication challenge was cached before the challenge resource was verified. The challenge is now cached only after resource verification succeeds [#48710](https://github.com/Azure/azure-sdk-for-python/pull/48710).

### Other Changes

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
