# Release History

## 1.0.0b2 (Unreleased)

### Features Added

### Breaking Changes
  - Removed support for max_concurrency

### Bugs Fixed

### Other Changes
  - Removed `msrest` dependency.
  - Added requirement for `isodate>=0.6.0` (`isodate` was required by `msrest`)

## 1.0.0b1 (2022-07-15)

  ## Features
  - Version (1.0.0b1) is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Monitor Ingestion.
    For more information about this, and preview releases of other Azure SDK libraries, please visit https://azure.github.io/azure-sdk/releases/latest/python.html.
  - Added `~azure.monitor.ingestion.LogsIngestionClient` to send logs to Azure Monitor along with `~azure.monitor.ingestion.aio.LogsIngestionClient`.
