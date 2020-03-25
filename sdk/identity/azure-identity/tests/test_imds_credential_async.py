# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest import mock

from azure.core.exceptions import HttpResponseError
from azure.identity.aio._credentials.managed_identity import ImdsCredential
import pytest

from helpers_async import AsyncMockTransport


@pytest.mark.asyncio
async def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    # the credential will probe the endpoint, taking HttpResponseError as indicating availability
    transport = mock.Mock(send=mock.Mock(side_effect=HttpResponseError()))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(ValueError):
        await credential.get_token()


@pytest.mark.asyncio
async def test_multiple_scopes():
    """The credential should raise ValueError when get_token is called with more than one scope"""

    # the credential will probe the endpoint, taking HttpResponseError as indicating availability
    transport = mock.Mock(send=mock.Mock(side_effect=HttpResponseError()))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(ValueError):
        await credential.get_token("one scope", "and another")


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
