# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from unittest.mock import Mock

import pytest

from azure.eventhub._pyamqp import SendClient, ReceiveClient
from azure.eventhub._pyamqp.constants import LINK_MAX_MESSAGE_SIZE
from azure.eventhub._pyamqp.performatives import AttachFrame
from azure.eventhub._pyamqp.session import Session


# shadows conftest's autouse amqpproxy, which skips without a live Event Hub
@pytest.fixture(autouse=True)
def amqpproxy():
    yield


@pytest.mark.parametrize(
    "kwargs, expected",
    [({}, LINK_MAX_MESSAGE_SIZE), ({"max_message_size": 5 * 1024 * 1024}, 5 * 1024 * 1024)],
)
@pytest.mark.parametrize(
    "cls, factory",
    [(SendClient, "create_sender_link"), (ReceiveClient, "create_receiver_link")],
)
def test_link_max_message_size(cls, factory, kwargs, expected):
    client = cls("fake.host.com", "fake_eh", auth="my_fake_auth", **kwargs)
    client._session = Mock()

    assert client._client_ready() is False
    assert getattr(client._session, factory).call_args.kwargs["max_message_size"] == expected


@pytest.mark.parametrize(
    "kwargs, expected",
    [({}, 0), ({"max_message_size": 5 * 1024 * 1024}, 5 * 1024 * 1024)],
)
def test_receiver_attach_frame_max_message_size(kwargs, expected):
    client = ReceiveClient("fake.host.com", "fake_eh", auth="my_fake_auth", **kwargs)
    connection = Mock()
    client._session = Session(connection, 0, network_trace=False, network_trace_params={})

    assert client._client_ready() is False
    frame = connection._process_outgoing_frame.call_args.args[1]
    assert isinstance(frame, AttachFrame)
    assert frame.max_message_size == expected
