# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.identity.aio._credentials.managed_identity import ImdsCredential
import pytest

from helpers_async import AsyncMockTransport


@pytest.mark.asyncio
async def test_imds_close():
    transport = AsyncMockTransport()

    credential = ImdsCredential(transport=transport)

    await credential.close()

    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_imds_context_manager():
    transport = AsyncMockTransport()
    credential = ImdsCredential(transport=transport)

    async with credential:
        pass

    assert transport.__aexit__.call_count == 1
