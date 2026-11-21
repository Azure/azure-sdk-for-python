# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Exercise scope selection through the compiled binding before any service request."""

import asyncio

import pytest
from azure.core.exceptions import HttpResponseError

from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos._base import create_scope_from_url
from azure.cosmos._backend.contracts import PreparedClientConfig

_OVERRIDE_ENV = "AZURE_COSMOS_AAD_SCOPE_OVERRIDE"
_GLOBAL_SCOPE = "https://cosmos.azure.com/.default"
_OVERRIDE_SCOPE = "https://override.example/.default"
_ENDPOINTS = [
    "https://alpha-bank-account.documents.azure.com:443/",
    "https://alpha-bank-account.documents.azure.cn/",
    "https://localhost:8081/",
]


def _set_override(monkeypatch, override):
    if override is None:
        monkeypatch.delenv(_OVERRIDE_ENV, raising=False)
    else:
        monkeypatch.setenv(_OVERRIDE_ENV, override)


class _FailingCredential:
    def __init__(self, fallback):
        self.scopes = []
        self.errors = []
        self.fallback = fallback
        self.closed = False

    def get_token(self, *scopes, **kwargs):
        self.scopes.append(scopes)
        message = "AADSTS500011: scope-test-stop" if self.fallback else "scope-test-stop"
        self.errors.append(HttpResponseError(message=message))
        raise self.errors[-1]

    def close(self):
        self.closed = True


class _AsyncFailingCredential(_FailingCredential):
    def __init__(self, fallback):
        super().__init__(fallback)
        self.loops = []

    async def get_token(self, *scopes, **kwargs):
        self.loops.append(asyncio.get_running_loop())
        return super().get_token(*scopes, **kwargs)

    async def close(self):
        self.closed = True


def _expected_scopes(endpoint, override, fallback):
    initial = override or create_scope_from_url(endpoint)
    scopes = [(initial,)]
    if fallback and not override and initial != _GLOBAL_SCOPE:
        scopes.append((_GLOBAL_SCOPE,))
    return scopes


def _assert_credential_error_preserved(raised, credential):
    # Like legacy, the customer app gets the credential's own exception, not a driver wrapper.
    assert type(raised) is HttpResponseError
    assert raised is credential.errors[-1]
    assert len(credential.errors) == len(credential.scopes)
    assert str(raised) == ("AADSTS500011: scope-test-stop" if credential.fallback else "scope-test-stop")


@pytest.mark.parametrize("endpoint", _ENDPOINTS)
@pytest.mark.parametrize("override", [None, "", _OVERRIDE_SCOPE])
@pytest.mark.parametrize("fallback", [False, True])
def test_sync_scope_is_captured_before_native_acquisition_rust(monkeypatch, endpoint, override, fallback):
    _set_override(monkeypatch, override)
    credential = _FailingCredential(fallback)
    client = CosmosClient(endpoint, credential, _backend="rust")
    try:
        assert credential.scopes == []
        monkeypatch.setenv(_OVERRIDE_ENV, "https://later.example/.default")
        # The test credential fails before any service request is sent.
        with pytest.raises(HttpResponseError) as raised:
            client.get_database_client("alpha-bank-db").read()
        assert credential.scopes == _expected_scopes(endpoint, override, fallback)
        _assert_credential_error_preserved(raised.value, credential)
    finally:
        client.close()
    assert not credential.closed


@pytest.mark.parametrize("endpoint", _ENDPOINTS)
@pytest.mark.parametrize("override", [None, "", _OVERRIDE_SCOPE])
@pytest.mark.parametrize("fallback", [False, True])
@pytest.mark.parametrize("async_credential", [False, True])
def test_async_scope_preserves_owner_loop_rust(monkeypatch, endpoint, override, fallback, async_credential):
    _set_override(monkeypatch, override)
    credential = (_AsyncFailingCredential if async_credential else _FailingCredential)(fallback)
    client = AsyncCosmosClient(endpoint, credential, _backend="rust")
    assert credential.scopes == []
    monkeypatch.setenv(_OVERRIDE_ENV, "https://later.example/.default")

    async def run():
        try:
            # The test credential fails before any service request is sent.
            with pytest.raises(HttpResponseError) as raised:
                await client.get_database_client("alpha-bank-db").read()
            assert credential.scopes == _expected_scopes(endpoint, override, fallback)
            _assert_credential_error_preserved(raised.value, credential)
            if async_credential:
                assert credential.loops == [asyncio.get_running_loop()] * len(credential.scopes)
        finally:
            await client.close()

    asyncio.run(run())
    assert not credential.closed


@pytest.mark.parametrize("value", [False, 1, (), {}])
def test_scope_override_requires_a_string_rust(value):
    with pytest.raises(TypeError):
        PreparedClientConfig(aad_scope_override=value)


def test_account_key_client_does_not_capture_scope_override_rust(monkeypatch):
    monkeypatch.setenv(_OVERRIDE_ENV, _OVERRIDE_SCOPE)
    client = CosmosClient(_ENDPOINTS[0], "example-key", _backend="rust")
    try:
        assert client._adapter._client_config is None
    finally:
        client.close()
