# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import AsyncIterable, AsyncContextManager, Callable, Awaitable
from typing_extensions import Self
import hashlib


class AsyncDownloadBlobStream(
    AsyncIterable[bytes],
    AsyncContextManager[Self],
):
    """Protocol for methods to provide streamed responses."""

    def __init__(self, **kwargs) -> None:
        self._response: AsyncIterable[bytes] = kwargs.get('response')
        self._next: Callable[[str], Awaitable[AsyncIterable[bytes]]] = kwargs.get('next')
        self._blob_size: int = kwargs.get('blob_size')
        self._downloaded: int = kwargs.get('downloaded')
        self._hasher = hashlib.sha256()
        self._digest: str = kwargs.get('digest')
        self._chunk_size: int = kwargs.get('chunk_size')

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    def __aiter__(self) -> Self:
        return self

    async def _yield_data(self) -> bytes:
        data = await anext(self._response)
        self._hasher.update(data)
        return data

    async def _download_chunk(self) -> AsyncIterable[bytes]:
        end_range = self._downloaded + self._chunk_size
        range_header = f"bytes={self._downloaded}-{end_range}"
        next_chunk, headers = await self._next(range=range_header)
        self._downloaded += headers["Content-Length"]
        return next_chunk

    async def __anext__(self) -> bytes:
        try:
            return await self._yield_data()
        except StopIteration:
            if self._downloaded >= self._blob_size:
                computed_digest = "sha256:" + self._hasher.hexdigest()
                if computed_digest != self._digest:
                    raise ValueError("The requested digest does not match the digest of the received blob.")
                raise
            self._response = await self._download_chunk()
            return await self._yield_data()

    async def close(self) -> None:
        # This is not currently supported in Core, and probably needs to be.
        # await self._response.close()
        pass
