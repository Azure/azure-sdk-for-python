# Copyright 2017, Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Abstract and helper bases for Future implementations."""

import abc
import concurrent.futures

from google.api_core import exceptions
from google.api_core import retry
from google.api_core.future import _helpers
from google.api_core.future import base


class _OperationNotComplete(Exception):
    """Private exception used for polling via retry."""

    pass


RETRY_PREDICATE = retry.if_exception_type(
    _OperationNotComplete,
    exceptions.TooManyRequests,
    exceptions.InternalServerError,
    exceptions.BadGateway,
)
DEFAULT_RETRY = retry.Retry(predicate=RETRY_PREDICATE)


class PollingFuture(base.Future):
    """A Future that needs to poll some service to check its status.

    The :meth:`done` method should be implemented by subclasses. The polling
    behavior will repeatedly call ``done`` until it returns True.

    .. note: Privacy here is intended to prevent the final class from
      overexposing, not to prevent subclasses from accessing methods.

    Args:
        retry (google.api_core.retry.Retry): The retry configuration used
            when polling. This can be used to control how often :meth:`done`
            is polled. Regardless of the retry's ``deadline``, it will be
            overridden by the ``timeout`` argument to :meth:`result`.
    """

    def __init__(self, retry=DEFAULT_RETRY):
        super(PollingFuture, self).__init__()
        self._retry = retry
        self._result = None
        self._exception = None
        self._result_set = False
        """bool: Set to True when the result has been set via set_result or
        set_exception."""
        self._polling_thread = None
        self._done_callbacks = []

    @abc.abstractmethod
    def done(self, retry=DEFAULT_RETRY):
        """Checks to see if the operation is complete.

        Args:
            retry (google.api_core.retry.Retry): (Optional) How to retry the RPC.

        Returns:
            bool: True if the operation is complete, False otherwise.
        """
        # pylint: disable=redundant-returns-doc, missing-raises-doc
        raise NotImplementedError()

    def _done_or_raise(self):
        """Check if the future is done and raise if it's not."""
        if not self.done():
            raise _OperationNotComplete()

    def running(self):
        """True if the operation is currently running."""
        return not self.done()

    def _blocking_poll(self, timeout=None):
        """Poll and wait for the Future to be resolved.

        Args:
            timeout (int):
                How long (in seconds) to wait for the operation to complete.
                If None, wait indefinitely.
        """
        if self._result_set:
            return

        retry_ = self._retry.with_deadline(timeout)

        try:
            retry_(self._done_or_raise)()
        except exceptions.RetryError:
            raise concurrent.futures.TimeoutError(
                "Operation did not complete within the designated " "timeout."
            )

    def result(self, timeout=None):
        """Get the result of the operation, blocking if necessary.

        Args:
            timeout (int):
                How long (in seconds) to wait for the operation to complete.
                If None, wait indefinitely.

        Returns:
            google.protobuf.Message: The Operation's result.

        Raises:
            google.api_core.GoogleAPICallError: If the operation errors or if
                the timeout is reached before the operation completes.
        """
        self._blocking_poll(timeout=timeout)

        if self._exception is not None:
            # pylint: disable=raising-bad-type
            # Pylint doesn't recognize that this is valid in this case.
            raise self._exception

        return self._result

    def exception(self, timeout=None):
        """Get the exception from the operation, blocking if necessary.

        Args:
            timeout (int): How long to wait for the operation to complete.
                If None, wait indefinitely.

        Returns:
            Optional[google.api_core.GoogleAPICallError]: The operation's
                error.
        """
        self._blocking_poll(timeout=timeout)
        return self._exception

    def add_done_callback(self, fn):
        """Add a callback to be executed when the operation is complete.

        If the operation is not already complete, this will start a helper
        thread to poll for the status of the operation in the background.

        Args:
            fn (Callable[Future]): The callback to execute when the operation
                is complete.
        """
        if self._result_set:
            _helpers.safe_invoke_callback(fn, self)
            return

        self._done_callbacks.append(fn)

        if self._polling_thread is None:
            # The polling thread will exit on its own as soon as the operation
            # is done.
            self._polling_thread = _helpers.start_daemon_thread(
                target=self._blocking_poll
            )

    def _invoke_callbacks(self, *args, **kwargs):
        """Invoke all done callbacks."""
        for callback in self._done_callbacks:
            _helpers.safe_invoke_callback(callback, *args, **kwargs)

    def set_result(self, result):
        """Set the Future's result."""
        self._result = result
        self._result_set = True
        self._invoke_callbacks(self)

    def set_exception(self, exception):
        """Set the Future's exception."""
        self._exception = exception
        self._result_set = True
        self._invoke_callbacks(self)
