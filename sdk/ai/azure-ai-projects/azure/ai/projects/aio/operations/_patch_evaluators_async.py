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
from typing import Any, Final, IO, Tuple, Optional, Union
from pathlib import Path
from urllib.parse import urlsplit
from azure.storage.blob.aio import ContainerClient
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from ._operations import BetaEvaluatorsOperations as BetaEvaluatorsOperationsGenerated, JSON
from ...models._enums import _FoundryFeaturesOptInKeys
from ...models._patch import _FOUNDRY_FEATURES_HEADER_NAME
from ...models._models import (
    CodeBasedEvaluatorDefinition,
    EvaluatorVersion,
)

logger = logging.getLogger(__name__)

_EVALUATORS_FOUNDRY_FEATURES_VALUE: Final[str] = _FoundryFeaturesOptInKeys.EVALUATIONS_V1_PREVIEW.value


class BetaEvaluatorsOperations(BetaEvaluatorsOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.aio.AIProjectClient`'s
        :attr:`beta.evaluators` attribute.
    """

    @staticmethod
    async def _upload_folder_to_blob(
        container_client: ContainerClient,
        folder: str,
        **kwargs: Any,
    ) -> None:
        """Walk *folder* and upload every eligible file to the blob container.

        Skips directories starting with ``.`` (e.g. ``.git``, ``.venv``),
        ``__pycache__``, ``venv``, ``node_modules``
        directories and ``.pyc`` / ``.pyo`` files.

        :param container_client: The blob container client to upload files to.
        :type container_client: ~azure.storage.blob.ContainerClient
        :param folder: Path to the local folder containing files to upload.
        :type folder: str
        :raises ValueError: If the folder contains no uploadable files.
        :raises HttpResponseError: Re-raised with a friendlier message on
            ``AuthorizationPermissionMismatch``.
        """
        skip_dirs = {"__pycache__", "venv", "node_modules"}
        skip_extensions = {".pyc", ".pyo"}
        files_uploaded = False

        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]
            for file_name in files:
                if any(file_name.endswith(ext) for ext in skip_extensions):
                    continue
                file_path = os.path.join(root, file_name)
                blob_name = os.path.relpath(file_path, folder).replace("\\", "/")
                logger.debug("[upload] Start uploading file `%s` as blob `%s`.", file_path, blob_name)
                with open(file=file_path, mode="rb") as data:
                    try:
                        await container_client.upload_blob(name=str(blob_name), data=data, **kwargs)
                    except HttpResponseError as e:
                        if getattr(e, "error_code", None) == "AuthorizationPermissionMismatch":
                            storage_account = urlsplit(container_client.url).hostname
                            raise HttpResponseError(
                                message=(
                                    f"Failed to upload file '{blob_name}' to blob storage: "
                                    f"permission denied. Ensure the identity that signed the SAS token "
                                    f"has the 'Storage Blob Data Contributor' role on the storage account "
                                    f"'{storage_account}'. "
                                    f"Original error: {e.message}"
                                ),
                                response=e.response,
                            ) from e
                        raise
                logger.debug("[upload] Done uploading file")
                files_uploaded = True

        logger.debug("[upload] Done uploading all files.")
        if not files_uploaded:
            raise ValueError("The provided folder is empty.")

    @staticmethod
    def _set_blob_uri(
        evaluator_version: Union[EvaluatorVersion, JSON, IO[bytes]],
        blob_uri: str,
    ) -> None:
        """Set ``blob_uri`` on the evaluator version's definition.

        :param evaluator_version: The evaluator version object to update.
        :type evaluator_version: Union[~azure.ai.projects.models.EvaluatorVersion, JSON, IO[bytes]]
        :param blob_uri: The blob URI to set on the definition.
        :type blob_uri: str
        """
        if isinstance(evaluator_version, dict):
            definition = evaluator_version.get("definition", {})
            if isinstance(definition, dict):
                definition["blob_uri"] = blob_uri
            elif isinstance(definition, CodeBasedEvaluatorDefinition):
                definition.blob_uri = blob_uri
        elif isinstance(evaluator_version, EvaluatorVersion):
            definition = evaluator_version.definition
            if isinstance(definition, CodeBasedEvaluatorDefinition):
                definition.blob_uri = blob_uri

    async def _start_pending_upload_and_get_container_client(
        self,
        name: str,
        version: str,
        connection_name: Optional[str] = None,
    ) -> Tuple[ContainerClient, str, str]:
        """Call startPendingUpload to get a SAS URI and return a ContainerClient and blob URI.

        :param name: The evaluator name.
        :type name: str
        :param version: The evaluator version.
        :type version: str
        :param connection_name: Optional storage account connection name.
        :type connection_name: Optional[str]
        :return: A tuple of (ContainerClient, version, blob_uri).
        :rtype: Tuple[ContainerClient, str, str]
        """

        request_body: dict = {}
        if connection_name:
            request_body["connectionName"] = connection_name

        pending_upload_response = await self.pending_upload(
            name=name,
            version=version,
            pending_upload_request=request_body,
            headers={_FOUNDRY_FEATURES_HEADER_NAME: _EVALUATORS_FOUNDRY_FEATURES_VALUE},
        )

        # The service returns blobReferenceForConsumption
        blob_ref = pending_upload_response.get("blobReferenceForConsumption")
        if not blob_ref:
            raise ValueError("Blob reference is not present in the pending upload response")

        credential = blob_ref.get("credential") if isinstance(blob_ref, dict) else None
        if not credential:
            raise ValueError("SAS credential is not present in the pending upload response")

        sas_uri = credential.get("sasUri") if isinstance(credential, dict) else None
        if not sas_uri:
            raise ValueError("SAS URI is missing or empty in the pending upload response")

        blob_uri = blob_ref.get("blobUri") if isinstance(blob_ref, dict) else None
        if not blob_uri:
            raise ValueError("Blob URI is missing or empty in the pending upload response")

        return (
            ContainerClient.from_container_url(container_url=sas_uri),
            version,
            blob_uri,
        )

    async def _get_next_version(self, name: str) -> str:
        """Get the next version number for an evaluator by fetching existing versions.

        :param name: The evaluator name.
        :type name: str
        :return: The next version number as a string.
        :rtype: str
        """
        try:
            versions = []
            async for v in self.list_versions(
                name=name, headers={_FOUNDRY_FEATURES_HEADER_NAME: _EVALUATORS_FOUNDRY_FEATURES_VALUE}
            ):
                versions.append(v)
            if versions:
                numeric_versions = []
                for v in versions:
                    ver = v.get("version") if isinstance(v, dict) else getattr(v, "version", None)
                    if ver and ver.isdigit():
                        numeric_versions.append(int(ver))
                if numeric_versions:
                    return str(max(numeric_versions) + 1)
            return "1"
        except ResourceNotFoundError:
            return "1"

    @distributed_trace_async
    async def upload(
        self,
        name: str,
        evaluator_version: Union[EvaluatorVersion, JSON, IO[bytes]],
        *,
        folder: str,
        connection_name: Optional[str] = None,
        **kwargs: Any,
    ) -> EvaluatorVersion:
        """Upload all files in a folder to blob storage and create a code-based evaluator version
        that references the uploaded code.

        This method calls startPendingUpload to get a SAS URI, uploads files from the folder
        to blob storage, then creates an evaluator version referencing the uploaded blob.

        The version is automatically determined by incrementing the latest existing version.

        :param name: The name of the evaluator. Required.
        :type name: str
        :param evaluator_version: The evaluator version definition. This is the same object accepted
         by ``create_version``. Is one of the following types: EvaluatorVersion, JSON,
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

        version = await self._get_next_version(name)
        logger.info("[upload] Auto-resolved version to '%s'.", version)

        # Get SAS URI via startPendingUpload
        container_client, _, blob_uri = await self._start_pending_upload_and_get_container_client(
            name=name,
            version=version,
            connection_name=connection_name,
        )

        async with container_client:
            await self._upload_folder_to_blob(container_client, folder, **kwargs)
            self._set_blob_uri(evaluator_version, blob_uri)

            result = await self.create_version(
                name=name,
                evaluator_version=evaluator_version,
                headers={_FOUNDRY_FEATURES_HEADER_NAME: _EVALUATORS_FOUNDRY_FEATURES_VALUE},
            )

        return result
