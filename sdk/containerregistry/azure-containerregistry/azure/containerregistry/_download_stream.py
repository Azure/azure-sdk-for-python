# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import hashlib
from typing import Iterator, ContextManager, cast, Tuple, Dict, Any
from typing_extensions import Protocol, Self
from azure.core.pipeline import PipelineResponse
from ._models import ManifestDigestValidationError


class GetNext(Protocol):
    def __call__(self, *args: Any, range_header: str) -> Iterator[bytes]:
        pass


class DownloadBlobStream(
    Iterator[bytes],
    ContextManager["DownloadBlobStream"],
):
    """Protocol for methods to provide streamed responses."""

    def __init__(
        self,
        *,
        response: PipelineResponse,
        get_next: GetNext,
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

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def __iter__(self) -> Self:
        return self

    def _yield_data(self) -> bytes:
        data = next(self._response_bytes)
        self._hasher.update(data)
        return data

    def _download_chunk(self) -> PipelineResponse:
        end_range = self._downloaded + self._chunk_size - 1
        range_header = f"bytes={self._downloaded}-{end_range}"
        next_chunk, headers = cast(
            Tuple[PipelineResponse, Dict[str, str]],
            self._next(range_header=range_header)
        )
        self._downloaded += int(headers["Content-Length"])
        return next_chunk

    def __next__(self) -> bytes:
        try:
            return self._yield_data()
        except StopIteration:
            if self._downloaded >= self._blob_size:
                computed_digest = "sha256:" + self._hasher.hexdigest()
                if computed_digest != self._digest:
                    raise ManifestDigestValidationError(
                        "The content of retrieved blob digest does not match the requested digest."
                    )
                raise
            self._response = self._download_chunk()
            self._response_bytes = self._response.http_response.iter_bytes()
            return self.__next__()

    def close(self):
        self._response.http_response.close()
