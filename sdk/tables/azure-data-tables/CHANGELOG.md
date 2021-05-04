# Release History

## 12.0.0b7 (Unreleased)
**Breaking**
* Removed explicit `LinearRetry` and `ExponentialRetry` in favor of keyword parameter.
* Renamed `filter` parameter in query APIs to `query_filter`.
* The `location_mode` attribute on clients is now read-only. This has been added as a keyword parameter to the constructor.
* The `TableItem.table_name` has been renamed to `TableItem.name`.
* Removed the `TableClient.create_batch` method along with the `TableBatchOperations` object. The transactional batching is now supported via a simple Python list of tuples.
* `TableClient.send_batch` has been renamed to `TableClient.submit_transaction`.
* Removed `BatchTransactionResult` object in favor of returning an iterable of batched entities with returned metadata.
* Removed Batching context-manager behavior
* Changed optional `value` and `type` arguments of `EntityProperty` to required.
* Renamed `EntityProperty.type` to `EntityProperty.edm_type`.
* `BatchErrorException` has been renamed to `TableTransactionError`.
* `EntityProperty` is now a tuple.
* Removed `date` and `api_version` from the `TableItem` class.

**Fixes**
* Fixed issue with Cosmos merge operations.
* Removed legacy Storage policies from pipeline.
* Removed unused legacy client-side encryption attributes from client classes.
* Fixed sharing of pipeline between service/table clients.
* Added support for Azurite storage emulator
* Throws a `RequestTooLargeError` on transaction requests that return a 413 error code
* Added support for Int64 and Binary types in query filters

## 12.0.0b6 (2021-04-06)
* Updated deserialization of datetime fields in entities to support preservation of the service format with additional decimal place.
* Passing a string parameter into a query filter will now be escaped to protect against injection.
* Fixed bug in incrementing retries in async retry policy

## 12.0.0b5 (2021-03-09)
* This version and all future versions will require Python 2.7 or Python 3.6+, Python 3.5 is no longer supported.
* Adds SAS credential as an authentication option
* Bumps minimum requirement of `azure-core` to 1.10.0
* Bumped minimum requirement of msrest from `0.6.10` to `0.6.19`.
* Adds support for datetime entities with milliseconds
* Adds support for Shared Access Signature authentication

## 12.0.0b4 (2021-01-12)
* Fixes an [issue](https://github.com/Azure/azure-sdk-for-python/issues/15554) where `query_entities` kwarg `parameters` would not work with multiple parameters or with non-string parameters. This now works with multiple parameters and numeric, string, boolean, UUID, and datetime objects.
* Fixes an [issue](https://github.com/Azure/azure-sdk-for-python/issues/15653) where `delete_entity` will return a `ClientAuthenticationError` when the '@' symbol is included in the entity.

## 12.0.0b3 (2020-11-12)
* Add support for transactional batching of entity operations.
* Fixed deserialization bug in `list_tables` and `query_tables` where `TableItem.table_name` was an object instead of a string.
* Fixed issue where unrecognized entity data fields were silently ignored. They will now raise a `TypeError`.
* Fixed issue where query filter parameters were being ignored (#15094)

## 12.0.0b2 (2020-10-07)
* Adds support for Enumerable types by converting the Enum to a string before sending to the service

## 12.0.0b1 (2020-09-08)
This is the first beta of the `azure-data-tables` client library. The Azure Tables client library can seamlessly target either Azure Table storage or Azure Cosmos DB table service endpoints with no code changes.
