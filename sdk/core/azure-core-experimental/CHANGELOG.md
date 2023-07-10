# Release History

## 1.0.0b4 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.0b3 (2023-07-06)

### Bug Fixes

- Update httpx transport to handle timeout and connection verify kwargs from `azure.core.pipeline.transport.HttpRequest`.
- Add a read override for `read` for clients using `azure.core.rest.HttpResponse` to get the response body.

## 1.0.0b2 (2023-04-06)

### Features Added

- httpx implementation of azure-core transport protocol

## 1.0.0b1 (2022-10-06)

Initial release

### Features Added

- pyodide implementation of azure-core transport protocol
