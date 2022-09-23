# Release History

## 1.0.0b9 (Unreleased)

### Features Added

### Breaking Changes

### Key Bugs Fixed

### Fixed

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

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
