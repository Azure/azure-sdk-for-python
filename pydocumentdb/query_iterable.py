# Copyright (c) Microsoft Corporation.  All rights reserved.

"""Iterable query results.
"""

import pydocumentdb.backoff_retry_utility as backoff_retry_utility
import pydocumentdb.errors as errors
import pydocumentdb.http_constants as http_constants


class QueryIterable(object):
    """Represents an iterable object of the query results.
    """

    def __init__(self, options, retry_policy, fetch_function):
        """
        :Parameters:
            - `options`: dict
            - `retry_policy`: documents.RetryPolicy
            - `fetch_function`: function

        Example of `fetch_function`:

        >>> def result_fn(result):
        >>>     return result['Databases']

        """
        self._options = options
        self._fetch_function = fetch_function
        self._results = []
        self._continuation = None
        self._has_started = False
        self._retry_policy = retry_policy

    def __iter__(self):
        """Makes this class iterable.
        """
        return self.Iterator(self)

    class Iterator(object):
        def __init__(self, iterable):
            self._iterable = iterable
            self._finished = False
            self._current = 0
            self._resource_throttle_retry_policy = (
                backoff_retry_utility.ResourceThrottleRetryPolicy(
                    self._iterable._retry_policy.MaxRetryAttemptsOnQuery))
            self._iterable._results = []
            self._iterable._continuation = None
            self._iterable._has_started = False

        def __iter__(self):
            # Always returns self
            return self

        def next(self):
            def callback():
                if not self._iterable.fetch_next_block():
                    self._finished = True

            if self._finished:
                # Must keep raising once we have ended
                raise StopIteration

            if (self._current >= len(self._iterable._results) and
                    not self._finished):
                backoff_retry_utility.Execute(
                    callback, self._resource_throttle_retry_policy)
                self._current = 0

            if self._finished:
                raise StopIteration

            result = self._iterable._results[self._current]
            self._current += 1
            return result

        # Also support Python 3.x iteration
        __next__ = next

    def fetch_next_block(self):
        """Fetches more items.

        :Returns:
            list of fetched items.

        """
        fetched_items = []
        while self._continuation or not self._has_started:
            if not self._has_started:
                self._has_started = True
            self._options['continuation'] = self._continuation
            (fetched_items, response_headers) = self._fetch_function(self._options)
            self._results = fetched_items
            self._continuation = response_headers.get(
                http_constants.HttpHeaders.Continuation)
            if fetched_items:
                break
        return fetched_items
