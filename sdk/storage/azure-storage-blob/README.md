# Azure Storage Blobs client library for Python
Azure Blob storage is Microsoft's object storage solution for the cloud. Blob storage is optimized for storing massive amounts of unstructured data, such as text or binary data.

Blob storage is ideal for:

* Serving images or documents directly to a browser
* Storing files for distributed access
* Streaming video and audio
* Storing data for backup and restore, disaster recovery, and archiving
* Storing data for analysis by an on-premises or Azure-hosted service

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob/azure/storage/blob) | [Package (PyPi)](https://pypi.org/project/azure-storage-blob/) | [API reference documentation](https://docs.microsoft.com/rest/api/storageservices/blob-service-rest-api) | [Product documentation](https://docs.microsoft.com/azure/storage/) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob/tests)


## Getting started

### Install the package
Install the Azure Storage Blobs client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-storage-blob
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
### Downloading a blob
Download a blob from your container.

```python
from azure.storage.blob import BlobClient

blob = BlobClient.from_connection_string("my_connection_string", container="mycontainer", blob="my_blob")

with open("./BlockDestination.txt", "wb") as my_blob:
    blob_data = blob.download_blob()
    my_blob.writelines(blob_data.content_as_bytes())
```

### Enumerating blobs
List the blob in your container.

```python
from azure.storage.blob import ContainerClient

container = ContainerClient.from_connection_string("my_connection_string", container="mycontainer")

blob_list = container.list_blobs()
for blob in blob_list:
    print(blob.name + '\n')
```

## Troubleshooting
Storage Blob clients raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/exceptions.md).

All Blob service operations will throw a StorageErrorException on failure with helpful [error codes](https://docs.microsoft.com/rest/api/storageservices/blob-service-error-codes).

## Next steps

### More sample code

Get started with our [Blob samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob/tests).

Several Storage Blobs Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Storage Blobs:

* [`test_blob_samples_hello_world.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob/tests/test_blob_samples_hello_world.py) - Examples for common Storage Blob tasks:
    * Set up a container
    * Create a block, page, or append blob
    * Upload blobs
    * Download blobs
    * Delete blobs

* [`test_blob_samples_authentication.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob/tests/test_blob_samples_authentication.py) - Examples for authenticating and creating the client:
    * From a connection string
    * From a shared access key
    * From a shared access signature token
    * From active directory
    
* [`test_blob_samples_service.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob/tests/test_blob_samples_service.py) - Examples for interacting with the blob service:
    * Get account information
    * Get and set service properties
    * Get service statistics
    * Create, list, and delete containers
    * Get the Blob or Container client

* [`test_blob_samples_containers.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob/tests/test_blob_samples_containers.py) - Examples for interacting with containers:
    * Create a container and delete containers
    * Set metadata on containers
    * Get container properties
    * Acquire a lease on container
    * Set an access policy on a container
    * Upload, list, delete blobs in container
    * Get the blob client to interact with a specific blob

* [`test_blob_samples_common.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob/tests/test_blob_samples_common.py) - Examples common to all types of blobs:
    * Create a snapshot
    * Delete a blob snapshot
    * Soft delete a blob
    * Undelete a blob
    * Acquire a lease on a blob


### Additional documentation

For more extensive documentation on the Azure Storage Blobs, see the [Azure Storage Blobs documentation](https://docs.microsoft.com/azure/storage/) on docs.microsoft.com.


## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
