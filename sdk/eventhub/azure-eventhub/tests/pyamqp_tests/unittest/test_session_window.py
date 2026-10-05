import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from threading import Event
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.eventhub._pyamqp._encode import (
    encode_frame,
    encode_ubyte,
    encode_uint,
    encode_ulong,
    encode_ushort,
)
from azure.eventhub._pyamqp.constants import (
    LinkDeliverySettleReason,
    LinkState,
    SenderSettleMode,
    SessionState,
    SessionTransferState,
)
from azure.eventhub._pyamqp.performatives import FlowFrame, TransferFrame
from azure.eventhub._pyamqp.error import MessageException
from azure.eventhub._pyamqp.session import Session
from azure.eventhub._pyamqp.sender import SenderLink
from azure.eventhub._pyamqp.aio._session_async import Session as AsyncSession
from azure.eventhub._pyamqp.aio._sender_async import SenderLink as AsyncSenderLink


def _delivery():
    return MagicMock(
        abort_requested=False,
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


@pytest.mark.asyncio
async def test_async_flow_waits_for_transfer_accounting():
    session, connection = _session(AsyncSession, async_connection=True)
    started, release = asyncio.Event(), asyncio.Event()
    send = connection._process_outgoing_frame

    async def send_frame(channel, frame):
        if isinstance(frame, TransferFrame):
            started.set()
            await release.wait()
        await send(channel, frame)

    connection._process_outgoing_frame = send_frame
    transfer = asyncio.create_task(session._outgoing_transfer(_delivery(), None))
    try:
        await asyncio.wait_for(started.wait(), 5)
        flow = asyncio.create_task(session._outgoing_flow({"handle": 2}))
        await asyncio.sleep(0)
        assert not flow.done()
    finally:
        release.set()
    await asyncio.gather(transfer, flow)
    frames = [call.args[1] for call in send.call_args_list]
    assert [type(frame) for frame in frames] == [TransferFrame, FlowFrame]
    assert frames[1].next_outgoing_id == 1


def test_sync_flow_waits_for_transfer_accounting():
    session, connection = _session(Session)
    started, release = Event(), Event()
    send = connection._process_outgoing_frame

    def send_frame(channel, frame):
        if isinstance(frame, TransferFrame):
            started.set()
            assert release.wait(5)
        send(channel, frame)

    connection._process_outgoing_frame = send_frame
    with ThreadPoolExecutor(max_workers=2) as pool:
        transfer = pool.submit(session._outgoing_transfer, _delivery(), None)
        try:
            assert started.wait(5)
            flow = pool.submit(session._outgoing_flow, {"handle": 2})
            assert not flow.done()
        finally:
            release.set()
        transfer.result(timeout=5)
        flow.result(timeout=5)
    frames = [call.args[1] for call in send.call_args_list]
    assert [type(frame) for frame in frames] == [TransferFrame, FlowFrame]
    assert frames[1].next_outgoing_id == 1


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


@pytest.mark.parametrize("async_session", [False, True])
@pytest.mark.asyncio
async def test_fragmented_transfer_replenishes_per_frame_and_waits_for_remote_credit(
    async_session,
):
    session, connection = _session(
        AsyncSession if async_session else Session,
        async_connection=async_session,
        outgoing_window=1,
    )
    delivery = _delivery()
    payload = b"abcdefg"
    delivery.frame["delivery_id"] = 0
    delivery.frame["payload"] = b""
    overhead = len(encode_frame(TransferFrame(**delivery.frame))[1])
    connection._remote_max_frame_size = overhead + 8 + 3
    delivery.frame["payload"] = payload
    session.remote_incoming_window = 1

    for remaining, expected_id in ((b"defg", 1), (b"g", 2), (b"", 3)):
        if async_session:
            await session._outgoing_transfer(delivery, None)
        else:
            session._outgoing_transfer(delivery, None)
        assert delivery.frame["payload"] == remaining
        assert session.next_outgoing_id == expected_id
        assert session.remote_incoming_window == 0
        assert session.outgoing_window == 1
        if remaining:
            assert delivery.transfer_state == SessionTransferState.BUSY
            assert delivery.frame["more"]
            assert isinstance(delivery.frame["payload"], memoryview)
            assert delivery.frame["payload"].obj is payload
            session.remote_incoming_window = 1
        else:
            assert delivery.transfer_state == SessionTransferState.OKAY
            assert not delivery.frame["more"]
            assert delivery.frame["payload"] == b""
            assert not isinstance(delivery.frame["payload"], memoryview)

    frames = [
        call.args[1] for call in connection._process_outgoing_frame.call_args_list
    ]
    transfers = [frame for frame in frames if isinstance(frame, TransferFrame)]
    flows = [frame for frame in frames if isinstance(frame, FlowFrame)]
    assert b"".join(frame.payload for frame in transfers) == payload
    assert [frame.delivery_id for frame in transfers] == [0, 0, 0]
    assert [frame.more for frame in transfers] == [True, True, False]
    assert all(isinstance(frame.payload, memoryview) and frame.payload.obj is payload for frame in transfers)
    assert [frame.next_outgoing_id for frame in flows] == [1, 2, 3]


def _sender(monkeypatch, async_session):
    from azure.eventhub._pyamqp import sender as sender_module
    from azure.eventhub._pyamqp.aio import _sender_async as async_sender_module

    sender_type = AsyncSenderLink if async_session else SenderLink
    monkeypatch.setattr(
        async_sender_module if async_session else sender_module,
        "encode_payload",
        lambda output, message: output.extend(message.payload),
    )
    session, connection = _session(
        AsyncSession if async_session else Session,
        async_connection=async_session,
        outgoing_window=1,
    )
    connection._remote_max_frame_size = 80
    session.remote_incoming_window = 1
    sender = sender_type.__new__(sender_type)
    sender._session = session
    sender.handle = 1
    sender.delivery_count = 0
    sender.current_link_credit = 10
    sender.network_trace = False
    sender.network_trace_params = {}
    sender._pending_deliveries = []
    if async_session:
        sender._updating_deliveries = False
        sender._update_requested = False
    sender._is_closed = False
    sender.state = LinkState.ATTACHED
    sender.send_settle_mode = SenderSettleMode.Mixed
    if not async_session:
        sender.lock = Lock()
    return sender, session, connection


@pytest.mark.parametrize("async_session", [False, True])
@pytest.mark.asyncio
async def test_sender_resumes_partial_delivery_before_sending_next(
    monkeypatch, async_session
):
    sender, session, connection = _sender(monkeypatch, async_session)

    message = MagicMock(_code=0, payload=b"a" * 120)
    if async_session:
        first = await sender.send_transfer(message)
        second = await sender.send_transfer(MagicMock(_code=0, payload=b"next"))
    else:
        first = sender.send_transfer(message)
        second = sender.send_transfer(MagicMock(_code=0, payload=b"next"))
    assert first.transfer_state == SessionTransferState.BUSY
    assert first.frame["more"]
    assert second.frame is None

    for _ in range(20):
        session.remote_incoming_window = 1
        if async_session:
            await sender.update_pending_deliveries()
        else:
            sender.update_pending_deliveries()
        if first.sent and second.sent:
            break
    assert first.sent and second.sent
    transfers = [
        call.args[1]
        for call in connection._process_outgoing_frame.call_args_list
        if isinstance(call.args[1], TransferFrame)
    ]
    assert b"".join(frame.payload for frame in transfers[:-1]) == message.payload
    assert transfers[-1].payload == b"next"
    assert {frame.delivery_id for frame in transfers[:-1]} == {0}
    assert transfers[-1].delivery_id == len(transfers) - 1
    assert [frame.delivery_tag for frame in transfers[:-1]] == [
        transfers[0].delivery_tag
    ] * (len(transfers) - 1)


@pytest.mark.asyncio
async def test_concurrent_async_sends_preserve_partial_delivery_order(monkeypatch):
    sender, session, connection = _sender(monkeypatch, True)
    started, release = asyncio.Event(), asyncio.Event()
    send = connection._process_outgoing_frame

    async def send_frame(channel, frame):
        if isinstance(frame, TransferFrame) and not started.is_set():
            started.set()
            await release.wait()
        await send(channel, frame)

    connection._process_outgoing_frame = send_frame
    first_task = asyncio.create_task(sender.send_transfer(MagicMock(_code=0, payload=b"a" * 120)))
    try:
        await asyncio.wait_for(started.wait(), 5)
        second = await sender.send_transfer(MagicMock(_code=0, payload=b"next"))
        assert second.frame is None
        assert len(sender._pending_deliveries) == 2
    finally:
        release.set()
    first = await first_task
    for _ in range(20):
        session.remote_incoming_window = 1
        await sender.update_pending_deliveries()
        if second.sent:
            break
    assert first.sent and second.sent
    transfers = [call.args[1] for call in send.call_args_list if isinstance(call.args[1], TransferFrame)]
    assert {frame.delivery_id for frame in transfers[:-1]} == {0}
    assert transfers[-1].delivery_id == len(transfers) - 1
    assert transfers[-1].payload == b"next"


@pytest.mark.asyncio
@pytest.mark.parametrize("final_frame", [False, True])
async def test_cancellation_during_async_transfer_write(monkeypatch, final_frame):
    sender, session, connection = _sender(monkeypatch, True)
    if final_frame:
        connection._remote_max_frame_size = 1024
    else:
        session.remote_incoming_window = 10
    started, release = asyncio.Event(), asyncio.Event()
    send = connection._process_outgoing_frame
    transfer_count = 0
    reasons = []

    async def send_frame(channel, frame):
        nonlocal transfer_count
        if isinstance(frame, TransferFrame):
            transfer_count += 1
            if transfer_count == (1 if final_frame else 2):
                assert frame.more is not final_frame
                started.set()
                await release.wait()
        await send(channel, frame)

    async def completed(reason, _state):
        reasons.append(reason)

    connection._process_outgoing_frame = send_frame
    task = asyncio.create_task(
        sender.send_transfer(MagicMock(_code=0, payload=b"a" * 120), settled=False, on_send_complete=completed)
    )
    try:
        await asyncio.wait_for(started.wait(), 5)
        delivery = sender._pending_deliveries[0]
        if final_frame:
            with pytest.raises(MessageException, match="already in flight"):
                await sender.cancel_transfer(delivery)
        else:
            await sender.cancel_transfer(delivery)
            assert reasons == [LinkDeliverySettleReason.CANCELLED]
    finally:
        release.set()
    await task
    transfers = [call.args[1] for call in send.call_args_list if isinstance(call.args[1], TransferFrame)]
    if final_frame:
        assert delivery.sent and not any(frame.aborted for frame in transfers)
    else:
        assert len([frame for frame in transfers if frame.aborted]) == 1
        assert transfers[-1].aborted and transfers[-1].delivery_id == transfers[0].delivery_id
        assert not delivery.frame["payload"]
        assert reasons == [LinkDeliverySettleReason.CANCELLED]


@pytest.mark.parametrize("async_session", [False, True])
@pytest.mark.parametrize("termination", ["timeout", "cancel"])
@pytest.mark.asyncio
async def test_partial_delivery_aborts_before_next_and_checks_later_timeouts(
    monkeypatch, async_session, termination
):
    sender, session, connection = _sender(monkeypatch, async_session)
    reasons = []

    def completed(reason, _state):
        reasons.append(reason)

    async def completed_async(reason, state):
        completed(reason, state)

    callback = completed_async if async_session else completed
    send = sender.send_transfer
    if async_session:
        first = await send(MagicMock(_code=0, payload=b"a" * 120), settled=False, on_send_complete=callback)
        expired = await send(
            MagicMock(_code=0, payload=b"expired"), send_async=True, timeout=1,
            settled=False, on_send_complete=callback,
        )
        next_delivery = await send(MagicMock(_code=0, payload=b"next"), send_async=True)
    else:
        first = send(MagicMock(_code=0, payload=b"a" * 120), settled=False, on_send_complete=callback)
        expired = send(
            MagicMock(_code=0, payload=b"expired"), send_async=True, timeout=1,
            settled=False, on_send_complete=callback,
        )
        next_delivery = send(MagicMock(_code=0, payload=b"next"), send_async=True)

    assert first.frame["more"] and not first.sent
    if termination == "timeout":
        first.timeout = 1
        first.start -= 10
    else:
        if async_session:
            await sender.cancel_transfer(first)
        else:
            sender.cancel_transfer(first)
    expired.start -= 10

    if async_session:
        await sender.update_pending_deliveries()
    else:
        sender.update_pending_deliveries()
    assert reasons == [
        LinkDeliverySettleReason.TIMEOUT if termination == "timeout" else LinkDeliverySettleReason.CANCELLED,
        LinkDeliverySettleReason.TIMEOUT,
    ]
    assert first.abort_pending
    assert first in sender._pending_deliveries
    assert expired not in sender._pending_deliveries
    assert next_delivery.frame is None

    for _ in range(20):
        session.remote_incoming_window = 1
        if async_session:
            await sender.update_pending_deliveries()
        else:
            sender.update_pending_deliveries()
        if next_delivery.sent:
            break
    assert next_delivery.sent
    assert first not in sender._pending_deliveries
    assert len(reasons) == 2
    transfers = [
        call.args[1]
        for call in connection._process_outgoing_frame.call_args_list
        if isinstance(call.args[1], TransferFrame)
    ]
    aborted = [frame for frame in transfers if frame.aborted]
    assert len(aborted) == 1
    assert aborted[0].delivery_id == transfers[0].delivery_id
    assert aborted[0].payload == b""
    assert not aborted[0].more
    assert transfers[-1].payload == b"next"
    assert transfers[-1].delivery_id == len(transfers) - 1


@pytest.mark.parametrize("async_session", [False, True])
@pytest.mark.asyncio
async def test_later_delivery_times_out_while_first_waits_for_credit(
    monkeypatch, async_session
):
    sender, _session, _connection = _sender(monkeypatch, async_session)
    reasons = []

    async def completed_async(reason, _state):
        reasons.append(reason)

    def completed(reason, _state):
        reasons.append(reason)

    callback = completed_async if async_session else completed
    if async_session:
        first = await sender.send_transfer(MagicMock(_code=0, payload=b"a" * 120), settled=False)
        later = await sender.send_transfer(
            MagicMock(_code=0, payload=b"later"), send_async=True, settled=False,
            timeout=1, on_send_complete=callback,
        )
    else:
        first = sender.send_transfer(MagicMock(_code=0, payload=b"a" * 120), settled=False)
        later = sender.send_transfer(
            MagicMock(_code=0, payload=b"later"), send_async=True, settled=False,
            timeout=1, on_send_complete=callback,
        )
    later.start -= 10
    if async_session:
        await sender.update_pending_deliveries()
    else:
        sender.update_pending_deliveries()
    assert reasons == [LinkDeliverySettleReason.TIMEOUT]
    assert sender._pending_deliveries == [first]
    assert first.frame["more"] and not first.abort_pending


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
    match = "Unsigned short value must be 0-65535" if encoder == encode_ushort else None
    with pytest.raises(ValueError, match=match):
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
    match = "Unsigned short value must be 0-65535" if encoder == encode_ushort else None
    with pytest.raises(ValueError, match=match):
        encoder(bytearray(), maximum + 1)
