
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to ...

USAGE:
    python sample_datasets.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
"""
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects.dp1 import AIProjectClient
from azure.ai.projects.dp1.models import DatasetVersion, DatasetType, PendingUploadResponse, PendingUploadRequest, PendingUploadType



project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)


# Auto-generated dataset methods:
project_client.datasets.list_latest_datasets
project_client.datasets.list_dataset_versions
project_client.datasets.delete_version
project_client.datasets.get_version
project_client.datasets.create_or_update
project_client.datasets.create_or_get_start_pending_upload


# How do I implement the following?
# From Neehar's https://github.com/Azure/agent-first-sdk/blob/ee7a09848ded49f925ef911a2eb2d8ac6aff9c50/specs/common_guidelines/README.md
#
# client.datasets.create_dataset(
#     name="my_dataset_name",
#     version="my_dataset_version",  # Optional
#     file="sample_file.pdf",
#     connection_name="my_train_data_connection" # Optional
# )
#
# By doing these steps:
# 1. Call StartPendingUpload ( "StartPendingUpdate will return an assetId with version, and that should be used in PUT call in #3.")
# 2. SDK uses SAS URI to upload to blob storage
# 3. Dataset.CreateOrUpdate API with Dataset.Uri as the blob url used in #2, like just removing SAS token from it.

dataset_name="my-dataset-name"
dataset_version="my-dataset-version"

# Step 1: Create a new dataset
pending_upload_request = PendingUploadRequest(
    pending_upload_type = PendingUploadType.TEMPORARY_BLOB_REFERENCE
)

pending_upload_response: PendingUploadResponse = project_client.datasets.create_or_get_start_pending_upload(
    name=dataset_name,
    version=dataset_version,
    pending_upload_request=pending_upload_request
)

print(pending_upload_response.pending_upload_id)
print(pending_upload_response.pending_upload_type)
print(pending_upload_response.blob_reference_for_consumption.blob_uri) # Hosted on behalf of (HOBO) not visible to the user
print(pending_upload_response.blob_reference_for_consumption.storage_account_arm_id) # /subscriptions/<>/resourceGroups/<>/Microsoft.Storage/accounts/<>
print(pending_upload_response.blob_reference_for_consumption.credential.sas_token)
print(pending_upload_response.blob_reference_for_consumption.credential.type) # == CredentialType.SAS

# Step 2:
# Make a PUT request to the blob URI provided above, using SAS token for auth
# Where is the REST API for this? https://learn.microsoft.com/en-us/rest/api/storageservices/put-blob?tabs=microsoft-entra-id
# Should we use blob storage SDK for this?
# Will return <account>.blob.windows.core.net/<container>/

# Step 3:
dataset_version = DatasetVersion(
    dataset_uri="?",# <account>.blob.windows.core.net/<container>/<file_name>
    dataset_type=DatasetType.URI_FILE
)

dataset_version = project_client.datasets.create_or_update(
    name=dataset_name,
    version=dataset_version, 
    dataset_version=dataset_version
)