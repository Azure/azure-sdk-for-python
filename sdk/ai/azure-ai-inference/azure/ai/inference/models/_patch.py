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

from typing import List
from .. import models as _models
from azure.core.rest import HttpResponse

class ChatCompletionsDeltaInterator:
    """Representation of the streaming response chat completions request.
    Completions support a wide variety of tasks and generate text that continues from or
    "completes"
    provided prompt data.
    """


    # Enable console logs for debugging
    ENABLE_CLASS_LOGS = False

    # The prefix of each line in the SSE stream that contains a JSON string 
    # to deserialize into a ChatCompletionsDelta object
    SSE_DATA_EVENT_PREFIX = "data: "

    # The line indicating the end of the SSE stream
    SSE_DATA_EVENT_DONE = "data: [DONE]"

    def __init__(self, response: HttpResponse):
        self._response = response
        self._bytes_iterator = response.iter_bytes()
        self._queue = queue.Queue()
        self._incomplete_json = ""
        self._done = False

    def __iter__(self):
        return self

    def __next__(self):
        if self._queue.empty():
            self._read_next_block()
        if self._queue.empty():
            raise StopIteration
        return self._queue.get()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._response.close()

    def close(self):
        self._response.close()

    def __del__(self):
        self._response.close()

    def _read_next_block(self):

        if self.ENABLE_CLASS_LOGS:
            start_time = time.time()

        try:
            element = next(self._bytes_iterator)
        except StopIteration:
            self._done = True
            return

        if self.ENABLE_CLASS_LOGS:
            print(f"Elapsed time: {int(1000*(time.time()- start_time))}ms")
            print(f"Size: {len(element)} bytes")

        # Clear the queue of ChatCompletionsDelta before processing the next block
        self._queue.queue.clear()

        # Convert `bytes` to string and split the string by newline, while keeping the new line char.
        # the last may be a partial "line" that does not contain a newline char at the end.
        line_list = re.split(r'(?<=\n)', element.decode('utf-8'))
        for index, element in enumerate(line_list):

            if self.ENABLE_CLASS_LOGS:
                print(f"[original] {repr(element)}")

            if index == 0:
                element = self._incomplete_json + element
                self._incomplete_json = ""

            if index == len(line_list) - 1 and not element.endswith("\n"):
                self._incomplete_json  = element
                return

            if self.ENABLE_CLASS_LOGS:
                print(f"[modified] {repr(element)}")

            if element == "\n": # Empty line, indicating flush output to client
                continue

            if not element.startswith(self.SSE_DATA_EVENT_PREFIX):
                    raise ValueError(f"SSE event not supported (line `{element}`)")

            if element.startswith(self.SSE_DATA_EVENT_DONE):
                self._done = True
                return

            # If you reached here, the line should contain `data: {...}\n`
            # where the curly braces contain a valid JSON object. Deserialize it into a ChatCompletionsDelta object
            # and add it to the queue.
            self._queue.put(_models.ChatCompletionsDelta._deserialize(json.loads(element[len(self.SSE_DATA_EVENT_PREFIX):-1]), []))

            if self.ENABLE_CLASS_LOGS:
                print("[added]")


__all__: List[str] = ["ChatCompletionsDeltaInterator"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
