# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest import mock

from azure.identity._constants import EnvironmentVariables
from azure.identity.aio._credentials.managed_identity import MsiCredential
import pytest

from helpers_async import AsyncMockTransport


@pytest.mark.asyncio
async def test_close():
    transport = AsyncMockTransport()

    with mock.patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "https://url"}):
        credential = MsiCredential(transport=transport)

    await credential.close()

    assert transport.exited


@pytest.mark.asyncio
async def test_context_manager():
    transport = AsyncMockTransport()

    with mock.patch("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "https://url"}):
        credential = MsiCredential(transport=transport)

    async with credential:
        pass

    assert transport.exited
