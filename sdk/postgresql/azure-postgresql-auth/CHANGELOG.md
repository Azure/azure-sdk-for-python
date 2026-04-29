# Release History

## 1.0.2 (2026-04-28)

### Bugs Fixed

- Removed dependency on `DefaultAzureCredential` in source library
- Fixed `get_entra_conninfo_async` and `get_entra_token_async` closing the credential by using it as a context manager

### Other Changes

- Bumped minimum dependency on `azure-core` to `>=1.31.0`

## 1.0.1 (2025-11-26)

### Other Changes

- Update author to Microsoft

## 1.0.0 (2025-11-14)

### Features Added

- Initial public release
