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

from azure.core.paging import PageIterator

from azure.cosmos._change_feed.change_feed_fetcher import ChangeFeedFetcherV1, ChangeFeedFetcherV2
from azure.cosmos._change_feed.change_feed_state import ChangeFeedStateV1, ChangeFeedState
from azure.cosmos._utils import is_base64_encoded


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

        change_feed_state = self._options.get("changeFeedState")
        if not change_feed_state:
            raise ValueError("Missing changeFeedState in feed options")

        if isinstance(change_feed_state, ChangeFeedStateV1):
            if continuation_token:
                if is_base64_encoded(continuation_token):
                    raise ValueError("Incompatible continuation token")
                else:
                    change_feed_state.apply_server_response_continuation(continuation_token)

            self._change_feed_fetcher = ChangeFeedFetcherV1(
                self._client,
                self._collection_link,
                self._options,
                fetch_function
            )
        else:
            if continuation_token:
                if not is_base64_encoded(continuation_token):
                    raise ValueError("Incompatible continuation token")

                effective_change_feed_context = {"continuationFeedRange": continuation_token}
                effective_change_feed_state = ChangeFeedState.from_json(change_feed_state.container_rid, effective_change_feed_context)
                # replace with the effective change feed state
                self._options["continuationFeedRange"] = effective_change_feed_state

            self._change_feed_fetcher = ChangeFeedFetcherV2(
                self._client,
                self._collection_link,
                self._options,
                fetch_function
            )
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
        block = self._change_feed_fetcher.fetch_next_block()
        if not block:
            raise StopIteration
        return block
