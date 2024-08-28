# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Callable
from unittest.mock import MagicMock
from azure.identity import ClientAssertionCredential, WorkloadIdentityCredential


def test_init_with_kwargs():
    tenant_id: str = "TENANT_ID"
    client_id: str = "CLIENT_ID"
    func: Callable[[], str] = lambda: "TOKEN"

    credential: ClientAssertionCredential = ClientAssertionCredential(
        tenant_id=tenant_id, client_id=client_id, func=func, authority="a"
    )

    # Test arbitrary keyword argument
    credential = ClientAssertionCredential(tenant_id=tenant_id, client_id=client_id, func=func, foo="a", bar="b")


def test_context_manager():
    tenant_id: str = "TENANT_ID"
    client_id: str = "CLIENT_ID"
    func: Callable[[], str] = lambda: "TOKEN"

    transport = MagicMock()
    credential: ClientAssertionCredential = ClientAssertionCredential(
        tenant_id=tenant_id, client_id=client_id, func=func, transport=transport
    )

    with credential:
        assert transport.__enter__.called
        assert not transport.__exit__.called
    assert transport.__exit__.called
