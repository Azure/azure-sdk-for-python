# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import hashlib
from typing import Iterator, ContextManager, Callable
from typing_extensions import Self


class DownloadBlobStream(
    Iterator[bytes],
    ContextManager[Self],
):
    """Protocol for methods to provide streamed responses."""

    def __init__(self, **kwargs) -> None:
        self._response: Iterator[bytes] = kwargs.get('response')
        self._next: Callable[[str], Iterator[bytes]] = kwargs.get('next')
        self._blob_size: int = kwargs.get('blob_size')
        self._downloaded: int = kwargs.get('downloaded')
        self._hasher = hashlib.sha256()
        self._digest: str = kwargs.get('digest')
        self._chunk_size: int = kwargs.get('chunk_size')

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def __iter__(self) -> Self:
        return self

    def _yield_data(self) -> bytes:
        data = next(self._response)
        self._hasher.update(data)
        return data

    def _download_chunk(self) -> Iterator[bytes]:
        end_range = self._downloaded + self._chunk_size
        range_header = f"bytes={self._downloaded}-{end_range}"
        next_chunk, headers = self._next(range=range_header)
        self._downloaded += headers["Content-Length"]
        return next_chunk

    def __next__(self) -> bytes:
        try:
            return self._yield_data()
        except StopIteration:
            if self._downloaded >= self._blob_size:
                computed_digest = "sha256:" + self._hasher.hexdigest()
                if computed_digest != self._digest:
                    raise ValueError("The requested digest does not match the digest of the received blob.")
                raise
            self._response = self._download_chunk()
            return self._yield_data()

    def close(self) -> None:
        self._response.close()
