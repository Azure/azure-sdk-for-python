# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# pylint: disable=protected-access

"""Regression tests for pyAMQP Event Hubs session window accounting."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.eventhub._pyamqp._encode import encode_frame
from azure.eventhub._pyamqp.aio._session_async import Session as AsyncSession
from azure.eventhub._pyamqp.constants import SessionState
from azure.eventhub._pyamqp.session import Session


def _delivery():
    delivery = MagicMock(name="delivery")
    delivery.frame = {
        "payload": b"x",
        "handle": 0,
        "delivery_tag": b"tag",
        "message_format": 0,
        "settled": False,
        "rcv_settle_mode": None,
        "state": None,
        "resume": False,
        "aborted": False,
        "batchable": False,
    }
    return delivery


def test_outgoing_transfer_preserves_zero_local_outgoing_window():
    connection = MagicMock(name="connection")
    connection._remote_max_frame_size = 4096
    session = Session(
        connection,
        channel=0,
        incoming_window=4,
        outgoing_window=0,
        network_trace=False,
        network_trace_params={},
    )
    session.state = SessionState.MAPPED
    session.remote_incoming_window = 1

    session._outgoing_transfer(_delivery(), network_trace_params=None)
    session._outgoing_flow()

    assert session.outgoing_window == 0
    assert session.remote_incoming_window == 0
    assert session.next_outgoing_id == 1
    _, flow = connection._process_outgoing_frame.call_args.args
    assert flow.outgoing_window == 0
    encode_frame(flow)


@pytest.mark.asyncio
async def test_async_outgoing_transfer_preserves_zero_local_outgoing_window():
    connection = MagicMock(name="connection")
    connection._remote_max_frame_size = 4096
    connection._process_outgoing_frame = AsyncMock(name="_process_outgoing_frame")
    session = AsyncSession(
        connection,
        channel=0,
        incoming_window=4,
        outgoing_window=0,
        network_trace=False,
        network_trace_params={},
    )
    session.state = SessionState.MAPPED
    session.remote_incoming_window = 1

    await session._outgoing_transfer(_delivery(), network_trace_params=None)
    await session._outgoing_flow()

    assert session.outgoing_window == 0
    assert session.remote_incoming_window == 0
    assert session.next_outgoing_id == 1
    _, flow = connection._process_outgoing_frame.call_args.args
    assert flow.outgoing_window == 0
    encode_frame(flow)
