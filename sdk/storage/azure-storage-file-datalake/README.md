# Azure Storage Blobs client library for Python
Overview

This preview package for Python includes ADLS Gen2 specific API support made available in Blob SDK. This includes:
1. New directory level operations (Create, Rename/Move, Delete) for both hierarchical namespace enabled (HNS) storage accounts and HNS disabled storage accounts. For HNS enabled accounts, the rename/move operations are atomic.
    (the current SDK only supports HNS operations)
2. Permission related operations (Get/Set ACLs) for hierarchical namespace enabled (HNS) accounts.


[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file-datalake/azure/storage/file/datalake) | [Package (PyPi)](https://pypi.org/project/azure-storage-file-datalake/) | [API reference documentation](https://azure.github.io/azure-sdk-for-python/ref/azure.storage.blob.html) | [Product documentation](https://docs.microsoft.com/azure/storage/) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob/tests)


## Getting started

### Install the package
Install the Azure Storage Blobs client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-storage-blob --pre
```
*Requires Python 2.7, 3.5 or later to use this package.

**Prerequisites**: You must have an [Azure subscription](https://azure.microsoft.com/free/), and a
[Storage Account](https://docs.microsoft.com/azure/storage/common/storage-account-overview) to use this package.

To create a Storage Account, you can use the [Azure Portal](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-portal),
[Azure PowerShell](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-powershell) or [Azure CLI](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-cli):

If you need to create a new resource group:

```bash
az group create --name my-resource-group --location westus2
```

Create your storage account:

```bash
az storage account create -n mystorageaccountname -g my-resource-group
```


### Authenticate the client

Interaction with Storage Blobs starts with an instance of the BlobServiceClient class. You need an existing storage account, its URL, and a credential to instantiate the client object.

#### Get credentials

To authenticate the client you have a few options:
1. Use a SAS token string 
2. Use an account shared access key
3. Use a token credential from [azure.identity](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity)

Alternatively, you can authenticate with a storage connection string using the `from_connection_string` method. See example: [Client creation with a connection string](#client-creation-with-a-connection-string).

You can omit the credential if your account URL already has a SAS token.

#### Create client

Once you have your account URL and credentials ready, you can create the BlobServiceClient:

```python
from azure.storage.blob import BlobServiceClient

service = BlobServiceClient(account_url="https://<my-storage-account-name>.blob.core.windows.net/", credential=credential)
```

## Key concepts

Blob storage offers three types of resources:
* The storage account
* A container in the storage account
* A blob in a container

#### Clients

The Storage Blobs SDK provides four different clients to interact with the Blob Service:
1. **BlobServiceClient** - this client interacts with the Blob Service at the account level. 
    It provides operations to retrieve and configure the account properties
    as well as list, create, and delete containers within the account.
    For operations relating to a specific container or blob, clients for those entities
    can also be retrieved using the `get_blob_client` or `get_container_client` functions.
2. **ContainerClient** - this client represents interaction with a specific
    container, although that container need not exist yet. It provides operations to create, delete, or
    configure containers and includes operations to list, upload, and delete blobs in the container.
    For operations relating to a specific blob, the client can also be retrieved using
    the `get_blob_client` function.
3. **BlobClient** - this client represents interaction with a specific
    blob, although that blob need not exist yet. It provides blob operations to upload, download, delete, 
    create snapshots, and list blobs, as well as specific operations per blob type.
4. **LeaseClient** - this client represents lease interactions with a ContainerClient or BlobClient.
    It provides operations to acquire, renew, release, change, and break leases on the resources.

#### Blob Types

Once you've initialized a Client, you can choose from the different types of blobs:
* **Block blobs** store text and binary data, up to about 4.7 TB. Block blobs are made up of blocks of data that can be managed individually
* **Append blobs** are made up of blocks like block blobs, but are optimized for append operations. Append blobs are ideal for scenarios such as logging data from virtual machines
* **Page blobs** store random access files up to 8 TB in size. Page blobs store virtual hard drive (VHD) files and serve as disks for Azure virtual machines

For more information about the different types of blobs, see [Understanding Block Blobs, Append Blobs, and Page Blobs](https://docs.microsoft.com/rest/api/storageservices/understanding-block-blobs--append-blobs--and-page-blobs)


## Examples

The following sections provide several code snippets covering some of the most common Storage Blob tasks, including:

* [Client creation with a connection string](#client-creation-with-a-connection-string)
* [Uploading a blob](#uploading-a-blob)
* [Downloading a blob](#downloading-a-blob)
* [Enumerating blobs](#enumerating-blobs)


### Client creation with a connection string
Create the BlobServiceClient using the connection string to your Azure Storage account.

```python
from azure.storage.blob import BlobServiceClient

service = BlobServiceClient.from_connection_string(conn_str="my_connection_string")
```

### Uploading a blob
Upload a blob to your container.

```python
from azure.storage.blob import BlobClient

blob = BlobClient.from_connection_string("my_connection_string", container="mycontainer", blob="my_blob")

with open("./SampleSource.txt", "rb") as data:
    blob.upload_blob(data)
```
Use the async client to upload a blob to your container.

```python
from azure.storage.blob.aio import BlobClient

blob = BlobClient.from_connection_string("my_connection_string", container="mycontainer", blob="my_blob")

with open("./SampleSource.txt", "rb") as data:
    await blob.upload_blob(data)
```

### Downloading a blob
Download a blob from your container.

```python
from azure.storage.blob import BlobClient

blob = BlobClient.from_connection_string("my_connection_string", container="mycontainer", blob="my_blob")

with open("./BlockDestination.txt", "wb") as my_blob:
    blob_data = blob.download_blob()
    my_blob.writelines(blob_data.readall())
```

Download a blob asynchronously.

```python
from azure.storage.blob.aio import BlobClient

blob = BlobClient.from_connection_string("my_connection_string", container="mycontainer", blob="my_blob")

with open("./BlockDestination.txt", "wb") as my_blob:
    stream = await blob.download_blob()
    data = await stream.readall()
    my_blob.write(data)
```

### Enumerating blobs
List the blobs in your container.

```python
from azure.storage.blob import ContainerClient

container = ContainerClient.from_connection_string("my_connection_string", container="mycontainer")

blob_list = container.list_blobs()
for blob in blob_list:
    print(blob.name + '\n')
```

List the blobs asynchronously.

```python
from azure.storage.blob.aio import ContainerClient

container = ContainerClient.from_connection_string("my_connection_string", container="mycontainer")

blob_list = [] 
async for blob in container.list_blobs():
    blob_list.append(blob)
print(blob_list)
```

## Troubleshooting
Storage Blob clients raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/exceptions.md).

All Blob service operations will throw a StorageErrorException on failure with helpful [error codes](https://docs.microsoft.com/rest/api/storageservices/blob-service-error-codes).

## Next steps

### More sample code

Get started with our [Azure DataLake samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file-datalake/tests).

Several Storage Blobs Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Storage Blobs:

* [`datalake_samples_access_control.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file-datalake/samples/datalake_samples_access_control.py) - Examples for common Storage Blob tasks:
    * Set up a file system
    * Create a directory
    * Set/Get access control for the directory
    * Create files under the directory
    * Set/Get access control for each file
    * Delete file system

* [`datalake_samples_upload_download.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file-datalake/samples/datalake_samples_upload_download.py) - Examples for authenticating and creating the client:
    * Set up a file system
    * Create dile
    * Append data to the file
    * Flush data to the file
    * Download the uploaded data
    * Delete file system


### Additional documentation

For more extensive REST documentation on Data Lake Storage Gen2, see the [Data Lake Storage Gen2 documentation](https://docs.microsoft.com/en-us/rest/api/storageservices/datalakestoragegen2/filesystem) on docs.microsoft.com.


## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
