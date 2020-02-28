# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.keyvault.certificates.aio import CertificateClient
import pytest

from _shared.helpers_async import AsyncMockTransport


@pytest.mark.asyncio
async def test_close():
    transport = AsyncMockTransport()
    client = CertificateClient(vault_url="https://localhost", credential=object(), transport=transport)

    await client.close()
    assert transport.__aenter__.call_count == 0
    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_context_manager():
    transport = AsyncMockTransport()
    client = CertificateClient(vault_url="https://localhost", credential=object(), transport=transport)

    async with client:
        assert transport.__aenter__.call_count == 1
    assert transport.__aenter__.call_count == 1
    assert transport.__aexit__.call_count == 1
