import copy
import json
from typing import Optional, Union, Dict, List, Mapping, Any, TYPE_CHECKING, cast

from .base_execution_context import _QueryExecutionContextBase
from azure.cosmos import _base
from azure.cosmos._execution_context.query_execution_info import _PartitionedQueryExecutionInfo
from azure.cosmos.query_engine import QueryEngine, QueryPipeline, PipelineResult, DataRequest

from .. import _retry_utility, http_constants

if TYPE_CHECKING:
    # We can't import this at runtime because it's circular, so only import it for type checking
    from azure.cosmos._cosmos_client_connection import CosmosClientConnection


class _QueryEngineExecutionContext(_QueryExecutionContextBase):

    DEFAULT_PAGE_SIZE = 1000

    def __init__(self,
                 # We have to use a string for this annotation because of the circular import problem above
                 client: 'CosmosClientConnection',
                 query_engine: QueryEngine,
                 query_plan: Dict[str, Any],
                 pkranges: List[Dict[str, Any]],
                 query: Optional[Union[str, Dict[str, Any]]],
                 collection_link: str,
                 options: Optional[Mapping[str, Any]] = None):
        super(_QueryEngineExecutionContext, self).__init__(client, options)

        self._options = options or {}
        if self._options.get("maxItemCount"):
            self._page_size = self._options["maxItemCount"]
        else:
            self._page_size = _QueryEngineExecutionContext.DEFAULT_PAGE_SIZE

        self._client = client
        self._query_engine = query_engine
        self._query_plan = query_plan
        self._pkranges = pkranges
        self._collection_link = collection_link

        self._path = _base.GetPathFromLink(collection_link, "docs")
        self._collection_id = cast(str, _base.GetResourceIdOrFullNameFromLink(
            collection_link))

        self._pipeline = self._query_engine.create_pipeline(
            query, query_plan, pkranges)

        # The query plan may have rewritten the query. Either way, we can get the final query from the pipeline.
        self._query = self._pipeline.query()

        self._active_results: Optional[PipelineResult] = None
        self._result_offset = 0
        self._completed = False

    def __next__(self):
        """Returns the next query result.

        :return: The next query result.
        :rtype: dict
        :raises StopIteration: If no more result is left.
        """

        # Ensure we have a buffer of results.
        if not self._completed:
            self._ensure_buffer()

        # Return the next item, if there is one.
        return self._pop_item()

    def fetch_next_block(self):
        """Returns a block of results.

        This method only exists for backward compatibility reasons. (Because
        QueryIterable has exposed fetch_next_block api).

        This method internally invokes next() as many times required to collect
        the requested fetch size.

        :return: List of results.
        :rtype: list
        """

        results = []
        for _ in range(self._page_size):
            try:
                results.append(next(self))
            except StopIteration:
                # no more results
                break
        return results

    def _ensure_buffer(self):
        while True:
            if self._active_results is None:
                self._active_results = self._pipeline.next_batch()

                # If we still don't have results, we're done.
                if self._active_results is None:
                    self._completed = True
                    raise StopIteration()

            self._completed = self._active_results.terminated

            # If this buffer has items, or is terminated, we're done.
            if self._completed or self._items_available():
                return

            # Ok, we have a batch, but it has no more items left.
            # If there are outstanding requests, use them to fill the pipeline.
            for request in self._active_results.requests:
                self._make_request(request)

            # Reset the active results and loop to get more results
            self._active_results = None

    def _fill_pipeline(self):
        assert (self._active_results is not None and len(
            self._active_results.requests) > 0)

        # Make requests
        for request in self._active_results.requests:
            self._make_request(request)

        # Get the next batch of results
        self._active_results = self._pipeline.next_batch()

    def _make_request(self, request: DataRequest):
        def callback():
            new_options = copy.deepcopy(self._options)
            new_options["continuation"] = request.continuation
            return self._client.QueryFeed(self._path, self._collection_id,
                                          self._query, new_options, request.pkrange_id)
        (items, headers) = _retry_utility.Execute(
            self._client, self._client._global_endpoint_manager, callback)

        # Insert the results into the pipeline
        continuation_key = http_constants.HttpHeaders.Continuation
        next_continuation = headers.get(continuation_key)
        self._pipeline.provide_data(
            request.pkrange_id, items, next_continuation)

    def _items_available(self):
        if self._active_results is None:
            return False
        return (len(self._active_results.items) - self._result_offset) > 0

    def _pop_item(self):
        if not self._items_available():
            raise StopIteration()

        index = self._result_offset
        self._result_offset += 1

        # The "cast" function is a no-op at runtime, it just helps the type checker
        return cast(PipelineResult, self._active_results).items[index]

    next = __next__  # Python 2 compatibility.
