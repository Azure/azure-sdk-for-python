# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


CHUNK_SIZE = 1024
PROCESSES_PER_CORE = 2
MAX_CONCURRENCY = 16  # number of parallel connections to be used for uploads > 64MB and downloads (Azure Storage param: https://docs.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.blobclient?view=azure-python#upload-blob-data--blob-type--blobtype-blockblob---blockblob----length-none--metadata-none----kwargs-)

ARTIFACT_ORIGIN = "LocalUpload"
LEGACY_ARTIFACT_DIRECTORY = "az-ml-artifacts"
UPLOAD_CONFIRMATION = {"upload_status": "completed"}

HASH_ALGORITHM_NAME = "md5"
AML_IGNORE_FILE_NAME = ".amlignore"
GIT_IGNORE_FILE_NAME = ".gitignore"

ASSET_PATH_ERROR = "(UserError) Asset paths cannot be updated."
CHANGED_ASSET_PATH_MSG = (
    "The code asset {name}:{version} is already linked to an asset "
    "in your datastore that does not match the content from your `directory` param "
    "and cannot be overwritten. Please provide a unique name or version "
    "to successfully create a new code asset."
)
CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA = "The code asset is already linked to an asset."
EMPTY_DIRECTORY_ERROR = "Directory {0} is empty. path or local_path must be a non-empty directory."
FILE_SIZE_WARNING = "Your file exceeds 100 MB. If you experience low upload speeds or latency, we recommend using the AzCopy tool for this file transfer. See https://docs.microsoft.com/azure/storage/common/storage-use-azcopy-v10 for more information."
INVALID_MLTABLE_METADATA_SCHEMA_MSG = "Invalid MLTable metadata schema"
INVALID_MLTABLE_METADATA_SCHEMA_ERROR = (
    "{jsonSchemaErrorPath}{jsonSchemaMessage}\n{invalidMLTableMsg}:\n{invalidSchemaSnippet}"
)
BLOB_DATASTORE_IS_HDI_FOLDER_KEY = "hdi_isfolder"
