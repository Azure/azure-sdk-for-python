# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Callable

from azure.core.async_paging import AsyncPagedMixin
from msrest.serialization import Model


class AsyncPagingAdapter:
    """For each item in an AsyncPagedMixin, returns the result of applying fn to that item.
    Python 3.6 added syntax that could replace this (yield within async for)."""
    def __init__(self, pages, fn):
        # type: (AsyncPagedMixin, Callable[[Model], Any]) -> None
        self._pages = pages
        self._fn = fn

    def __aiter__(self):
        return self

    async def __anext__(self):
        item = await self._pages.__anext__()
        if not item:
            raise StopAsyncIteration
        return self._fn(item)
