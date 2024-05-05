# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import json
import sys

from io import IOBase
from typing import Any, Dict, Union, IO, List, Optional, overload
from azure.core.pipeline import PipelineResponse
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from . import models as _models
from ._model_base import SdkJSONEncoder
from ._serialization import Serializer
from ._operations._operations import build_chat_completions_create_request
from ._client import ChatCompletionsClient as ChatCompletionsClientGenerated
from ._client import EmbeddingsClient, ImageGenerationClient

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_Unset: Any = object()
_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False

class AutoModelForInference():
    def __init__(self):
        pass

    def from_endpoint(endpoint: str, credential: Union[TokenCredential, AzureKeyCredential], **kwargs: Any):
        test_config = ChatCompletionsClient(endpoint, credential, **kwargs)
        try:
            config = test_config.get_model_info()

            if "model_type" in config:
                if config["model_type"] == "embedding":
                    return EmbeddingsClient(endpoint, credential, **kwargs)
                elif config["model_type"] == "image_generation":
                    return ImageGenerationClient(endpoint, credential, **kwargs)
                elif config["model_type"] == "completion":
                    return ChatCompletionsClient(endpoint, credential, **kwargs)
                else:
                    raise ValueError(
                        f"Model type {config['model_type']} is unkown by this inference client"
                    )
            raise ValueError(
                f"Model type couldn't be resolved in the endpoint."
            )
        except Exception as ex:
            raise ValueError(
                        f"The endpoint {endpoint} is not serving the Azure AI Model Inference API or is not in a healthy state."
                    ) from ex

class ChatCompletionsClient(ChatCompletionsClientGenerated):

    @overload
    def create_streaming(
        self,
        body: JSON,
        *,
        model_deployment: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models.StreamingChatCompletions:
        # pylint: disable=line-too-long
        """Gets streaming chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data. When using this method, the response is streamed
        back to the client. Iterate over the resulting ~azure.ai.inference.models.StreamingChatCompletions
        object to get content updates as they arrive.

        :param body: Required.
        :type body: JSON
        :keyword model_deployment: Name of the deployment to which you would like to route the request.
         Relevant only to Model-as-a-Platform (MaaP) deployments.
         Typically used when you want to target a test environment instead of production environment.
         Default value is None.
        :paramtype model_deployment: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ChatCompletions. The ChatCompletions is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.StreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_streaming(
        self,
        *,
        messages: List[_models.ChatRequestMessage],
        model_deployment: Optional[str] = None,
        content_type: str = "application/json",
        extras: Optional[Dict[str, str]] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Union[str, _models.ChatCompletionsResponseFormat]] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolSelectionPreset, _models.ChatCompletionsNamedToolSelection]
        ] = None,
        seed: Optional[int] = None,
        **kwargs: Any
    ) -> _models.StreamingChatCompletions:
        # pylint: disable=line-too-long
        """Gets streaming chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data. When using this method, the response is streamed
        back to the client. Iterate over the resulting ~azure.ai.inference.models.StreamingChatCompletions
        object to get content updates as they arrive.

        :keyword messages: The collection of context messages associated with this chat completions
         request.
         Typical usage begins with a chat message for the System role that provides instructions for
         the behavior of the assistant, followed by alternating messages between the User and
         Assistant roles. Required.
        :paramtype messages: list[~azure.ai.inference.models.ChatRequestMessage]
        :keyword model_deployment: Name of the deployment to which you would like to route the request.
         Relevant only to Model-as-a-Platform (MaaP) deployments.
         Typically used when you want to target a test environment instead of production environment.
         Default value is None.
        :paramtype model_deployment: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword extras: Extra parameters (in the form of string key-value pairs) that are not in the
         standard request payload.
         They will be passed to the service as-is in the root of the JSON request payload.
         How the service handles these extra parameters depends on the value of the
         ``extra-parameters``
         HTTP request header. Default value is None.
        :paramtype extras: dict[str, str]
        :keyword frequency_penalty: A value that influences the probability of generated tokens
         appearing based on their cumulative
         frequency in generated text.
         Positive values will make tokens less likely to appear as their frequency increases and
         decrease the likelihood of the model repeating the same statements verbatim. Default value is
         None.
        :paramtype frequency_penalty: float
        :keyword presence_penalty: A value that influences the probability of generated tokens
         appearing based on their existing
         presence in generated text.
         Positive values will make tokens less likely to appear when they already exist and increase
         the
         model's likelihood to output new topics. Default value is None.
        :paramtype presence_penalty: float
        :keyword temperature: The sampling temperature to use that controls the apparent creativity of
         generated completions.
         Higher values will make output more random while lower values will make results more focused
         and deterministic.
         It is not recommended to modify temperature and top_p for the same completions request as the
         interaction of these two settings is difficult to predict. Default value is None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature called nucleus sampling. This value
         causes the
         model to consider the results of tokens with the provided probability mass. As an example, a
         value of 0.15 will cause only the tokens comprising the top 15% of probability mass to be
         considered.
         It is not recommended to modify temperature and top_p for the same completions request as the
         interaction of these two settings is difficult to predict. Default value is None.
        :paramtype top_p: float
        :keyword max_tokens: The maximum number of tokens to generate. Default value is None.
        :paramtype max_tokens: int
        :keyword response_format: An object specifying the format that the model must output. Used to
         enable JSON mode. Known values are: "text" and "json_object". Default value is None.
        :paramtype response_format: str or ~azure.ai.inference.models.ChatCompletionsResponseFormat
        :keyword stop: A collection of textual sequences that will end completions generation. Default
         value is None.
        :paramtype stop: list[str]
        :keyword tools: The available tool definitions that the chat completions request can use,
         including caller-defined functions. Default value is None.
        :paramtype tools: list[~azure.ai.inference.models.ChatCompletionsToolDefinition]
        :keyword tool_choice: If specified, the model will configure which of the provided tools it can
         use for the chat completions response. Is either a Union[str,
         "_models.ChatCompletionsToolSelectionPreset"] type or a ChatCompletionsNamedToolSelection type.
         Default value is None.
        :paramtype tool_choice: str or ~azure.ai.inference.models.ChatCompletionsToolSelectionPreset or
         ~azure.ai.inference.models.ChatCompletionsNamedToolSelection
        :keyword seed: If specified, the system will make a best effort to sample deterministically
         such that repeated requests with the
         same seed and parameters should return the same result. Determinism is not guaranteed.".
         Default value is None.
        :paramtype seed: int
        :return: ChatCompletions. The ChatCompletions is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.ChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def create_streaming(
        self,
        body: IO[bytes],
        *,
        model_deployment: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models.StreamingChatCompletions:
        # pylint: disable=line-too-long
        """Gets streaming chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data. When using this method, the response is streamed
        back to the client. Iterate over the resulting ~azure.ai.inference.models.StreamingChatCompletions
        object to get content updates as they arrive.

        :param body: Required.
        :type body: IO[bytes]
        :keyword model_deployment: Name of the deployment to which you would like to route the request.
         Relevant only to Model-as-a-Platform (MaaP) deployments.
         Typically used when you want to target a test environment instead of production environment.
         Default value is None.
        :paramtype model_deployment: str
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ChatCompletions. The ChatCompletions is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.ChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def create_streaming(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        messages: List[_models.ChatRequestMessage] = _Unset,
        model_deployment: Optional[str] = None,
        extras: Optional[Dict[str, str]] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Union[str, _models.ChatCompletionsResponseFormat]] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolSelectionPreset, _models.ChatCompletionsNamedToolSelection]
        ] = None,
        seed: Optional[int] = None,
        **kwargs: Any
    ) -> _models.StreamingChatCompletions:
        # pylint: disable=line-too-long
        """Gets streaming chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data. When using this method, the response is streamed
        back to the client. Iterate over the resulting ~azure.ai.inference.models.StreamingChatCompletions
        object to get content updates as they arrive.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword messages: The collection of context messages associated with this chat completions
         request.
         Typical usage begins with a chat message for the System role that provides instructions for
         the behavior of the assistant, followed by alternating messages between the User and
         Assistant roles. Required.
        :paramtype messages: list[~azure.ai.inference.models.ChatRequestMessage]
        :keyword model_deployment: Name of the deployment to which you would like to route the request.
         Relevant only to Model-as-a-Platform (MaaP) deployments.
         Typically used when you want to target a test environment instead of production environment.
         Default value is None.
        :paramtype model_deployment: str
        :keyword extras: Extra parameters (in the form of string key-value pairs) that are not in the
         standard request payload.
         They will be passed to the service as-is in the root of the JSON request payload.
         How the service handles these extra parameters depends on the value of the
         ``extra-parameters``
         HTTP request header. Default value is None.
        :paramtype extras: dict[str, str]
        :keyword frequency_penalty: A value that influences the probability of generated tokens
         appearing based on their cumulative
         frequency in generated text.
         Positive values will make tokens less likely to appear as their frequency increases and
         decrease the likelihood of the model repeating the same statements verbatim. Default value is
         None.
        :paramtype frequency_penalty: float
        :keyword presence_penalty: A value that influences the probability of generated tokens
         appearing based on their existing
         presence in generated text.
         Positive values will make tokens less likely to appear when they already exist and increase
         the
         model's likelihood to output new topics. Default value is None.
        :paramtype presence_penalty: float
        :keyword temperature: The sampling temperature to use that controls the apparent creativity of
         generated completions.
         Higher values will make output more random while lower values will make results more focused
         and deterministic.
         It is not recommended to modify temperature and top_p for the same completions request as the
         interaction of these two settings is difficult to predict. Default value is None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature called nucleus sampling. This value
         causes the
         model to consider the results of tokens with the provided probability mass. As an example, a
         value of 0.15 will cause only the tokens comprising the top 15% of probability mass to be
         considered.
         It is not recommended to modify temperature and top_p for the same completions request as the
         interaction of these two settings is difficult to predict. Default value is None.
        :paramtype top_p: float
        :keyword max_tokens: The maximum number of tokens to generate. Default value is None.
        :paramtype max_tokens: int
        :keyword response_format: An object specifying the format that the model must output. Used to
         enable JSON mode. Known values are: "text" and "json_object". Default value is None.
        :paramtype response_format: str or ~azure.ai.inference.models.ChatCompletionsResponseFormat
        :keyword stop: A collection of textual sequences that will end completions generation. Default
         value is None.
        :paramtype stop: list[str]
        :keyword tools: The available tool definitions that the chat completions request can use,
         including caller-defined functions. Default value is None.
        :paramtype tools: list[~azure.ai.inference.models.ChatCompletionsToolDefinition]
        :keyword tool_choice: If specified, the model will configure which of the provided tools it can
         use for the chat completions response. Is either a Union[str,
         "_models.ChatCompletionsToolSelectionPreset"] type or a ChatCompletionsNamedToolSelection type.
         Default value is None.
        :paramtype tool_choice: str or ~azure.ai.inference.models.ChatCompletionsToolSelectionPreset or
         ~azure.ai.inference.models.ChatCompletionsNamedToolSelection
        :keyword seed: If specified, the system will make a best effort to sample deterministically
         such that repeated requests with the
         same seed and parameters should return the same result. Determinism is not guaranteed.".
         Default value is None.
        :paramtype seed: int
        :return: ChatCompletions. The ChatCompletions is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.ChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))

        if body is _Unset:
            if messages is _Unset:
                raise TypeError("missing required argument: messages")
            body = {
                "extras": extras,
                "frequency_penalty": frequency_penalty,
                "max_tokens": max_tokens,
                "messages": messages,
                "presence_penalty": presence_penalty,
                "response_format": response_format,
                "seed": seed,
                "stop": stop,
                "stream": True,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "tools": tools,
                "top_p": top_p,
            }
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_chat_completions_create_request(
            model_deployment=model_deployment,
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

        kwargs.pop("stream", True)  # Remove stream from kwargs (ignore value set by the application)
        pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=True, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        return _models.StreamingChatCompletions(response)


__all__: List[str] = [
    "ChatCompletionsClient",
    "AutoModelForInference"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
