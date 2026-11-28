# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from typing import Callable
from unittest.mock import MagicMock, Mock, patch

import pytest
from azure.identity._internal.aad_client_base import JWT_BEARER_ASSERTION
from azure.identity import TokenCachePersistenceOptions
from azure.identity.aio import ClientAssertionCredential

from helpers import build_aad_response, mock_response, GET_TOKEN_METHODS
from helpers_async import AsyncMockTransport


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


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
@pytest.mark.parametrize("callback_type", ["sync", "async", "future"])
@pytest.mark.parametrize("use_context_manager", [False, True])
async def test_assertion_callback(get_token_method, callback_type, use_context_manager):
    assertion = "ASSERTION_TOKEN"
    access_token = "access-token"

    async def async_callback():
        return assertion

    def callback():
        if callback_type == "async":
            return async_callback()
        if callback_type == "future":
            future = asyncio.get_running_loop().create_future()
            future.set_result(assertion)
            return future
        return assertion

    func = Mock(side_effect=callback)

    async def send(request, **kwargs):
        assert request.data["client_assertion"] == assertion
        assert request.data["client_assertion_type"] == JWT_BEARER_ASSERTION
        return mock_response(json_payload=build_aad_response(access_token=access_token))

    credential = ClientAssertionCredential(
        tenant_id="tenant-id", client_id="client-id", func=func, transport=AsyncMockTransport(send=send)
    )

    async def check_token():
        token = await getattr(credential, get_token_method)("scope")
        assert token.token == access_token
        cached_token = await getattr(credential, get_token_method)("scope")
        assert cached_token.token == access_token
        func.assert_called_once_with()

    if use_context_manager:
        async with credential:
            await check_token()
    else:
        try:
            await check_token()
        finally:
            await credential.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_token_cache_persistence(get_token_method):
    """The credential should use a persistent cache if cache_persistence_options are configured."""

    access_token = "foo"
    tenant_id: str = "TENANT_ID"
    client_id: str = "CLIENT_ID"
    scope = "scope"
    assertion = "ASSERTION_TOKEN"
    func: Callable[[], str] = lambda: assertion

    async def send(request, **kwargs):
        assert request.data["client_assertion"] == assertion
        assert request.data["client_assertion_type"] == JWT_BEARER_ASSERTION
        assert request.data["client_id"] == client_id
        assert request.data["grant_type"] == "client_credentials"
        assert request.data["scope"] == scope

        return mock_response(json_payload=build_aad_response(access_token=access_token))

    with patch("azure.identity._internal.aad_client_base._load_persistent_cache") as load_persistent_cache:
        credential = ClientAssertionCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            func=func,
            cache_persistence_options=TokenCachePersistenceOptions(),
            transport=Mock(send=send),
        )

        assert load_persistent_cache.call_count == 0
        assert credential._client._cache is None
        assert credential._client._cae_cache is None

        token = await getattr(credential, get_token_method)(scope)
        assert token.token == access_token
        assert load_persistent_cache.call_count == 1
        assert credential._client._cache is not None
        assert credential._client._cae_cache is None

        kwargs = {"enable_cae": True}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = await getattr(credential, get_token_method)(scope, **kwargs)
        assert load_persistent_cache.call_count == 2
        assert credential._client._cae_cache is not None
