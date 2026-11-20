# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# pylint: disable=protected-access

"""Regression tests for pyAMQP session window accounting (azure-sdk-for-python#49232)."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.servicebus._pyamqp._encode import encode_uint, encode_ulong
from azure.servicebus._pyamqp.constants import SessionState
from azure.servicebus._pyamqp.session import Session
from azure.servicebus._pyamqp.aio._session_async import Session as AsyncSession


def _session(*, incoming_window=4, outgoing_window=4):
    connection = MagicMock(name="connection")
    connection._remote_max_frame_size = 4096
    session = Session(
        connection,
        channel=0,
        incoming_window=incoming_window,
        outgoing_window=outgoing_window,
        network_trace=False,
        network_trace_params={},
    )
    session.state = SessionState.MAPPED
    return session, connection


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


def test_outgoing_transfer_does_not_exhaust_local_outgoing_window():
    session, connection = _session(outgoing_window=1)
    session.remote_incoming_window = 1

    session._outgoing_transfer(_delivery(), network_trace_params=None)

    assert session.outgoing_window == 1
    assert session.remote_incoming_window == 0
    assert session.next_outgoing_id == 1
    assert connection._process_outgoing_frame.call_count == 1


@pytest.mark.asyncio
async def test_async_outgoing_transfer_does_not_exhaust_local_outgoing_window():
    connection = MagicMock(name="connection")
    connection._remote_max_frame_size = 4096
    connection._process_outgoing_frame = AsyncMock(name="_process_outgoing_frame")
    session = AsyncSession(
        connection,
        channel=0,
        incoming_window=4,
        outgoing_window=1,
        network_trace=False,
        network_trace_params={},
    )
    session.state = SessionState.MAPPED
    session.remote_incoming_window = 1

    await session._outgoing_transfer(_delivery(), network_trace_params=None)

    assert session.outgoing_window == 1
    assert session.remote_incoming_window == 0
    assert session.next_outgoing_id == 1
    connection._process_outgoing_frame.assert_awaited_once()


def test_incoming_window_recovers_before_transfer_handler_exception():
    session, connection = _session(incoming_window=1)
    session.next_incoming_id = 0
    session.remote_outgoing_window = 2

    link = MagicMock(name="link")
    link._incoming_transfer.side_effect = RuntimeError("handler failed")
    session._input_handles[0] = link

    with pytest.raises(RuntimeError, match="handler failed"):
        session._incoming_transfer((0,))

    assert session.incoming_window == session.target_incoming_window == 1
    assert connection._process_outgoing_frame.call_count == 1


def test_negative_incoming_window_recovers_before_transfer_handler_exception():
    session, connection = _session(incoming_window=1)
    session.incoming_window = 0
    session.next_incoming_id = 0
    session.remote_outgoing_window = 2

    link = MagicMock(name="link")
    link._incoming_transfer.side_effect = RuntimeError("handler failed")
    session._input_handles[0] = link

    with pytest.raises(RuntimeError, match="handler failed"):
        session._incoming_transfer((0,))

    assert session.incoming_window == session.target_incoming_window == 1
    assert connection._process_outgoing_frame.call_count == 1


@pytest.mark.parametrize(("initial_window", "expected_window"), [(1, 0), (0, -1)])
def test_incoming_transfer_does_not_replenish_when_discarding(initial_window, expected_window):
    session, connection = _session(incoming_window=1)
    session.incoming_window = initial_window
    session.next_incoming_id = 0
    session.remote_outgoing_window = 2

    session._incoming_transfer((0,))

    assert session.state == SessionState.DISCARDING
    assert session.incoming_window == expected_window
    connection._process_outgoing_frame.assert_not_called()


def test_incoming_transfer_replenishes_after_successful_delivery():
    session, connection = _session(incoming_window=1)
    session.next_incoming_id = 0
    session.remote_outgoing_window = 2
    frame = (0, b"payload")

    link = MagicMock(name="link")
    session._input_handles[0] = link

    session._incoming_transfer(frame)

    link._incoming_transfer.assert_called_once_with(frame)
    assert session.state == SessionState.MAPPED
    assert session.incoming_window == session.target_incoming_window == 1
    connection._process_outgoing_frame.assert_called_once()


@pytest.mark.asyncio
async def test_async_incoming_window_recovers_before_transfer_handler_exception():
    connection = MagicMock(name="connection")
    connection._process_outgoing_frame = AsyncMock(name="_process_outgoing_frame")
    session = AsyncSession(
        connection,
        channel=0,
        incoming_window=1,
        outgoing_window=4,
        network_trace=False,
        network_trace_params={},
    )
    session.state = SessionState.MAPPED
    session.next_incoming_id = 0
    session.remote_outgoing_window = 2

    link = MagicMock(name="link")
    link._incoming_transfer = AsyncMock(side_effect=RuntimeError("handler failed"))
    session._input_handles[0] = link

    with pytest.raises(RuntimeError, match="handler failed"):
        await session._incoming_transfer((0,))

    assert session.incoming_window == session.target_incoming_window == 1
    connection._process_outgoing_frame.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(("initial_window", "expected_window"), [(1, 0), (0, -1)])
async def test_async_incoming_transfer_does_not_replenish_when_discarding(initial_window, expected_window):
    connection = MagicMock(name="connection")
    connection._process_outgoing_frame = AsyncMock(name="_process_outgoing_frame")
    session = AsyncSession(
        connection,
        channel=0,
        incoming_window=1,
        outgoing_window=4,
        network_trace=False,
        network_trace_params={},
    )
    session.state = SessionState.MAPPED
    session.incoming_window = initial_window
    session.next_incoming_id = 0
    session.remote_outgoing_window = 2

    await session._incoming_transfer((0,))

    assert session.state == SessionState.DISCARDING
    assert session.incoming_window == expected_window
    connection._process_outgoing_frame.assert_not_awaited()


@pytest.mark.asyncio
async def test_async_incoming_transfer_replenishes_after_successful_delivery():
    connection = MagicMock(name="connection")
    connection._process_outgoing_frame = AsyncMock(name="_process_outgoing_frame")
    session = AsyncSession(
        connection,
        channel=0,
        incoming_window=1,
        outgoing_window=4,
        network_trace=False,
        network_trace_params={},
    )
    session.state = SessionState.MAPPED
    session.next_incoming_id = 0
    session.remote_outgoing_window = 2
    frame = (0, b"payload")

    link = MagicMock(name="link")
    link._incoming_transfer = AsyncMock(name="_incoming_transfer")
    session._input_handles[0] = link

    await session._incoming_transfer(frame)

    link._incoming_transfer.assert_awaited_once_with(frame)
    assert session.state == SessionState.MAPPED
    assert session.incoming_window == session.target_incoming_window == 1
    connection._process_outgoing_frame.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_negative_incoming_window_recovers_before_transfer_handler_exception():
    connection = MagicMock(name="connection")
    connection._process_outgoing_frame = AsyncMock(name="_process_outgoing_frame")
    session = AsyncSession(
        connection,
        channel=0,
        incoming_window=1,
        outgoing_window=4,
        network_trace=False,
        network_trace_params={},
    )
    session.state = SessionState.MAPPED
    session.incoming_window = 0
    session.next_incoming_id = 0
    session.remote_outgoing_window = 2

    link = MagicMock(name="link")
    link._incoming_transfer = AsyncMock(side_effect=RuntimeError("handler failed"))
    session._input_handles[0] = link

    with pytest.raises(RuntimeError, match="handler failed"):
        await session._incoming_transfer((0,))

    assert session.incoming_window == session.target_incoming_window == 1
    connection._process_outgoing_frame.assert_awaited_once()


@pytest.mark.parametrize("encoder", [encode_uint, encode_ulong])
@pytest.mark.parametrize("value", [-1, -255, -256])
def test_unsigned_encoders_reject_negative_values(encoder, value):
    with pytest.raises(ValueError, match="invalid"):
        encoder(bytearray(), value)


@pytest.mark.asyncio
async def test_async_incoming_transfer_delivered_before_flow_cancellation():
    """Transfer must reach the link even if replenish flow is cancelled."""
    connection = MagicMock(name="connection")
    connection._process_outgoing_frame = AsyncMock(name="_process_outgoing_frame")
    session = AsyncSession(
        connection,
        channel=0,
        incoming_window=1,
        outgoing_window=4,
        network_trace=False,
        network_trace_params={},
    )
    session.state = SessionState.MAPPED
    session.next_incoming_id = 0
    session.remote_outgoing_window = 2

    delivered = []

    async def deliver(frame):
        delivered.append(frame)

    link = MagicMock(name="link")
    link._incoming_transfer = AsyncMock(side_effect=deliver)
    session._input_handles[0] = link

    async def cancel_flow(frame=None):
        raise asyncio.CancelledError()

    session._outgoing_flow = cancel_flow  # type: ignore

    with pytest.raises(asyncio.CancelledError):
        await session._incoming_transfer((0, b"payload"))

    assert delivered == [(0, b"payload")]
    assert session.state == SessionState.MAPPED
    assert session.incoming_window == session.target_incoming_window == 1
