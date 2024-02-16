# Release History

## 1.1.0 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

- Python 3.7 is no longer supported. Please use Python version 3.8 or later.

## 1.0.0 (2023-11-07)

### Features Added

- `enable_broker` is always on if running on Windows. Automatically fall back into non-broker mode if running on MacOS or Linux.

### Breaking Changes

- Removed `UsernamePasswordBrokerCredential`

## 1.0.0b1 (2023-10-12)

### Features Added

- Added `azure.identity.broker.InteractiveBrowserBrokerCredential`
  and `azure.identity.broker.UsernamePasswordBrokerCredential` which have broker support.
