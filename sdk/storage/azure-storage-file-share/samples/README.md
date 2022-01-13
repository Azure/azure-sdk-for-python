---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-storage
urlFragment: storage-file-share-samples
---

# Azure Storage File Share client library for Python Samples

These are code samples that show common scenario operations with the Azure Storage File Share client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations
with file shares.

* [file_samples_hello_world.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share/samples/file_samples_hello_world.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share/samples/file_samples_hello_world_async.py)) - Examples for getting started with file shares:
    * Client creation
    * Create a file share
    * Upload a file

* [file_samples_authentication.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share/samples/file_samples_authentication.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share/samples/file_samples_authentication_async.py)) - Examples for authenticating and creating the client:
    * From a connection string
    * From a shared access key
    * From a shared access signature token

* [file_samples_service.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share/samples/file_samples_service.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share/samples/file_samples_service_async.py)) - Examples for interacting with the file service:
    * Get and set service properties
    * Create, list, and delete shares
    * Get a share client

* [file_samples_share.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share/samples/file_samples_share.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share/samples/file_samples_share_async.py)) - Examples for interacting with file shares:
    * Create a share snapshot
    * Set share quota and metadata
    * List directories and files
    * Get the directory or file client to interact with a specific entity

* [file_samples_directory.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share/samples/file_samples_directory.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share/samples/file_samples_directory_async.py)) - Examples for interacting with directories:
    * Create a directory and add files
    * Create and delete subdirectories
    * Get the subdirectory client

* [file_samples_client.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share/samples/file_samples_client.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share/samples/file_samples_client_async.py)) - Examples for interacting with files:
    * Create, upload, download, and delete files
    * Copy a file from a URL

## Prerequisites
* Python 3.6 or later is required to use this package
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure storage account](https://docs.microsoft.com/azure/storage/common/storage-account-overview) to run these samples.

## Setup

1. Install the Azure Storage File Share client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-storage-file-share --pre
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python file_samples_hello_world.py`

## Next steps

Check out the [API reference documentation](https://aka.ms/azsdk-python-storage-fileshare-ref) to learn more about
what you can do with the Azure Storage File Share client library.
