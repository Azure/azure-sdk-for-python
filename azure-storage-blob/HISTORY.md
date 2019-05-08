# Change Log azure-storage-blob

> See [BreakingChanges](BreakingChanges.md) for a detailed list of API breaks.

## Version 2.0.0:

- New API.

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
