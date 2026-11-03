# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# pylint: disable=protected-access

import datetime
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from unittest.mock import Mock, call, patch

import pytest

from azure.servicebus import AutoLockRenewer
from azure.servicebus._common.message import ServiceBusReceivedMessage
from azure.servicebus._common.utils import utc_now
from azure.servicebus._servicebus_session import ServiceBusSession
from azure.servicebus.exceptions import AutoLockRenewFailed, AutoLockRenewTimeout, ServiceBusError


class _Message(ServiceBusReceivedMessage):
    locked_until_utc = property(lambda self: self._locked)
    _lock_expired = property(lambda self: False)

    def __init__(self, receiver):
        self._receiver = receiver
        self._received_timestamp_utc = utc_now()
        self._locked = utc_now() + datetime.timedelta(seconds=8)
        self._settled = False
        self._raw_amqp_message = None


class _Session(ServiceBusSession):
    locked_until_utc = property(lambda self: self._locked)
    _lock_expired = property(lambda self: False)

    def __init__(self, receiver):
        self._receiver = receiver
        self._session_start = utc_now()
        self._locked = utc_now() + datetime.timedelta(seconds=8)


class _Executor:
    def __init__(self):
        self.pending = []

    def submit(self, function, *args):
        future = Future()
        self.pending.append((future, function, args))
        return future

    def run_next(self):
        future, function, args = self.pending.pop(0)
        if future.set_running_or_notify_cancel():
            try:
                future.set_result(function(*args))
            except BaseException as error:
                future.set_exception(error)
                raise

    def shutdown(self, wait=True):
        pass


def _run_executor_until_idle(executor):
    clock = 0

    def tick(_):
        nonlocal clock
        clock += 1
        assert clock <= 20, "Dispatcher did not return to idle."
        if executor.pending:
            executor.run_next()

    with patch("azure.servicebus._common.auto_lock_renewer.time.time", side_effect=lambda: clock), patch(
        "azure.servicebus._common.auto_lock_renewer.time.sleep", side_effect=tick
    ):
        executor.run_next()


@pytest.mark.parametrize("delay", [4, 5, 6])
@pytest.mark.parametrize("renewable_type", [_Message, _Session])
def test_dispatcher_waits_for_outstanding_renewal(delay, renewable_type):
    receiver = Mock(_running=True)
    renewable = renewable_type(receiver)
    executor = _Executor()
    failures = Mock()
    renewer = AutoLockRenewer(executor=executor, on_lock_renew_failure=failures)
    renewer._is_max_workers_greater_than_one = True
    renewer._running_dispatcher.set()
    renewer._renew_tasks.put((receiver, renewable, utc_now(), 120, failures))
    clock = 0
    calls = 0

    def renew(*args):
        nonlocal calls
        calls += 1
        if calls == 2:
            receiver._running = False

    receiver.renew_message_lock.side_effect = renew
    if renewable_type is _Session:
        renewable.renew_lock = renew

    def tick(_):
        nonlocal clock
        clock += 1
        assert clock <= delay + 10, "Dispatcher did not return to idle."
        if clock >= delay and executor.pending:
            executor.run_next()

    try:
        with patch("azure.servicebus._common.auto_lock_renewer.time.time", side_effect=lambda: clock), patch(
            "azure.servicebus._common.auto_lock_renewer.time.sleep", side_effect=tick
        ):
            renewer._dispatch_worker()
        assert calls == 2
        assert renewer._renew_tasks.unfinished_tasks == 0
        assert not renewer._running_dispatcher.is_set()
        assert not executor.pending
        failures.assert_not_called()
    finally:
        renewer.close()


@pytest.mark.parametrize("failure", ["error", "timeout", "settled", "cancelled"])
def test_completed_or_cancelled_work_allows_idle_shutdown(failure):
    receiver = Mock(_running=True)
    message = _Message(receiver)
    callback = Mock()
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = True
    renewer._running_dispatcher.set()
    duration = -1 if failure == "timeout" else 120
    message._settled = failure == "settled"
    receiver.renew_message_lock.side_effect = ValueError("renewal failed")
    renewer._renew_tasks.put((receiver, message, utc_now(), duration, callback))
    clock = 0

    def tick(_):
        nonlocal clock
        clock += 1
        assert clock <= 10
        if executor.pending:
            if failure == "cancelled":
                executor.pending.pop(0)[0].cancel()
            else:
                executor.run_next()

    try:
        with patch("azure.servicebus._common.auto_lock_renewer.time.time", side_effect=lambda: clock), patch(
            "azure.servicebus._common.auto_lock_renewer.time.sleep", side_effect=tick
        ):
            renewer._dispatch_worker()
        assert renewer._renew_tasks.unfinished_tasks == 0
        assert not renewer._running_dispatcher.is_set()
        if failure == "error":
            callback.assert_called_once()
            assert isinstance(callback.call_args.args[1], AutoLockRenewFailed)
        elif failure == "timeout":
            assert isinstance(message.auto_renew_error, AutoLockRenewTimeout)
            callback.assert_not_called()
        else:
            callback.assert_not_called()
    finally:
        renewer.close()


def test_single_worker_completes_queue_accounting():
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = False
    renewer._running_dispatcher.set()
    receiver = Mock(_running=True)
    message = _Message(receiver)
    message._settled = True
    renewer._renew_tasks.put((receiver, message, utc_now(), 120))
    try:
        with patch("azure.servicebus._common.auto_lock_renewer.time.time", side_effect=[0, 0, 5]):
            renewer._dispatch_worker()
        assert renewer._renew_tasks.unfinished_tasks == 0
        assert not executor.pending
    finally:
        renewer.close()


def test_register_queues_before_starting_dispatcher():
    receiver = Mock(_running=True)
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = True

    def initialize():
        assert not renewer._renew_tasks.empty()

    try:
        with patch.object(renewer, "_init_workers", side_effect=initialize) as initialize_workers:
            renewer.register(receiver, _Message(receiver))
        initialize_workers.assert_called_once()
    finally:
        renewer.close()


def test_slow_renewal_does_not_block_another_message():
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = True
    renewer._running_dispatcher.set()
    slow = Mock(_running=True)
    fast = Mock(_running=True)
    slow_message = _Message(slow)
    fast_message = _Message(fast)
    clock = 0
    slow_calls = 0

    def renew_slow(*args):
        nonlocal slow_calls
        slow_calls += 1
        if slow_calls == 2:
            slow._running = False

    def renew_fast(*args):
        assert clock == 1
        fast._running = False

    slow.renew_message_lock.side_effect = renew_slow
    fast.renew_message_lock.side_effect = renew_fast
    for receiver, message in ((slow, slow_message), (fast, fast_message)):
        renewer._renew_tasks.put((receiver, message, utc_now(), 120))

    def tick(_):
        nonlocal clock
        clock += 1
        assert clock <= 20
        if clock == 1:
            executor.pending.reverse()
            executor.run_next()
        elif clock >= 6 and executor.pending:
            executor.run_next()

    try:
        with patch("azure.servicebus._common.auto_lock_renewer.time.time", side_effect=lambda: clock), patch(
            "azure.servicebus._common.auto_lock_renewer.time.sleep", side_effect=tick
        ):
            renewer._dispatch_worker()
        assert slow_calls == 2
        fast.renew_message_lock.assert_called_once_with(fast_message)
        assert renewer._renew_tasks.unfinished_tasks == 0
        assert not executor.pending
    finally:
        renewer.close()


@pytest.mark.parametrize("capacity", [None, False, True])
def test_closed_renewer_cannot_restart_dispatcher(capacity):
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = capacity
    renewer.close()
    with pytest.raises(ServiceBusError):
        renewer._init_workers()
    assert not executor.pending


def test_concurrent_initialization_starts_one_dispatcher():
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = True
    ready = threading.Barrier(5)
    errors = []

    def initialize():
        try:
            ready.wait(timeout=5)
            renewer._init_workers()
        except Exception as error:
            errors.append(error)

    threads = [threading.Thread(target=initialize) for _ in range(4)]
    try:
        for thread in threads:
            thread.start()
        ready.wait(timeout=5)
        for thread in threads:
            thread.join(timeout=5)
        assert all(not thread.is_alive() for thread in threads)
        assert not errors
        assert len(executor.pending) == 1
    finally:
        renewer.close()


def test_registration_during_idle_shutdown_restarts_dispatcher():
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = True
    renewer._running_dispatcher.set()
    checking_idle = threading.Event()
    registration_started = threading.Event()
    finish_idle = threading.Event()
    errors = []
    clock_calls = 0
    receiver = Mock(_running=True)
    message = _Message(receiver)
    message._locked = utc_now()

    def renew(*args):
        receiver._running = False

    receiver.renew_message_lock.side_effect = renew

    def clock():
        nonlocal clock_calls
        clock_calls += 1
        if clock_calls == 1:
            return 0
        checking_idle.set()
        assert finish_idle.wait(timeout=5)
        return 5

    def dispatch():
        try:
            renewer._dispatch_worker()
        except Exception as error:
            errors.append(error)

    def register():
        try:
            registration_started.set()
            renewer.register(receiver, message)
        except Exception as error:
            errors.append(error)

    dispatcher = threading.Thread(target=dispatch)
    registration = threading.Thread(target=register)
    try:
        with patch("azure.servicebus._common.auto_lock_renewer.time.time", side_effect=clock):
            dispatcher.start()
            assert checking_idle.wait(timeout=5)
            registration.start()
            assert registration_started.wait(timeout=5)
            finish_idle.set()
            dispatcher.join(timeout=5)
            registration.join(timeout=5)
        assert not dispatcher.is_alive()
        assert not registration.is_alive()
        assert not errors
        assert renewer._running_dispatcher.is_set()
        assert len(executor.pending) == 1
        assert renewer._renew_tasks.qsize() == 1
        _run_executor_until_idle(executor)
        receiver.renew_message_lock.assert_called_once_with(message)
        assert not executor.pending
        assert not renewer._running_dispatcher.is_set()
        assert renewer._renew_tasks.unfinished_tasks == 0
    finally:
        finish_idle.set()
        if dispatcher.ident is not None:
            dispatcher.join(timeout=5)
        if registration.ident is not None:
            registration.join(timeout=5)
        renewer.close()


@pytest.mark.parametrize("workers,supplied_executor", [(1, False), (2, False), (None, False), (1, True), (2, True)])
@pytest.mark.parametrize("renewable_type", [_Message, _Session])
def test_real_executor_renews_and_drains(workers, supplied_executor, renewable_type):
    executor = ThreadPoolExecutor(max_workers=workers) if supplied_executor else None
    renewer = AutoLockRenewer(executor=executor) if supplied_executor else AutoLockRenewer(max_workers=workers)
    renewer._sleep_time = 0.01
    receiver = Mock(_running=True)
    renewable = renewable_type(receiver)
    renewable._locked = utc_now()
    renewed = threading.Event()
    failures = Mock()

    def renew(*args):
        receiver._running = False
        renewed.set()

    operation = Mock(side_effect=renew)
    if renewable_type is _Session:
        renewable.renew_lock = operation
    else:
        receiver.renew_message_lock = operation

    with renewer:
        renewer.register(receiver, renewable, on_lock_renew_failure=failures)
        assert renewed.wait(timeout=5)
        with renewer._renew_tasks.all_tasks_done:
            assert renewer._renew_tasks.all_tasks_done.wait_for(
                lambda: renewer._renew_tasks.unfinished_tasks == 0, timeout=5
            )
        assert renewer._is_max_workers_greater_than_one is (workers is None or workers > 1)

    operation.assert_called_once()
    failures.assert_not_called()
    assert not renewer._running_dispatcher.is_set()


@pytest.mark.parametrize("workers", [1, 2])
@pytest.mark.parametrize("wait", [False, True])
def test_close_with_in_flight_renewal(workers, wait):
    renewer = AutoLockRenewer(max_workers=workers)
    renewer._sleep_time = 0.01
    receiver = Mock(_running=True)
    message = _Message(receiver)
    message._locked = utc_now()
    entered = threading.Event()
    release = threading.Event()
    closed = threading.Event()
    failures = Mock()
    errors = []

    def renew(*args):
        entered.set()
        assert release.wait(timeout=5)

    def close():
        try:
            renewer.close(wait=wait)
        except Exception as error:
            errors.append(error)
        finally:
            closed.set()

    receiver.renew_message_lock.side_effect = renew
    closer = threading.Thread(target=close)
    try:
        renewer.register(receiver, message, on_lock_renew_failure=failures)
        assert entered.wait(timeout=5)
        closer.start()
        assert renewer._shutdown.wait(timeout=5)
        if wait:
            assert not closed.is_set()
        else:
            assert closed.wait(timeout=5)
        assert renewer._renew_tasks.unfinished_tasks == 1
        release.set()
        closer.join(timeout=5)
        assert not closer.is_alive()
        assert not errors
    finally:
        release.set()
        if closer.ident is not None:
            closer.join(timeout=5)
        renewer.close()

    receiver.renew_message_lock.assert_called_once_with(message)
    failures.assert_not_called()
    assert renewer._renew_tasks.unfinished_tasks == 0
    assert renewer._renew_tasks.empty()
    assert not renewer._running_dispatcher.is_set()


def test_already_completed_future_releases_queue_accounting():
    executor = _Executor()

    def submit(function, *args):
        future = Future()
        future.set_result(function(*args))
        return future

    executor.submit = submit
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = True
    renewer._running_dispatcher.set()
    receiver = Mock(_running=True)
    message = _Message(receiver)
    message._settled = True
    renewer._renew_tasks.put((receiver, message, utc_now(), 120))
    try:
        with patch("azure.servicebus._common.auto_lock_renewer.time.time", side_effect=[0, 0, 5]):
            renewer._dispatch_worker()
        assert renewer._renew_tasks.unfinished_tasks == 0
        assert not renewer._running_dispatcher.is_set()
    finally:
        renewer.close()


@pytest.mark.parametrize("workers", [1, 2])
@pytest.mark.parametrize("renewable_type", [_Message, _Session])
@pytest.mark.parametrize("expiry", ["before", "during", "during-error"])
def test_expired_lock_notifies_once_and_releases_accounting(workers, renewable_type, expiry):
    executor = _Executor()
    callback = Mock()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = workers > 1
    receiver = Mock(_running=True, session=None)
    renewable = renewable_type(receiver)
    expired_at = utc_now() - datetime.timedelta(seconds=1)
    renewable._locked_until_utc = renewable._locked
    expiry_property = (
        ServiceBusReceivedMessage._lock_expired if renewable_type is _Message else ServiceBusSession._lock_expired
    )

    def expire(*args):
        renewable._locked = expired_at
        renewable._locked_until_utc = expired_at
        if expiry == "during-error":
            raise ValueError("Renewal failed after lock expiry.")

    operation = Mock(side_effect=expire)
    if renewable_type is _Session:
        renewable.renew_lock = operation
    else:
        receiver.renew_message_lock = operation
    if expiry == "before":
        expire()

    renewer._running_dispatcher.set()
    renewer._renew_tasks.put((receiver, renewable, utc_now(), 120, callback))
    executor.submit(renewer._dispatch_worker)
    try:
        with patch.object(renewable_type, "_lock_expired", expiry_property):
            _run_executor_until_idle(executor)
        if expiry == "before":
            operation.assert_not_called()
        else:
            operation.assert_called_once()
        if expiry == "during-error":
            assert isinstance(renewable.auto_renew_error, AutoLockRenewFailed)
            callback.assert_called_once_with(renewable, renewable.auto_renew_error)
        else:
            callback.assert_called_once_with(renewable, None)
        assert renewer._renew_tasks.empty()
        assert renewer._renew_tasks.unfinished_tasks == 0
        assert not renewer._running_dispatcher.is_set()
        assert not executor.pending
    finally:
        renewer.close()


@pytest.mark.parametrize("workers", [1, 2])
def test_raising_failure_callback_releases_accounting(workers):
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = workers > 1
    receiver = Mock(_running=True)
    message = _Message(receiver)
    receiver.renew_message_lock.side_effect = ValueError("Renewal failed.")
    callback_error = RuntimeError("Failure callback failed.")
    callback = Mock(side_effect=callback_error)
    renewer._running_dispatcher.set()
    renewer._renew_tasks.put((receiver, message, utc_now(), 120, callback))
    executor.submit(renewer._dispatch_worker)
    try:
        with patch.object(
            renewer._renew_tasks, "task_done", wraps=renewer._renew_tasks.task_done
        ) as task_done, patch.object(renewer, "_renew_task_done", wraps=renewer._renew_task_done) as completed:
            with pytest.raises(RuntimeError, match="Failure callback failed") as raised:
                _run_executor_until_idle(executor)
            task_done.assert_called_once_with()
            if workers > 1:
                completed.assert_called_once()
                assert completed.call_args.args[0].exception() is callback_error
            else:
                completed.assert_not_called()
        assert raised.value is callback_error
        callback.assert_called_once_with(message, message.auto_renew_error)
        assert isinstance(message.auto_renew_error, AutoLockRenewFailed)
        assert renewer._renew_tasks.empty()
        assert renewer._renew_tasks.unfinished_tasks == 0
        assert not executor.pending
    finally:
        renewer.close()


@pytest.mark.parametrize("workers", [1, 2])
def test_public_registration_renews_after_complete_idle_shutdown(workers):
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = workers > 1
    receiver = Mock(_running=True)
    messages = [_Message(receiver), _Message(receiver)]

    def renew(*args):
        receiver._running = False

    receiver.renew_message_lock.side_effect = renew
    try:
        for message in messages:
            receiver._running = True
            message._locked = utc_now()
            renewer.register(receiver, message)
            assert len(executor.pending) == 1
            _run_executor_until_idle(executor)
            assert renewer._renew_tasks.empty()
            assert renewer._renew_tasks.unfinished_tasks == 0
            assert not renewer._running_dispatcher.is_set()
            assert not executor.pending
        assert receiver.renew_message_lock.call_args_list == [call(message) for message in messages]
    finally:
        renewer.close()


def test_registration_before_idle_check_keeps_existing_dispatcher():
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = True
    renewer._dispatcher_timeout = 0
    renewer._sleep_time = 0.01
    renewer._running_dispatcher.set()
    checking_idle = threading.Event()
    registered = threading.Event()
    submitted = threading.Event()
    errors = []
    receiver = Mock(_running=True)
    message = _Message(receiver)
    message._locked = utc_now()
    original_empty = renewer._renew_tasks.empty
    original_submit = executor.submit

    def empty():
        result = original_empty()
        if not checking_idle.is_set():
            assert result
            checking_idle.set()
            assert registered.wait(timeout=5)
        return result

    def submit(function, *args):
        future = original_submit(function, *args)
        submitted.set()
        return future

    def renew(*args):
        receiver._running = False

    def dispatch():
        try:
            renewer._dispatch_worker()
        except Exception as error:
            errors.append(error)

    receiver.renew_message_lock.side_effect = renew
    dispatcher = threading.Thread(target=dispatch)
    try:
        with patch.object(renewer._renew_tasks, "empty", side_effect=empty), patch.object(
            executor, "submit", side_effect=submit
        ) as submit_work:
            dispatcher.start()
            assert checking_idle.wait(timeout=5)
            renewer.register(receiver, message)
            submit_work.assert_not_called()
            registered.set()
            assert submitted.wait(timeout=5)
            executor.run_next()
            dispatcher.join(timeout=5)
            assert not dispatcher.is_alive()
            assert not errors
            submit_work.assert_called_once()
            assert submit_work.call_args.args[0] == renewer._auto_lock_renew_task
        receiver.renew_message_lock.assert_called_once_with(message)
        assert not executor.pending
        assert renewer._renew_tasks.unfinished_tasks == 0
        assert not renewer._running_dispatcher.is_set()
    finally:
        registered.set()
        renewer.close()
        if dispatcher.ident is not None:
            dispatcher.join(timeout=5)


@pytest.mark.parametrize("boundary", ["enqueue", "initialize"])
def test_registration_racing_with_close_cannot_start_dispatcher(boundary):
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = True
    receiver = Mock(_running=True)
    message = _Message(receiver)
    reached = threading.Event()
    resume = threading.Event()
    errors = []
    target, name = (renewer._renew_tasks, "put") if boundary == "enqueue" else (renewer, "_init_workers")
    original = getattr(target, name)

    def pause(*args, **kwargs):
        reached.set()
        assert resume.wait(timeout=5)
        return original(*args, **kwargs)

    def register():
        try:
            renewer.register(receiver, message)
        except Exception as error:
            errors.append(error)

    registration = threading.Thread(target=register)
    try:
        with patch.object(target, name, side_effect=pause):
            registration.start()
            assert reached.wait(timeout=5)
            renewer.close()
            resume.set()
            registration.join(timeout=5)
            assert not registration.is_alive()
        assert len(errors) == 1
        assert isinstance(errors[0], ServiceBusError)
        assert not executor.pending
        assert not renewer._running_dispatcher.is_set()
        assert renewer._shutdown.is_set()
    finally:
        resume.set()
        renewer.close()
        if registration.ident is not None:
            registration.join(timeout=5)


@pytest.mark.parametrize("workers", [2, 3])
@pytest.mark.parametrize("queued_outcome", ["success", "cancelled", "failed"])
def test_saturated_executor_drains_success_cancelled_and_failed_work(workers, queued_outcome):
    callback = Mock()
    renewer = AutoLockRenewer(max_workers=workers, on_lock_renew_failure=callback)
    renewer._sleep_time = 0.01
    renewer._dispatcher_timeout = 0
    receiver = Mock(_running=True)
    messages = [_Message(receiver) for _ in range(workers + 2)]
    occupied = threading.Barrier(workers)
    release = threading.Event()
    submitted = threading.Event()
    idle_checked = threading.Event()
    futures = {}
    original_submit = renewer._executor.submit
    original_sleep = threading.Event().wait
    queued_message = messages[workers - 1]

    def submit(function, *args):
        future = original_submit(function, *args)
        if function == renewer._auto_lock_renew_task:
            futures[id(args[1])] = future
            if len(futures) == len(messages):
                submitted.set()
        return future

    def sleep(seconds):
        idle_checked.set()
        original_sleep(seconds)

    def renew(message):
        if message in messages[: workers - 1]:
            occupied.wait(timeout=5)
            assert release.wait(timeout=5)
        if message is queued_message and queued_outcome == "failed":
            raise ValueError("Queued renewal failed.")
        message._settled = True

    receiver.renew_message_lock.side_effect = renew
    try:
        with patch.object(renewer._executor, "submit", side_effect=submit), patch(
            "azure.servicebus._common.auto_lock_renewer.time.sleep", side_effect=sleep
        ):
            for message in messages:
                message._locked = utc_now()
                renewer.register(receiver, message)
            occupied.wait(timeout=5)
            assert submitted.wait(timeout=5)
            assert renewer._renew_tasks.empty()
            assert renewer._renew_tasks.unfinished_tasks == len(messages)
            if queued_outcome == "cancelled":
                assert futures[id(queued_message)].cancel()
                assert renewer._renew_tasks.unfinished_tasks == len(messages) - 1
            idle_checked.clear()
            assert idle_checked.wait(timeout=5)
            assert renewer._running_dispatcher.is_set()
            release.set()
            with renewer._renew_tasks.all_tasks_done:
                assert renewer._renew_tasks.all_tasks_done.wait_for(
                    lambda: renewer._renew_tasks.unfinished_tasks == 0, timeout=5
                )
            renewer.close()
        expected = [message for message in messages if queued_outcome != "cancelled" or message is not queued_message]
        assert receiver.renew_message_lock.call_count == len(expected)
        assert {id(invocation.args[0]) for invocation in receiver.renew_message_lock.call_args_list} == {
            id(message) for message in expected
        }
        assert all(future.done() for future in futures.values())
        assert renewer._renew_tasks.empty()
        assert not renewer._running_dispatcher.is_set()
        if queued_outcome == "failed":
            assert isinstance(queued_message.auto_renew_error, AutoLockRenewFailed)
            callback.assert_called_once_with(queued_message, queued_message.auto_renew_error)
        else:
            callback.assert_not_called()
    finally:
        release.set()
        occupied.abort()
        renewer.close()


@pytest.mark.parametrize("workers", [1, 2])
@pytest.mark.parametrize("operation", ["register", "enter"])
def test_close_during_first_inference_with_saturated_executor(workers, operation):
    executor = ThreadPoolExecutor(max_workers=workers)
    occupied = threading.Barrier(workers + 1)
    release = threading.Event()
    inference_submitted = threading.Event()
    closed = threading.Event()
    registration_errors = []
    close_errors = []
    renewer = AutoLockRenewer(executor=executor)
    original_submit = executor.submit

    def occupy():
        occupied.wait(timeout=5)
        assert release.wait(timeout=15)

    def submit(function, *args):
        future = original_submit(function, *args)
        if function == renewer._infer_max_workers_value_worker:
            inference_submitted.set()
        return future

    def register():
        try:
            if operation == "register":
                receiver = Mock(_running=True)
                renewer.register(receiver, _Message(receiver))
            else:
                renewer.__enter__()
        except Exception as error:
            registration_errors.append(error)

    def close():
        try:
            renewer.close(wait=False)
        except Exception as error:
            close_errors.append(error)
        finally:
            closed.set()

    blockers = [executor.submit(occupy) for _ in range(workers)]
    registration = threading.Thread(target=register)
    closer = threading.Thread(target=close)
    try:
        occupied.wait(timeout=5)
        with patch.object(executor, "submit", side_effect=submit) as submissions:
            registration.start()
            assert inference_submitted.wait(timeout=5)
            closer.start()
            assert closed.wait(timeout=5), "close(wait=False) waited for executor capacity inference."
            assert renewer._shutdown.is_set()
            assert not release.is_set()
            release.set()
            registration.join(timeout=5)
            closer.join(timeout=5)
            assert not registration.is_alive()
            assert not closer.is_alive()
            assert not close_errors
            assert len(registration_errors) == 1
            assert isinstance(registration_errors[0], (RuntimeError, ServiceBusError))
            assert all(invocation.args[0] != renewer._dispatch_worker for invocation in submissions.call_args_list)
        for blocker in blockers:
            blocker.result(timeout=5)
        assert not renewer._running_dispatcher.is_set()
    finally:
        release.set()
        occupied.abort()
        if registration.ident is not None:
            registration.join(timeout=5)
        if closer.ident is not None:
            closer.join(timeout=5)
        renewer.close()


@pytest.mark.parametrize("renewable", [None, object()])
def test_register_rejects_invalid_type_without_starting_workers(renewable):
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    try:
        with pytest.raises(TypeError, match="only supports registration"):
            renewer.register(Mock(), renewable)
        assert renewer._renew_tasks.empty()
        assert not executor.pending
    finally:
        renewer.close()


@pytest.mark.parametrize("renewable_type", [_Message, _Session])
def test_register_rejects_missing_lock_without_starting_workers(renewable_type):
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    receiver = Mock(_running=True)
    renewable = renewable_type(receiver)
    renewable._locked = None
    try:
        with pytest.raises(ValueError, match="PEEK_LOCK"):
            renewer.register(receiver, renewable)
        assert renewer._renew_tasks.empty()
        assert not executor.pending
    finally:
        renewer.close()


@pytest.mark.parametrize("operation", ["enter", "register"])
def test_closed_public_entry_points_cannot_restart_workers(operation):
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    receiver = Mock(_running=True)
    renewer.close()
    with pytest.raises(ServiceBusError, match="already been shutdown"):
        if operation == "enter":
            with renewer:
                pytest.fail("A closed renewer entered its context.")
        else:
            renewer.register(receiver, _Message(receiver))
    assert renewer._renew_tasks.empty()
    assert not executor.pending


@pytest.mark.parametrize("renewable_type", [_Message, _Session])
@pytest.mark.parametrize(
    "duration,expected_override",
    [(0, 0), (1, 0.75), (8, 6), (10.5, 7.5), (10.500001, None), (30, None)],
)
def test_register_short_lock_override_boundaries(renewable_type, duration, expected_override):
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = True
    receiver = Mock(_running=True)
    renewable = renewable_type(receiver)
    now = utc_now()
    renewable._locked = now + datetime.timedelta(seconds=duration)
    try:
        with patch("azure.servicebus._common.utils.utc_now", return_value=now):
            renewer.register(receiver, renewable)
        task = renewer._renew_tasks.get_nowait()
        renewer._renew_tasks.task_done()
        assert task[-1] == expected_override
    finally:
        renewer.close()


@pytest.mark.parametrize("override", [False, True])
@pytest.mark.parametrize("renewable_type", [_Message, _Session])
def test_registration_duration_override_controls_timeout(override, renewable_type):
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor, max_lock_renewal_duration=1)
    renewer._is_max_workers_greater_than_one = True
    receiver = Mock(_running=True)
    renewable = renewable_type(receiver)
    start = utc_now() - datetime.timedelta(seconds=20)
    if renewable_type is _Message:
        renewable._received_timestamp_utc = start
    else:
        renewable._session_start = start
    renewable._locked = utc_now()

    def renew(*args):
        receiver._running = False

    operation = Mock(side_effect=renew)
    if renewable_type is _Session:
        renewable.renew_lock = operation
    else:
        receiver.renew_message_lock = operation
    try:
        renewer.register(receiver, renewable, max_lock_renewal_duration=120 if override else None)
        _run_executor_until_idle(executor)
        if override:
            operation.assert_called_once()
        else:
            operation.assert_not_called()
            assert isinstance(renewable.auto_renew_error, AutoLockRenewTimeout)
        assert renewer._renew_tasks.unfinished_tasks == 0
    finally:
        renewer.close()


@pytest.mark.parametrize("override", [False, True])
def test_registration_callback_override_controls_failure_notification(override):
    executor = _Executor()
    default_callback = Mock()
    override_callback = Mock()
    renewer = AutoLockRenewer(executor=executor, on_lock_renew_failure=default_callback)
    renewer._is_max_workers_greater_than_one = True
    receiver = Mock(_running=True)
    receiver.renew_message_lock.side_effect = ValueError("Renewal failed.")
    message = _Message(receiver)
    message._locked = utc_now()
    try:
        renewer.register(receiver, message, on_lock_renew_failure=override_callback if override else None)
        _run_executor_until_idle(executor)
        selected, unused = (override_callback, default_callback) if override else (default_callback, override_callback)
        selected.assert_called_once_with(message, message.auto_renew_error)
        unused.assert_not_called()
        assert isinstance(message.auto_renew_error, AutoLockRenewFailed)
        assert renewer._renew_tasks.unfinished_tasks == 0
    finally:
        renewer.close()


def test_lock_is_requeued_without_early_renewal_until_due():
    executor = _Executor()
    renewer = AutoLockRenewer(executor=executor)
    renewer._is_max_workers_greater_than_one = True
    receiver = Mock(_running=True)
    message = _Message(receiver)
    now = utc_now()
    message._locked = now + datetime.timedelta(seconds=60)
    clock = 0

    def renew(*args):
        receiver._running = False

    receiver.renew_message_lock.side_effect = renew

    def tick(_):
        nonlocal clock
        clock += 1
        assert clock <= 10
        if executor.pending:
            executor.run_next()
        if clock == 1:
            receiver.renew_message_lock.assert_not_called()
            assert renewer._renew_tasks.qsize() == 1
            assert renewer._renew_tasks.unfinished_tasks == 1
            current_time.return_value = now + datetime.timedelta(seconds=55)

    try:
        renewer.register(receiver, message)
        with patch("azure.servicebus._common.auto_lock_renewer.utc_now", return_value=now) as current_time, patch(
            "azure.servicebus._common.auto_lock_renewer.time.time", side_effect=lambda: clock
        ), patch("azure.servicebus._common.auto_lock_renewer.time.sleep", side_effect=tick):
            executor.run_next()
        receiver.renew_message_lock.assert_called_once_with(message)
        assert renewer._renew_tasks.empty()
        assert renewer._renew_tasks.unfinished_tasks == 0
        assert not executor.pending
        assert not renewer._running_dispatcher.is_set()
    finally:
        renewer.close()
