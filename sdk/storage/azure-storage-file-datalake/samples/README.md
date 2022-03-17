---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-storage
urlFragment: storage-datalake-samples
---

# Azure Storage Datalake client library for Python Samples

These are code samples that show common scenario operations with the Azure DataLake Storage client library.

Several DataLake Storage Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with DataLake Storage:

* [`datalake_samples_service.py`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-datalake/samples/datalake_samples_service.py) - Examples for authenticating and operating on the client:
    * Instantiate DataLakeServiceClient using connection str
    * Instantiate DataLakeServiceClient using AAD Credential
    * Get user delegation key
    * Create all kinds of clients from DataLakeServiceClient and operate on those clients
    * List file systems

* [`datalake_samples_access_control.py`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-datalake/samples/datalake_samples_access_control.py) - Examples for common DataLake Storage tasks:
    * Set up a file system
    * Create a directory
    * Set/Get access control for the directory
    * Create files under the directory
    * Set/Get access control for each file
    * Delete file system

* [`datalake_samples_upload_download.py`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-datalake/samples/datalake_samples_upload_download.py) - Examples for authenticating and creating the client:
    * Set up a file system
    * Create file
    * Append data to the file
    * Flush data to the file
    * Download the uploaded data
    * Delete file system

## Prerequisites
* Python 3.6 later is required to use this package
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure storage account](https://docs.microsoft.com/azure/storage/blobs/data-lake-storage-quickstart-create-account) to run these samples.

## Setup

1. Install the Azure Storage Datalake client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-storage-file-datalake --pre
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables `STORAGE_ACCOUNT_NAME` and `STORAGE_ACCOUNT_KEY` with your own values.
3. run the file, eg.`python datalake_samples_upload_download.py`

## Next steps

Check out the [API reference documentation](https://aka.ms/azsdk-python-storage-filedatalake-ref) to learn more about
what you can do with the DataLake Storage client library.
