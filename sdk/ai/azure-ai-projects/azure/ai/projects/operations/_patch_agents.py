# pylint: disable=line-too-long,useless-suppression,pointless-string-statement
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import hashlib
import os
from pathlib import Path
from typing import Union, Optional, Any, IO, overload
from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace
from ._operations import AgentsOperations as GeneratedAgentsOperations, JSON, _Unset
from .. import models as _models
from ..models._patch import (
    _FOUNDRY_FEATURES_HEADER_NAME,
    _has_header_case_insensitive,
    _AGENT_OPERATION_FEATURE_HEADERS,
    _PREVIEW_FEATURE_REQUIRED_CODE,
    _PREVIEW_FEATURE_ADDED_ERROR_MESSAGE,
)


class AgentsOperations(GeneratedAgentsOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`agents` attribute.
    """

    @overload
    def create_version(
        self,
        agent_name: str,
        *,
        definition: _models.AgentDefinition,
        content_type: str = "application/json",
        metadata: Optional[dict[str, str]] = None,
        description: Optional[str] = None,
        blueprint_reference: Optional[_models.AgentBlueprintReference] = None,
        **kwargs: Any,
    ) -> _models.AgentVersionDetails:
        """Create a new agent version.

        :param agent_name: The unique name that identifies the agent. Name can be used to
         retrieve/update/delete the agent.

         * Must start and end with alphanumeric characters,
         * Can contain hyphens in the middle
         * Must not exceed 63 characters. Required.
        :type agent_name: str
        :keyword definition: The agent definition. This can be a workflow, hosted agent, or a simple
         agent definition. Required.
        :paramtype definition: ~azure.ai.projects.models.AgentDefinition
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword metadata: Set of 16 key-value pairs that can be attached to an object. This can be
         useful for storing additional information about the object in a structured
         format, and querying for objects via API or the dashboard.

         Keys are strings with a maximum length of 64 characters. Values are strings
         with a maximum length of 512 characters. Default value is None.
        :paramtype metadata: dict[str, str]
        :keyword description: A human-readable description of the agent. Default value is None.
        :paramtype description: str
        :keyword blueprint_reference: The blueprint reference for the agent. Default value is None.
        :paramtype blueprint_reference: ~azure.ai.projects.models.AgentBlueprintReference
        :return: AgentVersionDetails. The AgentVersionDetails is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.AgentVersionDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @overload
    def create_version(
        self, agent_name: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.AgentVersionDetails:
        """Create a new agent version.

        :param agent_name: The unique name that identifies the agent. Name can be used to
         retrieve/update/delete the agent.

         * Must start and end with alphanumeric characters,
         * Can contain hyphens in the middle
         * Must not exceed 63 characters. Required.
        :type agent_name: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AgentVersionDetails. The AgentVersionDetails is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.AgentVersionDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @overload
    def create_version(
        self, agent_name: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.AgentVersionDetails:
        """Create a new agent version.

        :param agent_name: The unique name that identifies the agent. Name can be used to
         retrieve/update/delete the agent.

         * Must start and end with alphanumeric characters,
         * Can contain hyphens in the middle
         * Must not exceed 63 characters. Required.
        :type agent_name: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AgentVersionDetails. The AgentVersionDetails is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.AgentVersionDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @distributed_trace
    def create_version(
        self,
        agent_name: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        definition: _models.AgentDefinition = _Unset,
        metadata: Optional[dict[str, str]] = None,
        description: Optional[str] = None,
        blueprint_reference: Optional[_models.AgentBlueprintReference] = None,
        **kwargs: Any,
    ) -> _models.AgentVersionDetails:
        """Create a new agent version.

        :param agent_name: The unique name that identifies the agent. Name can be used to
         retrieve/update/delete the agent.

         * Must start and end with alphanumeric characters,
         * Can contain hyphens in the middle
         * Must not exceed 63 characters. Required.
        :type agent_name: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword definition: The agent definition. This can be a workflow, hosted agent, or a simple
         agent definition. Required.
        :paramtype definition: ~azure.ai.projects.models.AgentDefinition
        :keyword metadata: Set of 16 key-value pairs that can be attached to an object. This can be
         useful for storing additional information about the object in a structured
         format, and querying for objects via API or the dashboard.

         Keys are strings with a maximum length of 64 characters. Values are strings
         with a maximum length of 512 characters. Default value is None.
        :paramtype metadata: dict[str, str]
        :keyword description: A human-readable description of the agent. Default value is None.
        :paramtype description: str
        :keyword blueprint_reference: The blueprint reference for the agent. Default value is None.
        :paramtype blueprint_reference: ~azure.ai.projects.models.AgentBlueprintReference
        :return: AgentVersionDetails. The AgentVersionDetails is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.AgentVersionDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if getattr(self._config, "allow_preview", False):
            # Add Foundry-Features header if not already present
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _AGENT_OPERATION_FEATURE_HEADERS}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _AGENT_OPERATION_FEATURE_HEADERS
                kwargs["headers"] = headers

        try:
            return super().create_version(
                agent_name,
                body,
                definition=definition,
                metadata=metadata,
                description=description,
                blueprint_reference=blueprint_reference,
                **kwargs,
            )
        except HttpResponseError as exc:
            """
            Example service response payload when the caller is trying to use a feature preview without opt-in flag (service error 403 (Forbidden)):

            "error": {
                "code": "preview_feature_required",
                "message": "Workflow agents is in preview. This operation requires the following opt-in preview feature(s): WorkflowAgents=V1Preview. Include the 'Foundry-Features: WorkflowAgents=V1Preview' header in your request.",
                "param": "Foundry-Features",
                "type": "invalid_request_error",
                "details": [],
                "additionalInfo": {
                "request_id": "fdbc95804b7599404973026cd9ec732a"
                }
            }

            """
            if exc.status_code == 403 and not self._config.allow_preview and exc.model is not None:
                api_error_response = exc.model
                if hasattr(api_error_response, "error") and api_error_response.error is not None:
                    if api_error_response.error.code == _PREVIEW_FEATURE_REQUIRED_CODE:
                        new_exc = HttpResponseError(
                            message=f"{exc.message} {_PREVIEW_FEATURE_ADDED_ERROR_MESSAGE}",
                        )
                        new_exc.status_code = exc.status_code
                        new_exc.reason = exc.reason
                        new_exc.response = exc.response
                        new_exc.model = exc.model
                        raise new_exc from exc
            raise

    @overload
    def upload_session_file(
        self,
        agent_name: str,
        session_id: str,
        *,
        content: bytes,
        remote_path: str,
        **kwargs: Any,
    ) -> _models.SessionFileWriteResult:
        """Upload binary content to the session sandbox.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param session_id: The session ID. Required.
        :type session_id: str
        :keyword content: The binary content to upload. Required.
        :paramtype content: bytes
        :keyword remote_path: The destination file path within the sandbox, relative to the session home
         directory. Required.
        :paramtype remote_path: str
        :return: SessionFileWriteResult. The SessionFileWriteResult is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.SessionFileWriteResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @overload
    def upload_session_file(
        self,
        agent_name: str,
        session_id: str,
        *,
        file_path: Union[str, "os.PathLike[str]"],
        remote_path: str,
        **kwargs: Any,
    ) -> _models.SessionFileWriteResult:
        """Upload a file from disk to the session sandbox.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param session_id: The session ID. Required.
        :type session_id: str
        :keyword file_path: The full path to a local file whose contents should be uploaded. Required.
        :paramtype file_path: str or os.PathLike[str]
        :keyword remote_path: The destination file path within the sandbox, relative to the session home
         directory. Required.
        :paramtype remote_path: str
        :return: SessionFileWriteResult. The SessionFileWriteResult is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.SessionFileWriteResult
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises FileNotFoundError: If *file_path* does not exist.
        """
        ...

    @distributed_trace
    def upload_session_file(  # type: ignore[override]
        self,
        agent_name: str,
        session_id: str,
        *,
        content: Optional[bytes] = None,
        file_path: Optional[Union[str, "os.PathLike[str]"]] = None,
        remote_path: str,
        **kwargs: Any,
    ) -> _models.SessionFileWriteResult:
        """Upload a file to the session sandbox.

        Accepts either binary content directly or a local file path.
        When a file path is provided the file is read from disk and its contents
        are forwarded to the service. Maximum file size is 50 MB. Uploads
        exceeding this limit return 413 Payload Too Large.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param session_id: The session ID. Required.
        :type session_id: str
        :keyword content: The binary content to upload. Mutually exclusive with *file_path*.
        :paramtype content: bytes
        :keyword file_path: The full path to a local file whose contents should be uploaded.
         Mutually exclusive with *content*.
        :paramtype file_path: str or os.PathLike[str]
        :keyword remote_path: The destination file path within the sandbox, relative to the session home
         directory. Required.
        :paramtype remote_path: str
        :return: SessionFileWriteResult. The SessionFileWriteResult is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.SessionFileWriteResult
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ValueError: If both *content* and *file_path* are provided, or neither is provided.
        :raises FileNotFoundError: If *file_path* is provided and does not exist.
        """
        if content is not None and file_path is not None:
            raise ValueError("Specify either 'content' or 'file_path', not both.")
        if content is None and file_path is None:
            raise ValueError("Specify either 'content' or 'file_path'.")

        if file_path is not None:
            p = Path(file_path)
            if not p.exists():
                raise FileNotFoundError(f"The provided file `{file_path}` does not exist.")
            if p.is_dir():
                raise ValueError(f"Provide a valid file path, not a folder path `{file_path}`.")
            with open(file_path, "rb") as f:
                content = f.read()

        assert content is not None  # Guaranteed by validation above

        return super()._upload_session_file(agent_name, session_id, content, remote_path=remote_path, **kwargs)

    @distributed_trace
    def download_session_file_to_path(
        self,
        agent_name: str,
        session_id: str,
        *,
        file_path: Union[str, "os.PathLike[str]"],
        overwrite: bool = False,
        remote_path: str,
        **kwargs: Any,
    ) -> None:
        """Download a session file directly to disk.

        Downloads the file at the specified sandbox path and writes it to a local file.
        The remote path is resolved relative to the session home directory.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param session_id: The session ID. Required.
        :type session_id: str
        :keyword file_path: The full path to the local file where the content should be written. Required.
        :paramtype file_path: str or os.PathLike[str]
        :keyword overwrite: If True, overwrite the local file if it already exists. If False (default),
         raise FileExistsError when the file already exists.
        :paramtype overwrite: bool
        :keyword remote_path: The file path to download from the sandbox, relative to the session home
         directory. Required.
        :paramtype remote_path: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises FileExistsError: If *file_path* already exists and *overwrite* is False.
        :raises ValueError: If *file_path* points to a directory.
        :raises OSError: If the file cannot be written.
        """
        p = Path(file_path)
        if p.exists():
            if p.is_dir():
                raise ValueError(f"Provide a valid file path, not a folder path `{file_path}`.")
            if not overwrite:
                raise FileExistsError(f"The file `{file_path}` already exists. Set overwrite=True to replace it.")

        # Download the file content using the existing method
        content_iterator = self.download_session_file_as_bytes(
            agent_name=agent_name,
            agent_session_id=session_id,
            remote_path=remote_path,
            **kwargs,
        )

        # Write the content to disk
        with open(file_path, "wb") as f:
            for chunk in content_iterator:
                f.write(chunk)

    @distributed_trace
    def download_code_to_path(
        self,
        agent_name: str,
        *,
        file_path: Union[str, "os.PathLike[str]"],
        overwrite: bool = False,
        agent_version: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Download agent code directly to disk.

        Downloads the code zip for a code-based hosted agent and writes it to a local file.

        If ``agent_version`` is supplied, downloads that version's code zip; otherwise
        downloads the latest version's code zip.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :keyword file_path: The full path to the local file where the code zip should be written. Required.
        :paramtype file_path: str or os.PathLike[str]
        :keyword overwrite: If True, overwrite the local file if it already exists. If False (default),
         raise FileExistsError when the file already exists.
        :paramtype overwrite: bool
        :keyword agent_version: The version of the agent whose code zip should be downloaded.
         If omitted, the latest version's code zip is downloaded. Default value is None.
        :paramtype agent_version: str
        :return: The SHA-256 hex digest of the downloaded file.
        :rtype: str
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises FileExistsError: If *file_path* already exists and *overwrite* is False.
        :raises ValueError: If *file_path* points to a directory.
        :raises OSError: If the file cannot be written.
        """
        p = Path(file_path)
        if p.exists():
            if p.is_dir():
                raise ValueError(f"Provide a valid file path, not a folder path `{file_path}`.")
            if not overwrite:
                raise FileExistsError(f"The file `{file_path}` already exists. Set overwrite=True to replace it.")

        # Download the code content using the existing method
        content_iterator = self.download_code_as_bytes(
            agent_name=agent_name,
            agent_version=agent_version,
            **kwargs,
        )

        # Write the content to disk and calculate SHA-256
        sha = hashlib.sha256()
        with open(file_path, "wb") as f:
            for chunk in content_iterator:
                f.write(chunk)
                sha.update(chunk)

        return sha.hexdigest()
