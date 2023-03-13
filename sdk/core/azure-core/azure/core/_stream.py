# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import (
    Iterable,
    AsyncIterable,
    ContextManager,
    AsyncContextManager,
    Generic,
    TypeVar
)
from typing_extensions import Protocol, runtime_checkable, Self


StreamContentType = TypeVar("StreamContentType")


@runtime_checkable
class Streamable(
    Iterable[StreamContentType],
    ContextManager[Self],
    Generic[StreamContentType],
    Protocol
):
    """Protocol for methods to provide streamed responses."""

    def close(self) -> None:
        pass


@runtime_checkable
class AsyncStreamable(
    AsyncIterable[StreamContentType],
    AsyncContextManager[Self],
    Generic[StreamContentType],
    Protocol
):
    """Protocol for methods to provide async streamed responses."""

    async def close(self) -> None:
        pass
