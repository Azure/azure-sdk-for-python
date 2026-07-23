# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from io import IOBase
from collections.abc import MutableMapping as MutableMappingABC
from typing import (
    Union,
    Optional,
    Any,
    IO,
    AsyncIterator,
    overload,
    cast,
    MutableMapping,
)

from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator_async import distributed_trace_async
from ._operations import AgentsOperations as GeneratedAgentsOperations, JSON, _Unset
from ... import models as _models
from ...operations._patch_agents import _compute_sha256_from_stream
from ...models._patch import (
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
        :class:`~azure.ai.projects.aio.AIProjectClient`'s
        :attr:`agents` attribute.
    """

    @overload  # type: ignore[override]
    async def create_version(
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
    async def create_version(
        self,
        agent_name: str,
        body: MutableMapping[str, Any],
        *,
        content_type: str = "application/json",
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
        :param body: Required.
        :type body: MutableMapping[str, Any]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AgentVersionDetails. The AgentVersionDetails is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.AgentVersionDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def create_version(
        self,
        agent_name: str,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
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
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: AgentVersionDetails. The AgentVersionDetails is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.AgentVersionDetails
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def create_version(
        self,
        agent_name: str,
        body: Union[JSON, MutableMapping[str, Any], IO[bytes]] = _Unset,
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
        :type body: JSON or MutableMapping[str, Any] or IO[bytes]
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
                kwargs["headers"] = {
                    _FOUNDRY_FEATURES_HEADER_NAME: _AGENT_OPERATION_FEATURE_HEADERS
                }
            elif not _has_header_case_insensitive(
                headers, _FOUNDRY_FEATURES_HEADER_NAME
            ):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = (
                    _AGENT_OPERATION_FEATURE_HEADERS
                )
                kwargs["headers"] = headers

        try:
            if body is _Unset:
                # Use keyword-only overload when body is not provided
                return await super().create_version(
                    agent_name,
                    definition=definition,
                    metadata=metadata,
                    description=description,
                    blueprint_reference=blueprint_reference,
                    draft=draft,
                    **kwargs,
                )
            # Use body overload when body is provided
            if isinstance(body, (IOBase, bytes)):
                typed_body: Union[MutableMapping[str, Any], IO[bytes]] = body
            else:
                # Strip service-owned fields from MutableMapping bodies before delegation
                if isinstance(body, MutableMappingABC):
                    body_copy = dict(body)
                    # Remove service-owned response fields per task requirements
                    for key in [
                        "object",
                        "id",
                        "name",
                        "version",
                        "createdAt",
                        "created_at",
                        "status",
                        "instanceIdentity",
                        "instance_identity",
                        "blueprint",
                        "agentGuid",
                        "agent_guid",
                    ]:
                        body_copy.pop(key, None)

                    typed_body = body_copy  # type: ignore[assignment]
                else:
                    typed_body = body  # type: ignore[assignment]
            return await super().create_version(
                agent_name,
                cast(Any, typed_body),
                **kwargs,
            )
        except HttpResponseError as exc:
            if (
                exc.status_code == 403
                and not self._config.allow_preview
                and exc.model is not None
            ):
                api_error_response = exc.model
                if (
                    hasattr(api_error_response, "error")
                    and api_error_response.error is not None
                ):
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

    @distributed_trace_async
    async def create_version_from_code(
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
                kwargs["headers"] = {
                    _FOUNDRY_FEATURES_HEADER_NAME: _AGENT_OPERATION_FEATURE_HEADERS
                }
            elif not _has_header_case_insensitive(
                headers, _FOUNDRY_FEATURES_HEADER_NAME
            ):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = (
                    _AGENT_OPERATION_FEATURE_HEADERS
                )
                kwargs["headers"] = headers

        try:
            return await super()._create_version_from_code(
                agent_name, content, code_zip_sha256=code_zip_sha256, **kwargs
            )
        except HttpResponseError as exc:
            if (
                exc.status_code == 403
                and not self._config.allow_preview
                and exc.model is not None
            ):
                api_error_response = exc.model
                if (
                    hasattr(api_error_response, "error")
                    and api_error_response.error is not None
                ):
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

    @distributed_trace_async
    async def get_session_log_stream(  # type: ignore[override]
        self,
        agent_name: str,
        agent_version: str,
        session_id: str,
        *,
        stream: bool = True,
        **kwargs: Any,
    ) -> AsyncIterator[bytes]:
        """Stream console logs for a hosted agent session.

        Streams console logs (stdout / stderr) for a specific hosted agent session
        as a Server-Sent Events (SSE) stream.

        Each SSE frame contains:

        * `event`: always `"log"`
        * `data`: a plain-text log line (currently JSON-formatted, but the schema
        is not contractual and may include additional keys or change format
        over time — clients should treat it as an opaque string)

        Example SSE frames:

        .. code-block::

           event: log
           data: {"timestamp":"2026-03-10T09:33:17.121Z","stream":"stdout","message":"Starting FoundryCBAgent server on port 8088"}

           event: log
           data: {"timestamp":"2026-03-10T09:33:17.130Z","stream":"stderr","message":"INFO: Application startup complete."}

           event: log
           data: {"timestamp":"2026-03-10T09:34:52.714Z","stream":"status","message":"Successfully connected to container"}

           event: log
           data: {"timestamp":"2026-03-10T09:35:52.714Z","stream":"status","message":"No logs since last 60 seconds"}

        The stream remains open until the client disconnects or the server
        terminates the connection. Clients should handle reconnection as needed.

        :param agent_name: The name of the hosted agent. Required.
        :type agent_name: str
        :param agent_version: The version of the agent. Required.
        :type agent_version: str
        :param session_id: The session ID (maps to an ADC sandbox). Required.
        :type session_id: str
        :keyword stream: Whether to stream the response. Default is True.
        :paramtype stream: bool
        :return: Async iterator of bytes containing SSE frames
        :rtype: AsyncIterator[bytes]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return cast(
            AsyncIterator[bytes],
            await super().get_session_log_stream(
                agent_name, agent_version, session_id, stream=stream, **kwargs
            ),
        )
