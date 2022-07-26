## Release History

## 12.0.0b5 (Unreleased)

This version and all future versions will require Python 3.7+. Python 3.6 is no longer supported.

### Features Added

### Bugs Fixed

### 12.0.0b4 (2022-06-15)

This version and all future versions will require Python 3.6+. Python 2.7 is no longer supported.

#### Features Added
- Added support for `max_single_get_size` and `max_chunk_get_size` to `ChangeFeedClient` to enable control over the initial size and chunk size when downloading ChangeFeed blobs.

### 12.0.0b3 (2021-11-17)
**Fixes**
- `pip install` now supports latest blob version

### 12.0.0b2 (2020-9-10)
**Breaking changes**
- Change the `continuation_token` from a dict to a str.
- `start_time`/`end_time` and `continuation_token` are mutually exclusive now.

### 12.0.0b1 (2020-07-07)
- Initial Release. Please see the README for information on the new design.
- Support for ChangeFeedClient: get change feed events by page, get all change feed events, get events in a time range

This package's
[documentation](https://aka.ms/azsdk-python-storage-blob-changefeed-ref)
and
[samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-blob-changefeed/samples)
