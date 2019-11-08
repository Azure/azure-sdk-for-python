# Change Log azure-storage-file-datalake

## Version 12.0.0b5 (2019-11-06)
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
