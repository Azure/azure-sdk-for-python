# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Callable
from unittest.mock import MagicMock

import pytest
from azure.identity.aio import ClientAssertionCredential


def test_init_with_kwargs():
    tenant_id: str = "TENANT_ID"
    client_id: str = "CLIENT_ID"
    func: Callable[[], str] = lambda: "TOKEN"

    credential: ClientAssertionCredential = ClientAssertionCredential(
        tenant_id=tenant_id, client_id=client_id, func=func, authority="a"
    )

    # Test arbitrary keyword argument
    credential = ClientAssertionCredential(tenant_id=tenant_id, client_id=client_id, func=func, foo="a", bar="b")


@pytest.mark.asyncio
async def test_context_manager():
    tenant_id: str = "TENANT_ID"
    client_id: str = "CLIENT_ID"
    func: Callable[[], str] = lambda: "TOKEN"

    transport = MagicMock()
    credential: ClientAssertionCredential = ClientAssertionCredential(
        tenant_id=tenant_id, client_id=client_id, func=func, transport=transport
    )

    async with credential:
        assert transport.__aenter__.called
        assert not transport.__aexit__.called

    assert transport.__aexit__.called
