# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import base64
import json
import logging
import queue
import re
import sys

from typing import Mapping, Literal, Any, List, AsyncIterator, Iterator, Optional, Union, overload
from azure.core.rest import HttpResponse, AsyncHttpResponse
from ._enums import ChatRole
from .._model_base import rest_discriminator, rest_field
from ._models import ChatRequestMessage
from ._models import ImageUrl as ImageUrlGenerated
from ._models import ChatCompletions as ChatCompletionsGenerated
from ._models import EmbeddingsResult as EmbeddingsResultGenerated
from ._models import ImageEmbeddingInput as EmbeddingInputGenerated
from ._models import InputAudio as InputAudioGenerated
from .. import models as _models

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

logger = logging.getLogger(__name__)


class UserMessage(ChatRequestMessage, discriminator="user"):
    """A request chat message representing user input to the assistant.

    :ivar role: The chat role associated with this message, which is always 'user' for user
     messages. Required. The role that provides input for chat completions.
    :vartype role: str or ~azure.ai.inference.models.USER
    :ivar content: The contents of the user message, with available input types varying by selected
     model. Required. Is either a str type or a [ContentItem] type.
    :vartype content: str or list[~azure.ai.inference.models.ContentItem]
    """

    role: Literal[ChatRole.USER] = rest_discriminator(name="role")  # type: ignore
    """The chat role associated with this message, which is always 'user' for user messages. Required.
     The role that provides input for chat completions."""
    content: Union["str", List["_models.ContentItem"]] = rest_field()
    """The contents of the user message, with available input types varying by selected model.
     Required. Is either a str type or a [ContentItem] type."""

    @overload
    def __init__(
        self,
        content: Union[str, List["_models.ContentItem"]],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1 and isinstance(args[0], (List, str)):
            if kwargs.get("content") is not None:
                raise ValueError("content cannot be provided as positional and keyword arguments")
            kwargs["content"] = args[0]
            args = tuple()
        super().__init__(*args, role=ChatRole.USER, **kwargs)


class SystemMessage(ChatRequestMessage, discriminator="system"):
    """A request chat message containing system instructions that influence how the model will
    generate a chat completions response.

    :ivar role: The chat role associated with this message, which is always 'system' for system
     messages. Required.
    :vartype role: str or ~azure.ai.inference.models.SYSTEM
    :ivar content: The contents of the system message. Required.
    :vartype content: str
    """

    role: Literal[ChatRole.SYSTEM] = rest_discriminator(name="role")  # type: ignore
    """The chat role associated with this message, which is always 'system' for system messages.
     Required."""
    content: str = rest_field()
    """The contents of the system message. Required."""

    @overload
    def __init__(
        self,
        content: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1 and isinstance(args[0], str):
            if kwargs.get("content") is not None:
                raise ValueError("content cannot be provided as positional and keyword arguments")
            kwargs["content"] = args[0]
            args = tuple()
        super().__init__(*args, role=ChatRole.SYSTEM, **kwargs)


class DeveloperMessage(ChatRequestMessage, discriminator="developer"):
    """A request chat message containing developer instructions that influence how the model will
    generate a chat completions response. Some AI models support developer messages instead
    of system messages.

    :ivar role: The chat role associated with this message, which is always 'developer' for developer
     messages. Required.
    :vartype role: str or ~azure.ai.inference.models.DEVELOPER
    :ivar content: The contents of the developer message. Required.
    :vartype content: str
    """

    role: Literal[ChatRole.DEVELOPER] = rest_discriminator(name="role")  # type: ignore
    """The chat role associated with this message, which is always 'developer' for developer messages.
     Required."""
    content: str = rest_field()
    """The contents of the developer message. Required."""

    @overload
    def __init__(
        self,
        content: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1 and isinstance(args[0], str):
            if kwargs.get("content") is not None:
                raise ValueError("content cannot be provided as positional and keyword arguments")
            kwargs["content"] = args[0]
            args = tuple()
        super().__init__(*args, role=ChatRole.DEVELOPER, **kwargs)


class AssistantMessage(ChatRequestMessage, discriminator="assistant"):
    """A request chat message representing response or action from the assistant.

    :ivar role: The chat role associated with this message, which is always 'assistant' for
     assistant messages. Required. The role that provides responses to system-instructed,
     user-prompted input.
    :vartype role: str or ~azure.ai.inference.models.ASSISTANT
    :ivar content: The content of the message.
    :vartype content: str
    :ivar tool_calls: The tool calls that must be resolved and have their outputs appended to
     subsequent input messages for the chat
     completions request to resolve as configured.
    :vartype tool_calls: list[~azure.ai.inference.models.ChatCompletionsToolCall]
    """

    role: Literal[ChatRole.ASSISTANT] = rest_discriminator(name="role")  # type: ignore
    """The chat role associated with this message, which is always 'assistant' for assistant messages.
     Required. The role that provides responses to system-instructed, user-prompted input."""
    content: Optional[str] = rest_field()
    """The content of the message."""
    tool_calls: Optional[List["_models.ChatCompletionsToolCall"]] = rest_field()
    """The tool calls that must be resolved and have their outputs appended to subsequent input
     messages for the chat
     completions request to resolve as configured."""

    @overload
    def __init__(
        self,
        content: Optional[str] = None,
        *,
        tool_calls: Optional[List["_models.ChatCompletionsToolCall"]] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1 and isinstance(args[0], str):
            if kwargs.get("content") is not None:
                raise ValueError("content cannot be provided as positional and keyword arguments")
            kwargs["content"] = args[0]
            args = tuple()
        super().__init__(*args, role=ChatRole.ASSISTANT, **kwargs)


class ToolMessage(ChatRequestMessage, discriminator="tool"):
    """A request chat message representing requested output from a configured tool.

    :ivar role: The chat role associated with this message, which is always 'tool' for tool
     messages. Required. The role that represents extension tool activity within a chat completions
     operation.
    :vartype role: str or ~azure.ai.inference.models.TOOL
    :ivar content: The content of the message.
    :vartype content: str
    :ivar tool_call_id: The ID of the tool call resolved by the provided content. Required.
    :vartype tool_call_id: str
    """

    role: Literal[ChatRole.TOOL] = rest_discriminator(name="role")  # type: ignore
    """The chat role associated with this message, which is always 'tool' for tool messages. Required.
     The role that represents extension tool activity within a chat completions operation."""
    content: Optional[str] = rest_field()
    """The content of the message."""
    tool_call_id: str = rest_field()
    """The ID of the tool call resolved by the provided content. Required."""

    @overload
    def __init__(
        self,
        content: Optional[str] = None,
        *,
        tool_call_id: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1 and isinstance(args[0], str):
            if kwargs.get("content") is not None:
                raise ValueError("content cannot be provided as positional and keyword arguments")
            kwargs["content"] = args[0]
            args = tuple()
        super().__init__(*args, role=ChatRole.TOOL, **kwargs)


class ChatCompletions(ChatCompletionsGenerated):
    """Representation of the response data from a chat completions request.
    Completions support a wide variety of tasks and generate text that continues from or
    "completes"
    provided prompt data.


    :ivar id: A unique identifier associated with this chat completions response. Required.
    :vartype id: str
    :ivar created: The first timestamp associated with generation activity for this completions
     response,
     represented as seconds since the beginning of the Unix epoch of 00:00 on 1 Jan 1970. Required.
    :vartype created: ~datetime.datetime
    :ivar model: The model used for the chat completion. Required.
    :vartype model: str
    :ivar usage: Usage information for tokens processed and generated as part of this completions
     operation. Required.
    :vartype usage: ~azure.ai.inference.models.CompletionsUsage
    :ivar choices: The collection of completions choices associated with this completions response.
     Generally, ``n`` choices are generated per provided prompt with a default value of 1.
     Token limits and other settings may limit the number of choices generated. Required.
    :vartype choices: list[~azure.ai.inference.models.ChatChoice]
    """

    def __str__(self) -> str:
        # pylint: disable=client-method-name-no-double-underscore
        return json.dumps(self.as_dict(), indent=2)


class EmbeddingsResult(EmbeddingsResultGenerated):
    """Representation of the response data from an embeddings request.
    Embeddings measure the relatedness of text strings and are commonly used for search,
    clustering,
    recommendations, and other similar scenarios.


    :ivar data: Embedding values for the prompts submitted in the request. Required.
    :vartype data: list[~azure.ai.inference.models.EmbeddingItem]
    :ivar usage: Usage counts for tokens input using the embeddings API. Required.
    :vartype usage: ~azure.ai.inference.models.EmbeddingsUsage
    :ivar model: The model ID used to generate this result. Required.
    :vartype model: str
    """

    def __str__(self) -> str:
        # pylint: disable=client-method-name-no-double-underscore
        return json.dumps(self.as_dict(), indent=2)


class ImageUrl(ImageUrlGenerated):

    @classmethod
    def load(
        cls, *, image_file: str, image_format: str, detail: Optional[Union[str, "_models.ImageDetailLevel"]] = None
    ) -> Self:
        """
        Create an ImageUrl object from a local image file. The method reads the image
        file and encodes it as a base64 string, which together with the image format
        is then used to format the JSON `url` value passed in the request payload.

        :keyword image_file: The name of the local image file to load. Required.
        :paramtype image_file: str
        :keyword image_format: The MIME type format of the image. For example: "jpeg", "png". Required.
        :paramtype image_format: str
        :keyword detail: The evaluation quality setting to use, which controls relative prioritization of
         speed, token consumption, and accuracy. Known values are: "auto", "low", and "high".
        :paramtype detail: str or ~azure.ai.inference.models.ImageDetailLevel
        :return: An ImageUrl object with the image data encoded as a base64 string.
        :rtype: ~azure.ai.inference.models.ImageUrl
        :raises FileNotFoundError: when the image file could not be opened.
        """
        with open(image_file, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        url = f"data:image/{image_format};base64,{image_data}"
        return cls(url=url, detail=detail)


class ImageEmbeddingInput(EmbeddingInputGenerated):

    @classmethod
    def load(cls, *, image_file: str, image_format: str, text: Optional[str] = None) -> Self:
        """
        Create an ImageEmbeddingInput object from a local image file. The method reads the image
        file and encodes it as a base64 string, which together with the image format
        is then used to format the JSON `url` value passed in the request payload.

        :keyword image_file: The name of the local image file to load. Required.
        :paramtype image_file: str
        :keyword image_format: The MIME type format of the image. For example: "jpeg", "png". Required.
        :paramtype image_format: str
        :keyword text: Optional. The text input to feed into the model (like DINO, CLIP).
         Returns a 422 error if the model doesn't support the value or parameter.
        :paramtype text: str
        :return: An ImageEmbeddingInput object with the image data encoded as a base64 string.
        :rtype: ~azure.ai.inference.models.EmbeddingsInput
        :raises FileNotFoundError: when the image file could not be opened.
        """
        with open(image_file, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        image_uri = f"data:image/{image_format};base64,{image_data}"
        return cls(image=image_uri, text=text)


class BaseStreamingChatCompletions:
    """A base class for the sync and async streaming chat completions responses, holding any common code
    to deserializes the Server Sent Events (SSE) response stream into chat completions updates, each one
    represented by a StreamingChatCompletionsUpdate object.
    """

    # Enable detailed logs of SSE parsing. For development only, should be `False` by default.
    _ENABLE_CLASS_LOGS = False

    # The prefix of each line in the SSE stream that contains a JSON string
    # to deserialize into a StreamingChatCompletionsUpdate object
    _SSE_DATA_EVENT_PREFIX = b"data: "

    # The line indicating the end of the SSE stream
    _SSE_DATA_EVENT_DONE = b"data: [DONE]"

    def __init__(self):
        self._queue: "queue.Queue[_models.StreamingChatCompletionsUpdate]" = queue.Queue()
        self._incomplete_line = b""
        self._done = False  # Will be set to True when reading 'data: [DONE]' line

    # See https://html.spec.whatwg.org/multipage/server-sent-events.html#parsing-an-event-stream
    def _deserialize_and_add_to_queue(self, element: bytes) -> bool:

        if self._ENABLE_CLASS_LOGS:
            logger.debug("[Original element] %s", repr(element))

        # Clear the queue of StreamingChatCompletionsUpdate before processing the next block
        self._queue.queue.clear()

        # Split the single input bytes object at new line characters, and get a list of bytes objects, each
        # representing a single "line". The bytes object at the end of the list may be a partial "line" that
        # does not contain a new line character at the end.
        # Note 1: DO NOT try to use something like this here:
        #   line_list: List[str] = re.split(r"(?<=\n)", element.decode("utf-8"))
        #   to do full UTF8 decoding of the whole input bytes object, as the last line in the list may be partial, and
        #   as such may contain a partial UTF8 Chinese character (for example). `decode("utf-8")` will raise an
        #   exception for such a case. See GitHub issue https://github.com/Azure/azure-sdk-for-python/issues/39565
        # Note 2: Consider future re-write and simplifications of this code by using:
        #   `codecs.getincrementaldecoder("utf-8")`
        line_list: List[bytes] = re.split(re.compile(b"(?<=\n)"), element)
        for index, line in enumerate(line_list):

            if self._ENABLE_CLASS_LOGS:
                logger.debug("[Original line] %s", repr(line))

            if index == 0:
                line = self._incomplete_line + line
                self._incomplete_line = b""

            if index == len(line_list) - 1 and not line.endswith(b"\n"):
                self._incomplete_line = line
                return False

            if self._ENABLE_CLASS_LOGS:
                logger.debug("[Modified line] %s", repr(line))

            if line == b"\n":  # Empty line, indicating flush output to client
                continue

            if not line.startswith(self._SSE_DATA_EVENT_PREFIX):
                raise ValueError(f"SSE event not supported (line `{repr(line)}`)")

            if line.startswith(self._SSE_DATA_EVENT_DONE):
                if self._ENABLE_CLASS_LOGS:
                    logger.debug("[Done]")
                return True

            # If you reached here, the line should contain `data: {...}\n`
            # where the curly braces contain a valid JSON object.
            # It is now safe to do UTF8 decoding of the line.
            line_str = line.decode("utf-8")

            # Deserialize it into a StreamingChatCompletionsUpdate object
            # and add it to the queue.
            # pylint: disable=W0212 # Access to a protected member _deserialize of a client class
            update = _models.StreamingChatCompletionsUpdate._deserialize(
                json.loads(line_str[len(self._SSE_DATA_EVENT_PREFIX) : -1]), []
            )

            # We skip any update that has a None or empty choices list, and does not have token usage info.
            # (this is what OpenAI Python SDK does)
            if update.choices or update.usage:
                self._queue.put(update)

            if self._ENABLE_CLASS_LOGS:
                logger.debug("[Added to queue]")

        return False


class StreamingChatCompletions(BaseStreamingChatCompletions):
    """Represents an interator over StreamingChatCompletionsUpdate objects. It can be used for either synchronous or
    asynchronous iterations. The class deserializes the Server Sent Events (SSE) response stream
    into chat completions updates, each one represented by a StreamingChatCompletionsUpdate object.
    """

    def __init__(self, response: HttpResponse):
        super().__init__()
        self._response = response
        self._bytes_iterator: Iterator[bytes] = response.iter_bytes()

    def __iter__(self) -> Any:
        return self

    def __next__(self) -> "_models.StreamingChatCompletionsUpdate":
        while self._queue.empty() and not self._done:
            self._done = self._read_next_block()
        if self._queue.empty():
            raise StopIteration
        return self._queue.get()

    def _read_next_block(self) -> bool:
        if self._ENABLE_CLASS_LOGS:
            logger.debug("[Reading next block]")
        try:
            element = self._bytes_iterator.__next__()
        except StopIteration:
            self.close()
            return True
        return self._deserialize_and_add_to_queue(element)

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:  # type: ignore
        self.close()

    def close(self) -> None:
        self._response.close()


class AsyncStreamingChatCompletions(BaseStreamingChatCompletions):
    """Represents an async interator over StreamingChatCompletionsUpdate objects.
    It can be used for either synchronous or asynchronous iterations. The class
    deserializes the Server Sent Events (SSE) response stream into chat
    completions updates, each one represented by a StreamingChatCompletionsUpdate object.
    """

    def __init__(self, response: AsyncHttpResponse):
        super().__init__()
        self._response = response
        self._bytes_iterator: AsyncIterator[bytes] = response.iter_bytes()

    def __aiter__(self) -> Any:
        return self

    async def __anext__(self) -> "_models.StreamingChatCompletionsUpdate":
        while self._queue.empty() and not self._done:
            self._done = await self._read_next_block_async()
        if self._queue.empty():
            raise StopAsyncIteration
        return self._queue.get()

    async def _read_next_block_async(self) -> bool:
        if self._ENABLE_CLASS_LOGS:
            logger.debug("[Reading next block]")
        try:
            element = await self._bytes_iterator.__anext__()
        except StopAsyncIteration:
            await self.aclose()
            return True
        return self._deserialize_and_add_to_queue(element)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:  # type: ignore
        await self.aclose()

    async def aclose(self) -> None:
        await self._response.close()


class InputAudio(InputAudioGenerated):

    @classmethod
    def load(
        cls,
        *,
        audio_file: str,
        audio_format: str,
    ) -> Self:
        """
        Create an InputAudio object from a local audio file. The method reads the audio
        file and encodes it as a base64 string, which together with the audio format
        is then used to create the InputAudio object passed to the request payload.

        :keyword audio_file: The name of the local audio file to load. Required.
        :vartype audio_file: str
        :keyword audio_format: The MIME type format of the audio. For example: "wav", "mp3". Required.
        :vartype audio_format: str
        :return: An InputAudio object with the audio data encoded as a base64 string.
        :rtype: ~azure.ai.inference.models.InputAudio
        :raises FileNotFoundError: when the image file could not be opened.
        """
        with open(audio_file, "rb") as f:
            audio_data = base64.b64encode(f.read()).decode("utf-8")
        return cls(data=audio_data, format=audio_format)


__all__: List[str] = [
    "AssistantMessage",
    "AsyncStreamingChatCompletions",
    "ChatCompletions",
    "ChatRequestMessage",
    "EmbeddingsResult",
    "ImageEmbeddingInput",
    "ImageUrl",
    "InputAudio",
    "StreamingChatCompletions",
    "SystemMessage",
    "ToolMessage",
    "UserMessage",
    "DeveloperMessage",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
