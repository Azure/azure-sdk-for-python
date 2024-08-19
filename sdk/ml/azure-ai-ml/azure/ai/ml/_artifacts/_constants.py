# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


CHUNK_SIZE = 1024
PROCESSES_PER_CORE = 2
# number of parallel connections to be used for uploads > 64MB and downloads
# pylint: disable=line-too-long
# (Azure Storage param: https://docs.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.blobclient?view=azure-python#upload-blob-data--blob-type--blobtype-blockblob---blockblob----length-none--metadata-none----kwargs-)
MAX_CONCURRENCY = 16

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
FILE_SIZE_WARNING = (
    "Your file exceeds 100 MB. If you experience low speeds, latency, or broken connections, we recommend using "
    "the AzCopyv10 tool for this file transfer.\n\nExample: azcopy copy '{source}' '{destination}' "  # cspell:disable-line
    "\n\nSee https://docs.microsoft.com/azure/storage/common/storage-use-azcopy-v10 for more information."
)
INVALID_MLTABLE_METADATA_SCHEMA_MSG = "Invalid MLTable metadata schema"
INVALID_MLTABLE_METADATA_SCHEMA_ERROR = (
    "{jsonSchemaErrorPath}{jsonSchemaMessage}\n{invalidMLTableMsg}:\n{invalidSchemaSnippet}"
)
BLOB_DATASTORE_IS_HDI_FOLDER_KEY = "hdi_isfolder"
BLOB_STORAGE_CLIENT_NAME = "BlobStorageClient"
GEN2_STORAGE_CLIENT_NAME = "Gen2StorageClient"
DEFAULT_CONNECTION_TIMEOUT = 14400
STORAGE_URI_REGEX = (
    r"(https:\/\/([a-zA-Z0-9@:%_\\\-+~#?&=]+)[a-zA-Z0-9@:%._\\\-+~#?&=]+\.?)\/([a-zA-Z0-9@:%._\\\-+~#?&=]+)\/?(.*)"
)

WORKSPACE_MANAGED_DATASTORE_WITH_SLASH = "azureml://datastores/workspacemanageddatastore/"
WORKSPACE_MANAGED_DATASTORE = "azureml://datastores/workspacemanageddatastore"
AUTO_DELETE_SETTING_NOT_ALLOWED_ERROR_NO_PERSONAL_DATA = (
    "Auto delete setting cannot be specified in JobOutput now. Please remove it and try again."
)
INVALID_MANAGED_DATASTORE_PATH_ERROR_NO_PERSONAL_DATA = f'Cannot specify a sub-path for workspace managed datastore. Please set "{WORKSPACE_MANAGED_DATASTORE}" as the path.'
SAS_KEY_AUTHENTICATION_ERROR_MSG = (
    "{0}\n{1}\n"
    "This SAS token is derived from an account key, but key-based authentication is not permitted "
    "for this storage account. To update workspace properties, please see the documentation: "
    "https://review.learn.microsoft.com/en-us/azure/machine-learning/how-to-disable-local-auth-storage?view="
    "azureml-api-2&branch=pr-en-us-278974&tabs=cli#update-an-existing-workspace"
)
KEY_AUTHENTICATION_ERROR_CODE = "KeyBasedAuthenticationNotPermitted"
