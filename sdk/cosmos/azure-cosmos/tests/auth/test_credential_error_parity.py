# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline authentication-error parity through public Rust-backed clients."""

import asyncio

import pytest
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import PipelineContext, PipelineRequest
from azure.core.rest import HttpRequest
from azure.cosmos import CosmosClient
from azure.cosmos._auth_policy import CosmosBearerTokenCredentialPolicy
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.aio._auth_policy_async import AsyncCosmosBearerTokenCredentialPolicy


class CustomAuthenticationError(ClientAuthenticationError):
    pass


@pytest.mark.parametrize("client_kind", ["sync", "async-sync-credential", "async-credential"])
@pytest.mark.parametrize("error_type", [ClientAuthenticationError, CustomAuthenticationError])
def test_credential_authentication_error_matches_legacy_rust(client_kind, error_type):
    endpoint = "https://authentication-error.invalid"
    scope = f"{endpoint}/.default"
    error = error_type(message="AADSTS7000215: offline authentication failure")
    calls = []

    class Credential:
        def get_token(self, *scopes, **kwargs):
            calls.append(scopes)
            raise error

    class AsyncCredential(Credential):
        async def get_token(self, *scopes, **kwargs):
            return super().get_token(*scopes, **kwargs)

    credential = AsyncCredential() if client_kind == "async-credential" else Credential()
    request = PipelineRequest(HttpRequest("GET", endpoint), PipelineContext(None))

    async def run_async():
        with pytest.raises(error_type) as legacy:
            await AsyncCosmosBearerTokenCredentialPolicy(credential, scope).on_request(request)
        assert legacy.value is error
        client = AsyncCosmosClient(endpoint, credential, _backend="rust")
        try:
            assert client._adapter.name == "rust"
            with pytest.raises(error_type) as current:
                await client.get_database_client("db").read(timeout=2)
            assert current.value is legacy.value
        finally:
            await client.close()

    if client_kind == "sync":
        with pytest.raises(error_type) as legacy:
            CosmosBearerTokenCredentialPolicy(credential, scope).on_request(request)
        assert legacy.value is error
        client = CosmosClient(endpoint, credential, _backend="rust")
        try:
            assert client._adapter.name == "rust"
            with pytest.raises(error_type) as current:
                client.get_database_client("db").read(timeout=2)
            assert current.value is legacy.value
        finally:
            client.close()
    else:
        asyncio.run(run_async())
    assert calls == [(scope,), (scope,)]
    assert str(error) == "AADSTS7000215: offline authentication failure"
