# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import asyncio
import base64
import inspect
import json
import logging
import queue
import re
import sys

from typing import List, AsyncIterator, Iterator, Optional, Union, Any, Callable, Dict, Iterable
from azure.core.rest import HttpResponse, AsyncHttpResponse
from ._models import ImageUrl as ImageUrlGenerated
from ._models import ChatCompletions as ChatCompletionsGenerated
from ._models import ChatCompletionsToolDefinition as ChatCompletionsToolDefinitionGenerated
from ._models import EmbeddingsResult as EmbeddingsResultGenerated
from .. import models as _models

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

logger = logging.getLogger(__name__)

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_TOOLS_FUNCTION_ARG_TYPE_MAP = {str: "string", bool: "boolean", int: "integer", float: "number"}

def _make_tools_function_parameters_properties_schema(args: inspect.FullArgSpec, key: str) -> JSON:
   """
   This function returns a dictionary that represents the JSON
   that can be assigned to the "tools->function->parameters->properties" 
   element in a chat completions request body.
   All function arguments must be annotated according to https://peps.python.org/pep-0727/.
   Only "int", "float", "bool" and "str" input argument types are supported.

   Args:
      args (inspect.FullArgSpe): The function arguments
      key (str): The function argument name
      A Python function. Each function

   Returns:
      dict: A Dictionary that should be converted to JSON string and used in chat
      completions request body.
   """
   # See https://docs.python.org/3/howto/annotations.html
   # TODO: Test on Python 3.8
   ann = getattr(args, 'annotations', None)
   if ann == None:
      ann = getattr(args, '__annotations__', None)
   if ann == None:
      raise Exception("Missing annotations for function arguments")

   if key in ann:
      if ann[key].__origin__ not in _TOOLS_FUNCTION_ARG_TYPE_MAP:
         raise TypeError(f"Function arguments in tool definitions can only be `str`, `bool`, `int` or `float`. Type `{ann[key].__origin__}` is not supported")
      # TODO: Test all options here... e.g. missing Doc(), empty doc string, and raise appropriate exception
      if not ann[key].__metadata__[0].documentation:
         raise Exception(f"Missing the documentation annotation on for function argument `{key}`")
      return {
         "type": _TOOLS_FUNCTION_ARG_TYPE_MAP[ann[key].__origin__],
         "description": ann[key].__metadata__[0].documentation
      }
   else:
      raise Exception(f"Missing annotation for function argument `{key}` in tool defintion")


def _make_tools_function_schema(func: Callable[..., Any]) -> JSON:
   """
   This function returns a dictionary that represents the JSON
   that can be assigned to the "tools->function" element in a chat completions
   request body.
   See: https://learn.microsoft.com/azure/ai-studio/reference/reference-model-inference-chat-completions#functionobject

   Args:
      func (Callable[]): A Python function. Each function
      must have a description using docstring, and function arguments
      must all be annotated according to https://peps.python.org/pep-0727/.
      Only "int", "float", "bool" and "str" input argument types are supported.

   Returns:
      dict: A Dictionary that when converted to JSON, represents the "tools.function"
      payload in a chat completions request.
   """
   argspec = inspect.getfullargspec(func)
   if argspec.varargs or argspec.varkw:
      raise ValueError("I cannot create a schema for a function with *args or **kwargs")
   args = [arg for arg in argspec.args + argspec.kwonlyargs]
   defaults = (argspec.kwonlydefaults or {}).copy()
   defaults.update(
      dict(zip(argspec.args[-len(argspec.defaults or []) :], argspec.defaults or []))
   )
   parameters_schema = {
      "type": "object",
      "properties": {argname: _make_tools_function_parameters_properties_schema(argspec, argname) for argname in args},
      "required": [arg for arg in args if not arg in defaults],
   }
   function_schema = {"name": func.__name__}
   if func.__doc__:
      function_schema["description"] = func.__doc__
   elif hasattr(func, "_class__") and func.__class__.__doc__:
      function_schema["description"] = func.__class__.__doc__
   function_schema["parameters"] = parameters_schema
   return function_schema


def _make_tool_schema(func: Callable[..., Any]) -> JSON:
   """
   This function returns a dictionary that represents the JSON of a single element 
   in the "tools" array in a chat completions request body.
   See: https://learn.microsoft.com/azure/ai-studio/reference/reference-model-inference-chat-completions#chatcompletiontool

   Args:
      func (typing.Callable[]): A Python functions used as the tool. The function
      must have a general function description using docstring, and function arguments
      must all be annotated according to https://peps.python.org/pep-0727/.
      Only "int", "float", "bool" and "str" input argument types are supported.

   Returns:
      dict: A Dictionary that when converted to JSON, represents a single element in the
      "tools" array in a chat completions request payload.
   """
   return {
      "type": "function",
      "function": _make_tools_function_schema(func)
    }

class ChatCompletionsToolDefinition(ChatCompletionsToolDefinitionGenerated):
    @classmethod
    def load(cls, func: Callable[..., Any]) -> Self:
        """
        TODO
        """
        return cls(_make_tool_schema(func))

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

        :ivar image_file: The name of the local image file to load. Required.
        :vartype image_file: str
        :ivar image_format: The MIME type format of the image. For example: "jpeg", "png". Required.
        :vartype image_format: str
        :ivar detail: The evaluation quality setting to use, which controls relative prioritization of
         speed, token consumption, and accuracy. Known values are: "auto", "low", and "high".
        :vartype detail: str or ~azure.ai.inference.models.ImageDetailLevel
        :return: An ImageUrl object with the image data encoded as a base64 string.
        :rtype: ~azure.ai.inference.models.ImageUrl
        :raises FileNotFoundError: when the image file could not be opened.
        """
        with open(image_file, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        url = f"data:image/{image_format};base64,{image_data}"
        return cls(url=url, detail=detail)


class BaseStreamingChatCompletions:
    """A base class for the sync and async streaming chat completions responses, holding any common code
    to deserializes the Server Sent Events (SSE) response stream into chat completions updates, each one
    represented by a StreamingChatCompletionsUpdate object.
    """

    # Enable detailed logs of SSE parsing. For development only, should be `False` by default.
    _ENABLE_CLASS_LOGS = False

    # The prefix of each line in the SSE stream that contains a JSON string
    # to deserialize into a StreamingChatCompletionsUpdate object
    _SSE_DATA_EVENT_PREFIX = "data: "

    # The line indicating the end of the SSE stream
    _SSE_DATA_EVENT_DONE = "data: [DONE]"

    def __init__(self):
        self._queue: "queue.Queue[_models.StreamingChatCompletionsUpdate]" = queue.Queue()
        self._incomplete_json = ""
        self._done = False  # Will be set to True when reading 'data: [DONE]' line

    def _deserialize_and_add_to_queue(self, element: bytes) -> bool:

        # Clear the queue of StreamingChatCompletionsUpdate before processing the next block
        self._queue.queue.clear()

        # Convert `bytes` to string and split the string by newline, while keeping the new line char.
        # the last may be a partial "line" that does not contain a newline char at the end.
        line_list: List[str] = re.split(r"(?<=\n)", element.decode("utf-8"))
        for index, line in enumerate(line_list):

            if self._ENABLE_CLASS_LOGS:
                logger.debug("[Original line] %s", repr(line))

            if index == 0:
                line = self._incomplete_json + line
                self._incomplete_json = ""

            if index == len(line_list) - 1 and not line.endswith("\n"):
                self._incomplete_json = line
                return False

            if self._ENABLE_CLASS_LOGS:
                logger.debug("[Modified line] %s", repr(line))

            if line == "\n":  # Empty line, indicating flush output to client
                continue

            if not line.startswith(self._SSE_DATA_EVENT_PREFIX):
                raise ValueError(f"SSE event not supported (line `{line}`)")

            if line.startswith(self._SSE_DATA_EVENT_DONE):
                if self._ENABLE_CLASS_LOGS:
                    logger.debug("[Done]")
                return True

            # If you reached here, the line should contain `data: {...}\n`
            # where the curly braces contain a valid JSON object.
            # Deserialize it into a StreamingChatCompletionsUpdate object
            # and add it to the queue.
            # pylint: disable=W0212 # Access to a protected member _deserialize of a client class
            update = _models.StreamingChatCompletionsUpdate._deserialize(
                json.loads(line[len(self._SSE_DATA_EVENT_PREFIX) : -1]), []
            )

            # We skip any update that has a None or empty choices list
            # (this is what OpenAI Python SDK does)
            if update.choices:

                # We update all empty content strings to None
                # (this is what OpenAI Python SDK does)
                # for choice in update.choices:
                #    if not choice.delta.content:
                #        choice.delta.content = None

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

    def __iter__(self):
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

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
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

    def __aiter__(self):
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

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        asyncio.run(self.aclose())

    async def aclose(self) -> None:
        await self._response.close()


__all__: List[str] = [
    "ImageUrl",
    "ChatCompletions",
    "ChatCompletionsToolDefinition",
    "EmbeddingsResult",
    "StreamingChatCompletions",
    "AsyncStreamingChatCompletions",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
