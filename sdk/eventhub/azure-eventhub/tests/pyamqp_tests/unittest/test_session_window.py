import asyncio
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from threading import RLock
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
    ConnectionState,
    LinkDeliverySettleReason,
    LinkState,
    ManagementExecuteOperationResult,
    SEND_DISPOSITION_REJECT,
    SenderSettleMode,
    SessionState,
    SessionTransferState,
)
from azure.eventhub._pyamqp.performatives import FlowFrame, TransferFrame
from azure.eventhub._pyamqp.error import AMQPConnectionError, MessageException
from azure.eventhub._pyamqp.session import Session
from azure.eventhub._pyamqp.sender import SenderLink
from azure.eventhub._pyamqp.management_link import ManagementLink
from azure.eventhub._pyamqp.message import Message
from azure.eventhub._pyamqp.aio._management_link_async import ManagementLink as AsyncManagementLink
from azure.eventhub._pyamqp.aio._connection_async import Connection as AsyncConnection
from azure.eventhub._pyamqp.aio._session_async import Session as AsyncSession
from azure.eventhub._pyamqp.aio._sender_async import SenderLink as AsyncSenderLink


def _delivery():
    return MagicMock(
        abort_requested=False,
        cancel_requested=False,
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


def test_sync_incoming_flow_accounts_before_outgoing_lock_wait():
    session, _ = _session(Session)
    session.next_incoming_id = None
    session.remote_outgoing_window = 0
    session._input_handles[1] = MagicMock()
    lock = session._outgoing_transfer_lock
    attempting = Event()

    class ObservedLock:
        def __enter__(self):
            attempting.set()
            lock.acquire()

        def __exit__(self, exc_type, exc_value, traceback):
            lock.release()

    session._outgoing_transfer_lock = ObservedLock()
    with ThreadPoolExecutor(max_workers=1) as executor:
        with lock:
            flow = executor.submit(session._incoming_flow, [0, 10, 0, 5, None])
            assert attempting.wait(5)
            session._incoming_transfer([1])
            assert session.next_incoming_id == 1
            assert session.remote_outgoing_window == 4
        flow.result(timeout=5)
    assert session.remote_incoming_window == 10


@pytest.mark.asyncio
async def test_async_incoming_flow_accounts_before_outgoing_lock_wait():
    session, _ = _session(AsyncSession, async_connection=True)
    session.next_incoming_id = None
    session.remote_outgoing_window = 0
    session._input_handles[1] = MagicMock(_incoming_transfer=AsyncMock())
    async with session._outgoing_transfer_lock:
        flow = asyncio.create_task(session._incoming_flow([0, 10, 0, 5, None]))
        await asyncio.sleep(0)
        await session._incoming_transfer([1])
        assert session.next_incoming_id == 1
        assert session.remote_outgoing_window == 4
    await flow
    assert session.remote_incoming_window == 10


@pytest.mark.parametrize("async_session", [False, True])
@pytest.mark.asyncio
async def test_zero_next_incoming_id_does_not_grant_extra_credit(async_session):
    session, _ = _session(AsyncSession if async_session else Session, async_connection=async_session)
    if async_session:
        async with session._outgoing_transfer_lock:
            flow = asyncio.create_task(session._incoming_flow([0, 1, 0, 5, None]))
            await asyncio.sleep(0)
            await session._outgoing_transfer_locked(_delivery(), None)
        await flow
    else:
        with ThreadPoolExecutor(max_workers=1) as executor:
            with session._outgoing_transfer_lock:
                flow = executor.submit(session._incoming_flow, [0, 1, 0, 5, None])
                session._outgoing_transfer_locked(_delivery(), None)
            flow.result(timeout=5)
    assert session.next_outgoing_id == 1
    assert session.remote_incoming_window == 0


@pytest.mark.parametrize("early_ack", [False, True])
def test_sync_flow_failure_preserves_completed_transfer(monkeypatch, early_ack):
    sender, session, connection = _sender(monkeypatch, False)
    connection._remote_max_frame_size = 1024
    written, reasons = [], []
    send = connection._process_outgoing_frame

    def completed(reason, state):
        reasons.append((reason, state))

    def send_frame(channel, frame):
        if isinstance(frame, FlowFrame):
            raise RuntimeError("Flow failed")
        written.append(frame)
        send(channel, frame)
        if early_ack:
            sender._incoming_disposition([None, frame.delivery_id, None, True, b"accepted"])

    connection._process_outgoing_frame = send_frame
    delivery = sender.send_transfer(
        MagicMock(_code=0, payload=b"message"),
        send_async=True, settled=False, on_send_complete=completed
    )
    with pytest.raises(RuntimeError, match="Flow failed"):
        sender.update_pending_deliveries()
    assert delivery.transfer_state == SessionTransferState.OKAY and delivery.sent
    assert sender.delivery_count == 1 and sender.current_link_credit == 9
    assert reasons == ([(LinkDeliverySettleReason.DISPOSITION_RECEIVED, b"accepted")] if early_ack else [])
    assert (delivery in sender._pending_deliveries) is not early_ack
    sender.update_pending_deliveries()
    assert len(written) == 1 and session.next_outgoing_id == 1
    assert reasons == ([(LinkDeliverySettleReason.DISPOSITION_RECEIVED, b"accepted")] if early_ack else [])


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


@pytest.mark.parametrize("partial", [False, True])
@pytest.mark.parametrize("failure", ["raise", "connection_error"])
def test_sync_failed_transfer_write_is_not_retried(monkeypatch, partial, failure):
    sender, session, connection = _sender(monkeypatch, False)
    if not partial:
        connection._remote_max_frame_size = 1024
    session.remote_incoming_window = 10
    connection._error = None
    send = connection._process_outgoing_frame
    transfers = []

    def send_frame(channel, frame):
        if isinstance(frame, TransferFrame):
            transfers.append(frame)
            if len(transfers) == (2 if partial else 1):
                if failure == "raise":
                    raise RuntimeError("Transfer write failed")
                connection._error = RuntimeError("Transfer write failed")
                return
        send(channel, frame)

    connection._process_outgoing_frame = send_frame
    with pytest.raises(RuntimeError, match="Transfer write failed"):
        sender.send_transfer(MagicMock(_code=0, payload=b"a" * 120), settled=False)
    assert session.state == SessionState.DISCARDING
    connection._disconnect.assert_called_once()
    assert not sender._pending_deliveries
    written_before_drain = len(transfers)
    sender.update_pending_deliveries()
    assert len(transfers) == written_before_drain


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
        sender.lock = RLock()
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


@pytest.mark.asyncio
async def test_concurrent_partial_cancellations_notify_once(monkeypatch):
    sender, session, connection = _sender(monkeypatch, True)
    session.remote_incoming_window = 10
    write_started, write_release = asyncio.Event(), asyncio.Event()
    callback_started, callback_release = asyncio.Event(), asyncio.Event()
    send = connection._process_outgoing_frame
    callbacks = []
    writes = 0

    async def send_frame(channel, frame):
        nonlocal writes
        if isinstance(frame, TransferFrame):
            writes += 1
            if writes == 2:
                write_started.set()
                await write_release.wait()
        await send(channel, frame)

    async def completed(reason, _state):
        callbacks.append(reason)
        callback_started.set()
        await callback_release.wait()

    connection._process_outgoing_frame = send_frame
    sending = asyncio.create_task(sender.send_transfer(
        MagicMock(_code=0, payload=b"a" * 120), settled=False, on_send_complete=completed
    ))
    try:
        await asyncio.wait_for(write_started.wait(), 5)
        delivery = sender._pending_deliveries[0]
        cancelling = asyncio.create_task(sender.cancel_transfer(delivery))
        await asyncio.wait_for(callback_started.wait(), 5)
        with pytest.raises(MessageException, match="already pending"):
            await sender.cancel_transfer(delivery)
    finally:
        callback_release.set()
        write_release.set()
    await cancelling
    await sending
    assert callbacks == [LinkDeliverySettleReason.CANCELLED]
    transfers = [call.args[1] for call in send.call_args_list if isinstance(call.args[1], TransferFrame)]
    assert len([frame for frame in transfers if frame.aborted]) == 1


@pytest.mark.parametrize("partial", [False, True])
@pytest.mark.asyncio
async def test_cancel_during_timeout_callback_does_not_notify_twice(monkeypatch, partial):
    sender, session, connection = _sender(monkeypatch, True)
    started, release = asyncio.Event(), asyncio.Event()
    reasons = []

    async def completed(reason, _state):
        reasons.append(reason)
        started.set()
        await release.wait()

    if partial:
        first = await sender.send_transfer(
            MagicMock(_code=0, payload=b"a" * 120), settled=False, on_send_complete=completed
        )
        assert first.frame["more"]
        session.remote_incoming_window = 10
    else:
        first = await sender.send_transfer(
            MagicMock(_code=0, payload=b"message"), send_async=True, settled=False, on_send_complete=completed
        )
    first.timeout = 1
    first.start -= 10
    draining = asyncio.create_task(sender.update_pending_deliveries())
    try:
        await asyncio.wait_for(started.wait(), 5)
        with pytest.raises((ValueError, MessageException)):
            await sender.cancel_transfer(first)
    finally:
        release.set()
    await draining
    assert reasons == [LinkDeliverySettleReason.TIMEOUT]
    transfers = [call.args[1] for call in connection._process_outgoing_frame.call_args_list
                 if isinstance(call.args[1], TransferFrame)]
    assert len([frame for frame in transfers if frame.aborted]) == int(partial)


@pytest.mark.asyncio
async def test_disposition_during_async_send_preserves_queued_deliveries(monkeypatch):
    sender, session, connection = _sender(monkeypatch, True)
    connection._remote_max_frame_size = 1024
    session.remote_incoming_window = 10
    first = await sender.send_transfer(MagicMock(_code=0, payload=b"first"), settled=False)
    started, release = asyncio.Event(), asyncio.Event()
    send = connection._process_outgoing_frame

    async def send_frame(channel, frame):
        if isinstance(frame, TransferFrame) and frame.delivery_id == 1:
            started.set()
            await release.wait()
        await send(channel, frame)

    connection._process_outgoing_frame = send_frame
    task = asyncio.create_task(sender.send_transfer(MagicMock(_code=0, payload=b"second")))
    try:
        await asyncio.wait_for(started.wait(), 5)
        queued = await sender.send_transfer(MagicMock(_code=0, payload=b"third"), send_async=True, settled=False)
        await sender._incoming_disposition([None, first.frame["delivery_id"], None, True, None])
        assert first not in sender._pending_deliveries
    finally:
        release.set()
    await task
    assert queued.sent and queued in sender._pending_deliveries
    assert [bytes(frame.payload) for frame in (call.args[1] for call in send.call_args_list)
            if isinstance(frame, TransferFrame)] == [b"first", b"second", b"third"]


@pytest.mark.asyncio
async def test_async_encoding_failure_does_not_block_next_send(monkeypatch):
    from azure.eventhub._pyamqp.aio import _sender_async as async_sender_module

    sender, session, connection = _sender(monkeypatch, True)
    session.remote_incoming_window = 10
    connection._remote_max_frame_size = 1024

    def encode(output, message):
        if message.payload == b"bad":
            raise ValueError("Unsupported message value")
        output.extend(message.payload)

    monkeypatch.setattr(async_sender_module, "encode_payload", encode)
    with pytest.raises(ValueError, match="Unsupported message value"):
        await sender.send_transfer(MagicMock(_code=0, payload=b"bad"))
    assert not sender._pending_deliveries
    good = await sender.send_transfer(MagicMock(_code=0, payload=b"good"), settled=False)
    assert good.sent and good in sender._pending_deliveries


@pytest.mark.asyncio
async def test_failed_older_queued_delivery_withdraws_immediate_caller(monkeypatch):
    from azure.eventhub._pyamqp.aio import _sender_async as async_sender_module

    sender, session, connection = _sender(monkeypatch, True)
    session.remote_incoming_window = 10
    connection._remote_max_frame_size = 1024

    def encode(output, message):
        if message.payload == b"bad":
            raise ValueError("Unsupported message value")
        output.extend(message.payload)

    monkeypatch.setattr(async_sender_module, "encode_payload", encode)
    bad = await sender.send_transfer(MagicMock(_code=0, payload=b"bad"), send_async=True)
    with pytest.raises(ValueError, match="Unsupported message value"):
        await sender.send_transfer(MagicMock(_code=0, payload=b"good"))
    assert bad not in sender._pending_deliveries
    assert not sender._pending_deliveries
    await sender.update_pending_deliveries()
    assert not [call for call in connection._process_outgoing_frame.call_args_list
                if isinstance(call.args[1], TransferFrame)]


@pytest.mark.asyncio
async def test_frame_write_failure_marks_delivery_failed(monkeypatch):
    sender, session, connection = _sender(monkeypatch, True)
    connection._remote_max_frame_size = 1024

    async def fail_write(_channel, frame):
        if isinstance(frame, TransferFrame):
            raise RuntimeError("frame write failed")

    connection._process_outgoing_frame = fail_write
    with pytest.raises(RuntimeError, match="frame write failed"):
        await sender.send_transfer(MagicMock(_code=0, payload=b"message"))
    assert not sender._pending_deliveries
    assert session.next_outgoing_id == 0
    await sender.update_pending_deliveries()
    assert session.next_outgoing_id == 0


@pytest.mark.asyncio
async def test_cancel_async_delivery_waiting_for_session_lock(monkeypatch):
    sender, session, connection = _sender(monkeypatch, True)
    async with session._outgoing_transfer_lock:
        task = asyncio.create_task(sender.send_transfer(MagicMock(_code=0, payload=b"never")))
        await asyncio.sleep(0)
        delivery = sender._pending_deliveries[0]
        await sender.cancel_transfer(delivery)
        assert delivery.cancel_requested and delivery not in sender._pending_deliveries
    await task
    assert not [call for call in connection._process_outgoing_frame.call_args_list
                if isinstance(call.args[1], TransferFrame)]


@pytest.mark.asyncio
@pytest.mark.parametrize("final_frame", [False, True])
async def test_cancel_async_delivery_during_replenishment_flow(monkeypatch, final_frame):
    sender, session, connection = _sender(monkeypatch, True)
    session.remote_incoming_window = 10
    if final_frame:
        connection._remote_max_frame_size = 1024
    started, release = asyncio.Event(), asyncio.Event()
    send = connection._process_outgoing_frame

    async def send_frame(channel, frame):
        if isinstance(frame, FlowFrame) and not started.is_set():
            started.set()
            await release.wait()
        await send(channel, frame)

    connection._process_outgoing_frame = send_frame
    task = asyncio.create_task(sender.send_transfer(MagicMock(_code=0, payload=b"a" * 120)))
    try:
        await asyncio.wait_for(started.wait(), 5)
        delivery = sender._pending_deliveries[0]
        if final_frame:
            with pytest.raises(MessageException, match="already in flight"):
                await sender.cancel_transfer(delivery)
        else:
            await sender.cancel_transfer(delivery)
    finally:
        release.set()
    await task
    transfers = [call.args[1] for call in send.call_args_list if isinstance(call.args[1], TransferFrame)]
    if final_frame:
        assert delivery.sent and not any(frame.aborted for frame in transfers)
    else:
        assert transfers[-1].aborted and transfers[-1].delivery_id == transfers[0].delivery_id
        assert len([frame for frame in transfers if frame.aborted]) == 1


@pytest.mark.asyncio
async def test_async_early_disposition_during_replenishment(monkeypatch):
    sender, session, connection = _sender(monkeypatch, True)
    connection._remote_max_frame_size = 1024
    reasons = []

    async def completed(reason, state):
        reasons.append((reason, state))

    started, release = asyncio.Event(), asyncio.Event()
    send = connection._process_outgoing_frame

    async def send_frame(channel, frame):
        if isinstance(frame, FlowFrame):
            started.set()
            await release.wait()
        await send(channel, frame)

    connection._process_outgoing_frame = send_frame
    task = asyncio.create_task(sender.send_transfer(
        MagicMock(_code=0, payload=b"accepted"), settled=False, on_send_complete=completed
    ))
    try:
        await asyncio.wait_for(started.wait(), 5)
        delivery = sender._pending_deliveries[0]
        assert not delivery.sent
        await sender._incoming_disposition([None, delivery.frame["delivery_id"], None, True, b"accepted"])
        assert delivery.early_disposition_received and delivery in sender._pending_deliveries
    finally:
        release.set()
    assert await task is delivery
    assert reasons == [(LinkDeliverySettleReason.DISPOSITION_RECEIVED, b"accepted")]
    assert delivery.sent and delivery not in sender._pending_deliveries


@pytest.mark.asyncio
@pytest.mark.parametrize("early_ack", [False, True])
@pytest.mark.parametrize("queued", [False, True])
async def test_cancelled_final_replenishment_does_not_resend(monkeypatch, early_ack, queued):
    sender, session, connection = _sender(monkeypatch, True)
    connection._remote_max_frame_size = 1024
    started, release = asyncio.Event(), asyncio.Event()
    reasons = []
    send = connection._process_outgoing_frame

    async def send_frame(channel, frame):
        if isinstance(frame, FlowFrame):
            started.set()
            await release.wait()
        await send(channel, frame)

    async def completed(reason, state):
        reasons.append((reason, state))

    connection._process_outgoing_frame = send_frame
    message = MagicMock(_code=0, payload=b"message")
    if queued:
        await sender.send_transfer(
            message, send_async=True, settled=False, on_send_complete=completed
        )
        task = asyncio.create_task(sender.update_pending_deliveries())
    else:
        task = asyncio.create_task(sender.send_transfer(message, settled=False, on_send_complete=completed))
    try:
        await asyncio.wait_for(started.wait(), 5)
        delivery = sender._pending_deliveries[0]
        assert not delivery.sent
        assert delivery.transfer_state == SessionTransferState.OKAY
        if early_ack:
            await sender._incoming_disposition([None, delivery.frame["delivery_id"], None, True, b"accepted"])
        task.cancel()
    finally:
        release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert delivery.sent and sender.delivery_count == 1 and sender.current_link_credit == 9
    await sender.update_pending_deliveries()
    transfers = [call.args[1] for call in send.call_args_list if isinstance(call.args[1], TransferFrame)]
    assert len(transfers) == 1
    assert reasons == ([(LinkDeliverySettleReason.DISPOSITION_RECEIVED, b"accepted")] if early_ack else [])
    assert (delivery in sender._pending_deliveries) is not early_ack


@pytest.mark.asyncio
async def test_cancelled_send_waiting_for_session_lock_is_withdrawn(monkeypatch):
    sender, session, connection = _sender(monkeypatch, True)
    reasons = []

    async def completed(reason, state):
        reasons.append(reason)

    async with session._outgoing_transfer_lock:
        task = asyncio.create_task(sender.send_transfer(
            MagicMock(_code=0, payload=b"message"), settled=False, on_send_complete=completed
        ))
        await asyncio.sleep(0)
        assert len(sender._pending_deliveries) == 1
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert sender._pending_deliveries == []
    assert reasons == [LinkDeliverySettleReason.CANCELLED]
    await sender.update_pending_deliveries()
    assert not any(isinstance(call.args[1], TransferFrame) for call in connection._process_outgoing_frame.call_args_list)


@pytest.mark.asyncio
async def test_cancelled_queued_drain_waiting_for_session_lock_is_withdrawn(monkeypatch):
    sender, session, connection = _sender(monkeypatch, True)
    reasons = []

    async def completed(reason, state):
        reasons.append(reason)

    delivery = await sender.send_transfer(
        MagicMock(_code=0, payload=b"message"), send_async=True, settled=False, on_send_complete=completed
    )
    async with session._outgoing_transfer_lock:
        task = asyncio.create_task(sender.update_pending_deliveries())
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert delivery.cancel_requested and delivery not in sender._pending_deliveries
    assert reasons == [LinkDeliverySettleReason.CANCELLED]
    await sender.update_pending_deliveries()
    assert not any(isinstance(call.args[1], TransferFrame) for call in connection._process_outgoing_frame.call_args_list)
    assert reasons == [LinkDeliverySettleReason.CANCELLED]


@pytest.mark.asyncio
async def test_cancelled_immediate_send_does_not_withdraw_older_queued_delivery(monkeypatch):
    sender, session, connection = _sender(monkeypatch, True)
    reasons = []
    drain_finished = asyncio.Event()
    original_drain = sender.update_pending_deliveries
    original_send = connection._process_outgoing_frame

    async def drain():
        try:
            await original_drain()
        finally:
            drain_finished.set()

    async def completed(reason, state):
        reasons.append(reason)

    sender.update_pending_deliveries = drain
    older = await sender.send_transfer(
        MagicMock(_code=0, payload=b"older"), send_async=True, settled=False
    )
    async with session._outgoing_transfer_lock:
        task = asyncio.create_task(sender.send_transfer(
            MagicMock(_code=0, payload=b"cancelled"), settled=False, on_send_complete=completed
        ))
        await asyncio.sleep(0)
        cancelled = sender._pending_deliveries[1]
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert older in sender._pending_deliveries
        assert cancelled not in sender._pending_deliveries
        assert reasons == [LinkDeliverySettleReason.CANCELLED]
    await asyncio.wait_for(drain_finished.wait(), 5)
    assert older.sent and sender.delivery_count == 1
    transfers = [call.args[1] for call in original_send.call_args_list if isinstance(call.args[1], TransferFrame)]
    assert len(transfers) == 1 and transfers[0].payload == b"older"


@pytest.mark.asyncio
async def test_cancel_first_caller_while_drain_sends_second(monkeypatch):
    sender, session, connection = _sender(monkeypatch, True)
    connection._remote_max_frame_size = 1024
    session.remote_incoming_window = 10
    first_started, second_started = asyncio.Event(), asyncio.Event()
    first_release, second_release = asyncio.Event(), asyncio.Event()
    reasons = []
    send = connection._process_outgoing_frame

    async def send_frame(channel, frame):
        if isinstance(frame, TransferFrame):
            if bytes(frame.payload) == b"first":
                first_started.set()
                await first_release.wait()
            elif bytes(frame.payload) == b"second":
                second_started.set()
                await second_release.wait()
        await send(channel, frame)

    async def completed(reason, _state):
        reasons.append(reason)

    connection._process_outgoing_frame = send_frame
    first_task = asyncio.create_task(sender.send_transfer(MagicMock(_code=0, payload=b"first")))
    try:
        await asyncio.wait_for(first_started.wait(), 5)
        second = await sender.send_transfer(
            MagicMock(_code=0, payload=b"second"), send_async=True, settled=False, on_send_complete=completed
        )
        first_release.set()
        await asyncio.wait_for(second_started.wait(), 5)
        first_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await first_task
        assert second in sender._pending_deliveries and not second.cancel_requested
    finally:
        first_release.set()
        second_release.set()
    for _ in range(20):
        await asyncio.sleep(0)
        if second.sent:
            break
    assert second.sent and reasons == []


@pytest.mark.asyncio
@pytest.mark.parametrize("partial", [False, True])
async def test_cancelled_immediate_send_after_older_queued_delivery(monkeypatch, partial):
    sender, session, connection = _sender(monkeypatch, True)
    connection._remote_max_frame_size = 80 if partial else 1024
    session.remote_incoming_window = 10
    started, release = asyncio.Event(), asyncio.Event()
    written = []
    original_send = connection._process_outgoing_frame

    async def send_frame(channel, frame):
        if isinstance(frame, TransferFrame):
            written.append(frame)
            if frame.payload and bytes(frame.payload).startswith(b"message"):
                started.set()
                await release.wait()
        await original_send(channel, frame)

    connection._process_outgoing_frame = send_frame
    older = await sender.send_transfer(MagicMock(_code=0, payload=b"older"), send_async=True, settled=False)
    task = asyncio.create_task(sender.send_transfer(
        MagicMock(_code=0, payload=b"message" * (20 if partial else 1)), settled=False
    ))
    try:
        await asyncio.wait_for(started.wait(), 5)
        active = sender._pending_deliveries[1]
        task.cancel()
        await asyncio.sleep(0)
        assert not task.done()
    finally:
        release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert older.sent and sender.delivery_count == (1 if partial else 2)
    if partial:
        assert active.abort_pending
        await sender.update_pending_deliveries()
        assert written[-1].aborted and active not in sender._pending_deliveries
    else:
        assert active.sent
        await sender.update_pending_deliveries()
    assert len([frame for frame in written if not frame.aborted]) == 2


@pytest.mark.asyncio
async def test_cancelled_queued_drain_aborts_partial_transfer(monkeypatch):
    sender, session, connection = _sender(monkeypatch, True)
    connection._remote_max_frame_size = 80
    started, release = asyncio.Event(), asyncio.Event()
    reasons, written = [], []
    send = connection._process_outgoing_frame

    async def completed(reason, state):
        reasons.append(reason)

    async def send_frame(channel, frame):
        if isinstance(frame, TransferFrame):
            written.append(frame)
            if not frame.aborted:
                started.set()
                await release.wait()
        await send(channel, frame)

    connection._process_outgoing_frame = send_frame
    delivery = await sender.send_transfer(
        MagicMock(_code=0, payload=b"message" * 20),
        send_async=True, settled=False, on_send_complete=completed
    )
    task = asyncio.create_task(sender.update_pending_deliveries())
    try:
        await asyncio.wait_for(started.wait(), 5)
        task.cancel()
        await asyncio.sleep(0)
        assert not task.done()
    finally:
        release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert delivery.abort_pending and delivery.frame["aborted"]
    assert reasons == [LinkDeliverySettleReason.CANCELLED]
    session.remote_incoming_window = 1
    await sender.update_pending_deliveries()
    assert delivery not in sender._pending_deliveries
    assert len(written) == 2 and written[1].aborted
    assert written[1].delivery_id == written[0].delivery_id
    assert reasons == [LinkDeliverySettleReason.CANCELLED]


@pytest.mark.asyncio
@pytest.mark.parametrize("partial", [False, True])
async def test_cancelled_transport_drain_does_not_retransmit(monkeypatch, partial):
    sender, session, connection = _sender(monkeypatch, True)
    connection._remote_max_frame_size = 80 if partial else 1024
    started, release = asyncio.Event(), asyncio.Event()
    written = []
    send = connection._process_outgoing_frame

    async def send_frame(channel, frame):
        if isinstance(frame, TransferFrame):
            written.append(frame)
            started.set()
            await release.wait()
        await send(channel, frame)

    connection._process_outgoing_frame = send_frame
    task = asyncio.create_task(sender.send_transfer(
        MagicMock(_code=0, payload=b"message" * (20 if partial else 1)), settled=False
    ))
    try:
        await asyncio.wait_for(started.wait(), 5)
        delivery = sender._pending_deliveries[0]
        task.cancel()
        await asyncio.sleep(0)
        assert not task.done()
    finally:
        release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert len(written) == 1
    assert session.next_outgoing_id == 1
    if partial:
        assert delivery.abort_pending
        session.remote_incoming_window = 1
        await sender.update_pending_deliveries()
        assert written[-1].aborted and written[-1].delivery_id == written[0].delivery_id
        assert len([frame for frame in written if not frame.aborted]) == 1
    else:
        assert delivery.sent and sender.delivery_count == 1
        await sender.update_pending_deliveries()
        assert len(written) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("tcp_transport", [False, True])
async def test_cancelled_stalled_transfer_invalidates_connection(monkeypatch, tcp_transport):
    from azure.eventhub._pyamqp.aio import _session_async

    monkeypatch.setattr(_session_async, "_CANCELLED_FRAME_WRITE_GRACE", 0.01)
    sender, session, connection = _sender(monkeypatch, True)
    started = asyncio.Event()
    never = asyncio.Event()
    written = []
    writer = MagicMock()
    connection._transport = SimpleNamespace(writer=writer) if tcp_transport else SimpleNamespace()
    connection._disconnect = AsyncMock()

    async def send_frame(channel, frame):
        written.append(frame)
        started.set()
        await never.wait()

    connection._process_outgoing_frame = send_frame
    task = asyncio.create_task(sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False))
    await asyncio.wait_for(started.wait(), 5)
    delivery = sender._pending_deliveries[0]
    task.cancel()
    with pytest.raises(AMQPConnectionError, match="Transfer write did not finish"):
        await asyncio.wait_for(task, 5)
    assert delivery.cancel_requested and delivery.transfer_state == SessionTransferState.ERROR
    assert session.state == SessionState.DISCARDING
    assert connection.state == ConnectionState.DISCARDING
    assert isinstance(connection._error, AMQPConnectionError)
    connection._disconnect.assert_awaited_once()
    if tcp_transport:
        writer.transport.abort.assert_called_once()
    await sender.update_pending_deliveries()
    assert len(written) == 1 and session.next_outgoing_id == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_during_flow", [False, True])
async def test_cancelled_stalled_replenishment_preserves_transfer(monkeypatch, cancel_during_flow):
    from azure.eventhub._pyamqp.aio import _session_async

    monkeypatch.setattr(_session_async, "_CANCELLED_FRAME_WRITE_GRACE", 0.03)
    sender, session, connection = _sender(monkeypatch, True)
    session.outgoing_window = 1
    transfer_started, release_transfer, flow_started, never = (asyncio.Event() for _ in range(4))
    written = []
    connection._transport = SimpleNamespace()
    connection._disconnect = AsyncMock()

    async def send_frame(channel, frame):
        written.append(frame)
        if isinstance(frame, TransferFrame):
            transfer_started.set()
            await release_transfer.wait()
        else:
            flow_started.set()
            await never.wait()

    connection._process_outgoing_frame = send_frame
    task = asyncio.create_task(sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False))
    await asyncio.wait_for(transfer_started.wait(), 5)
    delivery = sender._pending_deliveries[0]
    if not cancel_during_flow:
        task.cancel()
        await asyncio.sleep(0)
    release_transfer.set()
    await asyncio.wait_for(flow_started.wait(), 5)
    if cancel_during_flow:
        task.cancel()
    with pytest.raises(AMQPConnectionError, match="Flow write did not finish"):
        await asyncio.wait_for(task, 5)
    assert delivery.sent and delivery.cancel_requested
    assert delivery.transfer_state == SessionTransferState.OKAY
    assert sender.delivery_count == 1 and sender.current_link_credit == 9
    assert session.next_outgoing_id == 1 and session.state == SessionState.DISCARDING
    assert connection.state == ConnectionState.DISCARDING
    connection._disconnect.assert_awaited_once()
    await sender.update_pending_deliveries()
    assert len([frame for frame in written if isinstance(frame, TransferFrame)]) == 1
    assert len([frame for frame in written if isinstance(frame, FlowFrame)]) == 1


@pytest.mark.asyncio
async def test_stalled_flow_disconnect_notifies_other_sender_after_active_bookkeeping(monkeypatch):
    from azure.eventhub._pyamqp.aio import _session_async

    monkeypatch.setattr(_session_async, "_CANCELLED_FRAME_WRITE_GRACE", 0.01)
    sender, session, connection = _sender(monkeypatch, True)
    session.outgoing_window = 1
    connection._remote_max_frame_size = 1024
    connection.state = ConnectionState.OPENED
    connection._network_trace_params = {}
    connection._outgoing_endpoints = {session.channel: session}
    connection._transport = SimpleNamespace(close=AsyncMock())
    connection._set_state = AsyncConnection._set_state.__get__(connection)
    connection._disconnect = AsyncConnection._disconnect.__get__(connection)
    sender._on_link_state_change = None
    other = AsyncSenderLink(session, 2, "other", network_trace=False, network_trace_params={})
    other.state = LinkState.ATTACHED
    session.links = {1: sender, 2: other}
    reasons = []

    async def other_completed(reason, state):
        reasons.append(("other", reason))

    async def active_completed(reason, state):
        reasons.append(("active", reason, active.sent, sender.delivery_count))

    queued = await other.send_transfer(
        MagicMock(_code=0, payload=b"queued"), send_async=True,
        settled=False, on_send_complete=other_completed
    )
    flow_started, never = asyncio.Event(), asyncio.Event()

    async def send_frame(channel, frame):
        if isinstance(frame, FlowFrame):
            flow_started.set()
            await never.wait()

    connection._process_outgoing_frame = send_frame
    task = asyncio.create_task(sender.send_transfer(
        MagicMock(_code=0, payload=b"active"), settled=False, on_send_complete=active_completed
    ))
    await asyncio.wait_for(flow_started.wait(), 5)
    active = sender._pending_deliveries[0]
    task.cancel()
    with pytest.raises(AMQPConnectionError, match="Flow write did not finish"):
        await asyncio.wait_for(task, 5)
    assert active.sent and active.transfer_state == SessionTransferState.OKAY
    assert sender.delivery_count == 1 and session.next_outgoing_id == 1
    assert connection.state == ConnectionState.END
    connection._transport.close.assert_awaited_once()
    assert sender.state == other.state == LinkState.DETACHED
    assert sender._pending_deliveries == other._pending_deliveries == []
    assert queued.settled
    assert reasons == [
        ("active", LinkDeliverySettleReason.NOT_DELIVERED, True, 1),
        ("other", LinkDeliverySettleReason.NOT_DELIVERED),
    ]


@pytest.mark.asyncio
async def test_concurrent_discarding_notifications_settle_once(monkeypatch):
    sender, session, _ = _sender(monkeypatch, True)
    sender._on_link_state_change = None
    session.links = {1: sender}
    session.state = SessionState.DISCARDING
    session._discarding_links_pending = True
    callback_started, release = asyncio.Event(), asyncio.Event()
    reasons = []

    async def completed(reason, state):
        reasons.append(reason)
        callback_started.set()
        await release.wait()

    await sender.send_transfer(
        MagicMock(_code=0, payload=b"queued"), send_async=True,
        settled=False, on_send_complete=completed
    )
    first = asyncio.create_task(session._notify_discarding_links())
    try:
        await asyncio.wait_for(callback_started.wait(), 5)
        second = asyncio.create_task(session._notify_discarding_links())
        await asyncio.wait_for(second, 5)
        assert reasons == [LinkDeliverySettleReason.NOT_DELIVERED]
    finally:
        release.set()
        await first
    assert sender._pending_deliveries == [] and sender.state == LinkState.DETACHED


def test_threaded_early_disposition_during_replenishment(monkeypatch):
    sender, session, connection = _sender(monkeypatch, False)
    connection._remote_max_frame_size = 1024
    reasons = []

    def completed(reason, state):
        reasons.append((reason, state))

    started, release = Event(), Event()
    send = connection._process_outgoing_frame

    def send_frame(channel, frame):
        if isinstance(frame, FlowFrame):
            started.set()
            assert release.wait(5)
        send(channel, frame)

    connection._process_outgoing_frame = send_frame
    with ThreadPoolExecutor(max_workers=2) as pool:
        task = pool.submit(sender.send_transfer, MagicMock(_code=0, payload=b"accepted"),
                           settled=False, on_send_complete=completed)
        try:
            assert started.wait(5)
            delivery = sender._pending_deliveries[0]
            assert not delivery.sent
            disposition = pool.submit(
                sender._incoming_disposition, [None, delivery.frame["delivery_id"], None, True, b"accepted"]
            )
            assert not disposition.done()
        finally:
            release.set()
        disposition.result(timeout=5)
        assert task.result(timeout=5) is delivery
    assert reasons == [(LinkDeliverySettleReason.DISPOSITION_RECEIVED, b"accepted")]
    assert delivery.sent and delivery not in sender._pending_deliveries


def test_reentrant_disposition_during_sync_replenishment(monkeypatch):
    sender, session, connection = _sender(monkeypatch, False)
    connection._remote_max_frame_size = 1024
    reasons = []
    send = connection._process_outgoing_frame

    def send_frame(channel, frame):
        if isinstance(frame, FlowFrame):
            delivery = sender._pending_deliveries[0]
            assert not delivery.sent
            sender._incoming_disposition([None, delivery.frame["delivery_id"], None, True, b"accepted"])
            assert delivery.early_disposition_received
        send(channel, frame)

    connection._process_outgoing_frame = send_frame
    delivery = sender.send_transfer(
        MagicMock(_code=0, payload=b"accepted"), settled=False,
        on_send_complete=lambda reason, state: reasons.append((reason, state)),
    )
    assert delivery.sent and delivery not in sender._pending_deliveries
    assert reasons == [(LinkDeliverySettleReason.DISPOSITION_RECEIVED, b"accepted")]


@pytest.mark.parametrize("send_fails", [False, True])
def test_management_rejection_before_send_returns(send_fails):
    management = ManagementLink.__new__(ManagementLink)
    management.lock = RLock()
    management._pending_operations = []
    completed = []

    def send_transfer(message, *, on_send_complete, timeout):
        assert management._pending_operations[0].message is not None
        if send_fails:
            raise RuntimeError("send failed")
        on_send_complete(
            LinkDeliverySettleReason.DISPOSITION_RECEIVED,
            {SEND_DISPOSITION_REJECT: [[b"amqp:not-allowed", b"rejected", None]]},
        )

    management._request_link = SimpleNamespace(send_transfer=send_transfer)
    if send_fails:
        with pytest.raises(RuntimeError, match="send failed"):
            management.execute_operation(Message(application_properties={}), lambda *a, **kw: completed.append((a, kw)))
        assert not completed
    else:
        management.execute_operation(Message(application_properties={}), lambda *a, **kw: completed.append((a, kw)))
        assert len(completed) == 1
        assert completed[0][0][0] is ManagementExecuteOperationResult.ERROR
        assert completed[0][1]["error"].description == b"rejected"
    assert management._pending_operations == []


@pytest.mark.asyncio
@pytest.mark.parametrize("send_failure", [None, RuntimeError, asyncio.CancelledError])
async def test_async_management_rejection_before_send_returns(send_failure):
    management = AsyncManagementLink.__new__(AsyncManagementLink)
    management._pending_operations = []
    completed = []

    async def on_complete(*args, **kwargs):
        completed.append((args, kwargs))

    async def send_transfer(message, *, on_send_complete, timeout):
        assert management._pending_operations[0].message is not None
        if send_failure:
            raise send_failure("send failed")
        await on_send_complete(
            LinkDeliverySettleReason.DISPOSITION_RECEIVED,
            {SEND_DISPOSITION_REJECT: [[b"amqp:not-allowed", b"rejected", None]]},
        )

    management._request_link = SimpleNamespace(send_transfer=send_transfer)
    if send_failure:
        with pytest.raises(send_failure, match="send failed"):
            await management.execute_operation(Message(application_properties={}), on_complete)
        assert not completed
    else:
        await management.execute_operation(Message(application_properties={}), on_complete)
        assert len(completed) == 1
        assert completed[0][0][0] is ManagementExecuteOperationResult.ERROR
        assert completed[0][1]["error"].description == b"rejected"
    assert management._pending_operations == []


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


@pytest.mark.parametrize("termination", ["cancel", "timeout"])
def test_reentrant_settlement_aborts_before_draining(monkeypatch, termination):
    sender, session, connection = _sender(monkeypatch, False)
    first = sender.send_transfer(
        MagicMock(_code=0, payload=b"a" * 120), settled=False,
        on_send_complete=lambda _reason, _state: sender.update_pending_deliveries(),
    )
    assert first.frame["more"]
    session.remote_incoming_window = 10
    if termination == "cancel":
        sender.cancel_transfer(first)
    else:
        first.timeout = 1
        first.start -= 10
        sender.update_pending_deliveries()
    transfers = [call.args[1] for call in connection._process_outgoing_frame.call_args_list
                 if isinstance(call.args[1], TransferFrame)]
    assert len(transfers) == 2
    assert transfers[1].aborted and not transfers[1].payload
    assert transfers[1].delivery_id == transfers[0].delivery_id


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
