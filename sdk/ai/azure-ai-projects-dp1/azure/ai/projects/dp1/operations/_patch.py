# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from ._operations import AgentsOperations as AgentsOperationsGenerated
from ._operations import build_agents_run_request, build_agents_create_agent_request
import datetime
from io import IOBase
import json
import sys
from typing import Any, Callable, Dict, IO, Iterable, List, Literal, Optional, TypeVar, Union, overload
import urllib.parse
import uuid

from azure.core import PipelineClient
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    StreamClosedError,
    StreamConsumedError,
    map_error,
)
from azure.core.paging import ItemPaged
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from ..models import _models as _models
from .._configuration import AIProjectClientConfiguration
from .._model_base import SdkJSONEncoder, _deserialize
from .._serialization import Deserializer, Serializer
from ..models._enums import PendingUploadType
from ..models._models import AzureAgentModel, UserMessage, DeveloperMessage, TextContent, ChatMessage

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]
_Unset: Any = object()

__all__: List[str] = []  # Add all objects you want publicly available to users at this package level


class AgentsOperations(AgentsOperationsGenerated):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @overload
    def create_agent(self, *, model_id: str, display_name: str, instructions: str, **kwargs: Any) -> "_models.Agent":
        """
        Creates a new Agent resource with simplified parameters.

        :keyword model_id: The ID of the model to use for the agent. Required.
        :paramtype model_id: str
        :keyword display_name: The display name of the agent. Required.
        :paramtype display_name: str
        :keyword instructions: Instructions provided to guide how this agent operates. Required.
        :paramtype instructions: str
        :return: The created Agent object.
        :rtype: ~azure.ai.projects.dp1.models.Agent
        :raises TypeError: If mutually exclusive arguments are provided.
        """
        ...

    @overload
    def create_agent(
        self,
        *,
        display_name: str,
        content_type: str = "application/json",
        agent_model: Optional[_models.AgentModel] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[_models.AgentToolDefinition]] = None,
        tool_choice: Optional[_models.ToolChoiceBehavior] = None,
        **kwargs: Any
    ) -> _models.Agent:
        """Creates a new Agent resource and returns it.

        :keyword display_name: The display name of the agent; used for display purposes and sent to the
         LLM to identify the agent. Required.
        :paramtype display_name: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword agent_model: The model definition for this agent. This is optional (not needed) when
         doing a run using persistent agent. Default value is None.
        :paramtype agent_model: ~azure.ai.projects.dp1.models.AgentModel
        :keyword instructions: Instructions provided to guide how this agent operates. Default value is
         None.
        :paramtype instructions: str
        :keyword tools: A list of tool definitions available to the agent. Default value is None.
        :paramtype tools: list[~azure.ai.projects.dp1.models.AgentToolDefinition]
        :keyword tool_choice: How the agent should choose among provided tools. Default value is None.
        :paramtype tool_choice: ~azure.ai.projects.dp1.models.ToolChoiceBehavior
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.projects.dp1.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_agent(self, body: JSON, *, content_type: str = "application/json", **kwargs: Any) -> _models.Agent:
        """Creates a new Agent resource and returns it.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.projects.dp1.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_agent(self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any) -> _models.Agent:
        """Creates a new Agent resource and returns it.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.projects.dp1.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_agent(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        display_name: str = _Unset,
        agent_model: Optional[_models.AgentModel] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[_models.AgentToolDefinition]] = None,
        tool_choice: Optional[_models.ToolChoiceBehavior] = None,
        model_id: Optional[str] = None,
        **kwargs: Any
    ) -> _models.Agent:
        """Creates a new Agent resource and returns it.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword display_name: The display name of the agent; used for display purposes and sent to the
         LLM to identify the agent. Required.
        :paramtype display_name: str
        :keyword agent_model: The model definition for this agent. This is optional (not needed) when
         doing a run using persistent agent. Default value is None.
        :paramtype agent_model: ~azure.ai.projects.dp1.models.AgentModel
        :keyword instructions: Instructions provided to guide how this agent operates. Default value is
         None.
        :paramtype instructions: str
        :keyword tools: A list of tool definitions available to the agent. Default value is None.
        :paramtype tools: list[~azure.ai.projects.dp1.models.AgentToolDefinition]
        :keyword tool_choice: How the agent should choose among provided tools. Default value is None.
        :paramtype tool_choice: ~azure.ai.projects.dp1.models.ToolChoiceBehavior
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.projects.dp1.models.Agent
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        # Error handling for mutually exclusive arguments
        if model_id and agent_model:
            raise TypeError("`model_id` and `agent_model` cannot be provided together.")
        if model_id:
            agent_model = _models.AgentModel(id=model_id)

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.Agent] = kwargs.pop("cls", None)

        if body is _Unset:
            if display_name is _Unset:
                raise TypeError("missing required argument: display_name")
            body = {
                "agentModel": agent_model,
                "displayName": display_name,
                "instructions": instructions,
                "toolChoice": tool_choice,
                "tools": tools,
            }
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_agents_create_agent_request(
            content_type=content_type,
            api_version=self._config.api_version,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                try:
                    response.read()  # Load the body in memory and close the socket
                except (StreamConsumedError, StreamClosedError):
                    pass
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if _stream:
            deserialized = response.iter_bytes()
        else:
            deserialized = _deserialize(_models.Agent, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    def run(self, *, model_id: str, instructions: str, message: str, **kwargs: Any) -> "_models.Run":
        """Creates and waits for a run to finish, returning the completed Run (including its outputs).

        :keyword model_id: The ID of the model to use for the run. Required.
        :paramtype model_id: str
        :keyword instructions: Instructions for the agent. Required.
        :paramtype instructions: str
        :keyword message: A message to send to the agent. Required.
        :paramtype message: str
        :return: The completed Run object.
        :rtype: ~azure.ai.projects.dp1.models.Run
        :raises TypeError: If required arguments are missing.
        """
        ...

    @overload
    def run(self, *, agent_id: str, message: str, **kwargs: Any) -> "_models.Run":
        """Creates and waits for a run to finish, returning the completed Run (including its outputs).

        :keyword agent_id: The ID of the agent to use for the run. Required.
        :paramtype agent_id: str
        :keyword message: A message to send to the agent. Required.
        :paramtype message: str
        :return: The completed Run object.
        :rtype: ~azure.ai.projects.dp1.models.Run
        :raises TypeError: If required arguments are missing.
        """
        ...

    @overload
    def run(
        self,
        *,
        input: List[_models.ChatMessage],
        content_type: str = "application/json",
        agent_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        options: Optional[_models.RunOptions] = None,
        user_id: Optional[str] = None,
        agent_configuration: Optional[_models.AgentConfigurationOptions] = None,
        **kwargs: Any
    ) -> _models.Run:
        """Creates and waits for a run to finish, returning the completed Run (including its outputs).

        :keyword input: The list of input messages for the run. Required.
        :paramtype input: list[~azure.ai.projects.dp1.models.ChatMessage]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword agent_id: Unique identifier for the agent responsible for the run. This is optional
         (not needeed) when doing a run using ephemeral agent. Default value is None.
        :paramtype agent_id: str
        :keyword conversation_id: Optional identifier for an existing conversation. Default value is
         None.
        :paramtype conversation_id: str
        :keyword metadata: Optional metadata associated with the run request. Default value is None.
        :paramtype metadata: dict[str, str]
        :keyword options: Optional configuration for run generation. Default value is None.
        :paramtype options: ~azure.ai.projects.dp1.models.RunOptions
        :keyword user_id: Identifier for the user making the request. Default value is None.
        :paramtype user_id: str
        :keyword agent_configuration: The agent configuration when not using a previously created
         agent. Default value is None.
        :paramtype agent_configuration: ~azure.ai.projects.dp1.models.AgentConfigurationOptions
        :return: Run. The Run is compatible with MutableMapping
        :rtype: ~azure.ai.projects.dp1.models.Run
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def run(self, body: JSON, *, content_type: str = "application/json", **kwargs: Any) -> _models.Run:
        """Creates and waits for a run to finish, returning the completed Run (including its outputs).

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Run. The Run is compatible with MutableMapping
        :rtype: ~azure.ai.projects.dp1.models.Run
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def run(self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any) -> _models.Run:
        """Creates and waits for a run to finish, returning the completed Run (including its outputs).

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: Run. The Run is compatible with MutableMapping
        :rtype: ~azure.ai.projects.dp1.models.Run
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def run(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        input: List[_models.ChatMessage] = _Unset,
        agent_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        options: Optional[_models.RunOptions] = None,
        user_id: Optional[str] = None,
        agent_configuration: Optional[_models.AgentConfigurationOptions] = None,
        model_id: Optional[str] = None,
        instructions: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs: Any
    ) -> _models.Run:
        """Creates and waits for a run to finish, returning the completed Run (including its outputs).

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword input: The list of input messages for the run. Required.
        :paramtype input: list[~azure.ai.projects.dp1.models.ChatMessage]
        :keyword agent_id: Unique identifier for the agent responsible for the run. This is optional
         (not needeed) when doing a run using ephemeral agent. Default value is None.
        :paramtype agent_id: str
        :keyword conversation_id: Optional identifier for an existing conversation. Default value is
         None.
        :paramtype conversation_id: str
        :keyword metadata: Optional metadata associated with the run request. Default value is None.
        :paramtype metadata: dict[str, str]
        :keyword options: Optional configuration for run generation. Default value is None.
        :paramtype options: ~azure.ai.projects.dp1.models.RunOptions
        :keyword user_id: Identifier for the user making the request. Default value is None.
        :paramtype user_id: str
        :keyword agent_configuration: The agent configuration when not using a previously created
         agent. Default value is None.
        :paramtype agent_configuration: ~azure.ai.projects.dp1.models.AgentConfigurationOptions
        :return: Run. The Run is compatible with MutableMapping
        :rtype: ~azure.ai.projects.dp1.models.Run
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Error handling for mutually exclusive arguments
        if model_id and agent_configuration:
            raise TypeError("`model_id` and `agent_configuration` cannot be provided together.")
        if message and input is not _Unset:
            raise TypeError("`message` and `input` cannot be provided together.")
        if instructions and not model_id:
            raise TypeError("`model_id` must be provided when `instructions` is specified.")

        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.Run] = kwargs.pop("cls", None)

        if body is _Unset:
            if model_id:
                agent_model = _models.AzureAgentModel(id=model_id)
                agent_configuration = _models.AgentConfigurationOptions(
                    display_name="", agent_model=agent_model, instructions=instructions
                )

            if message:
                chat_content = _models.TextContent(text=message)
                chat_message = _models.ChatMessage(content=[chat_content])
                input = [chat_message]

            if input is _Unset:
                raise TypeError("missing required argument: `input`")

            body = {
                "agentConfiguration": agent_configuration,
                "agentId": agent_id,
                "conversationId": conversation_id,
                "input": input,
                "metadata": metadata,
                "options": options,
                "userId": user_id,
            }
            body = {k: v for k, v in body.items() if v is not None}

        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_agents_run_request(
            content_type=content_type,
            api_version=self._config.api_version,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                try:
                    response.read()  # Load the body in memory and close the socket
                except (StreamConsumedError, StreamClosedError):
                    pass
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if _stream:
            deserialized = response.iter_bytes()
        else:
            deserialized = _deserialize(_models.Run, response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore


__all__: List[str] = [
    "AgentsOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
