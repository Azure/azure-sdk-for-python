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
    def create_agent(
        self,
        *,
        model_id: Optional[str] = None,
        display_name: Optional[str] = None,
        instructions: Optional[str] = None,
        **kwargs: Any
    ) -> _models.Agent:
        """Creates an agent with the specified model and instructions.

        :param model_id: The identifier of the model to use for this agent. Required.
        :type model_id: str
        :param display_name: The name of the agent; used for display purposes and sent to the LLM to identify
        :type display_name: str
        :param instructions: Instructions provided to guide how this agent operates. Required.
        :type instructions: str
        :return: Agent. The Agent is compatible with MutableMapping
        :rtype: ~azure.ai.projects.dp1.models.Agent
        """

    @overload
    def create_agent(
        self, *, options: _models.AgentCreationOptions, content_type: str = "application/json", **kwargs: Any
    ) -> _models.Agent:
        """Creates a new Agent resource and returns it.

        :keyword options: The options for agent creation. Required.
        :paramtype options: ~azure.ai.projects.dp1.models.AgentCreationOptions
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
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
        self, body: Union[JSON, IO[bytes]] = _Unset, *, options: _models.AgentCreationOptions = _Unset, model_id: Optional[str] = None, display_name: Optional[str] = None, instructions: Optional[str] = None,**kwargs: Any
    ) -> _models.Agent:
        """Creates a new Agent resource and returns it.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword options: The options for agent creation. Required.
        :paramtype options: ~azure.ai.projects.dp1.models.AgentCreationOptions
        :param model_id: The identifier of the model to use for this agent. Required.
        :type model_id: str
        :param display_name: The name of the agent; used for display purposes and sent to the LLM to identify
        :type display_name: str
        :param instructions: Instructions provided to guide how this agent operates. Required.
        :type instructions: str
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

        if body is _Unset:
            if model_id and display_name and instructions:
                if options is not _Unset:
                    raise TypeError("options and model_id/display_name/instructions are mutually exclusive")
                agent_model = AzureAgentModel(id=model_id)
                options = _models.AgentCreationOptions(
                    model=agent_model, display_name=display_name, instructions=instructions
                )
            elif model_id or display_name or instructions:
                raise TypeError("missing required argument: model_id/display_name/instructions")

            if options is _Unset:
                raise TypeError("missing required argument: options")
            body = {"options": options}
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
    def run(
        self,
        *,
        model_id: Optional[str] = None,
        instructions: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs: Any
    ) -> _models.Run:
        """Creates and waits for a run to finish, returning the completed Run (including its outputs).

        :keyword model_id: Identifier for the model used by the agent responsible for the run.
        :paramtype model_id: str
        :keyword instructions: Instructions for the agent responsible for the run.
        :paramtype instructions: str
        :keyword message: Input message to be procssed during the run.
        :paramtype message: str
        :return: Run. The Run is compatible with MutableMapping
        :rtype: ~azure.ai.projects.dp1.models.Run
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def run(
        self,
        *,
        agent_id: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs: Any
    ) -> _models.Run:
        """Creates and waits for a run to finish, returning the completed Run (including its outputs).

        :keyword agent_id: Unique identifier for the agent responsible for the run.
        :paramtype agent_id: str
        :keyword message: Input message to be procssed during the run.
        :paramtype message: str
        :return: Run. The Run is compatible with MutableMapping
        :rtype: ~azure.ai.projects.dp1.models.Run
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def run(
        self,
        *,
        options: _models.AgentConfigurationOptions,
        inputs: _models.RunInputs,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models.Run:
        """Creates and waits for a run to finish, returning the completed Run (including its outputs).

        :keyword options: The options for the agent completing the run. Required.
        :paramtype options: ~azure.ai.projects.dp1.models.AgentConfigurationOptions
        :keyword inputs: The inputs for the run. Required.
        :paramtype inputs: ~azure.ai.projects.dp1.models.RunInputs
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
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
        options: _models.AgentConfigurationOptions = _Unset,
        inputs: _models.RunInputs = _Unset,
        model_id: Optional[str] = None,
        instructions: Optional[str] = None,
        agent_id: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs: Any
    ) -> _models.Run:
        """Creates and waits for a run to finish, returning the completed Run (including its outputs).

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword options: The options for the agent completing the run. Required.
        :paramtype options: ~azure.ai.projects.dp1.models.AgentConfigurationOptions
        :keyword inputs: The inputs for the run. Required.
        :paramtype inputs: ~azure.ai.projects.dp1.models.RunInputs
        :keyword model_id: Identifier for the model used by the agent responsible for the run.
        :paramtype model_id: str
        :keyword instructions: Instructions for the agent responsible for the run.
        :paramtype instructions: str
        :keyword agent_id: Unique identifier for the agent responsible for the run.
        :paramtype agent_id: str
        :keyword message: Input message to be procssed during the run.
        :paramtype message: str
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

        if body is _Unset:
            if model_id:
                if options is not _Unset:
                    raise TypeError("options and model_id are mutually exclusive")
                agent_model = AzureAgentModel(id=model_id)
                options = _models.AgentConfigurationOptions(model=agent_model, instructions=instructions)
            elif instructions:
                raise TypeError("missing required argument: model_id required with instructions")

            if agent_id and message:
                if inputs is not _Unset:
                    raise TypeError("inputs and agent_id/message are mutually exclusive")
                chat_content = TextContent(text=message)
                chat_message = ChatMessage(content=[chat_content])
                inputs = _models.RunInputs(agent_id=agent_id, input=[chat_message])
            elif agent_id or message:
                raise TypeError("missing required argument: agent_id/message")

            if options is _Unset:
                raise TypeError("missing required argument: options")
            if inputs is _Unset:
                raise TypeError("missing required argument: inputs")
            body = {"inputs": inputs, "options": options}
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
