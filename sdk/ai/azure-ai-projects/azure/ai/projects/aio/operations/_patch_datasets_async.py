# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import logging
from typing import Any, Tuple
from pathlib import Path
from azure.storage.blob.aio import ContainerClient
from azure.core.tracing.decorator_async import distributed_trace_async

from ._operations import DatasetsOperations as DatasetsOperationsGenerated
from ...models._models import (
    DatasetVersion,
    PendingUploadRequest,
    PendingUploadType,
    PendingUploadResponse,
)
from ...models._enums import DatasetType, CredentialType

logger = logging.getLogger(__name__)


class DatasetsOperations(DatasetsOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.aio.AIProjectClient`'s
        :attr:`datasets` attribute.
    """

    # Internal helper method to create a new dataset and return a ContainerClient from azure-storage-blob package,
    # to the dataset's blob storage.
    async def _create_dataset_and_get_its_container_client(
        self,
        name: str,
        input_version: str,
    ) -> Tuple[ContainerClient, str]:

        pending_upload_response: PendingUploadResponse = await self.start_pending_upload_version(
            name=name,
            version=input_version,
            body=PendingUploadRequest(pending_upload_type=PendingUploadType.TEMPORARY_BLOB_REFERENCE),
        )
        output_version: str = input_version

        if not pending_upload_response.blob_reference_for_consumption:
            raise ValueError("Blob reference for consumption is not present")
        if not pending_upload_response.blob_reference_for_consumption.credential.type:
            raise ValueError("Credential type is not present")
        if pending_upload_response.blob_reference_for_consumption.credential.type != CredentialType.SAS:
            raise ValueError("Credential type is not SAS")
        if not pending_upload_response.blob_reference_for_consumption.blob_uri:
            raise ValueError("Blob URI is not present or empty")

        if logger.getEffectiveLevel() == logging.DEBUG:
            logger.debug(
                "[_create_dataset_and_get_its_container_client] pending_upload_response.pending_upload_id = %s.",
                pending_upload_response.pending_upload_id,
            )
            logger.debug(
                "[_create_dataset_and_get_its_container_client] pending_upload_response.pending_upload_type = %s.",
                pending_upload_response.pending_upload_type,
            )  # == PendingUploadType.TEMPORARY_BLOB_REFERENCE
            logger.debug(
                "[_create_dataset_and_get_its_container_client] pending_upload_response.blob_reference_for_consumption.blob_uri = %s.",
                pending_upload_response.blob_reference_for_consumption.blob_uri,
            )  # Hosted on behalf of (HOBO) not visible to the user. If the form of: "https://<account>.blob.core.windows.net/<container>?<sasToken>"
            logger.debug(
                "[_create_dataset_and_get_its_container_client] pending_upload_response.blob_reference_for_consumption.storage_account_arm_id = %s.",
                pending_upload_response.blob_reference_for_consumption.storage_account_arm_id,
            )  # /subscriptions/<>/resourceGroups/<>/Microsoft.Storage/accounts/<>
            logger.debug(
                "[_create_dataset_and_get_its_container_client] pending_upload_response.blob_reference_for_consumption.credential.sas_uri = %s.",
                pending_upload_response.blob_reference_for_consumption.credential.sas_uri,
            )
            logger.debug(
                "[_create_dataset_and_get_its_container_client] pending_upload_response.blob_reference_for_consumption.credential.type = %s.",
                pending_upload_response.blob_reference_for_consumption.credential.type,
            )  # == CredentialType.SAS

        # For overview on Blob storage SDK in Python see:
        # https://learn.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-python
        # https://learn.microsoft.com/azure/storage/blobs/storage-blob-upload-python

        # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-from-container-url
        return (
            await ContainerClient.from_container_url(
                container_url=pending_upload_response.blob_reference_for_consumption.blob_uri,  # Of the form: "https://<account>.blob.core.windows.net/<container>?<sasToken>"
            ),
            output_version,
        )

    @distributed_trace_async
    async def upload_file_and_create(self, *, name: str, version: str, file: str, **kwargs: Any) -> DatasetVersion:
        """Upload file to a blob storage, and create a dataset that references this file.
        This method uses the `ContainerClient.upload_blob` method from the azure-storage-blob package
        to upload the file. Any keyword arguments provided will be passed to the `upload_blob` method.

        :keyword name: The name of the dataset. Required.
        :paramtype name: str
        :keyword version: The version identifier for the dataset. Required.
        :paramtype version: str
        :keyword file: The file name (including optional path) to be uploaded. Required.
        :paramtype file: str
        :return: The created dataset version.
        :rtype: ~azure.ai.projects.models.DatasetVersion
        :raises ~azure.core.exceptions.HttpResponseError: If an error occurs during the HTTP request.
        """

        path_file = Path(file)
        if not path_file.exists():
            raise ValueError("The provided file does not exist.")
        if path_file.is_dir():
            raise ValueError("The provided file is actually a folder. Use method `create_and_upload_folder` instead")

        container_client, output_version = await self._create_dataset_and_get_its_container_client(
            name=name, input_version=version
        )

        async with container_client:

            with open(file=file, mode="rb") as data:  # TODO: What is the best async options for file reading?

                blob_name = path_file.name  # Extract the file name from the path.
                logger.debug(
                    "[upload_file_and_create] Start uploading file `%s` as blob `%s`.",
                    file,
                    blob_name,
                )

                # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-upload-blob
                with await container_client.upload_blob(name=blob_name, data=data, **kwargs) as blob_client:

                    logger.debug("[upload_file_and_create] Done uploading")

                    dataset_version = await self.create_or_update_version(
                        name=name,
                        version=output_version,
                        body=DatasetVersion(
                            # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.blobclient?view=azure-python#azure-storage-blob-blobclient-url
                            # Per above doc the ".url" contains SAS token... should this be stripped away?
                            dataset_uri=blob_client.url,  # "<account>.blob.windows.core.net/<container>/<file_name>"
                            type=DatasetType.URI_FILE,
                        ),
                    )

        return dataset_version

    @distributed_trace_async
    async def upload_folder_and_create(self, *, name: str, version: str, folder: str, **kwargs: Any) -> DatasetVersion:
        """Upload all files in a folder and its sub folders to a blob storage, while maintaining
        relative paths, and create a dataset that references this folder.
        This method uses the `ContainerClient.upload_blob` method from the azure-storage-blob package
        to upload each file. Any keyword arguments provided will be passed to the `upload_blob` method.

        :keyword name: The name of the dataset. Required.
        :paramtype name: str
        :keyword version: The version identifier for the dataset. Required.
        :paramtype version: str
        :keyword folder: The folder name (including optional path) to be uploaded. Required.
        :paramtype file: str
        :return: The created dataset version.
        :rtype: ~azure.ai.projects.models.DatasetVersion
        :raises ~azure.core.exceptions.HttpResponseError: If an error occurs during the HTTP request.
        """
        path_folder = Path(folder)
        if not Path(path_folder).exists():
            raise ValueError("The provided folder does not exist.")
        if Path(path_folder).is_file():
            raise ValueError("The provided folder is actually a file. Use method `create_and_upload_file` instead.")

        container_client, output_version = await self._create_dataset_and_get_its_container_client(
            name=name, input_version=version
        )

        async with container_client:

            # Recursively traverse all files in the folder
            files_uploaded: bool = False
            for file_path in path_folder.rglob("*"):  # `rglob` matches all files and folders recursively
                if file_path.is_file():  # Check if the path is a file. Skip folders.
                    blob_name = file_path.relative_to(path_folder)  # Blob name relative to the folder
                    logger.debug(
                        "[upload_folder_and_create] Start uploading file `%s` as blob `%s`.",
                        file_path,
                        blob_name,
                    )
                    with file_path.open(
                        "rb"
                    ) as data:  # Open the file for reading in binary mode # TODO: async version?
                        # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-upload-blob
                        container_client.upload_blob(name=str(blob_name), data=data, **kwargs)
                    logger.debug("[upload_folder_and_create] Done uploaded.")
                    files_uploaded = True

            if not files_uploaded:
                raise ValueError("The provided folder is empty.")

            dataset_version = await self.create_or_update_version(
                name=name,
                version=output_version,
                body=DatasetVersion(
                    # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.blobclient?view=azure-python#azure-storage-blob-blobclient-url
                    # Per above doc the ".url" contains SAS token... should this be stripped away?
                    dataset_uri=container_client.url,  # "<account>.blob.windows.core.net/<container> ?"
                    type=DatasetType.URI_FOLDER,
                ),
            )

        return dataset_version
