"""Tests for observable receiver-link settlement outcomes.

On the pyamqp transport a PEEK_LOCK settlement was sent pre-settled, so a settlement the
service never applied was indistinguishable from a successful one and the message silently
redelivered at lock expiry. This was reproduced live: on one session with one dead lock,
``complete_message()`` returned success in 0.42 ms while the management link raised
``SessionLockLostError`` for the same lock, and the message stayed queued.

These tests assert the three things the fix must guarantee:

1. a settlement the service rejects raises,
2. a settlement the service never confirms is reported as unconfirmed (so the caller can
   re-settle authoritatively) rather than as success,
3. the default behavior is unchanged for callers who do not opt in.
"""
import itertools
import threading

import pytest
from unittest.mock import AsyncMock, MagicMock

from azure.servicebus import ServiceBusClient, ServiceBusReceiveMode
from azure.servicebus._common.constants import MESSAGE_COMPLETE
from azure.servicebus._common.message import ServiceBusReceivedMessage

_DELIVERY_IDS = itertools.count(1000)
from azure.servicebus._servicebus_receiver import ServiceBusReceiver
from azure.servicebus.aio._servicebus_receiver_async import ServiceBusReceiver as ServiceBusReceiverAsync
from azure.servicebus._pyamqp.constants import LinkState, ReceiverSettleMode, Role
from azure.servicebus._pyamqp.error import (
    ErrorCondition,
    MessageException,
    MessageSettlementUnconfirmed,
)
from azure.servicebus._pyamqp.constants import SEND_DISPOSITION_ACCEPT
from azure.servicebus._pyamqp.outcomes import Accepted, Modified, Rejected
from azure.servicebus._pyamqp.receiver import ReceiverLink, check_disposition_outcome, outcome_name
from azure.servicebus._pyamqp.aio._receiver_async import ReceiverLink as ReceiverLinkAsync
from azure.servicebus._pyamqp.client import ReceiveClient
from azure.servicebus._pyamqp.aio._client_async import ReceiveClientAsync
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus.aio._transport._pyamqp_transport_async import PyamqpTransportAsync

DELIVERY_TAG = b"delivery-tag"
DELIVERY_ID = 7

ACCEPTED = {"accepted": []}
REJECTED = {"rejected": [[b"com.microsoft:message-lock-lost", "The lock supplied is invalid.", None]]}

CONN_STR = "Endpoint=sb://fake.servicebus.windows.net/;SharedAccessKeyName=k;SharedAccessKey=YWJjZGVm"


def disposition_frame(first, last, settled, state, role=Role.Sender):
    """Build the positional disposition frame tuple as the decoder produces it."""
    return (role, first, last, settled, state, None)


class FakeConnection:
    """Replays a scripted sequence of incoming disposition frames, one per ``listen`` call."""

    def __init__(self, link, frames=None):
        self._link = link
        self._frames = list(frames or [])
        self.listen_calls = 0

    def listen(self, wait=False, **kwargs):  # pylint: disable=unused-argument
        self.listen_calls += 1
        if self._frames:
            self._link._incoming_disposition(self._frames.pop(0))


class FakeSession:
    def __init__(self):
        self._connection = None
        self.outgoing_frames = []

    def _outgoing_disposition(self, frame):
        self.outgoing_frames.append(frame)


class FakeConnectionAsync(FakeConnection):
    async def listen(self, wait=False, **kwargs):  # pylint: disable=invalid-overridden-method,unused-argument
        self.listen_calls += 1
        if self._frames:
            await self._link._incoming_disposition(self._frames.pop(0))


class FakeSessionAsync(FakeSession):
    async def _outgoing_disposition(self, frame):  # pylint: disable=invalid-overridden-method
        self.outgoing_frames.append(frame)


def _build_link(link_cls, session_cls, connection_cls, frames=None):
    session = session_cls()
    link = link_cls(
        session,
        handle=1,
        source_address="test-source",
        network_trace=False,
        network_trace_params={},
        on_transfer=lambda *args, **kwargs: None,
        rcv_settle_mode=ReceiverSettleMode.Second,
    )
    session._connection = connection_cls(link, frames)
    link.state = LinkState.ATTACHED
    link._received_delivery_tags.add(DELIVERY_TAG)
    return link


def build_sync_link(frames=None):
    return _build_link(ReceiverLink, FakeSession, FakeConnection, frames)


def build_async_link(frames=None):
    return _build_link(ReceiverLinkAsync, FakeSessionAsync, FakeConnectionAsync, frames)


def settle(link, **kwargs):
    kwargs.setdefault("settled", False)
    kwargs.setdefault("await_outcome", True)
    return link.send_disposition(first_delivery_id=DELIVERY_ID, delivery_tag=DELIVERY_TAG, **kwargs)


async def settle_async(link, **kwargs):
    kwargs.setdefault("settled", False)
    kwargs.setdefault("await_outcome", True)
    return await link.send_disposition(first_delivery_id=DELIVERY_ID, delivery_tag=DELIVERY_TAG, **kwargs)


# ---------------------------------------------------------------------------
# check_disposition_outcome
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("outcome", [None, {}, {"released": []}, {"modified": []}])
def test_outcome_that_does_not_match_the_request_is_a_failed_settlement(outcome):
    """An echo that is not what we asked for -- or no echo at all -- is a failure."""
    with pytest.raises(MessageException) as exc_info:
        check_disposition_outcome(DELIVERY_ID, outcome, SEND_DISPOSITION_ACCEPT)
    assert exc_info.value.condition == ErrorCondition.InternalError


# The service echoes the outcome it APPLIED rather than always replying `accepted`.
# These are the exact echoes captured from a live namespace; requiring `accepted`
# falsely failed abandon, defer and dead-letter.
@pytest.mark.parametrize(
    "operation, echoed, requested",
    [
        ("complete", {"accepted": []}, "accepted"),
        ("abandon", {"modified": [None, False, None]}, "modified"),
        ("defer", {"modified": [None, True, None]}, "modified"),
        ("dead_letter", {"rejected": [None]}, "rejected"),
    ],
)
def test_service_echo_of_the_requested_outcome_is_a_success(operation, echoed, requested):
    """Every settle operation must be confirmable, not just complete."""
    assert check_disposition_outcome(DELIVERY_ID, echoed, requested) is None


@pytest.mark.parametrize("requested", ["accepted", "modified", "rejected"])
def test_service_rejection_still_fails_whatever_was_requested(requested):
    """A rejected outcome carrying an error is a failure even when rejection was requested.

    Dead-lettering sends `rejected`, so the error payload -- not the outcome name --
    is what distinguishes a failed settlement from a successful dead-letter.
    """
    with pytest.raises(MessageException) as exc_info:
        check_disposition_outcome(DELIVERY_ID, REJECTED, requested)
    assert exc_info.value.condition == b"com.microsoft:message-lock-lost"


def test_outcome_name_maps_delivery_state_to_the_echoed_key():
    """The expected outcome is derived from the state sent, so no plumbing is needed."""
    assert outcome_name(Accepted()) == "accepted"
    assert outcome_name(Modified()) == "modified"
    assert outcome_name(Rejected()) == "rejected"
    assert outcome_name(None) == "accepted"


# ---------------------------------------------------------------------------
# Sync link: default behavior is unchanged
# ---------------------------------------------------------------------------


def test_default_settlement_stays_pre_settled_and_never_waits():
    """Callers who do not opt in keep the existing fire-and-forget behavior exactly."""
    link = build_sync_link()
    link.send_disposition(first_delivery_id=DELIVERY_ID, delivery_tag=DELIVERY_TAG, settled=True)

    assert link._session.outgoing_frames[0].settled is True
    assert link._session._connection.listen_calls == 0
    assert not link._pending_dispositions


# ---------------------------------------------------------------------------
# Sync link: awaited settlement
# ---------------------------------------------------------------------------


def test_awaited_settlement_sends_unsettled_and_returns_once_accepted():
    """Awaiting sends the disposition unsettled -- honouring rcv-settle-mode=second."""
    link = build_sync_link(frames=[disposition_frame(DELIVERY_ID, DELIVERY_ID, True, ACCEPTED)])
    settle(link)

    assert link._session.outgoing_frames[0].settled is False
    assert link._session._connection.listen_calls == 1
    assert not link._pending_dispositions


def test_awaited_settlement_raises_when_the_service_rejects():
    """A rejection the service sends must reach the caller, not be discarded."""
    link = build_sync_link(frames=[disposition_frame(DELIVERY_ID, DELIVERY_ID, True, REJECTED)])

    with pytest.raises(MessageException) as exc_info:
        settle(link)

    assert exc_info.value.condition == b"com.microsoft:message-lock-lost"
    assert not isinstance(exc_info.value, MessageSettlementUnconfirmed), (
        "a definitive rejection must not be reported as unconfirmed"
    )
    assert not link._pending_dispositions


def test_awaited_settlement_reports_unconfirmed_when_no_outcome_arrives():
    """An unconfirmed settlement is distinct from a rejection: the caller must re-settle."""
    link = build_sync_link(frames=[])

    with pytest.raises(MessageSettlementUnconfirmed) as exc_info:
        settle(link, outcome_timeout=0.1)

    assert exc_info.value.condition == ErrorCondition.ClientError
    assert not link._pending_dispositions


def test_awaited_settlement_reports_unconfirmed_when_the_link_detaches():
    """A detach mid-settlement leaves the outcome unknown, which must not read as success."""
    link = build_sync_link(frames=[])

    def detach_on_listen(wait=False, **kwargs):  # pylint: disable=unused-argument
        link._session._connection.listen_calls += 1
        link.state = LinkState.DETACHED

    link._session._connection.listen = detach_on_listen

    with pytest.raises(MessageSettlementUnconfirmed) as exc_info:
        settle(link, outcome_timeout=5)

    assert exc_info.value.condition == ErrorCondition.LinkDetachForced


def test_receiver_role_dispositions_are_ignored():
    """Deliveries on a receiver link are settled by the remote sender, not by a receiver."""
    link = build_sync_link(
        frames=[
            disposition_frame(DELIVERY_ID, DELIVERY_ID, True, ACCEPTED, role=Role.Receiver),
            disposition_frame(DELIVERY_ID, DELIVERY_ID, True, ACCEPTED),
        ]
    )
    settle(link, outcome_timeout=5)
    assert link._session._connection.listen_calls == 2


def test_unsettled_disposition_carrying_an_outcome_does_not_confirm():
    """rcv-settle-mode Second is satisfied only once the sender settles.

    A disposition that carries a terminal outcome with settled=False is still unsettled;
    treating it as confirmation would report success before the service committed.
    """
    link = build_sync_link(
        frames=[
            disposition_frame(DELIVERY_ID, DELIVERY_ID, False, ACCEPTED),
            disposition_frame(DELIVERY_ID, DELIVERY_ID, True, ACCEPTED),
        ]
    )
    settle(link, outcome_timeout=5)
    # Two listens: the unsettled frame was ignored, the settled one resolved it.
    assert link._session._connection.listen_calls == 2


def test_huge_advertised_range_costs_only_the_pending_deliveries():
    """`first`/`last` are peer-controlled 32-bit values.

    Resolving the outcome must be proportional to what we are actually tracking, not to the
    advertised range. Note that a regression here manifests as a hang rather than a failure,
    because the old code walked every ID in the range.
    """
    link = build_sync_link(frames=[disposition_frame(0, 2**32 - 1, True, ACCEPTED)])
    settle(link, outcome_timeout=5)
    assert link._pending_dispositions == {}


def test_inverted_range_is_rejected_rather_than_confirming_nothing():
    """An empty range would register no deliveries and then report instant success."""
    link = build_sync_link()
    with pytest.raises(ValueError):
        link.send_disposition(
            first_delivery_id=DELIVERY_ID,
            last_delivery_id=DELIVERY_ID - 1,
            delivery_tag=DELIVERY_TAG,
            settled=False,
            delivery_state=Accepted(),
            await_outcome=True,
        )


# ---------------------------------------------------------------------------
# Async link -- the PBI requires parity on both receivers
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_default_settlement_stays_pre_settled_and_never_waits():
    """Async default behavior is unchanged."""
    link = build_async_link()
    await link.send_disposition(first_delivery_id=DELIVERY_ID, delivery_tag=DELIVERY_TAG, settled=True)

    assert link._session.outgoing_frames[0].settled is True
    assert link._session._connection.listen_calls == 0


@pytest.mark.asyncio
async def test_async_awaited_settlement_returns_once_accepted():
    """The async link confirms a settlement the same way the sync link does."""
    link = build_async_link(frames=[disposition_frame(DELIVERY_ID, DELIVERY_ID, True, ACCEPTED)])
    await settle_async(link)

    assert link._session.outgoing_frames[0].settled is False
    assert not link._pending_dispositions


@pytest.mark.asyncio
async def test_async_awaited_settlement_raises_when_the_service_rejects():
    """A rejection reaches the caller on the async receiver too."""
    link = build_async_link(frames=[disposition_frame(DELIVERY_ID, DELIVERY_ID, True, REJECTED)])

    with pytest.raises(MessageException) as exc_info:
        await settle_async(link)

    assert exc_info.value.condition == b"com.microsoft:message-lock-lost"


@pytest.mark.asyncio
async def test_async_awaited_settlement_reports_unconfirmed_when_no_outcome_arrives():
    """An unconfirmed settlement must not read as success on the async receiver."""
    link = build_async_link(frames=[])

    with pytest.raises(MessageSettlementUnconfirmed):
        await settle_async(link, outcome_timeout=0.1)

    assert not link._pending_dispositions


# ---------------------------------------------------------------------------
# Receiver plumbing
# ---------------------------------------------------------------------------


def _receiver(await_settlement_outcome, is_async=False):
    cls = ServiceBusReceiverAsync if is_async else ServiceBusReceiver
    r = cls.__new__(cls)
    r._handler = MagicMock(name="handler")
    r._session = None
    r._await_settlement_outcome = await_settlement_outcome
    r._config = MagicMock(name="config")
    r._config.timeout = 60
    r._shutdown = threading.Event()
    r._running = True
    r._receive_mode = ServiceBusReceiveMode.PEEK_LOCK
    r._amqp_transport = MagicMock(name="transport")
    if is_async:
        r._amqp_transport.settle_message_via_receiver_link_async = AsyncMock(name="settle")
    else:
        r._amqp_transport.settle_message_via_receiver_link = MagicMock(name="settle")
    return r


def _received_message(deferred=False):
    """A ServiceBusReceivedMessage stand-in that satisfies complete_messages' isinstance check."""
    message = ServiceBusReceivedMessage.__new__(ServiceBusReceivedMessage)
    message._is_deferred_message = deferred
    message._is_peeked_message = False
    message._settled = False
    message._delivery_id = next(_DELIVERY_IDS)
    message._delivery_tag = f"tag-{message._delivery_id}".encode()
    # complete_messages consults locked_until_utc, which reads these.
    message._expiry = None
    message._raw_amqp_message = MagicMock(annotations={})
    message.auto_renew_error = None
    return message


@pytest.mark.parametrize("opted_in", [True, False])
def test_sync_receiver_forwards_the_option_and_timeout(opted_in):
    """The receiver-level option is what turns on outcome observation at the transport."""
    receiver = _receiver(opted_in)
    receiver._settle_message(_received_message(), MESSAGE_COMPLETE)

    _, kwargs = receiver._amqp_transport.settle_message_via_receiver_link.call_args
    assert kwargs["await_outcome"] is opted_in
    assert kwargs["outcome_timeout"] == 60


@pytest.mark.asyncio
@pytest.mark.parametrize("opted_in", [True, False])
async def test_async_receiver_forwards_the_option_and_timeout(opted_in):
    """The async receiver plumbs the option through identically."""
    receiver = _receiver(opted_in, is_async=True)
    await receiver._settle_message(_received_message(), MESSAGE_COMPLETE)

    _, kwargs = receiver._amqp_transport.settle_message_via_receiver_link_async.call_args
    assert kwargs["await_outcome"] is opted_in
    assert kwargs["outcome_timeout"] == 60


@pytest.mark.parametrize("kwargs, expected", [({}, False), ({"await_settlement_outcome": True}, True)])
def test_option_is_off_unless_explicitly_enabled(kwargs, expected):
    """Existing applications keep today's behavior; one keyword covers all four settle operations."""
    with ServiceBusClient.from_connection_string(CONN_STR) as client:
        receiver = client.get_queue_receiver(queue_name="q", **kwargs)
        assert receiver._await_settlement_outcome is expected


def test_option_is_rejected_in_receive_and_delete_mode():
    """RECEIVE_AND_DELETE messages are settled by the service on delivery -- there is no outcome."""
    with ServiceBusClient.from_connection_string(CONN_STR) as client:
        with pytest.raises(ValueError):
            client.get_queue_receiver(
                queue_name="q",
                receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
                await_settlement_outcome=True,
            )


def test_non_pyamqp_transport_is_rejected_at_construction():
    """The guard must fire while building the receiver, not at settle time.

    The transport raises NotImplementedError, which subclasses RuntimeError and would be
    swallowed by the management-link fallback -- silently settling instead of failing loudly.
    Exercised through a stand-in transport so the guard stays covered where uamqp is absent.
    """
    receiver = ServiceBusReceiver.__new__(ServiceBusReceiver)
    receiver._entity_name = "q"
    receiver.fully_qualified_namespace = "ns.servicebus.windows.net"
    receiver._config = MagicMock(name="config")
    receiver._amqp_transport = MagicMock(name="transport")
    receiver._amqp_transport.KIND = "uamqp"
    receiver._amqp_transport.TIMEOUT_FACTOR = 1

    with pytest.raises(ValueError, match="uamqp"):
        receiver._populate_attributes(queue_name="q", await_settlement_outcome=True)


def test_pyamqp_transport_accepts_the_option():
    """The same construction path succeeds on the supported transport."""
    receiver = ServiceBusReceiver.__new__(ServiceBusReceiver)
    receiver._entity_name = "q"
    receiver.fully_qualified_namespace = "ns.servicebus.windows.net"
    receiver._config = MagicMock(name="config")
    receiver._amqp_transport = MagicMock(name="transport")
    receiver._amqp_transport.KIND = "pyamqp"
    receiver._amqp_transport.TIMEOUT_FACTOR = 1

    receiver._populate_attributes(queue_name="q", await_settlement_outcome=True)
    assert receiver._await_settlement_outcome is True


def test_uamqp_transport_settle_call_still_refuses():
    """Defense in depth: the transport itself must not silently ignore the request."""
    uamqp_transport = pytest.importorskip("azure.servicebus._transport._uamqp_transport")
    if not hasattr(uamqp_transport, "UamqpTransport"):
        pytest.skip("uamqp is not installed")
    with pytest.raises(NotImplementedError):
        uamqp_transport.UamqpTransport.settle_message_via_receiver_link(
            MagicMock(), _received_message(), MESSAGE_COMPLETE, await_outcome=True
        )


# ---------------------------------------------------------------------------
# ReceiveClient.settle_messages -- the layer that chooses pre-settled vs unsettled
# ---------------------------------------------------------------------------


def _receive_client(is_async=False):
    cls = ReceiveClientAsync if is_async else ReceiveClient
    client = cls.__new__(cls)
    client._link = MagicMock(name="link")
    if is_async:
        client._link.send_disposition = AsyncMock(name="send_disposition")
    return client


@pytest.mark.parametrize("await_outcome, expected_settled", [(True, False), (False, True)])
def test_settle_messages_chooses_pre_settled_based_on_the_option(await_outcome, expected_settled):
    """The opt-in is what makes the disposition unsettled -- which is what lets the service reply.

    Sending ``settled=True`` terminates the exchange, so the service never reports an outcome.
    """
    client = _receive_client()
    client.settle_messages(DELIVERY_ID, DELIVERY_TAG, "accepted", await_outcome=await_outcome)

    _, kwargs = client._link.send_disposition.call_args
    assert kwargs["settled"] is expected_settled
    assert kwargs["await_outcome"] is await_outcome


def test_settle_messages_does_not_leak_the_new_keywords_into_the_outcome():
    """``rejected``/``modified`` build their outcome from **kwargs, so the new keywords must be popped."""
    client = _receive_client()
    client.settle_messages(
        DELIVERY_ID, DELIVERY_TAG, "modified", delivery_failed=True, undeliverable_here=False, await_outcome=True
    )
    state = client._link.send_disposition.call_args[1]["delivery_state"]
    assert state.delivery_failed is True
    assert not hasattr(state, "await_outcome")


# ---------------------------------------------------------------------------
# Transport: unconfirmed must route to the management-link fallback, rejected must not
# ---------------------------------------------------------------------------


def _handler_raising(exc, is_async=False):
    handler = MagicMock(name="handler")
    if is_async:
        handler.settle_messages_async = AsyncMock(name="settle", side_effect=exc)
    else:
        handler.settle_messages = MagicMock(name="settle", side_effect=exc)
    return handler


UNCONFIRMED = MessageSettlementUnconfirmed(
    condition=ErrorCondition.ClientError, description="no outcome arrived"
)
REJECTION = MessageException(condition=b"com.microsoft:message-lock-lost", description="lock lost")


def test_unconfirmed_settlement_routes_to_the_management_link_fallback():
    """`_settle_message` only falls back on RuntimeError, so an unknown outcome must become one.

    This is what lets the caller re-settle over the management link, which is request/response
    and therefore authoritative.
    """
    with pytest.raises(RuntimeError):
        PyamqpTransport.settle_message_via_receiver_link(
            _handler_raising(UNCONFIRMED), _received_message(), MESSAGE_COMPLETE, await_outcome=True
        )


def test_rejected_settlement_is_not_downgraded_to_a_fallback():
    """A rejection is a definitive answer, so it must reach the caller instead of being retried."""
    with pytest.raises(MessageException) as exc_info:
        PyamqpTransport.settle_message_via_receiver_link(
            _handler_raising(REJECTION), _received_message(), MESSAGE_COMPLETE, await_outcome=True
        )
    assert not isinstance(exc_info.value, RuntimeError)
    assert exc_info.value.condition == b"com.microsoft:message-lock-lost"


@pytest.mark.asyncio
async def test_async_unconfirmed_settlement_routes_to_the_management_link_fallback():
    """Async transport routes an unknown outcome to the fallback the same way."""
    with pytest.raises(RuntimeError):
        await PyamqpTransportAsync.settle_message_via_receiver_link_async(
            _handler_raising(UNCONFIRMED, is_async=True), _received_message(), MESSAGE_COMPLETE, await_outcome=True
        )


@pytest.mark.asyncio
async def test_async_rejected_settlement_is_not_downgraded_to_a_fallback():
    """A rejection reaches the caller on the async transport too."""
    with pytest.raises(MessageException) as exc_info:
        await PyamqpTransportAsync.settle_message_via_receiver_link_async(
            _handler_raising(REJECTION, is_async=True), _received_message(), MESSAGE_COMPLETE, await_outcome=True
        )
    assert not isinstance(exc_info.value, RuntimeError)
