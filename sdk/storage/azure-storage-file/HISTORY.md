# Change Log azure-storage-file

## Version 12.0.0b1:

For release notes and more information please visit
https://aka.ms/azure-sdk-preview1-python

- **Breaking** New API desgin:
    - Operations are now scoped to a particular client:
        - `FileServiceClient`: This client handles account-level operations. This includes managing service properties and listing the shares within an account.
        - `ShareClient`: The client handles operations for a particular share. This includes creating or deleting that share, as well as listing the directories within that share, and managing properties and metadata.
        - `DirectoryClient`: The client handles operations for a particular directory. This includes creating or deleting that directory, as well as listing the files and subdirectories, and managing properties and metadata.
        - `FileClient`: The client handles operations for a particular file. This includes creating or deleting that file, as well as upload and download data and managing properties.

        These clients can be accessed by navigating down the client hierarchy, or instantiated directly using URLs to the resource (account, share, directory or file).
      For full details on the new API, please see reference documentation.
    - The copy file operation now return a polling object that can be used to check the status of the operation, as well as abort the operation.
    - The `close_handles` operation now return a polling object that can be used to check the status of the operation.
    - Download operations now return a streaming object that can download data in multiple ways:
        - Iteration: The streamer is an iterable object that will download and yield the content in chunks. Only supports single threaded download.
        - `content_as_bytes`: Return the entire file content as bytes. Blocking operation that suppots multi-threaded download.
        - `content_as_text`: Return the entire file content as decoded text. Blocking operation that supports multi-threaded download.
        - `download_to_stream`: Download the entire content to an open stream handle (e.g. an open file). Supports multi-threaded download.
    - New underlying REST pipeline implementation, based on the new `azure.core` library.
    - Client and pipeline configuration is now available via keyword arguments at both the client level, and per-operation. See reference documentation for a full list of optional configuration arguments.
    - New error hierarchy:
        - All service errors will now use the base type: `azure.core.exceptions.HttpResponseError`
        - The are a couple of specific exception types derived from this base type for common error scenarios:
            - `ResourceNotFoundError`: The resource (e.g. queue, message) could not be found. Commonly a 404 status code.
            - `ResourceExistsError`: A resource conflict - commonly caused when attempting to create a resource that already exists.
            - `ResourceModifiedError`: The resource has been modified (e.g. overwritten) and therefore the current operation is in conflict. Alternatively this may be raised if a condition on the operation is not met.
            - `ClientAuthenticationError`: Authentication failed.
    - Operation `set_file_properties` has been renamed to `set_http_headers`.
    - Operations `get_file_to_<output>` have been replaced with `download_file`. See above for download output options.
    - Operations `create_file_from_<input>` have been replace with `upload_file`.
    - Operations `get_share_acl` and `set_share_acl` have been renamed to `get_share_access_policy` and `set_share_access_policy`.
    - Operation `set_share_properties` has been renamed to `set_share_quota`.
    - Operation `snapshot_share` has been renamed to `create_snapshot`.
    - Operation `copy_file` has been renamed to `copy_file_from_url`.
    - No longer have specific operations for `get_metadata` - use `get_properties` instead.
    - No longer have specific operations for `exists` - use `get_properties` instead.
    - Operation `update_range` has been renamed to `upload_range`.

## Version 2.0.1:
- Updated dependency on azure-storage-common.

## Version 2.0.0:
- Support for 2018-11-09 REST version. Please see our REST API documentation and blogs for information about the related added features.
- Added an option to get share stats in bytes.
- Added support for listing and closing file handles.

## Version 1.4.0:

- azure-storage-nspkg is not installed anymore on Python 3 (PEP420-based namespace package)

## Version 1.3.1:

- Fixed design flaw where get_file_to_* methods buffer entire file when max_connections is set to 1.

## Version 1.3.0:

- Support for 2018-03-28 REST version. Please see our REST API documentation and blog for information about the related added features.

## Version 1.2.0rc1:

- Support for 2017-11-09 REST version. Please see our REST API documentation and blog for information about the related added features.

## Version 1.1.0:

- Support for 2017-07-29 REST version. Please see our REST API documentation and blogs for information about the related added features.
- Error message now contains the ErrorCode from the x-ms-error-code header value.

## Version 1.0.0:

- The package has switched from Apache 2.0 to the MIT license.
- Fixed bug where get_file_to_* cannot get a single byte when start_range and end_range are both equal to 0.
- Metadata keys are now case-preserving when fetched from the service. Previously they were made lower-case by the library.