# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.keyvault.keys.aio import KeyClient
from azure.keyvault.keys.crypto.aio import CryptographyClient

from _shared.helpers_async import AsyncMockTransport


@pytest.mark.asyncio
async def test_key_client_close():
    transport = AsyncMockTransport()
    client = KeyClient(vault_url="https://localhost", credential=object(), transport=transport)

    await client.close()
    assert transport.__aenter__.call_count == 0
    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_key_client_context_manager():
    transport = AsyncMockTransport()
    client = KeyClient(vault_url="https://localhost", credential=object(), transport=transport)

    async with client:
        assert transport.__aenter__.call_count == 1
    assert transport.__aenter__.call_count == 1
    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_crypto_client_close():
    transport = AsyncMockTransport()
    client = CryptographyClient(key="https://localhost/a/b/c", credential=object(), transport=transport)
    await client.close()
    assert transport.__aenter__.call_count == 0
    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_crypto_client_context_manager():
    transport = AsyncMockTransport()
    client = CryptographyClient(key="https://localhost/a/b/c", credential=object(), transport=transport)
    async with client:
        assert transport.__aenter__.call_count == 1
    assert transport.__aenter__.call_count == 1
    assert transport.__aexit__.call_count == 1
