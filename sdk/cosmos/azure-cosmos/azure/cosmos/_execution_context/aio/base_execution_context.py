# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Internal class for query execution context implementation in the Azure Cosmos
database service.
"""

from collections import deque
import copy

from ...aio import _retry_utility_async
from ... import http_constants

# pylint: disable=protected-access


class _QueryExecutionContextBase(object):
    """
    This is the abstract base execution context class.
    """

    def __init__(self, client, options):
        """
        :param CosmosClient client:
        :param dict options: The request options for the request.
        """
        self._client = client
        self._options = options
        self._is_change_feed = "changeFeed" in options and options["changeFeed"] is True
        self._continuation = self._get_initial_continuation()
        self._has_started = False
        self._has_finished = False
        self._buffer = deque()

    def _get_initial_continuation(self):
        if "continuation" in self._options:
            return self._options["continuation"]
        return None

    def _has_more_pages(self):
        return not self._has_finished

    async def _ensure(self):
        if not self._has_more_pages():
            return

        if not self._buffer:
            results = await self._fetch_next_block()
            self._buffer.extend(results)

        if not self._buffer:
            self._has_finished = True

    async def fetch_next_block(self):
        """Returns a block of results with respecting retry policy.

        This method only exists for backward compatibility reasons. (Because
        QueryIterable has exposed fetch_next_block api).

        :return: List of results.
        :rtype: list
        """
        await self._ensure()
        res = list(self._buffer)
        self._buffer.clear()
        return res

    async def _fetch_next_block(self):
        raise NotImplementedError

    def __aiter__(self):
        """Returns itself as an iterator
        :returns: Query as an iterator.
        :rtype: Iterator
        """
        return self

    async def __anext__(self):
        """Return the next query result.

        :return: The next query result.
        :rtype: dict
        :raises StopAsyncIteration: If no more result is left.
        """
        await self._ensure()

        if not self._buffer:
            raise StopAsyncIteration

        return self._buffer.popleft()

    async def _fetch_items_helper_no_retries(self, fetch_function):
        """Fetches more items and doesn't retry on failure

        :param Callable fetch_function: The function that fetches the items.
        :return: List of fetched items.
        :rtype: list
        """
        fetched_items = []
        new_options = copy.deepcopy(self._options)
        while self._continuation or not self._has_started:
            # Check if this is first fetch for read from specific time change feed.
            # For read specific time the first fetch will return empty even if we have more pages.
            is_s_time_first_fetch = self._is_change_feed and self._options.get("startTime") and not self._has_started

            new_options["continuation"] = self._continuation

            response_headers = {}
            (fetched_items, response_headers) = await fetch_function(new_options)
            if not self._has_started:
                self._has_started = True

            continuation_key = http_constants.HttpHeaders.Continuation
            # Use Etag as continuation token for change feed queries.
            if self._is_change_feed:
                continuation_key = http_constants.HttpHeaders.ETag
            # In change feed queries, the continuation token is always populated. The hasNext() test is whether
            # there is any items in the response or not.
            # No initial fetch for start time change feed, so we need to pass continuation token for first fetch
            if not self._is_change_feed or fetched_items or is_s_time_first_fetch:
                self._continuation = response_headers.get(continuation_key)
            else:
                self._continuation = None
            if fetched_items:
                break
        return fetched_items

    async def _fetch_items_helper_with_retries(self, fetch_function):
        async def callback():
            return await self._fetch_items_helper_no_retries(fetch_function)

        return await _retry_utility_async.ExecuteAsync(self._client, self._client._global_endpoint_manager, callback)


class _DefaultQueryExecutionContext(_QueryExecutionContextBase):
    """
    This is the default execution context.
    """

    def __init__(self, client, options, fetch_function):
        """
        :param CosmosClient client:
        :param dict options: The request options for the request.
        :param method fetch_function:
            Will be invoked for retrieving each page

            Example of `fetch_function`:

            >>> def result_fn(result):
            >>>     return result['Databases']

        """
        super(_DefaultQueryExecutionContext, self).__init__(client, options)
        self._fetch_function = fetch_function

    async def _fetch_next_block(self):
        while super(_DefaultQueryExecutionContext, self)._has_more_pages() and not self._buffer:
            return await self._fetch_items_helper_with_retries(self._fetch_function)
