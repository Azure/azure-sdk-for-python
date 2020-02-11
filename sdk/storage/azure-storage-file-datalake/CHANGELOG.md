# Release History

## 12.0.0b7 (Unreleased)
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
