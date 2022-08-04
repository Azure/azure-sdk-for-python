# Release History

## 12.14.0b1 (Unreleased)

This version and all future versions will require Python 3.7+. Python 3.6 is no longer supported.

### Features Added
- Added support for `AzureNamedKeyCredential` as a valid `credential` type.

### Bugs Fixed
- Removed dead retry meachism from async `azure.storage.blob.aio.StorageStreamDownloader`.
- Updated exception catching of `azure.storage.blob.StorageStreamDownloader`'s retry mechanism.
- Adjusted type hints for `upload_blob` and `StorageStreamDownloader.readall`.

## 12.13.0 (2022-07-07)

### Bugs Fixed
- Stable release of features from 12.13.0b1.
- Added support for deleting versions in `delete_blobs` by supplying `version_id`.

## 12.13.0b1 (2022-06-15)

### Features Added
- Added support for service version 2021-08-06.
- Added a new version of client-side encryption for blobs (version 2.0) which utilizes AES-GCM-256 encryption.
If you are currently using client-side encryption, it is **highly recommended** to switch to a form of server-side
encryption (Customer-Provided Key, Encryption Scope, etc.) or version 2.0 of client-side encryption. The encryption
version can be specified on any client constructor via the `encryption_version` keyword (`encryption_version='2.0'`).

## 12.12.0 (2022-05-09)

### Features Added
- Stable release of features from 12.12.0b1.
- Added support for progress tracking to `upload_blob()` and `download_blob()` via a new optional callback,`progress_hook`.

### Bugs Fixed
- Fixed a bug in `BlobClient.from_blob_url()` such that users will receive a more helpful error
message if they pass an incorrect URL without a full `/container/blob` path.
- Fixed a bug, introduced in the previous beta release, that caused Authentication errors when attempting to use
an Account SAS with certain service level operations.

## 12.12.0b1 (2022-04-14)

### Features Added
- Added support for service version 2021-06-08.
- Added a new paginated method for listing page ranges, `list_page_ranges()`. This replaces `get_page_ranges()` which has been deprecated.
- Added support for copying source blob tags with `start_copy_from_url()` by specifying `"COPY"` for the `tags` keyword.

## 12.11.0 (2022-03-29)

**Warning** This release involves a bug fix that may change the behavior for some users. In previous versions,
the `tag` parameter on`BlobSasPermissions` defaulted to `True` meaning a Blob SAS URL would include the `t` permission
by default. This was not the intended behavior. This release adjusts `BlobSasPermission` so the `tag` permission will
default to `False`, like all other permissions.

### Bugs Fixed
- Fixed a bug in `BlobSasPermissions` where the `tag` permission had a default value of `True` and
therefore was being added to the SAS token by default.

## 12.10.0 (2022-03-08)

This version and all future versions will require Python 3.6+. Python 2.7 is no longer supported.

### Stable release of preview features
- Added support for service version 2021-02-12, 2021-04-10.
- Account level SAS tokens now supports two new permissions:
    - `permanent_delete`
    - `set_immutability_policy`
- Encryption Scope is now supported for Sync Blob Copy (`copy_from_url()`).
- Encryption Scope is now supported as a SAS permission.
- Added support for blob names containing invalid XML characters. 
  Previously \uFFFE and \uFFFF would fail if present in blob name.
- Added support for listing system containers with get_blob_containers().
- Added support for `find_blobs_by_tags()` on a container.
- Added support for `Find (f)` container SAS permission.

### Bugs Fixed
- Added all missing Service SAS permissions.
- Fixed a bug that prevented `upload_blob()` from working with an OS pipe
reader stream on Linux. (#23131)

## 12.10.0b4 (2022-02-24)

### Features Added
- Updated clients to support both SAS and OAuth together.
- Updated OAuth implementation to use the AAD scope returned in a Bearer challenge.

### Bugs Fixed
- Addressed a few `mypy` typing hint errors.

## 12.10.0b3 (2022-02-08)

This version and all future versions will require Python 3.6+. Python 2.7 is no longer supported.

### Features Added
- Added support for service version 2021-04-10.
- Added support for `find_blobs_by_tags()` on a container.
- Added support for `Find (f)` container SAS permission.

### Bugs Fixed
- Update `azure-core` dependency to avoid inconsistent dependencies from being installed.

## 12.10.0b2 (2021-12-13)

### Features Added
- Added support for service version 2021-02-12
- Added support for blob names container invalid XML characters. Previously \uFFFE and \uFFFF would fail if present in blob name.
- Added support for listing system containers with get_blob_containers().

### Bugs Fixed
- BlobPrefix for aio operations is now exposed to be imported, previously it was private.

## 12.10.0b1 (2021-11-08)
**New Features**
- Account level SAS tokens now support two new permissions:
    - `permanent_delete`
- Encryption Scope is now supported for Sync Blob Copy (`copy_from_url()`)
- Encryption Scope is now supported as a SAS permission

**Fixes**
- Blob Client Typing annotation issues have been resolved, specifically `invalid type inference` issues (#19906)
- Duplicate type signature issue has been resolved (#19739) 

## 12.9.0 (2021-09-15)
**Stable release of preview features**
- Added support for service version 2020-10-02 (STG78)
- Added support for object level immutability policy with versioning (Version Level WORM).
- Added support for listing deleted root blobs that have versions.
- Added OAuth support for sync copy blob source.

## 12.9.0b1 (2021-07-27)
**New Features**
- Added support for object level immutability policy with versioning (Version Level WORM).
- Added support for listing deleted root blobs that have versions.
- Added OAuth support for sync copy blob source.

**Fixes**
- Fixed a bug for get_block_list (#16314)
- Ensured that download fails if blob modified mid download
- Enabled exists() for CPK encrypted blobs (#18041)

**Notes**
- Deprecated new_name in for undelete container operation

## 12.8.1 (2021-04-20)
**Fixes**
- Fixed retry on large block upload
- Make `AccountName`, `AccountKey` etc. in conn_str case insensitive
- Fixed downloader.chunks() return chunks in different size (#9419, #15648)
- Enabled `exists()` for CPK encrypted blobs (#18041)
- Fixed the ability to upload from a generator (#17418)
- Fixed unclosed `ThreadPoolExecutor` (#8955)
- Fixed retries for blob download streams (#18164, #17974, #10572 (comment))
- Added chunk streaming docstrings and samples (#17149, #11009)
- Added retry for blob download (#17974, #10572)
- Fixed encryption algorithm hardcoded setting (#17835)

## 12.8.0 (2021-03-01)
**Stable release of preview features**
- Added `ContainerClient.exists()` method
- Added container SAS support for blob batch operations

**Fixes**
- Fixed `delete_blob()` method signature (#15891)
- Fixed Content-MD5 throwing when passed (#15919)

## 12.8.0b1 (2021-02-10)
**New Features**
- Added `ContainerClient.exists()` method
- Added container SAS support for blob batch operations

## 12.7.1 (2021-01-20)
**Fixes**
- Fixed msrest dependency issue (#16250)

## 12.7.0 (2021-01-13)
**Stable release of preview features**
- Added `upload_blob_from_url` api on `BlobClient`.
- Added support for leasing blob when get/set tags, listing all tags when find blobs by tags.
- Added support for `AzureSasCredential` to allow SAS rotation in long living clients.

**Fixes**
- Fixed url parsing for blob emulator/localhost (#15882)

## 12.7.0b1 (2020-12-07)
**New features**
- Added `upload_blob_from_url` api on `BlobClient`
- Added support for leasing blob when get/set tags, listing all tags when find blobs by tags.


## 12.6.0 (2020-11-10)
**Stable release of preview features**
- Preview feature `ArrowDialect` as output format of `query_blob`
- Preview feature `undelete_container` on BlobServiceClient.
- Preview feature Last Access Time.

**Fixes**
- Fixed the expired Authorization token problem during retry (#14701, #14067)
- Catch exceptions thrown by async download (#14319)

**Notes**
- Updated dependency `azure-core` from  azure-core<2.0.0,>=1.6.0 to azure-core<2.0.0,>=1.9.0 to get continuation_token attr on AzureError.

## 12.6.0b1 (2020-10-02)
**New features**
- Added support for Arrow format (`ArrowType`) output serialization using `quick_query()`.
- Added support for undeleting a container.
- Added support for `LastAccessTime` property on a blob, which could be the last time a blob was written or read.


## 12.5.0 (2020-09-10)
**New features**
- Added support for checking if a blob exists using the `exists` method (#13221).

**Fixes**
- Fixed source URLs special characters issue. Users can now have special characters in their source URLs for `copy_blob_from_url`, `upload_blob_from_url` etc (#13275).
- Fixed authorization header on asyncio requests containing url-encoded-able characters (#11028).
- Fixed SAS credentials URL malformation when using local Azurite container (#11941).
- Fixed issue with permission string causing an authentication failure (#13099).
- Support for returning snapshot value in `get_blob_properties` response (#13287).

## 12.4.0 (2020-08-12)
**New features**
- Added support for Object Replication Service on `list_blobs` and `get_blob_properties`.
- Added more support for blob tags. Added `if_tags_match_condition` that allow a user to specify a SQL statement for the blob's tags to satisfy.
- Added support for setting and getting the `default_index_document_path` of `StaticWebsite` property on the service client.
- Added `rehydrate_priority` to BlobProperties.
- Added support to seal an append blob. Added `test_seal_append_blob`. Added ability to specify `seal_destination_blob` on `start_copy_from_url`. `is_append_blob_sealed` property returned on get_blob_properties/download_blob/list_blobs.
- Added support to set tier on a snapshot or version.

**Fixes**
- Fixed the bug when parsing blob url with '/' in blob name (#12563, #12568).
- Support batch delete empty blob list (#12778, #12779).
- Fixed `blob_samples_query` bug.
- Fixed empty etag in acquire_blob response (#8490).

## 12.4.0b1 (2020-07-07)
**New features**
- Added `query_blob` API to enable users to select/project on block blob or block blob snapshot data by providing simple query expressions.
- Added blob versioning feature, so that every time there is a blob override the `version_id` will be updated automatically and returned in the response, the `version_id` could be used later to refer to the overwritten blob.
- Added `set_blob_tags`,`get_blob_tags` and `find_blobs_by_tags` so that user can get blobs based on blob tags.
- Block size is increased to 4GB at maximum, max single put size is increased to 5GB.
- For replication enabled account, users can get replication policies when get blob properties.

## 12.3.2
**Fixes**
- Fixed issue where batch requests could not be combined with SAS (#9534)
- Batch requests now support applying parameters to individual blobs within the request via passing in a dictionary.
- Metadata cannot have leading space (#11457)
- Improve the performance of upload when using max_concurrency

**Notes**
- Updated dependency from azure-core<2.0.0,>=1.2.2 to azure-core<2.0.0,>=1.6.0

## 12.3.1 (2020-04-29)

**Fixes**
- Fixed issue where batch requests could not be combined with token credentials (#9534)
- Skip '/' in url encoding.


## 12.3.0 (2020-03-10)

**New features**

- `stage_block` now propagates the response from the service.

**Fixes**
- Fixed a bug where a new transport is being passed in the `get_blob_client` method instead
of using the existing one in the `ContainerClient`.

**Notes**
- The `StorageUserAgentPolicy` is now replaced with the `UserAgentPolicy` from azure-core. With this, the custom user agents are now added as a prefix instead of being appended.


## 12.2.0

**New features**
- Added support for the 2019-07-07 service version, and added `api_version` parameter to clients.
- Added support for encryption scopes that that could be used to encrypt blob content.
- Added `get_page_range_diff_for_managed_disk` API which returns the list of valid page ranges diff between a snapshot and managed disk or another snapshot.

**Fixes**
- Responses are always decoded as UTF8

## 12.1.0 (2019-12-04)

**New features**
- Added `download_blob` method to the `container_client`.
- All the clients now have a `close()` method to close the sockets opened by the client when using without a context manager.

**Fixes and improvements**
- Fixes a bug where determining length breaks while uploading a blob when provided with an invalid fileno.
- Fix metadata not being included in `commit_block_list` operation.


## 12.0.0 (2019-10-31)

**Breaking changes**

- `set_container_access_policy` has required parameter `signed_identifiers`.
- `NoRetry` policy has been removed. Use keyword argument `retry_total=0` for no retries.
- `StorageStreamDownloader` is no longer iterable. To iterate over the blob data stream, use `StorageStreamDownloader.chunks`.
- The public attributes of `StorageStreamDownloader` have been limited to:
  - `name` (str): The name of the blob.
  - `container` (str): The container the blob is being downloaded from.
  - `properties` (`BlobProperties`): The properties of the blob.
  - `size` (int): The size of the download. Either the total blob size, or the length of a subsection if sepcified. Previously called `download_size`.
- `StorageStreamDownloader` now has new functions:
  - `readall()`: Reads the complete download stream, returning bytes. This replaces the functions `content_as_bytes` and `content_as_text` which have been deprecated.
  - `readinto(stream)`: Download the complete stream into the supplied writable stream, returning the number of bytes written. This replaces the function `download_to_stream` which has been deprecated.
- Module level functions `upload_blob_to_url` and `download_blob_from_url` functions options are now keyword only:
  - `overwrite`
  - `max_concurrency`
  - `encoding`
- Removed types that were accidentally exposed from two modules. Only `BlobServiceClient`, `ContainerClient`,
`BlobClient` and `BlobLeaseClient` should be imported from azure.storage.blob.aio
- `Logging` has been renamed to `BlobAnalyticsLogging`.
- Client and model files have been made internal. Users should import from the top level modules `azure.storage.blob` and `azure.storage.blob.aio` only.
- All operations that take Etag conditional parameters (`if_match` and `if_none_match`) now take explicit `etag` and `match_condition` parameters, where `etag` is the Etag value, and `match_condition` is an instance of `azure.core.MatchConditions`.
- The `generate_shared_access_signature` methods on each of `BlobServiceClient`, `ContainerClient` and `BlobClient` have been replaced by module level functions `generate_account_sas`, `generate_container_sas` and `generate_blob_sas`.
- The batch APIs now have an additional keyword only argument `raise_on_any_failure` which defaults to True. This will raise an error even if there's a partial batch failure.
- `LeaseClient` has been renamed to `BlobLeaseClient`.
- `get_service_stats` now returns a dict
- `get_service_properties` now returns a dict with keys consistent to `set_service_properties`

**New features**

- Added async module-level `upload_blob_to_url` and `download_blob_from_url` functions.
- `ResourceTypes`, and `Services` now have method `from_string` which takes parameters as a string.

## 12.0.0b4 (2019-10-08)

**Breaking changes**

- Permission models.
  - `AccountPermissions`, `BlobPermissions` and `ContainerPermissions` have been renamed to
  `AccountSasPermissions`, `BlobSasPermissions` and `ContainerSasPermissions` respectively.
  - enum-like list parameters have been removed from all three of them.
  - `__add__` and `__or__` methods are removed.
- `max_connections` is now renamed to `max_concurrency`.
- `ContainerClient` now accepts only `account_url` with a mandatory string param `container_name`.
To use a container_url, the method `from_container_url` must be used.
- `BlobClient` now accepts only `account_url` with mandatory string params `container_name` and
`blob_name`. To use a blob_url, the method `from_blob_url` must be used.
- Some parameters have become keyword only, rather than positional. Some examples include:
  - `loop`
  - `max_concurrency`
  - `validate_content`
  - `timeout` etc.
- APIs now take in `offset` and `length` instead of `range_start` and `range_end` consistently.
`length` is the number of bytes to take in starting from the `offset`. The APIs that have been
changed include:
  - `get_page_ranges`
  - `upload_page`
  - `upload_pages_from_url`
  - `clear_page`
  - `append_block_from_url`
- `block_id` is not optional in `BlobBlock` model.

**New features**

- Add support for delete_blobs API to ContainerClient (Python 3 only)
- Add support for set_standard_blob_tier_blobs to ContainerClient (Python 3 only)
- Add support for set_premium_page_blob_tier_blobs to ContainerClient (Python 3 only)
- Added support to set rehydrate blob priority for Block Blob, including Set Standard Blob Tier/Copy Blob APIs
- Added blob tier support for Block Blob, including Upload Blob/Commit Block List/Copy Blob APIs.
- `AccountSasPermissions`, `BlobSasPermissions`, `ContainerSasPermissions` now have method `from_string`
which takes parameters as a string.

**Fixes and improvements**
- Downloading page blobs now take advantage of their sparseness.
- The `length` param in `download_blob` now takes the number of bytes to take in starting from the `offset`
instead of a harde set end value.

**Dependency updates**
- Adopted [azure-core](https://pypi.org/project/azure-core/) 1.0.0b4
  - If you later want to revert to previous versions of azure-storage-blob, or another Azure SDK
  library requiring azure-core 1.0.0b1 or azure-core 1.0.0b2, you must explicitly install
  the specific version of azure-core as well. For example:

  `pip install azure-core==1.0.0b2 azure-storage-blob==12.0.0b2`

## 12.0.0b3 (2019-09-10)

**New features**
- Added SAS support for snapshot and identity.
- Distributed tracing framework OpenCensus is now supported.
- Added support for append_block_from_url API for append blobs.
- Added support for upload_pages_from_url API for page blobs.
- Added support for client provided encryption key to numerous APIs.

**Dependency updates**
- Adopted [azure-core](https://pypi.org/project/azure-core/) 1.0.0b3
  - If you later want to revert to previous versions of azure-storage-blob, or another Azure SDK
  library requiring azure-core 1.0.0b1 or azure-core 1.0.0b2, you must explicitly install
  the specific version of azure-core as well. For example:

  `pip install azure-core==1.0.0b2 azure-storage-blob==12.0.0b2`

**Fixes and improvements**
- Fix where content-type was being added in the request when not mentioned explicitly.


## 12.0.0b2 (2019-08-06)

**Breaking changes**
- Renamed `copy_blob_from_url` to `start_copy_from_url` and changed behaviour to return a dictionary of copy properties rather than a polling object. Status of the copy operation can be retrieved with the `get_blob_properties` operation.
- Added `abort_copy` operation to the `BlobClient` class. This replaces the previous abort operation on the copy status polling operation.
- The behavior of listing operations has been modified:
    - The previous `marker` parameter has been removed.
    - The iterable response object now supports a `by_page` function that will return a secondary iterator of batches of results. This function supports a `continuation_token` parameter to replace the previous `marker` parameter.
- Some parameters have become keyword only, rather than positional. Some examples include:
    - `timeout`
    - `lease`
    - `encoding`
    - Modification conditions, e.g. `if_modified_since`, `if_match` , `maxsize_condition`, etc

**New features**
- Added async APIs to subnamespace `azure.storage.blob.aio`.
- Distributed tracing framework OpenCensus is now supported.

**Dependency updates**
- Adopted [azure-core](https://pypi.org/project/azure-core/) 1.0.0b2
  - If you later want to revert to azure-storage-blob 12.0.0b1, or another Azure SDK
  library requiring azure-core 1.0.0b1, you must explicitly install azure-core
  1.0.0b1 as well. For example:

  `pip install azure-core==1.0.0b1 azure-storage-blob==12.0.0b1`

**Fixes and improvements**
- Fix for SAS URL encoding (#6500)
- General refactor of duplicate and shared code.


## 12.0.0b1 (2019-07-02)

Version 12.0.0b1 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Storage Blobs. For more information about this, and preview releases of other Azure SDK libraries, please visit
https://aka.ms/azure-sdk-preview1-python.

**Breaking changes: New API design**
- Operations are now scoped to a particular client:
    - `BlobServiceClient`: This client handles account-level operations. This includes managing service properties and listing the containers within an account.
    - `ContainerClient`: The client handles operations for a particular container. This includes creating or deleting that container, as well as listing the blobs within that container and managing properties and metadata.
    - `BlobClient`: The client handles operations for a particular blob. This includes creating or deleting that blob, as well as upload and download data and managing properties.
    This BlobClient handles all blob types (block, page and append). Where operations can behave differently according to type (i.e. `upload_blob`) the default behaviour will be block blobs unless otherwise specified.
    - `LeaseClient`: Handles all lease operations for both containers and blobs.

    These clients can be accessed by navigating down the client hierarchy, or instantiated directly using URLs to the resource (account, container or blob).
    For full details on the new API, please see the [reference documentation](https://azure.github.io/azure-sdk-for-python/storage.html#azure-storage-blob).
- Copy blob operations now return a polling object that can be used to check the status of the operation, as well as abort the operation.
- New module level operations for simple upload and download using a blob URL.
- Download operations now return a streaming object that can download data in multiple ways:
    - Iteration: The streamer is an iterable object that will download and yield the content in chunks. Only supports single threaded download.
    - `content_as_bytes`: Return the entire blob content as bytes. Blocking operation that supports multi-threaded download.
    - `content_as_text`: Return the entire blob content as decoded text. Blocking operation that supports multi-threaded download.
    - `download_to_stream`: Download the entire content to an open stream handle (e.g. an open file). Supports multi-threaded download.
- New underlying REST pipeline implementation, based on the new `azure-core` library.
- Client and pipeline configuration is now available via keyword arguments at both the client level, and per-operation. See reference documentation for a full list of optional configuration arguments.
- Authentication using `azure-identity` credentials
  - see the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md)
  for more information
- New error hierarchy:
    - All service errors will now use the base type: `azure.core.exceptions.HttpResponseError`
    - The are a couple of specific exception types derived from this base type for common error scenarios:
        - `ResourceNotFoundError`: The resource (e.g. queue, message) could not be found. Commonly a 404 status code.
        - `ResourceExistsError`: A resource conflict - commonly caused when attempting to create a resource that already exists.
        - `ResourceModifiedError`: The resource has been modified (e.g. overwritten) and therefore the current operation is in conflict. Alternatively this may be raised if a condition on the operation is not met.
        - `ClientAuthenticationError`: Authentication failed.
- Operation `set_blob_properties` has been renamed to `set_http_headers`.
- Operations `get_blob_to_<output>` have been replaced with `download_blob`. See above for download output options.
- Operations `create_blob_from_<input>` have been replace with `upload_blob`.
- Operation `create_blob` has been renamed to separate `create_page_blob` and `create_append_blob`.
- Operations `get_container_acl` and `set_container_acl` have been renamed to `get_container_access_policy` and `set_container_access_policy`.
- Operation `snapshot_blob` has been renamed to `create_snapshot`.
- Operation `copy_blob` has been renamed to `copy_blob_from_url`.
- Operations `put_block` and `put_block_from_url` have been renamed to `stage_block` and `stage_block_from_url`.
- Operation `put_block_list` has been renamed to `commit_block_list`.
- No longer have specific operations for `get_metadata` - use `get_properties` instead.
- No longer have specific operations for `exists` - use `get_properties` instead.
- Operation `incremental_copy_blob` has been replaced by an optional boolean flag in the `copy_blob_from_url` operation.
- Operation `update_page` has been renamed to `upload_page`.
- Operation `get_page_ranges_diff` has been replaced by an optional str flag in the `get_page_ranges` operation.

## 2.0.1

- Updated dependency on azure-storage-common.

## 2.0.0

- Support for 2018-11-09 REST version. Please see our REST API documentation and blog for information about the related added features.
- Added support for append block from URL(synchronously) for append blobs.
- Added support for update page from URL(synchronously) for page blobs.
- Added support for generating and using blob snapshot SAS tokens.
- Added support for generating user delegation SAS tokens.

## 1.5.0

- Added new method list_blob_names to efficiently list only blob names in an efficient way.

## 1.4.0

- azure-storage-nspkg is not installed anymore on Python 3 (PEP420-based namespace package)
- copy_blob method added to BlockBlobService to enable support for deep sync copy.

## 1.3.1

- Fixed design flaw where get_blob_to_* methods buffer entire blob when max_connections is set to 1.
- Added support for access conditions on append_blob_from_* methods.

## 1.3.0

- Support for 2018-03-28 REST version. Please see our REST API documentation and blog for information about the related added features.
- Added support for setting static website service properties.
- Added support for getting account information, such as SKU name and account kind.
- Added support for put block from URL(synchronously).

## 1.2.0rc1

- Support for 2017-11-09 REST version. Please see our REST API documentation and blog for information about the related added features.
- Support for write-once read-many containers.
- Added support for OAuth authentication for HTTPS requests(Please note that this feature is available in preview).

## 1.1.0

- Support for 2017-07-29 REST version. Please see our REST API documentation and blogs for information about the related added features.
- Added support for soft delete feature. If a delete retention policy is enabled through the set service properties API, then blobs or snapshots could be deleted softly and retained for a specified number of days, before being permanently removed by garbage collection.
- Error message now contains the ErrorCode from the x-ms-error-code header value.

## 1.0.0

- The package has switched from Apache 2.0 to the MIT license.
- Fixed bug where get_blob_to_* cannot get a single byte when start_range and end_range are both equal to 0.
- Optimized page blob upload for create_blob_from_* methods, by skipping the empty chunks.
- Added convenient method to generate container url (make_container_url).
- Metadata keys are now case-preserving when fetched from the service. Previously they were made lower-case by the library.

## 0.37.1

- Enabling MD5 validation no longer uses the memory-efficient algorithm for large block blobs, since computing the MD5 hash requires reading the entire block into memory.
- Fixed a bug in the _SubStream class which was at risk of causing data corruption when using the memory-efficient algorithm for large block blobs.
- Support for AccessTierChangeTime to get the last time a tier was modified on an individual blob.
