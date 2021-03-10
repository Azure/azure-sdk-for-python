# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import cast, List, TYPE_CHECKING
import time

from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import ServiceResponseTimeoutError
from ._timer import Timer
from .._utils import is_retryable_status_code
from .._search_indexing_buffered_sender_base import SearchIndexingBufferedSenderBase
from .._generated.aio import SearchClient as SearchIndexClient
from .._generated.models import IndexingResult
from .._search_documents_error import RequestEntityTooLargeError
from ._index_documents_batch_async import IndexDocumentsBatch
from .._headers_mixin import HeadersMixin
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials import AzureKeyCredential


class SearchIndexingBufferedSender(SearchIndexingBufferedSenderBase, HeadersMixin):
    """A buffered sender for document indexing actions.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param index_name: The name of the index to connect to
    :type index_name: str
    :param credential: A credential to authorize search client requests
    :type credential: ~azure.core.credentials.AzureKeyCredential
    :keyword int auto_flush_interval: how many max seconds if between 2 flushes. This only takes effect
        when auto_flush is on. Default to 60 seconds.
    :keyword int initial_batch_action_count: The initial number of actions to group into a batch when
        tuning the behavior of the sender. The default value is 512.
    :keyword int max_retries_per_action: The number of times to retry a failed document. The default value is 3.
    :keyword callable on_new: If it is set, the client will call corresponding methods when there
        is a new IndexAction added.
    :keyword callable on_progress: If it is set, the client will call corresponding methods when there
        is a IndexAction succeeds.
    :keyword callable on_error: If it is set, the client will call corresponding methods when there
        is a IndexAction fails.
    :keyword callable on_remove: If it is set, the client will call corresponding methods when there
        is a IndexAction removed from the queue (succeeds or fails).
    :keyword str api_version: The Search API version to use for requests.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, endpoint, index_name, credential, **kwargs):
        # type: (str, str, AzureKeyCredential, **Any) -> None
        super(SearchIndexingBufferedSender, self).__init__(
            endpoint=endpoint,
            index_name=index_name,
            credential=credential,
            **kwargs)
        self._index_documents_batch = IndexDocumentsBatch()
        self._client = SearchIndexClient(
            endpoint=endpoint,
            index_name=index_name,
            sdk_moniker=SDK_MONIKER,
            api_version=self._api_version, **kwargs
        )  # type: SearchIndexClient
        self._reset_timer()

    async def _cleanup(self, flush=True):
        # type: () -> None
        """Clean up the client.

        :param bool flush: flush the actions queue before shutdown the client
            Default to True.
        """
        if flush:
            await self.flush()
        if self._auto_flush:
            self._timer.cancel()

    def __repr__(self):
        # type: () -> str
        return "<SearchIndexingBufferedSender [endpoint={}, index={}]>".format(
            repr(self._endpoint), repr(self._index_name)
        )[:1024]

    @property
    def actions(self):
        # type: () -> List[IndexAction]
        """The list of currently index actions in queue to index.
        :rtype: List[IndexAction]
        """
        return self._index_documents_batch.actions

    @distributed_trace_async
    async def close(self, **kwargs):  # pylint: disable=unused-argument
        # type: () -> None
        """Close the :class:`~azure.search.documents.aio.SearchClient` session."""
        await self._cleanup(flush=True)
        return await self._client.close()

    @distributed_trace_async
    async def flush(self, timeout=86400, **kwargs):    # pylint:disable=unused-argument
        # type: (bool) -> bool
        """Flush the batch.
        :param int timeout: time out setting. Default is 86400s (one day)
        :return: True if there are errors. Else False
        :rtype: bool
        :raises ~azure.core.exceptions.ServiceResponseTimeoutError:
        """
        has_error = False
        begin_time = int(time.time())
        while len(self.actions) > 0:
            now = int(time.time())
            remaining = timeout - (now - begin_time)
            if remaining < 0:
                if self._on_error:
                    actions = await self._index_documents_batch.dequeue_actions()
                    for action in actions:
                        await self._on_error(action)
                raise ServiceResponseTimeoutError("Service response time out")
            result = await self._process(timeout=remaining, raise_error=False)
            if result:
                has_error = True
        return has_error

    async def _process(self, timeout=86400, **kwargs):
        # type: (int) -> bool
        from ..indexes.aio import SearchIndexClient as SearchServiceClient
        raise_error = kwargs.pop("raise_error", True)
        actions = await self._index_documents_batch.dequeue_actions()
        has_error = False
        if not self._index_key:
            try:
                client = SearchServiceClient(self._endpoint, self._credential)
                result = await client.get_index(self._index_name)
                if result:
                    for field in result.fields:
                        if field.key:
                            self._index_key = field.name
                            break
            except Exception:  # pylint: disable=broad-except
                pass

        self._reset_timer()

        try:
            results = await self._index_documents_actions(actions=actions, timeout=timeout)
            for result in results:
                try:
                    action = next(x for x in actions if x.additional_properties.get(self._index_key) == result.key)
                    if result.succeeded:
                        await self._callback_succeed(action)
                    elif is_retryable_status_code(result.status_code):
                        await self._retry_action(action)
                        has_error = True
                    else:
                        await self._callback_fail(action)
                        has_error = True
                except StopIteration:
                    pass

            return has_error

        except Exception:  # pylint: disable=broad-except
            for action in actions:
                await self._retry_action(action)
                if raise_error:
                    raise
                return True

    async def _process_if_needed(self):
        # type: () -> bool
        """ Every time when a new action is queued, this method
            will be triggered. It checks the actions already queued and flushes them if:
            1. Auto_flush is on
            2. There are self._batch_action_count actions queued
        """
        if not self._auto_flush:
            return

        if len(self._index_documents_batch.actions) < self._batch_action_count:
            return

        await self._process(raise_error=False)

    def _reset_timer(self):
        # pylint: disable=access-member-before-definition
        try:
            self._timer.cancel()
        except AttributeError:
            pass
        if self._auto_flush:
            self._timer = Timer(self._auto_flush_interval, self._process)

    @distributed_trace_async
    async def upload_documents(self, documents, **kwargs):  # pylint: disable=unused-argument
        # type: (List[dict]) -> None
        """Queue upload documents actions.
        :param documents: A list of documents to upload.
        :type documents: List[dict]
        """
        actions = await self._index_documents_batch.add_upload_actions(documents)
        await self._callback_new(actions)
        await self._process_if_needed()

    @distributed_trace_async
    async def delete_documents(self, documents, **kwargs):  # pylint: disable=unused-argument
        # type: (List[dict]) -> None
        """Queue delete documents actions
        :param documents: A list of documents to delete.
        :type documents: List[dict]
        """
        actions = await self._index_documents_batch.add_delete_actions(documents)
        await self._callback_new(actions)
        await self._process_if_needed()

    @distributed_trace_async
    async def merge_documents(self, documents, **kwargs):  # pylint: disable=unused-argument
        # type: (List[dict]) -> None
        """Queue merge documents actions
        :param documents: A list of documents to merge.
        :type documents: List[dict]
        """
        actions = await self._index_documents_batch.add_merge_actions(documents)
        await self._callback_new(actions)
        await self._process_if_needed()

    @distributed_trace_async
    async def merge_or_upload_documents(self, documents, **kwargs):  # pylint: disable=unused-argument
        # type: (List[dict]) -> None
        """Queue merge documents or upload documents actions
        :param documents: A list of documents to merge or upload.
        :type documents: List[dict]
        """
        actions = await self._index_documents_batch.add_merge_or_upload_actions(documents)
        await self._callback_new(actions)
        await self._process_if_needed()

    @distributed_trace_async
    async def index_documents(self, batch, **kwargs):
        # type: (IndexDocumentsBatch, **Any) -> List[IndexingResult]
        """Specify a document operations to perform as a batch.

        :param batch: A batch of document operations to perform.
        :type batch: IndexDocumentsBatch
        :rtype:  List[IndexingResult]
        :raises :class:`~azure.search.documents.RequestEntityTooLargeError`
        """
        return await self._index_documents_actions(actions=batch.actions, **kwargs)

    async def _index_documents_actions(self, actions, **kwargs):
        # type: (List[IndexAction], **Any) -> List[IndexingResult]
        error_map = {413: RequestEntityTooLargeError}

        timeout = kwargs.pop('timeout', 86400)
        begin_time = int(time.time())
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        try:
            batch_response = await self._client.documents.index(actions=actions, error_map=error_map, **kwargs)
            return cast(List[IndexingResult], batch_response.results)
        except RequestEntityTooLargeError:
            if len(actions) == 1:
                raise
            pos = round(len(actions) / 2)
            if pos < self._batch_action_count:
                self._index_documents_batch = pos
            now = int(time.time())
            remaining = timeout - (now - begin_time)
            if remaining < 0:
                raise ServiceResponseTimeoutError("Service response time out")
            batch_response_first_half = await self._index_documents_actions(
                actions=actions[:pos],
                error_map=error_map,
                **kwargs
            )
            if len(batch_response_first_half) > 0:
                result_first_half = cast(List[IndexingResult], batch_response_first_half.results)
            else:
                result_first_half = []
            now = int(time.time())
            remaining = timeout - (now - begin_time)
            if remaining < 0:
                raise ServiceResponseTimeoutError("Service response time out")
            batch_response_second_half = await self._index_documents_actions(
                actions=actions[pos:],
                error_map=error_map,
                **kwargs
            )
            if len(batch_response_second_half) > 0:
                result_second_half = cast(List[IndexingResult], batch_response_second_half.results)
            else:
                result_second_half = []
            return result_first_half.extend(result_second_half)

    async def __aenter__(self):
        # type: () -> SearchIndexingBufferedSender
        await self._client.__aenter__()  # pylint: disable=no-member
        return self

    async def __aexit__(self, *args):
        # type: (*Any) -> None
        await self.close()
        await self._client.__aexit__(*args)  # pylint: disable=no-member

    async def _retry_action(self, action):
        # type: (IndexAction) -> None
        if not self._index_key:
            await self._callback_fail(action)
            return
        key = action.additional_properties.get(self._index_key)
        counter = self._retry_counter.get(key)
        if not counter:
            # first time that fails
            self._retry_counter[key] = 1
            await self._index_documents_batch.enqueue_actions(action)
        elif counter < self._max_retries_per_action - 1:
            # not reach retry limit yet
            self._retry_counter[key] = counter + 1
            await self._index_documents_batch.enqueue_actions(action)
        else:
            await self._callback_fail(action)

    async def _callback_succeed(self, action):
        # type: (IndexAction) -> None
        if self._on_remove:
            await self._on_remove(action)
        if self._on_progress:
            await self._on_progress(action)

    async def _callback_fail(self, action):
        # type: (IndexAction) -> None
        if self._on_remove:
            await self._on_remove(action)
        if self._on_error:
            await self._on_error(action)

    async def _callback_new(self, actions):
        # type: (List[IndexAction]) -> None
        if self._on_new:
            for action in actions:
                await self._on_new(action)
