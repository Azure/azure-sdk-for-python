# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import cast, List, TYPE_CHECKING
import time
import threading

from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import ServiceResponseTimeoutError
from ._utils import is_retryable_status_code, get_authentication_policy
from .indexes import SearchIndexClient as SearchServiceClient
from ._search_indexing_buffered_sender_base import SearchIndexingBufferedSenderBase
from ._generated import SearchClient as SearchIndexClient
from ._generated.models import IndexingResult
from ._search_documents_error import RequestEntityTooLargeError
from ._index_documents_batch import IndexDocumentsBatch
from ._headers_mixin import HeadersMixin
from ._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Union
    from azure.core.credentials import TokenCredential

class SearchIndexingBufferedSender(SearchIndexingBufferedSenderBase, HeadersMixin):
    """A buffered sender for document indexing actions.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param index_name: The name of the index to connect to
    :type index_name: str
    :param credential: A credential to authorize search client requests
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential
    :keyword int auto_flush_interval: how many max seconds if between 2 flushes. This only takes effect
        when auto_flush is on. Default to 60 seconds.
    :keyword int initial_batch_action_count: The initial number of actions to group into a batch when
        tuning the behavior of the sender. The default value is 512.
    :keyword int max_retries_per_action: The number of times to retry a failed document. The default value is 3.
    :keyword callable on_new: If it is set, the client will call corresponding methods when there
        is a new IndexAction added. This may be called from main thread or a worker thread.
    :keyword callable on_progress: If it is set, the client will call corresponding methods when there
        is a IndexAction succeeds. This may be called from main thread or a worker thread.
    :keyword callable on_error: If it is set, the client will call corresponding methods when there
        is a IndexAction fails. This may be called from main thread or a worker thread.
    :keyword callable on_remove: If it is set, the client will call corresponding methods when there
        is a IndexAction removed from the queue (succeeds or fails). This may be called from main
        thread or a worker thread.
    :keyword str api_version: The Search API version to use for requests.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, endpoint, index_name, credential, **kwargs):
        # type: (str, str, Union[AzureKeyCredential, TokenCredential], **Any) -> None
        super(SearchIndexingBufferedSender, self).__init__(
            endpoint=endpoint,
            index_name=index_name,
            credential=credential,
            **kwargs)
        self._index_documents_batch = IndexDocumentsBatch()
        if isinstance(credential, AzureKeyCredential):
            self._aad = False
            self._client = SearchIndexClient(
                endpoint=endpoint,
                index_name=index_name,
                sdk_moniker=SDK_MONIKER,
                api_version=self._api_version, **kwargs
            )  # type: SearchIndexClient
        else:
            self._aad = True
            authentication_policy = get_authentication_policy(credential)
            self._client = SearchIndexClient(
                endpoint=endpoint,
                index_name=index_name,
                authentication_policy=authentication_policy,
                sdk_moniker=SDK_MONIKER,
                api_version=self._api_version, **kwargs
            )  # type: SearchIndexClient
        self._reset_timer()

    def _cleanup(self, flush=True):
        # type: () -> None
        """Clean up the client.

        :param bool flush: flush the actions queue before shutdown the client
            Default to True.
        """
        if flush:
            self.flush()
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

    @distributed_trace
    def close(self, **kwargs):  # pylint: disable=unused-argument
        # type: () -> None
        """Close the :class:`~azure.search.documents.SearchClient` session."""
        self._cleanup(flush=True)
        return self._client.close()

    @distributed_trace
    def flush(self, timeout=86400, **kwargs):   # pylint:disable=unused-argument
        # type: (int) -> bool
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
                    actions = self._index_documents_batch.dequeue_actions()
                    for action in actions:
                        self._on_error(action)
                raise ServiceResponseTimeoutError("Service response time out")
            result = self._process(timeout=remaining, raise_error=False)
            if result:
                has_error = True
        return has_error

    def _process(self, timeout=86400, **kwargs):
        # type: (int) -> bool
        raise_error = kwargs.pop("raise_error", True)
        actions = self._index_documents_batch.dequeue_actions()
        has_error = False
        if not self._index_key:
            try:
                client = SearchServiceClient(self._endpoint, self._credential)
                result = client.get_index(self._index_name)
                if result:
                    for field in result.fields:
                        if field.key:
                            self._index_key = field.name
                            break
            except Exception:  # pylint: disable=broad-except
                pass

        self._reset_timer()

        try:
            results = self._index_documents_actions(actions=actions, timeout=timeout)
            for result in results:
                try:
                    action = next(x for x in actions if x.additional_properties.get(self._index_key) == result.key)
                    if result.succeeded:
                        self._callback_succeed(action)
                    elif is_retryable_status_code(result.status_code):
                        self._retry_action(action)
                        has_error = True
                    else:
                        self._callback_fail(action)
                        has_error = True
                except StopIteration:
                    pass
            return has_error
        except Exception:  # pylint: disable=broad-except
            for action in actions:
                self._retry_action(action)
                if raise_error:
                    raise
                return True

    def _process_if_needed(self):
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

        self._process(raise_error=False)

    def _reset_timer(self):
        # pylint: disable=access-member-before-definition
        try:
            self._timer.cancel()
        except AttributeError:
            pass
        self._timer = threading.Timer(self._auto_flush_interval, self._process)
        if self._auto_flush:
            self._timer.start()

    @distributed_trace
    def upload_documents(self, documents, **kwargs):  # pylint: disable=unused-argument
        # type: (List[dict]) -> None
        """Queue upload documents actions.

        :param documents: A list of documents to upload.
        :type documents: List[dict]
        """
        actions = self._index_documents_batch.add_upload_actions(documents)
        self._callback_new(actions)
        self._process_if_needed()

    @distributed_trace
    def delete_documents(self, documents, **kwargs):  # pylint: disable=unused-argument
        # type: (List[dict]) -> None
        """Queue delete documents actions

        :param documents: A list of documents to delete.
        :type documents: List[dict]
        """
        actions = self._index_documents_batch.add_delete_actions(documents)
        self._callback_new(actions)
        self._process_if_needed()

    @distributed_trace
    def merge_documents(self, documents, **kwargs):  # pylint: disable=unused-argument
        # type: (List[dict]) -> None
        """Queue merge documents actions

        :param documents: A list of documents to merge.
        :type documents: List[dict]
        """
        actions = self._index_documents_batch.add_merge_actions(documents)
        self._callback_new(actions)
        self._process_if_needed()

    @distributed_trace
    def merge_or_upload_documents(self, documents, **kwargs):  # pylint: disable=unused-argument
        # type: (List[dict]) -> None
        """Queue merge documents or upload documents actions

        :param documents: A list of documents to merge or upload.
        :type documents: List[dict]
        """
        actions = self._index_documents_batch.add_merge_or_upload_actions(documents)
        self._callback_new(actions)
        self._process_if_needed()

    @distributed_trace
    def index_documents(self, batch, **kwargs):
        # type: (IndexDocumentsBatch, **Any) -> List[IndexingResult]
        """Specify a document operations to perform as a batch.

        :param batch: A batch of document operations to perform.
        :type batch: IndexDocumentsBatch
        :rtype:  List[IndexingResult]
        :raises :class:`~azure.search.documents.RequestEntityTooLargeError`
        """
        return self._index_documents_actions(actions=batch.actions, **kwargs)

    def _index_documents_actions(self, actions, **kwargs):
        # type: (List[IndexAction], **Any) -> List[IndexingResult]
        error_map = {413: RequestEntityTooLargeError}

        timeout = kwargs.pop('timeout', 86400)
        begin_time = int(time.time())
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        try:
            batch_response = self._client.documents.index(actions=actions, error_map=error_map, **kwargs)
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
            batch_response_first_half = self._index_documents_actions(
                actions=actions[:pos],
                error_map=error_map,
                timeout=remaining,
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
            batch_response_second_half = self._index_documents_actions(
                actions=actions[pos:],
                error_map=error_map,
                timeout=remaining,
                **kwargs
            )
            if len(batch_response_second_half) > 0:
                result_second_half = cast(List[IndexingResult], batch_response_second_half.results)
            else:
                result_second_half = []
            return result_first_half.extend(result_second_half)

    def __enter__(self):
        # type: () -> SearchIndexingBufferedSender
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self.close()
        self._client.__exit__(*args)  # pylint:disable=no-member

    def _retry_action(self, action):
        # type: (IndexAction) -> None
        if not self._index_key:
            self._callback_fail(action)
            return
        key = action.additional_properties.get(self._index_key)
        counter = self._retry_counter.get(key)
        if not counter:
            # first time that fails
            self._retry_counter[key] = 1
            self._index_documents_batch.enqueue_actions(action)
        elif counter < self._max_retries_per_action - 1:
            # not reach retry limit yet
            self._retry_counter[key] = counter + 1
            self._index_documents_batch.enqueue_actions(action)
        else:
            self._callback_fail(action)

    def _callback_succeed(self, action):
        # type: (IndexAction) -> None
        if self._on_remove:
            self._on_remove(action)
        if self._on_progress:
            self._on_progress(action)

    def _callback_fail(self, action):
        # type: (IndexAction) -> None
        if self._on_remove:
            self._on_remove(action)
        if self._on_error:
            self._on_error(action)

    def _callback_new(self, actions):
        # type: (List[IndexAction]) -> None
        if self._on_new:
            for action in actions:
                self._on_new(action)
