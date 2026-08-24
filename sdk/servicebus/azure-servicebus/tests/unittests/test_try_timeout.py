# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# --------------------------------------------------------------------------

"""Unit tests for the opt-in per-attempt timeout (`try_timeout`).

`try_timeout` bounds a single attempt of an operation rather than the whole operation. It
applies to sending, to management operations, and to AMQP link acquisition, where the wait for
the link to become ready was previously unbounded. It is off by default.

It deliberately does not apply to the receive long poll or the streaming iterator: bounding
those would silently truncate a caller who asked for a long wait. That exclusion is the
safety property these tests exist to pin.

Mirrors `TryTimeout` in the Go SDK (Azure/azure-sdk-for-go#27176), which is likewise opt-in
and off by default, and the same concept in the .NET (`ServiceBusRetryOptions.TryTimeout`) and
Java (`AmqpRetryOptions.tryTimeout`) SDKs, which default it on at 60 seconds.
"""

import time

from unittest.mock import MagicMock, patch

import pytest

from azure.servicebus._common._configuration import Configuration
from azure.servicebus._common.constants import DEFAULT_RECEIVE_WAIT_TIME_SECS
from azure.servicebus._common.utils import (
    check_link_ready_deadline,
    get_attempt_timeout,
    get_link_ready_deadline,
    get_remaining_timeout,
)
from azure.servicebus.exceptions import OperationTimeoutError


class TestAttemptTimeout:
    """`get_attempt_timeout` decides the bound for a single retry attempt."""

    @pytest.mark.parametrize(
        "remaining,try_timeout,expected",
        [
            # Disabled: None, zero and negative all leave the caller's bound untouched.
            (None, None, None),
            (30, None, 30),
            (30, 0, 30),
            (30, -1, 30),
            # Enabled: bounds the attempt, but never past what the caller has left.
            (None, 5, 5),
            (30, 5, 5),
            (10, 60, 10),
        ],
    )
    def test_bound_for_one_attempt(self, remaining, try_timeout, expected):
        assert get_attempt_timeout(remaining, try_timeout) == expected


class _FakeConfig:
    """Minimal stand-in for `Configuration` in the retry loop."""

    def __init__(self, try_timeout=None, retry_total=3):
        self.try_timeout = try_timeout
        self.retry_total = retry_total


class TestConfigurationTryTimeout:
    def test_defaults_to_disabled(self):
        # Opt-in, so existing callers are unaffected.
        config = Configuration(hostname="fake.servicebus.windows.net", amqp_transport=MagicMock())
        assert config.try_timeout is None

    def test_negative_value_preserved(self):
        # A negative value is not normalized; it simply means disabled.
        config = Configuration(
            hostname="fake.servicebus.windows.net",
            amqp_transport=MagicMock(),
            try_timeout=-1,
        )
        assert config.try_timeout == -1
        assert get_attempt_timeout(30, config.try_timeout) == 30


class TestTryTimeoutPropagation:
    """The knob is set on the client but consumed by the handlers, so it must reach them."""

    def _client(self, **kwargs):
        from azure.servicebus import ServiceBusClient

        return ServiceBusClient("fake.servicebus.windows.net", MagicMock(), **kwargs)

    def test_reaches_handlers(self):
        client = self._client(try_timeout=7)
        assert client._config.try_timeout == 7
        assert client.get_queue_receiver("q")._config.try_timeout == 7
        assert client.get_queue_sender("q")._config.try_timeout == 7
        assert client.get_subscription_receiver("t", "s")._config.try_timeout == 7

    def test_default_remains_unset_on_handlers(self):
        client = self._client()
        assert client.get_queue_receiver("q")._config.try_timeout is None
        assert client.get_queue_sender("q")._config.try_timeout is None

    @pytest.mark.asyncio
    async def test_reaches_async_handlers(self):
        from azure.servicebus.aio import ServiceBusClient as AsyncServiceBusClient

        client = AsyncServiceBusClient("fake.servicebus.windows.net", MagicMock(), try_timeout=7)
        assert client.get_queue_receiver("q")._config.try_timeout == 7
        assert client.get_queue_sender("q")._config.try_timeout == 7


class TestAsyncParity:
    """The async retry loop is a separate implementation and can drift from the sync one."""

    @pytest.mark.asyncio
    async def test_async_retry_loop_honors_opt_in(self):
        from azure.servicebus.aio._base_handler_async import BaseHandler as AsyncBaseHandler

        handler = AsyncBaseHandler.__new__(AsyncBaseHandler)
        handler._config = _FakeConfig(try_timeout=5)
        handler._container_id = "test-container"

        seen = []

        async def operation(**kwargs):
            seen.append(kwargs.get("timeout"))
            return "ok"

        await handler._do_retryable_operation(
            operation,
            timeout=30,
            operation_requires_timeout=True,
            apply_try_timeout=True,
        )
        assert seen == [5]

        seen.clear()
        await handler._do_retryable_operation(
            operation,
            timeout=30,
            operation_requires_timeout=True,
        )
        assert seen[0] == pytest.approx(30, abs=1)


class TestRetryLoopAppliesAttemptTimeout:
    """The bound applies only where a call site opts in, so long polls are never truncated."""

    def _make_handler(self, try_timeout):
        from azure.servicebus._base_handler import BaseHandler

        handler = BaseHandler.__new__(BaseHandler)
        handler._config = _FakeConfig(try_timeout=try_timeout)
        handler._container_id = "test-container"
        return handler

    def test_opted_in_call_site_is_bounded(self):
        # A call site passing `apply_try_timeout=True` has each attempt bounded by the configured
        # value.
        handler = self._make_handler(try_timeout=5)
        seen = []

        def operation(**kwargs):
            seen.append(kwargs.get("timeout"))
            return "ok"

        result = handler._do_retryable_operation(
            operation,
            timeout=30,
            operation_requires_timeout=True,
            apply_try_timeout=True,
        )
        assert result == "ok"
        assert seen == [5]

    def test_call_site_without_opt_in_keeps_full_caller_timeout(self):
        # Receive and streaming iteration do not opt in, so they keep the caller's timeout.
        handler = self._make_handler(try_timeout=5)
        seen = []

        def operation(**kwargs):
            seen.append(kwargs.get("timeout"))
            return "ok"

        handler._do_retryable_operation(
            operation,
            timeout=30,
            operation_requires_timeout=True,
        )
        # The full remaining caller timeout, not the 5s per-attempt value.
        assert len(seen) == 1
        assert seen[0] == pytest.approx(30, abs=1)

    def test_disabled_config_leaves_behavior_unchanged(self):
        # With the knob off, an opted-in call site behaves exactly as before.
        handler = self._make_handler(try_timeout=None)
        seen = []

        def operation(**kwargs):
            seen.append(kwargs.get("timeout"))
            return "ok"

        handler._do_retryable_operation(
            operation,
            timeout=30,
            operation_requires_timeout=True,
            apply_try_timeout=True,
        )
        assert len(seen) == 1
        assert seen[0] == pytest.approx(30, abs=1)

    def test_unbounded_caller_stays_unbounded_when_disabled(self):
        # No caller timeout and no per-attempt bound means no timeout is applied at all.
        handler = self._make_handler(try_timeout=None)
        seen = []

        def operation(**kwargs):
            seen.append(kwargs.get("timeout", "unset"))
            return "ok"

        handler._do_retryable_operation(
            operation,
            timeout=None,
            operation_requires_timeout=True,
            apply_try_timeout=True,
        )
        assert seen == ["unset"]

    def test_attempt_bound_applies_to_every_retry(self):
        # Each attempt is bounded afresh rather than sharing one budget.
        handler = self._make_handler(try_timeout=5)
        seen = []
        clock = {"now": 1000.0}

        def operation(**kwargs):
            seen.append(kwargs.get("timeout"))
            if len(seen) < 3:
                clock["now"] += 10  # this attempt burned 10s of the caller's budget
                raise ValueError("transient")
            return "ok"

        handler._handle_exception = lambda exc: exc
        handler._backoff = lambda **kwargs: None

        with patch("azure.servicebus._base_handler.time.time", lambda: clock["now"]):
            result = handler._do_retryable_operation(
                operation,
                timeout=30,
                operation_requires_timeout=True,
                apply_try_timeout=True,
            )

        assert result == "ok"
        # Caller's remaining time went 30 -> 20 -> 10, yet every attempt still
        # received the full 5s per-attempt budget.
        assert seen == [5, 5, 5]

    def test_without_the_knob_the_budget_visibly_shrinks(self):
        # Control for the test above: with the knob off, the same scenario shows the caller's single
        # budget decaying across attempts.
        handler = self._make_handler(try_timeout=None)
        seen = []
        clock = {"now": 1000.0}

        def operation(**kwargs):
            seen.append(kwargs.get("timeout"))
            if len(seen) < 3:
                clock["now"] += 10
                raise ValueError("transient")
            return "ok"

        handler._handle_exception = lambda exc: exc
        handler._backoff = lambda **kwargs: None

        with patch("azure.servicebus._base_handler.time.time", lambda: clock["now"]):
            handler._do_retryable_operation(
                operation,
                timeout=30,
                operation_requires_timeout=True,
                apply_try_timeout=True,
            )

        assert seen == [30, 20, 10]


class TestLinkAcquisitionIsBounded:
    """The unbounded `client_ready()` poll was a Python-only gap; .NET, Java and Go all bound it."""

    def _receiver(self, try_timeout):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock(), try_timeout=try_timeout)
        receiver = client.get_queue_receiver("q")
        receiver._create_handler = lambda auth: None
        return receiver

    def _never_ready_handler(self):
        handler = MagicMock()
        handler._shutdown = True
        handler.client_ready.return_value = False
        return handler

    def test_open_times_out_when_link_never_becomes_ready(self):
        # The gap this closes: previously this loop had no bound and could spin forever.
        receiver = self._receiver(try_timeout=0.2)
        receiver._handler = self._never_ready_handler()

        with patch("azure.servicebus._servicebus_receiver.create_authentication", lambda c: None):
            with pytest.raises(OperationTimeoutError):
                receiver._open(timeout=0.2)

    def test_open_is_unbounded_when_knob_is_off(self):
        # Default behavior is unchanged: no timeout means no deadline.
        receiver = self._receiver(try_timeout=None)
        receiver._handler = self._never_ready_handler()
        ready = {"n": 0}

        def client_ready():
            ready["n"] += 1
            return ready["n"] > 3  # becomes ready after a few polls

        receiver._handler.client_ready = client_ready

        with patch("azure.servicebus._servicebus_receiver.create_authentication", lambda c: None):
            receiver._open(timeout=None)

        assert receiver._running is True

    def test_open_with_retry_opts_in(self):
        # `_open_with_retry` must pass the per-attempt bound through to `_open`.
        receiver = self._receiver(try_timeout=7)
        seen = []

        receiver._open = lambda timeout=None: seen.append(timeout)
        receiver._open_with_retry()

        assert seen == [7]

    def test_open_with_retry_passes_nothing_when_knob_is_off(self):
        receiver = self._receiver(try_timeout=None)
        seen = []

        receiver._open = lambda timeout=None: seen.append(timeout)
        receiver._open_with_retry()

        assert seen == [None]

    def test_timeout_error_is_retryable(self):
        # A per-attempt expiry must be retried, not surfaced as a terminal failure - the behavior
        # Go gets from ErrTryTimeoutExhausted / RecoveryKindNone. Python needs no sentinel because
        # OperationTimeoutError is already retryable.
        assert OperationTimeoutError()._retryable is True


class TestSendIsBounded:
    """Sending opts in, matching Go, where every call through the retry loop is bounded."""

    def _sender(self, try_timeout):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock(), try_timeout=try_timeout)
        sender = client.get_queue_sender("q")
        sender._check_live = lambda: None
        return sender

    def _message(self):
        from azure.servicebus import ServiceBusMessage

        return ServiceBusMessage("m")

    def test_send_is_bounded_by_try_timeout(self):
        # Drives the real call site, so removing `apply_try_timeout=True` there fails loudly.
        sender = self._sender(try_timeout=5)
        seen = []

        sender._send = lambda **kwargs: seen.append(kwargs.get("timeout", "unset"))
        sender.send_messages(self._message())

        assert seen == [5]

    def test_send_is_capped_by_the_callers_timeout(self):
        # The caller's remaining time still wins when it is the smaller of the two.
        sender = self._sender(try_timeout=30)
        seen = []

        sender._send = lambda **kwargs: seen.append(kwargs.get("timeout", "unset"))
        sender.send_messages(self._message(), timeout=2)

        assert len(seen) == 1
        assert seen[0] == pytest.approx(2, abs=1)

    def test_send_is_unbounded_when_knob_is_off(self):
        # Default behavior is unchanged.
        sender = self._sender(try_timeout=None)
        seen = []

        sender._send = lambda **kwargs: seen.append(kwargs.get("timeout", "unset"))
        sender.send_messages(self._message())

        assert seen == ["unset"]


class TestLongPollIsNeverTruncated:
    """The bound must not reach the receive long poll or iterator; drives the real call sites."""

    def _receiver(self, try_timeout):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient(
            "fake.servicebus.windows.net",
            MagicMock(),
            try_timeout=try_timeout,
        )
        receiver = client.get_queue_receiver("q")
        assert receiver._config.try_timeout == try_timeout
        receiver._check_live = lambda: None
        return receiver

    def test_receive_messages_keeps_the_callers_wait(self):
        # A caller asking for a 300s wait must get 300s, not the 5s per-attempt value.
        receiver = self._receiver(try_timeout=5)
        seen = []

        def fake_receive(**kwargs):
            seen.append(kwargs.get("timeout"))
            return []

        receiver._receive = fake_receive
        receiver.receive_messages(max_message_count=1, max_wait_time=300)

        assert len(seen) == 1
        assert seen[0] == pytest.approx(300, abs=1)

    def test_try_timeout_does_not_reach_the_receive_call(self):
        # The per-attempt knob must not be passed down as the receive wait. The receive has its
        # own default bound (see TestReceiveHasADefaultBound); it must not be `try_timeout`.
        receiver = self._receiver(try_timeout=5)
        seen = []

        def fake_receive(**kwargs):
            seen.append(kwargs.get("timeout", "unset"))
            return []

        receiver._receive = fake_receive
        receiver.receive_messages(max_message_count=1)

        assert seen == ["unset"]

    def test_streaming_iterator_keeps_the_callers_wait(self):
        # The receive-forever iterator must not be truncated either.
        receiver = self._receiver(try_timeout=5)
        seen = []

        def fake_iter_next(**kwargs):
            seen.append(kwargs.get("wait_time"))
            raise StopIteration

        receiver._iter_next = fake_iter_next
        receiver._message_iter = iter([])

        with pytest.raises(StopIteration):
            receiver._do_retryable_operation(receiver._iter_next, wait_time=300)

        assert seen == [300]


class TestReceiveHasADefaultBound:
    """`receive_messages()` with no wait had no deadline: `abs_timeout` was 0 so the guard never fired."""

    def _receiver(self, max_wait_time=None):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q", max_wait_time=max_wait_time)
        receiver._check_live = lambda: None
        receiver._open = lambda timeout=None: None
        return receiver

    def _seconds_waited(self, receiver, **kwargs):
        """Drive the real _receive loop against a handler that never yields a message.

        The fake clock advances one second per poll, so the number of polls is the deadline.
        """
        from queue import Queue

        handler = MagicMock()
        handler._received_messages = Queue()
        clock = {"t": 0.0}

        def do_work():
            clock["t"] += 1.0
            return True

        handler.do_work = do_work
        receiver._handler = handler

        transport = MagicMock()
        transport.TIMEOUT_FACTOR = 1
        transport.get_current_time = lambda _client: clock["t"]
        receiver._amqp_transport = transport

        assert receiver._receive(max_message_count=1, **kwargs) == []
        return clock["t"]

    def test_no_wait_anywhere_falls_back_to_the_default(self):
        # The gap this closes: previously unbounded.
        waited = self._seconds_waited(self._receiver())
        assert waited == pytest.approx(DEFAULT_RECEIVE_WAIT_TIME_SECS, abs=2)

    def test_explicit_call_wait_wins(self):
        # A caller asking for 5s must get 5s, not the 60s default.
        waited = self._seconds_waited(self._receiver(), timeout=5)
        assert waited == pytest.approx(5, abs=2)

    def test_receiver_level_wait_wins(self):
        # `max_wait_time` on the receiver also takes precedence over the default.
        waited = self._seconds_waited(self._receiver(max_wait_time=8))
        assert waited == pytest.approx(8, abs=2)

    def test_call_wait_beats_receiver_wait(self):
        waited = self._seconds_waited(self._receiver(max_wait_time=30), timeout=3)
        assert waited == pytest.approx(3, abs=2)

    def test_a_long_explicit_wait_is_never_truncated(self):
        # The safety property: an explicit long poll must outlive the default.
        waited = self._seconds_waited(self._receiver(), timeout=300)
        assert waited == pytest.approx(300, abs=2)


class TestAsyncReceiveHasADefaultBound:
    """Async `_receive` is a separate implementation, so it needs its own coverage."""

    def _receiver(self, max_wait_time=None):
        from azure.servicebus.aio import ServiceBusClient as AsyncClient

        client = AsyncClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q", max_wait_time=max_wait_time)
        receiver._check_live = lambda: None

        async def _open(timeout=None):
            return None

        receiver._open = _open
        return receiver

    async def _seconds_waited(self, receiver, **kwargs):
        from queue import Queue

        handler = MagicMock()
        handler._received_messages = Queue()
        clock = {"t": 0.0}

        async def do_work_async():
            clock["t"] += 1.0
            return True

        handler.do_work_async = do_work_async
        receiver._handler = handler

        transport = MagicMock()
        transport.TIMEOUT_FACTOR = 1
        transport.get_current_time = lambda _client: clock["t"]

        async def reset_link_credit_async(_client, _credit):
            return None

        transport.reset_link_credit_async = reset_link_credit_async
        receiver._amqp_transport = transport

        assert await receiver._receive(max_message_count=1, **kwargs) == []
        return clock["t"]

    @pytest.mark.asyncio
    async def test_no_wait_anywhere_falls_back_to_the_default(self):
        waited = await self._seconds_waited(self._receiver())
        assert waited == pytest.approx(DEFAULT_RECEIVE_WAIT_TIME_SECS, abs=2)

    @pytest.mark.asyncio
    async def test_explicit_call_wait_wins(self):
        waited = await self._seconds_waited(self._receiver(), timeout=5)
        assert waited == pytest.approx(5, abs=2)

    @pytest.mark.asyncio
    async def test_receiver_level_wait_wins(self):
        waited = await self._seconds_waited(self._receiver(max_wait_time=8))
        assert waited == pytest.approx(8, abs=2)

    @pytest.mark.asyncio
    async def test_a_long_explicit_wait_is_never_truncated(self):
        waited = await self._seconds_waited(self._receiver(), timeout=300)
        assert waited == pytest.approx(300, abs=2)


class TestLinkAcquisitionIsBoundedInsideOperations:
    """Send and management open the link internally, so timing only the operation left it unbounded."""

    def _never_ready(self):
        handler = MagicMock()
        handler._shutdown = True
        handler.client_ready.return_value = False
        return handler

    def test_send_bounds_link_acquisition(self):
        from azure.servicebus import ServiceBusClient, ServiceBusMessage

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock(), try_timeout=0.2)
        sender = client.get_queue_sender("q")
        sender._check_live = lambda: None
        handler = self._never_ready()
        # _open closes any existing handler first, so re-supply it on create.
        sender._create_handler = lambda auth: setattr(sender, "_handler", handler)
        sender._handler = handler

        with patch("azure.servicebus._servicebus_sender.create_authentication", lambda c: None):
            with pytest.raises(OperationTimeoutError) as exc:
                sender.send_messages(ServiceBusMessage("m"))

        # The original link message must survive the retry wrapper rather than be replaced
        # wholesale by the NEXT_AVAILABLE_SESSION guidance.
        assert "AMQP link" in str(exc.value)

    def test_management_bounds_link_acquisition(self):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock(), try_timeout=0.2)
        receiver = client.get_queue_receiver("q")
        receiver._check_live = lambda: None
        receiver._create_handler = lambda auth: None
        receiver._handler = self._never_ready()

        with patch("azure.servicebus._servicebus_receiver.create_authentication", lambda c: None):
            with pytest.raises(OperationTimeoutError) as exc:
                receiver._mgmt_request_response_with_retry(b"op", {}, lambda *a: None, timeout=0.2)

        assert "AMQP link" in str(exc.value)


class TestExhaustedBudgetDoesNotBecomeUnbounded:
    """A used-up budget must raise: both transports read a zero timeout as "wait forever"."""

    def test_raises_when_no_time_is_left(self):
        started = time.time() - 5  # the whole 5s budget already spent
        with pytest.raises(OperationTimeoutError):
            get_remaining_timeout(5, started)

    def test_raises_when_the_budget_is_overrun(self):
        started = time.time() - 30
        with pytest.raises(OperationTimeoutError):
            get_remaining_timeout(5, started)

    def test_never_returns_zero(self):
        # The dangerous value specifically: 0 means unbounded downstream.
        for spent in (0.999999, 1.0, 1.000001):
            try:
                left = get_remaining_timeout(1.0, time.time() - spent)
            except OperationTimeoutError:
                continue
            assert left > 0

    def test_unbounded_stays_unbounded(self):
        assert get_remaining_timeout(None, time.time() - 100) is None

    def test_returns_what_is_left(self):
        left = get_remaining_timeout(10, time.time() - 2)
        assert left == pytest.approx(8, abs=0.5)


class TestDeadlineSentinels:
    """Only None may mean unbounded; a falsy check would make an exhausted budget read as no bound."""

    def test_zero_timeout_is_an_expired_deadline_not_unbounded(self):
        deadline = get_link_ready_deadline(0)
        assert deadline is not None
        with pytest.raises(OperationTimeoutError):
            check_link_ready_deadline(deadline)

    def test_negative_timeout_is_an_expired_deadline(self):
        deadline = get_link_ready_deadline(-1)
        assert deadline is not None
        with pytest.raises(OperationTimeoutError):
            check_link_ready_deadline(deadline)

    def test_none_timeout_is_unbounded(self):
        assert get_link_ready_deadline(None) is None
        check_link_ready_deadline(None)  # must not raise

    def test_future_deadline_does_not_raise(self):
        check_link_ready_deadline(time.time() + 30)

    def test_open_with_zero_timeout_raises(self):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q")
        receiver._create_handler = lambda auth: None
        handler = MagicMock()
        handler._shutdown = True
        handler.client_ready.return_value = False
        receiver._handler = handler

        with patch("azure.servicebus._servicebus_receiver.create_authentication", lambda c: None):
            with pytest.raises(OperationTimeoutError):
                receiver._open(timeout=0)


class TestSettlementIsNotBounded:
    """Settlement is documented as excluded; pin it so opting it in fails loudly."""

    def _receiver(self):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock(), try_timeout=5)
        receiver = client.get_queue_receiver("q")
        receiver._check_live = lambda: None
        return receiver

    def test_settle_message_never_receives_a_timeout(self):
        from azure.servicebus import ServiceBusReceivedMessage

        receiver = self._receiver()
        seen = []
        receiver._settle_message = lambda **kwargs: seen.append(kwargs.get("timeout", "unset"))
        receiver._check_message_alive = lambda m, op: None

        message = MagicMock(spec=ServiceBusReceivedMessage)
        message._settled = False
        message._lock_expired = False
        message.auto_renew_error = None
        receiver._settle_message_with_retry(message, "completed")

        assert seen == ["unset"]


class TestAsyncLinkAcquisitionIsBounded:
    """The async send path is a separate implementation from its sync twin."""

    @pytest.mark.asyncio
    async def test_async_send_bounds_link_acquisition(self):
        from azure.servicebus import ServiceBusMessage
        from azure.servicebus.aio import ServiceBusClient as AsyncClient

        client = AsyncClient("fake.servicebus.windows.net", MagicMock(), try_timeout=0.2)
        sender = client.get_queue_sender("q")
        sender._check_live = lambda: None

        handler = MagicMock()

        async def close_async():
            return None

        async def open_async(connection=None):
            return None

        async def client_ready_async():
            return False

        handler.close_async = close_async
        handler.open_async = open_async
        handler.client_ready_async = client_ready_async
        sender._create_handler = lambda auth: setattr(sender, "_handler", handler)
        sender._handler = handler

        async def fake_auth(_c):
            return None

        with patch("azure.servicebus.aio._servicebus_sender_async.create_authentication", fake_auth):
            with pytest.raises(OperationTimeoutError) as exc:
                await sender.send_messages(ServiceBusMessage("m"))

        assert "AMQP link" in str(exc.value)


class TestReadyReturningTrueLateStillTimesOut:
    """client_ready() can block then return true; the loop only checks the deadline when false."""

    def _receiver(self, ready_cost):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q")
        handler = MagicMock()
        handler._shutdown = True

        def client_ready():
            time.sleep(ready_cost)  # readiness itself consumes the budget
            return True

        handler.client_ready = client_ready
        receiver._create_handler = lambda auth: setattr(receiver, "_handler", handler)
        receiver._handler = handler
        return receiver

    def test_ready_after_the_deadline_raises(self):
        receiver = self._receiver(ready_cost=0.3)
        with patch("azure.servicebus._servicebus_receiver.create_authentication", lambda c: None):
            with pytest.raises(OperationTimeoutError):
                receiver._open(timeout=0.1)
        assert receiver._running is False

    def test_ready_within_the_deadline_still_opens(self):
        receiver = self._receiver(ready_cost=0.0)
        with patch("azure.servicebus._servicebus_receiver.create_authentication", lambda c: None):
            receiver._open(timeout=30)
        assert receiver._running is True


class TestExpiredAuthDoesNotEnterOpen:
    """open() cannot be cancelled once entered, so an exhausted budget must stop before it."""

    def _receiver(self, auth_cost):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q")
        handler = MagicMock()
        handler._shutdown = True
        handler.client_ready.return_value = True
        receiver._create_handler = lambda auth: setattr(receiver, "_handler", handler)
        receiver._handler = handler
        self.handler = handler

        def slow_auth(_c):
            time.sleep(auth_cost)  # credential acquisition consumes the budget
            return None

        self.slow_auth = slow_auth
        return receiver

    def test_open_is_not_entered_when_auth_used_the_budget(self):
        receiver = self._receiver(auth_cost=0.3)
        with patch("azure.servicebus._servicebus_receiver.create_authentication", self.slow_auth):
            with pytest.raises(OperationTimeoutError):
                receiver._open(timeout=0.1)
        self.handler.open.assert_not_called()
        assert receiver._running is False

    def test_open_is_entered_when_budget_remains(self):
        receiver = self._receiver(auth_cost=0.0)
        with patch("azure.servicebus._servicebus_receiver.create_authentication", self.slow_auth):
            receiver._open(timeout=30)
        self.handler.open.assert_called_once()
        assert receiver._running is True
