# Azure DataLake service client library for Python
Overview

This preview package for Python includes ADLS Gen2 specific API support made available in Storage SDK. This includes:
1. New directory level operations (Create, Rename, Delete) for hierarchical namespace enabled (HNS) storage account. For HNS enabled accounts, the rename/move operations are atomic.
2. Permission related operations (Get/Set ACLs) for hierarchical namespace enabled (HNS) accounts.


[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file-datalake/azure/storage/filedatalake) | [Package (PyPi)](https://pypi.org/project/azure-storage-file-datalake/) | [API reference documentation](https://aka.ms/azsdk-python-storage-filedatalake-ref) | [Product documentation](https://docs.microsoft.com/azure/storage/) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file-datalake/samples)


## Getting started

### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure storage account](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-quickstart-create-account) to use this package.

### Install the package
Install the Azure DataLake Storage client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-storage-file-datalake --pre
```

### Create a storage account
If you wish to create a new storage account, you can use the
[Azure Portal](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-quickstart-create-account#create-an-account-using-the-azure-portal),
[Azure PowerShell](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-quickstart-create-account#create-an-account-using-powershell),
or [Azure CLI](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-quickstart-create-account#create-an-account-using-azure-cli):

```bash
# Create a new resource group to hold the storage account -
# if using an existing resource group, skip this step
az group create --name my-resource-group --location westus2

# Create the storage account
az storage account create -n my-storage-account-name -g my-resource-group --hierarchical-namespace true
```

### Authenticate the client

Interaction with DataLake Storage starts with an instance of the DataLakeServiceClient class. You need an existing storage account, its URL, and a credential to instantiate the client object.

#### Get credentials

To authenticate the client you have a few options:
1. Use a SAS token string 
2. Use an account shared access key
3. Use a token credential from [azure.identity](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity)

Alternatively, you can authenticate with a storage connection string using the `from_connection_string` method. See example: [Client creation with a connection string](#client-creation-with-a-connection-string).

You can omit the credential if your account URL already has a SAS token.

#### Create client

Once you have your account URL and credentials ready, you can create the DataLakeServiceClient:

```python
from azure.storage.filedatalake import DataLakeServiceClient

service = DataLakeServiceClient(account_url="https://<my-storage-account-name>.dfs.core.windows.net/", credential=credential)
```

## Key concepts

DataLake storage offers four types of resources:
* The storage account
* A file system in the storage account
* A directory under the file system
* A file in a the file system or under directory

#### Clients

The DataLake Storage SDK provides four different clients to interact with the DataLake Service:
1. **DataLakeServiceClient** - this client interacts with the DataLake Service at the account level. 
    It provides operations to retrieve and configure the account properties
    as well as list, create, and delete file systems within the account.
    For operations relating to a specific file system, directory or file, clients for those entities
    can also be retrieved using the `get_file_client`, `get_directory_client` or `get_file_system_client` functions.
2. **FileSystemClient** - this client represents interaction with a specific
    file system, even if that file system does not exist yet. It provides operations to create, delete, or
    configure file systems and includes operations to list paths under file system, upload, and delete file or
    directory in the file system.  
    For operations relating to a specific file, the client can also be retrieved using
    the `get_file_client` function.  
    For operations relating to a specific directory, the client can be retrieved using 
    the `get_directory_client` function.  
3. **DataLakeDirectoryClient** - this client represents interaction with a specific
    directory, even if that directory does not exist yet. It provides directory operations create, delete, rename,
    get properties and set properties operations.
3. **DataLakeFileClient** - this client represents interaction with a specific
    file, even if that file does not exist yet. It provides file operations to append data, flush data, delete, 
    create, and read file.
4. **DataLakeLeaseClient** - this client represents lease interactions with a FileSystemClient, DataLakeDirectoryClient
    or DataLakeFileClient. It provides operations to acquire, renew, release, change, and break leases on the resources.

## Examples

The following sections provide several code snippets covering some of the most common Storage DataLake tasks, including:

* [Client creation with a connection string](#client-creation-with-a-connection-string)
* [Uploading a file](#uploading-a-file)
* [Downloading a file](#downloading-a-file)
* [Enumerating paths](#enumerating-paths)


### Client creation with a connection string
Create the DataLakeServiceClient using the connection string to your Azure Storage account.

```python
from azure.storage.filedatalake import DataLakeServiceClient

service = DataLakeServiceClient.from_connection_string(conn_str="my_connection_string")
```

### Uploading a file
Upload a file to your file system.

```python
from azure.storage.filedatalake import DataLakeFileClient

data = b"abc"
file = DataLakeFileClient.from_connection_string("my_connection_string", 
                                                 file_system_name="myfilesystem", file_path="myfile")

file.append_data(data, offset=0, length=len(data))
file.flush_data(len(data))
```

### Downloading a file
Download a file from your file system.

```python
from azure.storage.filedatalake import DataLakeFileClient

file = DataLakeFileClient.from_connection_string("my_connection_string", 
                                                 file_system_name="myfilesystem", file_path="myfile")

with open("./BlockDestination.txt", "wb") as my_file:
    download = file.download_file()
    download.readinto(my_file)
```

### Enumerating paths
List the paths in your file system.

```python
from azure.storage.filedatalake import FileSystemClient

file_system = FileSystemClient.from_connection_string("my_connection_string", file_system_name="myfilesystem")

paths = file_system.get_paths()
for path in paths:
    print(path.name + '\n')
```

## Troubleshooting
### General
DataLake Storage clients raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md).

All DataLake service operations will throw a StorageErrorException on failure with helpful [error codes](https://docs.microsoft.com/rest/api/storageservices/blob-service-error-codes).

### Logging
This library uses the standard
[logging](https://docs.python.org/3/library/logging.html) library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument:
```python
import sys
import logging
from azure.storage.filedatalake import DataLakeServiceClient

# Create a logger for the 'azure.storage.filedatalake' SDK
logger = logging.getLogger('azure.storage')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# This client will log detailed information about its HTTP sessions, at DEBUG level
service_client = DataLakeServiceClient.from_connection_string("your_connection_string", logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```py
service_client.list_file_systems(logging_enable=True)
```

## Next steps

### More sample code

Get started with our [Azure DataLake samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file-datalake/samples).

Several DataLake Storage Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with DataLake Storage:

* [`datalake_samples_access_control.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file-datalake/samples/datalake_samples_access_control.py) - Examples for common DataLake Storage tasks:
    * Set up a file system
    * Create a directory
    * Set/Get access control for the directory
    * Create files under the directory
    * Set/Get access control for each file
    * Delete file system

* [`datalake_samples_upload_download.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-file-datalake/samples/datalake_samples_upload_download.py) - Examples for common DataLake Storage tasks:
    * Set up a file system
    * Create file
    * Append data to the file
    * Flush data to the file
    * Download the uploaded data
    * Delete file system


### Additional documentation

Table for [ADLS Gen1 to ADLS Gen2 API Mapping](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/storage/azure-storage-file-datalake/GEN1_GEN2_MAPPING.md)  
For more extensive REST documentation on Data Lake Storage Gen2, see the [Data Lake Storage Gen2 documentation](https://docs.microsoft.com/en-us/rest/api/storageservices/datalakestoragegen2/filesystem) on docs.microsoft.com.


## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
