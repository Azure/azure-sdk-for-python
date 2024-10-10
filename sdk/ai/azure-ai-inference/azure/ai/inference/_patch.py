# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=too-many-lines)
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize

Why do we patch auto-generated code?
1. Add support for input argument `model_extras` (all clients)
2. Add support for function load_client
3. Add support for setting sticky chat completions/embeddings input arguments in the client constructor
4. Add support for get_model_info, while caching the result (all clients)
5. Add support for chat completion streaming (ChatCompletionsClient client only)
6. Add support for friendly print of result objects (__str__ method) (all clients)
7. Add support for load() method in ImageUrl class (see /models/_patch.py).

"""
import os
import copy
import json
import logging
import sys
import importlib
import functools

from urllib.parse import urlparse
from enum import Enum
from io import IOBase
from typing import (
    Any,
    Callable,
    Dict,
    Union,
    IO,
    List,
    Literal,
    Optional,
    overload,
    Tuple,
    Type,
    TYPE_CHECKING,
    Iterator,
    Iterable,
)

from azure.core.pipeline import PipelineResponse
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    map_error,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
)

# pylint: disable = no-name-in-module
from azure.core import CaseInsensitiveEnumMeta  # type: ignore
from azure.core.settings import settings

from . import models as _models
from ._model_base import SdkJSONEncoder, _deserialize
from ._serialization import Serializer
from ._operations._operations import (
    build_chat_completions_complete_request,
    build_embeddings_embed_request,
    build_image_embeddings_embed_request,
)
from ._client import ChatCompletionsClient as ChatCompletionsClientGenerated
from ._client import EmbeddingsClient as EmbeddingsClientGenerated
from ._client import ImageEmbeddingsClient as ImageEmbeddingsClientGenerated

try:
    # pylint: disable = no-name-in-module
    from azure.core.tracing import AbstractSpan, SpanKind  # type: ignore
    from opentelemetry.trace import StatusCode, Span

    TRACING_LIBRARY_AVAILABLE = True
except ModuleNotFoundError as _:
    TRACING_LIBRARY_AVAILABLE = False


if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials import TokenCredential

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_Unset: Any = object()

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False

_LOGGER = logging.getLogger(__name__)


def load_client(
    endpoint: str, credential: Union[AzureKeyCredential, "TokenCredential"], **kwargs: Any
) -> Union["ChatCompletionsClient", "EmbeddingsClient", "ImageEmbeddingsClient"]:
    """
    Load a client from a given endpoint URL. The method makes a REST API call to the `/info` route
    on the given endpoint, to determine the model type and therefore which client to instantiate.
    This method will only work when using Serverless API or Managed Compute endpoint.
    It will not work for GitHub Models endpoint or Azure OpenAI endpoint.

    :param endpoint: Service host. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "2024-05-01-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    :return: The appropriate synchronous client associated with the given endpoint
    :rtype: ~azure.ai.inference.ChatCompletionsClient or ~azure.ai.inference.EmbeddingsClient
     or ~azure.ai.inference.ImageEmbeddingsClient
    :raises ~azure.core.exceptions.HttpResponseError:
    """

    with ChatCompletionsClient(
        endpoint, credential, **kwargs
    ) as client:  # Pick any of the clients, it does not matter.
        model_info = client.get_model_info()  # type: ignore

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
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
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
        credential: Union[AzureKeyCredential, "TokenCredential"],
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
    def complete(
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
    def complete(
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
    ) -> Iterable[_models.StreamingChatCompletionsUpdate]: ...

    @overload
    def complete(
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
    ) -> Union[Iterable[_models.StreamingChatCompletionsUpdate], _models.ChatCompletions]:
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
        :return: ChatCompletions for non-streaming, or Iterable[StreamingChatCompletionsUpdate] for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.StreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def complete(
        self,
        body: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> Union[Iterable[_models.StreamingChatCompletionsUpdate], _models.ChatCompletions]:
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
        :return: ChatCompletions for non-streaming, or Iterable[StreamingChatCompletionsUpdate] for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.StreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def complete(
        self,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> Union[Iterable[_models.StreamingChatCompletionsUpdate], _models.ChatCompletions]:
        # pylint: disable=line-too-long
        # pylint: disable=too-many-locals
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data.

        :param body: Specifies the full request payload. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ChatCompletions for non-streaming, or Iterable[StreamingChatCompletionsUpdate] for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.StreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    # pylint:disable=client-method-missing-tracing-decorator
    def complete(
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
    ) -> Union[Iterable[_models.StreamingChatCompletionsUpdate], _models.ChatCompletions]:
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
        :return: ChatCompletions for non-streaming, or Iterable[StreamingChatCompletionsUpdate] for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.StreamingChatCompletions
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
        pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if _stream:
            return _models.StreamingChatCompletions(response)

        return _deserialize(_models._patch.ChatCompletions, response.json())  # pylint: disable=protected-access

    @distributed_trace
    def get_model_info(self, **kwargs: Any) -> _models.ModelInfo:
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
            self._model_info = self._get_model_info(**kwargs)  # pylint: disable=attribute-defined-outside-init
        return self._model_info

    def __str__(self) -> str:
        # pylint: disable=client-method-name-no-double-underscore
        return super().__str__() + f"\n{self._model_info}" if self._model_info else super().__str__()


class EmbeddingsClient(EmbeddingsClientGenerated):
    """EmbeddingsClient.

    :param endpoint: Service host. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
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
        credential: Union[AzureKeyCredential, "TokenCredential"],
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
    def embed(
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
    def embed(
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
    def embed(
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

    @distributed_trace
    def embed(
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
        pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if _stream:
            deserialized = response.iter_bytes()
        else:
            deserialized = _deserialize(
                _models._patch.EmbeddingsResult, response.json()  # pylint: disable=protected-access
            )

        return deserialized  # type: ignore

    @distributed_trace
    def get_model_info(self, **kwargs: Any) -> _models.ModelInfo:
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
            self._model_info = self._get_model_info(**kwargs)  # pylint: disable=attribute-defined-outside-init
        return self._model_info

    def __str__(self) -> str:
        # pylint: disable=client-method-name-no-double-underscore
        return super().__str__() + f"\n{self._model_info}" if self._model_info else super().__str__()


class ImageEmbeddingsClient(ImageEmbeddingsClientGenerated):
    """ImageEmbeddingsClient.

    :param endpoint: Service host. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
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
        credential: Union[AzureKeyCredential, "TokenCredential"],
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
    def embed(
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
    def embed(
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
    def embed(
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

    @distributed_trace
    def embed(
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
        pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if _stream:
            deserialized = response.iter_bytes()
        else:
            deserialized = _deserialize(
                _models._patch.EmbeddingsResult, response.json()  # pylint: disable=protected-access
            )

        return deserialized  # type: ignore

    @distributed_trace
    def get_model_info(self, **kwargs: Any) -> _models.ModelInfo:
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
            self._model_info = self._get_model_info(**kwargs)  # pylint: disable=attribute-defined-outside-init
        return self._model_info

    def __str__(self) -> str:
        # pylint: disable=client-method-name-no-double-underscore
        return super().__str__() + f"\n{self._model_info}" if self._model_info else super().__str__()


_inference_traces_enabled: bool = False
_trace_inference_content: bool = False
INFERENCE_GEN_AI_SYSTEM_NAME = "az.ai.inference"


class TraceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):  # pylint: disable=C4747
    """An enumeration class to represent different types of traces."""

    INFERENCE = "Inference"


class AIInferenceInstrumentor:
    """
    A class for managing the trace instrumentation of AI Inference.

    This class allows enabling or disabling tracing for AI Inference.
    and provides functionality to check whether instrumentation is active.

    """

    def __init__(self):
        if not TRACING_LIBRARY_AVAILABLE:
            raise ModuleNotFoundError(
                "Azure Core Tracing Opentelemetry is not installed. "
                "Please install it using 'pip install azure-core-tracing-opentelemetry'"
            )
        # In the future we could support different versions from the same library
        # and have a parameter that specifies the version to use.
        self._impl = AIInferenceInstrumentorPreview()

    def instrument(self):
        """
        Enable trace instrumentation for AI Inference.

        Raises:
            RuntimeError: If instrumentation is already enabled.

        """
        self._impl.instrument()

    def uninstrument(self):
        """
        Disable trace instrumentation for AI Inference.

        Raises:
            RuntimeError: If instrumentation is not currently enabled.

        This method removes any active instrumentation, stopping the tracing
        of AI Inference.
        """
        self._impl.uninstrument()

    def is_instrumented(self):
        """
        Check if trace instrumentation for AI Inference is currently enabled.

        :return: True if instrumentation is active, False otherwise.
        :rtype: bool
        """
        return self._impl.is_instrumented()


class AIInferenceInstrumentorPreview:
    """
    A class for managing the trace instrumentation of AI Inference.

    This class allows enabling or disabling tracing for AI Inference.
    and provides functionality to check whether instrumentation is active.
    """

    def _str_to_bool(self, s):
        if s is None:
            return False
        return str(s).lower() == "true"

    def instrument(self):
        """
        Enable trace instrumentation for AI Inference.

        Raises:
            RuntimeError: If instrumentation is already enabled.

        This method checks the environment variable
        'AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED' to determine
        whether to enable content tracing.
        """
        if self.is_instrumented():
            raise RuntimeError("Already instrumented")

        var_value = os.environ.get("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED")
        enable_content_tracing = self._str_to_bool(var_value)
        self._instrument_inference(enable_content_tracing)

    def uninstrument(self):
        """
        Disable trace instrumentation for AI Inference.

        Raises:
            RuntimeError: If instrumentation is not currently enabled.

        This method removes any active instrumentation, stopping the tracing
        of AI Inference.
        """
        if not self.is_instrumented():
            raise RuntimeError("Not instrumented")
        self._uninstrument_inference()

    def is_instrumented(self):
        """
        Check if trace instrumentation for AI Inference is currently enabled.

        :return: True if instrumentation is active, False otherwise.
        :rtype: bool
        """
        return self._is_instrumented()

    def _set_attributes(self, span: "AbstractSpan", *attrs: Tuple[str, Any]) -> None:
        for attr in attrs:
            key, value = attr
            if value is not None:
                span.add_attribute(key, value)

    def _add_request_chat_message_event(self, span: "AbstractSpan", **kwargs: Any) -> None:
        for message in kwargs.get("messages", []):
            try:
                message = message.as_dict()
            except AttributeError:
                pass

            if message.get("role"):
                name = f"gen_ai.{message.get('role')}.message"
                span.span_instance.add_event(
                    name=name,
                    attributes={
                        "gen_ai.system": INFERENCE_GEN_AI_SYSTEM_NAME,
                        "gen_ai.event.content": json.dumps(message),
                    },
                )

    def _parse_url(self, url):
        parsed = urlparse(url)
        server_address = parsed.hostname
        port = parsed.port
        return server_address, port

    def _add_request_chat_attributes(self, span: "AbstractSpan", *args: Any, **kwargs: Any) -> None:
        client = args[0]
        endpoint = client._config.endpoint  # pylint: disable=protected-access
        server_address, port = self._parse_url(endpoint)
        model = "chat"
        if kwargs.get("model") is not None:
            model_value = kwargs.get("model")
            if model_value is not None:
                model = model_value

        self._set_attributes(
            span,
            ("gen_ai.operation.name", "chat"),
            ("gen_ai.system", INFERENCE_GEN_AI_SYSTEM_NAME),
            ("gen_ai.request.model", model),
            ("gen_ai.request.max_tokens", kwargs.get("max_tokens")),
            ("gen_ai.request.temperature", kwargs.get("temperature")),
            ("gen_ai.request.top_p", kwargs.get("top_p")),
            ("server.address", server_address),
        )
        if port is not None and port != 443:
            span.add_attribute("server.port", port)

    def _remove_function_call_names_and_arguments(self, tool_calls: list) -> list:
        tool_calls_copy = copy.deepcopy(tool_calls)
        for tool_call in tool_calls_copy:
            if "function" in tool_call:
                if "name" in tool_call["function"]:
                    del tool_call["function"]["name"]
                if "arguments" in tool_call["function"]:
                    del tool_call["function"]["arguments"]
                if not tool_call["function"]:
                    del tool_call["function"]
        return tool_calls_copy

    def _get_finish_reasons(self, result):
        if hasattr(result, "choices") and result.choices:
            finish_reasons = []
            for choice in result.choices:
                finish_reason = getattr(choice, "finish_reason", None)

                if finish_reason is None:
                    # If finish_reason is None, default to "none"
                    finish_reasons.append("none")
                elif hasattr(finish_reason, "value"):
                    # If finish_reason has a 'value' attribute (i.e., it's an enum), use it
                    finish_reasons.append(finish_reason.value)
                elif isinstance(finish_reason, str):
                    # If finish_reason is a string, use it directly
                    finish_reasons.append(finish_reason)
                else:
                    # For any other type, you might want to handle it or default to "none"
                    finish_reasons.append("none")

            return finish_reasons
        return None

    def _get_finish_reason_for_choice(self, choice):
        return (
            getattr(choice, "finish_reason", None).value
            if getattr(choice, "finish_reason", None) is not None
            else "none"
        )

    def _add_response_chat_message_event(self, span: "AbstractSpan", result: _models.ChatCompletions) -> None:
        for choice in result.choices:
            if _trace_inference_content:
                full_response: Dict[str, Any] = {
                    "message": {"content": choice.message.content},
                    "finish_reason": self._get_finish_reason_for_choice(choice),
                    "index": choice.index,
                }
                if choice.message.tool_calls:
                    full_response["message"]["tool_calls"] = [tool.as_dict() for tool in choice.message.tool_calls]
                attributes = {
                    "gen_ai.system": INFERENCE_GEN_AI_SYSTEM_NAME,
                    "gen_ai.event.content": json.dumps(full_response),
                }
            else:
                response: Dict[str, Any] = {
                    "finish_reason": self._get_finish_reason_for_choice(choice),
                    "index": choice.index,
                }
                if choice.message.tool_calls:
                    response["message"] = {}
                    tool_calls_function_names_and_arguments_removed = self._remove_function_call_names_and_arguments(
                        choice.message.tool_calls
                    )
                    response["message"]["tool_calls"] = [
                        tool.as_dict() for tool in tool_calls_function_names_and_arguments_removed
                    ]

                attributes = {
                    "gen_ai.system": INFERENCE_GEN_AI_SYSTEM_NAME,
                    "gen_ai.event.content": json.dumps(response),
                }
            span.span_instance.add_event(name="gen_ai.choice", attributes=attributes)

    def _add_response_chat_attributes(
        self, span: "AbstractSpan", result: Union[_models.ChatCompletions, _models.StreamingChatCompletionsUpdate]
    ) -> None:
        self._set_attributes(
            span,
            ("gen_ai.response.id", result.id),
            ("gen_ai.response.model", result.model),
            (
                "gen_ai.usage.input_tokens",
                result.usage.prompt_tokens if hasattr(result, "usage") and result.usage else None,
            ),
            (
                "gen_ai.usage.output_tokens",
                result.usage.completion_tokens if hasattr(result, "usage") and result.usage else None,
            ),
        )
        finish_reasons = self._get_finish_reasons(result)
        span.add_attribute("gen_ai.response.finish_reasons", finish_reasons)

    def _add_request_span_attributes(self, span: "AbstractSpan", _span_name: str, args: Any, kwargs: Any) -> None:
        self._add_request_chat_attributes(span, *args, **kwargs)
        if _trace_inference_content:
            self._add_request_chat_message_event(span, **kwargs)

    def _add_response_span_attributes(self, span: "AbstractSpan", result: object) -> None:
        if isinstance(result, _models.ChatCompletions):
            self._add_response_chat_attributes(span, result)
            self._add_response_chat_message_event(span, result)
        # TODO add more models here

    def _accumulate_response(self, item, accumulate: Dict[str, Any]) -> None:
        if item.finish_reason:
            accumulate["finish_reason"] = item.finish_reason
        if item.index:
            accumulate["index"] = item.index
        if item.delta.content:
            accumulate.setdefault("message", {})
            accumulate["message"].setdefault("content", "")
            accumulate["message"]["content"] += item.delta.content
        if item.delta.tool_calls:
            accumulate.setdefault("message", {})
            accumulate["message"].setdefault("tool_calls", [])
            if item.delta.tool_calls is not None:
                for tool_call in item.delta.tool_calls:
                    if tool_call.id:
                        accumulate["message"]["tool_calls"].append(
                            {"id": tool_call.id, "type": "", "function": {"name": "", "arguments": ""}}
                        )
                    if tool_call.function:
                        accumulate["message"]["tool_calls"][-1]["type"] = "function"
                    if tool_call.function and tool_call.function.name:
                        accumulate["message"]["tool_calls"][-1]["function"]["name"] = tool_call.function.name
                    if tool_call.function and tool_call.function.arguments:
                        accumulate["message"]["tool_calls"][-1]["function"]["arguments"] += tool_call.function.arguments

    def _wrapped_stream(
        self, stream_obj: _models.StreamingChatCompletions, span: "AbstractSpan"
    ) -> _models.StreamingChatCompletions:
        class StreamWrapper(_models.StreamingChatCompletions):
            def __init__(self, stream_obj, instrumentor):
                super().__init__(stream_obj._response)
                self._instrumentor = instrumentor

            def __iter__(self) -> Iterator[_models.StreamingChatCompletionsUpdate]:
                try:
                    accumulate: Dict[str, Any] = {}
                    chunk = None
                    for chunk in stream_obj:
                        for item in chunk.choices:
                            self._instrumentor._accumulate_response(item, accumulate)
                        yield chunk

                    if chunk is not None:
                        self._instrumentor._add_response_chat_attributes(span, chunk)

                except Exception as exc:
                    # Set the span status to error
                    if isinstance(span.span_instance, Span):
                        span.span_instance.set_status(StatusCode.ERROR, description=str(exc))
                    module = exc.__module__ if hasattr(exc, "__module__") and exc.__module__ != "builtins" else ""
                    error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                    self._instrumentor._set_attributes(span, ("error.type", error_type))
                    raise

                finally:
                    if stream_obj._done is False:
                        if accumulate.get("finish_reason") is None:
                            accumulate["finish_reason"] = "error"
                    else:
                        # Only one choice expected with streaming
                        accumulate["index"] = 0
                        # Delete message if content tracing is not enabled
                        if not _trace_inference_content:
                            if "message" in accumulate:
                                if "content" in accumulate["message"]:
                                    del accumulate["message"]["content"]
                                if not accumulate["message"]:
                                    del accumulate["message"]
                            if "message" in accumulate:
                                if "tool_calls" in accumulate["message"]:
                                    tool_calls_function_names_and_arguments_removed = (
                                        self._instrumentor._remove_function_call_names_and_arguments(
                                            accumulate["message"]["tool_calls"]
                                        )
                                    )
                                    accumulate["message"]["tool_calls"] = list(
                                        tool_calls_function_names_and_arguments_removed
                                    )

                    span.span_instance.add_event(
                        name="gen_ai.choice",
                        attributes={
                            "gen_ai.system": INFERENCE_GEN_AI_SYSTEM_NAME,
                            "gen_ai.event.content": json.dumps(accumulate),
                        },
                    )
                    span.finish()

        return StreamWrapper(stream_obj, self)

    def _trace_sync_function(
        self,
        function: Callable,
        *,
        _args_to_ignore: Optional[List[str]] = None,
        _trace_type=TraceType.INFERENCE,
        _name: Optional[str] = None,
    ) -> Callable:
        """
        Decorator that adds tracing to a synchronous function.

        :param function: The function to be traced.
        :type function: Callable
        :param args_to_ignore: A list of argument names to be ignored in the trace.
                            Defaults to None.
        :type: args_to_ignore: [List[str]], optional
        :param trace_type: The type of the trace. Defaults to TraceType.INFERENCE.
        :type trace_type: TraceType, optional
        :param name: The name of the trace, will set to func name if not provided.
        :type name: str, optional
        :return: The traced function.
        :rtype: Callable
        """

        @functools.wraps(function)
        def inner(*args, **kwargs):

            span_impl_type = settings.tracing_implementation()
            if span_impl_type is None:
                return function(*args, **kwargs)

            class_function_name = function.__qualname__

            if class_function_name.startswith("ChatCompletionsClient.complete"):
                if kwargs.get("model") is None:
                    span_name = "chat"
                else:
                    model = kwargs.get("model")
                    span_name = f"chat {model}"

                span = span_impl_type(name=span_name, kind=SpanKind.CLIENT)
                try:
                    # tracing events not supported in azure-core-tracing-opentelemetry
                    # so need to access the span instance directly
                    with span_impl_type.change_context(span.span_instance):
                        self._add_request_span_attributes(span, span_name, args, kwargs)
                        result = function(*args, **kwargs)
                        if kwargs.get("stream") is True:
                            return self._wrapped_stream(result, span)
                        self._add_response_span_attributes(span, result)

                except Exception as exc:
                    # Set the span status to error
                    if isinstance(span.span_instance, Span):
                        span.span_instance.set_status(StatusCode.ERROR, description=str(exc))
                    module = getattr(exc, "__module__", "")
                    module = module if module != "builtins" else ""
                    error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                    self._set_attributes(span, ("error.type", error_type))
                    span.finish()
                    raise

                span.finish()
                return result

            # Handle the default case (if the function name does not match)
            return None  # Ensure all paths return

        return inner

    def _trace_async_function(
        self,
        function: Callable,
        *,
        _args_to_ignore: Optional[List[str]] = None,
        _trace_type=TraceType.INFERENCE,
        _name: Optional[str] = None,
    ) -> Callable:
        """
        Decorator that adds tracing to an asynchronous function.

        :param function: The function to be traced.
        :type function: Callable
        :param args_to_ignore: A list of argument names to be ignored in the trace.
                            Defaults to None.
        :type: args_to_ignore: [List[str]], optional
        :param trace_type: The type of the trace. Defaults to TraceType.INFERENCE.
        :type trace_type: TraceType, optional
        :param name: The name of the trace, will set to func name if not provided.
        :type name: str, optional
        :return: The traced function.
        :rtype: Callable
        """

        @functools.wraps(function)
        async def inner(*args, **kwargs):
            span_impl_type = settings.tracing_implementation()
            if span_impl_type is None:
                return function(*args, **kwargs)

            class_function_name = function.__qualname__

            if class_function_name.startswith("ChatCompletionsClient.complete"):
                if kwargs.get("model") is None:
                    span_name = "chat"
                else:
                    model = kwargs.get("model")
                    span_name = f"chat {model}"

                span = span_impl_type(name=span_name, kind=SpanKind.CLIENT)
                try:
                    # tracing events not supported in azure-core-tracing-opentelemetry
                    # so need to access the span instance directly
                    with span_impl_type.change_context(span.span_instance):
                        self._add_request_span_attributes(span, span_name, args, kwargs)
                        result = await function(*args, **kwargs)
                        if kwargs.get("stream") is True:
                            return self._wrapped_stream(result, span)
                        self._add_response_span_attributes(span, result)

                except Exception as exc:
                    # Set the span status to error
                    if isinstance(span.span_instance, Span):
                        span.span_instance.set_status(StatusCode.ERROR, description=str(exc))
                    module = getattr(exc, "__module__", "")
                    module = module if module != "builtins" else ""
                    error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
                    self._set_attributes(span, ("error.type", error_type))
                    span.finish()
                    raise

                span.finish()
                return result

            # Handle the default case (if the function name does not match)
            return None  # Ensure all paths return

        return inner

    def _inject_async(self, f, _trace_type, _name):
        wrapper_fun = self._trace_async_function(f)
        wrapper_fun._original = f  # pylint: disable=protected-access
        return wrapper_fun

    def _inject_sync(self, f, _trace_type, _name):
        wrapper_fun = self._trace_sync_function(f)
        wrapper_fun._original = f  # pylint: disable=protected-access
        return wrapper_fun

    def _inference_apis(self):
        sync_apis = (
            (
                "azure.ai.inference",
                "ChatCompletionsClient",
                "complete",
                TraceType.INFERENCE,
                "inference_chat_completions_complete",
            ),
        )
        async_apis = (
            (
                "azure.ai.inference.aio",
                "ChatCompletionsClient",
                "complete",
                TraceType.INFERENCE,
                "inference_chat_completions_complete",
            ),
        )
        return sync_apis, async_apis

    def _inference_api_list(self):
        sync_apis, async_apis = self._inference_apis()
        yield sync_apis, self._inject_sync
        yield async_apis, self._inject_async

    def _generate_api_and_injector(self, apis):
        for api, injector in apis:
            for module_name, class_name, method_name, trace_type, name in api:
                try:
                    module = importlib.import_module(module_name)
                    api = getattr(module, class_name)
                    if hasattr(api, method_name):
                        yield api, method_name, trace_type, injector, name
                except AttributeError as e:
                    # Log the attribute exception with the missing class information
                    logging.warning(
                        "AttributeError: The module '%s' does not have the class '%s'. %s",
                        module_name,
                        class_name,
                        str(e),
                    )
                except Exception as e:  # pylint: disable=broad-except
                    # Log other exceptions as a warning, as we're not sure what they might be
                    logging.warning("An unexpected error occurred: '%s'", str(e))

    def _available_inference_apis_and_injectors(self):
        """
        Generates a sequence of tuples containing Inference API classes, method names, and
        corresponding injector functions.

        :return: A generator yielding tuples.
        :rtype: tuple
        """
        yield from self._generate_api_and_injector(self._inference_api_list())

    def _instrument_inference(self, enable_content_tracing: bool = False):
        """This function modifies the methods of the Inference API classes to
        inject logic before calling the original methods.
        The original methods are stored as _original attributes of the methods.

        :param enable_content_tracing: Indicates whether tracing of message content should be enabled.
                                    This also controls whether function call tool function names,
                                    parameter names and parameter values are traced.
        :type enable_content_tracing: bool
        """
        # pylint: disable=W0603
        global _inference_traces_enabled
        global _trace_inference_content
        if _inference_traces_enabled:
            raise RuntimeError("Traces already started for azure.ai.inference")
        _inference_traces_enabled = True
        _trace_inference_content = enable_content_tracing
        for api, method, trace_type, injector, name in self._available_inference_apis_and_injectors():
            # Check if the method of the api class has already been modified
            if not hasattr(getattr(api, method), "_original"):
                setattr(api, method, injector(getattr(api, method), trace_type, name))

    def _uninstrument_inference(self):
        """This function restores the original methods of the Inference API classes
        by assigning them back from the _original attributes of the modified methods.
        """
        # pylint: disable=W0603
        global _inference_traces_enabled
        global _trace_inference_content
        _trace_inference_content = False
        for api, method, _, _, _ in self._available_inference_apis_and_injectors():
            if hasattr(getattr(api, method), "_original"):
                setattr(api, method, getattr(getattr(api, method), "_original"))
        _inference_traces_enabled = False

    def _is_instrumented(self):
        """This function returns True if Inference libary has already been instrumented
        for tracing and False if it has not been instrumented.

        :return: A value indicating whether the Inference library is currently instrumented or not.
        :rtype: bool
        """
        return _inference_traces_enabled


__all__: List[str] = [
    "load_client",
    "ChatCompletionsClient",
    "EmbeddingsClient",
    "ImageEmbeddingsClient",
    "AIInferenceInstrumentor",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
