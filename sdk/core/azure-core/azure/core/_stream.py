# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import (
    Iterable,
    AsyncIterable,
    # ContextManager,
    # AsyncContextManager,
    Generic,
    TypeVar
)
from typing_extensions import Protocol, runtime_checkable, Self


_StreamContentType_co = TypeVar("_StreamContentType_co", covariant=True)


@runtime_checkable
class Streamable(
    Iterable[_StreamContentType_co],
    # ContextManager["Streamable"],  # Not supported in Python 3.7
    Generic[_StreamContentType_co],
    Protocol
):
    """Protocol for methods to provide streamed responses."""
    def __enter__(self) -> Self:
        ...

    def __exit__(self, *args) -> None:
        ...

    def close(self) -> None:
        ...


@runtime_checkable
class AsyncStreamable(
    AsyncIterable[_StreamContentType_co],
    # AsyncContextManager["AsyncStreamable"],    # Not supported in Python 3.7
    Generic[_StreamContentType_co],
    Protocol
):
    """Protocol for methods to provide async streamed responses."""
    async def __aenter__(self) -> Self:
        ...

    async def __aexit__(self, *args) -> None:
        ...

    async def close(self) -> None:
        ...
