import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.eventhub._pyamqp._encode import (
    encode_frame,
    encode_ubyte,
    encode_uint,
    encode_ulong,
    encode_ushort,
)
from azure.eventhub._pyamqp.constants import SessionState, SessionTransferState
from azure.eventhub._pyamqp.performatives import FlowFrame, TransferFrame
from azure.eventhub._pyamqp.session import Session
from azure.eventhub._pyamqp.aio._session_async import Session as AsyncSession


def _delivery():
    return MagicMock(
        frame={
            "handle": 1,
            "delivery_tag": b"tag",
            "message_format": 0,
            "settled": False,
            "more": False,
            "rcv_settle_mode": None,
            "state": None,
            "resume": False,
            "aborted": False,
            "batchable": False,
            "payload": b"message",
        }
    )


def _session(session_type, async_connection=False, outgoing_window=2):
    connection = MagicMock()
    connection._remote_max_frame_size = 1024
    connection._process_outgoing_frame = (
        AsyncMock() if async_connection else MagicMock()
    )
    session = session_type(
        connection,
        1,
        outgoing_window=outgoing_window,
        incoming_window=5,
        network_trace=False,
        network_trace_params={},
    )
    session.state = SessionState.MAPPED
    session.remote_incoming_window = 10
    return session, connection


def _assert_transfers_and_credit(session, connection):
    frames = [
        call.args[1] for call in connection._process_outgoing_frame.call_args_list
    ]
    assert [type(frame) for frame in frames] == [
        TransferFrame,
        TransferFrame,
        FlowFrame,
        TransferFrame,
    ]
    assert frames[2].outgoing_window == 2
    assert frames[2].next_outgoing_id == 2
    encode_frame(frames[2])
    assert session.outgoing_window == 1
    assert session.remote_incoming_window == 7
    assert session.next_outgoing_id == 3


def test_outgoing_window_replenishes_after_transfers():
    session, connection = _session(Session)
    for _ in range(3):
        delivery = _delivery()
        session._outgoing_transfer(delivery, None)
        assert delivery.transfer_state == SessionTransferState.OKAY
    _assert_transfers_and_credit(session, connection)


@pytest.mark.asyncio
async def test_async_outgoing_window_replenishes_after_transfers():
    session, connection = _session(AsyncSession, async_connection=True)
    for _ in range(3):
        delivery = _delivery()
        await session._outgoing_transfer(delivery, None)
        assert delivery.transfer_state == SessionTransferState.OKAY
    _assert_transfers_and_credit(session, connection)


@pytest.mark.asyncio
async def test_concurrent_async_transfers_do_not_reuse_delivery_ids():
    session, connection = _session(
        AsyncSession, async_connection=True, outgoing_window=1
    )
    first_frame_started = asyncio.Event()
    release_first_frame = asyncio.Event()
    original_send = connection._process_outgoing_frame

    async def send_frame(channel, frame):
        if isinstance(frame, TransferFrame) and not first_frame_started.is_set():
            first_frame_started.set()
            await release_first_frame.wait()
        await original_send(channel, frame)

    connection._process_outgoing_frame = send_frame
    first = asyncio.create_task(session._outgoing_transfer(_delivery(), None))
    await first_frame_started.wait()
    second = asyncio.create_task(session._outgoing_transfer(_delivery(), None))
    await asyncio.sleep(0)
    release_first_frame.set()
    await asyncio.gather(first, second)
    transfers = [
        call.args[1]
        for call in original_send.call_args_list
        if isinstance(call.args[1], TransferFrame)
    ]
    assert [frame.delivery_id for frame in transfers] == [0, 1]
    assert session.outgoing_window == 1
    assert session.next_outgoing_id == 2


@pytest.mark.parametrize("async_session", [False, True])
@pytest.mark.asyncio
async def test_zero_outgoing_window_blocks_transfer(async_session):
    session, connection = _session(
        AsyncSession if async_session else Session,
        async_connection=async_session,
        outgoing_window=0,
    )
    delivery = _delivery()
    if async_session:
        await session._outgoing_transfer(delivery, None)
    else:
        session._outgoing_transfer(delivery, None)
    assert delivery.transfer_state == SessionTransferState.BUSY
    assert session.outgoing_window == 0
    connection._process_outgoing_frame.assert_not_called()


def test_replenished_window_stays_positive_across_reported_boundary():
    session, connection = _session(Session)
    session.remote_incoming_window = 300
    for _ in range(258):
        session._outgoing_transfer(_delivery(), None)
        assert session.outgoing_window in (1, 2)
    flows = [
        call.args[1]
        for call in connection._process_outgoing_frame.call_args_list
        if isinstance(call.args[1], FlowFrame)
    ]
    assert len(flows) == 129
    assert all(flow.outgoing_window == 2 for flow in flows)


@pytest.mark.parametrize(
    "encoder", [encode_ubyte, encode_ushort, encode_uint, encode_ulong]
)
@pytest.mark.parametrize("value", [-1, -255, -256])
def test_unsigned_encoders_reject_negative_values(encoder, value):
    output = bytearray()
    with pytest.raises(ValueError):
        encoder(output, value)
    assert not output


@pytest.mark.parametrize(
    "encoder,maximum",
    [
        (encode_ubyte, 255),
        (encode_ushort, 65535),
        (encode_uint, 4294967295),
        (encode_ulong, 18446744073709551615),
    ],
)
def test_unsigned_encoders_preserve_valid_boundaries(encoder, maximum):
    for value in (0, maximum):
        output = bytearray()
        encoder(output, value)
        assert output
    with pytest.raises(ValueError):
        encoder(bytearray(), maximum + 1)
