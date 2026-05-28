# pylint: disable=line-too-long,useless-suppression,pointless-string-statement
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Union, Optional, Any, IO, overload, Final
from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace
from ._operations import AgentsOperations as GeneratedAgentsOperations, JSON, _Unset
from .. import models as _models
from ..models._enums import _AgentDefinitionOptInKeys
from ..models._patch import _FOUNDRY_FEATURES_HEADER_NAME, _has_header_case_insensitive

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
_PREVIEW_FEATURE_REQUIRED_CODE: Final = "preview_feature_required"
_PREVIEW_FEATURE_ADDED_ERROR_MESSAGE: Final = (
    '\n**Python SDK users**: This operation requires you to set "allow_preview=True" '
    "when calling the AIProjectClient constructor. "
    "\nNote that preview features are under development and subject to change. They should not be used in production environments."
)
_AGENT_OPERATION_FEATURE_HEADERS: Final[str] = ",".join(
    [
        _AgentDefinitionOptInKeys.HOSTED_AGENTS_V1_PREVIEW.value,
        _AgentDefinitionOptInKeys.WORKFLOW_AGENTS_V1_PREVIEW.value,
        _AgentDefinitionOptInKeys.AGENT_ENDPOINT_V1_PREVIEW.value,
    ]
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
