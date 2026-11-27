# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Receive-window recovery must preserve delivery order and session teardown."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.eventhub._pyamqp._encode import encode_frame
from azure.eventhub._pyamqp.aio._session_async import Session as AsyncSession
from azure.eventhub._pyamqp.constants import SessionState
from azure.eventhub._pyamqp.session import Session


def _session(initial_window, *, asynchronous=False):
    connection = MagicMock(name="connection")
    if asynchronous:
        connection._process_outgoing_frame = AsyncMock()
    session_type = AsyncSession if asynchronous else Session
    session = session_type(
        connection,
        channel=0,
        incoming_window=4,
        outgoing_window=4,
        network_trace=False,
        network_trace_params={},
    )
    session.state = SessionState.MAPPED
    session.incoming_window = initial_window
    session.next_incoming_id = 0
    session.remote_outgoing_window = 2
    link = MagicMock(name="link")
    if asynchronous:
        link._incoming_transfer = AsyncMock()
    session._input_handles[0] = link
    return session, connection, link


def _assert_replenished(session, connection):
    assert session.incoming_window == session.target_incoming_window == 4
    assert session.next_incoming_id == 1
    assert session.remote_outgoing_window == 1
    connection._process_outgoing_frame.assert_called_once()
    channel, flow = connection._process_outgoing_frame.call_args.args
    assert channel == 0
    assert flow.incoming_window == 4
    assert flow.next_incoming_id == 1
    encode_frame(flow)


@pytest.mark.parametrize("initial_window", [1, 0, -1, -255, -256])
def test_handler_failure_replenishes_receive_window(initial_window):
    session, connection, link = _session(initial_window)
    error = RuntimeError("handler failed")
    link._incoming_transfer.side_effect = error

    with pytest.raises(RuntimeError) as caught:
        session._incoming_transfer((0, b"payload"))

    assert caught.value is error
    assert session.state == SessionState.MAPPED
    link._incoming_transfer.assert_called_once_with((0, b"payload"))
    _assert_replenished(session, connection)


@pytest.mark.asyncio
@pytest.mark.parametrize("initial_window", [1, 0, -1, -255, -256])
async def test_async_handler_failure_replenishes_receive_window(initial_window):
    session, connection, link = _session(initial_window, asynchronous=True)
    error = RuntimeError("handler failed")
    link._incoming_transfer.side_effect = error

    with pytest.raises(RuntimeError) as caught:
        await session._incoming_transfer((0, b"payload"))

    assert caught.value is error
    assert session.state == SessionState.MAPPED
    link._incoming_transfer.assert_awaited_once_with((0, b"payload"))
    connection._process_outgoing_frame.assert_awaited_once()
    _assert_replenished(session, connection)


@pytest.mark.parametrize("initial_window", [1, 0, -1])
def test_unattached_handle_does_not_advertise_receive_capacity(initial_window):
    session, connection, _ = _session(initial_window)
    session._input_handles.clear()

    session._incoming_transfer((0, b"payload"))

    assert session.state == SessionState.DISCARDING
    assert session.incoming_window == initial_window - 1
    connection._process_outgoing_frame.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("initial_window", [1, 0, -1])
async def test_async_unattached_handle_does_not_advertise_receive_capacity(initial_window):
    session, connection, _ = _session(initial_window, asynchronous=True)
    session._input_handles.clear()

    await session._incoming_transfer((0, b"payload"))

    assert session.state == SessionState.DISCARDING
    assert session.incoming_window == initial_window - 1
    connection._process_outgoing_frame.assert_not_awaited()


@pytest.mark.parametrize("state", [SessionState.DISCARDING, SessionState.END_SENT, SessionState.UNMAPPED])
def test_handler_teardown_does_not_replenish(state):
    session, connection, link = _session(1)

    def teardown(_):
        session.state = state

    link._incoming_transfer.side_effect = teardown
    session._incoming_transfer((0, b"payload"))

    assert session.state == state
    assert session.incoming_window == 0
    connection._process_outgoing_frame.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("state", [SessionState.DISCARDING, SessionState.END_SENT, SessionState.UNMAPPED])
async def test_async_handler_teardown_does_not_replenish(state):
    session, connection, link = _session(1, asynchronous=True)

    async def teardown(_):
        session.state = state

    link._incoming_transfer.side_effect = teardown
    await session._incoming_transfer((0, b"payload"))

    assert session.state == state
    assert session.incoming_window == 0
    connection._process_outgoing_frame.assert_not_awaited()


def test_transfer_is_delivered_before_flow_failure():
    session, connection, link = _session(1)
    frame = (0, b"payload")

    def fail_flow(*_):
        link._incoming_transfer.assert_called_once_with(frame)
        raise OSError("flow failed")

    connection._process_outgoing_frame.side_effect = fail_flow
    with pytest.raises(OSError, match="flow failed"):
        session._incoming_transfer(frame)

    _assert_replenished(session, connection)


@pytest.mark.asyncio
async def test_transfer_is_delivered_before_flow_cancellation():
    session, connection, link = _session(1, asynchronous=True)
    frame = (0, b"payload")

    async def cancel_flow(*_):
        link._incoming_transfer.assert_awaited_once_with(frame)
        raise asyncio.CancelledError()

    connection._process_outgoing_frame.side_effect = cancel_flow
    with pytest.raises(asyncio.CancelledError):
        await session._incoming_transfer(frame)

    _assert_replenished(session, connection)


@pytest.mark.asyncio
async def test_handler_cancellation_is_propagated_after_replenishment():
    session, connection, link = _session(1, asynchronous=True)
    link._incoming_transfer.side_effect = asyncio.CancelledError()

    with pytest.raises(asyncio.CancelledError):
        await session._incoming_transfer((0, b"payload"))

    _assert_replenished(session, connection)


def test_positive_remaining_window_is_not_replenished():
    session, connection, link = _session(2)

    session._incoming_transfer((0, b"payload"))

    link._incoming_transfer.assert_called_once_with((0, b"payload"))
    assert session.incoming_window == 1
    connection._process_outgoing_frame.assert_not_called()


@pytest.mark.asyncio
async def test_async_positive_remaining_window_is_not_replenished():
    session, connection, link = _session(2, asynchronous=True)

    await session._incoming_transfer((0, b"payload"))

    link._incoming_transfer.assert_awaited_once_with((0, b"payload"))
    assert session.incoming_window == 1
    connection._process_outgoing_frame.assert_not_awaited()
