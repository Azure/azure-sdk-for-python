# Release History

## 1.0.0b7 (Unreleased)

### Features Added

- Native tracing support was added. [#39172](https://github.com/Azure/azure-sdk-for-python/pull/39172)
  - The `OpenTelemetryTracer` class was added to the `corehttp.instrumentation.tracing.opentelemetry` module. This is a wrapper around the OpenTelemetry tracer that is used to create spans for SDK operations.
  - Added a `get_tracer` method to the new `corehttp.instrumentation` module. This method returns an instance of the `OpenTelemetryTracer` class if OpenTelemetry is available.
  - A `TracingOptions` TypedDict class was added to define the options that SDK users can use to configure tracing per-operation. These options include the ability to enable or disable tracing and set additional attributes on spans.
    - Example usage: `client.method(tracing_options={"enabled": True, "attributes": {"foo": "bar"}})`
  - `DistributedHttpTracingPolicy` and `distributed_trace`/`distributed_trace_async` decorators were added to support OpenTelemetry tracing for SDK operations.
    - SDK clients can define an `_instrumentation_config` class variable to configure the OpenTelemetry tracer used in method span creation. Possible configuration options are `library_name`, `library_version`, `schema_url`, and `attributes`.
- Added a global settings object, `corehttp.settings`, to the `corehttp` package. This object can be used to set global settings for the `corehttp` package. Currently the only setting is `tracing_enabled` for enabling/disabling tracing. [#39172](https://github.com/Azure/azure-sdk-for-python/pull/39172)

### Breaking Changes

### Bugs Fixed

### Other Changes

- Added `opentelemetry-api` as an optional dependency for tracing. [#39172](https://github.com/Azure/azure-sdk-for-python/pull/39172)

## 1.0.0b6 (2025-03-27)

### Features Added

- The `TokenCredential` and `AsyncTokenCredential` protocols have been updated to include a new `get_token_info` method. This method should be used to acquire tokens and return an `AccessTokenInfo` object. [#38346](https://github.com/Azure/azure-sdk-for-python/pull/38346)
- Added a new `TokenRequestOptions` class, which is a `TypedDict` with optional parameters, that can be used to define options for token requests through the `get_token_info` method. [#38346](https://github.com/Azure/azure-sdk-for-python/pull/38346)
- Added a new `AccessTokenInfo` class, which is returned by `get_token_info` implementations. This class contains the token, its expiration time, and optional additional information like when a token should be refreshed. [#38346](https://github.com/Azure/azure-sdk-for-python/pull/38346)
- `BearerTokenCredentialPolicy` and `AsyncBearerTokenCredentialPolicy` now check if a credential has the `get_token_info` method defined. If so, the `get_token_info` method is used to acquire a token. [#38346](https://github.com/Azure/azure-sdk-for-python/pull/38346)
  - These policies now also check the `refresh_on` attribute when determining if a new token request should be made.
- Added `model` attribute to `HttpResponseError` to allow accessing error attributes based on a known model. [#39636](https://github.com/Azure/azure-sdk-for-python/pull/39636)
- Added `auth_flows` support in `BearerTokenCredentialPolicy`. [#40084](https://github.com/Azure/azure-sdk-for-python/pull/40084)

### Breaking Changes

- The `get_token` method has been removed from the `TokenCredential` and `AsyncTokenCredential` protocols. Implementations should now use the new `get_token_info` method to acquire tokens. [#38346](https://github.com/Azure/azure-sdk-for-python/pull/38346)
- The `AccessToken` class has been removed and replaced with a new `AccessTokenInfo` class. [#38346](https://github.com/Azure/azure-sdk-for-python/pull/38346)
- `BearerTokenCredentialPolicy` and `AsyncBearerTokenCredentialPolicy` now rely on credentials having the `get_token_info` method defined. [#38346](https://github.com/Azure/azure-sdk-for-python/pull/38346)

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
