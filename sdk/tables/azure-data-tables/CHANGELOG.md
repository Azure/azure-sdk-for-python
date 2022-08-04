# Release History

## 12.4.1 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed
* Fix handling of client-side exceptions that get raised during service requests (such as [#21416](https://github.com/Azure/azure-sdk-for-python/issues/21416)) ([#24788](https://github.com/Azure/azure-sdk-for-python/pull/24788))

### Other Changes
* Bumped dependency on `azure-core` to `>=1.23.0`

## 12.4.0 (2022-05-10)

### Features Added
* Support for multitenant authentication ([#24278](https://github.com/Azure/azure-sdk-for-python/pull/24278))

### Bugs Fixed
* Fixed bug where odmtype tag was not being included for boolean and int32 types even when a full EdmProperty tuple was passed in. This is needed for CLI compatibility.

## 12.3.0 (2022-03-10)

### Bugs Fixed
* Validation of the table name has been removed from the constructor of the TableClient. Instead individual APIs will validate the table name and raise a ValueError only if the service rejects the request due to the table name not being valid (#23106)
* Fixed hard-coded URL scheme in batch requests (#21953)
* Improved documentation for query formatting in `query_entities` APIs (#23235)
* Removed unsecure debug logging

### Other Changes
* Python 2.7 is no longer supported. Please use Python version 3.6 or later.
* Bumped dependency on `azure-core` to `>=1.15.0`

## 12.2.0 (2021-11-10)
**Warning** This release involves a bug fix that may change the behaviour for some users. Partition and Row keys that contain a single quote character (`'`) will now be automatically escaped for upsert, update and delete entity operations. Partition and Row keys that were already escaped, or contained duplicate single quote char (`''`) will now be treated as unescaped values.


### Bugs Fixed
* Resolved bug where strings couldn't be used instead of enum value for entity Update Mode (#20247).
* Resolved bug where single quote characters in Partition and Row keys were not escaped correctly (#20301).

### Features Added
* Added support for async iterators in `aio.TableClient.submit_transaction (#21083, thank you yashbhutoria).

### Other Changes
* Bumped dependency on `msrest` to `>=0.6.21`

## 12.1.0 (2021-07-06)

### Features Added
* Storage Accounts only: `TableClient` and `TableServiceClient`s can now use `azure-identity` credentials for authentication. Note: A `TableClient` authenticated with a `TokenCredential` cannot use the `get_table_access_policy` or `set_table_access_policy` methods.

## 12.0.0 (2021-06-08)
**Breaking**
* EdmType.Binary data in entities will now be deserialized as `bytes` in Python 3 and `str` in Python 2, rather than an `EdmProperty` instance. Likewise on serialization, `bytes` in Python 3 and `str` in Python 2 will be interpreted as binary (this is unchanged for Python 3, but breaking for Python 2, where `str` was previously serialized as EdmType.String)
* `TableClient.create_table` now returns an instance of `TableItem`.
* All optional parameters for model constructors are now keyword-only.
* Storage service configuration models have now been prefixed with `Table`, including
  `TableAccessPolicy`, `TableMetrics`, `TableRetentionPolicy`, `TableCorsRule`
* All parameters for `TableServiceClient.set_service_properties` are now keyword-only.
* The `credential` parameter for all Clients is now keyword-only.
* The method `TableClient.get_access_policy` will now return `None` where previously it returned an "empty" access policy object.
* Timestamp properties on `TableAccessPolicy` instances returned from `TableClient.get_access_policy` will now be deserialized to `datetime` instances.

**Fixes**
* Fixed support for Cosmos emulator endpoint, via URL/credential or connection string.
* Fixed table name from URL parsing in `TableClient.from_table_url` classmethod.
* The `account_name` attribute on clients will now be pulled from an `AzureNamedKeyCredential` if used.
* Any additional odata metadata is returned in entity's metadata.
* The timestamp in entity metadata is now deserialized to a timestamp.
* If the `prefer` header is added in the `create_entity` operation, the echo will be returned.
* Errors raised on a 412 if-not-match error will now be a specific `azure.core.exceptions.ResourceModifiedError`.
* `EdmType.DOUBLE` values are now explicitly typed in the request payload.
* Fixed de/serialization of list attributes on `TableCorsRule`.

## 12.0.0b7 (2021-05-11)
**Breaking**
* The `account_url` parameter in the client constructors has been renamed to `endpoint`.
* The `TableEntity` object now acts exclusively like a dictionary, and no longer supports key access via attributes.
* Metadata of an entity is now accessed via `TableEntity.metadata` attribute rather than a method.
* Removed explicit `LinearRetry` and `ExponentialRetry` in favor of keyword parameter.
* Renamed `filter` parameter in query APIs to `query_filter`.
* The `location_mode` attribute on clients is now read-only. This has been added as a keyword parameter to the constructor.
* The `TableItem.table_name` has been renamed to `TableItem.name`.
* Removed the `TableClient.create_batch` method along with the `TableBatchOperations` object. The transactional batching is now supported via a simple Python list of tuples.
* `TableClient.send_batch` has been renamed to `TableClient.submit_transaction`.
* Removed `BatchTransactionResult` object in favor of returning an iterable of batched entities with returned metadata.
* Removed Batching context-manager behavior
* `EntityProperty` is now a NampedTuple, and can be represented by a tuple of `(entity, EdmType)`.
* Renamed `EntityProperty.type` to `EntityProperty.edm_type`.
* `BatchErrorException` has been renamed to `TableTransactionError`.
* The `location_mode` is no longer a public attribute on the Clients.
* The only supported credentials are `AzureNamedKeyCredential`, `AzureSasCredential`, or authentication by connection string
* Removed `date` and `api_version` from the `TableItem` class.

**Fixes**
* Fixed issue with Cosmos merge operations.
* Removed legacy Storage policies from pipeline.
* Removed unused legacy client-side encryption attributes from client classes.
* Fixed sharing of pipeline between service/table clients.
* Added support for Azurite storage emulator
* Throws a `RequestTooLargeError` on transaction requests that return a 413 error code
* Added support for Int64 and Binary types in query filters
* Added support for `select` keyword parameter to `TableClient.get_entity()`.
* On `update_entity` and `delete_entity` if no `etag` is supplied via kwargs, the `etag` in the entity will be used if it is in the entity.

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
