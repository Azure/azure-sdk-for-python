# Copyright (c) Microsoft Corporation.  All rights reserved.

"""The backoff retry utility functions and classes.
"""

import logging
import time

import pydocumentdb.errors as errors


def Execute(callback_fn, resource_throttle_retry_policy):
    """Exectutes the callback function using the resource_throttle_retry_policy.

    :Parameters:
        - `callback_fn`: function
        - `resource_throttle_retry_policy`: retry.ResourceThrottleRetryPolicy

    """
    while True:
        try:
            callback_fn()
            break  # Break from the while loop if no exception happened.
        except Exception, e:
            should_retry = resource_throttle_retry_policy.ShouldRetry(e)
            if not should_retry:
                raise e
        time.sleep(resource_throttle_retry_policy.retry_after_in_milliseconds)


class ResourceThrottleRetryPolicy(object):
    """The resource throttle retry policy."""

    _default_retry_in_seconds = 5

    def __init__(self, max_retry_count):
        self._max_attempt_count = max_retry_count
        self._current_attempt_count = 0
        self.retry_after_in_milliseconds = 0

    def ShouldRetry(self, exception):
        """Returns true if should retry on the passed-in exception.

        :Parameters:
            - `exception`: Exception

        :Returns:
            boolean

        """
        self.retry_after_in_milliseconds = 0

        if (self._current_attempt_count < self._max_attempt_count and
                self._CheckIfRetryNeeded(exception)):
            self._current_attempt_count += 1
            logging.info('Operation will be retried after %d milliseconds. Exception: %s' %
                         (self.retry_after_in_milliseconds,
                          str(exception)))
            return True
        else:
            logging.warning('Operation will NOT be retried. Exception: %s' %
                            str(exception))
            return False

    def _CheckIfRetryNeeded(self, exception):
        self.retry_after_in_milliseconds = 0

        if (isinstance(exception, errors.DocumentDBError) and exception.status_code == 429):
            self.retry_after_in_milliseconds = exception.retry_after_in_milliseconds

            if self.retry_after_in_milliseconds == 0:
                self.retry_after_in_milliseconds = ResourceThrottleRetryPolicy._default_retry_in_seconds

            return True

        return False