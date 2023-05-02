# Release History

## 12.13.0b1 (Unreleased)

### Features Added
- Added support for service version 2023-01-03.
- Added `access_rights` property to `Handle`.

## 12.12.0 (2023-04-12)

### Features Added
- Stable release of features from 12.12.0b1

## 12.12.0b1 (2023-03-28)

### Features Added
- Added support for service version 2022-11-02.
- Added support for `TokenCredential` to be used for authentication. A `TokenCredential` can be provided for the
`credential` parameter to any client constructor. **Note:** When using a `TokenCredential`, the new keyword parameter
`token_intent` is **required** and must be provided. Additionally, this form of authentication is only supported for
certain operations in the Data Plane SDK.
- Added support for `allow_trailing_dot` and `allow_source_trailing_dot` on client construction. When
`allow_trailing_dot` is provided, the service will not silently remove any trailing `.` character from directory/file
names for all operations made from that client. `allow_source_trailing_dot` will apply this same rule to source files
when performing a rename or copy operation.

## 12.11.1 (2023-03-08)

### Bugs Fixed
- Fixed "duplicate type signatures" MyPy error.

## 12.11.0 (2023-02-22)

### Features Added
- Stable release of features from 12.11.0b1

## 12.11.0b1 (2023-02-02)

### Features Added
- Added support for service version 2021-12-02.
- Added support for file and directory paths that contain invalid XML characters. When listing or fetching properties,
the service will encode illegal characters and the SDK will now automatically decode them.
- Added support for `AsyncIterable` as data type for async file upload.

### Bugs Fixed
- Fixed an issue where keyword `name_starts_with` was not being passed to the service properly for the `list_shares` async API

### Other Changes
- Removed `msrest` dependency.
- Added `typing-extensions>=4.0.1` as a dependency.
- Added `isodate>=0.6.1` as a dependency.
- Added extra dependency `aio` for installing optional async dependencies. Use `pip install azure-storage-file-share[aio]` to install.

## 12.10.1 (2022-10-18)

### Bugs Fixed
- Fixed possible `ValueError` for invalid content range that gets raised when downloading empty files through Azurite.

## 12.10.0 (2022-10-11)

### Features Added
- Stable release of features from 12.10.0b1.

### Bugs Fixed
- Fixed an issue where calling `download_file` with an invalid base64-encoded account key would raise an
`AttributeError` rather than the proper `AzureSigningError`.

### Other Changes
- Changed the default value for `read_timeout` to 60 seconds for all clients.

## 12.10.0b1 (2022-08-23)

This version and all future versions will require Python 3.7+. Python 3.6 is no longer supported.

### Features Added
- Added support for `AzureNamedKeyCredential` as a valid `credential` type.

## 12.9.0 (2022-07-07)

### Features Added
- Stable release of features from 12.9.0b1.
- Added support for progress tracking to `upload_file()` and `download_file()` via a new optional callback, `progress_hook`.

## 12.9.0b1 (2022-06-15)

### Features Added
- Added support for `file_change_time` to `start_copy_from_url` API

## 12.8.0 (2022-05-09)

### Features Added
- Stable release of features from 12.8.0b1.

### Bugs Fixed
- Fixed a bug, introduced in the previous beta release, that caused Authentication errors when attempting to use
an Account SAS with certain service level operations.

## 12.8.0b1 (2022-04-14)

### Features Added
- Added support for service version 2021-06-08.
- Added support for missing parameters on `create_directory()` including `file_attributes`, `file_creation_time`,
`file_last_write_time`, `file_permission` and `file_permission_key`.
- Added support for setting `content_type` on `rename_file()`.
- Added support for setting `file_change_time` on `create_directory()`, `set_http_headers()` (directory)
`rename_directory()`, `create_file()`, `set_http_headers()` (file) and `rename_file()`.
- Added support for setting `file_last_write_mode` on `upload_range()` and `upload_range_from_url()`
with possible values of `Now` or `Preserve`.

### Bugs Fixed
- Updated `create_share()` docstring to have the correct return-type of `None`

## 12.7.0 (2022-03-08)

This version and all future versions will require Python 3.6+. Python 2.7 is no longer supported.

### Stable release of preview features
- Added support for service version 2021-02-12, 2021-04-10.
- Added support for premium file share provisioned_bandwidth property.
- Added support for checking if a directory exists using `exists()`.
- Added support for `rename_directory()` and `rename_file()`.
- Added support for `Create (c)` SAS permission for Share SAS.

### Bugs Fixed
- Fixed a bug where `start_copy_from_url()` was not sending the `ignore_read_only` parameter correctly.

## 12.7.0b2 (2022-02-08)

This version and all future versions will require Python 3.6+. Python 2.7 is no longer supported.

### Features Added
- Added support for service version 2021-04-10.
- Added support for `rename_directory()` and `rename_file()`.
- Added support for `Create (c)` SAS permission for Share SAS.

### Bugs Fixed
- Update `azure-core` dependency to avoid inconsistent dependencies from being installed.
- Fixed a bug, that was introduced in the previous beta release, where `generate_account_sas()`
was not generating the proper SAS signature.

## 12.7.0b1 (2021-12-13)

### Features Added
- Added support for service version 2021-02-12.
- Added support for premium file share provisioned_bandwidth property.
- Added support for checking if a directory exists using `exists()`.

## 12.6.0 (2021-09-15)
**Stable release of preview features**
- Added support for service version 2020-10-02 (STG78)
- Added OAuth support for file copy source.

## 12.6.0b1 (2021-07-27)
**New features**
- Added OAuth support for file copy source.

**Fixes**
- Ensured that download fails if file modified mid download

## 12.5.0 (2021-06-09)
**New features**
- Added support for lease operation on a share, eg. acquire_lease

## 12.5.0b1 (2021-05-12)
**New features**
- Added support for lease operation on a share, eg. acquire_lease

## 12.4.2 (2021-04-20)
**Fixes**
- Make `AccountName`, `AccountKey` etc. in conn_str case insensitive
- Fixed `downloader.chunks()` return chunks in different size (#9419, #15648)
- Fixed unclosed `ThreadPoolExecutor` (#8955)

## 12.4.1 (2021-01-20)
**Fixes**
- Fixed msrest dependency issue (#16250)

## 12.4.0 (2021-01-13)
**Stable release of preview features**
- Added support for enabling root squash and share protocols for file share.
- Added support for `AzureSasCredential` to allow SAS rotation in long living clients.

## 12.4.0b1 (2020-12-07)
**New features**
- Added support for enabling root squash and share protocols for file share.


## 12.3.0 (2020-11-10)
**Stable release of preview features**
- Preview feature enabling SMB Multichannel for the share service.
- Preview feature `get_ranges` on ShareFileClient

**New features**
- Added `set_share_properties` which allows setting share tier. 

**Notes**
- Updated dependency `azure-core` from  azure-core<2.0.0,>=1.2.2 to azure-core<2.0.0,>=1.9.0 to get continuation_token attr on AzureError.

## 12.3.0b1 (2020-10-02)
**New features**
- Added support for enabling SMB Multichannel for the share service.
- Added support for leasing a share.
- Added support for getting the range diff between current file and a snapshot as well as getting the diff between two file snapshots.


## 12.2.0 (2020-08-13)
**Stable release of preview features**
- Preview feature `undelete_share` on FileShareServiceClient.

## 12.2.0b1 (2020-07-07)
**New features**
- Added `undelete_share` on FileShareServiceClient so that users can restore deleted share on share soft delete enabled account. Users can also list deleted shares when `list_shares` by specifying `include_deleted=True`.

## 12.1.2 
**Fixes**
- Improve the performance of upload when using max_concurrency

## 12.1.1 (2020-03-10)

**Notes**
- The `StorageUserAgentPolicy` is now replaced with the `UserAgentPolicy` from azure-core. With this, the custom user agents are now added as a prefix instead of being appended.

## 12.1.0 

**New features**
- Added support for the 2019-07-07 service version, and added `api_version` parameter to clients.
- `ShareLeaseClient` was introduced to both sync and async versions of the SDK, which allows users to perform operations on file leases.
- `failed_handles_count` info was included in `close_handle` and `close_all_handles` result.
- Added support for obtaining premium file properties in `list_shares` and `get_share_properties`.
- Added support for additional `start_copy_from_url` parameters - `file_permission`, `permission_key`, `file_attributes`, `file_creation_time`, `file_last_write_time`, `ignore_read_only`, and `set_archive_attribute`.

**Fixes and improvements**
- Fixed a bug: `clear_range` API was not working.

**Fixes**
- Responses are always decoded as UTF8

## 12.0.0 

**New features**
- Added `delete_directory` method to the `share_client`.
- All the clients now have a `close()` method to close the sockets opened by the client when using without a context manager.

**Fixes and improvements**
- Fixes a bug where determining length breaks while uploading a file when provided with an invalid fileno.

**Breaking changes**
- `close_handle(handle)` and `close_all_handles()` no longer return int. These functions return a dictionary which has the number of handles closed and number of handles failed to be closed.

## 12.0.0b5 

**Important: This package was previously named azure-storage-file**

Going forward, to use this SDK, please install `azure-storage-file-share`.
Additionally:
- The namespace within the package has also been renamed to `azure.storage.fileshare`.
- `FileServiceClient` has been renamed to `ShareServiceClient`.
- `DirectoryClient` has been renamed to `ShareDirectoryClient`.
- `FileClient` has been renamed to `ShareFileClient`.

**Additional Breaking changes**

- `ShareClient` now accepts only `account_url` with mandatory a string param `share_name`.
To use a share_url, the method `from_share_url` must be used.
- `ShareDirectoryClient` now accepts only `account_url` with mandatory string params `share_name` and `directory_path`.
To use a directory_url, the method `from_directory_url` must be used.
- `ShareFileClient` now accepts only `account_url` with mandatory string params `share_name` and
`file_path`. To use a file_url, the method `from_file_url` must be used.
- `file_permission_key` parameter has been renamed to `permission_key`
- `set_share_access_policy` has required parameter `signed_identifiers`.
- `NoRetry` policy has been removed. Use keyword argument `retry_total=0` for no retries.
- Removed types that were accidentally exposed from two modules. Only `ShareServiceClient`, `ShareClient`, `ShareDirectoryClient` and `ShareFileClient` should be imported from azure.storage.fileshare.aio
- Some parameters have become keyword only, rather than positional. Some examples include:
  - `loop`
  - `max_concurrency`
  - `validate_content`
  - `timeout` etc.
- Client and model files have been made internal. Users should import from the top level modules `azure.storage.fileshare` and `azure.storage.fileshare.aio` only.
- The `generate_shared_access_signature` methods on each of `ShareServiceClient`, `ShareClient` and `ShareFileClient` have been replaced by module level functions `generate_account_sas`, `generate_share_sas` and `generate_file_sas`.
- `start_range` and `end_range` params are now renamed to and behave like`offset` and `length` in
the following APIs:
  - download_file
  - upload_range
  - upload_range_from_url
  - clear_range
  - get_ranges
- `StorageStreamDownloader` is no longer iterable. To iterate over the file data stream, use `StorageStreamDownloader.chunks`.
- The public attributes of `StorageStreamDownloader` have been limited to:
  - `name` (str): The name of the file.
  - `path` (str): The full path of the file.
  - `share` (str): The share the file will be downloaded from.
  - `properties` (`FileProperties`): The properties of the file.
  - `size` (int): The size of the download. Either the total file size, or the length of a subsection if specified. Previously called `download_size`.
- `StorageStreamDownloader` now has new functions:
  - `readall()`: Reads the complete download stream, returning bytes. This replaces the functions `content_as_bytes` and `content_as_text` which have been deprecated.
  - `readinto(stream)`: Download the complete stream into the supplied writable stream, returning the number of bytes written. This replaces the function `download_to_stream` which has been deprecated.
- `ShareFileClient.close_handles` and `ShareDirectoryClient.close_handles` have both been replaced by two functions each; `close_handle(handle)` and `close_all_handles()`. These functions are blocking and return integers (the number of closed handles) rather than polling objects.
- `get_service_properties` now returns a dict with keys consistent to `set_service_properties`

**New features**

- `ResourceTypes`, `NTFSAttributes`, and `Services` now have method `from_string` which takes parameters as a string.


## 12.0.0b4 

**Breaking changes**

- Permission models.
  - `AccountPermissions`, `SharePermissions` and `FilePermissions` have been renamed to
  `AccountSasPermissions`, `ShareSasPermissions` and `FileSasPermissions` respectively.
  - enum-like list parameters have been removed from all three of them.
  - `__add__` and `__or__` methods are removed.
- `max_connections` is now renamed to `max_concurrency`.

**New features**

- `AccountSasPermissions`, `FileSasPermissions`, `ShareSasPermissions` now have method `from_string` which
takes parameters as a string.

## 12.0.0b3 

**New features**
- Added upload_range_from_url API to write the bytes from one Azure File endpoint into the specified range of another Azure File endpoint.
- Added set_http_headers for directory_client, create_permission_for_share and get_permission_for_share APIs.
- Added optional parameters for smb properties related parameters for create_file*, create_directory* related APIs and set_http_headers API.
- Updated get_properties for directory and file so that the response has SMB properties.

**Dependency updates**
- Adopted [azure-core](https://pypi.org/project/azure-core/) 1.0.0b3
  - If you later want to revert to previous versions of azure-storage-file, or another Azure SDK
  library requiring azure-core 1.0.0b1 or azure-core 1.0.0b2, you must explicitly install
  the specific version of azure-core as well. For example:

  `pip install azure-core==1.0.0b2 azure-storage-file==12.0.0b2`

**Fixes and improvements**
- Fix where content-type was being added in the request when not mentioned explicitly.


## 12.0.0b2 

**Breaking changes**
- Renamed `copy_file_from_url` to `start_copy_from_url` and changed behaviour to return a dictionary of copy properties rather than a polling object. Status of the copy operation can be retrieved with the `get_file_properties` operation.
- Added `abort_copy` operation to the `FileClient` class. This replaces the previous abort operation on the copy status polling operation.
- The behavior of listing operations has been modified:
    - The previous `marker` parameter has been removed.
    - The iterable response object now supports a `by_page` function that will return a secondary iterator of batches of results. This function supports a `continuation_token` parameter to replace the previous `marker` parameter.
- The new listing behaviour is also adopted by the `receive_messages` operation:
    - The receive operation returns a message iterator as before.
    - The returned iterator supports a `by_page` operation to receive messages in batches.

**New features**
- Added async APIs to subnamespace `azure.storage.file.aio`.
- Distributed tracing framework OpenCensus is now supported.

**Dependency updates**
- Adopted [azure-core](https://pypi.org/project/azure-core/) 1.0.0b2
  - If you later want to revert to azure-storage-file 12.0.0b1, or another Azure SDK
  library requiring azure-core 1.0.0b1, you must explicitly install azure-core
  1.0.0b1 as well. For example:

  `pip install azure-core==1.0.0b1 azure-storage-file==12.0.0b1`

**Fixes and improvements**
- Fix for closing file handles - continuation token was not being passed to subsequent calls.
- General refactor of duplicate and shared code.


## 12.0.0b1 

Version 12.0.0b1 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Storage Files. For more information about this, and preview releases of other Azure SDK libraries, please visit
https://aka.ms/azure-sdk-preview1-python.

**Breaking changes: New API design**
- Operations are now scoped to a particular client:
    - `FileServiceClient`: This client handles account-level operations. This includes managing service properties and listing the shares within an account.
    - `ShareClient`: The client handles operations for a particular share. This includes creating or deleting that share, as well as listing the directories within that share, and managing properties and metadata.
    - `DirectoryClient`: The client handles operations for a particular directory. This includes creating or deleting that directory, as well as listing the files and subdirectories, and managing properties and metadata.
    - `FileClient`: The client handles operations for a particular file. This includes creating or deleting that file, as well as upload and download data and managing properties.

    These clients can be accessed by navigating down the client hierarchy, or instantiated directly using URLs to the resource (account, share, directory or file).
    For full details on the new API, please see the [reference documentation](https://azure.github.io/azure-sdk-for-python/storage.html#azure-storage-file-share).
- The copy file operation now returns a polling object that can be used to check the status of the operation, as well as abort the operation.
- The `close_handles` operation now return a polling object that can be used to check the status of the operation.
- Download operations now return a streaming object that can download data in multiple ways:
    - Iteration: The streamer is an iterable object that will download and yield the content in chunks. Only supports single threaded download.
    - `content_as_bytes`: Return the entire file content as bytes. Blocking operation that supports multi-threaded download.
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

## 2.0.1 
- Updated dependency on azure-storage-common.

## 2.0.0 
- Support for 2018-11-09 REST version. Please see our REST API documentation and blogs for information about the related added features.
- Added an option to get share stats in bytes.
- Added support for listing and closing file handles.

## 1.4.0 

- azure-storage-nspkg is not installed anymore on Python 3 (PEP420-based namespace package)

## 1.3.1 

- Fixed design flaw where get_file_to_* methods buffer entire file when max_connections is set to 1.

## 1.3.0 

- Support for 2018-03-28 REST version. Please see our REST API documentation and blog for information about the related added features.

## 1.2.0rc1 

- Support for 2017-11-09 REST version. Please see our REST API documentation and blog for information about the related added features.

## 1.1.0 

- Support for 2017-07-29 REST version. Please see our REST API documentation and blogs for information about the related added features.
- Error message now contains the ErrorCode from the x-ms-error-code header value.

## 1.0.0 

- The package has switched from Apache 2.0 to the MIT license.
- Fixed bug where get_file_to_* cannot get a single byte when start_range and end_range are both equal to 0.
- Metadata keys are now case-preserving when fetched from the service. Previously they were made lower-case by the library.
