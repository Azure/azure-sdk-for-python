# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import hashlib
from typing import AsyncIterator, AsyncContextManager, Awaitable, TypeVar, cast, Tuple, Dict, Any
from typing_extensions import Protocol

T = TypeVar('T', bound='AsyncDownloadBlobStream')


class GetNext(Protocol):
    def __call__(self, *args: Any, range_header: str) -> Awaitable[AsyncIterator[bytes]]:
        pass


class AsyncDownloadBlobStream(
    AsyncIterator[bytes],
    AsyncContextManager[T],
):
    """Protocol for methods to provide streamed responses."""

    def __init__(
        self,
        *,
        response: AsyncIterator[bytes],
        get_next: GetNext,
        blob_size: int,
        downloaded: int,
        digest: str,
        chunk_size: int
    ) -> None:
        self._response = response
        self._next = get_next
        self._blob_size = blob_size
        self._downloaded = downloaded
        self._digest = digest
        self._chunk_size = chunk_size
        self._hasher = hashlib.sha256()

    async def __aenter__(self: T) -> T:
        return self

    async def __aexit__(self, *args) -> None:
        return None

    def __aiter__(self: T) -> T:
        return self

    async def _yield_data(self) -> bytes:
        data = await self._response.__anext__()
        self._hasher.update(data)
        return data

    async def _download_chunk(self) -> AsyncIterator[bytes]:
        end_range = self._downloaded + self._chunk_size
        range_header = f"bytes={self._downloaded}-{end_range}"
        next_chunk, headers = cast(
            Tuple[AsyncIterator[bytes], Dict[str, str]],
            await self._next(range_header=range_header)
        )
        self._downloaded += int(headers["Content-Length"])
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
