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

"""Iterable query results in the Azure Cosmos database service.
"""
import asyncio # pylint: disable=do-not-import-asyncio
import time
from typing import List

from azure.core.async_paging import AsyncPageIterator
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._constants import _Constants, TimeoutScope
from azure.cosmos._execution_context.aio import execution_dispatcher
from azure.cosmos import exceptions

# pylint: disable=protected-access


class QueryIterable(AsyncPageIterator):  # pylint: disable=too-many-instance-attributes
    """Represents an iterable object of the query results.

    QueryIterable is a wrapper for query execution context.
    """

    def __init__(
        self,
        client,
        query,
        options,
        fetch_function=None,
        collection_link=None,
        database_link=None,
        partition_key=None,
        continuation_token=None,
        resource_type=None,
        response_hook=None,
        raw_response_hook=None,
    ):
        """Instantiates a QueryIterable for non-client side partitioning queries.

        _ProxyQueryExecutionContext will be used as the internal query execution
        context.

        :param CosmosClient client: Instance of document client.
        :param (str or dict) query:
        :param dict options: The request options for the request.
        :param method fetch_function:
        :param str resource_type: The type of the resource being queried
        :param str resource_link: If this is a Document query/feed collection_link is required.

        Example of `fetch_function`:

        >>> def result_fn(result):
        >>>     return result['Databases']

        """
        self._client = client
        self.retry_options = client.connection_policy.RetryOptions
        self._query = query
        self._options = options
        if continuation_token:
            options['continuation'] = continuation_token
        self._fetch_function = fetch_function
        self._collection_link = collection_link
        self._database_link = database_link
        self._partition_key = partition_key
        self._ex_context = execution_dispatcher._ProxyQueryExecutionContext(
            self._client, self._collection_link, self._query, self._options, self._fetch_function,
            response_hook, raw_response_hook, resource_type)

        # Response headers tracking for query operations
        self._response_headers: List[CaseInsensitiveDict] = []

        super(QueryIterable, self).__init__(self._fetch_next, self._unpack, continuation_token=continuation_token)

    async def _unpack(self, block):
        continuation = None
        if self._client.last_response_headers:
            continuation = self._client.last_response_headers.get("x-ms-continuation") or \
                           self._client.last_response_headers.get('etag')
        if block:
            self._did_a_call_already = False
        return continuation, block

    async def _fetch_next(self, *args):  # pylint: disable=unused-argument
        """Return a block of results with respecting retry policy.

        This method only exists for backward compatibility reasons. (Because
        QueryIterable has exposed fetch_next_block api).

        :param Any args:
        :return: List of results.
        :rtype: list
        """
        timeout = self._options.get('timeout')
        if 'partitionKey' in self._options and asyncio.iscoroutine(self._options['partitionKey']):
            self._options['partitionKey'] = await self._options['partitionKey']

        # Check timeout before fetching next block

        if timeout and self._options.get(_Constants.TimeoutScope) != TimeoutScope.OPERATION:
            self._options[_Constants.OperationStartTime] = time.time()

        # Check timeout before fetching next block
        if timeout:
            elapsed = time.time() - self._options.get(_Constants.OperationStartTime)
            if elapsed >= timeout:
                raise exceptions.CosmosClientTimeoutError()

        block = await self._ex_context.fetch_next_block()

        # Capture response headers after each page fetch
        self._capture_response_headers()

        if not block:
            raise StopAsyncIteration
        return block

    def _capture_response_headers(self) -> None:
        """Capture response headers from the last request.

        Note: This captures headers from client.last_response_headers immediately after
        the fetch operation. In concurrent scenarios where multiple operations share the
        same client, headers may be overwritten. For most single-iterator use cases,
        this provides accurate header capture.
        """
        if self._client.last_response_headers:
            headers = self._client.last_response_headers.copy()
            self._response_headers.append(headers)

    def get_response_headers(self) -> List[CaseInsensitiveDict]:
        """Get all response headers collected during query iteration.

        Each entry in the list corresponds to one page/request made during
        the query execution. Headers are captured as queries are iterated,
        so this list grows as you consume more results.

        This method is typically accessed via the
        :class:`~azure.cosmos.aio.CosmosAsyncItemPaged` object returned from
        :meth:`~azure.cosmos.aio.ContainerProxy.query_items`.

        :return: List of response headers from each page request.
        :rtype: list[~azure.core.utils.CaseInsensitiveDict]

        Example::

            # container.query_items returns a CosmosAsyncItemPaged instance
            >>> paged_items = container.query_items(query="SELECT * FROM c")
            >>> async for item in paged_items:
            ...     process(item)
            >>> headers = paged_items.get_response_headers()
            >>> print(f"Total pages fetched: {len(headers)}")
        """
        return [h.copy() for h in self._response_headers]

    def get_last_response_headers(self) -> CaseInsensitiveDict:
        """Get the response headers from the most recent page fetch.

        :return: Response headers from the last page, or empty dict if no pages fetched yet.
        :rtype: ~azure.core.utils.CaseInsensitiveDict
        """
        if self._response_headers:
            return self._response_headers[-1].copy()
        return CaseInsensitiveDict()
