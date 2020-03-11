# Release History

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
