# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import os
import re
import logging
from typing import Any, Tuple, Optional
from pathlib import Path
from urllib.parse import urlsplit
from azure.storage.blob import ContainerClient
from azure.core.tracing.decorator import distributed_trace
from ._operations import DatasetsOperations as DatasetsOperationsGenerated
from ..models._models import (
    FileDatasetVersion,
    FolderDatasetVersion,
    PendingUploadRequest,
    PendingUploadResponse,
    PendingUploadType,
)

logger = logging.getLogger(__name__)


class DatasetsOperations(DatasetsOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`datasets` attribute.
    """

    # Internal helper method to create a new dataset and return a ContainerClient from azure-storage-blob package,
    # to the dataset's blob storage.
    def _create_dataset_and_get_its_container_client(
        self,
        name: str,
        input_version: str,
        connection_name: Optional[str] = None,
    ) -> Tuple[ContainerClient, str]:

        pending_upload_result: PendingUploadResponse = self.pending_upload(
            name=name,
            version=input_version,
            pending_upload_request=PendingUploadRequest(
                pending_upload_type=PendingUploadType.BLOB_REFERENCE,
                connection_name=connection_name,
            ),
        )
        output_version: str = input_version

        if not pending_upload_result.blob_reference:
            raise ValueError("Blob reference is not present")
        if not pending_upload_result.blob_reference.credential:
            raise ValueError("SAS credential are not present")
        if not pending_upload_result.blob_reference.credential.sas_uri:
            raise ValueError("SAS URI is missing or empty")

        # For overview on Blob storage SDK in Python see:
        # https://learn.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-python
        # https://learn.microsoft.com/azure/storage/blobs/storage-blob-upload-python

        # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-from-container-url
        return (
            ContainerClient.from_container_url(
                container_url=pending_upload_result.blob_reference.credential.sas_uri  # Of the form: "https://<account>.blob.core.windows.net/<container>?<sasToken>"
            ),
            output_version,
        )

    @distributed_trace
    def upload_file(
        self, *, name: str, version: str, file_path: str, connection_name: Optional[str] = None, **kwargs: Any
    ) -> FileDatasetVersion:
        """Upload file to a blob storage, and create a dataset that references this file.
        This method uses the `ContainerClient.upload_blob` method from the azure-storage-blob package
        to upload the file. Any keyword arguments provided will be passed to the `upload_blob` method.

        :keyword name: The name of the dataset. Required.
        :paramtype name: str
        :keyword version: The version identifier for the dataset. Required.
        :paramtype version: str
        :keyword file_path: The file name (including optional path) to be uploaded. Required.
        :paramtype file_path: str
        :keyword connection_name: The name of an Azure Storage Account connection, where the file should be uploaded.
         If not specified, the default Azure Storage Account connection will be used. Optional.
        :paramtype connection_name: str
        :return: The created dataset version.
        :rtype: ~azure.ai.projects.models.FileDatasetVersion
        :raises ~azure.core.exceptions.HttpResponseError: If an error occurs during the HTTP request.
        """

        pathlib_file_path = Path(file_path)
        if not pathlib_file_path.exists():
            raise ValueError(f"The provided file `{file_path}` does not exist.")
        if pathlib_file_path.is_dir():
            raise ValueError("The provided file is actually a folder. Use method `upload_folder` instead")

        container_client, output_version = self._create_dataset_and_get_its_container_client(
            name=name, input_version=version, connection_name=connection_name
        )

        with container_client:

            with open(file=file_path, mode="rb") as data:

                blob_name = pathlib_file_path.name  # Extract the file name from the path.
                logger.debug(
                    "[upload_file] Start uploading file `%s` as blob `%s`.",
                    file_path,
                    blob_name,
                )

                # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-upload-blob
                with container_client.upload_blob(name=blob_name, data=data, **kwargs) as blob_client:
                    logger.debug("[upload_file] Done uploading")

                    # Remove the SAS token from the URL (remove all query strings).
                    # The resulting format should be "https://<account>.blob.core.windows.net/<container>/<file_name>"
                    data_uri = urlsplit(blob_client.url)._replace(query="").geturl()

                    dataset_version = self.create_or_update(
                        name=name,
                        version=output_version,
                        dataset_version=FileDatasetVersion(
                            # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.blobclient?view=azure-python#azure-storage-blob-blobclient-url
                            # Per above doc the ".url" contains SAS token... should this be stripped away?
                            data_uri=data_uri,
                        ),
                    )

        return dataset_version  # type: ignore

    @distributed_trace
    def upload_folder(
        self,
        *,
        name: str,
        version: str,
        folder: str,
        connection_name: Optional[str] = None,
        file_pattern: Optional[re.Pattern] = None,
        **kwargs: Any,
    ) -> FolderDatasetVersion:
        """Upload all files in a folder and its sub folders to a blob storage, while maintaining
        relative paths, and create a dataset that references this folder.
        This method uses the `ContainerClient.upload_blob` method from the azure-storage-blob package
        to upload each file. Any keyword arguments provided will be passed to the `upload_blob` method.

        :keyword name: The name of the dataset. Required.
        :paramtype name: str
        :keyword version: The version identifier for the dataset. Required.
        :paramtype version: str
        :keyword folder: The folder name (including optional path) to be uploaded. Required.
        :paramtype folder: str
        :keyword connection_name: The name of an Azure Storage Account connection, where the file should be uploaded.
         If not specified, the default Azure Storage Account connection will be used. Optional.
        :paramtype connection_name: str
        :keyword file_pattern: A regex pattern to filter files to be uploaded. Only files matching the pattern
         will be uploaded. Optional.
        :paramtype file_pattern: re.Pattern
        :return: The created dataset version.
        :rtype: ~azure.ai.projects.models.FolderDatasetVersion
        :raises ~azure.core.exceptions.HttpResponseError: If an error occurs during the HTTP request.
        """
        path_folder = Path(folder)
        if not Path(path_folder).exists():
            raise ValueError(f"The provided folder `{folder}` does not exist.")
        if Path(path_folder).is_file():
            raise ValueError("The provided folder is actually a file. Use method `upload_file` instead.")

        container_client, output_version = self._create_dataset_and_get_its_container_client(
            name=name,
            input_version=version,
            connection_name=connection_name,
        )

        with container_client:

            # Recursively traverse all files in the folder
            files_uploaded: bool = False
            for root, _, files in os.walk(folder):
                for file in files:
                    if file_pattern and not file_pattern.search(file):
                        continue  # Skip files that do not match the pattern
                    file_path = os.path.join(root, file)
                    blob_name = os.path.relpath(file_path, folder).replace("\\", "/")  # Ensure correct format for Azure
                    logger.debug(
                        "[upload_folder] Start uploading file `%s` as blob `%s`.",
                        file_path,
                        blob_name,
                    )
                    with open(file=file_path, mode="rb") as data:  # Open the file for reading in binary mode
                        # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-upload-blob
                        container_client.upload_blob(name=str(blob_name), data=data, **kwargs)
                    logger.debug("[upload_folder] Done uploading file")
                    files_uploaded = True
            logger.debug("[upload_folder] Done uploaded.")

            if not files_uploaded:
                raise ValueError("The provided folder is empty.")

            # Remove the SAS token from the URL (remove all query strings).
            # The resulting format should be "https://<account>.blob.core.windows.net/<container>"
            # See https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python#azure-storage-blob-containerclient-url
            data_uri = urlsplit(container_client.url)._replace(query="").geturl()

            dataset_version = self.create_or_update(
                name=name,
                version=output_version,
                dataset_version=FolderDatasetVersion(data_uri=data_uri),
            )

        return dataset_version  # type: ignore
