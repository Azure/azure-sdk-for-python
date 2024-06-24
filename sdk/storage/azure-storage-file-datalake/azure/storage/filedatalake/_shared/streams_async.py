# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import annotations

import sys
from collections.abc import AsyncIterable
from io import IOBase


class AsyncIterStreamer(IOBase):
    """An async file-like wrapper over an async iterable."""
    def __init__(self, iterable: AsyncIterable[bytes], encoding: str = "UTF-8"):
        self.iterable = iterable
        self.iterator = iterable.__aiter__()
        self.leftover = b""
        self.encoding = encoding

    def __len__(self):
        # Not part of the ABC, but here in case the iterable also has a len
        return len(self.iterable)  # type: ignore

    def __aiter__(self):
        return self.iterator

    def __anext__(self):
        return self.iterator.__anext__()

    def readable(self):
        return True

    async def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = sys.maxsize
        data = self.leftover
        count = len(self.leftover)
        try:
            while count < size:
                chunk = await self.iterator.__anext__()
                if isinstance(chunk, str):
                    chunk = chunk.encode(self.encoding)
                data += chunk
                count += len(chunk)
        # This means count < size and what's leftover will be returned in this call.
        except StopAsyncIteration:
            self.leftover = b""

        if count >= size:
            self.leftover = data[size:]

        return data[:size]
