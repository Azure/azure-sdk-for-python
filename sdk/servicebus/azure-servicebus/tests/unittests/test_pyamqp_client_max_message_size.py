# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from unittest.mock import AsyncMock, Mock

import pytest

from azure.servicebus._pyamqp import SendClient, ReceiveClient
from azure.servicebus._pyamqp.aio import SendClientAsync, ReceiveClientAsync
from azure.servicebus._pyamqp.aio._session_async import Session as SessionAsync
from azure.servicebus._pyamqp.constants import LINK_MAX_MESSAGE_SIZE
from azure.servicebus._pyamqp.performatives import AttachFrame
from azure.servicebus._pyamqp.session import Session

SIZE_CASES = [({}, LINK_MAX_MESSAGE_SIZE), ({"max_message_size": 5 * 1024 * 1024}, 5 * 1024 * 1024)]
ATTACH_SIZE_CASES = [({}, 0), ({"max_message_size": 5 * 1024 * 1024}, 5 * 1024 * 1024)]


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


@pytest.mark.parametrize("kwargs, expected", ATTACH_SIZE_CASES)
def test_receiver_attach_frame_max_message_size(kwargs, expected):
    client = ReceiveClient("fake.host.com", "fake_sb", auth="my_fake_auth", **kwargs)
    connection = Mock()
    client._session = Session(connection, 0, network_trace=False, network_trace_params={})

    assert client._client_ready() is False
    frame = connection._process_outgoing_frame.call_args.args[1]
    assert isinstance(frame, AttachFrame)
    assert frame.max_message_size == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("kwargs, expected", ATTACH_SIZE_CASES)
async def test_receiver_attach_frame_max_message_size_async(kwargs, expected):
    client = ReceiveClientAsync("fake.host.com", "fake_sb", auth="my_fake_auth", **kwargs)
    connection = AsyncMock()
    client._session = SessionAsync(connection, 0, network_trace=False, network_trace_params={})

    assert await client._client_ready_async() is False
    frame = connection._process_outgoing_frame.call_args.args[1]
    assert isinstance(frame, AttachFrame)
    assert frame.max_message_size == expected
