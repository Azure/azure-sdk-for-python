# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Create clients without provisioning resources; callers own client cleanup."""

from functools import lru_cache
from types import SimpleNamespace

from azure.cosmos import ConnectionPoolOptions, CosmosClient, CosmosRuntime
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient

from config.settings import TestSettings


@lru_cache(maxsize=2)
def _aad_credential(async_mode):
    from devtools_testutils.azure_recorded_testcase import get_credential
    from devtools_testutils.helpers import is_live

    is_live._cache = True
    return get_credential(is_async=True) if async_mode else get_credential()


def _credential(settings, async_mode):
    if settings.data_auth_mode not in ("key", "aad"):
        raise ValueError(f"Unknown COSMOS_TEST_DATA_AUTH_MODE: {settings.data_auth_mode!r}. Expected 'key' or 'aad'.")
    if settings.data_auth_mode == "key" or settings.is_emulator:
        return settings.masterKey
    return _aad_credential(async_mode)


def create_setup_client(*, settings=TestSettings, **kwargs):
    """Create the key-authenticated Rust client used for provisioning."""
    kwargs.setdefault("_backend", "rust")
    return CosmosClient(settings.host, settings.masterKey, **kwargs)


def create_fault_setup_client(endpoint, key):
    """Create an independent, direct Rust client without fault rules."""
    runtime = CosmosRuntime.create(connection_pool=ConnectionPoolOptions(proxy_allowed=False))
    return create_setup_client(
        settings=SimpleNamespace(host=endpoint, masterKey=key),
        runtime=runtime,
        timeout=30,
    )


def create_data_client(*, settings=TestSettings, **kwargs):
    """Create a synchronous Rust client using the configured data authentication."""
    return create_data_client_for_endpoint(settings.host, settings=settings, **kwargs)


def create_data_client_for_endpoint(endpoint, *, settings=TestSettings, **kwargs):
    """Create a synchronous client, optionally overriding the configured endpoint."""
    kwargs.setdefault("_backend", "rust")
    return CosmosClient(endpoint or settings.host, _credential(settings, False), **kwargs)


def create_data_client_async(*, settings=TestSettings, **kwargs):
    """Create an unentered async client; the caller must enter and close it."""
    return create_data_client_async_for_endpoint(settings.host, settings=settings, **kwargs)


def create_data_client_async_for_endpoint(endpoint, *, settings=TestSettings, **kwargs):
    """Create an unentered async client for a particular endpoint."""
    kwargs.setdefault("_backend", "rust")
    return AsyncCosmosClient(endpoint or settings.host, _credential(settings, True), **kwargs)
