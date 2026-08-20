# pylint: disable=line-too-long,useless-suppression,pointless-string-statement
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import hashlib
from io import IOBase
from typing import Union, Optional, Any, IO, cast, overload, TYPE_CHECKING
from azure.core.exceptions import HttpResponseError
from azure.core.polling import NoPolling, PollingMethod
from azure.core.polling.base_polling import LROBasePolling
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict
from ._operations import (
    AgentsOperations as GeneratedAgentsOperations,
    BetaAgentsOperations as BetaAgentsOperationsGenerated,
    JSON,
    _Unset,
)
from .. import models as _models
from .._utils.model_base import _deserialize
from ..models import AgentOptimizationLROPoller
from ..models._patch import (
    _FOUNDRY_FEATURES_HEADER_NAME,
    _has_header_case_insensitive,
    _AGENT_OPERATION_FEATURE_HEADERS,
    _PREVIEW_FEATURE_REQUIRED_CODE,
    _PREVIEW_FEATURE_ADDED_ERROR_MESSAGE,
)

if TYPE_CHECKING:
    from .. import _unions


def _compute_sha256_from_stream(stream: IO[bytes], *, chunk_size: int = 1024 * 1024) -> str:
    if not isinstance(stream, IOBase) or not stream.seekable():
        raise TypeError("'code' must be provided as a seekable IO[bytes] stream.")

    stream.seek(0)
    digest = hashlib.sha256()
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        if isinstance(chunk, str):
            raise TypeError("'code' must be provided as IO[bytes], not text IO.")
        digest.update(chunk)
    stream.seek(0)
    return digest.hexdigest()


class AgentsOperations(GeneratedAgentsOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`agents` attribute.
    """

    @overload  # type: ignore[override]
    def create_version(
        self,
        agent_name: str,
        *,
        definition: _models.AgentDefinition,
        content_type: str = "application/json",
        metadata: Optional[dict[str, str]] = None,
        description: Optional[str] = None,
        blueprint_reference: Optional[_models.AgentBlueprintReference] = None,
        draft: Optional[bool] = None,
        **kwargs: Any,
    ) -> _models.AgentVersionDetails:
        """Create an agent version.

        Creates a new version for the specified agent and returns the created version resource.

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
        :keyword draft: (Preview) Whether this agent version is a draft (candidate) rather than a
         release. The service defaults to ``false`` if a value is not specified by the caller. Draft
         versions are recorded but excluded from default 'latest' resolution and are not auto-promoted.
         Default value is None.
        :paramtype draft: bool
        :return: AgentVersionDetails. The AgentVersionDetails is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.AgentVersionDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_version(
        self, agent_name: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.AgentVersionDetails:
        """Create an agent version.

        Creates a new version for the specified agent and returns the created version resource.

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

    @overload
    def create_version(
        self, agent_name: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.AgentVersionDetails:
        """Create an agent version.

        Creates a new version for the specified agent and returns the created version resource.

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

    @distributed_trace
    def create_version(  # type: ignore[override]
        self,
        agent_name: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        definition: _models.AgentDefinition = _Unset,
        metadata: Optional[dict[str, str]] = None,
        description: Optional[str] = None,
        blueprint_reference: Optional[_models.AgentBlueprintReference] = None,
        draft: Optional[bool] = None,
        **kwargs: Any,
    ) -> _models.AgentVersionDetails:
        """Create an agent version.

        Creates a new version for the specified agent and returns the created version resource.

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
        :keyword draft: (Preview) Whether this agent version is a draft (candidate) rather than a
         release. The service defaults to ``false`` if a value is not specified by the caller. Draft
         versions are recorded but excluded from default 'latest' resolution and are not auto-promoted.
         Default value is None.
        :paramtype draft: bool
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
            return super().create_version(  # type: ignore[misc]
                agent_name,
                body,  # type: ignore[arg-type]
                definition=definition,
                metadata=metadata,
                description=description,
                blueprint_reference=blueprint_reference,
                draft=draft,
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

    @distributed_trace
    def create_version_from_code(
        self,
        agent_name: str,
        *,
        definition: _models.HostedAgentDefinition,
        code: IO[bytes],
        code_zip_sha256: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> _models.AgentVersionDetails:
        """Create an agent version from code.

        Creates a new agent version from code. Uploads the code zip and creates a new version for an
        existing agent. The SHA-256 hex digest of the zip is provided in the ``x-ms-code-zip-sha256``
        header for integrity and dedup. The request body is multipart/form-data with a JSON metadata
        part and a binary code part (part order is irrelevant). Maximum upload size is 250 MB.

        :param agent_name: The unique name that identifies the agent. Name can be used to
         retrieve/update/delete the agent.

         * Must start and end with alphanumeric characters,
         * Can contain hyphens in the middle
         * Must not exceed 63 characters. Required.
        :type agent_name: str
        :keyword definition: The hosted agent definition including code_configuration (runtime,
         entry_point), cpu, memory, and protocol_versions. Required.
        :paramtype definition: ~azure.ai.projects.models.HostedAgentDefinition
        :keyword code: The code zip file stream (max 250 MB). Required. The stream must
         expose a ``name`` attribute (for example, a stream returned by
         :meth:`pathlib.Path.open`) and that name must end with ``.zip``.
        :paramtype code: IO[bytes]
        :keyword code_zip_sha256: SHA-256 hex digest of the uploaded code zip. Used for change
         detection (dedup) and integrity verification. If not provided, it will be calculated
         automatically from the code content. Default value is None.
        :paramtype code_zip_sha256: str
        :keyword description: A human-readable description of the agent. Default value is None.
        :paramtype description: str
        :keyword metadata: Set of 16 key-value pairs that can be attached to an object. This can be
         useful for storing additional information about the object in a structured
         format, and querying for objects via API or the dashboard.

         Keys are strings with a maximum length of 64 characters. Values are strings
         with a maximum length of 512 characters. Default value is None.
        :paramtype metadata: dict[str, str]
        :return: AgentVersionDetails. The AgentVersionDetails is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.AgentVersionDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        # If code_zip_sha256 is not provided, calculate it from the code content
        if code_zip_sha256 is None:
            code_zip_sha256 = _compute_sha256_from_stream(code)

        # Build content from expanded parameters using internal model classes
        metadata_obj = _models._models._CreateAgentVersionFromCodeMetadata(  # pylint: disable=protected-access
            definition=definition,
            description=description,
            metadata=metadata,
        )
        content = _models._models._CreateAgentVersionFromCodeContent(  # pylint: disable=protected-access
            metadata=metadata_obj,
            code=code,
        )

        if getattr(self._config, "allow_preview", False):
            # Add Foundry-Features header if not already present
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _AGENT_OPERATION_FEATURE_HEADERS}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _AGENT_OPERATION_FEATURE_HEADERS
                kwargs["headers"] = headers

        try:
            return super()._create_version_from_code(
                agent_name,
                content,
                code_zip_sha256=code_zip_sha256,
                **kwargs,
            )
        except HttpResponseError as exc:
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


class BetaAgentsOperations(BetaAgentsOperationsGenerated):
    """Custom operations for beta agent optimization jobs."""

    @overload
    def begin_create_optimization_job(
        self,
        job: _models.AgentOptimizationJob,
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AgentOptimizationLROPoller: ...

    @overload
    def begin_create_optimization_job(
        self,
        job: JSON,
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AgentOptimizationLROPoller: ...

    @overload
    def begin_create_optimization_job(
        self,
        job: IO[bytes],
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AgentOptimizationLROPoller: ...

    @distributed_trace
    def begin_create_optimization_job(
        self,
        job: Union[_models.AgentOptimizationJob, JSON, IO[bytes]],
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AgentOptimizationLROPoller:
        """Create an agent optimization job.

        :param job: The job to create. Required.
        :type job: ~azure.ai.projects.models.AgentOptimizationJob or JSON or IO[bytes]
        :keyword operation_id: Client-generated unique ID for idempotent retries. When absent, the
         server creates the job unconditionally. Default value is None.
        :paramtype operation_id: str
        :return: A poller that returns AgentOptimizationJobResult and exposes the job ID in ``details``.
        :rtype: ~azure.ai.projects.models.AgentOptimizationLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", headers.pop("Content-Type", None))
        cls = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        continuation_token: Optional[str] = kwargs.pop("continuation_token", None)
        raw_result = None
        if continuation_token is None:
            raw_result = self._create_optimization_job_initial(
                job=job,
                operation_id=operation_id,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=headers,
                params=params,
                **kwargs,
            )
            raw_result.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )
            response_headers["Location"] = self._deserialize("str", response.headers.get("Location"))

            deserialized = _deserialize(_models.AgentOptimizationJobResult, response.json().get("result", {}))
            if cls:
                return cls(pipeline_response, deserialized, response_headers)
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: PollingMethod = cast(
                PollingMethod, LROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs)
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if continuation_token:
            return AgentOptimizationLROPoller.from_continuation_token(
                polling_method=polling_method,
                continuation_token=continuation_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        assert raw_result is not None
        return AgentOptimizationLROPoller(self._client, raw_result, get_long_running_output, polling_method)  # type: ignore

    @distributed_trace
    def generate_agent(self, body: _models.GenerateVoiceAgentRequest, **kwargs: Any) -> _models.AgentDetails:  # type: ignore[override]
        """Generate an agent.

        Generates and creates an agent from kind-specific high-level inputs. The generated definition
        remains fully editable through the standard agent versioning operations. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param body: The kind-specific inputs for generating and creating an agent. Required.
        :type body: ~azure.ai.projects.models.GenerateVoiceAgentRequest
        :return: AgentDetails. The AgentDetails is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.AgentDetails
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
            return super().generate_agent(body, **kwargs)  # type: ignore[misc]
        except HttpResponseError as exc:
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
