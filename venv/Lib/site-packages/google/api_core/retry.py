# Copyright 2017 Google LLC
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

"""Helpers for retrying functions with exponential back-off.

The :class:`Retry` decorator can be used to retry functions that raise
exceptions using exponential backoff. Because a exponential sleep algorithm is
used, the retry is limited by a `deadline`. The deadline is the maxmimum amount
of time a method can block. This is used instead of total number of retries
because it is difficult to ascertain the amount of time a function can block
when using total number of retries and exponential backoff.

By default, this decorator will retry transient
API errors (see :func:`if_transient_error`). For example:

.. code-block:: python

    @retry.Retry()
    def call_flaky_rpc():
        return client.flaky_rpc()

    # Will retry flaky_rpc() if it raises transient API errors.
    result = call_flaky_rpc()

You can pass a custom predicate to retry on different exceptions, such as
waiting for an eventually consistent item to be available:

.. code-block:: python

    @retry.Retry(predicate=if_exception_type(exceptions.NotFound))
    def check_if_exists():
        return client.does_thing_exist()

    is_available = check_if_exists()

Some client library methods apply retry automatically. These methods can accept
a ``retry`` parameter that allows you to configure the behavior:

.. code-block:: python

    my_retry = retry.Retry(deadline=60)
    result = client.some_method(retry=my_retry)

"""

from __future__ import unicode_literals

import datetime
import functools
import logging
import random
import time

import six

from google.api_core import datetime_helpers
from google.api_core import exceptions
from google.api_core import general_helpers

_LOGGER = logging.getLogger(__name__)
_DEFAULT_INITIAL_DELAY = 1.0  # seconds
_DEFAULT_MAXIMUM_DELAY = 60.0  # seconds
_DEFAULT_DELAY_MULTIPLIER = 2.0
_DEFAULT_DEADLINE = 60.0 * 2.0  # seconds


def if_exception_type(*exception_types):
    """Creates a predicate to check if the exception is of a given type.

    Args:
        exception_types (Sequence[:func:`type`]): The exception types to check
            for.

    Returns:
        Callable[Exception]: A predicate that returns True if the provided
            exception is of the given type(s).
    """

    def if_exception_type_predicate(exception):
        """Bound predicate for checking an exception type."""
        return isinstance(exception, exception_types)

    return if_exception_type_predicate


# pylint: disable=invalid-name
# Pylint sees this as a constant, but it is also an alias that should be
# considered a function.
if_transient_error = if_exception_type(
    exceptions.InternalServerError,
    exceptions.TooManyRequests,
    exceptions.ServiceUnavailable,
)
"""A predicate that checks if an exception is a transient API error.

The following server errors are considered transient:

- :class:`google.api_core.exceptions.InternalServerError` - HTTP 500, gRPC
    ``INTERNAL(13)`` and its subclasses.
- :class:`google.api_core.exceptions.TooManyRequests` - HTTP 429
- :class:`google.api_core.exceptions.ServiceUnavailable` - HTTP 503
- :class:`google.api_core.exceptions.ResourceExhausted` - gRPC
    ``RESOURCE_EXHAUSTED(8)``
"""
# pylint: enable=invalid-name


def exponential_sleep_generator(initial, maximum, multiplier=_DEFAULT_DELAY_MULTIPLIER):
    """Generates sleep intervals based on the exponential back-off algorithm.

    This implements the `Truncated Exponential Back-off`_ algorithm.

    .. _Truncated Exponential Back-off:
        https://cloud.google.com/storage/docs/exponential-backoff

    Args:
        initial (float): The minimum amout of time to delay. This must
            be greater than 0.
        maximum (float): The maximum amout of time to delay.
        multiplier (float): The multiplier applied to the delay.

    Yields:
        float: successive sleep intervals.
    """
    delay = initial
    while True:
        # Introduce jitter by yielding a delay that is uniformly distributed
        # to average out to the delay time.
        yield min(random.uniform(0.0, delay * 2.0), maximum)
        delay = delay * multiplier


def retry_target(target, predicate, sleep_generator, deadline, on_error=None):
    """Call a function and retry if it fails.

    This is the lowest-level retry helper. Generally, you'll use the
    higher-level retry helper :class:`Retry`.

    Args:
        target(Callable): The function to call and retry. This must be a
            nullary function - apply arguments with `functools.partial`.
        predicate (Callable[Exception]): A callable used to determine if an
            exception raised by the target should be considered retryable.
            It should return True to retry or False otherwise.
        sleep_generator (Iterable[float]): An infinite iterator that determines
            how long to sleep between retries.
        deadline (float): How long to keep retrying the target. The last sleep
            period is shortened as necessary, so that the last retry runs at
            ``deadline`` (and not considerably beyond it).
        on_error (Callable[Exception]): A function to call while processing a
            retryable exception.  Any error raised by this function will *not*
            be caught.

    Returns:
        Any: the return value of the target function.

    Raises:
        google.api_core.RetryError: If the deadline is exceeded while retrying.
        ValueError: If the sleep generator stops yielding values.
        Exception: If the target raises a method that isn't retryable.
    """
    if deadline is not None:
        deadline_datetime = datetime_helpers.utcnow() + datetime.timedelta(
            seconds=deadline
        )
    else:
        deadline_datetime = None

    last_exc = None

    for sleep in sleep_generator:
        try:
            return target()

        # pylint: disable=broad-except
        # This function explicitly must deal with broad exceptions.
        except Exception as exc:
            if not predicate(exc):
                raise
            last_exc = exc
            if on_error is not None:
                on_error(exc)

        now = datetime_helpers.utcnow()

        if deadline_datetime is not None:
            if deadline_datetime <= now:
                six.raise_from(
                    exceptions.RetryError(
                        "Deadline of {:.1f}s exceeded while calling {}".format(
                            deadline, target
                        ),
                        last_exc,
                    ),
                    last_exc,
                )
            else:
                time_to_deadline = (deadline_datetime - now).total_seconds()
                sleep = min(time_to_deadline, sleep)

        _LOGGER.debug(
            "Retrying due to {}, sleeping {:.1f}s ...".format(last_exc, sleep)
        )
        time.sleep(sleep)

    raise ValueError("Sleep generator stopped yielding sleep values.")


@six.python_2_unicode_compatible
class Retry(object):
    """Exponential retry decorator.

    This class is a decorator used to add exponential back-off retry behavior
    to an RPC call.

    Although the default behavior is to retry transient API errors, a
    different predicate can be provided to retry other exceptions.

    Args:
        predicate (Callable[Exception]): A callable that should return ``True``
            if the given exception is retryable.
        initial (float): The minimum a,out of time to delay in seconds. This
            must be greater than 0.
        maximum (float): The maximum amout of time to delay in seconds.
        multiplier (float): The multiplier applied to the delay.
        deadline (float): How long to keep retrying in seconds. The last sleep
            period is shortened as necessary, so that the last retry runs at
            ``deadline`` (and not considerably beyond it).
    """

    def __init__(
        self,
        predicate=if_transient_error,
        initial=_DEFAULT_INITIAL_DELAY,
        maximum=_DEFAULT_MAXIMUM_DELAY,
        multiplier=_DEFAULT_DELAY_MULTIPLIER,
        deadline=_DEFAULT_DEADLINE,
        on_error=None,
    ):
        self._predicate = predicate
        self._initial = initial
        self._multiplier = multiplier
        self._maximum = maximum
        self._deadline = deadline
        self._on_error = on_error

    def __call__(self, func, on_error=None):
        """Wrap a callable with retry behavior.

        Args:
            func (Callable): The callable to add retry behavior to.
            on_error (Callable[Exception]): A function to call while processing
                a retryable exception. Any error raised by this function will
                *not* be caught.

        Returns:
            Callable: A callable that will invoke ``func`` with retry
                behavior.
        """
        if self._on_error is not None:
            on_error = self._on_error

        @general_helpers.wraps(func)
        def retry_wrapped_func(*args, **kwargs):
            """A wrapper that calls target function with retry."""
            target = functools.partial(func, *args, **kwargs)
            sleep_generator = exponential_sleep_generator(
                self._initial, self._maximum, multiplier=self._multiplier
            )
            return retry_target(
                target,
                self._predicate,
                sleep_generator,
                self._deadline,
                on_error=on_error,
            )

        return retry_wrapped_func

    def with_deadline(self, deadline):
        """Return a copy of this retry with the given deadline.

        Args:
            deadline (float): How long to keep retrying.

        Returns:
            Retry: A new retry instance with the given deadline.
        """
        return Retry(
            predicate=self._predicate,
            initial=self._initial,
            maximum=self._maximum,
            multiplier=self._multiplier,
            deadline=deadline,
            on_error=self._on_error,
        )

    def with_predicate(self, predicate):
        """Return a copy of this retry with the given predicate.

        Args:
            predicate (Callable[Exception]): A callable that should return
                ``True`` if the given exception is retryable.

        Returns:
            Retry: A new retry instance with the given predicate.
        """
        return Retry(
            predicate=predicate,
            initial=self._initial,
            maximum=self._maximum,
            multiplier=self._multiplier,
            deadline=self._deadline,
            on_error=self._on_error,
        )

    def with_delay(self, initial=None, maximum=None, multiplier=None):
        """Return a copy of this retry with the given delay options.

        Args:
            initial (float): The minimum amout of time to delay. This must
                be greater than 0.
            maximum (float): The maximum amout of time to delay.
            multiplier (float): The multiplier applied to the delay.

        Returns:
            Retry: A new retry instance with the given predicate.
        """
        return Retry(
            predicate=self._predicate,
            initial=initial if initial is not None else self._initial,
            maximum=maximum if maximum is not None else self._maximum,
            multiplier=multiplier if maximum is not None else self._multiplier,
            deadline=self._deadline,
            on_error=self._on_error,
        )

    def __str__(self):
        return (
            "<Retry predicate={}, initial={:.1f}, maximum={:.1f}, "
            "multiplier={:.1f}, deadline={:.1f}, on_error={}>".format(
                self._predicate,
                self._initial,
                self._maximum,
                self._multiplier,
                self._deadline,
                self._on_error,
            )
        )
