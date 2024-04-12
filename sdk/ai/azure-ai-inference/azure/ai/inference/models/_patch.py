# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import queue
import time
import re
import json
import types

from typing import List, Union
from .. import models as _models
from azure.core.rest import HttpResponse


class StreamingChatCompletions:
    """Represents an interator over ChatCompletionsUpdate objects. It can be used for either synchronous or
    asynchronous iterations. The class deserializes the Server Sent Events (SSE) response stream
    into chat completions updates, each one represented by a ChatCompletionsUpdate object.
    """

    # Enable console logs for debugging. For development only, will be removed before release.
    ENABLE_CLASS_LOGS = False

    # The prefix of each line in the SSE stream that contains a JSON string
    # to deserialize into a ChatCompletionsUpdate object
    SSE_DATA_EVENT_PREFIX = "data: "

    # The line indicating the end of the SSE stream
    SSE_DATA_EVENT_DONE = "data: [DONE]"

    def __init__(self, bytes_iterator: Union[types.AsyncGeneratorType, types.GeneratorType]):
        self._bytes_iterator = bytes_iterator
        self._is_async_iterator = isinstance(self._bytes_iterator, types.AsyncGeneratorType)
        self._queue = queue.Queue()
        self._incomplete_json = ""
        self._done = False

    def __aiter__(self):
        if not self._is_async_iterator:
            raise ValueError("This method is only supported for async iterators")
        return self

    def __iter__(self):
        if self._is_async_iterator:
            raise ValueError("This method is not supported for async iterators")
        return self

    async def __anext__(self) -> _models.ChatCompletionsUpdate:
        if not self._is_async_iterator:
            raise ValueError("This method is only supported for async iterators")
        if self._queue.empty():
            await self._read_next_block_async()
        if self._queue.empty():
            await self.aclose()
            raise StopAsyncIteration
        return self._queue.get()

    def __next__(self) -> _models.ChatCompletionsUpdate:
        if self._is_async_iterator:
            raise ValueError("This method is not supported for async iterators")
        if self._queue.empty():
            self._read_next_block()
        if self._queue.empty():
            self.close()
            raise StopIteration
        return self._queue.get()

    async def _read_next_block_async(self):
        start_time = 0.0
        if self.ENABLE_CLASS_LOGS:
            start_time = time.time()
        try:
            element = await self._bytes_iterator.__anext__()
        except StopAsyncIteration:
            await self.aclose()
            self._done = True
            return
        self._deserialize_and_add_to_queue(element, start_time)

    def _read_next_block(self):
        start_time = 0.0
        if self.ENABLE_CLASS_LOGS:
            start_time = time.time()
        try:
            element = next(self._bytes_iterator)
        except StopIteration:
            self.close()
            self._done = True
            return
        self._deserialize_and_add_to_queue(element, start_time)

    def _deserialize_and_add_to_queue(self, element: bytes, start_time: float = 0.0):

        if self.ENABLE_CLASS_LOGS:
            print(f"Elapsed time: {int(1000*(time.time()- start_time))}ms")
            print(f"Size: {len(element)} bytes")

        # Clear the queue of ChatCompletionsUpdate before processing the next block
        self._queue.queue.clear()

        # Convert `bytes` to string and split the string by newline, while keeping the new line char.
        # the last may be a partial "line" that does not contain a newline char at the end.
        line_list = re.split(r"(?<=\n)", element.decode("utf-8"))
        for index, element in enumerate(line_list):

            if self.ENABLE_CLASS_LOGS:
                print(f"[original] {repr(element)}")

            if index == 0:
                element = self._incomplete_json + element
                self._incomplete_json = ""

            if index == len(line_list) - 1 and not element.endswith("\n"):
                self._incomplete_json = element
                return

            if self.ENABLE_CLASS_LOGS:
                print(f"[modified] {repr(element)}")

            if element == "\n":  # Empty line, indicating flush output to client
                continue

            if not element.startswith(self.SSE_DATA_EVENT_PREFIX):
                raise ValueError(f"SSE event not supported (line `{element}`)")

            if element.startswith(self.SSE_DATA_EVENT_DONE):
                self._done = True
                return

            # If you reached here, the line should contain `data: {...}\n`
            # where the curly braces contain a valid JSON object. Deserialize it into a ChatCompletionsUpdate object
            # and add it to the queue.
            self._queue.put(
                _models.ChatCompletionsUpdate._deserialize(json.loads(element[len(self.SSE_DATA_EVENT_PREFIX) : -1]), [])
            )

            if self.ENABLE_CLASS_LOGS:
                print("[added]")

    def __enter__(self):
        return self

    def __exit__(self) -> None:
        self.close()

    def close(self) -> None:
        self._bytes_iterator.close()

    async def aclose(self) -> None:
        await self._bytes_iterator.aclose()


__all__: List[str] = [
    "StreamingChatCompletions"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
