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
from urllib.parse import urlsplit
from azure.storage.blob import ContainerClient
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from ._operations import BetaEvaluatorsOperations as EvaluatorsOperationsGenerated, JSON
from ..models._models import (
    EvaluatorVersion,
)

logger = logging.getLogger(__name__)


class EvaluatorsOperations(EvaluatorsOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`beta.evaluators` attribute.
    """

    def _start_pending_upload_and_get_container_client(
        self,
        name: str,
        version: str,
        connection_name: Optional[str] = None,
    ) -> Tuple[ContainerClient, str, str]:
        """Call startPendingUpload to get a SAS URI and return a ContainerClient and blob URI."""

        request_body: dict = {}
        if connection_name:
            request_body["connectionName"] = connection_name

        try:
            pending_upload_response = self.pending_upload(
                name=name,
                version=version,
                pending_upload_request=request_body,
            )
        except HttpResponseError as e:
            if e.message and "409" in e.message:
                raise ValueError(
                    f"Evaluator '{name}' version '{version}' already exists. "
                    f"Use a different version, delete the existing version with "
                    f"'client.beta.evaluators.delete_version(name=\"{name}\", version=\"{version}\")' "
                    f"before uploading, or set 'overwrite=True' in the upload call."
                ) from e
            raise

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

    def _get_next_version(self, name: str) -> str:
        """Get the next version number for an evaluator by fetching existing versions."""
        try:
            versions = list(self.list_versions(name=name))
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

    @distributed_trace
    def upload(
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

        version = self._get_next_version(name)
        logger.info("[upload] Auto-resolved version to '%s'.", version)

        # Get SAS URI via startPendingUpload
        container_client, output_version, blob_uri = self._start_pending_upload_and_get_container_client(
            name=name,
            version=version,
            connection_name=connection_name,
        )

        with container_client:
            # Upload all files from the folder (including nested subdirectories)
            skip_dirs = {"__pycache__", ".git", ".venv", "venv", "node_modules"}
            skip_extensions = {".pyc", ".pyo"}
            files_uploaded: bool = False
            for root, dirs, files in os.walk(folder):
                # Prune directories we don't want to traverse
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                for file in files:
                    if any(file.endswith(ext) for ext in skip_extensions):
                        continue
                    file_path = os.path.join(root, file)
                    blob_name = os.path.relpath(file_path, folder).replace("\\", "/")
                    logger.debug(
                        "[upload] Start uploading file `%s` as blob `%s`.",
                        file_path,
                        blob_name,
                    )
                    with open(file=file_path, mode="rb") as data:
                        try:
                            container_client.upload_blob(name=str(blob_name), data=data, **kwargs)
                        except HttpResponseError as e:
                            if e.error_code == "AuthorizationPermissionMismatch":
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

            # Set the blob_uri in the evaluator version definition
            if isinstance(evaluator_version, dict):
                definition = evaluator_version.get("definition", {})
                if isinstance(definition, dict):
                    definition["blob_uri"] = blob_uri
                else:
                    definition.blob_uri = blob_uri
            else:
                if hasattr(evaluator_version, "definition") and evaluator_version.definition:
                    evaluator_version.definition.blob_uri = blob_uri

            result = self.create_version(
                name=name,
                evaluator_version=evaluator_version,
            )

        return result
