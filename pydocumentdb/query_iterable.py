# Copyright (c) Microsoft Corporation.  All rights reserved.

"""Iterable query results.
"""

import pydocumentdb.errors as errors
import pydocumentdb.http_constants as http_constants


class QueryIterable(object):
    """Represents an iterable object of the query results.
    """

    def __init__(self, options, fetch_function):
        """
        :Parameters:
            - `options`: dict
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

    def __iter__(self):
        """Makes this class iterable.
        """
        return self.Iterator(self)

    class Iterator(object):
        def __init__(self, iterable):
            self._iterable = iterable
            self._finished = False
            self._current = -1
            self._iterable._results = []
            self._iterable._continuation = None
            self._iterable._has_started = False

        def __iter__(self):
            # Always returns self
            return self

        def next(self):
            if self._finished:
                # Must keep raising once we have ended
                raise StopIteration

            self._current += 1
            if self._current < len(self._iterable._results):
                return self._iterable._results[self._current]
            else:
                if self._iterable.fetch_next_block():
                    self._current = 0
                    return self._iterable._results[self._current]
            self._finished = True
            raise StopIteration

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
