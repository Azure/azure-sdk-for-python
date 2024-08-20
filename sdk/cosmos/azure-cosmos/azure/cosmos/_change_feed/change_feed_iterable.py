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
from typing import Dict, Any

from azure.core.paging import PageIterator

from azure.cosmos._change_feed.change_feed_fetcher import ChangeFeedFetcherV1, ChangeFeedFetcherV2
from azure.cosmos._change_feed.change_feed_state import ChangeFeedStateV1, ChangeFeedState
from azure.cosmos._utils import is_base64_encoded, is_key_exists_and_not_none


class ChangeFeedIterable(PageIterator):
    """Represents an iterable object of the change feed results.

    ChangeFeedIterable is a wrapper for change feed execution.
    """

    def __init__(
        self,
        client,
        options,
        fetch_function=None,
        collection_link=None,
        continuation_token=None,
    ):
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
        self._change_feed_fetcher = None

        if not is_key_exists_and_not_none(self._options, "changeFeedStateContext"):
            raise ValueError("Missing changeFeedStateContext in feed options")

        change_feed_state_context = self._options.pop("changeFeedStateContext")
        continuation = continuation_token if continuation_token is not None\
            else change_feed_state_context.pop("continuation", None)

        # analysis and validate continuation token
        # there are two types of continuation token we support currently:
        # v1 version: the continuation token would just be the _etag,
        # which is being returned when customer is using partition_key_range_id,
        # which is under deprecation and does not support split/merge
        # v2 version: the continuation token will be base64 encoded composition token
        # which includes full change feed state
        if continuation is not None:
            if is_base64_encoded(continuation):
                change_feed_state_context["continuationFeedRange"] = continuation
            else:
                change_feed_state_context["continuationPkRangeId"] = continuation

        self._validate_change_feed_state_context(change_feed_state_context)
        self._options["changeFeedStateContext"] = change_feed_state_context

        super(ChangeFeedIterable, self).__init__(self._fetch_next, self._unpack, continuation_token=continuation_token)

    def _unpack(self, block):
        continuation = None
        if self._client.last_response_headers:
            continuation = self._client.last_response_headers.get('etag')

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

        if self._change_feed_fetcher is None:
            self._initialize_change_feed_fetcher()

        block = self._change_feed_fetcher.fetch_next_block()
        if not block:
            raise StopIteration
        return block

    def _initialize_change_feed_fetcher(self):
        change_feed_state_context = self._options.pop("changeFeedStateContext")
        change_feed_state = \
            ChangeFeedState.from_json(
                self._collection_link,
                self._options.get("containerRID"),
                change_feed_state_context)

        self._options["changeFeedState"] = change_feed_state

        if isinstance(change_feed_state, ChangeFeedStateV1):
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

        if is_key_exists_and_not_none(change_feed_state_context, "continuationPkRangeId"):
            # if continuation token is in v1 format, throw exception if feed_range is set
            if is_key_exists_and_not_none(change_feed_state_context, "feedRange"):
                raise ValueError("feed_range and continuation are incompatible")
        elif is_key_exists_and_not_none(change_feed_state_context, "continuationFeedRange"):
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
