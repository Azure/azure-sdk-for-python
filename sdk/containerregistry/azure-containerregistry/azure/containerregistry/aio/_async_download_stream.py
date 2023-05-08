# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import hashlib
from typing import AsyncIterator, AsyncContextManager, Awaitable, cast, Tuple, Dict, Any
from typing_extensions import Protocol, Self
from azure.core.pipeline import PipelineResponse
from .._models import ManifestDigestValidationError


class AsyncGetNext(Protocol):
    def __call__(self, *args: Any, range_header: str) -> Awaitable[AsyncIterator[bytes]]:
        pass


class AsyncDownloadBlobStream(
    AsyncIterator[bytes],
    AsyncContextManager["AsyncDownloadBlobStream"],
):
    """Protocol for methods to provide streamed responses."""

    def __init__(
        self,
        *,
        response: PipelineResponse,
        get_next: AsyncGetNext,
        blob_size: int,
        downloaded: int,
        digest: str,
        chunk_size: int
    ) -> None:
        self._response = response
        self._response_bytes = response.http_response.iter_bytes()
        self._next = get_next
        self._blob_size = blob_size
        self._downloaded = downloaded
        self._digest = digest
        self._chunk_size = chunk_size
        self._hasher = hashlib.sha256()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    def __aiter__(self) -> Self:
        return self

    async def _yield_data(self) -> bytes:
        data = await self._response_bytes.__anext__()
        self._hasher.update(data)
        return data

    async def _download_chunk(self) -> PipelineResponse:
        end_range = self._downloaded + self._chunk_size - 1
        range_header = f"bytes={self._downloaded}-{end_range}"
        next_chunk, headers = cast(
            Tuple[PipelineResponse, Dict[str, str]],
            await self._next(range_header=range_header)
        )
        self._downloaded += int(headers["Content-Length"])
        return next_chunk

    async def __anext__(self) -> bytes:
        try:
            return await self._yield_data()
        except StopAsyncIteration:
            if self._downloaded >= self._blob_size:
                computed_digest = "sha256:" + self._hasher.hexdigest()
                if computed_digest != self._digest:
                    raise ManifestDigestValidationError(
                        "The content of retrieved blob digest does not match the requested digest."
                    )
                raise
            self._response = await self._download_chunk()
            self._response_bytes = self._response.http_response.iter_bytes()
            return await self._yield_data()

    async def close(self):
        await self._response.http_response.close()
