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
from azure.eventhub._pyamqp.error import AMQPConnectionError, AMQPLinkError, MessageException
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
    if async_connection:
        connection._disconnect = AsyncMock()
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


@pytest.mark.parametrize("early_notification", [False, True])
def test_sync_failed_write_callback_reentry(monkeypatch, early_notification):
    sender, session, connection = _sender(monkeypatch, False)
    session.links["sender"] = sender
    sender._on_link_state_change = None
    connection._remote_max_frame_size = 1024
    reasons, frames = [], []

    def completed(reason, _state):
        unlocked = session._outgoing_transfer_lock.acquire(blocking=False)
        assert unlocked is not early_notification
        if unlocked:
            session._outgoing_transfer_lock.release()
        reasons.append(reason)
        sender.update_pending_deliveries()

    def fail_write(_channel, frame):
        frames.append(frame)
        if isinstance(frame, TransferFrame):
            if early_notification:
                session._set_state(SessionState.DISCARDING)
            raise RuntimeError("Transfer write failed")

    connection._process_outgoing_frame = fail_write

    def disconnect():
        sender.current_link_credit = 0
        sender.update_pending_deliveries()

    connection._disconnect.side_effect = disconnect
    sender.send_transfer(
        MagicMock(_code=0, payload=b"queued"), send_async=True, settled=False, on_send_complete=completed
    )
    with ThreadPoolExecutor(max_workers=1) as executor:
        result = executor.submit(sender.send_transfer, MagicMock(_code=0, payload=b"failing"), settled=False)
        with pytest.raises(RuntimeError, match="Transfer write failed"):
            result.result(timeout=5)
    assert reasons == [LinkDeliverySettleReason.NOT_DELIVERED]
    assert session.state == SessionState.DISCARDING
    assert not sender._pending_deliveries
    assert len(frames) == 1 and isinstance(frames[0], TransferFrame)


def test_sync_teardown_serializes_pending_queue_and_membership(monkeypatch):
    sender, _, _ = _sender(monkeypatch, False)
    delivery = sender.send_transfer(MagicMock(_code=0, payload=b"queued"), send_async=True)
    started = Event()

    def teardown():
        started.set()
        sender._remove_pending_deliveries()

    with ThreadPoolExecutor(max_workers=1) as executor:
        with sender.lock:
            result = executor.submit(teardown)
            assert started.wait(5)
            assert not result.done()
            assert sender._pending_ids() == {id(delivery)}
        result.result(timeout=5)
    assert sender._pending_ids() == set()
    assert not sender._pending_deliveries


def test_sync_teardown_callback_cannot_queue_on_discarded_session(monkeypatch):
    sender, session, _ = _sender(monkeypatch, False)
    session.links["sender"] = sender
    sender._on_link_state_change = None
    reasons = []

    def completed(reason, _state):
        reasons.append(reason)
        with pytest.raises(AMQPLinkError, match="not attached"):
            sender.send_transfer(MagicMock(_code=0, payload=b"late"), send_async=True)

    sender.send_transfer(
        MagicMock(_code=0, payload=b"queued"), send_async=True, settled=False, on_send_complete=completed
    )
    session._set_state(SessionState.DISCARDING)
    assert reasons == [LinkDeliverySettleReason.NOT_DELIVERED]
    assert not sender._pending_deliveries
    assert not sender._pending_ids()


def test_sync_pending_poll_uses_identity_membership(monkeypatch):
    sender, session, _ = _sender(monkeypatch, False)
    session.remote_incoming_window = 0

    class ObservedList(list):
        comparisons = 0

        def __contains__(self, value):
            self.comparisons += 1
            return super().__contains__(value)

    for _ in range(500):
        delivery = sender.send_transfer(MagicMock(_code=0, payload=b"queued"), send_async=True)
        delivery.sent = True
    observed = ObservedList(sender._pending_deliveries)
    sender._pending_deliveries = observed
    sender.update_pending_deliveries()
    assert len(sender._pending_deliveries) == 500
    assert observed.comparisons == 0


def test_sync_poll_preserves_callback_queue_changes(monkeypatch):
    sender, session, _ = _sender(monkeypatch, False)
    session.remote_incoming_window = 0
    added = []

    def completed(_reason, _state):
        sender.cancel_transfer(second)
        added.append(sender.send_transfer(MagicMock(_code=0, payload=b"new"), send_async=True))

    first = sender.send_transfer(
        MagicMock(_code=0, payload=b"expired"), send_async=True, settled=False, timeout=1, on_send_complete=completed
    )
    second = sender.send_transfer(MagicMock(_code=0, payload=b"cancel"), send_async=True)
    first.start -= 10
    sender.update_pending_deliveries()
    assert sender._pending_deliveries == added
    assert sender._pending_ids() == {id(added[0])}


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
        sender._pending_delivery_ids = set()
        sender.lock = RLock()
    return sender, session, connection


@pytest.mark.parametrize("async_session", [False, True])
@pytest.mark.parametrize("queued", [False, True])
@pytest.mark.parametrize("settle_mode", [SenderSettleMode.Mixed, SenderSettleMode.Settled])
@pytest.mark.asyncio
async def test_presettled_send_completes_once(monkeypatch, async_session, queued, settle_mode):
    sender, _, connection = _sender(monkeypatch, async_session)
    sender.send_settle_mode = settle_mode
    connection._remote_max_frame_size = 1024
    reasons = []
    disposition = [None, 0, None, True, b"accepted"]

    def completed(reason, _state):
        reasons.append(reason)
        if len(reasons) == 1:
            sender._incoming_disposition(disposition)

    async def completed_async(reason, _state):
        reasons.append(reason)
        if len(reasons) == 1:
            await sender._incoming_disposition(disposition)

    kwargs = {"send_async": queued, "on_send_complete": completed_async if async_session else completed}
    message = MagicMock(_code=0, payload=b"one")
    if async_session:
        delivery = await sender.send_transfer(message, **kwargs)
        if queued:
            await sender.update_pending_deliveries()
        await delivery.on_settled(LinkDeliverySettleReason.NOT_DELIVERED, None)
    else:
        delivery = sender.send_transfer(message, **kwargs)
        if queued:
            sender.update_pending_deliveries()
        delivery.on_settled(LinkDeliverySettleReason.NOT_DELIVERED, None)
    assert delivery.sent
    assert reasons == [LinkDeliverySettleReason.SETTLED]
    assert not sender._pending_deliveries


@pytest.mark.parametrize("async_session", [False, True])
@pytest.mark.parametrize("queued", [False, True])
@pytest.mark.parametrize("settled", [False, True])
@pytest.mark.asyncio
async def test_sender_drains_only_peer_link_credit(monkeypatch, async_session, queued, settled):
    sender, session, connection = _sender(monkeypatch, async_session)
    connection._remote_max_frame_size = 1024
    session.remote_incoming_window = 10
    sender.link_credit = 10
    sender.current_link_credit = 1
    first_message = MagicMock(_code=0, payload=b"first")
    second_message = MagicMock(_code=0, payload=b"second")
    if async_session:
        first = await sender.send_transfer(first_message, send_async=True, settled=settled)
        second = await sender.send_transfer(second_message, send_async=queued, settled=settled)
        await sender.update_pending_deliveries()
        await sender.update_pending_deliveries()
    else:
        first = sender.send_transfer(first_message, send_async=True, settled=settled)
        second = sender.send_transfer(second_message, send_async=queued, settled=settled)
        sender.update_pending_deliveries()
        sender.update_pending_deliveries()
    transfers = [call.args[1] for call in connection._process_outgoing_frame.call_args_list
                 if isinstance(call.args[1], TransferFrame)]
    assert len(transfers) == 1
    assert sum(delivery.sent for delivery in (first, second)) == 1
    assert sender.current_link_credit == 0
    peer_flow = [None, 10, 0, 10, sender.handle, sender.delivery_count, 1]
    if async_session:
        await sender._incoming_flow(peer_flow)
    else:
        sender._incoming_flow(peer_flow)
    transfers = [call.args[1] for call in connection._process_outgoing_frame.call_args_list
                 if isinstance(call.args[1], TransferFrame)]
    assert len(transfers) == 2
    assert first.sent and second.sent
    assert sender.current_link_credit == 0


@pytest.mark.parametrize("async_session", [False, True])
@pytest.mark.parametrize("credit", [0, -1])
@pytest.mark.parametrize("queued", [False, True])
@pytest.mark.asyncio
async def test_sender_checks_timeouts_without_link_credit(monkeypatch, async_session, credit, queued):
    sender, _, connection = _sender(monkeypatch, async_session)
    sender.link_credit = 10
    sender.current_link_credit = credit
    reasons = []

    def completed(reason, _state):
        reasons.append(reason)

    async def completed_async(reason, state):
        completed(reason, state)

    callback = completed_async if async_session else completed
    if async_session:
        first = await sender.send_transfer(MagicMock(_code=0, payload=b"first"), send_async=queued)
        later = await sender.send_transfer(
            MagicMock(_code=0, payload=b"later"), send_async=True, timeout=1, on_send_complete=callback
        )
    else:
        first = sender.send_transfer(MagicMock(_code=0, payload=b"first"), send_async=queued)
        later = sender.send_transfer(
            MagicMock(_code=0, payload=b"later"), send_async=True, timeout=1, on_send_complete=callback
        )
    later.start -= 10
    if async_session:
        await sender.update_pending_deliveries()
    else:
        sender.update_pending_deliveries()
    assert reasons == [LinkDeliverySettleReason.TIMEOUT]
    assert sender._pending_deliveries == [first]
    assert sender.current_link_credit == credit
    assert not first.sent
    assert not connection._process_outgoing_frame.call_args_list


@pytest.mark.parametrize("async_session", [False, True])
@pytest.mark.parametrize("termination", [None, "cancel", "timeout"])
@pytest.mark.asyncio
async def test_sender_continues_partial_delivery_without_link_credit(monkeypatch, async_session, termination):
    sender, session, connection = _sender(monkeypatch, async_session)
    sender.link_credit = 10
    sender.current_link_credit = 1
    message = MagicMock(_code=0, payload=b"a" * 120)
    if async_session:
        first = await sender.send_transfer(message, settled=False)
        later = await sender.send_transfer(MagicMock(_code=0, payload=b"later"), send_async=True)
    else:
        first = sender.send_transfer(message, settled=False)
        later = sender.send_transfer(MagicMock(_code=0, payload=b"later"), send_async=True)
    assert first.frame["more"] and not first.sent
    sender.current_link_credit = 0
    if termination == "cancel":
        if async_session:
            await sender.cancel_transfer(first)
        else:
            sender.cancel_transfer(first)
    elif termination == "timeout":
        first.timeout = 1
        first.start -= 10
    session.remote_incoming_window = 10
    if async_session:
        await sender.update_pending_deliveries()
        await sender.update_pending_deliveries()
    else:
        sender.update_pending_deliveries()
        sender.update_pending_deliveries()
    transfers = [call.args[1] for call in connection._process_outgoing_frame.call_args_list
                 if isinstance(call.args[1], TransferFrame)]
    assert len(transfers) > 1
    assert all(frame.delivery_id == transfers[0].delivery_id for frame in transfers)
    assert not transfers[-1].more
    assert bool(transfers[-1].aborted) == (termination is not None)
    assert first.sent and not later.sent
    assert sender.current_link_credit <= 0
    peer_flow = [None, 10, 0, 10, sender.handle, sender.delivery_count, 1]
    if async_session:
        await sender._incoming_flow(peer_flow)
    else:
        sender._incoming_flow(peer_flow)
    assert later.sent and sender.current_link_credit == 0


@pytest.mark.parametrize("completion_path", ["presettled", "early_disposition", "disposition"])
@pytest.mark.asyncio
async def test_async_cancelled_completion_callback_withdraws_delivery(monkeypatch, completion_path):
    sender, _, connection = _sender(monkeypatch, True)
    connection._remote_max_frame_size = 1024
    entered, release = asyncio.Event(), asyncio.Event()
    reasons = []

    async def completed(reason, _state):
        reasons.append(reason)
        entered.set()
        await release.wait()

    delivery = await sender.send_transfer(
        MagicMock(_code=0, payload=b"message"), send_async=True,
        settled=completion_path == "presettled", on_send_complete=completed,
    )
    disposition = [None, 0, None, True, b"accepted"]
    if completion_path == "early_disposition":
        original_send = connection._process_outgoing_frame

        async def send_frame(channel, frame):
            await original_send(channel, frame)
            if isinstance(frame, FlowFrame):
                await sender._incoming_disposition(disposition)

        connection._process_outgoing_frame = send_frame
    if completion_path == "disposition":
        await sender.update_pending_deliveries()
        task = asyncio.create_task(sender._incoming_disposition(disposition))
    else:
        task = asyncio.create_task(sender.update_pending_deliveries())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert delivery.sent and delivery.settled
        assert delivery not in sender._pending_deliveries
        await sender.update_pending_deliveries()
        assert delivery not in sender._pending_deliveries
        assert len(reasons) == 1
    finally:
        release.set()
        if not task.done():
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task


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


@pytest.mark.parametrize("stored_error", [False, True])
@pytest.mark.asyncio
async def test_frame_write_failure_marks_delivery_failed(monkeypatch, stored_error):
    sender, session, connection = _sender(monkeypatch, True)
    connection._remote_max_frame_size = 1024
    connection._error = None

    async def fail_write(_channel, frame):
        if isinstance(frame, TransferFrame):
            if stored_error:
                connection._error = RuntimeError("frame write failed")
            else:
                raise RuntimeError("frame write failed")

    connection._process_outgoing_frame = fail_write
    with pytest.raises(RuntimeError, match="frame write failed"):
        await sender.send_transfer(MagicMock(_code=0, payload=b"message"))
    assert not sender._pending_deliveries
    assert session.next_outgoing_id == 0
    assert session.outgoing_window == 1
    assert session.remote_incoming_window == 1
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
async def test_cancel_busy_caller_while_later_timeout_callback_waits(monkeypatch):
    sender, session, connection = _sender(monkeypatch, True)
    session.remote_incoming_window = 0
    timed_out, release = asyncio.Event(), asyncio.Event()
    reasons = []

    async def completed(reason, _state):
        reasons.append(reason)

    async def timeout_completed(reason, _state):
        reasons.append(reason)
        timed_out.set()
        await release.wait()

    async with session._outgoing_transfer_lock:
        task = asyncio.create_task(sender.send_transfer(
            MagicMock(_code=0, payload=b"first"), settled=False, on_send_complete=completed
        ))
        await asyncio.sleep(0)
        first = sender._pending_deliveries[0]
        second = await sender.send_transfer(
            MagicMock(_code=0, payload=b"second"), send_async=True,
            settled=False, timeout=1, on_send_complete=timeout_completed
        )
        second.start -= 10
    try:
        await asyncio.wait_for(timed_out.wait(), 5)
        assert first.frame is not None and first._inflight_more is None
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert first not in sender._pending_deliveries
        assert reasons == [LinkDeliverySettleReason.TIMEOUT, LinkDeliverySettleReason.CANCELLED]
    finally:
        release.set()
    await asyncio.sleep(0)
    session.remote_incoming_window = 1
    await sender.update_pending_deliveries()
    assert not sender._pending_deliveries
    assert not [call for call in connection._process_outgoing_frame.call_args_list
                if isinstance(call.args[1], TransferFrame)]


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


@pytest.mark.asyncio
@pytest.mark.parametrize("async_sender", [False, True])
async def test_reentrant_disposition_completes_delivery_once(monkeypatch, async_sender):
    sender, _, _ = _sender(monkeypatch, async_sender)
    sender.send_settle_mode = SenderSettleMode.Unsettled
    calls = []
    frame = [True, 0, 0, True, {"accepted": []}, False]

    async def async_complete(reason, state):
        calls.append(reason)
        if len(calls) == 1:
            await sender._incoming_disposition(frame)

    def sync_complete(reason, state):
        calls.append(reason)
        if len(calls) == 1:
            sender._incoming_disposition(frame)

    callback = async_complete if async_sender else sync_complete
    if async_sender:
        await sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False, on_send_complete=callback)
        await sender._incoming_disposition(frame)
    else:
        sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False, on_send_complete=callback)
        sender._incoming_disposition(frame)
    assert calls == [LinkDeliverySettleReason.DISPOSITION_RECEIVED]
    assert not sender._pending_deliveries


@pytest.mark.asyncio
async def test_async_discard_during_disposition_does_not_complete_twice(monkeypatch):
    sender, session, _ = _sender(monkeypatch, True)
    session.links = {"sender": sender}
    sender._on_link_state_change = None
    sender.send_settle_mode = SenderSettleMode.Unsettled
    entered = asyncio.Event()
    release = asyncio.Event()
    calls = []

    async def complete(reason, state):
        calls.append(reason)
        if reason == LinkDeliverySettleReason.DISPOSITION_RECEIVED:
            entered.set()
            await release.wait()

    await sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False, on_send_complete=complete)
    disposition = asyncio.create_task(sender._incoming_disposition([True, 0, 0, True, {"accepted": []}, False]))
    try:
        await asyncio.wait_for(entered.wait(), timeout=1)
        await session._set_state(SessionState.DISCARDING)
        assert calls == [LinkDeliverySettleReason.DISPOSITION_RECEIVED]
        assert not sender._pending_deliveries
    finally:
        release.set()
        await disposition


@pytest.mark.asyncio
@pytest.mark.parametrize("async_sender", [False, True])
@pytest.mark.parametrize("stored_error", [False, True])
async def test_partial_write_failure_discards_session_and_pending_deliveries(monkeypatch, async_sender, stored_error):
    sender, session, connection = _sender(monkeypatch, async_sender)
    session.links = {"sender": sender}
    sender._on_link_state_change = None
    session.remote_incoming_window = 10
    connection._remote_max_frame_size = 80
    calls = []
    writes = []

    def write(channel, frame, **kwargs):
        if isinstance(frame, TransferFrame):
            writes.append(frame)
            if len(writes) == 2:
                error = RuntimeError("uncertain partial write")
                if stored_error:
                    connection._error = error
                else:
                    raise error

    async def async_write(channel, frame, **kwargs):
        write(channel, frame, **kwargs)

    async def async_complete(reason, state):
        calls.append(reason)

    def sync_complete(reason, state):
        calls.append(reason)

    connection._process_outgoing_frame.side_effect = async_write if async_sender else write
    with pytest.raises(RuntimeError, match="uncertain partial write"):
        if async_sender:
            await sender.send_transfer(
                MagicMock(_code=0, payload=b"x" * 100), settled=False, on_send_complete=async_complete
            )
        else:
            sender.send_transfer(MagicMock(_code=0, payload=b"x" * 100), settled=False, on_send_complete=sync_complete)
    assert len(writes) == 2
    assert session.next_outgoing_id == 1
    assert session.state == SessionState.DISCARDING
    assert sender.state == LinkState.DETACHED
    assert not sender._pending_deliveries
    assert calls == [LinkDeliverySettleReason.NOT_DELIVERED]
    connection._disconnect.assert_called_once()


def test_sync_queued_encoding_failure_withdraws_delivery(monkeypatch):
    sender, _, connection = _sender(monkeypatch, False)
    sender.send_transfer(MagicMock(_code=0, payload=b"bad"), send_async=True)

    def fail_encode(output, message):
        raise ValueError("cannot encode")

    with monkeypatch.context() as context:
        context.setattr("azure.eventhub._pyamqp.sender.encode_payload", fail_encode)
        with pytest.raises(ValueError, match="cannot encode"):
            sender.update_pending_deliveries()
    assert not sender._pending_deliveries
    assert not sender._pending_delivery_ids
    connection._process_outgoing_frame.assert_not_called()
    sender.send_transfer(MagicMock(_code=0, payload=b"good"))
    assert (
        len(
            [
                call
                for call in connection._process_outgoing_frame.call_args_list
                if isinstance(call.args[1], TransferFrame)
            ]
        )
        == 1
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("async_sender", [False, True])
async def test_stored_flow_error_is_raised_without_resending_transfer(monkeypatch, async_sender):
    sender, session, connection = _sender(monkeypatch, async_sender)
    session.outgoing_window = 1
    sender.send_settle_mode = SenderSettleMode.Unsettled

    def write(channel, frame, **kwargs):
        if isinstance(frame, FlowFrame):
            connection._error = RuntimeError("stored Flow error")

    async def async_write(channel, frame, **kwargs):
        write(channel, frame, **kwargs)

    connection._process_outgoing_frame.side_effect = async_write if async_sender else write
    with pytest.raises(RuntimeError, match="stored Flow error"):
        if async_sender:
            await sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False)
        else:
            sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False)
    delivery = sender._pending_deliveries[0]
    assert delivery.sent
    assert delivery.transfer_state == SessionTransferState.OKAY
    assert session.next_outgoing_id == 1
    connection._error = None
    if async_sender:
        await sender.update_pending_deliveries()
    else:
        sender.update_pending_deliveries()
    assert (
        len(
            [
                call
                for call in connection._process_outgoing_frame.call_args_list
                if isinstance(call.args[1], TransferFrame)
            ]
        )
        == 1
    )


@pytest.mark.asyncio
async def test_async_discard_callback_cannot_enqueue_delivery(monkeypatch):
    sender, session, _ = _sender(monkeypatch, True)
    session.links = {"sender": sender}
    sender._on_link_state_change = None
    sender.send_settle_mode = SenderSettleMode.Unsettled
    rejected = []

    async def complete(reason, state):
        with pytest.raises(AMQPLinkError):
            await sender.send_transfer(MagicMock(_code=0, payload=b"late"), send_async=True)
        rejected.append(reason)

    await sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False, on_send_complete=complete)
    await session._set_state(SessionState.DISCARDING)
    assert rejected == [LinkDeliverySettleReason.NOT_DELIVERED]
    assert sender.state == LinkState.DETACHED
    assert not sender._pending_deliveries


@pytest.mark.asyncio
@pytest.mark.parametrize("async_sender", [False, True])
async def test_discard_callback_can_remove_its_link(monkeypatch, async_sender):
    sender, session, _ = _sender(monkeypatch, async_sender)
    sender._on_link_state_change = None
    session.links = {"sender": sender}

    def complete(reason, state):
        session.links.pop("sender", None)

    async def async_complete(reason, state):
        complete(reason, state)

    if async_sender:
        await sender.send_transfer(
            MagicMock(_code=0, payload=b"message"), settled=False, on_send_complete=async_complete
        )
        await session._set_state(SessionState.DISCARDING)
    else:
        sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False, on_send_complete=complete)
        session._set_state(SessionState.DISCARDING)
    assert not session.links
    assert not sender._pending_deliveries


@pytest.mark.asyncio
async def test_cancelled_discard_notification_finishes_remaining_links(monkeypatch):
    sender, session, _ = _sender(monkeypatch, True)
    sender._on_link_state_change = None
    other = MagicMock()
    other._on_session_state_change = AsyncMock()
    session.links = {"sender": sender, "other": other}
    started = asyncio.Event()

    async def complete(reason, state):
        started.set()
        await asyncio.Event().wait()

    await sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False, on_send_complete=complete)
    session.state = SessionState.DISCARDING
    session._discarding_links_pending = True
    notification = asyncio.create_task(session._notify_discarding_links())
    try:
        await asyncio.wait_for(started.wait(), timeout=1)
    finally:
        notification.cancel()
        with pytest.raises(asyncio.CancelledError):
            await notification
    await sender.update_pending_deliveries()
    other._on_session_state_change.assert_awaited_once()
    assert not session._discarding_links_pending


@pytest.mark.asyncio
@pytest.mark.parametrize("async_sender", [False, True])
async def test_transport_close_notifies_after_transfer_lock_is_released(monkeypatch, async_sender):
    sender, session, connection = _sender(monkeypatch, async_sender)
    sender._on_link_state_change = None
    session.links = {"sender": sender}
    observed = []

    def complete(reason, state):
        observed.append(session._outgoing_transfer_lock.locked())

    async def async_complete(reason, state):
        complete(reason, state)

    def write(channel, frame, **kwargs):
        if isinstance(frame, TransferFrame):
            connection.state = ConnectionState.END
            session._on_connection_state_change()
            raise RuntimeError("transport closed")

    async def async_write(channel, frame, **kwargs):
        if isinstance(frame, TransferFrame):
            connection.state = ConnectionState.END
            await session._on_connection_state_change()
            raise RuntimeError("transport closed")

    connection._process_outgoing_frame.side_effect = async_write if async_sender else write
    with pytest.raises(RuntimeError, match="transport closed"):
        if async_sender:
            await sender.send_transfer(
                MagicMock(_code=0, payload=b"message"), settled=False, on_send_complete=async_complete
            )
        else:
            sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False, on_send_complete=complete)
    assert observed == [False]
    assert sender.state == LinkState.DETACHED
    assert not sender._pending_deliveries


@pytest.mark.asyncio
@pytest.mark.parametrize("async_management", [False, True])
@pytest.mark.parametrize("send_fails", [False, True])
async def test_early_management_response_reentry_completes_once(async_management, send_fails):
    kind = AsyncManagementLink if async_management else ManagementLink
    management = kind.__new__(kind)
    management.lock = RLock()
    management._pending_operations = []
    management._status_code_field = b"statusCode"
    management._status_description_field = b"statusDescription"
    completed = []
    received = []

    def complete(*args, **kwargs):
        completed.append((args, len(management._pending_operations)))
        if not async_management and len(completed) == 1:
            management._on_message_received(None, received[0])

    async def async_complete(*args, **kwargs):
        complete(*args, **kwargs)
        if len(completed) == 1:
            await management._on_message_received(None, received[0])

    def response(message):
        return message._replace(
            properties=message.properties._replace(correlation_id=message.properties.message_id),
            application_properties={b"statusCode": 200},
        )

    def send(message, **kwargs):
        received.append(response(message))
        management._on_message_received(None, received[0])
        if send_fails:
            raise RuntimeError("send failed after response")

    async def async_send(message, **kwargs):
        received.append(response(message))
        await management._on_message_received(None, received[0])
        if send_fails:
            raise RuntimeError("send failed after response")

    management._request_link = SimpleNamespace(send_transfer=async_send if async_management else send)

    async def execute():
        if async_management:
            await management.execute_operation(Message(application_properties={}), async_complete)
        else:
            management.execute_operation(Message(application_properties={}), complete)

    if send_fails:
        with pytest.raises(RuntimeError, match="send failed after response"):
            await execute()
    else:
        await execute()
    assert len(completed) == 1
    assert completed[0][0][0] == ManagementExecuteOperationResult.OK
    assert completed[0][1] == 0
    assert not management._pending_operations


@pytest.mark.asyncio
@pytest.mark.parametrize("async_sender", [False, True])
async def test_discard_poll_waits_for_active_transfer_lock(monkeypatch, async_sender):
    sender, session, _ = _sender(monkeypatch, async_sender)
    sender._on_link_state_change = None
    session.links = {"sender": sender}
    observed = []

    def complete(reason, state):
        observed.append(session._outgoing_transfer_lock.locked())

    async def async_complete(reason, state):
        complete(reason, state)

    if async_sender:
        await sender.send_transfer(
            MagicMock(_code=0, payload=b"message"), settled=False, on_send_complete=async_complete
        )
        await session._outgoing_transfer_lock.acquire()
    else:
        sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False, on_send_complete=complete)
        session._outgoing_transfer_lock.acquire()
    session.state = SessionState.DISCARDING
    session._discarding_links_pending = True
    try:
        if async_sender:
            await sender.update_pending_deliveries()
        else:
            sender.update_pending_deliveries()
        assert not observed
        assert session._discarding_links_pending
    finally:
        session._outgoing_transfer_lock.release()
    if async_sender:
        await sender.update_pending_deliveries()
    else:
        sender.update_pending_deliveries()
    assert observed == [False]
    assert not session._discarding_links_pending


@pytest.mark.asyncio
@pytest.mark.parametrize("async_sender", [False, True])
@pytest.mark.parametrize("stored_error", [False, True])
@pytest.mark.parametrize("partial", [False, True])
async def test_failed_replenishment_discards_delivery_without_resuming(
    monkeypatch, async_sender, stored_error, partial
):
    sender, session, connection = _sender(monkeypatch, async_sender)
    sender._on_link_state_change = None
    session.links = {"sender": sender}
    session.remote_incoming_window = 10
    connection._error = None
    frames, reasons = [], []
    error = RuntimeError("replenishment failed")

    def write(channel, frame, **kwargs):
        frames.append(frame)
        if isinstance(frame, FlowFrame):
            if stored_error:
                connection._error = error
            else:
                raise error

    async def async_write(channel, frame, **kwargs):
        write(channel, frame, **kwargs)

    def complete(reason, state):
        reasons.append(reason)

    async def async_complete(reason, state):
        complete(reason, state)

    connection._process_outgoing_frame.side_effect = async_write if async_sender else write
    message = MagicMock(_code=0, payload=b"x" * (120 if partial else 1))
    if async_sender:
        delivery = await sender.send_transfer(message, settled=False, send_async=True, on_send_complete=async_complete)
        with pytest.raises(RuntimeError) as caught:
            await sender.update_pending_deliveries()
        await sender.update_pending_deliveries()
    else:
        delivery = sender.send_transfer(message, settled=False, send_async=True, on_send_complete=complete)
        with pytest.raises(RuntimeError) as caught:
            sender.update_pending_deliveries()
        sender.update_pending_deliveries()
    assert caught.value is error
    assert [type(frame) for frame in frames] == [TransferFrame, FlowFrame]
    assert session.next_outgoing_id == 1
    assert session.remote_incoming_window == 9
    assert delivery.sent is not partial
    assert delivery.transfer_state == (SessionTransferState.BUSY if partial else SessionTransferState.OKAY)
    assert sender.delivery_count == (0 if partial else 1)
    assert sender.current_link_credit == (10 if partial else 9)
    assert session.state == SessionState.DISCARDING
    assert sender.state == LinkState.DETACHED
    assert not sender._pending_deliveries
    assert reasons == [LinkDeliverySettleReason.NOT_DELIVERED]
    connection._disconnect.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("async_session", [False, True])
@pytest.mark.parametrize("stored_error", [False, True])
async def test_standalone_flow_failure_closes_after_releasing_lock(async_session, stored_error):
    session, connection = _session(AsyncSession if async_session else Session, async_connection=async_session)
    error = RuntimeError("Flow failed")
    link = MagicMock()
    link._on_session_state_change = AsyncMock() if async_session else MagicMock()
    session.links = {"link": link}

    def write(channel, frame, **kwargs):
        if stored_error:
            connection._error = error
        else:
            raise error

    async def async_write(channel, frame, **kwargs):
        write(channel, frame, **kwargs)

    connection._process_outgoing_frame.side_effect = async_write if async_session else write
    with pytest.raises(RuntimeError) as caught:
        if async_session:
            await session._outgoing_flow()
        else:
            session._outgoing_flow()
    assert caught.value is error
    assert session.state == SessionState.DISCARDING
    assert not session._outgoing_transfer_lock.locked()
    assert not session._discarding_links_pending
    link._on_session_state_change.assert_called_once()
    connection._disconnect.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("async_sender", [False, True])
@pytest.mark.parametrize("fail_flow", [False, True])
async def test_cleanup_failure_preserves_write_error_and_logs_secondary(monkeypatch, async_sender, fail_flow, caplog):
    sender, session, connection = _sender(monkeypatch, async_sender)
    sender._on_link_state_change = None
    session.links = {"sender": sender}
    error = RuntimeError("primary write failure")
    connection._disconnect.side_effect = RuntimeError("secondary cleanup failure")

    def write(channel, frame, **kwargs):
        if isinstance(frame, FlowFrame if fail_flow else TransferFrame):
            raise error

    async def async_write(channel, frame, **kwargs):
        write(channel, frame, **kwargs)

    connection._process_outgoing_frame.side_effect = async_write if async_sender else write
    with pytest.raises(RuntimeError) as caught:
        if async_sender:
            await sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False)
        else:
            sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False)
    assert caught.value is error
    assert connection._error is error
    assert "secondary cleanup failure" in caplog.text
    assert session.state == SessionState.DISCARDING
    assert not sender._pending_deliveries
    connection._disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_transport_abort_failure_still_disconnects_and_preserves_write_error(monkeypatch, caplog):
    sender, session, connection = _sender(monkeypatch, True)
    sender._on_link_state_change = None
    session.links = {"sender": sender}
    error = RuntimeError("primary write failure")
    connection._process_outgoing_frame.side_effect = error
    connection._transport.writer.transport.abort.side_effect = RuntimeError("secondary abort failure")
    with pytest.raises(RuntimeError) as caught:
        await sender.send_transfer(MagicMock(_code=0, payload=b"message"), settled=False)
    assert caught.value is error
    assert connection._error is error
    assert "secondary abort failure" in caplog.text
    assert session.state == SessionState.DISCARDING
    assert not sender._pending_deliveries
    connection._disconnect.assert_awaited_once()
