# Release History

## 1.0.0b2 (Unreleased)

### Features Added

- Added HTTPX transport initial implementation. [#32813](https://github.com/Azure/azure-sdk-for-python/pull/32813)

### Breaking Changes

- Removed `requests` as a default dependency of `corehttp`. This is now an "extras" dependency and can be installed via `corehttp[requests]`. [#32813](https://github.com/Azure/azure-sdk-for-python/pull/32813)

### Bugs Fixed

- Fixed an issue with `multipart/form-data` in the async transport where `data` was not getting encoded into the request body. [#32473](https://github.com/Azure/azure-sdk-for-python/pull/32473)

### Other Changes

- Added extras for `requests`, `aiohttp`, and `httpx`. [#32813](https://github.com/Azure/azure-sdk-for-python/pull/32813)

## 1.0.0b1 (2023-10-18)

* Initial Release
