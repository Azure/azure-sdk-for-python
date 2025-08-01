# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

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
from typing import Optional, Union, Dict, Any, Mapping, Callable, Tuple, List, TYPE_CHECKING
from requests.structures import CaseInsensitiveDict
from azure.core.paging import PageIterator  # type: ignore
from azure.cosmos._execution_context import execution_dispatcher
from azure.cosmos.query_engine import QueryEngine

# pylint: disable=protected-access

if TYPE_CHECKING:
    # We can't import this at runtime because it's circular, so only import it for type checking
    from azure.cosmos._cosmos_client_connection import PartitionKeyType, CosmosClientConnection


class QueryIterable(PageIterator):
    """Represents an iterable object of the query results.

    QueryIterable is a wrapper for query execution context.
    """

    def __init__(
        self,
        client: 'CosmosClientConnection',
        query: Optional[Union[str, Dict[str, Any]]],
        options: Optional[Mapping[str, Any]],
        fetch_function: Callable[[
            Mapping[str, Any]], Tuple[List[Dict[str, Any]], CaseInsensitiveDict]] = None,
        collection_link: Optional[str] = None,
        database_link: Optional[str] = None,
        partition_key: Optional['PartitionKeyType'] = None,
        continuation_token: Optional[str] = None,
        query_engine: Optional[QueryEngine] = None,
        resource_type: str = None,
        response_hook: Optional[Callable[[Mapping[str, Any], Dict[str, Any]], None]] = None,
        raw_response_hook: Optional[Callable[[Mapping[str, Any], Dict[str, Any]], None]] = None,
    ):
        """Instantiates a QueryIterable for non-client side partitioning queries.

        _ProxyQueryExecutionContext will be used as the internal query execution
        context.

        :param CosmosClient client: Instance of document client.
        :param (str or dict) query:
        :param dict options: The request options for the request.
        :param method fetch_function:
        :param str resource_type: The type of the resource being queried

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
            response_hook, raw_response_hook, resource_type, query_engine
        )
        super(QueryIterable, self).__init__(self._fetch_next, self._unpack, continuation_token=continuation_token)

    def _unpack(self, block):
        continuation = None
        if self._client.last_response_headers:
            continuation = self._client.last_response_headers.get("x-ms-continuation") or \
                self._client.last_response_headers.get('etag')
        if block:
            self._did_a_call_already = False
        return continuation, block

    def _fetch_next(self, *args):  # pylint: disable=unused-argument
        """Return a block of results with respecting retry policy.

        This method only exists for backward compatibility reasons. (Because
        QueryIterable has exposed fetch_next_block api).

        :param Any args:
        :return: List of results.
        :rtype: list
        """
        block = self._ex_context.fetch_next_block()
        if not block:
            raise StopIteration
        return block
