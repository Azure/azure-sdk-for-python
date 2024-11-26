# Release History

## 1.0.0b10 (2024-11-05)

### Other Changes

- This package has been deprecated and will no longer be maintained after 11-05-2024. Use the [azure-core-tracing-opentelemetry](https://pypi.org/project/azure-core-tracing-opentelemetry/) package for tracing support in Azure SDK libraries.

## 1.0.0b9 (2023-05-09)

### Bugs Fixed

- Fixed a bug where starting a span would fail if an unexpected keyword argument was passed in to `OpenCensusSpan`.

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.7 or later.

## 1.0.0b8 (2021-07-01)

- Fix for supporting `kind` keyword while instantiating the span.

## 1.0.0b7 (2021-04-08)

- `Link` and `SpanKind` can now be added while creating the span instance.

## 1.0.0b6 (2020-05-04)

- `link` and `link_from_headers` now accept attributes.

## 1.0.0b5 (2020-01-14)

### Bugfix

- Fix context passing for multi-threading
- Don't fail on unknown span type, but maps to PRODUCER or UNSPECIFIED

### Features

- Implement new "change_context" API

## 1.0.0b4 (2019-10-07)

### Features

- Opencensus implementation of azure-core tracing protocol
