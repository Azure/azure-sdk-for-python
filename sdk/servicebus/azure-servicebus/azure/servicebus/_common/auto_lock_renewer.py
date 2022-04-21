# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import datetime
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import TYPE_CHECKING

from .._servicebus_receiver import ServiceBusReceiver
from .._servicebus_session import ServiceBusSession
from .message import ServiceBusReceivedMessage
from ..exceptions import AutoLockRenewFailed, AutoLockRenewTimeout, ServiceBusError
from .utils import get_renewable_start_time, utc_now, get_renewable_lock_duration

if TYPE_CHECKING:
    from typing import Callable, Union, Optional

    Renewable = Union[ServiceBusSession, ServiceBusReceivedMessage]
    LockRenewFailureCallback = Callable[[Renewable, Optional[Exception]], None]

try:
    import queue
except ImportError:
    import Queue as queue  # type: ignore

_log = logging.getLogger(__name__)

SHORT_RENEW_OFFSET = 0.5  # Seconds that if a renew period is longer than lock duration + offset, it's "too long"
SHORT_RENEW_SCALING_FACTOR = (
    0.75  # In this situation we need a "Short renew" and should scale by this factor.
)


class AutoLockRenewer(object):  # pylint:disable=too-many-instance-attributes
    """Auto renew locks for messages and sessions using a background thread pool.

    :param max_lock_renewal_duration: A time in seconds that locks registered to this renewer
     should be maintained for. Default value is 300 (5 minutes).
    :type max_lock_renewal_duration: float
    :param on_lock_renew_failure: A callback may be specified to be called when the lock is lost on the renewable
     that is being registered. Default value is None (no callback).
    :type on_lock_renew_failure: Optional[LockRenewFailureCallback]
    :param executor: A user-specified thread pool. This cannot be combined with
     setting `max_workers`.
    :type executor: Optional[~concurrent.futures.ThreadPoolExecutor]
    :param max_workers: Specify the maximum workers in the thread pool. If not
     specified the number used will be derived from the core count of the environment.
     This cannot be combined with `executor`.
    :type max_workers: Optional[int]

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START auto_lock_renew_message_sync]
            :end-before: [END auto_lock_renew_message_sync]
            :language: python
            :dedent: 4
            :caption: Automatically renew a message lock

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START auto_lock_renew_session_sync]
            :end-before: [END auto_lock_renew_session_sync]
            :language: python
            :dedent: 4
            :caption: Automatically renew a session lock

    """

    def __init__(
        self,
        max_lock_renewal_duration=300,
        on_lock_renew_failure=None,
        executor=None,
        max_workers=None,
    ):
        # type: (float, Optional[LockRenewFailureCallback], Optional[ThreadPoolExecutor], Optional[int]) -> None
        """Auto renew locks for messages and sessions using a background thread pool. It is recommended
        setting max_worker to a large number or passing ThreadPoolExecutor of large max_workers number when
        AutoLockRenewer is supposed to deal with multiple messages or sessions simultaneously.

        :param max_lock_renewal_duration: A time in seconds that locks registered to this renewer
         should be maintained for. Default value is 300 (5 minutes).
        :type max_lock_renewal_duration: float
        :param on_lock_renew_failure: A callback may be specified to be called when the lock is lost on the renewable
         that is being registered. Default value is None (no callback).
        :type on_lock_renew_failure: Optional[LockRenewFailureCallback]
        :param executor: A user-specified thread pool. This cannot be combined with
         setting `max_workers`.
        :type executor: Optional[~concurrent.futures.ThreadPoolExecutor]
        :param max_workers: Specify the maximum workers in the thread pool. If not
         specified the number used will be derived from the core count of the environment.
         This cannot be combined with `executor`.
        :type max_workers: Optional[int]
        """
        self._executor = executor or ThreadPoolExecutor(max_workers=max_workers)
        # None indicates it's unknown whether the provided executor has max workers > 1
        self._is_max_workers_greater_than_one = None if executor else (max_workers is None or max_workers > 1)
        self._shutdown = threading.Event()
        self._sleep_time = 0.5
        self._renew_period = 10
        self._running_dispatcher = threading.Event()  # indicate whether the dispatcher is running
        self._last_activity_timestamp = None  # the last timestamp when the dispatcher is active dealing with tasks
        self._dispatcher_timeout = 5  # the idle time that dispatcher should exit if there's no activity
        self._max_lock_renewal_duration = max_lock_renewal_duration
        self._on_lock_renew_failure = on_lock_renew_failure
        self._renew_tasks = queue.Queue()  # type: ignore
        self._infer_max_workers_time = 1

    def __enter__(self):
        if self._shutdown.is_set():
            raise ServiceBusError(
                "The AutoLockRenewer has already been shutdown. Please create a new instance for"
                " auto lock renewing."
            )

        self._init_workers()
        return self

    def __exit__(self, *args):
        self.close()

    def _init_workers(self):
        if not self._running_dispatcher.is_set():
            self._infer_max_workers_greater_than_one_if_needed()
            self._running_dispatcher.set()
            self._executor.submit(self._dispatch_worker)

    def _infer_max_workers_greater_than_one_if_needed(self):
        # infer max_workers value if executor is passed in
        if self._is_max_workers_greater_than_one is None:
            max_wokers_checker = self._executor.submit(self._infer_max_workers_value_worker)
            max_wokers_checker.result()

    def _infer_max_workers_value_worker(self):
        max_workers_checker = self._executor.submit(pow, 1, 1)
        # This will never complete because there is only one worker thread and
        # it is executing this function.
        try:
            max_workers_checker.result(timeout=self._infer_max_workers_time)
            self._is_max_workers_greater_than_one = True
        except FuturesTimeoutError:
            self._is_max_workers_greater_than_one = False

    def _renewable(self, renewable):
        # pylint: disable=protected-access
        if self._shutdown.is_set():
            return False
        if hasattr(renewable, "_settled") and renewable._settled:
            return False
        if not renewable._receiver._running:
            return False
        if renewable._lock_expired:
            return False
        return True

    def _dispatch_worker(self):
        self._last_activity_timestamp = time.time()
        while not self._shutdown.is_set() and self._running_dispatcher.is_set():
            while not self._renew_tasks.empty():
                renew_task = self._renew_tasks.get()
                if self._is_max_workers_greater_than_one:
                    self._executor.submit(self._auto_lock_renew_task, *renew_task)
                else:
                    self._auto_lock_renew_task(*renew_task)
                self._renew_tasks.task_done()
                self._last_activity_timestamp = time.time()
            # If there's no activity in the past self._idle_timeout seconds, exit the method
            # This ensures the dispatching thread could exit, not blocking the main python thread
            # the main worker thread could be started again if new tasks get registered
            if time.time() - self._last_activity_timestamp >= self._dispatcher_timeout:
                self._running_dispatcher.clear()
                self._last_activity_timestamp = None
                return
            time.sleep(self._sleep_time)  # save cpu cycles if there's currently no task in self._renew_tasks

    def _auto_lock_renew_task(
        self,
        receiver,
        renewable,
        starttime,
        max_lock_renewal_duration,
        on_lock_renew_failure=None,
        renew_period_override=None,
    ):
        # pylint: disable=protected-access
        error = None
        clean_shutdown = False  # Only trigger the on_lock_renew_failure if halting was not expected (shutdown, etc)
        renew_period = renew_period_override or self._renew_period
        try:
            if self._renewable(renewable):
                if (utc_now() - starttime) >= datetime.timedelta(
                    seconds=max_lock_renewal_duration
                ):
                    _log.debug(
                        "Reached max auto lock renew duration - letting lock expire."
                    )
                    raise AutoLockRenewTimeout(
                        "Auto-renew period ({} seconds) elapsed.".format(
                            max_lock_renewal_duration
                        )
                    )
                if (renewable.locked_until_utc - utc_now()) <= datetime.timedelta(
                    seconds=renew_period
                ):
                    _log.debug(
                        "%r seconds or less until lock expires - auto renewing.",
                        renew_period,
                    )
                    try:
                        # Renewable is a session
                        renewable.renew_lock()  # type: ignore
                    except AttributeError:
                        # Renewable is a message
                        receiver.renew_message_lock(renewable)  # type: ignore
                time.sleep(self._sleep_time)
                # enqueue a new task, keeping renewing the renewable
                if self._renewable(renewable):
                    self._renew_tasks.put(
                        (
                            receiver,
                            renewable,
                            starttime,
                            max_lock_renewal_duration,
                            on_lock_renew_failure,
                            renew_period_override
                        )
                    )
            clean_shutdown = not renewable._lock_expired
        except AutoLockRenewTimeout as e:
            error = e
            renewable.auto_renew_error = e
            clean_shutdown = not renewable._lock_expired
        except Exception as e:  # pylint: disable=broad-except
            _log.debug("Failed to auto-renew lock: %r. Closing thread.", e)
            error = AutoLockRenewFailed("Failed to auto-renew lock", error=e)
            renewable.auto_renew_error = error
        finally:
            if on_lock_renew_failure and not clean_shutdown:
                on_lock_renew_failure(renewable, error)

    def register(
        self,
        receiver,
        renewable,
        max_lock_renewal_duration=None,
        on_lock_renew_failure=None,
    ):
        # type: (ServiceBusReceiver, Renewable, Optional[float], Optional[LockRenewFailureCallback]) -> None
        """Register a renewable entity for automatic lock renewal.

        :param receiver: The ServiceBusReceiver instance that is associated with the message or the session to
         be auto-lock-renewed.
        :type receiver: ~azure.servicebus.ServiceBusReceiver
        :param renewable: A locked entity that needs to be renewed.
        :type renewable: Union[~azure.servicebus.ServiceBusReceivedMessage, ~azure.servicebus.ServiceBusSession]
        :param max_lock_renewal_duration: A time in seconds that the lock should be maintained for.
         Default value is None. If specified, this value will override the default value specified at the constructor.
        :type max_lock_renewal_duration: Optional[float]
        :param on_lock_renew_failure: A callback may be specified to be called when the lock is lost on the renewable
         that is being registered. Default value is None (no callback).
        :type on_lock_renew_failure: Optional[LockRenewFailureCallback]

        :rtype: None
        """
        if not isinstance(renewable, (ServiceBusReceivedMessage, ServiceBusSession)):
            raise TypeError(
                "AutoLockRenewer only supports registration of types "
                "azure.servicebus.ServiceBusReceivedMessage (via a receiver's receive methods) and "
                "azure.servicebus.ServiceBusSession (via a session receiver's property receiver.session)."
            )
        if self._shutdown.is_set():
            raise ServiceBusError(
                "The AutoLockRenewer has already been shutdown. Please create a new instance for"
                " auto lock renewing."
            )
        if renewable.locked_until_utc is None:
            raise ValueError(
                "Only azure.servicebus.ServiceBusReceivedMessage objects in PEEK_LOCK receive mode may"
                "be lock-renewed.  (E.g. only messages received via receive() or the receiver iterator,"
                "not using RECEIVE_AND_DELETE receive mode, and not returned from Peek)"
            )

        starttime = get_renewable_start_time(renewable)

        # This is a heuristic to compensate if it appears the user has a lock duration less than our base renew period
        time_until_expiry = get_renewable_lock_duration(renewable)
        renew_period_override = None
        # Default is 10 seconds, but let's leave ourselves a small margin of error because clock skew is a real problem
        if time_until_expiry <= datetime.timedelta(
            seconds=self._renew_period + SHORT_RENEW_OFFSET
        ):
            renew_period_override = (
                time_until_expiry.seconds * SHORT_RENEW_SCALING_FACTOR
            )

        _log.debug(
            "Running lock auto-renew for %r for %r seconds", renewable, max_lock_renewal_duration
        )

        self._init_workers()

        self._renew_tasks.put(
            (
                receiver,
                renewable,
                starttime,
                max_lock_renewal_duration or self._max_lock_renewal_duration,
                on_lock_renew_failure or self._on_lock_renew_failure,
                renew_period_override
            )
        )

    def close(self, wait=True):
        """Cease autorenewal by shutting down the thread pool to clean up any remaining lock renewal threads.

        :param wait: Whether to block until thread pool has shutdown. Default is `True`.
        :type wait: bool

        :rtype: None
        """
        self._running_dispatcher.clear()
        self._shutdown.set()
        self._executor.shutdown(wait=wait)
