## 12.0.0b3 (Unreleased)


## 12.0.0b2 (2020-9-10)
**Breaking changes**
- Change the `continuation_token` from a dict to a str.
- `start_time`/`end_time` and `continuation_token` are mutually exclusive now.

## 12.0.0b1 (2020-07-07)
- Initial Release. Please see the README for information on the new design.
- Support for ChangeFeedClient: get change feed events by page, get all change feed events, get events in a time range

This package's
[documentation](https://aka.ms/azsdk-python-storage-blob-changefeed-ref)
and
[samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob-changefeed/samples)
