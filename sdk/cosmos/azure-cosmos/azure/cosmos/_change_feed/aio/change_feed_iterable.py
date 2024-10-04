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

"""Iterable change feed results in the Azure Cosmos database service.
"""
from typing import Dict, Any, Optional, Callable, Tuple, List, Awaitable, Union

from azure.core.async_paging import AsyncPageIterator

from azure.cosmos._change_feed.aio.change_feed_fetcher import ChangeFeedFetcherV1, ChangeFeedFetcherV2
from azure.cosmos._change_feed.change_feed_state import ChangeFeedState, ChangeFeedStateVersion


# pylint: disable=protected-access

class ChangeFeedIterable(AsyncPageIterator):
    """Represents an iterable object of the change feed results.

    ChangeFeedIterable is a wrapper for change feed execution.
    """

    def __init__(
        self,
        client,
        options: Dict[str, Any],
        fetch_function=Optional[Callable[[Dict[str, Any]], Awaitable[Tuple[List[Dict[str, Any]], Dict[str, Any]]]]],
        collection_link=Optional[str],
        continuation_token=Optional[str],
    ) -> None:
        """Instantiates a ChangeFeedIterable for non-client side partitioning queries.

             :param CosmosClient client: Instance of document client.
             :param dict options: The request options for the request.
             :param fetch_function: The fetch function.
             :param collection_link: The collection resource link.
             :param continuation_token: The continuation token passed in from by_page
        """

        self._client = client
        self.retry_options = client.connection_policy.RetryOptions
        self._options = options
        self._fetch_function = fetch_function
        self._collection_link = collection_link
        self._change_feed_fetcher: Optional[Union[ChangeFeedFetcherV1, ChangeFeedFetcherV2]] = None

        if self._options.get("changeFeedStateContext") is None:
            raise ValueError("Missing changeFeedStateContext in feed options")

        change_feed_state_context = self._options.pop("changeFeedStateContext")

        continuation =  continuation_token if continuation_token is not None\
            else change_feed_state_context.pop("continuation", None)

        # analysis and validate continuation token
        # there are two types of continuation token we support currently:
        # v1 version: the continuation token would just be the _etag,
        # which is being returned when customer is using partition_key_range_id,
        # which is under deprecation and does not support split/merge
        # v2 version: the continuation token will be base64 encoded composition token
        # which includes full change feed state
        if continuation is not None:
            if continuation.isdigit() or continuation.strip('\'"').isdigit():
                change_feed_state_context["continuationPkRangeId"] = continuation
            else:
                change_feed_state_context["continuationFeedRange"] = continuation

        self._validate_change_feed_state_context(change_feed_state_context)
        self._options["changeFeedStateContext"] = change_feed_state_context

        super(ChangeFeedIterable, self).__init__(
            self._fetch_next,
            self._unpack, # type: ignore[arg-type]
            continuation_token=continuation_token)

    async def _unpack(
            self,
            block: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        continuation: Optional[str] = None
        if self._client.last_response_headers:
            continuation = self._client.last_response_headers.get('etag')

        if block:
            self._did_a_call_already = False
        return continuation, block

    async def _fetch_next(self, *args) -> List[Dict[str, Any]]:  # pylint: disable=unused-argument
        """Return a block of results with respecting retry policy.

        :param Any args:
        :return: List of results.
        :rtype: list
        """
        if self._change_feed_fetcher is None:
            await self._initialize_change_feed_fetcher()

        assert self._change_feed_fetcher is not None
        block = await self._change_feed_fetcher.fetch_next_block()
        if not block:
            raise StopAsyncIteration
        return block

    async def _initialize_change_feed_fetcher(self) -> None:
        change_feed_state_context = self._options.pop("changeFeedStateContext")
        conn_properties = await self._options.pop("containerProperties")
        if change_feed_state_context.get("partitionKey"):
            change_feed_state_context["partitionKey"] = await change_feed_state_context.pop("partitionKey")
            change_feed_state_context["partitionKeyFeedRange"] =\
                await change_feed_state_context.pop("partitionKeyFeedRange")

        change_feed_state =\
            ChangeFeedState.from_json(self._collection_link, conn_properties["_rid"], change_feed_state_context)
        self._options["changeFeedState"] = change_feed_state

        if change_feed_state.version == ChangeFeedStateVersion.V1:
            self._change_feed_fetcher = ChangeFeedFetcherV1(
                self._client,
                self._collection_link,
                self._options,
                self._fetch_function
            )
        else:
            self._change_feed_fetcher = ChangeFeedFetcherV2(
                self._client,
                self._collection_link,
                self._options,
                self._fetch_function
            )

    def _validate_change_feed_state_context(self, change_feed_state_context: Dict[str, Any]) -> None:

        if change_feed_state_context.get("continuationPkRangeId") is not None:
            # if continuation token is in v1 format, throw exception if feed_range is set
            if change_feed_state_context.get("feedRange") is not None:
                raise ValueError("feed_range and continuation are incompatible")
        elif change_feed_state_context.get("continuationFeedRange") is not None:
            # if continuation token is in v2 format, since the token itself contains the full change feed state
            # so we will ignore other parameters (including incompatible parameters) if they passed in
            pass
        else:
            # validation when no continuation is passed
            exclusive_keys = ["partitionKeyRangeId", "partitionKey", "feedRange"]
            count = sum(1 for key in exclusive_keys if
                        key in change_feed_state_context and change_feed_state_context[key] is not None)
            if count > 1:
                raise ValueError(
                    "partition_key_range_id, partition_key, feed_range are exclusive parameters,"
                    " please only set one of them")
