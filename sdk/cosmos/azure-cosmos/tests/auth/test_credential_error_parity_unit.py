# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline credential-error parity through public Rust-backed clients."""

import asyncio
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import PipelineContext, PipelineRequest
from azure.core.rest import HttpRequest
from azure.cosmos import CosmosClient
from azure.cosmos._auth_policy import CosmosBearerTokenCredentialPolicy
from azure.cosmos._backend import binding_adapter as sync_rust
from azure.cosmos._backend.contracts import BindingPartitionKey, PreparedPageRequest, PreparedRequest
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.aio._auth_policy_async import AsyncCosmosBearerTokenCredentialPolicy
from azure.cosmos.aio._backend import binding_adapter as async_rust
from azure.cosmos.exceptions import CosmosClientTimeoutError


class CustomAuthenticationError(ClientAuthenticationError):
    pass


class CustomTimeoutError(TimeoutError):
    def __getattribute__(self, name):
        if name in ("__dict__", "_cosmos_credential_error"):
            raise AssertionError("credential attributes must not be invoked")
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name == "_cosmos_credential_error":
            raise AssertionError("credential attributes must not be invoked")
        super().__setattr__(name, value)


@pytest.mark.parametrize("client_kind", ["sync", "async-sync-credential", "async-credential"])
@pytest.mark.parametrize("error_type", [
    ClientAuthenticationError, CustomAuthenticationError,
    ValueError, TimeoutError, CustomTimeoutError, RuntimeError,
])
def test_credential_authentication_error_matches_legacy_rust(client_kind, error_type):
    endpoint = "https://authentication-error.invalid"
    scope = f"{endpoint}/.default"
    error = error_type("AADSTS7000215: offline authentication failure")
    original_args = error.args
    original_cause = ValueError("offline credential cause")
    error.__cause__ = original_cause
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
    assert error.args == original_args
    assert error.__cause__ is original_cause


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("operation", ["point", "metadata", "page"])
@pytest.mark.parametrize("has_deadline", [False, True])
@pytest.mark.parametrize("credential_error", [False, True])
def test_credential_timeout_is_not_operation_deadline_rust(
    monkeypatch, async_mode, operation, has_deadline, credential_error
):
    error = CustomTimeoutError("offline timeout")
    if credential_error:
        BaseException.__dict__["__dict__"].__get__(error)["_cosmos_credential_error"] = True
    module = async_rust if async_mode else sync_rust
    cls = module.AsyncBindingAdapter if async_mode else module.BindingAdapter
    backend = cls("https://authentication-error.invalid", master_key="test-key")
    mock = AsyncMock if async_mode else MagicMock
    monkeypatch.setattr(backend, "_ensure_driver_handle", mock(return_value="handle"))
    method = {"point": "read_database", "metadata": "get_container_metadata", "page": "list_databases"}[operation]
    dispatch = mock(side_effect=error)
    monkeypatch.setattr(module, "_rust_module", SimpleNamespace(
        **{method + ("_async" if async_mode else ""): dispatch}
    ))
    deadline = time.monotonic() + 10 if has_deadline else None
    prepared = PreparedRequest(
        op="read_database", container_link="dbs/db", body_bytes=b"",
        partition_key=BindingPartitionKey("cross_partition"),
    )
    page = PreparedPageRequest(op="list_databases", container_link="")

    async def run_async():
        if operation == "point":
            await backend.execute(prepared, deadline=deadline)
        elif operation == "metadata":
            await backend.get_container_metadata("dbs/db/colls/container", deadline=deadline)
        else:
            async for _ in backend.execute_pages(page, deadline=deadline):
                pass

    translated = has_deadline and not credential_error
    with pytest.raises(CosmosClientTimeoutError if translated else CustomTimeoutError) as caught:
        if async_mode:
            asyncio.run(run_async())
        elif operation == "point":
            backend.execute(prepared, deadline=deadline)
        elif operation == "metadata":
            backend.get_container_metadata("dbs/db/colls/container", deadline=deadline)
        else:
            list(backend.execute_pages(page, deadline=deadline))
    if translated:
        assert caught.value.__cause__ is error
    else:
        assert caught.value is error
    assert dispatch.call_count == 1
