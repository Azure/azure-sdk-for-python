# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional
from pathlib import Path
from azure.storage.blob import ContainerClient, BlobClient, BlobType

from ._operations import DatasetOperations as DatasetOperationsGenerated
from ..models._models import (
    DatasetVersion,
    PendingUploadRequest,
    PendingUploadType,
    PendingUploadResponse,
    CredentialType,
)
from ..models._enums import (
    DatasetType,
)

class DatasetOperations(DatasetOperationsGenerated):

    def __init__(self, outer_instance):
        self._outer_instance = outer_instance

    def create_and_upload(
        self,
        *,
        name: str,
        version: Optional[str] = None,
        file: str,
        connection_name: Optional[str] = None, # TODO: Use me.
    ) -> DatasetVersion:
        """Upload file to an internal blob storage, and create a dataset that references this file.

        :param name: The name of the dataset. Required.
        :type name: str
        :param version: The version identifier for the dataset. Optional.
        :type version: str or None
        :param file: The file name (including optional path) to be uploaded. Required.
        :type file: str
        :param connection_name: The name of the AI Project Connection to be used. Optional.
        :type connection_name: str or None
        :return: The created dataset version.
        :rtype: ~azure.ai.projects.dp1.models.DatasetVersion
        :raises ~azure.core.exceptions.HttpResponseError: If an error occurs during the HTTP request.
        """

        pending_upload_response: PendingUploadResponse = self._outer_instance.datasets.create_or_get_start_pending_upload(
            name=name,
            version=version,
            pending_upload_request=PendingUploadRequest(
                pending_upload_type=PendingUploadType.TEMPORARY_BLOB_REFERENCE
            ),
        )

        if (True): # Debugging. Remove me.
            print(pending_upload_response.pending_upload_id)
            print(pending_upload_response.pending_upload_type) # == PendingUploadType.TEMPORARY_BLOB_REFERENCE
            print(pending_upload_response.blob_reference_for_consumption.blob_uri) # Hosted on behalf of (HOBO) not visible to the user. If the form of: "https://<account>.blob.core.windows.net/<container>?<sasToken>"
            print(pending_upload_response.blob_reference_for_consumption.storage_account_arm_id) # /subscriptions/<>/resourceGroups/<>/Microsoft.Storage/accounts/<>
            print(pending_upload_response.blob_reference_for_consumption.credential.sas_token)
            print(pending_upload_response.blob_reference_for_consumption.credential.type) # == CredentialType.SAS

        if pending_upload_response.blob_reference_for_consumption.credential.type != CredentialType.SAS:
            raise ValueError("Credential type is not SAS")

        # For overview on Blob storage SDK in Python see: 
        # https://learn.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-python
        # https://learn.microsoft.com/azure/storage/blobs/storage-blob-upload-python

        # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-from-container-url
        container_client: ContainerClient = ContainerClient.from_container_url(
            container_url=pending_upload_response.blob_reference_for_consumption.blob_uri, # Of the form: "https://<account>.blob.core.windows.net/<container>?<sasToken>"
        )

        with open(file=file, mode="rb") as data:

            # See https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-upload-blob
            blob_client: BlobClient = container_client.upload_blob(
                name=Path(file).name, # Extract the file name from the path.
                data=data,
                blob_type=BlobType.BLOCKBLOB,
            )

        dataset_version = self._outer_instance.datasets.create_or_update(
            name=name,
            version=version, 
            dataset_version=DatasetVersion(
                # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.blobclient?view=azure-python#azure-storage-blob-blobclient-url
                # Per above doc the ".url" contains SAS token... should this be stripped away?
                dataset_uri=blob_client.url, # "<account>.blob.windows.core.net/<container>/<file_name>"
                dataset_type=DatasetType.URI_FILE
            ),
        )

        return dataset_version


__all__: List[str] = [DatasetOperations]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
