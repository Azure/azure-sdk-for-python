# Release History

## 12.0.0b4 (2020-01-12)
* Fixes an [issue](https://github.com/Azure/azure-sdk-for-python/issues/15554) where `query_entities` kwarg `parameters` would not work with multiple parameters or with non-string parameters. This now works with multiple parameters and numeric, string, boolean, UUID, and datetime objects.
* Fixes an [issue](https://github.com/Azure/azure-sdk-for-python/issues/15653) where `delete_entity` will return an `ClientAuthenticationError` when the '@' symbol is included in the entity.

## 12.0.0b3 (2020-11-12)
* Add support for transactional batching of entity operations.
* Fixed deserialization bug in `list_tables` and `query_tables` where `TableItem.table_name` was an object instead of a string.
* Fixed issue where unrecognized entity data fields were silently ignored. They will now raise a `TypeError`.
* Fixed issue where query filter parameters were being ignored (#15094)

## 12.0.0b2 (2020-10-07)
* Adds support for Enumerable types by converting the Enum to a string before sending to the service

## 12.0.0b1 (2020-09-08)
This is the first beta of the `azure-data-tables` client library. The Azure Tables client library can seamlessly target either Azure Table storage or Azure Cosmos DB table service endpoints with no code changes.



