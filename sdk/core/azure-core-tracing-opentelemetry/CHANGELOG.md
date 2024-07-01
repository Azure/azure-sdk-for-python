# Release History

## 1.0.0b12 (Unreleased)

### Features Added

- If a span exits with an exception, the exception name is now recorded in the `error.type` attribute. ([#34619](https://github.com/Azure/azure-sdk-for-python/pull/34619))

### Breaking Changes

- Remapped certain attributes to converge with OpenTelemetry semantic conventions version `1.23.1` ([#34089](https://github.com/Azure/azure-sdk-for-python/pull/34089)):
    - `http.method` -> `http.request.method`
    - `http.status_code` -> `http.response.status_code`
    - `net.peer.name` -> `server.address`
    - `net.peer.port` -> `server.port`
    - `http.url` -> `url.full`

### Bugs Fixed

### Other Changes

## 1.0.0b11 (2023-09-07)

### Bugs Fixed

- Fixed `OpenTelemetrySpan` typing to correctly implement the `AbstractSpan` protocol. ([#31943](https://github.com/Azure/azure-sdk-for-python/pull/31943))

## 1.0.0b10 (2023-07-11)

### Features Added

- Enabled the use of the `context` keyword argument for passing in context headers of a parent span. This will be the parent context used when creating the span. ([#30411](https://github.com/Azure/azure-sdk-for-python/pull/30411))

### Breaking Changes

- Remapped certain attributes to converge with OpenTelemetry semantic conventions ([#29203](https://github.com/Azure/azure-sdk-for-python/pull/29203)):
    - `x-ms-client-request-id` -> `az.client_request_id`,
    - `x-ms-request-id` -> `az.service_request_id`,
    - `http.user_agent` -> `user_agent.original`,
    - `message_bus.destination` -> `messaging.destination.name`,
    - `peer.address` -> `net.peer.name`,

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.7 or later.
- Nested internal spans are now suppressed with just the outermost internal span being recorded. Nested client spans will be children of the outermost span. ([#29616](https://github.com/Azure/azure-sdk-for-python/pull/29616))
- When client spans are created, a flag is set to indicate that automatic HTTP instrumentation should be suppressed. Since azure-core already instruments HTTP calls, this prevents duplicate spans from being produced. ([#29616](https://github.com/Azure/azure-sdk-for-python/pull/29616))
- Schema URL is now set on the tracer's instrumentation scope. ([#30014](https://github.com/Azure/azure-sdk-for-python/pull/30014))
- Minimum `opentelemetry-api` dependency bumped to `1.12.0`.
- Minimum `azure-core` dependency bumped to `1.24.0`.

## 1.0.0b9 (2021-04-06)

- Updated opentelemetry-api to version 1.0.0
- `Link` and `SpanKind` can now be added while creating the span instance.

## 1.0.0b8 (2021-02-08)

- Pinned opentelemetry-api to version 0.17b0

## 1.0.0b7 (2020-10-05)

- Pinned opentelemetry-api to version 0.13b0

## 1.0.0b6 (2020-07-06)

- Pinned opentelemetry-api to version 0.10b0

## 1.0.0b5 (2020-06-08)

- Pinned opentelemetry-api to version 0.8b0
- Fixed a bug where `DefaultSpan` sometimes throws an AttributeError.

## 1.0.0b4 (2020-05-04)

- `link` and `link_from_headers` now accepts attributes.

## 1.0.0b3 (2020-04-06)

### Features

- Pinned opentelemetry-api to version 0.6b0

## 1.0.0b2 (2020-03-09)

### Features

- Pinned opentelemetry-api to version 0.4a0

## 1.0.0b1

### Features

- Opentelemetry implementation of azure-core tracing protocol
