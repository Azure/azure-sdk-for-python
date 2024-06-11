# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import asyncio
import json
import logging
import queue
import re

from typing import List, AsyncIterator, Iterator
from azure.core.rest import HttpResponse, AsyncHttpResponse
from .. import models as _models

logger = logging.getLogger(__name__)


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
            self._queue.put(
                # pylint: disable=W0212 # Access to a protected member _deserialize of a client class
                _models.StreamingChatCompletionsUpdate._deserialize(
                    json.loads(line[len(self._SSE_DATA_EVENT_PREFIX) : -1]), []
                )
            )

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

    def __next__(self) -> _models.StreamingChatCompletionsUpdate:
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

    async def __anext__(self) -> _models.StreamingChatCompletionsUpdate:
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
    "StreamingChatCompletions",
    "AsyncStreamingChatCompletions",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
