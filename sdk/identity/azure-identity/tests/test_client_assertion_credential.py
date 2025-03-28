# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Callable
from unittest.mock import MagicMock, Mock, patch
from urllib.parse import urlparse

from azure.identity._internal.aad_client_base import JWT_BEARER_ASSERTION
from azure.identity import ClientAssertionCredential, TokenCachePersistenceOptions
import pytest

from helpers import build_aad_response, mock_response, get_discovery_response, GET_TOKEN_METHODS


def test_init_with_kwargs():
    tenant_id: str = "tenant-id"
    client_id: str = "CLIENT_ID"
    func: Callable[[], str] = lambda: "TOKEN"

    credential: ClientAssertionCredential = ClientAssertionCredential(
        tenant_id=tenant_id, client_id=client_id, func=func, authority="a"
    )

    # Test arbitrary keyword argument
    credential = ClientAssertionCredential(tenant_id=tenant_id, client_id=client_id, func=func, foo="a", bar="b")


def test_context_manager():
    tenant_id: str = "tenant-id"
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


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_token_cache_persistence(get_token_method):
    """The credential should use a persistent cache if cache_persistence_options are configured."""

    access_token = "foo"
    tenant_id: str = "tenant-id"
    client_id: str = "CLIENT_ID"
    scope = "scope"
    assertion = "ASSERTION_TOKEN"
    func: Callable[[], str] = lambda: assertion

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))

        assert request.data["client_assertion"] == assertion
        assert request.data["client_assertion_type"] == JWT_BEARER_ASSERTION
        assert request.data["client_id"] == client_id
        assert request.data["grant_type"] == "client_credentials"
        assert request.data["scope"] == scope
        assert tenant_id in request.url
        return mock_response(json_payload=build_aad_response(access_token=access_token))

    with patch("azure.identity._internal.msal_credentials._load_persistent_cache") as load_persistent_cache:
        credential = ClientAssertionCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            func=func,
            cache_persistence_options=TokenCachePersistenceOptions(),
            transport=Mock(send=send),
        )

        assert load_persistent_cache.call_count == 0
        assert credential._cache is None
        assert credential._cae_cache is None

        token = getattr(credential, get_token_method)(scope)
        assert token.token == access_token
        assert load_persistent_cache.call_count == 1
        assert credential._cache is not None
        assert credential._cae_cache is None

        kwargs = {"enable_cae": True}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = getattr(credential, get_token_method)(scope, **kwargs)
        assert load_persistent_cache.call_count == 2
        assert credential._cae_cache is not None


def test_client_capabilities():
    """The credential should use the CAE-enabled client when enable_cae is True"""
    assertion = "ASSERTION_TOKEN"
    transport = Mock(send=Mock(side_effect=Exception("this test mocks MSAL, so no request should be sent")))
    func: Callable[[], str] = lambda: assertion
    credential = ClientAssertionCredential("tenant-id", "client-id", func, transport=transport)
    with patch("msal.ConfidentialClientApplication") as ConfidentialClientApplication:
        credential._get_app()

        assert ConfidentialClientApplication.call_count == 1
        _, kwargs = ConfidentialClientApplication.call_args
        assert kwargs["client_capabilities"] == None

        credential._get_app(enable_cae=True)
        assert ConfidentialClientApplication.call_count == 2
        _, kwargs = ConfidentialClientApplication.call_args
        assert kwargs["client_capabilities"] == ["CP1"]
