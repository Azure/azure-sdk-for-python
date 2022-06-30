# Artifact Storage

## Overview

The AzureML v2 artifacts module facilitates interaction with Azure datastores for artifact creation and retrieval.

#### Supported Storage Account Types

Azure Storage offers four different account types (Blob, Gen1, Gen2, and File), and AzureML v2 currently supports Blob and Gen2.<sup>**</sup> Each has its own unique design and architecture which adds value for multiple user groups, but also provides its own set of challenges and requirements when building storage infrastructure. During implementation of the classes and functionality, the goal is to share as much as possible across the account types for code clarity and cleanliness while still taking advantage of their differences where possible and efficient.

[_gen2_storage_helper.py](_gen2_storage_helper.py) contains the client object and methods for uploading to and downloading from ADLS Gen2 storage accounts. This implementation heavily relies on the [ADLS Gen2 Storage SDK](https://docs.microsoft.com/python/api/azure-storage-file-datalake/azure.storage.filedatalake?view=azure-python).

[_blob_storage_helper.py](_blob_storage_helper.py) contains the client object and methods for uploading to and downloading from Azure Blob storage accounts. This implementation heavily relies on the [Blob Storage SDK](https://docs.microsoft.com/python/api/azure-storage-blob/azure.storage.blob?view=azure-python).

<sub>**This folder includes an implementation of support for Azure File Storage; however, Azure File datastores are not yet supported for AzureML v2 due to Management Front End (MFE) restrictions.</sub>

#### What are artifacts?

Artifacts are the datastore representations of the files and folders that Assets are associated with. There can be a many-to-one relationship between assets and artifacts (e.g. asset _experiment-4-dataset:1_ and asset _experiment-1-dataset:1_ can both point to the same file or folder in storage). Artifacts are idempotent and thus are never overwritten or altered via AzureML once uploaded.

#### Upload Process
![](upload_process_flowchart.png)

Datastore upload functionality is triggered by calling an **Asset** or **Job**  object's `create_or_update` method which then calls `_check_and_upload_path` in [_artifact_utilities.py](_artifact_utilities.py) to do basic checks to see if the path the user provided is a local path or if it is a reference to a remote object (e.g. a storage uri)

If the path is determined to be a local path, `_upload_to_datastore` in [_artifact_utilities.py](_artifact_utilities.py) is called which 1) checks for a .amlignore or .gitignore file at the path and creates a filter for any excluded files, 2) creates a hash for the path and its contents, and 3) determines the datastore name and finally sends it off to `upload_artifact` in [_artifact_utilities.py](_artifact_utilities.py) which initializes a storage client in [_storage_utils.py](../_utils/_storage_utils.py) corresponding to the datastore type, either **Gen2StorageClient** or **BlobStorageClient**.

The hash created in `_upload_to_datastore` will be used as a the name of the directory in the v2-specific LocalUpload/ directory inside the datastore where the file(s) will be stored. The storage client checks the hash against all existing directory names to see if the content has already been uploaded. If it has, the client returns the artifact's path in the blob storage along with the name and version of the asset is was last registered to, and the `create_or_update` method concludes its client-side work and continues onto contacting Management Front End for the service call. If the file or folder does not exist, it is uploaded, confirmation metadata is set, and then the asset path is returned to the `create_or_update` method.


### Download Process

Download functionality is currently limited to **Job** and **Model** objects and does not require any of the pre-process steps that uploading does. It simply takes in the path, finds it in the storage account, and downloads it to the user's local machine.
