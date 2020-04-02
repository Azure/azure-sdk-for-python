# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest import mock

from azure.core.exceptions import HttpResponseError
from azure.identity.aio._credentials.managed_identity import ImdsCredential
import pytest

from helpers import mock_response
from helpers_async import AsyncMockTransport, get_completed_future


@pytest.mark.asyncio
async def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    successful_probe = mock_response(status_code=400, json_payload={})
    transport = mock.Mock(send=mock.Mock(return_value=get_completed_future(successful_probe)))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(ValueError):
        await credential.get_token()


@pytest.mark.asyncio
async def test_multiple_scopes():
    """The credential should raise ValueError when get_token is called with more than one scope"""

    successful_probe = mock_response(status_code=400, json_payload={})
    transport = mock.Mock(send=mock.Mock(return_value=get_completed_future(successful_probe)))
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
