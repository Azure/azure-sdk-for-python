# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from unittest.mock import AsyncMock, Mock

import pytest

from azure.servicebus._pyamqp import SendClient, ReceiveClient
from azure.servicebus._pyamqp.aio import SendClientAsync, ReceiveClientAsync
from azure.servicebus._pyamqp.constants import LINK_MAX_MESSAGE_SIZE

SIZE_CASES = [({}, LINK_MAX_MESSAGE_SIZE), ({"max_message_size": 5 * 1024 * 1024}, 5 * 1024 * 1024)]


@pytest.mark.parametrize("kwargs, expected", SIZE_CASES)
@pytest.mark.parametrize(
    "cls, factory",
    [(SendClient, "create_sender_link"), (ReceiveClient, "create_receiver_link")],
)
def test_link_max_message_size(cls, factory, kwargs, expected):
    client = cls("fake.host.com", "fake_sb", auth="my_fake_auth", **kwargs)
    client._session = Mock()

    assert client._client_ready() is False
    assert getattr(client._session, factory).call_args.kwargs["max_message_size"] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("kwargs, expected", SIZE_CASES)
@pytest.mark.parametrize(
    "cls, factory",
    [(SendClientAsync, "create_sender_link"), (ReceiveClientAsync, "create_receiver_link")],
)
async def test_link_max_message_size_async(cls, factory, kwargs, expected):
    client = cls("fake.host.com", "fake_sb", auth="my_fake_auth", **kwargs)
    client._session = Mock()
    getattr(client._session, factory).return_value = AsyncMock()

    assert await client._client_ready_async() is False
    assert getattr(client._session, factory).call_args.kwargs["max_message_size"] == expected
