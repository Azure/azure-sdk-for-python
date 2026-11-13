# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Public proxies backed by deterministic typed pages, with legacy access forbidden."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from azure.cosmos._backend.contracts import BackendPage, ContainerMetadata
from azure.cosmos._helpers._item_context import ItemClientContext, ItemClientDefaults
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy

LINK = "dbs/testdb/colls/testcontainer"


def page(rows=(), charge=None, *, more=False, diagnostics=None, status=200):
    headers = {} if charge is None else {"X-MS-REQUEST-CHARGE": str(charge)}
    return BackendPage(
        status_code=status, headers=headers, body=json.dumps({"Documents": list(rows)}).encode(),
        has_more=more, continuation_supported=False, diagnostics=diagnostics,
    )


class ForbiddenConnection:
    def __getattr__(self, name):
        raise AssertionError(f"read_items touched legacy connection: {name}")


def make_proxy(asynchronous=False, pages=None, *, paths=("/pk",), kind="Hash", defaults=None):
    responses = iter([page()] if pages is None else pages)
    backend = SimpleNamespace(name="rust", calls=[], deadlines=[], closed=0)
    metadata = ContainerMetadata("rid", paths, kind, False)
    backend.get_container_metadata = (AsyncMock if asynchronous else MagicMock)(return_value=metadata)
    backend.create_item_feed_cursor = MagicMock(side_effect=lambda: SimpleNamespace(has_more=True))

    def next_page(prepared, deadline):
        backend.calls.append(prepared)
        backend.deadlines.append(deadline)
        response = next(responses)
        if isinstance(response, BaseException):
            raise response
        return response() if callable(response) else response

    def execute(prepared, *, deadline=None):
        try:
            yield next_page(prepared, deadline)
        finally:
            backend.closed += 1

    async def execute_async(prepared, *, deadline=None):
        try:
            yield next_page(prepared, deadline)
        finally:
            backend.closed += 1

    backend.execute_pages = execute_async if asynchronous else execute
    proxy = object.__new__(AsyncContainerProxy if asynchronous else ContainerProxy)
    proxy.container_link = LINK
    proxy.id = "testcontainer"
    proxy.client_connection = ForbiddenConnection()
    proxy._item_context = ItemClientContext(backend, defaults=defaults or ItemClientDefaults())
    return proxy, backend
