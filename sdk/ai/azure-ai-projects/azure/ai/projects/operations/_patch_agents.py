# pylint: disable=line-too-long,useless-suppression,pointless-string-statement,too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import datetime
import hashlib
from io import IOBase
from typing import Union, Optional, Any, IO, List, cast, overload, TYPE_CHECKING
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
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

    @overload  # type: ignore[override]
    def create_telephony_binding(
        self,
        agent_name: str,
        body: _models.CreateTelephonyBindingRequest,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.TelephonyBinding:
        """Create an agent telephony binding.

        Creates a telephony binding for the voice agent named in the path. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the voice agent that owns the binding. Required.
        :type agent_name: str
        :param body: The provider-specific binding to create. Required.
        :type body: ~azure.ai.projects.models.CreateTelephonyBindingRequest
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TelephonyBinding. The TelephonyBinding is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyBinding
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_telephony_binding(
        self, agent_name: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.TelephonyBinding:
        """Create an agent telephony binding.

        Creates a telephony binding for the voice agent named in the path. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the voice agent that owns the binding. Required.
        :type agent_name: str
        :param body: The provider-specific binding to create. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TelephonyBinding. The TelephonyBinding is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyBinding
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_telephony_binding(
        self, agent_name: str, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.TelephonyBinding:
        """Create an agent telephony binding.

        Creates a telephony binding for the voice agent named in the path. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the voice agent that owns the binding. Required.
        :type agent_name: str
        :param body: The provider-specific binding to create. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TelephonyBinding. The TelephonyBinding is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyBinding
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_telephony_binding(  # type: ignore[override]
        self, agent_name: str, body: Union[_models.CreateTelephonyBindingRequest, JSON, IO[bytes]], **kwargs: Any
    ) -> _models.TelephonyBinding:
        """Create an agent telephony binding.

        Creates a telephony binding for the voice agent named in the path. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the voice agent that owns the binding. Required.
        :type agent_name: str
        :param body: The provider-specific binding to create. Is one of the following types:
         CreateTelephonyBindingRequest, JSON, IO[bytes] Required.
        :type body: ~azure.ai.projects.models.CreateTelephonyBindingRequest or JSON or IO[bytes]
        :return: TelephonyBinding. The TelephonyBinding is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyBinding
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
            return super().create_telephony_binding(agent_name, body, **kwargs)  # type: ignore[arg-type]
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

    @distributed_trace
    def list_telephony_bindings(  # type: ignore[override]
        self,
        agent_name: str,
        *,
        provider: Optional[Union[str, _models.TelephonyProvider]] = None,
        status: Optional[Union[str, _models.TelephonyBindingStatus]] = None,
        limit: Optional[int] = None,
        order: Optional[Union[str, _models.PageOrder]] = None,
        before: Optional[str] = None,
        **kwargs: Any,
    ) -> ItemPaged["_models.TelephonyBindingListItem"]:
        """List agent telephony bindings.

        Returns the telephony bindings owned by the voice agent named in the path. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the voice agent whose bindings are listed. Required.
        :type agent_name: str
        :keyword provider: Filters bindings by provider. Known values are: "teams_phone_extension" and
         "twilio". Default value is None.
        :paramtype provider: str or ~azure.ai.projects.models.TelephonyProvider
        :keyword status: Filters bindings by lifecycle status. Known values are: "active" and
         "suspended". Default value is None.
        :paramtype status: str or ~azure.ai.projects.models.TelephonyBindingStatus
        :keyword limit: A limit on the number of objects to be returned. Default value is None.
        :paramtype limit: int
        :keyword order: Sort order by the ``created_at`` timestamp of the objects. Known values are:
         "asc" and "desc". Default value is None.
        :paramtype order: str or ~azure.ai.projects.models.PageOrder
        :keyword before: A cursor for use in pagination. Default value is None.
        :paramtype before: str
        :return: An iterator like instance of TelephonyBindingListItem
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.projects.models.TelephonyBindingListItem]
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

        return super().list_telephony_bindings(
            agent_name, provider=provider, status=status, limit=limit, order=order, before=before, **kwargs
        )

    @distributed_trace
    def get_telephony_binding(  # type: ignore[override]
        self, agent_name: str, binding_id: str, **kwargs: Any
    ) -> _models.TelephonyBinding:
        """Get an agent telephony binding.

        Retrieves a telephony binding owned by the voice agent named in the path. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the voice agent that owns the binding. Required.
        :type agent_name: str
        :param binding_id: The service-generated binding identifier. Required.
        :type binding_id: str
        :return: TelephonyBinding. The TelephonyBinding is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyBinding
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _AGENT_OPERATION_FEATURE_HEADERS}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _AGENT_OPERATION_FEATURE_HEADERS
                kwargs["headers"] = headers

        try:
            return super().get_telephony_binding(agent_name, binding_id, **kwargs)
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

    @overload  # type: ignore[override]
    def update_telephony_binding(
        self,
        agent_name: str,
        binding_id: str,
        body: _models.UpdateTelephonyBindingRequest,
        *,
        etag: str,
        match_condition: MatchConditions,
        content_type: str = "application/merge-patch+json",
        **kwargs: Any,
    ) -> _models.TelephonyBinding:
        """Update an agent telephony binding.

        Updates a telephony binding owned by the voice agent named in the path. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the voice agent that owns the binding. Required.
        :type agent_name: str
        :param binding_id: The service-generated binding identifier. Required.
        :type binding_id: str
        :param body: The binding properties to update. Required.
        :type body: ~azure.ai.projects.models.UpdateTelephonyBindingRequest
        :keyword etag: check if resource is changed. Set None to skip checking etag. Required.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Required.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/merge-patch+json".
        :paramtype content_type: str
        :return: TelephonyBinding. The TelephonyBinding is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyBinding
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def update_telephony_binding(
        self,
        agent_name: str,
        binding_id: str,
        body: JSON,
        *,
        etag: str,
        match_condition: MatchConditions,
        content_type: str = "application/merge-patch+json",
        **kwargs: Any,
    ) -> _models.TelephonyBinding:
        """Update an agent telephony binding.

        Updates a telephony binding owned by the voice agent named in the path. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the voice agent that owns the binding. Required.
        :type agent_name: str
        :param binding_id: The service-generated binding identifier. Required.
        :type binding_id: str
        :param body: The binding properties to update. Required.
        :type body: JSON
        :keyword etag: check if resource is changed. Set None to skip checking etag. Required.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Required.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/merge-patch+json".
        :paramtype content_type: str
        :return: TelephonyBinding. The TelephonyBinding is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyBinding
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def update_telephony_binding(
        self,
        agent_name: str,
        binding_id: str,
        body: IO[bytes],
        *,
        etag: str,
        match_condition: MatchConditions,
        content_type: str = "application/merge-patch+json",
        **kwargs: Any,
    ) -> _models.TelephonyBinding:
        """Update an agent telephony binding.

        Updates a telephony binding owned by the voice agent named in the path. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the voice agent that owns the binding. Required.
        :type agent_name: str
        :param binding_id: The service-generated binding identifier. Required.
        :type binding_id: str
        :param body: The binding properties to update. Required.
        :type body: IO[bytes]
        :keyword etag: check if resource is changed. Set None to skip checking etag. Required.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Required.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/merge-patch+json".
        :paramtype content_type: str
        :return: TelephonyBinding. The TelephonyBinding is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyBinding
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def update_telephony_binding(  # type: ignore[override]
        self,
        agent_name: str,
        binding_id: str,
        body: Union[_models.UpdateTelephonyBindingRequest, JSON, IO[bytes]],
        *,
        etag: str,
        match_condition: MatchConditions,
        **kwargs: Any,
    ) -> _models.TelephonyBinding:
        """Update an agent telephony binding.

        Updates a telephony binding owned by the voice agent named in the path. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the voice agent that owns the binding. Required.
        :type agent_name: str
        :param binding_id: The service-generated binding identifier. Required.
        :type binding_id: str
        :param body: The binding properties to update. Is one of the following types:
         UpdateTelephonyBindingRequest, JSON, IO[bytes] Required.
        :type body: ~azure.ai.projects.models.UpdateTelephonyBindingRequest or JSON or IO[bytes]
        :keyword etag: check if resource is changed. Set None to skip checking etag. Required.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Required.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: TelephonyBinding. The TelephonyBinding is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyBinding
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _AGENT_OPERATION_FEATURE_HEADERS}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _AGENT_OPERATION_FEATURE_HEADERS
                kwargs["headers"] = headers

        try:
            return super().update_telephony_binding(  # type: ignore[arg-type]
                agent_name, binding_id, body, etag=etag, match_condition=match_condition, **kwargs
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

    @distributed_trace
    def delete_telephony_binding(  # type: ignore[override] # pylint: disable=inconsistent-return-statements
        self, agent_name: str, binding_id: str, *, etag: str, match_condition: MatchConditions, **kwargs: Any
    ) -> None:
        """Delete an agent telephony binding.

        Deletes a telephony binding owned by the voice agent named in the path. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the voice agent that owns the binding. Required.
        :type agent_name: str
        :param binding_id: The service-generated binding identifier. Required.
        :type binding_id: str
        :keyword etag: check if resource is changed. Set None to skip checking etag. Required.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Required.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _AGENT_OPERATION_FEATURE_HEADERS}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _AGENT_OPERATION_FEATURE_HEADERS
                kwargs["headers"] = headers

        try:
            return super().delete_telephony_binding(agent_name, binding_id, etag=etag, match_condition=match_condition, **kwargs)  # type: ignore[misc]
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

    @distributed_trace
    def list_telephony_calls(  # type: ignore[override]
        self,
        agent_name: str,
        *,
        provider: Optional[Union[str, _models.TelephonyProvider]] = None,
        status: Optional[Union[str, _models.TelephonyCallStatus]] = None,
        started_after: Optional[datetime.datetime] = None,
        started_before: Optional[datetime.datetime] = None,
        limit: Optional[int] = None,
        order: Optional[Union[str, _models.PageOrder]] = None,
        before: Optional[str] = None,
        **kwargs: Any,
    ) -> ItemPaged["_models.TelephonyCallSummary"]:
        """List agent telephony calls.

        Returns the durable inbound call history for the voice agent named in the path. When the
        client is constructed with ``allow_preview=True``, the required preview opt-in header is
        added automatically.

        :param agent_name: The name of the voice agent whose calls are listed. Required.
        :type agent_name: str
        :keyword provider: Filters calls by provider. Known values are: "teams_phone_extension" and
         "twilio". Default value is None.
        :paramtype provider: str or ~azure.ai.projects.models.TelephonyProvider
        :keyword status: Filters calls by lifecycle status. Known values are: "in_progress",
         "success", and "failed". Default value is None.
        :paramtype status: str or ~azure.ai.projects.models.TelephonyCallStatus
        :keyword started_after: Includes calls that started at or after this Unix timestamp in
         seconds. Default value is None.
        :paramtype started_after: ~datetime.datetime
        :keyword started_before: Includes calls that started at or before this Unix timestamp in
         seconds. Default value is None.
        :paramtype started_before: ~datetime.datetime
        :keyword limit: A limit on the number of objects to be returned. Default value is None.
        :paramtype limit: int
        :keyword order: Sort order by the ``created_at`` timestamp of the objects. Known values are:
         "asc" and "desc". Default value is None.
        :paramtype order: str or ~azure.ai.projects.models.PageOrder
        :keyword before: A cursor for use in pagination. Default value is None.
        :paramtype before: str
        :return: An iterator like instance of TelephonyCallSummary
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.projects.models.TelephonyCallSummary]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _AGENT_OPERATION_FEATURE_HEADERS}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _AGENT_OPERATION_FEATURE_HEADERS
                kwargs["headers"] = headers

        return super().list_telephony_calls(
            agent_name,
            provider=provider,
            status=status,
            started_after=started_after,
            started_before=started_before,
            limit=limit,
            order=order,
            before=before,
            **kwargs,
        )

    @distributed_trace
    def get_telephony_call(  # type: ignore[override]
        self, agent_name: str, call_id: str, **kwargs: Any
    ) -> _models.TelephonyCallRecord:
        """Get an agent telephony call.

        Retrieves a durable inbound call record owned by the voice agent named in the path. When the
        client is constructed with ``allow_preview=True``, the required preview opt-in header is
        added automatically.

        :param agent_name: The name of the voice agent that owns the call record. Required.
        :type agent_name: str
        :param call_id: The service-generated call identifier. Required.
        :type call_id: str
        :return: TelephonyCallRecord. The TelephonyCallRecord is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyCallRecord
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _AGENT_OPERATION_FEATURE_HEADERS}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _AGENT_OPERATION_FEATURE_HEADERS
                kwargs["headers"] = headers

        try:
            return super().get_telephony_call(agent_name, call_id, **kwargs)
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

    @overload  # type: ignore[override]
    def transfer_telephony_call(
        self, agent_name: str, call_id: str, *, target: str, content_type: str = "application/json", **kwargs: Any
    ) -> _models.TelephonyCallRecord:
        """Transfer an active agent telephony call.

        Transfers an active inbound call to a configured target for the voice agent named in the
        path. When the client is constructed with ``allow_preview=True``, the required preview opt-in
        header is added automatically.

        :param agent_name: The name of the voice agent that owns the active call. Required.
        :type agent_name: str
        :param call_id: The service-generated call identifier. Required.
        :type call_id: str
        :keyword target: The name of a transfer target configured for the voice agent. Required.
        :paramtype target: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TelephonyCallRecord. The TelephonyCallRecord is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyCallRecord
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def transfer_telephony_call(
        self, agent_name: str, call_id: str, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.TelephonyCallRecord:
        """Transfer an active agent telephony call.

        Transfers an active inbound call to a configured target for the voice agent named in the
        path. When the client is constructed with ``allow_preview=True``, the required preview opt-in
        header is added automatically.

        :param agent_name: The name of the voice agent that owns the active call. Required.
        :type agent_name: str
        :param call_id: The service-generated call identifier. Required.
        :type call_id: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TelephonyCallRecord. The TelephonyCallRecord is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyCallRecord
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def transfer_telephony_call(
        self,
        agent_name: str,
        call_id: str,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.TelephonyCallRecord:
        """Transfer an active agent telephony call.

        Transfers an active inbound call to a configured target for the voice agent named in the
        path. When the client is constructed with ``allow_preview=True``, the required preview opt-in
        header is added automatically.

        :param agent_name: The name of the voice agent that owns the active call. Required.
        :type agent_name: str
        :param call_id: The service-generated call identifier. Required.
        :type call_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TelephonyCallRecord. The TelephonyCallRecord is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyCallRecord
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def transfer_telephony_call(  # type: ignore[override]
        self,
        agent_name: str,
        call_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        target: str = _Unset,
        **kwargs: Any,
    ) -> _models.TelephonyCallRecord:
        """Transfer an active agent telephony call.

        Transfers an active inbound call to a configured target for the voice agent named in the
        path. When the client is constructed with ``allow_preview=True``, the required preview opt-in
        header is added automatically.

        :param agent_name: The name of the voice agent that owns the active call. Required.
        :type agent_name: str
        :param call_id: The service-generated call identifier. Required.
        :type call_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword target: The name of a transfer target configured for the voice agent. Required.
        :paramtype target: str
        :return: TelephonyCallRecord. The TelephonyCallRecord is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyCallRecord
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _AGENT_OPERATION_FEATURE_HEADERS}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _AGENT_OPERATION_FEATURE_HEADERS
                kwargs["headers"] = headers

        try:
            return super().transfer_telephony_call(agent_name, call_id, body, target=target, **kwargs)  # type: ignore[misc]
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

    @distributed_trace
    def end_telephony_call(  # type: ignore[override]
        self, agent_name: str, call_id: str, **kwargs: Any
    ) -> _models.TelephonyCallRecord:
        """End an active agent telephony call.

        Ends an active inbound call owned by the voice agent named in the path. When the client is
        constructed with ``allow_preview=True``, the required preview opt-in header is added
        automatically.

        :param agent_name: The name of the voice agent that owns the active call. Required.
        :type agent_name: str
        :param call_id: The service-generated call identifier. Required.
        :type call_id: str
        :return: TelephonyCallRecord. The TelephonyCallRecord is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyCallRecord
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _AGENT_OPERATION_FEATURE_HEADERS}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _AGENT_OPERATION_FEATURE_HEADERS
                kwargs["headers"] = headers

        try:
            return super().end_telephony_call(agent_name, call_id, **kwargs)
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

    @distributed_trace
    def get_telephony_transfer_targets(  # type: ignore[override]
        self, agent_name: str, **kwargs: Any
    ) -> _models.TelephonyTransferTargets:
        """Get agent telephony transfer targets.

        Returns all transfer targets configured for the voice agent named in the path. When the
        client is constructed with ``allow_preview=True``, the required preview opt-in header is
        added automatically.

        :param agent_name: The name of the voice agent whose transfer targets are retrieved. Required.
        :type agent_name: str
        :return: TelephonyTransferTargets. The TelephonyTransferTargets is compatible with
         MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyTransferTargets
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _AGENT_OPERATION_FEATURE_HEADERS}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _AGENT_OPERATION_FEATURE_HEADERS
                kwargs["headers"] = headers

        try:
            return super().get_telephony_transfer_targets(agent_name, **kwargs)
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

    @overload  # type: ignore[override]
    def replace_telephony_transfer_targets(
        self,
        agent_name: str,
        *,
        transfer_targets: List[_models.TelephonyTransferTarget],
        etag: str,
        match_condition: MatchConditions,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.TelephonyTransferTargets:
        """Replace agent telephony transfer targets.

        Replaces all transfer targets configured for the voice agent named in the path. When the
        client is constructed with ``allow_preview=True``, the required preview opt-in header is
        added automatically.

        :param agent_name: The name of the voice agent whose transfer targets are replaced. Required.
        :type agent_name: str
        :keyword transfer_targets: The complete set of destinations to which the voice agent may
         transfer calls. An empty array clears all targets when replacing the configuration. Required.
        :paramtype transfer_targets: list[~azure.ai.projects.models.TelephonyTransferTarget]
        :keyword etag: check if resource is changed. Set None to skip checking etag. Required.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Required.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TelephonyTransferTargets. The TelephonyTransferTargets is compatible with
         MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyTransferTargets
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def replace_telephony_transfer_targets(
        self,
        agent_name: str,
        body: JSON,
        *,
        etag: str,
        match_condition: MatchConditions,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.TelephonyTransferTargets:
        """Replace agent telephony transfer targets.

        Replaces all transfer targets configured for the voice agent named in the path. When the
        client is constructed with ``allow_preview=True``, the required preview opt-in header is
        added automatically.

        :param agent_name: The name of the voice agent whose transfer targets are replaced. Required.
        :type agent_name: str
        :param body: Required.
        :type body: JSON
        :keyword etag: check if resource is changed. Set None to skip checking etag. Required.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Required.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TelephonyTransferTargets. The TelephonyTransferTargets is compatible with
         MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyTransferTargets
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def replace_telephony_transfer_targets(
        self,
        agent_name: str,
        body: IO[bytes],
        *,
        etag: str,
        match_condition: MatchConditions,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.TelephonyTransferTargets:
        """Replace agent telephony transfer targets.

        Replaces all transfer targets configured for the voice agent named in the path. When the
        client is constructed with ``allow_preview=True``, the required preview opt-in header is
        added automatically.

        :param agent_name: The name of the voice agent whose transfer targets are replaced. Required.
        :type agent_name: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword etag: check if resource is changed. Set None to skip checking etag. Required.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Required.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: TelephonyTransferTargets. The TelephonyTransferTargets is compatible with
         MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyTransferTargets
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def replace_telephony_transfer_targets(  # type: ignore[override]
        self,
        agent_name: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        transfer_targets: List[_models.TelephonyTransferTarget] = _Unset,
        etag: str,
        match_condition: MatchConditions,
        **kwargs: Any,
    ) -> _models.TelephonyTransferTargets:
        """Replace agent telephony transfer targets.

        Replaces all transfer targets configured for the voice agent named in the path. When the
        client is constructed with ``allow_preview=True``, the required preview opt-in header is
        added automatically.

        :param agent_name: The name of the voice agent whose transfer targets are replaced. Required.
        :type agent_name: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword transfer_targets: The complete set of destinations to which the voice agent may
         transfer calls. An empty array clears all targets when replacing the configuration. Required.
        :paramtype transfer_targets: list[~azure.ai.projects.models.TelephonyTransferTarget]
        :keyword etag: check if resource is changed. Set None to skip checking etag. Required.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Required.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: TelephonyTransferTargets. The TelephonyTransferTargets is compatible with
         MutableMapping
        :rtype: ~azure.ai.projects.models.TelephonyTransferTargets
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if getattr(self._config, "allow_preview", False):
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: _AGENT_OPERATION_FEATURE_HEADERS}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                headers[_FOUNDRY_FEATURES_HEADER_NAME] = _AGENT_OPERATION_FEATURE_HEADERS
                kwargs["headers"] = headers

        try:
            return super().replace_telephony_transfer_targets(  # type: ignore[arg-type]
                agent_name,
                body,
                transfer_targets=transfer_targets,
                etag=etag,
                match_condition=match_condition,
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

    @overload  # type: ignore[override]
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
    def begin_create_optimization_job(  # type: ignore[reportIncompatibleMethodOverride, override]
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
                job=job,  # type: ignore[reportArgumentType, arg-type]
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
