# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import logging
import inspect
from typing import List, Optional, Any, Tuple
from pathlib import Path
from azure.storage.blob.aio import ContainerClient

from ._operations import DatasetsOperations as DatasetsOperationsGenerated
from ...models._models import (
    DatasetVersion,
    PendingUploadRequest,
    PendingUploadType,
    PendingUploadResponse,
)
from ...models._enums import (
    DatasetType,
    AuthenticationType,
)

logger = logging.getLogger(__name__)


class DatasetsOperations(DatasetsOperationsGenerated):

    # Internal helper method to create a new dataset and return a ContainerClient from azure-storage-blob package,
    # to the dataset's blob storage.
    async def _create_dataset_and_get_its_container_client(
        self,
        name: str,
        input_version: Optional[str] = None,
    ) -> Tuple[ContainerClient, str]:

        if input_version:
            pending_upload_response: PendingUploadResponse = await self.start_pending_upload_version(
                name=name,
                version=input_version,
                body=PendingUploadRequest(pending_upload_type=PendingUploadType.TEMPORARY_BLOB_REFERENCE),
            )
            output_version: str = input_version
        else:
            pending_upload_response: PendingUploadResponse = await self.start_pending_upload(
                name=name,
                body=PendingUploadRequest(pending_upload_type=PendingUploadType.TEMPORARY_BLOB_REFERENCE),
            )
            if pending_upload_response.dataset_version:
                output_version: str = pending_upload_response.dataset_version
            else:
                raise ValueError("Dataset version is not present in the response")

        if not pending_upload_response.blob_reference_for_consumption:
            raise ValueError("Blob reference for consumption is not present")
        if not pending_upload_response.blob_reference_for_consumption.credential.type:
            raise ValueError("Credential type is not present")
        if pending_upload_response.blob_reference_for_consumption.credential.type != AuthenticationType.SAS:
            raise ValueError("Credential type is not SAS")
        if not pending_upload_response.blob_reference_for_consumption.blob_uri:
            raise ValueError("Blob URI is not present or empty")

        if logger.getEffectiveLevel() == logging.DEBUG:
            method = inspect.currentframe().f_code.co_name
            logger.debug(
                "[%s] pending_upload_response.pending_upload_id = %s.",
                method,
                pending_upload_response.pending_upload_id,
            )
            logger.debug(
                "[%s] pending_upload_response.pending_upload_type = %s.",
                method,
                pending_upload_response.pending_upload_type,
            )  # == PendingUploadType.TEMPORARY_BLOB_REFERENCE
            logger.debug(
                "[%s] pending_upload_response.blob_reference_for_consumption.blob_uri = %s.",
                method,
                pending_upload_response.blob_reference_for_consumption.blob_uri,
            )  # Hosted on behalf of (HOBO) not visible to the user. If the form of: "https://<account>.blob.core.windows.net/<container>?<sasToken>"
            logger.debug(
                "[%s] pending_upload_response.blob_reference_for_consumption.storage_account_arm_id = %s.",
                method,
                pending_upload_response.blob_reference_for_consumption.storage_account_arm_id,
            )  # /subscriptions/<>/resourceGroups/<>/Microsoft.Storage/accounts/<>
            logger.debug(
                "[%s] pending_upload_response.blob_reference_for_consumption.credential.sas_uri = %s.",
                method,
                pending_upload_response.blob_reference_for_consumption.credential.sas_uri,
            )
            logger.debug(
                "[%s] pending_upload_response.blob_reference_for_consumption.credential.type = %s.",
                method,
                pending_upload_response.blob_reference_for_consumption.credential.type,
            )  # == AuthenticationType.SAS

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

    async def upload_file_and_create(
        self, *, name: str, version: Optional[str] = None, file: str, **kwargs: Any
    ) -> DatasetVersion:
        """Upload file to a blob storage, and create a dataset that references this file.
        This method uses the `ContainerClient.upload_blob` method from the azure-storage-blob package
        to upload the file. Any keyword arguments provided will be passed to the `upload_blob` method.

        :param name: The name of the dataset. Required.
        :type name: str
        :param version: The version identifier for the dataset. Optional.
        :type version: str or None
        :param file: The file name (including optional path) to be uploaded. Required.
        :type file: str
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
                    "[%s] Start uploading file `%s` as blob `%s`.",
                    inspect.currentframe().f_code.co_name,
                    file,
                    blob_name,
                )

                # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-upload-blob
                with await container_client.upload_blob(name=blob_name, data=data, **kwargs) as blob_client:

                    logger.debug("[%s] Done uploading", inspect.currentframe().f_code.co_name)

                    dataset_version = await self.create_version(
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

    async def upload_folder_and_create(
        self, *, name: str, version: Optional[str] = None, folder: str, **kwargs: Any
    ) -> DatasetVersion:
        """Upload all files in a folder and its sub folders to a blob storage, while maintaining
        relative paths, and create a dataset that references this folder.
        This method uses the `ContainerClient.upload_blob` method from the azure-storage-blob package
        to upload each file. Any keyword arguments provided will be passed to the `upload_blob` method.

        :param name: The name of the dataset. Required.
        :type name: str
        :param version: The version identifier for the dataset. Optional.
        :type version: str or None
        :param folder: The folder name (including optional path) to be uploaded. Required.
        :type file: str
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
                        "[%s] Start uploading file `%s` as blob `%s`.",
                        inspect.currentframe().f_code.co_name,
                        file_path,
                        blob_name,
                    )
                    with file_path.open(
                        "rb"
                    ) as data:  # Open the file for reading in binary mode # TODO: async version?
                        # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-upload-blob
                        container_client.upload_blob(name=str(blob_name), data=data, **kwargs)
                    logger.debug("[%s] Done uploaded.", inspect.currentframe().f_code.co_name)
                    files_uploaded = True

            if not files_uploaded:
                raise ValueError("The provided folder is empty.")

            dataset_version = await self.create_version(
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


__all__: List[str] = [
    "DatasetsOperations"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
