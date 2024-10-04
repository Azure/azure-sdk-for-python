# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=too-many-lines)
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import json
import logging
import sys

from io import IOBase
from typing import Any, Dict, Union, IO, List, Literal, Optional, overload, Type, TYPE_CHECKING, AsyncIterable

from azure.core.pipeline import PipelineResponse
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    map_error,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
)
from .. import models as _models
from .._model_base import SdkJSONEncoder, _deserialize
from ._client import ChatCompletionsClient as ChatCompletionsClientGenerated
from ._client import EmbeddingsClient as EmbeddingsClientGenerated
from ._client import ImageEmbeddingsClient as ImageEmbeddingsClientGenerated
from .._operations._operations import (
    build_chat_completions_complete_request,
    build_embeddings_embed_request,
    build_image_embeddings_embed_request,
)

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials_async import AsyncTokenCredential

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_Unset: Any = object()
_LOGGER = logging.getLogger(__name__)


async def load_client(
    endpoint: str, credential: Union[AzureKeyCredential, "AsyncTokenCredential"], **kwargs: Any
) -> Union["ChatCompletionsClient", "EmbeddingsClient", "ImageEmbeddingsClient"]:
    # pylint: disable=line-too-long
    """
    Load a client from a given endpoint URL. The method makes a REST API call to the `/info` route
    on the given endpoint, to determine the model type and therefore which client to instantiate.

    :param endpoint: Service host. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a AsyncTokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "2024-05-01-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    :return: The appropriate asynchronous client associated with the given endpoint
    :rtype: ~azure.ai.inference.aio.ChatCompletionsClient or ~azure.ai.inference.aio.EmbeddingsClient
     or ~azure.ai.inference.aio.ImageEmbeddingsClient
    :raises ~azure.core.exceptions.HttpResponseError:
    """

    async with ChatCompletionsClient(
        endpoint, credential, **kwargs
    ) as client:  # Pick any of the clients, it does not matter.
        model_info = await client.get_model_info()  # type: ignore

    _LOGGER.info("model_info=%s", model_info)
    if not model_info.model_type:
        raise ValueError(
            "The AI model information is missing a value for `model type`. Cannot create an appropriate client."
        )

    # TODO: Remove "completions" and "embedding" once Mistral Large and Cohere fixes their model type
    if model_info.model_type in (_models.ModelType.CHAT, "completion"):
        chat_completion_client = ChatCompletionsClient(endpoint, credential, **kwargs)
        chat_completion_client._model_info = (  # pylint: disable=protected-access,attribute-defined-outside-init
            model_info
        )
        return chat_completion_client

    if model_info.model_type in (_models.ModelType.EMBEDDINGS, "embedding"):
        embedding_client = EmbeddingsClient(endpoint, credential, **kwargs)
        embedding_client._model_info = model_info  # pylint: disable=protected-access,attribute-defined-outside-init
        return embedding_client

    if model_info.model_type == _models.ModelType.IMAGE_EMBEDDINGS:
        image_embedding_client = ImageEmbeddingsClient(endpoint, credential, **kwargs)
        image_embedding_client._model_info = (  # pylint: disable=protected-access,attribute-defined-outside-init
            model_info
        )
        return image_embedding_client

    raise ValueError(f"No client available to support AI model type `{model_info.model_type}`")


class ChatCompletionsClient(ChatCompletionsClientGenerated):  # pylint: disable=too-many-instance-attributes
    """ChatCompletionsClient.

    :param endpoint: Service host. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a AsyncTokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword frequency_penalty: A value that influences the probability of generated tokens
        appearing based on their cumulative frequency in generated text.
        Positive values will make tokens less likely to appear as their frequency increases and
        decrease the likelihood of the model repeating the same statements verbatim.
        Supported range is [-2, 2].
        Default value is None.
    :paramtype frequency_penalty: float
    :keyword presence_penalty: A value that influences the probability of generated tokens
        appearing based on their existing
        presence in generated text.
        Positive values will make tokens less likely to appear when they already exist and increase
        the model's likelihood to output new topics.
        Supported range is [-2, 2].
        Default value is None.
    :paramtype presence_penalty: float
    :keyword temperature: The sampling temperature to use that controls the apparent creativity of
        generated completions.
        Higher values will make output more random while lower values will make results more focused
        and deterministic.
        It is not recommended to modify temperature and top_p for the same completions request as the
        interaction of these two settings is difficult to predict.
        Supported range is [0, 1].
        Default value is None.
    :paramtype temperature: float
    :keyword top_p: An alternative to sampling with temperature called nucleus sampling. This value
        causes the
        model to consider the results of tokens with the provided probability mass. As an example, a
        value of 0.15 will cause only the tokens comprising the top 15% of probability mass to be
        considered.
        It is not recommended to modify temperature and top_p for the same completions request as the
        interaction of these two settings is difficult to predict.
        Supported range is [0, 1].
        Default value is None.
    :paramtype top_p: float
    :keyword max_tokens: The maximum number of tokens to generate. Default value is None.
    :paramtype max_tokens: int
    :keyword response_format: The format that the model must output. Use this to enable JSON mode
        instead of the default text mode.
        Note that to enable JSON mode, some AI models may also require you to instruct the model to
        produce JSON via a system or user message. Default value is None.
    :paramtype response_format: ~azure.ai.inference.models.ChatCompletionsResponseFormat
    :keyword stop: A collection of textual sequences that will end completions generation. Default
        value is None.
    :paramtype stop: list[str]
    :keyword tools: The available tool definitions that the chat completions request can use,
        including caller-defined functions. Default value is None.
    :paramtype tools: list[~azure.ai.inference.models.ChatCompletionsToolDefinition]
    :keyword tool_choice: If specified, the model will configure which of the provided tools it can
        use for the chat completions response. Is either a Union[str,
        "_models.ChatCompletionsToolChoicePreset"] type or a ChatCompletionsNamedToolChoice type.
        Default value is None.
    :paramtype tool_choice: str or ~azure.ai.inference.models.ChatCompletionsToolChoicePreset or
        ~azure.ai.inference.models.ChatCompletionsNamedToolChoice
    :keyword seed: If specified, the system will make a best effort to sample deterministically
        such that repeated requests with the
        same seed and parameters should return the same result. Determinism is not guaranteed.
        Default value is None.
    :paramtype seed: int
    :keyword model: ID of the specific AI model to use, if more than one model is available on the
        endpoint. Default value is None.
    :paramtype model: str
    :keyword model_extras: Additional, model-specific parameters that are not in the
        standard request payload. They will be added as-is to the root of the JSON in the request body.
        How the service handles these extra parameters depends on the value of the
        ``extra-parameters`` request header. Default value is None.
    :paramtype model_extras: dict[str, Any]
    :keyword api_version: The API version to use for this operation. Default value is
     "2024-05-01-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "AsyncTokenCredential"],
        *,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[_models.ChatCompletionsResponseFormat] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolChoicePreset, _models.ChatCompletionsNamedToolChoice]
        ] = None,
        seed: Optional[int] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:

        self._model_info: Optional[_models.ModelInfo] = None

        # Store default chat completions settings, to be applied in all future service calls
        # unless overridden by arguments in the `complete` method.
        self._frequency_penalty = frequency_penalty
        self._presence_penalty = presence_penalty
        self._temperature = temperature
        self._top_p = top_p
        self._max_tokens = max_tokens
        self._response_format = response_format
        self._stop = stop
        self._tools = tools
        self._tool_choice = tool_choice
        self._seed = seed
        self._model = model
        self._model_extras = model_extras

        super().__init__(endpoint, credential, **kwargs)

    @overload
    async def complete(
        self,
        *,
        messages: List[_models.ChatRequestMessage],
        stream: Literal[False] = False,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[_models.ChatCompletionsResponseFormat] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolChoicePreset, _models.ChatCompletionsNamedToolChoice]
        ] = None,
        seed: Optional[int] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> _models.ChatCompletions: ...

    @overload
    async def complete(
        self,
        *,
        messages: List[_models.ChatRequestMessage],
        stream: Literal[True],
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[_models.ChatCompletionsResponseFormat] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolChoicePreset, _models.ChatCompletionsNamedToolChoice]
        ] = None,
        seed: Optional[int] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> AsyncIterable[_models.StreamingChatCompletionsUpdate]: ...

    @overload
    async def complete(
        self,
        *,
        messages: List[_models.ChatRequestMessage],
        stream: Optional[bool] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[_models.ChatCompletionsResponseFormat] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolChoicePreset, _models.ChatCompletionsNamedToolChoice]
        ] = None,
        seed: Optional[int] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[AsyncIterable[_models.StreamingChatCompletionsUpdate], _models.ChatCompletions]:
        # pylint: disable=line-too-long
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data. The method makes a REST API call to the `/chat/completions` route
        on the given endpoint.
        When using this method with `stream=True`, the response is streamed
        back to the client. Iterate over the resulting StreamingChatCompletions
        object to get content updates as they arrive. By default, the response is a ChatCompletions object
        (non-streaming).

        :keyword messages: The collection of context messages associated with this chat completions
         request.
         Typical usage begins with a chat message for the System role that provides instructions for
         the behavior of the assistant, followed by alternating messages between the User and
         Assistant roles. Required.
        :paramtype messages: list[~azure.ai.inference.models.ChatRequestMessage]
        :keyword stream: A value indicating whether chat completions should be streamed for this request.
         Default value is False. If streaming is enabled, the response will be a StreamingChatCompletions.
         Otherwise the response will be a ChatCompletions.
        :paramtype stream: bool
        :keyword frequency_penalty: A value that influences the probability of generated tokens
         appearing based on their cumulative frequency in generated text.
         Positive values will make tokens less likely to appear as their frequency increases and
         decrease the likelihood of the model repeating the same statements verbatim.
         Supported range is [-2, 2].
         Default value is None.
        :paramtype frequency_penalty: float
        :keyword presence_penalty: A value that influences the probability of generated tokens
         appearing based on their existing
         presence in generated text.
         Positive values will make tokens less likely to appear when they already exist and increase
         the model's likelihood to output new topics.
         Supported range is [-2, 2].
         Default value is None.
        :paramtype presence_penalty: float
        :keyword temperature: The sampling temperature to use that controls the apparent creativity of
         generated completions.
         Higher values will make output more random while lower values will make results more focused
         and deterministic.
         It is not recommended to modify temperature and top_p for the same completions request as the
         interaction of these two settings is difficult to predict.
         Supported range is [0, 1].
         Default value is None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature called nucleus sampling. This value
         causes the
         model to consider the results of tokens with the provided probability mass. As an example, a
         value of 0.15 will cause only the tokens comprising the top 15% of probability mass to be
         considered.
         It is not recommended to modify temperature and top_p for the same completions request as the
         interaction of these two settings is difficult to predict.
         Supported range is [0, 1].
         Default value is None.
        :paramtype top_p: float
        :keyword max_tokens: The maximum number of tokens to generate. Default value is None.
        :paramtype max_tokens: int
        :keyword response_format: The format that the model must output. Use this to enable JSON mode
         instead of the default text mode.
         Note that to enable JSON mode, some AI models may also require you to instruct the model to
         produce JSON via a system or user message. Default value is None.
        :paramtype response_format: ~azure.ai.inference.models.ChatCompletionsResponseFormat
        :keyword stop: A collection of textual sequences that will end completions generation. Default
         value is None.
        :paramtype stop: list[str]
        :keyword tools: The available tool definitions that the chat completions request can use,
         including caller-defined functions. Default value is None.
        :paramtype tools: list[~azure.ai.inference.models.ChatCompletionsToolDefinition]
        :keyword tool_choice: If specified, the model will configure which of the provided tools it can
         use for the chat completions response. Is either a Union[str,
         "_models.ChatCompletionsToolChoicePreset"] type or a ChatCompletionsNamedToolChoice type.
         Default value is None.
        :paramtype tool_choice: str or ~azure.ai.inference.models.ChatCompletionsToolChoicePreset or
         ~azure.ai.inference.models.ChatCompletionsNamedToolChoice
        :keyword seed: If specified, the system will make a best effort to sample deterministically
         such that repeated requests with the
         same seed and parameters should return the same result. Determinism is not guaranteed.
         Default value is None.
        :paramtype seed: int
        :keyword model: ID of the specific AI model to use, if more than one model is available on the
         endpoint. Default value is None.
        :paramtype model: str
        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``extra-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
        :return: ChatCompletions for non-streaming, or AsyncIterable[StreamingChatCompletionsUpdate] for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.AsyncStreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def complete(
        self,
        body: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> Union[AsyncIterable[_models.StreamingChatCompletionsUpdate], _models.ChatCompletions]:
        # pylint: disable=line-too-long
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data.

        :param body: An object of type MutableMapping[str, Any], such as a dictionary, that
         specifies the full request payload. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ChatCompletions for non-streaming, or AsyncIterable[StreamingChatCompletionsUpdate] for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.AsyncStreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def complete(
        self,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> Union[AsyncIterable[_models.StreamingChatCompletionsUpdate], _models.ChatCompletions]:
        # pylint: disable=line-too-long
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data.

        :param body: Specifies the full request payload. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ChatCompletions for non-streaming, or AsyncIterable[StreamingChatCompletionsUpdate] for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.AsyncStreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def complete(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        messages: List[_models.ChatRequestMessage] = _Unset,
        stream: Optional[bool] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[_models.ChatCompletionsResponseFormat] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolChoicePreset, _models.ChatCompletionsNamedToolChoice]
        ] = None,
        seed: Optional[int] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[AsyncIterable[_models.StreamingChatCompletionsUpdate], _models.ChatCompletions]:
        # pylint: disable=line-too-long
        # pylint: disable=too-many-locals
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data. When using this method with `stream=True`, the response is streamed
        back to the client. Iterate over the resulting :class:`~azure.ai.inference.models.StreamingChatCompletions`
        object to get content updates as they arrive.

        :param body: Is either a MutableMapping[str, Any] type (like a dictionary) or a IO[bytes] type
         that specifies the full request payload. Required.
        :type body: JSON or IO[bytes]
        :keyword messages: The collection of context messages associated with this chat completions
         request.
         Typical usage begins with a chat message for the System role that provides instructions for
         the behavior of the assistant, followed by alternating messages between the User and
         Assistant roles. Required.
        :paramtype messages: list[~azure.ai.inference.models.ChatRequestMessage]
        :keyword stream: A value indicating whether chat completions should be streamed for this request.
         Default value is False. If streaming is enabled, the response will be a StreamingChatCompletions.
         Otherwise the response will be a ChatCompletions.
        :paramtype stream: bool
        :keyword frequency_penalty: A value that influences the probability of generated tokens
         appearing based on their cumulative frequency in generated text.
         Positive values will make tokens less likely to appear as their frequency increases and
         decrease the likelihood of the model repeating the same statements verbatim.
         Supported range is [-2, 2].
         Default value is None.
        :paramtype frequency_penalty: float
        :keyword presence_penalty: A value that influences the probability of generated tokens
         appearing based on their existing
         presence in generated text.
         Positive values will make tokens less likely to appear when they already exist and increase
         the model's likelihood to output new topics.
         Supported range is [-2, 2].
         Default value is None.
        :paramtype presence_penalty: float
        :keyword temperature: The sampling temperature to use that controls the apparent creativity of
         generated completions.
         Higher values will make output more random while lower values will make results more focused
         and deterministic.
         It is not recommended to modify temperature and top_p for the same completions request as the
         interaction of these two settings is difficult to predict.
         Supported range is [0, 1].
         Default value is None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature called nucleus sampling. This value
         causes the
         model to consider the results of tokens with the provided probability mass. As an example, a
         value of 0.15 will cause only the tokens comprising the top 15% of probability mass to be
         considered.
         It is not recommended to modify temperature and top_p for the same completions request as the
         interaction of these two settings is difficult to predict.
         Supported range is [0, 1].
         Default value is None.
        :paramtype top_p: float
        :keyword max_tokens: The maximum number of tokens to generate. Default value is None.
        :paramtype max_tokens: int
        :keyword response_format: The format that the model must output. Use this to enable JSON mode
         instead of the default text mode.
         Note that to enable JSON mode, some AI models may also require you to instruct the model to
         produce JSON via a system or user message. Default value is None.
        :paramtype response_format: ~azure.ai.inference.models.ChatCompletionsResponseFormat
        :keyword stop: A collection of textual sequences that will end completions generation. Default
         value is None.
        :paramtype stop: list[str]
        :keyword tools: The available tool definitions that the chat completions request can use,
         including caller-defined functions. Default value is None.
        :paramtype tools: list[~azure.ai.inference.models.ChatCompletionsToolDefinition]
        :keyword tool_choice: If specified, the model will configure which of the provided tools it can
         use for the chat completions response. Is either a Union[str,
         "_models.ChatCompletionsToolChoicePreset"] type or a ChatCompletionsNamedToolChoice type.
         Default value is None.
        :paramtype tool_choice: str or ~azure.ai.inference.models.ChatCompletionsToolChoicePreset or
         ~azure.ai.inference.models.ChatCompletionsNamedToolChoice
        :keyword seed: If specified, the system will make a best effort to sample deterministically
         such that repeated requests with the
         same seed and parameters should return the same result. Determinism is not guaranteed.
         Default value is None.
        :paramtype seed: int
        :keyword model: ID of the specific AI model to use, if more than one model is available on the
         endpoint. Default value is None.
        :paramtype model: str
        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``extra-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
        :return: ChatCompletions for non-streaming, or AsyncIterable[StreamingChatCompletionsUpdate] for streaming.
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
        _extra_parameters: Union[_models._enums.ExtraParameters, None] = None

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))

        if body is _Unset:
            if messages is _Unset:
                raise TypeError("missing required argument: messages")
            body = {
                "messages": messages,
                "stream": stream,
                "frequency_penalty": frequency_penalty if frequency_penalty is not None else self._frequency_penalty,
                "max_tokens": max_tokens if max_tokens is not None else self._max_tokens,
                "model": model if model is not None else self._model,
                "presence_penalty": presence_penalty if presence_penalty is not None else self._presence_penalty,
                "response_format": response_format if response_format is not None else self._response_format,
                "seed": seed if seed is not None else self._seed,
                "stop": stop if stop is not None else self._stop,
                "temperature": temperature if temperature is not None else self._temperature,
                "tool_choice": tool_choice if tool_choice is not None else self._tool_choice,
                "tools": tools if tools is not None else self._tools,
                "top_p": top_p if top_p is not None else self._top_p,
            }
            if model_extras is not None and bool(model_extras):
                body.update(model_extras)
                _extra_parameters = _models._enums.ExtraParameters.PASS_THROUGH  # pylint: disable=protected-access
            elif self._model_extras is not None and bool(self._model_extras):
                body.update(self._model_extras)
                _extra_parameters = _models._enums.ExtraParameters.PASS_THROUGH  # pylint: disable=protected-access
            body = {k: v for k, v in body.items() if v is not None}
        elif isinstance(body, dict) and "stream" in body and isinstance(body["stream"], bool):
            stream = body["stream"]
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_chat_completions_complete_request(
            extra_params=_extra_parameters,
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

        return _deserialize(_models._patch.ChatCompletions, response.json())  # pylint: disable=protected-access

    @distributed_trace_async
    async def get_model_info(self, **kwargs: Any) -> _models.ModelInfo:
        # pylint: disable=line-too-long
        """Returns information about the AI model.
        The method makes a REST API call to the ``/info`` route on the given endpoint.
        This method will only work when using Serverless API or Managed Compute endpoint.
        It will not work for GitHub Models endpoint or Azure OpenAI endpoint.

        :return: ModelInfo. The ModelInfo is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.ModelInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if not self._model_info:
            self._model_info = await self._get_model_info(**kwargs)  # pylint: disable=attribute-defined-outside-init
        return self._model_info

    def __str__(self) -> str:
        # pylint: disable=client-method-name-no-double-underscore
        return super().__str__() + f"\n{self._model_info}" if self._model_info else super().__str__()


class EmbeddingsClient(EmbeddingsClientGenerated):
    """EmbeddingsClient.

    :param endpoint: Service host. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a AsyncTokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
        have. Default value is None.
    :paramtype dimensions: int
    :keyword encoding_format: Optional. The desired format for the returned embeddings.
        Known values are:
        "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
    :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
    :keyword input_type: Optional. The type of the input. Known values are:
        "text", "query", and "document". Default value is None.
    :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
    :keyword model: ID of the specific AI model to use, if more than one model is available on the
        endpoint. Default value is None.
    :paramtype model: str
    :keyword model_extras: Additional, model-specific parameters that are not in the
        standard request payload. They will be added as-is to the root of the JSON in the request body.
        How the service handles these extra parameters depends on the value of the
        ``extra-parameters`` request header. Default value is None.
    :paramtype model_extras: dict[str, Any]
    :keyword api_version: The API version to use for this operation. Default value is
     "2024-05-01-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "AsyncTokenCredential"],
        *,
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:

        self._model_info: Optional[_models.ModelInfo] = None

        # Store default embeddings settings, to be applied in all future service calls
        # unless overridden by arguments in the `embed` method.
        self._dimensions = dimensions
        self._encoding_format = encoding_format
        self._input_type = input_type
        self._model = model
        self._model_extras = model_extras

        super().__init__(endpoint, credential, **kwargs)

    @overload
    async def embed(
        self,
        *,
        input: List[str],
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> _models.EmbeddingsResult:
        """Return the embedding vectors for given text prompts.
        The method makes a REST API call to the `/embeddings` route on the given endpoint.

        :keyword input: Input text to embed, encoded as a string or array of tokens.
         To embed multiple inputs in a single request, pass an array
         of strings or array of token arrays. Required.
        :paramtype input: list[str]
        :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
         have. Default value is None.
        :paramtype dimensions: int
        :keyword encoding_format: Optional. The desired format for the returned embeddings.
         Known values are:
         "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
        :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
        :keyword input_type: Optional. The type of the input. Known values are:
         "text", "query", and "document". Default value is None.
        :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
        :keyword model: ID of the specific AI model to use, if more than one model is available on the
         endpoint. Default value is None.
        :paramtype model: str
        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``extra-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def embed(
        self,
        body: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.EmbeddingsResult:
        """Return the embedding vectors for given text prompts.
        The method makes a REST API call to the `/embeddings` route on the given endpoint.

        :param body: An object of type MutableMapping[str, Any], such as a dictionary, that
         specifies the full request payload. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def embed(
        self,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.EmbeddingsResult:
        """Return the embedding vectors for given text prompts.
        The method makes a REST API call to the `/embeddings` route on the given endpoint.

        :param body: Specifies the full request payload. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def embed(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        input: List[str] = _Unset,
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> _models.EmbeddingsResult:
        # pylint: disable=line-too-long
        """Return the embedding vectors for given text prompts.
        The method makes a REST API call to the `/embeddings` route on the given endpoint.

        :param body: Is either a MutableMapping[str, Any] type (like a dictionary) or a IO[bytes] type
         that specifies the full request payload. Required.
        :type body: JSON or IO[bytes]
        :keyword input: Input text to embed, encoded as a string or array of tokens.
         To embed multiple inputs in a single request, pass an array
         of strings or array of token arrays. Required.
        :paramtype input: list[str]
        :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
         have. Default value is None.
        :paramtype dimensions: int
        :keyword encoding_format: Optional. The desired format for the returned embeddings.
         Known values are:
         "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
        :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
        :keyword input_type: Optional. The type of the input. Known values are:
         "text", "query", and "document". Default value is None.
        :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
        :keyword model: ID of the specific AI model to use, if more than one model is available on the
         endpoint. Default value is None.
        :paramtype model: str
        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``extra-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
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
        _extra_parameters: Union[_models._enums.ExtraParameters, None] = None

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))

        if body is _Unset:
            if input is _Unset:
                raise TypeError("missing required argument: input")
            body = {
                "input": input,
                "dimensions": dimensions if dimensions is not None else self._dimensions,
                "encoding_format": encoding_format if encoding_format is not None else self._encoding_format,
                "input_type": input_type if input_type is not None else self._input_type,
                "model": model if model is not None else self._model,
            }
            if model_extras is not None and bool(model_extras):
                body.update(model_extras)
                _extra_parameters = _models._enums.ExtraParameters.PASS_THROUGH  # pylint: disable=protected-access
            elif self._model_extras is not None and bool(self._model_extras):
                body.update(self._model_extras)
                _extra_parameters = _models._enums.ExtraParameters.PASS_THROUGH  # pylint: disable=protected-access
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_embeddings_embed_request(
            extra_params=_extra_parameters,
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
            deserialized = _deserialize(
                _models._patch.EmbeddingsResult, response.json()  # pylint: disable=protected-access
            )

        return deserialized  # type: ignore

    @distributed_trace_async
    async def get_model_info(self, **kwargs: Any) -> _models.ModelInfo:
        # pylint: disable=line-too-long
        """Returns information about the AI model.
        The method makes a REST API call to the ``/info`` route on the given endpoint.
        This method will only work when using Serverless API or Managed Compute endpoint.
        It will not work for GitHub Models endpoint or Azure OpenAI endpoint.

        :return: ModelInfo. The ModelInfo is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.ModelInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if not self._model_info:
            self._model_info = await self._get_model_info(**kwargs)  # pylint: disable=attribute-defined-outside-init
        return self._model_info

    def __str__(self) -> str:
        # pylint: disable=client-method-name-no-double-underscore
        return super().__str__() + f"\n{self._model_info}" if self._model_info else super().__str__()


class ImageEmbeddingsClient(ImageEmbeddingsClientGenerated):
    """ImageEmbeddingsClient.

    :param endpoint: Service host. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a AsyncTokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
        have. Default value is None.
    :paramtype dimensions: int
    :keyword encoding_format: Optional. The desired format for the returned embeddings.
        Known values are:
        "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
    :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
    :keyword input_type: Optional. The type of the input. Known values are:
        "text", "query", and "document". Default value is None.
    :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
    :keyword model: ID of the specific AI model to use, if more than one model is available on the
        endpoint. Default value is None.
    :paramtype model: str
    :keyword model_extras: Additional, model-specific parameters that are not in the
        standard request payload. They will be added as-is to the root of the JSON in the request body.
        How the service handles these extra parameters depends on the value of the
        ``extra-parameters`` request header. Default value is None.
    :paramtype model_extras: dict[str, Any]
    :keyword api_version: The API version to use for this operation. Default value is
     "2024-05-01-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "AsyncTokenCredential"],
        *,
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:

        self._model_info: Optional[_models.ModelInfo] = None

        # Store default embeddings settings, to be applied in all future service calls
        # unless overridden by arguments in the `embed` method.
        self._dimensions = dimensions
        self._encoding_format = encoding_format
        self._input_type = input_type
        self._model = model
        self._model_extras = model_extras

        super().__init__(endpoint, credential, **kwargs)

    @overload
    async def embed(
        self,
        *,
        input: List[_models.EmbeddingInput],
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> _models.EmbeddingsResult:
        """Return the embedding vectors for given images.
        The method makes a REST API call to the `/images/embeddings` route on the given endpoint.

        :keyword input: Input image to embed. To embed multiple inputs in a single request, pass an
         array.
         The input must not exceed the max input tokens for the model. Required.
        :paramtype input: list[~azure.ai.inference.models.EmbeddingInput]
        :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
         have. Default value is None.
        :paramtype dimensions: int
        :keyword encoding_format: Optional. The desired format for the returned embeddings.
         Known values are:
         "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
        :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
        :keyword input_type: Optional. Known values are:
         "text", "query", and "document". Default value is None.
        :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
        :keyword model: ID of the specific AI model to use, if more than one model is available on the
         endpoint. Default value is None.
        :paramtype model: str
        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``extra-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def embed(
        self,
        body: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.EmbeddingsResult:
        """Return the embedding vectors for given images.
        The method makes a REST API call to the `/images/embeddings` route on the given endpoint.

        :param body: An object of type MutableMapping[str, Any], such as a dictionary, that
         specifies the full request payload. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def embed(
        self,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.EmbeddingsResult:
        """Return the embedding vectors for given images.
        The method makes a REST API call to the `/images/embeddings` route on the given endpoint.

        :param body: Specifies the full request payload. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def embed(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        input: List[_models.EmbeddingInput] = _Unset,
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> _models.EmbeddingsResult:
        # pylint: disable=line-too-long
        """Return the embedding vectors for given images.
        The method makes a REST API call to the `/images/embeddings` route on the given endpoint.

        :param body: Is either a MutableMapping[str, Any] type (like a dictionary) or a IO[bytes] type
         that specifies the full request payload. Required.
        :type body: JSON or IO[bytes]
        :keyword input: Input image to embed. To embed multiple inputs in a single request, pass an
         array.
         The input must not exceed the max input tokens for the model. Required.
        :paramtype input: list[~azure.ai.inference.models.EmbeddingInput]
        :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
         have. Default value is None.
        :paramtype dimensions: int
        :keyword encoding_format: Optional. The desired format for the returned embeddings.
         Known values are:
         "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
        :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
        :keyword input_type: Optional. The type of the input. Known values are:
         "text", "query", and "document". Default value is None.
        :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
        :keyword model: ID of the specific AI model to use, if more than one model is available on the
         endpoint. Default value is None.
        :paramtype model: str
        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``extra-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
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
        _extra_parameters: Union[_models._enums.ExtraParameters, None] = None

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))

        if body is _Unset:
            if input is _Unset:
                raise TypeError("missing required argument: input")
            body = {
                "input": input,
                "dimensions": dimensions if dimensions is not None else self._dimensions,
                "encoding_format": encoding_format if encoding_format is not None else self._encoding_format,
                "input_type": input_type if input_type is not None else self._input_type,
                "model": model if model is not None else self._model,
            }
            if model_extras is not None and bool(model_extras):
                body.update(model_extras)
                _extra_parameters = _models._enums.ExtraParameters.PASS_THROUGH  # pylint: disable=protected-access
            elif self._model_extras is not None and bool(self._model_extras):
                body.update(self._model_extras)
                _extra_parameters = _models._enums.ExtraParameters.PASS_THROUGH  # pylint: disable=protected-access
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_image_embeddings_embed_request(
            extra_params=_extra_parameters,
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
            deserialized = _deserialize(
                _models._patch.EmbeddingsResult, response.json()  # pylint: disable=protected-access
            )

        return deserialized  # type: ignore

    @distributed_trace_async
    async def get_model_info(self, **kwargs: Any) -> _models.ModelInfo:
        # pylint: disable=line-too-long
        """Returns information about the AI model.
        The method makes a REST API call to the ``/info`` route on the given endpoint.
        This method will only work when using Serverless API or Managed Compute endpoint.
        It will not work for GitHub Models endpoint or Azure OpenAI endpoint.

        :return: ModelInfo. The ModelInfo is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.ModelInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if not self._model_info:
            self._model_info = await self._get_model_info(**kwargs)  # pylint: disable=attribute-defined-outside-init
        return self._model_info

    def __str__(self) -> str:
        # pylint: disable=client-method-name-no-double-underscore
        return super().__str__() + f"\n{self._model_info}" if self._model_info else super().__str__()


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
