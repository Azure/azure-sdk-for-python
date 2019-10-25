# Azure Storage Files client library for Python
Azure File storage offers fully managed file shares in the cloud that are accessible via the industry standard [Server Message Block (SMB) protocol](https://docs.microsoft.com/windows/desktop/FileIO/microsoft-smb-protocol-and-cifs-protocol-overview). Azure file shares can be mounted concurrently by cloud or on-premises deployments of Windows, Linux, and macOS. Additionally, Azure file shares can be cached on Windows Servers with Azure File Sync for fast access near where the data is being used.

Azure file shares can be used to:

* Replace or supplement on-premises file servers
* "Lift and shift" applications
* Simplify cloud development with shared application settings, diagnostic share, and Dev/Test/Debug tools

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/azure/storage/file) | [Package (PyPI)](https://pypi.org/project/azure-storage-file/) | [API reference documentation](https://docs.microsoft.com/en-us/python/api/azure-storage-file/azure.storage.file) | [Product documentation](https://docs.microsoft.com/azure/storage/) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples)

## Getting started

### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure storage account](https://docs.microsoft.com/azure/storage/common/storage-account-overview) to use this package.

### Install the package
Install the Azure Storage Files client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-storage-file --pre
```

### Create a storage account
If you wish to create a new storage account, you can use the
[Azure Portal](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-portal),
[Azure PowerShell](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-powershell),
or [Azure CLI](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-cli):

```bash
# Create a new resource group to hold the storage account -
# if using an existing resource group, skip this step
az group create --name my-resource-group --location westus2

# Create the storage account
az storage account create -n my-storage-account-name -g my-resource-group
```

### Create the client
The Azure Storage Files client library for Python allows you to interact with four types of resources: the storage
account itself, file shares, directories, and files. Interaction with these resources starts with an instance of a
[client](#clients). To create a client object, you will need the storage account's file service endpoint URL and a
credential that allows you to access the storage account:

```python
from azure.storage.file import FileServiceClient

service = FileServiceClient(account_url="https://<my-storage-account-name>.file.core.windows.net/", credential=credential)
```

#### Looking up the endpoint URL
You can find the storage account's file service endpoint URL using the
[Azure Portal](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview#storage-account-endpoints),
[Azure PowerShell](https://docs.microsoft.com/en-us/powershell/module/az.storage/get-azstorageaccount),
or [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/storage/account?view=azure-cli-latest#az-storage-account-show):

```bash
# Get the file service endpoint for the storage account
az storage account show -n my-storage-account-name -g my-resource-group --query "primaryEndpoints.file"
```

#### Types of credentials
The `credential` parameter may be provided in a number of different forms, depending on the type of
[authorization](https://docs.microsoft.com/en-us/azure/storage/common/storage-auth) you wish to use:
1. To use a [shared access signature (SAS) token](https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview),
   provide the token as a string. If your account URL includes the SAS token, omit the credential parameter.
2. To use a storage account [shared access key](https://docs.microsoft.com/rest/api/storageservices/authenticate-with-shared-key/),
   provide the key as a string.

#### Creating the client from a connection string
Depending on your use case and authorization method, you may prefer to initialize a client instance with a storage
connection string instead of providing the account URL and credential separately. To do this, pass the storage
connection string to the client's `from_connection_string` class method:

```python
from azure.storage.file import FileServiceClient

service = FileServiceClient.from_connection_string(conn_str="my_connection_string")
```

## Key concepts
The following components make up the Azure File Service:
* The storage account itself
* A file share within the storage account
* An optional hierarchy of directories within the file share
* A file within the file share, which may be up to 1 TiB in size

The Azure Storage Files client library for Python allows you to interact with each of these components through the
use of a dedicated client object.

### Clients
Four different clients are provided to to interact with the various components of the File Service:
1. **[FileServiceClient](https://docs.microsoft.com/en-us/python/api/azure-storage-file/azure.storage.file.fileserviceclient)** -
    this client represents interaction with the Azure storage account itself, and allows you to acquire preconfigured
    client instances to access the file shares within. It provides operations to retrieve and configure the service
    properties as well as list, create, and delete shares within the account. To perform operations on a specific share,
    retrieve a client using the `get_share_client` method.
2. **[ShareClient](https://docs.microsoft.com/en-us/python/api/azure-storage-file/azure.storage.file.shareclient)** -
    this client represents interaction with a specific file share (which need not exist yet), and allows you to acquire
    preconfigured client instances to access the directories and files within. It provides operations to create, delete,
    configure, or create snapshots of a share and includes operations to create and enumerate the contents of
    directories within it. To perform operations on a specific directory or file, retrieve a client using the
    `get_directory_client` or `get_file_client` methods.
3. **[DirectoryClient](https://docs.microsoft.com/en-us/python/api/azure-storage-file/azure.storage.file.directoryclient)** -
    this client represents interaction with a specific directory (which need not exist yet). It provides operations to
    create, delete, or enumerate the contents of an immediate or nested subdirectory, and includes operations to create
    and delete files within it. For operations relating to a specific subdirectory or file, a client for that entity can
    also be retrieved using the `get_subdirectory_client` and `get_file_client` functions.
4. **[FileClient](https://docs.microsoft.com/en-us/python/api/azure-storage-file/azure.storage.file.fileclient)** -
    this client represents interaction with a specific file (which need not exist yet). It provides operations to
    upload, download, create, delete, and copy a file.

For details on path naming restrictions, see [Naming and Referencing Shares, Directories, Files, and Metadata](https://docs.microsoft.com/rest/api/storageservices/naming-and-referencing-shares--directories--files--and-metadata).

## Examples
The following sections provide several code snippets covering some of the most common Storage File tasks, including:

* [Creating a file share](#creating-a-file-share)
* [Uploading a file](#uploading-a-file)
* [Downloading a file](#downloading-a-file)
* [Listing contents of a directory](#listing-contents-of-a-directory)

### Creating a file share
Create a file share to store your files

```python
from azure.storage.file import ShareClient

share = ShareClient.from_connection_string(conn_str="my_connection_string", share_name="my_share")
share.create_share()
```

Use the async client to create a file share

```python
from azure.storage.file.aio import ShareClient

share = ShareClient.from_connection_string(conn_str="my_connection_string", share_name="my_share")
await share.create_share()
```

### Uploading a file
Upload a file to the share

```python
from azure.storage.file import FileClient

file_client = FileClient.from_connection_string(conn_str="my_connection_string", share_name="my_share", file_path="my_file")

with open("./SampleSource.txt", "rb") as source_file:
    file_client.upload_file(source_file)
```

Upload a file asynchronously

```python
from azure.storage.file.aio import FileClient

file_client = FileClient.from_connection_string(conn_str="my_connection_string", share_name="my_share", file_path="my_file")

with open("./SampleSource.txt", "rb") as source_file:
    await file_client.upload_file(source_file)
```

### Downloading a file
Download a file from the share

```python
from azure.storage.file import FileClient

file_client = FileClient.from_connection_string(conn_str="my_connection_string", share_name="my_share", file_path="my_file")

with open("DEST_FILE", "wb") as file_handle:
    data = file_client.download_file()
    data.readinto(file_handle)
```

Download a file asynchronously

```python
from azure.storage.file.aio import FileClient

file_client = FileClient.from_connection_string(conn_str="my_connection_string", share_name="my_share", file_path="my_file")

with open("DEST_FILE", "wb") as file_handle:
    data = await file_client.download_file()
    await data.readinto(file_handle)
```

### Listing contents of a directory
List all directories and files under a parent directory

```python
from azure.storage.file import DirectoryClient

parent_dir = DirectoryClient.from_connection_string(conn_str="my_connection_string", share_name="my_share", directory_path="parent_dir")

my_list = list(parent_dir.list_directories_and_files())
print(my_list)
```

List contents of a directory asynchronously

```python
from azure.storage.file.aio import DirectoryClient

parent_dir = DirectoryClient.from_connection_string(conn_str="my_connection_string", share_name="my_share", directory_path="parent_dir")

my_files = []
async for item in parent_dir.list_directories_and_files():
    my_files.append(item)
print(my_files)
```

## Troubleshooting
Storage File clients raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/exceptions.md).
All File service operations will throw a `StorageErrorException` on failure with helpful [error codes](https://docs.microsoft.com/rest/api/storageservices/file-service-error-codes).

## Next steps

### More sample code

Get started with our [File samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples).

Several Storage File Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Storage File:

* [`file_samples_hello_world.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples/file_samples_hello_world.py)([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples/file_samples_hello_world_async.py)) - Examples found in this article:
    * Client creation
    * Create a file share
    * Upload a file

* [`file_samples_authentication.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples/file_samples_authentication.py)([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples/file_samples_authentication_async.py)) - Examples for authenticating and creating the client:
    * From a connection string
    * From a shared access key
    * From a shared access signature token

* [`file_samples_service.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples/file_samples_service.py)([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples/file_samples_service_async.py)) - Examples for interacting with the file service:
    * Get and set service properties
    * Create, list, and delete shares
    * Get a share client

* [`file_samples_share.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples/file_samples_share.py)([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples/file_samples_share_async.py)) - Examples for interacting with file shares:
    * Create a share snapshot
    * Set share quota and metadata
    * List directories and files
    * Get the directory or file client to interact with a specific entity

* [`file_samples_directory.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples/file_samples_directory.py)([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples/file_samples_directory_async.py)) - Examples for interacting with directories:
    * Create a directory and add files
    * Create and delete subdirectories
    * Get the subdirectory client

* [`file_samples_client.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples/file_samples_client.py)([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file/samples/file_samples_client_async.py)) - Examples for interacting with files:
    * Create, upload, download, and delete files
    * Copy a file from a URL

### Additional documentation
For more extensive documentation on Azure File storage, see the [Azure File storage documentation](https://docs.microsoft.com/en-us/azure/storage/files/) on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
