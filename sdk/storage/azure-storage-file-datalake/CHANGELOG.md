# Release History

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
[documentation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file-datalake/README.md)
and
[samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file-datalake/samples)
