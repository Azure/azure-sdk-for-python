# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import os
import logging
import sys
from pathlib import Path
from typing import Any, BinaryIO, List, Union

from jsonrpc.jsonrpc2 import JSONRPC20Request

from . import AutorestAPI, Channel


_LOGGER = logging.getLogger(__name__)


def read_message(stream: BinaryIO = sys.stdin.buffer) -> str:
    # Content-Length
    order = stream.readline().rstrip()

    if not order.startswith(b"Content-Length"):
        raise ValueError("I was expecting to see Content-Length")
    _LOGGER.debug("Received: %s", order)
    try:
        bytes_size = int(order.split(b":")[1].strip())
    except Exception as err:
        raise ValueError(f"Was unable to read length from {order!r}") from err
    # Double new line, so read another emptyline and ignore it
    stream.readline()

    # Read the right number of bytes
    _LOGGER.debug("Trying to read the message")
    message = stream.read(bytes_size)
    assert isinstance(message, bytes)
    message_str = message.decode("utf-8")
    _LOGGER.debug("Received a %d bytes message", len(message_str))
    # _LOGGER.debug("Read %s", message)

    return message_str


def write_message(message: str, stream: BinaryIO = sys.stdout.buffer) -> None:
    bytes_message = message.encode("utf-8")
    stream.write(b"Content-Length: ")
    stream.write(str(len(bytes_message)).encode("ascii"))
    stream.write(b"\r\n\r\n")
    stream.write(bytes_message)
    stream.flush()


class StdStreamAutorestAPI(AutorestAPI):
    """The stream API with Autorest"""

    def __init__(self, session_id: str) -> None:
        super().__init__()
        self.session_id = session_id

    def write_file(self, filename: Union[str, Path], file_content: str) -> None:
        _LOGGER.debug("Writing a file: %s", filename)
        filename = os.fspath(filename)
        request = JSONRPC20Request(
            method="WriteFile",
            params=[self.session_id, filename, file_content, None],  # sourceMap ?
            is_notification=True,
        )
        write_message(request.json)

    def read_file(self, filename: Union[str, Path]) -> str:
        _LOGGER.debug("Asking content for file %s", filename)
        filename = os.fspath(filename)
        request = JSONRPC20Request(
            method="ReadFile", params=[self.session_id, filename], _id=42
        )
        write_message(request.json)
        return json.loads(read_message())["result"]

    def list_inputs(self) -> List[str]:
        _LOGGER.debug("Calling list inputs to Autorest")
        request = JSONRPC20Request(
            method="ListInputs", params=[self.session_id, None], _id=42
        )
        write_message(request.json)
        return json.loads(read_message())["result"]

    def get_value(self, key: str) -> Any:
        _LOGGER.debug("Calling get value to Autorest: %s", key)
        request = JSONRPC20Request(
            method="GetValue", params=[self.session_id, key], _id=42
        )
        write_message(request.json)
        return json.loads(read_message())["result"]

    def message(self, channel: Channel, text: str) -> None:
        # https://github.com/Azure/autorest/blob/ad7f01ffe17aa74ad0075d6b1562a3fa78fd2e96/src/autorest-core/lib/message.ts#L53
        # Don't log anything here, or you will create a cycle with the autorest handler
        message = {
            "Channel": channel.value,
            "Text": text,
        }
        request = JSONRPC20Request(
            method="Message", params=[self.session_id, message], is_notification=True
        )
        write_message(request.json)
