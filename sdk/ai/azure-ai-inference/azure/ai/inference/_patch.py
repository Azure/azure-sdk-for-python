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
3. Add support for get_model_info, while caching the result (all clients)
4. Add support for chat completion streaming (ChatCompletionsClient client only)
5. __enter__ (and __aenter__) method had to be overridden due to
   https://github.com/Azure/autorest.python/issues/2619 (all clients).
   Otherwise intellisense did not show the patched public methods on the client object,
   when the client is defined using context manager ("with" statement).
6. Add support for load() method in ImageUrl class (see /models/_patch.py).

"""
import json
import logging
import sys

from io import IOBase
from typing import Any, Dict, Union, IO, List, Literal, Optional, overload, Type, TYPE_CHECKING, Iterable

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

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

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
    :raises ~azure.core.exceptions.HttpResponseError
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
        chat_completion_client._model_info = ( # pylint: disable=protected-access,attribute-defined-outside-init
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


class ChatCompletionsClient(ChatCompletionsClientGenerated):
    """ChatCompletionsClient.

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
    """

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, "TokenCredential"], **kwargs: Any) -> None:
        self._model_info: Optional[_models.ModelInfo] = None
        super().__init__(endpoint, credential, **kwargs)

    @overload
    def complete(
        self,
        *,
        messages: List[_models.ChatRequestMessage],
        content_type: str = "application/json",
        model_extras: Optional[Dict[str, Any]] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Union[str, _models.ChatCompletionsResponseFormat]] = None,
        stop: Optional[List[str]] = None,
        stream: Literal[False] = False,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolSelectionPreset, _models.ChatCompletionsNamedToolSelection]
        ] = None,
        seed: Optional[int] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> _models.ChatCompletions: ...

    @overload
    def complete(
        self,
        *,
        messages: List[_models.ChatRequestMessage],
        content_type: str = "application/json",
        model_extras: Optional[Dict[str, Any]] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Union[str, _models.ChatCompletionsResponseFormat]] = None,
        stop: Optional[List[str]] = None,
        stream: Literal[True],
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolSelectionPreset, _models.ChatCompletionsNamedToolSelection]
        ] = None,
        seed: Optional[int] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Iterable[_models.StreamingChatCompletionsUpdate]: ...

    @overload
    def complete(
        self,
        *,
        messages: List[_models.ChatRequestMessage],
        content_type: str = "application/json",
        model_extras: Optional[Dict[str, Any]] = None,
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
        model: Optional[str] = None,
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
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``unknown-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
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
         same seed and parameters should return the same result. Determinism is not guaranteed.
         Default value is None.
        :paramtype seed: int
        :keyword model: ID of the specific AI model to use, if more than one model is available on the
         endpoint. Default value is None.
        :paramtype model: str
        :return: ChatCompletions for non-streaming, or Iterable[StreamingChatCompletionsUpdate] for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.StreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError
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
        :raises ~azure.core.exceptions.HttpResponseError
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
        :raises ~azure.core.exceptions.HttpResponseError
        """

    @distributed_trace
    def complete(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        messages: List[_models.ChatRequestMessage] = _Unset,
        model_extras: Optional[Dict[str, Any]] = None,
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
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[Iterable[_models.StreamingChatCompletionsUpdate], _models.ChatCompletions]:
        # pylint: disable=line-too-long
        # pylint: disable=too-many-locals
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data. When using this method with `stream=True`, the response is streamed
        back to the client. Iterate over the resulting ~azure.ai.inference.models.StreamingChatCompletions
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
        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``unknown-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
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
         same seed and parameters should return the same result. Determinism is not guaranteed.
         Default value is None.
        :paramtype seed: int
        :keyword model: ID of the specific AI model to use, if more than one model is available on the
         endpoint. Default value is None.
        :paramtype model: str
        :return: ChatCompletions for non-streaming, or Iterable[StreamingChatCompletionsUpdate] for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.StreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError
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
        _unknown_params: Union[_models._enums.UnknownParams, None] = None

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))

        if body is _Unset:
            if messages is _Unset:
                raise TypeError("missing required argument: messages")
            body = {
                "frequency_penalty": frequency_penalty,
                "max_tokens": max_tokens,
                "messages": messages,
                "model": model,
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
            if model_extras is not None and bool(model_extras):
                body.update(model_extras)
                _unknown_params = _models._enums.UnknownParams.PASS_THROUGH  # pylint: disable=protected-access
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
            unknown_params=_unknown_params,
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

        return _deserialize(_models._models.ChatCompletions, response.json())  # pylint: disable=protected-access

    @distributed_trace
    def get_model_info(self, **kwargs: Any) -> _models.ModelInfo:
        # pylint: disable=line-too-long
        """Returns information about the AI model.

        :return: ModelInfo. The ModelInfo is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.ModelInfo
        :raises ~azure.core.exceptions.HttpResponseError
        """
        if not self._model_info:
            self._model_info = self._get_model_info(**kwargs)  # pylint: disable=attribute-defined-outside-init
        return self._model_info

    def __str__(self) -> str:
        # pylint: disable=client-method-name-no-double-underscore
        return super().__str__() + f"\n{self._model_info}" if self._model_info else super().__str__()

    # Remove this once https://github.com/Azure/autorest.python/issues/2619 is fixed,
    # and you see the equivalent auto-generated method in _client.py return "Self"
    def __enter__(self) -> Self:
        self._client.__enter__()
        return self


class EmbeddingsClient(EmbeddingsClientGenerated):
    """EmbeddingsClient.

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
    """

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, "TokenCredential"], **kwargs: Any) -> None:
        self._model_info: Optional[_models.ModelInfo] = None
        super().__init__(endpoint, credential, **kwargs)

    @overload
    def embed(
        self,
        *,
        model_extras: Optional[Dict[str, Any]] = None,
        input: List[str],
        content_type: str = "application/json",
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        **kwargs: Any,
    ) -> _models.EmbeddingsResult:
        """Return the embedding vectors for given text prompts.
        The method makes a REST API call to the `/embeddings` route on the given endpoint.

        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``unknown-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
        :keyword input: Input text to embed, encoded as a string or array of tokens.
         To embed multiple inputs in a single request, pass an array
         of strings or array of token arrays. Required.
        :paramtype input: list[str]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
         have.
         Passing null causes the model to use its default value.
         Returns a 422 error if the model doesn't support the value or parameter. Default value is
         None.
        :paramtype dimensions: int
        :keyword encoding_format: Optional. The desired format for the returned embeddings.
         Known values are:
         "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
        :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
        :keyword input_type: Optional. The type of the input.
         Returns a 422 error if the model doesn't support the value or parameter. Known values are:
         "text", "query", and "document". Default value is None.
        :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError
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
        :raises ~azure.core.exceptions.HttpResponseError
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
        :raises ~azure.core.exceptions.HttpResponseError
        """

    @distributed_trace
    def embed(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        model_extras: Optional[Dict[str, Any]] = None,
        input: List[str] = _Unset,
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        **kwargs: Any,
    ) -> _models.EmbeddingsResult:
        # pylint: disable=line-too-long
        """Return the embedding vectors for given text prompts.
        The method makes a REST API call to the `/embeddings` route on the given endpoint.

        :param body: Is either a MutableMapping[str, Any] type (like a dictionary) or a IO[bytes] type
         that specifies the full request payload. Required.
        :type body: JSON or IO[bytes]
        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``unknown-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
        :keyword input: Input text to embed, encoded as a string or array of tokens.
         To embed multiple inputs in a single request, pass an array
         of strings or array of token arrays. Required.
        :paramtype input: list[str]
        :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
         have.
         Passing null causes the model to use its default value.
         Returns a 422 error if the model doesn't support the value or parameter. Default value is
         None.
        :paramtype dimensions: int
        :keyword encoding_format: Optional. The desired format for the returned embeddings.
         Known values are:
         "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
        :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
        :keyword input_type: Optional. The type of the input.
         Returns a 422 error if the model doesn't support the value or parameter. Known values are:
         "text", "query", and "document". Default value is None.
        :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError
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
        _unknown_params: Union[_models._enums.UnknownParams, None] = None

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
            if model_extras is not None and bool(model_extras):
                body.update(model_extras)
                _unknown_params = _models._enums.UnknownParams.PASS_THROUGH  # pylint: disable=protected-access
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_embeddings_embed_request(
            unknown_params=_unknown_params,
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
            deserialized = _deserialize(_models.EmbeddingsResult, response.json())

        return deserialized  # type: ignore

    @distributed_trace
    def get_model_info(self, **kwargs: Any) -> _models.ModelInfo:
        # pylint: disable=line-too-long
        """Returns information about the AI model.

        :return: ModelInfo. The ModelInfo is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.ModelInfo
        :raises ~azure.core.exceptions.HttpResponseError
        """
        if not self._model_info:
            self._model_info = self._get_model_info(**kwargs)  # pylint: disable=attribute-defined-outside-init
        return self._model_info

    def __str__(self) -> str:
        # pylint: disable=client-method-name-no-double-underscore
        return super().__str__() + f"\n{self._model_info}" if self._model_info else super().__str__()

    # Remove this once https://github.com/Azure/autorest.python/issues/2619 is fixed,
    # and you see the equivalent auto-generated method in _client.py return "Self"
    def __enter__(self) -> Self:
        self._client.__enter__()
        return self


class ImageEmbeddingsClient(ImageEmbeddingsClientGenerated):
    """ImageEmbeddingsClient.

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
    """

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, "TokenCredential"], **kwargs: Any) -> None:
        self._model_info: Optional[_models.ModelInfo] = None
        super().__init__(endpoint, credential, **kwargs)

    @overload
    def embed(
        self,
        *,
        model_extras: Optional[Dict[str, Any]] = None,
        input: List[_models.EmbeddingInput],
        content_type: str = "application/json",
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        **kwargs: Any,
    ) -> _models.EmbeddingsResult:
        """Return the embedding vectors for given images.
        The method makes a REST API call to the `/images/embeddings` route on the given endpoint.

        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``unknown-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
        :keyword input: Input image to embed. To embed multiple inputs in a single request, pass an
         array.
         The input must not exceed the max input tokens for the model. Required.
        :paramtype input: list[~azure.ai.inference.models.EmbeddingInput]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
         have.
         Passing null causes the model to use its default value.
         Returns a 422 error if the model doesn't support the value or parameter. Default value is
         None.
        :paramtype dimensions: int
        :keyword encoding_format: Optional. The desired format for the returned embeddings.
         Known values are:
         "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
        :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
        :keyword input_type: Optional. The type of the input.
         Returns a 422 error if the model doesn't support the value or parameter. Known values are:
         "text", "query", and "document". Default value is None.
        :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError
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
        :raises ~azure.core.exceptions.HttpResponseError
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
        :raises ~azure.core.exceptions.HttpResponseError
        """

    @distributed_trace
    def embed(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        model_extras: Optional[Dict[str, Any]] = None,
        input: List[_models.EmbeddingInput] = _Unset,
        dimensions: Optional[int] = None,
        encoding_format: Optional[Union[str, _models.EmbeddingEncodingFormat]] = None,
        input_type: Optional[Union[str, _models.EmbeddingInputType]] = None,
        **kwargs: Any,
    ) -> _models.EmbeddingsResult:
        # pylint: disable=line-too-long
        """Return the embedding vectors for given images.
        The method makes a REST API call to the `/images/embeddings` route on the given endpoint.

        :param body: Is either a MutableMapping[str, Any] type (like a dictionary) or a IO[bytes] type
         that specifies the full request payload. Required.
        :type body: JSON or IO[bytes]
        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``unknown-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
        :keyword input: Input image to embed. To embed multiple inputs in a single request, pass an
         array.
         The input must not exceed the max input tokens for the model. Required.
        :paramtype input: list[~azure.ai.inference.models.EmbeddingInput]
        :keyword dimensions: Optional. The number of dimensions the resulting output embeddings should
         have.
         Passing null causes the model to use its default value.
         Returns a 422 error if the model doesn't support the value or parameter. Default value is
         None.
        :paramtype dimensions: int
        :keyword encoding_format: Optional. The desired format for the returned embeddings.
         Known values are:
         "base64", "binary", "float", "int8", "ubinary", and "uint8". Default value is None.
        :paramtype encoding_format: str or ~azure.ai.inference.models.EmbeddingEncodingFormat
        :keyword input_type: Optional. The type of the input.
         Returns a 422 error if the model doesn't support the value or parameter. Known values are:
         "text", "query", and "document". Default value is None.
        :paramtype input_type: str or ~azure.ai.inference.models.EmbeddingInputType
        :return: EmbeddingsResult. The EmbeddingsResult is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.EmbeddingsResult
        :raises ~azure.core.exceptions.HttpResponseError
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
        _unknown_params: Union[_models._enums.UnknownParams, None] = None

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
            if model_extras is not None and bool(model_extras):
                body.update(model_extras)
                _unknown_params = _models._enums.UnknownParams.PASS_THROUGH  # pylint: disable=protected-access
            body = {k: v for k, v in body.items() if v is not None}
        content_type = content_type or "application/json"
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_image_embeddings_embed_request(
            unknown_params=_unknown_params,
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
            deserialized = _deserialize(_models.EmbeddingsResult, response.json())

        return deserialized  # type: ignore

    @distributed_trace
    def get_model_info(self, **kwargs: Any) -> _models.ModelInfo:
        # pylint: disable=line-too-long
        """Returns information about the AI model.

        :return: ModelInfo. The ModelInfo is compatible with MutableMapping
        :rtype: ~azure.ai.inference.models.ModelInfo
        :raises ~azure.core.exceptions.HttpResponseError
        """
        if not self._model_info:
            self._model_info = self._get_model_info(**kwargs)  # pylint: disable=attribute-defined-outside-init
        return self._model_info

    def __str__(self) -> str:
        # pylint: disable=client-method-name-no-double-underscore
        return super().__str__() + f"\n{self._model_info}" if self._model_info else super().__str__()

    # Remove this once https://github.com/Azure/autorest.python/issues/2619 is fixed,
    # and you see the equivalent auto-generated method in _client.py return "Self"
    def __enter__(self) -> Self:
        self._client.__enter__()
        return self


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
