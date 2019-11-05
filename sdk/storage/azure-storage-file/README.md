# Azure Storage File client library for Python
Azure File offers fully managed file shares in the cloud that are accessible via the industry standard [Server Message Block (SMB) protocol](https://docs.microsoft.com/windows/desktop/FileIO/microsoft-smb-protocol-and-cifs-protocol-overview). Azure file shares can be mounted concurrently by cloud or on-premises deployments of Windows, Linux, and macOS. Additionally, Azure file shares can be cached on Windows Servers with Azure File Sync for fast access near where the data is being used.

Azure file shares can be used to:

* Replace or supplement on-premises file servers
* "Lift and shift" applications
* Simplify cloud development with shared application settings, diagnostic share, and Dev/Test/Debug tools

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/azure/storage/file) | [Package (PyPi)](https://pypi.org/project/azure-storage-file/) | [API reference documentation](https://docs.microsoft.com/rest/api/storageservices/file-service-rest-api) | [Product documentation](https://docs.microsoft.com/azure/storage/) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests)

## Getting started

### Install the package
Install the Azure Storage File client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-storage-file --pre
```

**Prerequisites**: You must have an [Azure subscription](https://azure.microsoft.com/free/), and a
[Storage Account](https://docs.microsoft.com/azure/storage/common/storage-account-overview) to use this package.

To create a Storage Account, you can use the [Azure Portal](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-portal),
[Azure PowerShell](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-powershell) or [Azure CLI](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-cli):

```bash
az storage account create -n MyStorageAccountName -g MyResourceGroupName
```

Requires Python 2.7, 3.5 or later to use this package.

### Authenticate the client

Interaction with Storage File starts with an instance of the FileServiceClient class. You need an existing storage account, its URL, and a credential to instantiate the client object.

#### Get credentials

To authenticate the client you have a few options:
1. Use a SAS token string 
2. Use an account shared access key

Alternatively, you can authenticate with a storage connection string using the `from_connection_string` method. See example: [Client creation with a connection string](#client-creation-with-a-connection-string).

You can omit the credential if your account URL already has a SAS token.

#### Create client

Once you have your account URL and credentials ready, you can create the FileServiceClient:

```python
from azure.storage.file import FileServiceClient

service = FileServiceClient(account_url="https://<my-storage-account-name>.file.core.windows.net/", credential=credential)
```

## Key concepts

File storage includes the following concepts:
* The storage account
* A file storage share
* An optional hierarchy of directories
* A file in the share which may be up to 1 TiB in size

#### Clients

The Storage File SDK provides four different clients to interact with the File Service:
1. **FileServiceClient** - this client interacts with the File Service at the account level. 
    It provides operations to retrieve and configure the service properties
    as well as list, create, and delete shares within the storage account.
    For operations relating to a specific share, a client for that entity
    can also be retrieved using the `get_share_client` function.
2. **ShareClient** - this client represents interaction with a specific
    file share, although that share need not exist yet. It provides operations to create, delete, or
    configure shares and includes operations to list and create files or directories.
    For operations relating to a specific directory or file, those clients can also be retrieved using
    the `get_directory_client` or `get_file_client` functions.
3. **DirectoryClient** - this client represents interaction with a specific
    directory, although that directory need not exist yet. It provides operations to create, delete, and list 
    directories and subdirectories, as well as create and delete files in the directory. For operations 
    relating to a specific subdirectory or file, a client for that entity can also be retrieved using
    the `get_subdirectory_client` and `get_file_client` functions.
4. **FileClient** - this client represents interaction with a specific file, although the file need not
    exist yet. It provides operations to create, upload, copy, and download files as well as more advanced
    operations.

For details on path naming restrictions, see [Naming and Referencing Shares, Directories, Files, and Metadata](https://docs.microsoft.com/rest/api/storageservices/naming-and-referencing-shares--directories--files--and-metadata).

## Examples

The following sections provide several code snippets covering some of the most common Storage File tasks, including:

* [Client creation with a connection string](#client-creation-with-a-connection-string)
* [Create a file share](#create-a-file-share)
* [Upload a file](#upload-a-file)


### Client creation with a connection string
Create the FileServiceClient using the connection string to your Azure Storage account.

```python
from azure.storage.file import FileServiceClient

service = FileServiceClient.from_connection_string("my_connection_string")
```

### Create a file share
Create a file share to store your files.

```python
from azure.storage.file import ShareClient

share = ShareClient.from_connection_string("my_connection_string", share_name="myshare")
share.create_share()
```

### Upload a file
Upload a file to the share

```python
from azure.storage.file import FileClient

file_client = FileClient.from_connection_string("my_connection_string", share_name="share", file_path="myfile")

with open("./SampleSource.txt", "rb") as source_file:
    file_client.upload_file(source_file)
```

### Download a file
Download a file to the share

```python
from azure.storage.file import FileClient

file_client = FileClient.from_connection_string("my_connection_string", share_name="share", file_path="myfile")

with open("DEST_FILE", "wb") as file_handle:
    data = file_client.download_file()
    data.readinto(file_handle)
```

### List contents of a directory.
Lists all the directories and files under the directory.

```python
from azure.storage.file import ShareClient
share = ShareClient.from_connection_string(self.connection_string, "subdirshare")
parent_dir = share.get_directory_client(directory_path="parentdir")

my_list = list(parent_dir.list_directories_and_files())
print(my_list)
```

### Client creation with a connection string
Create the FileServiceClient using the connection string to your Azure Storage account.

```python
from azure.storage.file.aio import FileServiceClient

service = FileServiceClient.from_connection_string("my_connection_string")
```

### Create a file share asynchronously
Create a file share to store your files.

```python
from azure.storage.file.aio import ShareClient

share = ShareClient.from_connection_string("my_connection_string", share_name="myshare")
await share.create_share()
```

### Upload a file asynchronously
Upload a file to the share

```python
from azure.storage.file.aio import FileClient

file_client = FileClient.from_connection_string("my_connection_string", share_name="share", file_path="myfile")

with open("./SampleSource.txt", "rb") as source_file:
    await file_client.upload_file(source_file)
```

### Download a file asynchronously
Download a file to the share

```python
from azure.storage.file.aio import FileClient

file_client = FileClient.from_connection_string("my_connection_string", share_name="share", file_path="myfile")

with open("DEST_FILE", "wb") as file_handle:
    data = await file_client.download_file()
    await data.readinto(file_handle)
```

### List contents of a directory asynchronously
Lists all the directories and files under the directory.

```python
from azure.storage.file import ShareClient
share = ShareClient.from_connection_string(self.connection_string, "subdirshare")
parent_dir = share.get_directory_client(directory_path="parentdir")

my_files = []
async for item in parent_dir.list_directories_and_files():
    my_files.append(item)
print(my_files)
```

## Troubleshooting
Storage File clients raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/exceptions.md).

All File service operations will throw a StorageErrorException on failure with helpful [error codes](https://docs.microsoft.com/rest/api/storageservices/file-service-error-codes).

## Next steps
### More sample code

Get started with our [File samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests).

Several Storage File Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Storage File:

* [`test_file_samples_hello_world.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests/test_file_samples_hello_world.py)([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests/test_file_samples_hello_world_async.py)) - Examples found in this article:
    * Client creation
    * Create a file share
    * Upload a file

* [`test_file_samples_authentication.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests/test_file_samples_authentication.py)([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests/test_file_samples_authentication_async.py)) - Examples for authenticating and creating the client:
    * From a connection string
    * From a shared access key
    * From a shared access signature token

* [`test_file_samples_service.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests/test_file_samples_service.py)([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests/test_file_samples_service_async.py)) - Examples for interacting with the file service:
    * Get and set service properties
    * Create, list, and delete shares
    * Get a share client

* [`test_file_samples_share.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests/test_file_samples_share.py)([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests/test_file_samples_share_async.py)) - Examples for interacting with file shares:
    * Create a share snapshot
    * Set share quota and metadata
    * List directories and files
    * Get the directory or file client to interact with a specific entity

* [`test_file_samples_directory.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests/test_file_samples_directory.py)([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests/test_file_samples_directory_async.py)) - Examples for interacting with directories:
    * Create a directory and add files
    * Create and delete subdirectories
    * Get the subdirectory client

* [`test_file_samples_file.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests/test_file_samples_file.py)([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/tests/test_file_samples_file_async.py)) - Examples for interacting with files:
    * Create, upload, download, and delete files
    * Copy a file from a URL

### Additional documentation

For more extensive documentation on the Azure Storage File, see the [Azure Storage File documentation](https://azure.github.io/azure-sdk-for-python/ref/azure.storage.file) on docs.microsoft.com.


## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
