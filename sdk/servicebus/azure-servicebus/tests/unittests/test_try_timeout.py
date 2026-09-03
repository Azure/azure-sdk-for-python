# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# --------------------------------------------------------------------------

"""Unit tests for the opt-in per-attempt timeout (`try_timeout`).

`try_timeout` bounds a single attempt of an operation rather than the whole operation. It
applies to sending, to management operations, and to AMQP link acquisition, where the wait for
the link to become ready was previously unbounded. That includes the link acquisition performed
by `receive_messages` and by the streaming iterator. It must be greater than 0 if given, and is
off by default.

It deliberately does not apply to the receive long poll or the iterator's own wait: bounding
those would silently truncate a caller who asked for a long wait. That exclusion is the
safety property these tests exist to pin.

Mirrors `TryTimeout` in the Go SDK (Azure/azure-sdk-for-go#27176), which is likewise opt-in
and off by default, and the same concept in the .NET (`ServiceBusRetryOptions.TryTimeout`) and
Java (`AmqpRetryOptions.tryTimeout`) SDKs, which default it on at 60 seconds.
"""

import asyncio  # pylint:disable=do-not-import-asyncio
import time

from unittest.mock import MagicMock, patch

import azure.servicebus._common.utils as utils_module
import azure.servicebus._servicebus_receiver as sync_receiver_module
import azure.servicebus.aio._servicebus_receiver_async as async_receiver_module

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


class VirtualClock:
    """A fake clock so deadline tests do not depend on real scheduling.

    Real-time budgets make these tests flaky: a GC pause or a descheduled CI worker can
    cross a 20 ms deadline before the code under test runs at all. Here time only moves
    when the code sleeps, or when a test explicitly injects a stall.
    """

    def __init__(self, stall_before_first_check=0.0):
        self.now = 1000.0
        self._stall = stall_before_first_check
        self._reads = 0

    def time(self):
        self._reads += 1
        value = self.now
        if self._reads == 1:
            # The first read creates the deadline; charge the injected stall to it.
            self.now += self._stall
        return value

    def sleep(self, seconds):
        self.now += seconds

    async def sleep_async(self, seconds):
        self.now += seconds


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

    def test_non_positive_values_are_rejected(self):
        # Every other timeout keyword validates, and silently disabling the bound on a
        # mistyped value would remove the protection the caller asked for.
        for bad in (0, -1):
            with pytest.raises(ValueError) as exc:
                Configuration(
                    hostname="fake.servicebus.windows.net",
                    amqp_transport=MagicMock(),
                    try_timeout=bad,
                )
            assert "try_timeout" in str(exc.value)

    def test_non_finite_values_are_rejected(self):
        # NaN and infinity pass a `<= 0` check but yield a deadline that never expires,
        # so they would disable the bound rather than reject it.
        for bad in (float("nan"), float("inf")):
            with pytest.raises(ValueError) as exc:
                Configuration(
                    hostname="fake.servicebus.windows.net",
                    amqp_transport=MagicMock(),
                    try_timeout=bad,
                )
            assert "try_timeout" in str(exc.value)

    def test_positive_value_is_preserved(self):
        config = Configuration(
            hostname="fake.servicebus.windows.net",
            amqp_transport=MagicMock(),
            try_timeout=5,
        )
        assert config.try_timeout == 5
        assert get_attempt_timeout(30, config.try_timeout) == 5


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

        # The receive gets the default 60s budget, not the 5s try_timeout.
        assert seen[0] == pytest.approx(DEFAULT_RECEIVE_WAIT_TIME_SECS, abs=1)

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

        # retry_total=1 still exercises the retry wrapper but keeps the real backoff short.
        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock(), try_timeout=0.2, retry_total=1)
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

        # retry_total=1 still exercises the retry wrapper but keeps the real backoff short.
        client = AsyncClient("fake.servicebus.windows.net", MagicMock(), try_timeout=0.2, retry_total=1)
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


class TestReceiveUsesOneBudget:
    """Acquisition and polling share the receive budget rather than each getting a full one."""

    def _receiver(self, open_cost, max_wait_time=None, try_timeout=None):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock(), try_timeout=try_timeout)
        receiver = client.get_queue_receiver("q", max_wait_time=max_wait_time)
        receiver._check_live = lambda: None
        self.open_timeouts = []
        self.clock = VirtualClock()

        def slow_open(timeout=None):
            self.open_timeouts.append(timeout)
            self.clock.sleep(open_cost)  # virtual, so the budget maths is exact

        receiver._open = slow_open
        return receiver

    def _polled_seconds(self, receiver, **kwargs):
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
        transport.get_current_time = lambda _c: clock["t"]
        receiver._amqp_transport = transport
        with patch.object(sync_receiver_module, "time", self.clock):
            assert receiver._receive(max_message_count=1, **kwargs) == []
        return clock["t"]

    def test_open_time_is_deducted_from_the_poll_window(self):
        # Budget 10s, acquisition spends 4s, so polling gets 6s - not another full 10s.
        # do_work advances the transport clock 1s per tick and stops on the first tick past the
        # window, so a 6s window ends at t=7. A fresh 10s budget would have ended at t=11.
        receiver = self._receiver(open_cost=4.0, max_wait_time=10)
        assert self._polled_seconds(receiver) == 7

    def test_try_timeout_caps_acquisition_not_the_poll(self):
        # try_timeout bounds only the open phase; the long poll keeps the caller's wait.
        receiver = self._receiver(open_cost=0.0, max_wait_time=300, try_timeout=5)
        polled = self._polled_seconds(receiver)
        assert self.open_timeouts == [5]
        assert polled == 301  # 300s window, stopping on the first tick past it

    def test_acquisition_gets_the_budget_when_try_timeout_is_off(self):
        receiver = self._receiver(open_cost=0.0, max_wait_time=30)
        self._polled_seconds(receiver)
        assert self.open_timeouts == [30]

    def test_zero_budget_does_not_select_the_default(self):
        # A zero wait is expired, not absent: it must not fall through to the 60s default.
        receiver = self._receiver(open_cost=0.0)
        assert self._polled_seconds(receiver, timeout=0) == 0


class TestAsyncReceiveUsesOneBudget:
    """Async `_receive` is a separate implementation, so the single-budget rule needs its own test."""

    def _receiver(self, open_cost, max_wait_time=None, try_timeout=None):
        from azure.servicebus.aio import ServiceBusClient as AsyncClient

        client = AsyncClient("fake.servicebus.windows.net", MagicMock(), try_timeout=try_timeout)
        receiver = client.get_queue_receiver("q", max_wait_time=max_wait_time)
        receiver._check_live = lambda: None
        self.open_timeouts = []
        self.clock = VirtualClock()

        async def slow_open(timeout=None):
            self.open_timeouts.append(timeout)
            self.clock.sleep(open_cost)  # virtual, so the budget maths is exact

        receiver._open = slow_open
        return receiver

    async def _polled_seconds(self, receiver, **kwargs):
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
        transport.get_current_time = lambda _c: clock["t"]

        async def reset_link_credit_async(_c, _n):
            return None

        transport.reset_link_credit_async = reset_link_credit_async
        receiver._amqp_transport = transport
        with patch.object(async_receiver_module, "time", self.clock):
            assert await receiver._receive(max_message_count=1, **kwargs) == []
        return clock["t"]

    @pytest.mark.asyncio
    async def test_open_time_is_deducted_from_the_poll_window(self):
        # 6s of window left after a 4s acquisition; the loop stops on the first tick past it.
        receiver = self._receiver(open_cost=4.0, max_wait_time=10)
        assert await self._polled_seconds(receiver) == 7

    @pytest.mark.asyncio
    async def test_try_timeout_caps_acquisition_not_the_poll(self):
        receiver = self._receiver(open_cost=0.0, max_wait_time=300, try_timeout=5)
        polled = await self._polled_seconds(receiver)
        assert self.open_timeouts == [5]
        assert polled == 301  # 300s window, stopping on the first tick past it

    @pytest.mark.asyncio
    async def test_acquisition_gets_the_budget_when_try_timeout_is_off(self):
        receiver = self._receiver(open_cost=0.0, max_wait_time=30)
        await self._polled_seconds(receiver)
        assert self.open_timeouts == [30]

    @pytest.mark.asyncio
    async def test_zero_budget_does_not_select_the_default(self):
        receiver = self._receiver(open_cost=0.0)
        assert await self._polled_seconds(receiver, timeout=0) == 0


class TestExpiredBudgetStillDrainsPrefetched:
    """An exhausted budget must not discard messages prefetch already queued.

    `_open()` can queue messages while completing, so returning early on an expired budget
    without checking the queue would drop messages the client already holds.
    """

    def _drive(self, queued, open_cost, max_wait_time=10):
        from queue import Queue
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q", max_wait_time=max_wait_time)
        receiver._check_live = lambda: None
        receiver._build_received_message = lambda m: m

        q = Queue()
        handler = MagicMock()
        handler._received_messages = q

        def slow_open(timeout=None):
            time.sleep(open_cost)
            for m in queued:  # prefetch delivers while the link is coming up
                q.put(m)

        receiver._open = slow_open
        receiver._handler = handler
        clock = {"t": 0.0}

        def do_work():
            clock["t"] += 1.0
            return True

        handler.do_work = do_work
        transport = MagicMock()
        transport.TIMEOUT_FACTOR = 1
        transport.get_current_time = lambda _c: clock["t"]
        receiver._amqp_transport = transport
        return receiver._receive(max_message_count=10)

    def test_queued_messages_survive_an_expired_budget(self):
        # Budget fully spent opening, but prefetch already delivered two messages.
        got = self._drive(queued=["m1", "m2"], open_cost=1.2, max_wait_time=1)
        assert got == ["m1", "m2"]

    def test_empty_queue_at_expiry_still_returns_empty(self):
        got = self._drive(queued=[], open_cost=1.2, max_wait_time=1)
        assert got == []


class TestAsyncExpiredBudgetStillDrainsPrefetched:
    """Async mirror: `_receive` is a separate implementation and needs its own coverage."""

    async def _drive(self, queued, open_cost, max_wait_time=10):
        from queue import Queue
        from azure.servicebus.aio import ServiceBusClient as AsyncClient

        client = AsyncClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q", max_wait_time=max_wait_time)
        receiver._check_live = lambda: None
        receiver._build_received_message = lambda m: m

        q = Queue()
        handler = MagicMock()
        handler._received_messages = q

        async def slow_open(timeout=None):
            time.sleep(open_cost)
            for m in queued:  # prefetch delivers while the link is coming up
                q.put(m)

        receiver._open = slow_open
        receiver._handler = handler
        clock = {"t": 0.0}

        async def do_work_async():
            clock["t"] += 1.0
            return True

        handler.do_work_async = do_work_async
        transport = MagicMock()
        transport.TIMEOUT_FACTOR = 1
        transport.get_current_time = lambda _c: clock["t"]

        async def reset_link_credit_async(_c, _n):
            return None

        transport.reset_link_credit_async = reset_link_credit_async
        receiver._amqp_transport = transport
        return await receiver._receive(max_message_count=10)

    @pytest.mark.asyncio
    async def test_queued_messages_survive_an_expired_budget(self):
        got = await self._drive(queued=["m1", "m2"], open_cost=1.2, max_wait_time=1)
        assert got == ["m1", "m2"]

    @pytest.mark.asyncio
    async def test_empty_queue_at_expiry_still_returns_empty(self):
        got = await self._drive(queued=[], open_cost=1.2, max_wait_time=1)
        assert got == []


class TestExpiredBudgetDoesNotIssueLinkCredit:
    """An exhausted budget must not ask the broker for more messages.

    Issuing credit makes the broker lock messages this call can no longer return, so they
    sit unavailable until the lock expires rather than going to the next caller.
    """

    def _drive(self, queued, open_cost, max_wait_time, credit_calls):
        from queue import Queue
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q", max_wait_time=max_wait_time)
        receiver._check_live = lambda: None
        receiver._build_received_message = lambda m: m

        q = Queue()
        handler = MagicMock()
        handler._received_messages = q

        def slow_open(timeout=None):
            time.sleep(open_cost)
            for m in queued:
                q.put(m)

        receiver._open = slow_open
        receiver._handler = handler
        clock = {"t": 0.0}

        def do_work():
            clock["t"] += 1.0
            return True

        handler.do_work = do_work
        transport = MagicMock()
        transport.TIMEOUT_FACTOR = 1
        transport.get_current_time = lambda _c: clock["t"]
        transport.reset_link_credit = lambda _c, n: credit_calls.append(n)
        receiver._amqp_transport = transport
        # prefetch_count 0 is the default, and the only mode that issues credit here
        receiver._prefetch_count = 0
        return receiver._receive(max_message_count=10)

    def test_no_credit_is_issued_once_the_budget_is_spent(self):
        credit_calls = []
        # One queued message, ten asked for: the batch is short, so credit would normally follow.
        got = self._drive(queued=["m1"], open_cost=1.2, max_wait_time=1, credit_calls=credit_calls)
        assert got == ["m1"]
        assert credit_calls == [], f"issued credit with no budget left: {credit_calls}"

    def test_credit_is_still_issued_while_budget_remains(self):
        credit_calls = []
        self._drive(queued=["m1"], open_cost=0.0, max_wait_time=10, credit_calls=credit_calls)
        assert credit_calls == [9]


class TestAsyncSettlementIsNotBounded:
    """Async settlement must use the direct request path like sync, not the retry wrapper.

    The wrapper opts into try_timeout, which the docs exclude for settlement, and it nests a
    retry inside the one _settle_message_with_retry already provides.
    """

    def _receiver(self):
        from azure.servicebus.aio import ServiceBusClient as AsyncClient

        client = AsyncClient("fake.servicebus.windows.net", MagicMock(), try_timeout=5)
        receiver = client.get_queue_receiver("q")
        receiver._check_live = lambda: None
        receiver._populate_message_properties = lambda m: None
        return receiver

    @pytest.mark.asyncio
    async def test_settlement_uses_the_direct_request_path(self):
        receiver = self._receiver()
        direct, wrapped = [], []

        async def fake_direct(*args, **kwargs):
            direct.append(kwargs.get("timeout", "unset"))
            return None

        async def fake_wrapped(*args, **kwargs):
            wrapped.append(kwargs)
            return None

        receiver._mgmt_request_response = fake_direct
        receiver._mgmt_request_response_with_retry = fake_wrapped
        await receiver._settle_message_via_mgmt_link("completed", ["tok"])

        assert wrapped == []  # the retry wrapper must not be used
        assert direct == ["unset"]  # and no timeout is applied

    @pytest.mark.asyncio
    async def test_settle_message_never_receives_a_timeout(self):
        # Mirrors the sync coverage in TestSettlementIsNotBounded.
        from azure.servicebus import ServiceBusReceivedMessage

        receiver = self._receiver()
        seen = []

        async def fake_settle(**kwargs):
            seen.append(kwargs.get("timeout", "unset"))

        receiver._settle_message = fake_settle
        receiver._check_message_alive = lambda m, op: None

        message = MagicMock(spec=ServiceBusReceivedMessage)
        message._settled = False
        message._lock_expired = False
        message.auto_renew_error = None
        await receiver._settle_message_with_retry(message, "completed")

        assert seen == ["unset"]


class TestSleepCrossingDeadlineStopsPolling:
    """The 50 ms sleep can cross the deadline, so readiness must not be entered again.

    Readiness can block once entered, so checking only before the sleep is not enough:
    the deadline must be re-checked before every readiness call.
    """

    def _receiver(self, calls):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q")
        handler = MagicMock()
        handler._shutdown = True  # already shut down, so no close happens first

        def client_ready():
            calls.append(1)
            return False  # never ready, so the loop relies on the deadline

        handler.client_ready = client_ready
        receiver._create_handler = lambda auth: setattr(receiver, "_handler", handler)
        receiver._handler = handler
        return receiver

    def test_second_readiness_call_is_not_entered_after_the_sleep_expires(self):
        calls = []
        receiver = self._receiver(calls)
        clock = VirtualClock()
        # Budget smaller than one 50 ms sleep: the first call fits, the sleep exhausts it.
        with patch.object(utils_module, "time", clock), patch.object(sync_receiver_module, "time", clock):
            with patch("azure.servicebus._servicebus_receiver.create_authentication", lambda c: None):
                with pytest.raises(OperationTimeoutError):
                    receiver._open(timeout=0.02)
        assert len(calls) == 1, f"readiness entered {len(calls)} times, expected 1"

    def test_polling_continues_while_budget_remains(self):
        calls = []
        receiver = self._receiver(calls)
        clock = VirtualClock()
        with patch.object(utils_module, "time", clock), patch.object(sync_receiver_module, "time", clock):
            with patch("azure.servicebus._servicebus_receiver.create_authentication", lambda c: None):
                with pytest.raises(OperationTimeoutError):
                    receiver._open(timeout=0.4)
        assert len(calls) > 1


class TestAsyncSleepCrossingDeadlineStopsPolling:
    """Async mirror: readiness is a separate implementation."""

    def _receiver(self, calls):
        from azure.servicebus.aio import ServiceBusClient as AsyncClient

        client = AsyncClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q")
        handler = MagicMock()
        handler._shutdown = True

        async def close_async():
            return None

        async def open_async(connection=None):
            return None

        async def client_ready_async():
            calls.append(1)
            return False

        handler.close_async = close_async
        handler.open_async = open_async
        handler.client_ready_async = client_ready_async
        receiver._create_handler = lambda auth: setattr(receiver, "_handler", handler)
        receiver._handler = handler
        return receiver

    @pytest.mark.asyncio
    async def test_second_readiness_call_is_not_entered_after_the_sleep_expires(self):
        calls = []
        receiver = self._receiver(calls)
        clock = VirtualClock()

        async def fake_auth(_c):
            return None

        with patch.object(utils_module, "time", clock):
            with patch.object(async_receiver_module.asyncio, "sleep", clock.sleep_async):
                with patch.object(async_receiver_module, "create_authentication", fake_auth):
                    with pytest.raises(OperationTimeoutError):
                        await receiver._open(timeout=0.02)
        assert len(calls) == 1, f"readiness entered {len(calls)} times, expected 1"


class TestSlowCloseIsChargedToTheBudget:
    """Closing the previous link is link acquisition too.

    close() does network I/O. If it spends the attempt budget, authentication and open()
    must not then proceed against a fresh full timeout.
    """

    def _receiver(self, events):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q")
        handler = MagicMock()
        handler._shutdown = False  # so the close path runs
        handler.close = lambda: events.append("close")
        handler.client_ready = lambda: True
        receiver._create_handler = lambda auth: events.append("create_handler")
        receiver._handler = handler
        return receiver

    def test_a_slow_close_stops_the_attempt_before_authentication(self):
        events = []
        receiver = self._receiver(events)
        clock = VirtualClock(stall_before_first_check=0.05)  # close overruns the 20 ms budget
        with patch.object(utils_module, "time", clock), patch.object(sync_receiver_module, "time", clock):
            with patch("azure.servicebus._servicebus_receiver.create_authentication", lambda c: events.append("auth")):
                with pytest.raises(OperationTimeoutError):
                    receiver._open(timeout=0.02)
        assert events == ["close"], f"continued past a budget-consuming close: {events}"

    def test_a_fast_close_leaves_the_attempt_running(self):
        events = []
        receiver = self._receiver(events)
        clock = VirtualClock()  # close costs nothing
        with patch.object(utils_module, "time", clock), patch.object(sync_receiver_module, "time", clock):
            with patch("azure.servicebus._servicebus_receiver.create_authentication", lambda c: events.append("auth")):
                receiver._open(timeout=0.02)
        assert events == ["close", "auth", "create_handler"]


class TestAsyncSlowCloseIsChargedToTheBudget:
    """Async mirror: close_async() is awaited before the rest of link acquisition."""

    def _receiver(self, events):
        from azure.servicebus.aio import ServiceBusClient as AsyncClient

        client = AsyncClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q")
        handler = MagicMock()
        handler._shutdown = False

        async def close_async():
            events.append("close")

        async def open_async(connection=None):
            return None

        async def client_ready_async():
            return True

        handler.close_async = close_async
        handler.open_async = open_async
        handler.client_ready_async = client_ready_async
        receiver._create_handler = lambda auth: events.append("create_handler")
        receiver._handler = handler
        return receiver

    @pytest.mark.asyncio
    async def test_a_slow_close_stops_the_attempt_before_authentication(self):
        events = []
        receiver = self._receiver(events)
        clock = VirtualClock(stall_before_first_check=0.05)

        async def fake_auth(_c):
            events.append("auth")

        with patch.object(utils_module, "time", clock):
            with patch.object(async_receiver_module, "create_authentication", fake_auth):
                with pytest.raises(OperationTimeoutError):
                    await receiver._open(timeout=0.02)
        assert events == ["close"], f"continued past a budget-consuming close: {events}"

    @pytest.mark.asyncio
    async def test_a_fast_close_leaves_the_attempt_running(self):
        events = []
        receiver = self._receiver(events)
        clock = VirtualClock()  # close costs nothing

        async def fake_auth(_c):
            events.append("auth")

        with patch.object(utils_module, "time", clock):
            with patch.object(async_receiver_module, "create_authentication", fake_auth):
                await receiver._open(timeout=0.02)
        assert events == ["close", "auth", "create_handler"]


class TestRetryDoesNotRestartTheDefaultReceiveBudget:
    """The 60s default is one budget for the whole call, not one per retry attempt.

    Driven through the public receive_messages() so it covers the retry wrapper,
    which is where the budget was previously restarting.
    """

    def _receiver(self, attempts):
        from azure.servicebus import ServiceBusClient
        from azure.servicebus.exceptions import ServiceBusConnectionError

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q")
        receiver._check_live = lambda: None
        self.deadlines = []

        def fake_receive(max_message_count=None, timeout=None):
            self.deadlines.append(timeout)
            if len(self.deadlines) < attempts:
                raise ServiceBusConnectionError(message="transient")
            return []

        receiver._receive = fake_receive
        return receiver

    def test_second_attempt_inherits_the_remaining_budget(self):
        receiver = self._receiver(attempts=2)
        receiver.receive_messages()
        assert len(self.deadlines) == 2
        # Both attempts are bounded, and the second cannot exceed the first.
        assert self.deadlines[0] is not None and self.deadlines[1] is not None
        assert self.deadlines[0] <= DEFAULT_RECEIVE_WAIT_TIME_SECS
        assert self.deadlines[1] <= self.deadlines[0]

    def test_explicit_max_wait_time_is_still_one_budget(self):
        receiver = self._receiver(attempts=2)
        receiver.receive_messages(max_wait_time=5)
        assert self.deadlines[0] <= 5
        assert self.deadlines[1] <= self.deadlines[0]


class TestAsyncRetryDoesNotRestartTheDefaultReceiveBudget:
    """Async mirror: the retry wrapper is a separate implementation."""

    def _receiver(self, attempts):
        from azure.servicebus.aio import ServiceBusClient as AsyncClient
        from azure.servicebus.exceptions import ServiceBusConnectionError

        client = AsyncClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q")
        receiver._check_live = lambda: None
        self.deadlines = []

        async def fake_receive(max_message_count=None, timeout=None):
            self.deadlines.append(timeout)
            if len(self.deadlines) < attempts:
                raise ServiceBusConnectionError(message="transient")
            return []

        receiver._receive = fake_receive
        return receiver

    @pytest.mark.asyncio
    async def test_second_attempt_inherits_the_remaining_budget(self):
        receiver = self._receiver(attempts=2)
        await receiver.receive_messages()
        assert len(self.deadlines) == 2
        assert self.deadlines[0] is not None and self.deadlines[1] is not None
        assert self.deadlines[0] <= DEFAULT_RECEIVE_WAIT_TIME_SECS
        assert self.deadlines[1] <= self.deadlines[0]


class TestSessionHintOnlyForNextAvailableSession:
    """The NEXT_AVAILABLE_SESSION advice belongs to session receivers, not senders or management."""

    def _never_ready(self):
        handler = MagicMock()
        handler._shutdown = True
        handler.client_ready.return_value = False
        return handler

    def test_sender_timeout_carries_no_session_advice(self):
        from azure.servicebus import ServiceBusClient, ServiceBusMessage

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock(), try_timeout=0.2, retry_total=0)
        sender = client.get_queue_sender("q")
        sender._check_live = lambda: None
        handler = self._never_ready()
        sender._create_handler = lambda auth: setattr(sender, "_handler", handler)
        sender._handler = handler

        with patch("azure.servicebus._servicebus_sender.create_authentication", lambda c: None):
            with pytest.raises(OperationTimeoutError) as exc:
                sender.send_messages(ServiceBusMessage("m"))

        assert "AMQP link" in str(exc.value)
        assert "NEXT_AVAILABLE_SESSION" not in str(exc.value)

    def test_next_available_session_receiver_keeps_the_advice(self):
        from azure.servicebus import ServiceBusClient, NEXT_AVAILABLE_SESSION

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock(), try_timeout=0.2, retry_total=0)
        receiver = client.get_queue_receiver("q", session_id=NEXT_AVAILABLE_SESSION)
        receiver._check_live = lambda: None
        handler = self._never_ready()
        receiver._create_handler = lambda auth: setattr(receiver, "_handler", handler)
        receiver._handler = handler

        with patch("azure.servicebus._servicebus_receiver.create_authentication", lambda c: None):
            with pytest.raises(OperationTimeoutError) as exc:
                receiver.receive_messages(max_wait_time=1)

        assert "NEXT_AVAILABLE_SESSION" in str(exc.value)


class TestIteratorBoundsLinkAcquisition:
    """Iterating an unopened receiver acquires the link, so try_timeout must reach that open."""

    def _receiver(self, seen, try_timeout):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock(), try_timeout=try_timeout)
        receiver = client.get_queue_receiver("q")
        receiver._check_live = lambda: None
        receiver._open = lambda timeout=None: seen.append(timeout)
        receiver._handler = MagicMock()
        receiver._message_iter = iter([])  # exhausted, so iteration stops right after the open
        return receiver

    def test_sync_iterator_open_is_bounded(self):
        from azure.servicebus._transport._pyamqp_transport import PyamqpTransport

        seen = []
        with pytest.raises(StopIteration):
            PyamqpTransport.iter_next(self._receiver(seen, try_timeout=7))
        assert seen == [7]

    def test_sync_iterator_open_is_unbounded_when_try_timeout_is_off(self):
        from azure.servicebus._transport._pyamqp_transport import PyamqpTransport

        seen = []
        with pytest.raises(StopIteration):
            PyamqpTransport.iter_next(self._receiver(seen, try_timeout=None))
        assert seen == [None]

    def _async_receiver(self, seen, try_timeout):
        from azure.servicebus.aio import ServiceBusClient as AsyncClient

        client = AsyncClient("fake.servicebus.windows.net", MagicMock(), try_timeout=try_timeout)
        receiver = client.get_queue_receiver("q")
        receiver._check_live = lambda: None

        async def fake_open(timeout=None):
            seen.append(timeout)

        async def empty():
            for item in []:
                yield item

        receiver._open = fake_open
        receiver._handler = MagicMock()
        receiver._message_iter = empty()
        return receiver

    @pytest.mark.asyncio
    async def test_async_iterator_open_is_bounded(self):
        from azure.servicebus.aio._transport._pyamqp_transport_async import PyamqpTransportAsync

        seen = []
        with pytest.raises(StopAsyncIteration):
            await PyamqpTransportAsync.iter_next_async(self._async_receiver(seen, try_timeout=7))
        assert seen == [7]


class TestDelayedHandlerOpen:
    """A slow `open` must not run unbounded past the attempt budget.

    Sync and async differ deliberately. A blocking `open()` cannot be interrupted, so the
    sync path can only detect the overrun once it returns; an async open can be cancelled,
    so the budget bounds the open itself. These tests pin both behaviours with real elapsed
    time, since that is the property under test.
    """

    OPEN_COST = 1.0
    BUDGET = 0.05

    def test_sync_open_completes_then_raises(self):
        from azure.servicebus import ServiceBusClient

        client = ServiceBusClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q")
        handler = MagicMock()
        handler._shutdown = True
        handler.open = lambda connection=None: time.sleep(self.OPEN_COST)
        handler.client_ready = lambda: True
        receiver._create_handler = lambda auth: setattr(receiver, "_handler", handler)
        receiver._handler = handler

        started = time.time()
        with patch("azure.servicebus._servicebus_receiver.create_authentication", lambda c: None):
            with pytest.raises(OperationTimeoutError):
                receiver._open(timeout=self.BUDGET)
        elapsed = time.time() - started
        # Documents the limitation rather than hiding it: the open runs to completion.
        assert elapsed >= self.OPEN_COST

    @pytest.mark.asyncio
    async def test_async_open_is_cancelled_at_the_deadline(self):
        from azure.servicebus.aio import ServiceBusClient as AsyncClient

        client = AsyncClient("fake.servicebus.windows.net", MagicMock())
        receiver = client.get_queue_receiver("q")
        handler = MagicMock()
        handler._shutdown = True
        opened_fully = []

        async def slow_open(connection=None):
            await asyncio.sleep(self.OPEN_COST)
            opened_fully.append(1)

        async def close_async():
            return None

        async def client_ready_async():
            return True

        handler.open_async = slow_open
        handler.close_async = close_async
        handler.client_ready_async = client_ready_async
        receiver._create_handler = lambda auth: setattr(receiver, "_handler", handler)
        receiver._handler = handler

        async def fake_auth(_c):
            return None

        started = time.time()
        with patch("azure.servicebus.aio._servicebus_receiver_async.create_authentication", fake_auth):
            with pytest.raises(OperationTimeoutError):
                await receiver._open(timeout=self.BUDGET)
        elapsed = time.time() - started
        assert elapsed < self.OPEN_COST / 2, f"open was not cancelled: took {elapsed:.2f}s"
        assert not opened_fully, "open ran to completion instead of being cancelled"
