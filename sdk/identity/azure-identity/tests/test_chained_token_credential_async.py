# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.identity.aio import ChainedTokenCredential
import pytest
from unittest.mock import Mock

from helpers_async import get_completed_future


@pytest.mark.asyncio
async def test_close():
    credentials = [Mock(close=Mock(wraps=get_completed_future)) for _ in range(5)]
    chain = ChainedTokenCredential(*credentials)

    await chain.close()

    for credential in credentials:
        assert credential.close.call_count == 1


@pytest.mark.asyncio
async def test_context_manager():
    credentials = [Mock(close=Mock(wraps=get_completed_future)) for _ in range(5)]
    chain = ChainedTokenCredential(*credentials)

    async with chain:
        pass

    for credential in credentials:
        assert credential.close.call_count == 1
