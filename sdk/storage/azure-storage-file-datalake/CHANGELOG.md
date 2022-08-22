# Release History

## 12.9.0b1 (2022-08-09)

This version and all future versions will require Python 3.7+. Python 3.6 is no longer supported.

### Features Added
- Added support for `AzureNamedKeyCredential` as a valid `credential` type.
- Added support for `flush` to `append_data` API, allowing for append and flush in one operation.
- Encryption Scope is now supported for both `create_file_system` APIs (`FileSystemClient`, `DataLakeServiceClient`).
- Encryption Scope is now supported as a SAS permission.
- Added standard `read` method to `StorageStreamDownloader`.

## 12.8.0 (2022-07-07)

### Features Added
- Stable release of features from 12.8.0b1.
- Removed support for `expiry_options` from file `create` APIs. With this change, `expires_on` now covers all functionality `expiry_options` offered.

## 12.8.0b1 (2022-06-15)

### Features Added
- Added support for service version 2021-08-06.
- Added support for `owner`, `group`, `acl`, `lease_id`, `lease_duration` to both file and directory `create` APIs.
- Added support for `expiry_options`, `expires_on` to file `create` APIs.

## 12.7.0 (2022-05-09)

### Features Added
- Stable release of features from 12.7.0b1.

### Bugs Fixed
- Fixed a bug, introduced in the previous beta release, that caused Authentication errors when attempting to use
an Account SAS with certain service level operations.

## 12.7.0b1 (2022-04-14)

### Features Added
- Added support for service version 2021-06-08 as well as previous versions.
- Added support for Customer-Provided Keys (cpk) to all required APIs.
- The `get_paths()` API now returns `creation_time` and `expiry_time` for each path.

### Bugs Fixed
- Updated `create_file_system()` docstring to have the correct return-type of `None`
- Fixed parsing of extra `/` symbols not being stripped properly in `async` clients
- Fixed a bug where `get_paths()` would fail if a path did not contain `last_modified` from the service.

## 12.6.0 (2022-03-08)

This version and all future versions will require Python 3.6+. Python 2.7 is no longer supported.

### Stable release of preview features
- Added support for service version 2021-02-12.
- Account level SAS tokens now supports two new permissions:
    - `permanent_delete`
    - `set_immutability_policy`
- Added support for listing system file systems with list_file_systems().

### Bugs Fixed
- Update `azure-core` dependency to avoid inconsistent dependencies from being installed.
- Added all missing Service SAS permissions.

### Other Changes
- Temporarily removed the preview `delete_files()` method on `FileSystemClient`. This feature will be added back
in a future release.

## 12.6.0b2 (2021-12-13)

### Features Added
- Added support for service version 2021-02-12.
- Added support for listing system file systems with list_file_systems().

### Bugs Fixed
- Connection string SAS now works as expected.

## 12.6.0b1 (2021-11-08)
**New features**
- Added support for batch deleting files using the `delete_files()` method from a `FileSystemClient`
- Account level SAS tokens now support two new permissions:
    - `permanent_delete`
    - `set_immutability_policy`
**Fixes**
- `FileSystemProperties` was not subscriptable. Now it is both subscriptable and attributes can also be accessed directly (#20772) 
- Datalake Client Typing annotation issues have been resolved (#19906)

## 12.5.0 (2021-09-15)
**Stable release of preview features**
- Added support for service version 2020-10-02 (STG78)
- Added support for quick query parquet

## 12.5.0b1 (2021-07-27)
**New features**
- Added support for quick query parquet

**Fixes**
- Fixed PathProperties class init issue (#18490)

**Notes**
- Deprecated new_name in for undelete filesystem operation

## 12.4.0 (2021-06-09)
**New features**
- Added support `set_service_properties()`,`get_service_properties()` on `DataLakeServiceClient`
- Added support for `list_deleted_paths()` on `FileSystemClient`

## 12.4.0b1 (2021-05-12)
**New features**
- Added support `set_service_properties()`,`get_service_properties()` on `DataLakeServiceClient`
- Added support for `list_deleted_paths()` on `FileSystemClient`

**Fixes**
- Fixed initiating `PathProperties` problem (#18490)

## 12.3.1 (2021-04-20)
**Fixes**
- Fixed `recursive=True` on file deletion
- Make `AccountName`, `AccountKey` etc. in conn_str case insensitive
- Fixed `downloader.chunks()` return chunks in different size (#9419, #15648)
- Optimized memory usage for datalake file uploads large chunks (#16890)
- Fixed unclosed `ThreadPoolExecutor` (#8955)

**New Features**
- Added `get_account_information()` API

## 12.3.0 (2021-03-01)
**Stable release of preview features**
- Added support for `DatalakeServiceClient.undelete_filesystem()`
- Added support for `DirectoryClient.exists()`, `FileClient.exists()` and `FileSystemClient.exists()`

**Fixes**
- Fixed `DatalakeServiceClient` context manager/session closure issue (#15358)
- `PurePosixPath` is now handled correctly if passed as a path (#16159)

## 12.3.0b1 (2021-02-10)
**New Features**
- Added support for `DatalakeServiceClient.undelete_filesystem()`

**Fixes**
- Fixed `DatalakeServiceClient` context manager/session closure issue (#15358)
- `PurePosixPath` is now handled correctly if passed as a path (#16159)

## 12.2.3 (2021-02-08)
**Fixes**
- Fixed paging issue (#16531)

## 12.2.2 (2021-01-20)
**Fixes**
- Fixed msrest dependency issue (#16250)

## 12.2.1 (2021-01-13)
**New features**
- Added support for `AzureSasCredential` to allow SAS rotation in long living clients.

**Fixes**
- Converted PathProperties.last_modified to datetime format (#16019)

## 12.2.0 (2020-11-10)
**Stable release of preview features**
- Preview feature set/update/remove access control recursively.
- Preview feature `set_file_expiry` on DataLakeFileClient.
- Preview feature generating directory level sas.

**Fixes**
- Fixed session closure of filesystem (#14497)

**Notes**
- Updated dependency `azure-core` from  azure-core<2.0.0,>=1.6.0 to azure-core<2.0.0,>=1.9.0

## 12.2.0b1 (2020-10-02)
**New Features**
- Added support for recursive set/update/remove Access Control on a path and sub-paths.
- Added support for setting an expiry on files where the file gets deleted once it expires.
- Added support to generate directory SAS and added support to specify additional user ids and correlation ids for user delegation SAS.

## 12.1.2 (2020-09-10)
**Fixes**
- Fixed renaming with SAS string (#12057).

## 12.1.1 (2020-08-13)
- Patch release to update the minimum dependency requirement.

## 12.1.0 (2020-08-12)
- Added `query_file` API to enable users to select/project on DataLake file data by providing simple query expressions.

## 12.1.0b1 (2020-07-07)
**New Feature**
- Block size is increased to 4GB at maximum, max single put size is increased to 5GB.

## 12.0.2
**Fixes**
- Improve the performance of upload when using max_concurrency

**Notes**
- Updated dependency from azure-core<2.0.0,>=1.2.2 to azure-core<2.0.0,>=1.6.0

## 12.0.1 (2020-04-29)
**Fixes**
- Fixed rename_directory and rename_file doc
- upload_data didn't support setting umask and permissions.

## 12.0.0 (2020-03-10)
**New Feature**
- Added `set_file_system_access_policy` and `get_file_system_access_policy` APIs on FileSystemClient

**Breaking changes**
- For `generate_file_system_sas`, `generate_directory_sas`, `generate_file_sas` APIs, `account_key` and `user_delegation_key` are merged into one parameter called `credential`.
- Rename `rename_destination` to `new_name` for rename_directory and rename_file APIs
- Rename `read_file` to `download_file`. The return type is changed to `StorageStreamDownloader` with which user can do `readinto()` and `readall()`
- `metadata` is a required parameter for FileSystemClient, DataLakeFileClient and DataLakeDirectoryClient  `set_*_metadata` APIs.

**Notes**
- The `StorageUserAgentPolicy` is now replaced with the `UserAgentPolicy` from azure-core. With this, the custom user agents are now added as a prefix instead of being appended.

## 12.0.0b7 (2020-02-12)
**New Feature**
- Async APIs are supported.

**Fixes**
- Responses are always decoded as UTF8

## 12.0.0b6 (2019-12-04)
- `StorageErrorException` is parsed into more detailed error.
- `etag` and `match_condition` parameters are added as an option('if_match' and 'if_none_match' are still supported).
- ADLS Gen1 to Gen2 API Mapping is available.
- All the clients now have a `close()` method to close the sockets opened by the client

## 12.0.0b5 (2019-11-06)
- Initial Release. Please see the README for information on the new design.
- Support for Azure Data Lake Storage REST APIs.
- Support for DataLakeServiceClient: create file system, delete file system, get file systems, and get user delegation key
- Support for DataLakeLeaseClient: acquire, renew, release, change, and break lease
- Support for FileSystemClient: create, delete, get properties, set metadata, get paths, create directory, delete directory, create file, delete file
- Support for DataLakeDirectoryClient: create, delete, rename, get properties, get access control, set metadata, set properties, set access control, create file, delete file, create sub-directory, delete sub-directory
- Support for DataLakeFileClient: create, delete, rename, get properties, get access control, set metadata, set properties, set access control, append, flush, read

This package's
[documentation](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-datalake/README.md)
and
[samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-datalake/samples)
