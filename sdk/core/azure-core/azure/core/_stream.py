# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import Iterator, AsyncIterator
from typing_extensions import Protocol, runtime_checkable, Self


@runtime_checkable
class Streamable(Protocol):
    """Protocol for methods to provide streamed responses."""

    def close(self) -> None:
        pass

    def __iter__(self) -> Iterator[bytes]:
        pass

    def __enter__(self) -> Self:
        pass

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass


@runtime_checkable
class AsyncStreamable(Protocol):
    """Protocol for methods to provide async streamed responses."""

    async def close(self) -> None:
        pass

    async def __aiter__(self) -> AsyncIterator[bytes]:
        pass

    async def __aenter__(self) -> Self:
        pass

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass
