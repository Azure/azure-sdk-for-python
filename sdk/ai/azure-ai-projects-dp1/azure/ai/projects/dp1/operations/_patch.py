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
    def run(
        self,
        *,
        input: List[_models.ChatMessage],
        content_type: str = "application/json",
        name: Optional[str] = None,
        agent_model: Optional[_models.AgentModel] = None,
        instructions: Optional[List[_models.DeveloperMessage]] = None,
        tools: Optional[List[_models.AgentToolDefinition]] = None,
        tool_choice: Optional[_models.ToolChoiceBehavior] = None,
        agent_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        options: Optional[_models.RunOptions] = None,
        user_id: Optional[str] = None,
        **kwargs: Any
    ) -> _models.Run:
        """Creates and waits for a run to finish, returning the completed Run (including its outputs).

        :keyword input: The list of input messages for the run. Required.
        :paramtype input: list[~azure.ai.projects.dp1.models.ChatMessage]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword name: The name of the agent; used for display purposes and sent to the LLM to identify
         the agent. Default value is None.
        :paramtype name: str
        :keyword agent_model: The model definition for this agent. This is optional (not needed) when
         doing a run using persistent agent. Default value is None.
        :paramtype agent_model: ~azure.ai.projects.dp1.models.AgentModel
        :keyword instructions: Instructions provided to guide how this agent operates. Default value is
         None.
        :paramtype instructions: list[~azure.ai.projects.dp1.models.DeveloperMessage]
        :keyword tools: A list of tool definitions available to the agent. Default value is None.
        :paramtype tools: list[~azure.ai.projects.dp1.models.AgentToolDefinition]
        :keyword tool_choice: How the agent should choose among provided tools. Default value is None.
        :paramtype tool_choice: ~azure.ai.projects.dp1.models.ToolChoiceBehavior
        :keyword agent_id: Unique identifier for the agent responsible for the run. This is optional
         (not needeed) when doing a run using ephemeral agent. Default value is None.
        :paramtype agent_id: str
        :keyword thread_id: Optional identifier for an existing conversation thread. Default value is
         None.
        :paramtype thread_id: str
        :keyword metadata: Optional metadata associated with the run request. Default value is None.
        :paramtype metadata: dict[str, str]
        :keyword options: Optional configuration for run generation. Default value is None.
        :paramtype options: ~azure.ai.projects.dp1.models.RunOptions
        :keyword user_id: Identifier for the user making the request. Default value is None.
        :paramtype user_id: str
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
        :raises ~azure.core.exceptions.HttpResponseError:sdk\ai\azure-ai-projects-dp1\azure\ai\projects\dp1\operations
        """

    @overload
    def run(self, *, model_id: str, instructions_str: str, message: str, **kwargs: Any) -> _models.Run:
        """Creates and waits for a run to finish, returning the completed Run (including its outputs).

        :param model_id: The identifier of the model to use for this run. Required.
        :type model_id: str
        :param instructions_str: Instructions provided to guide how this agent operates. Required.
        :type instructions_str: str
        :param message: The list of input messages for the run. Required.
        :type message: str
        :return: Run. The Run is compatible with MutableMapping
        """

    @distributed_trace
    def run(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        input: List[_models.ChatMessage] = _Unset,
        name: Optional[str] = None,
        agent_model: Optional[_models.AgentModel] = None,
        instructions: Optional[List[_models.DeveloperMessage]] = None,
        tools: Optional[List[_models.AgentToolDefinition]] = None,
        tool_choice: Optional[_models.ToolChoiceBehavior] = None,
        agent_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        options: Optional[_models.RunOptions] = None,
        user_id: Optional[str] = None,
        model_id: Optional[str] = None,
        instructions_str: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs: Any
    ) -> _models.Run:
        """Creates and waits for a run to finish, returning the completed Run (including its outputs).

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword input: The list of input messages for the run. Required.
        :paramtype input: list[~azure.ai.projects.dp1.models.ChatMessage]
        :keyword name: The name of the agent; used for display purposes and sent to the LLM to identify
         the agent. Default value is None.
        :paramtype name: str
        :keyword agent_model: The model definition for this agent. This is optional (not needed) when
         doing a run using persistent agent. Default value is None.
        :paramtype agent_model: ~azure.ai.projects.dp1.models.AgentModel
        :keyword instructions: Instructions provided to guide how this agent operates. Default value is
         None.
        :paramtype instructions: list[~azure.ai.projects.dp1.models.DeveloperMessage]
        :keyword tools: A list of tool definitions available to the agent. Default value is None.
        :paramtype tools: list[~azure.ai.projects.dp1.models.AgentToolDefinition]
        :keyword tool_choice: How the agent should choose among provided tools. Default value is None.
        :paramtype tool_choice: ~azure.ai.projects.dp1.models.ToolChoiceBehavior
        :keyword agent_id: Unique identifier for the agent responsible for the run. This is optional
         (not needeed) when doing a run using ephemeral agent. Default value is None.
        :paramtype agent_id: str
        :keyword thread_id: Optional identifier for an existing conversation thread. Default value is
         None.
        :paramtype thread_id: str
        :keyword metadata: Optional metadata associated with the run request. Default value is None.
        :paramtype metadata: dict[str, str]
        :keyword options: Optional configuration for run generation. Default value is None.
        :paramtype options: ~azure.ai.projects.dp1.models.RunOptions
        :keyword user_id: Identifier for the user making the request. Default value is None.
        :paramtype user_id: str
        :param model_id: The identifier of the model to use for this run.
        :type model_id: str
        :param instructions_str: Instructions provided to guide how this agent operates.
        :type instructions_str: str
        :param message: The list of input messages for the run.
        :type message: str        
        :return: Run. The Run is compatible with MutableMapping
        :rtype: ~azure.ai.projects.dp1.models.Run
        :raises ~azure.core.exceptions.HttpResponseError:
        """
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

        if model_id and instructions_str:
            instructions_content = TextContent(text=instructions_str)
            instructions_message = DeveloperMessage(content=[instructions_content])
            instructions = [instructions_message]
            agent_model = AzureAgentModel(id=model_id)
            chat_content = TextContent(text=message)
            chat_message = ChatMessage(content=[chat_content])
            input = [chat_message]

        if body is _Unset:
            if input is _Unset:
                raise TypeError("missing required argument: input")
            body = {
                "agentId": agent_id,
                "agentModel": agent_model,
                "input": input,
                "instructions": instructions,
                "metadata": metadata,
                "name": name,
                "options": options,
                "threadId": thread_id,
                "toolChoice": tool_choice,
                "tools": tools,
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

    @overload
    def create_agent(self, *, model_id: Optional[str] = None, name: Optional[str] = None, instructions_str: Optional[str] = None, **kwargs: Any) -> _models.Agent:
        """Creates an agent with the specified model and instructions.

        :param model_id: The identifier of the model to use for this agent. Required.
        :type model_id: str
        :param name: The name of the agent; used for display purposes and sent to the LLM to identify
        :type name: str
        :param instructions_str: Instructions provided to guide how this agent operates. Required.
        :type instructions_str: str
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.projects.dp1.models.Agent
        """

    @overload
    def create_agent(
        self,
        *,
        content_type: str = "application/json",
        name: Optional[str] = None,
        agent_model: Optional[_models.AgentModel] = None,
        instructions: Optional[List[_models.DeveloperMessage]] = None,
        tools: Optional[List[_models.AgentToolDefinition]] = None,
        tool_choice: Optional[_models.ToolChoiceBehavior] = None,
        **kwargs: Any
    ) -> _models.Agent:
        """Creates a new Agent resource and returns it.

        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword name: The name of the agent; used for display purposes and sent to the LLM to identify
         the agent. Default value is None.
        :paramtype name: str
        :keyword agent_model: The model definition for this agent. This is optional (not needed) when
         doing a run using persistent agent. Default value is None.
        :paramtype agent_model: ~azure.ai.projects.dp1.models.AgentModel
        :keyword instructions: Instructions provided to guide how this agent operates. Default value is
         None.
        :paramtype instructions: list[~azure.ai.projects.dp1.models.DeveloperMessage]
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
        name: Optional[str] = None,
        agent_model: Optional[_models.AgentModel] = None,
        instructions: Optional[List[_models.DeveloperMessage]] = None,
        tools: Optional[List[_models.AgentToolDefinition]] = None,
        tool_choice: Optional[_models.ToolChoiceBehavior] = None,
        model_id: Optional[str] = None,
        instructions_str: Optional[str] = None,
        **kwargs: Any
    ) -> _models.Agent:
        """Creates a new Agent resource and returns it.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword name: The name of the agent; used for display purposes and sent to the LLM to identify
         the agent. Default value is None.
        :paramtype name: str
        :keyword agent_model: The model definition for this agent. This is optional (not needed) when
         doing a run using persistent agent. Default value is None.
        :paramtype agent_model: ~azure.ai.projects.dp1.models.AgentModel
        :keyword instructions: Instructions provided to guide how this agent operates. Default value is
         None.
        :paramtype instructions: list[~azure.ai.projects.dp1.models.DeveloperMessage]
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

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.Agent] = kwargs.pop("cls", None)

        if model_id and instructions_str:
            instructions_content = TextContent(text=instructions_str)
            instructions_message = DeveloperMessage(content=[instructions_content])
            instructions = [instructions_message]
            agent_model = AzureAgentModel(id=model_id)

        if body is _Unset:
            body = {
                "agentModel": agent_model,
                "instructions": instructions,
                "name": name,
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

__all__: List[str] = [
    "AgentsOperations",
]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
