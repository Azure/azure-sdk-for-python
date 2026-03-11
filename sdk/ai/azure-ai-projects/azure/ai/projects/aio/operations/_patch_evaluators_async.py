# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import os
import logging
from typing import Any, IO, Tuple, Optional, Union
from pathlib import Path
from azure.storage.blob.aio import ContainerClient
from azure.core.tracing.decorator_async import distributed_trace_async
from ._operations import BetaEvaluatorsOperations as EvaluatorsOperationsGenerated, JSON
from ...models._models import (
    EvaluatorVersion,
    PendingUploadRequest,
    PendingUploadResponse,
    PendingUploadType,
)

logger = logging.getLogger(__name__)


class EvaluatorsOperations(EvaluatorsOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.aio.AIProjectClient`'s
        :attr:`beta.evaluators` attribute.
    """

    async def _start_pending_upload_and_get_container_client(
        self,
        name: str,
        version: str,
        connection_name: Optional[str] = None,
    ) -> Tuple[ContainerClient, str]:
        """Call startPendingUpload to get a SAS URI and return a ContainerClient."""

        pending_upload_response: PendingUploadResponse = await self.pending_upload(
            name=name,
            version=version,
            pending_upload_request=PendingUploadRequest(
                pending_upload_type=PendingUploadType.BLOB_REFERENCE,
                connection_name=connection_name,
            ),
        )

        if not pending_upload_response.blob_reference:
            raise ValueError("Blob reference is not present")
        if not pending_upload_response.blob_reference.credential:
            raise ValueError("SAS credential are not present")
        if not pending_upload_response.blob_reference.credential.sas_uri:
            raise ValueError("SAS URI is missing or empty")

        return (
            ContainerClient.from_container_url(
                container_url=pending_upload_response.blob_reference.credential.sas_uri,
            ),
            version,
        )

    @distributed_trace_async
    async def upload(
        self,
        name: str,
        version: str,
        evaluator_version: Union[EvaluatorVersion, JSON, IO[bytes]],
        *,
        folder: str,
        connection_name: Optional[str] = None,
        **kwargs: Any,
    ) -> EvaluatorVersion:
        """Upload all files in a folder to blob storage and create a code-based evaluator version
        that references the uploaded code.

        This method uses the ``ContainerClient.upload_blob`` method from the azure-storage-blob
        package to upload each file. Any extra keyword arguments are forwarded to ``upload_blob``.

        :param name: The name of the evaluator. Required.
        :type name: str
        :param version: The version identifier for the evaluator. Required.
        :type version: str
        :param evaluator_version: The evaluator version definition. This is the same object accepted
         by ``create_version``. The definition should include an ``entry_point`` specifying the main
         Python file of the uploaded code. Is one of the following types: EvaluatorVersion, JSON,
         IO[bytes]. Required.
        :type evaluator_version: ~azure.ai.projects.models.EvaluatorVersion or JSON or IO[bytes]
        :keyword folder: Path to the folder containing the evaluator Python code. Required.
        :paramtype folder: str
        :keyword connection_name: The name of an Azure Storage Account connection where the files
         should be uploaded. If not specified, the default Azure Storage Account connection will be
         used. Optional.
        :paramtype connection_name: str
        :return: The created evaluator version.
        :rtype: ~azure.ai.projects.models.EvaluatorVersion
        :raises ~azure.core.exceptions.HttpResponseError: If an error occurs during the HTTP request.
        """
        path_folder = Path(folder)
        if not path_folder.exists():
            raise ValueError(f"The provided folder `{folder}` does not exist.")
        if path_folder.is_file():
            raise ValueError("The provided path is a file, not a folder.")

        container_client, output_version = await self._start_pending_upload_and_get_container_client(
            name=name,
            version=version,
            connection_name=connection_name,
        )

        async with container_client:
            files_uploaded: bool = False
            for root, _, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    blob_name = os.path.relpath(file_path, folder).replace("\\", "/")
                    logger.debug(
                        "[upload] Start uploading file `%s` as blob `%s`.",
                        file_path,
                        blob_name,
                    )
                    with open(file=file_path, mode="rb") as data:
                        await container_client.upload_blob(name=str(blob_name), data=data, **kwargs)
                    logger.debug("[upload] Done uploading file")
                    files_uploaded = True
            logger.debug("[upload] Done uploading all files.")

            if not files_uploaded:
                raise ValueError("The provided folder is empty.")

            result = await self.create_version(
                name=name,
                evaluator_version=evaluator_version,
            )

        return result
