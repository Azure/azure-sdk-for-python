# Change Log azure-storage-blob


## Version 12.0.0b2:

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


## Version 12.0.0b1:

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
    For full details on the new API, please see the [reference documentation](http://azure.github.io/azure-sdk-for-python/ref/azure.storage.blob.html).
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
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md)
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

## Version 2.0.1:

- Updated dependency on azure-storage-common.

## Version 2.0.0:

- Support for 2018-11-09 REST version. Please see our REST API documentation and blog for information about the related added features.
- Added support for append block from URL(synchronously) for append blobs.
- Added support for update page from URL(synchronously) for page blobs.
- Added support for generating and using blob snapshot SAS tokens.
- Added support for generating user delegation SAS tokens.

## Version 1.5.0:

- Added new method list_blob_names to efficiently list only blob names in an efficient way.

## Version 1.4.0:

- azure-storage-nspkg is not installed anymore on Python 3 (PEP420-based namespace package)
- copy_blob method added to BlockBlobService to enable support for deep sync copy.

## Version 1.3.1:

- Fixed design flaw where get_blob_to_* methods buffer entire blob when max_connections is set to 1.
- Added support for access conditions on append_blob_from_* methods.

## Version 1.3.0:

- Support for 2018-03-28 REST version. Please see our REST API documentation and blog for information about the related added features.
- Added support for setting static website service properties.
- Added support for getting account information, such as SKU name and account kind.
- Added support for put block from URL(synchronously).

## Version 1.2.0rc1:

- Support for 2017-11-09 REST version. Please see our REST API documentation and blog for information about the related added features.
- Support for write-once read-many containers.
- Added support for OAuth authentication for HTTPS requests(Please note that this feature is available in preview).

## Version 1.1.0:

- Support for 2017-07-29 REST version. Please see our REST API documentation and blogs for information about the related added features.
- Added support for soft delete feature. If a delete retention policy is enabled through the set service properties API, then blobs or snapshots could be deleted softly and retained for a specified number of days, before being permanently removed by garbage collection.
- Error message now contains the ErrorCode from the x-ms-error-code header value.

## Version 1.0.0:

- The package has switched from Apache 2.0 to the MIT license.
- Fixed bug where get_blob_to_* cannot get a single byte when start_range and end_range are both equal to 0.
- Optimized page blob upload for create_blob_from_* methods, by skipping the empty chunks.
- Added convenient method to generate container url (make_container_url).
- Metadata keys are now case-preserving when fetched from the service. Previously they were made lower-case by the library.

## Version 0.37.1:

- Enabling MD5 validation no longer uses the memory-efficient algorithm for large block blobs, since computing the MD5 hash requires reading the entire block into memory.
- Fixed a bug in the _SubStream class which was at risk of causing data corruption when using the memory-efficient algorithm for large block blobs.
- Support for AccessTierChangeTime to get the last time a tier was modified on an individual blob.
