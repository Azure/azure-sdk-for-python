# Release History

## 1.3.0b2 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.3.0b1 (2024-11-05)

### Features Added

- Added broker on macOS support.

## 1.2.0 (2024-10-08)

### Other Changes

- Stable release for the Proof-of-Possession (PoP) token support to `InteractiveBrowserBrokerCredential`.

## 1.2.0b1 (2024-09-20)

### Features Added

- `InteractiveBrowserBrokerCredential` now implements the `SupportsTokenInfo` protocol. It now has a `get_token_info` method which returns an `AccessTokenInfo` object. The `get_token_info` method is an alternative method to `get_token` that improves support for more complex authentication scenarios.
- Added Proof-of-Possession (PoP) token support to `InteractiveBrowserBrokerCredential`.

## 1.1.0 (2024-04-09)

### Features Added

- `InteractiveBrowserBrokerCredential` now supports a `use_default_broker_account` property to enable the use of the currently logged in operating system account for authentication rather than prompting for a credential.
- Added `enable_support_logging` as a keyword argument to `InteractiveBrowserBrokerCredential`. This allows additional support logging which may contain PII.

### Other Changes

- Python 3.7 is no longer supported. Please use Python version 3.8 or later.
- Bumped minimum dependency on `azure-identity` to `1.15.0`.

## 1.0.0 (2023-11-07)

### Features Added

- `enable_broker` is always on if running on Windows. Automatically fall back into non-broker mode if running on MacOS or Linux.

### Breaking Changes

- Removed `UsernamePasswordBrokerCredential`

## 1.0.0b1 (2023-10-12)

### Features Added

- Added `azure.identity.broker.InteractiveBrowserBrokerCredential`
  and `azure.identity.broker.UsernamePasswordBrokerCredential` which have broker support.
