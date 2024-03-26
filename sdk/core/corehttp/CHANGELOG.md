# Release History

## 1.0.0b5 (2024-02-29)

### Other Changes

- Accept float for `retry_after` header.

## 1.0.0b4 (2024-02-23)

### Other Changes

- Relax type checking in `Pipeline` constructors to only check that each user-supplied policy object has either a `send` method or both an `on_request` and `on_response` method. This allows for more flexible policy implementations. [#34296](https://github.com/Azure/azure-sdk-for-python/pull/34296)

## 1.0.0b3 (2024-02-01)

### Features Added

- Support tuple input for `files` values to `corehttp.rest.HttpRequest` #34082
- Support simultaneous `files` and `data` field entry into `corehttp.rest.HttpRequest` #34082

## 1.0.0b2 (2023-11-14)

### Features Added

- Added the initial implementation of the HTTPX transport. [#32813](https://github.com/Azure/azure-sdk-for-python/pull/32813)

### Breaking Changes

- Removed `requests` as a default dependency of `corehttp`. This is now an "extras" dependency and can be installed via `corehttp[requests]`. [#32813](https://github.com/Azure/azure-sdk-for-python/pull/32813)
- Renamed the `aio` extra to `aiohttp`. [#32813](https://github.com/Azure/azure-sdk-for-python/pull/32813)

### Bugs Fixed

- Fixed an issue with `multipart/form-data` in the async transport where `data` was not getting encoded into the request body. [#32473](https://github.com/Azure/azure-sdk-for-python/pull/32473)
- Fixed an issue with `connection_verify`, `connection_cert`, and `connection_timeout` not being propagated to underlying transports.  [#33057](https://github.com/Azure/azure-sdk-for-python/pull/33057)
- Fixed an issue with the `aiohttp` transport not using SSL by default. [#33057](https://github.com/Azure/azure-sdk-for-python/pull/33057)

### Other Changes

- Added extras for `httpx`. [#32813](https://github.com/Azure/azure-sdk-for-python/pull/32813)

## 1.0.0b1 (2023-10-18)

* Initial Release
