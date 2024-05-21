# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import json
import logging
import sys

from io import IOBase
from typing import Any, Dict, Union, IO, List, Optional, overload, Type
from azure.core.pipeline import PipelineResponse
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from .. import models as _models
from .._model_base import SdkJSONEncoder, _deserialize
from ._client import ChatCompletionsClient as ChatCompletionsClientGenerated
from ._client import EmbeddingsClient as EmbeddingsClientGenerated
from ._client import ImageEmbeddingsClient as ImageEmbeddingsClientGenerated
from .._operations._operations import  (
    build_chat_completions_complete_request,
    build_embeddings_embedding_request,
    build_image_embeddings_embedding_request
)

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_Unset: Any = object()
_LOGGER = logging.getLogger(__name__)


async def load_client(
    endpoint: str, credential: AzureKeyCredential, **kwargs: Any
) -> Union[ChatCompletionsClientGenerated, EmbeddingsClientGenerated, ImageEmbeddingsClientGenerated]:
    client = ChatCompletionsClient(endpoint, credential, **kwargs)  # Pick any of the clients, it does not matter...
    model_info = await client.get_model_info()
    await client.close()
    _LOGGER.info("model_info=%s", model_info)
    if model_info.model_type in (None, ""):
        raise ValueError(
            "The AI model information is missing a value for `model type`. Cannot create an appropriate client."
        )
    # TODO: Remove "completions" once Mistral Large fixes their model type
    if model_info.model_type in (_models.ModelType.CHAT, "completion"):
        return ChatCompletionsClient(endpoint, credential, **kwargs)
    if model_info.model_type == _models.ModelType.EMBEDDINGS:
        return EmbeddingsClient(endpoint, credential, **kwargs)
    if model_info.model_type == _models.ModelType.IMAGE_EMBEDDINGS:
        return ImageEmbeddingsClient(endpoint, credential, **kwargs)
    raise ValueError(f"No client available to support AI model type `{model_info.model_type}`")


class ChatCompletionsClient(ChatCompletionsClientGenerated):

    @overload
    async def complete(
        self,
        body: JSON,
        *,
        model_deployment: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> Union[_models.AsyncStreamingChatCompletions, _models.ChatCompletions]:
        # pylint: disable=line-too-long
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data. When using this method with `stream=True`, the response is streamed
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
        :return: ChatCompletions for non-streaming, or AsyncStreamingChatCompletions for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.AsyncStreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def complete(
        self,
        *,
        messages: List[_models.ChatRequestMessage],
        model_deployment: Optional[str] = None,
        content_type: str = "application/json",
        hyper_params: Optional[Dict[str, Any]] = None,
        extras: Optional[Dict[str, str]] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Union[str, _models.ChatCompletionsResponseFormat]] = None,
        stop: Optional[List[str]] = None,
        stream: Optional[bool] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolSelectionPreset, _models.ChatCompletionsNamedToolSelection]
        ] = None,
        seed: Optional[int] = None,
        **kwargs: Any,
    ) -> Union[_models.AsyncStreamingChatCompletions, _models.ChatCompletions]:
        # pylint: disable=line-too-long
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data. When using this method with `stream=True`, the response is streamed
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
        :keyword hyper_params: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these hypter parameters depends on the value of the
         ``unknown-parameters`` request header. Default value is None.
        :paramtype hyper_params: dict[str, Any]
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
        :keyword stream: A value indicating whether chat completions should be streamed for this request.
         Default value is False. If streaming is enabled, the response will be a StreamingChatCompletions.
         Otherwise the response will be a ChatCompletions.
        :paramtype stream: bool
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
        :return: ChatCompletions for non-streaming, or AsyncStreamingChatCompletions for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.AsyncStreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def complete(
        self,
        body: IO[bytes],
        *,
        model_deployment: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> Union[_models.AsyncStreamingChatCompletions, _models.ChatCompletions]:
        # pylint: disable=line-too-long
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data. When using this method with `stream=True`, the response is streamed
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
        :return: ChatCompletions for non-streaming, or AsyncStreamingChatCompletions for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.AsyncStreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def complete(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        messages: List[_models.ChatRequestMessage] = _Unset,
        model_deployment: Optional[str] = None,
        hyper_params: Optional[Dict[str, Any]] = None,
        extras: Optional[Dict[str, str]] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Union[str, _models.ChatCompletionsResponseFormat]] = None,
        stop: Optional[List[str]] = None,
        stream: Optional[bool] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolSelectionPreset, _models.ChatCompletionsNamedToolSelection]
        ] = None,
        seed: Optional[int] = None,
        **kwargs: Any,
    ) -> Union[_models.AsyncStreamingChatCompletions, _models.ChatCompletions]:
        # pylint: disable=line-too-long
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data. When using this method with `stream=True`, the response is streamed
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
        :keyword hyper_params: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these hypter parameters depends on the value of the
         ``unknown-parameters`` request header. Default value is None.
        :paramtype hyper_params: dict[str, Any]
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
        :keyword stream: A value indicating whether chat completions should be streamed for this request.
         Default value is False. If streaming is enabled, the response will be a StreamingChatCompletions.
         Otherwise the response will be a ChatCompletions.
        :paramtype stream: bool
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
        :return: ChatCompletions for non-streaming, or AsyncStreamingChatCompletions for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.AsyncStreamingChatCompletions
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
                "stream": stream,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "tools": tools,
                "top_p": top_p,
            }
            if hyper_params is not None:
                body.update(hyper_params)
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_chat_completions_complete_request(
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

        _stream = stream or False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                await response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if _stream:
            return _models.AsyncStreamingChatCompletions(response)
        else:
            return _deserialize(_models.ChatCompletions, response.json())  # pylint: disable=protected-access


class EmbeddingsClient(EmbeddingsClientGenerated):

    @overload
    async def embedding(
        self,
        body: JSON,
        *,
        model_deployment: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models.EmbeddingsResult:
        """Return the embeddings for a given text prompt.

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
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def embedding(
        self,
        *,
        hyper_params: Optional[Dict[str, Any]] = None,
        input: List[str],
        model_deployment: Optional[str] = None,
        content_type: str = "application/json",
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        **kwargs: Any
    ) -> _models.EmbeddingsResult:
        """Return the embeddings for a given text prompt.

        :keyword hyper_params: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these hypter parameters depends on the value of the
         ``unknown-parameters`` request header. Default value is None.
        :paramtype hyper_params: dict[str, Any]
        :keyword input: Input text to embed, encoded as a string or array of tokens.
         To embed multiple inputs in a single request, pass an array
         of strings or array of token arrays. Required.
        :paramtype input: list[str]
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
        :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
         have.
         Passing null causes the model to use its default value.
         Returns a 422 error if the model doesn't support the value or parameter. Default value is
         None.
        :paramtype dimensions: int
        :keyword encoding_format: Optional. The number of dimensions the resulting output embeddings
         should have.
         Passing null causes the model to use its default value.
         Returns a 422 error if the model doesn't support the value or parameter. Known values are:
         "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
        :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
        :keyword input_type: Optional. The type of the input.
         Returns a 422 error if the model doesn't support the value or parameter. Known values are:
         "text", "query", and "document". Default value is None.
        :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def embedding(
        self,
        body: IO[bytes],
        *,
        model_deployment: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models.EmbeddingsResult:
        """Return the embeddings for a given text prompt.

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
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def embedding(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        hyper_params: Optional[Dict[str, Any]] = None,
        input: List[str] = _Unset,
        model_deployment: Optional[str] = None,
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        **kwargs: Any
    ) -> _models.EmbeddingsResult:
        # pylint: disable=line-too-long
        """Return the embeddings for a given text prompt.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword hyper_params: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these hypter parameters depends on the value of the
         ``unknown-parameters`` request header. Default value is None.
        :paramtype hyper_params: dict[str, Any]
        :keyword input: Input text to embed, encoded as a string or array of tokens.
         To embed multiple inputs in a single request, pass an array
         of strings or array of token arrays. Required.
        :paramtype input: list[str]
        :keyword model_deployment: Name of the deployment to which you would like to route the request.
         Relevant only to Model-as-a-Platform (MaaP) deployments.
         Typically used when you want to target a test environment instead of production environment.
         Default value is None.
        :paramtype model_deployment: str
        :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
         have.
         Passing null causes the model to use its default value.
         Returns a 422 error if the model doesn't support the value or parameter. Default value is
         None.
        :paramtype dimensions: int
        :keyword encoding_format: Optional. The number of dimensions the resulting output embeddings
         should have.
         Passing null causes the model to use its default value.
         Returns a 422 error if the model doesn't support the value or parameter. Known values are:
         "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
        :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
        :keyword input_type: Optional. The type of the input.
         Returns a 422 error if the model doesn't support the value or parameter. Known values are:
         "text", "query", and "document". Default value is None.
        :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map: MutableMapping[int, Type[HttpResponseError]] = {
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
            if input is _Unset:
                raise TypeError("missing required argument: input")
            body = {
                "dimensions": dimensions,
                "encoding_format": encoding_format,
                "input": input,
                "input_type": input_type,
            }
            if hyper_params is not None:
                body.update(hyper_params)
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_embeddings_embedding_request(
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

        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                await response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if _stream:
            deserialized = response.iter_bytes()
        else:
            deserialized = _deserialize(_models.EmbeddingsResult, response.json())

        return deserialized  # type: ignore


class ImageEmbeddingsClient(ImageEmbeddingsClientGenerated):

    @overload
    async def embedding(
        self,
        body: JSON,
        *,
        model_deployment: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models.EmbeddingsResult:
        """Return the embeddings for given images.

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
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def embedding(
        self,
        *,
        hyper_params: Optional[Dict[str, Any]] = None,
        input: List[_models.EmbeddingInput],
        model_deployment: Optional[str] = None,
        content_type: str = "application/json",
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        **kwargs: Any
    ) -> _models.EmbeddingsResult:
        """Return the embeddings for given images.

        :keyword hyper_params: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these hypter parameters depends on the value of the
         ``unknown-parameters`` request header. Default value is None.
        :paramtype hyper_params: dict[str, Any]
        :keyword input: Input image to embed. To embed multiple inputs in a single request, pass an
         array.
         The input must not exceed the max input tokens for the model. Required.
        :paramtype input: list[~azure.ai.inference.models.EmbeddingInput]
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
        :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
         have.
         Passing null causes the model to use its default value.
         Returns a 422 error if the model doesn't support the value or parameter. Default value is
         None.
        :paramtype dimensions: int
        :keyword encoding_format: Optional. The number of dimensions the resulting output embeddings
         should have.
         Passing null causes the model to use its default value.
         Returns a 422 error if the model doesn't support the value or parameter. Known values are:
         "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
        :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
        :keyword input_type: Optional. The type of the input.
         Returns a 422 error if the model doesn't support the value or parameter. Known values are:
         "text", "query", and "document". Default value is None.
        :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def embedding(
        self,
        body: IO[bytes],
        *,
        model_deployment: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models.EmbeddingsResult:
        """Return the embeddings for given images.

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
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def embedding(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        hyper_params: Optional[Dict[str, Any]] = None,
        input: List[_models.EmbeddingInput] = _Unset,
        model_deployment: Optional[str] = None,
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        **kwargs: Any
    ) -> _models.EmbeddingsResult:
        # pylint: disable=line-too-long
        """Return the embeddings for given images.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword hyper_params: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these hypter parameters depends on the value of the
         ``unknown-parameters`` request header. Default value is None.
        :paramtype hyper_params: dict[str, Any]
        :keyword input: Input image to embed. To embed multiple inputs in a single request, pass an
         array.
         The input must not exceed the max input tokens for the model. Required.
        :paramtype input: list[~azure.ai.inference.models.EmbeddingInput]
        :keyword model_deployment: Name of the deployment to which you would like to route the request.
         Relevant only to Model-as-a-Platform (MaaP) deployments.
         Typically used when you want to target a test environment instead of production environment.
         Default value is None.
        :paramtype model_deployment: str
        :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
         have.
         Passing null causes the model to use its default value.
         Returns a 422 error if the model doesn't support the value or parameter. Default value is
         None.
        :paramtype dimensions: int
        :keyword encoding_format: Optional. The number of dimensions the resulting output embeddings
         should have.
         Passing null causes the model to use its default value.
         Returns a 422 error if the model doesn't support the value or parameter. Known values are:
         "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
        :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
        :keyword input_type: Optional. The type of the input.
         Returns a 422 error if the model doesn't support the value or parameter. Known values are:
         "text", "query", and "document". Default value is None.
        :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map: MutableMapping[int, Type[HttpResponseError]] = {
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
            if input is _Unset:
                raise TypeError("missing required argument: input")
            body = {
                "dimensions": dimensions,
                "encoding_format": encoding_format,
                "input": input,
                "input_type": input_type,
            }
            if hyper_params is not None:
                body.update(hyper_params)
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_image_embeddings_embedding_request(
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

        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                await response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if _stream:
            deserialized = response.iter_bytes()
        else:
            deserialized = _deserialize(_models.EmbeddingsResult, response.json())

        return deserialized  # type: ignore


__all__: List[str] = [
    "load_client",
    "ChatCompletionsClient",
    "EmbeddingsClient",
    "ImageEmbeddingsClient",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
