# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import cast, List, Any, Union, Dict
import time
import threading

from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import ServiceResponseTimeoutError
from ._utils import is_retryable_status_code, get_authentication_policy
from .indexes import SearchIndexClient as SearchServiceClient
from ._search_indexing_buffered_sender_base import SearchIndexingBufferedSenderBase
from ._generated import SearchIndexClient
from ._generated.models import IndexingResult, IndexBatch, IndexAction
from ._search_documents_error import RequestEntityTooLargeError
from ._index_documents_batch import IndexDocumentsBatch
from ._headers_mixin import HeadersMixin
from ._version import SDK_MONIKER


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
    :keyword str audience: sets the Audience to use for authentication with Azure Active Directory (AAD). The
        audience is not considered when using a shared key. If audience is not provided, the public cloud audience
        will be assumed.
    """

    _client: SearchIndexClient

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self, endpoint: str, index_name: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any
    ) -> None:
        super(SearchIndexingBufferedSender, self).__init__(
            endpoint=endpoint, index_name=index_name, credential=credential, **kwargs
        )
        self._index_documents_batch = IndexDocumentsBatch()
        audience = kwargs.pop("audience", None)
        if isinstance(credential, AzureKeyCredential):
            self._aad = False
            self._client = SearchIndexClient(
                endpoint=endpoint,
                index_name=index_name,
                sdk_moniker=SDK_MONIKER,
                api_version=self._api_version,
                **kwargs
            )
        else:
            self._aad = True
            authentication_policy = get_authentication_policy(credential, audience=audience)
            self._client = SearchIndexClient(
                endpoint=endpoint,
                index_name=index_name,
                authentication_policy=authentication_policy,
                sdk_moniker=SDK_MONIKER,
                api_version=self._api_version,
                **kwargs
            )
        self._reset_timer()

    def _cleanup(self, flush: bool = True) -> None:
        """Clean up the client.

        :param bool flush: flush the actions queue before shutdown the client
            Default to True.
        """
        if flush:
            self.flush()
        if self._auto_flush:
            self._timer.cancel()

    def __repr__(self) -> str:
        return "<SearchIndexingBufferedSender [endpoint={}, index={}]>".format(
            repr(self._endpoint), repr(self._index_name)
        )[:1024]

    @property
    def actions(self) -> List[IndexAction]:
        """The list of currently index actions in queue to index.

        :rtype: list[IndexAction]
        """
        return self._index_documents_batch.actions

    @distributed_trace
    def close(self, **kwargs) -> None:  # pylint: disable=unused-argument
        """Close the session.
        :return: None
        :rtype: None
        """
        self._cleanup(flush=True)
        return self._client.close()

    @distributed_trace
    def flush(self, timeout: int = 86400, **kwargs: Any) -> bool:  # pylint:disable=unused-argument
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

    def _process(self, timeout: int = 86400, **kwargs) -> bool:
        raise_error = kwargs.pop("raise_error", True)
        actions = self._index_documents_batch.dequeue_actions()
        has_error = False
        if not self._index_key:
            try:
                credential = cast(Union[AzureKeyCredential, TokenCredential], self._credential)
                client = SearchServiceClient(self._endpoint, credential)
                index_result = client.get_index(self._index_name)
                if index_result:
                    for field in index_result.fields:
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
                    assert self._index_key is not None  # Hint for mypy
                    action = next(
                        x
                        for x in actions
                        if x.additional_properties and x.additional_properties.get(self._index_key) == result.key
                    )
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
        return has_error

    def _process_if_needed(self) -> bool:
        """Every time when a new action is queued, this method
        will be triggered. It checks the actions already queued and flushes them if:
        1. Auto_flush is on
        2. There are self._batch_action_count actions queued
        :return: True if proces is needed, False otherwise
        :rtype: bool
        """
        if not self._auto_flush:
            return False

        if len(self._index_documents_batch.actions) < self._batch_action_count:
            return False

        return self._process(raise_error=False)

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
    def upload_documents(self, documents: List[Dict], **kwargs) -> None:  # pylint: disable=unused-argument
        """Queue upload documents actions.

        :param documents: A list of documents to upload.
        :type documents: list[dict]
        """
        actions = self._index_documents_batch.add_upload_actions(documents)
        self._callback_new(actions)
        self._process_if_needed()

    @distributed_trace
    def delete_documents(self, documents: List[Dict], **kwargs) -> None:  # pylint: disable=unused-argument
        """Queue delete documents actions

        :param documents: A list of documents to delete.
        :type documents: list[dict]
        """
        actions = self._index_documents_batch.add_delete_actions(documents)
        self._callback_new(actions)
        self._process_if_needed()

    @distributed_trace
    def merge_documents(self, documents: List[Dict], **kwargs) -> None:  # pylint: disable=unused-argument
        """Queue merge documents actions

        :param documents: A list of documents to merge.
        :type documents: list[dict]
        """
        actions = self._index_documents_batch.add_merge_actions(documents)
        self._callback_new(actions)
        self._process_if_needed()

    @distributed_trace
    def merge_or_upload_documents(self, documents: List[Dict], **kwargs) -> None:
        # pylint: disable=unused-argument
        """Queue merge documents or upload documents actions

        :param documents: A list of documents to merge or upload.
        :type documents: list[dict]
        """
        actions = self._index_documents_batch.add_merge_or_upload_actions(documents)
        self._callback_new(actions)
        self._process_if_needed()

    @distributed_trace
    def index_documents(self, batch: IndexDocumentsBatch, **kwargs) -> List[IndexingResult]:
        """Specify a document operations to perform as a batch.

        :param batch: A batch of document operations to perform.
        :type batch: IndexDocumentsBatch
        :return: Indexing result of each action in the batch.
        :rtype:  list[IndexingResult]

        :raises ~azure.search.documents.RequestEntityTooLargeError
        """
        return self._index_documents_actions(actions=batch.actions, **kwargs)

    def _index_documents_actions(self, actions: List[IndexAction], **kwargs) -> List[IndexingResult]:
        error_map = {413: RequestEntityTooLargeError}

        timeout = kwargs.pop("timeout", 86400)
        begin_time = int(time.time())
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        batch = IndexBatch(actions=actions)
        try:
            batch_response = self._client.documents.index(batch=batch, error_map=error_map, **kwargs)
            return cast(List[IndexingResult], batch_response.results)
        except RequestEntityTooLargeError as ex:
            if len(actions) == 1:
                raise
            pos = round(len(actions) / 2)
            if pos < self._batch_action_count:
                self._index_documents_batch.enqueue_actions(actions)
            now = int(time.time())
            remaining = timeout - (now - begin_time)
            if remaining < 0:
                raise ServiceResponseTimeoutError("Service response time out") from ex
            batch_response_first_half = self._index_documents_actions(
                actions=actions[:pos], error_map=error_map, timeout=remaining, **kwargs
            )
            if len(batch_response_first_half) > 0:
                result_first_half = batch_response_first_half
            else:
                result_first_half = []
            now = int(time.time())
            remaining = timeout - (now - begin_time)
            if remaining < 0:
                raise ServiceResponseTimeoutError("Service response time out") from ex
            batch_response_second_half = self._index_documents_actions(
                actions=actions[pos:], error_map=error_map, timeout=remaining, **kwargs
            )
            if len(batch_response_second_half) > 0:
                result_second_half = batch_response_second_half
            else:
                result_second_half = []
            result_first_half.extend(result_second_half)
            return result_first_half

    def __enter__(self) -> "SearchIndexingBufferedSender":
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args) -> None:
        self.close()
        self._client.__exit__(*args)

    def _retry_action(self, action: IndexAction) -> None:
        if not self._index_key:
            self._callback_fail(action)
            return
        key = cast(str, action.additional_properties.get(self._index_key) if action.additional_properties else "")
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

    def _callback_succeed(self, action: IndexAction) -> None:
        if self._on_remove:
            self._on_remove(action)
        if self._on_progress:
            self._on_progress(action)

    def _callback_fail(self, action: IndexAction) -> None:
        if self._on_remove:
            self._on_remove(action)
        if self._on_error:
            self._on_error(action)

    def _callback_new(self, actions: List[IndexAction]) -> None:
        if self._on_new:
            for action in actions:
                self._on_new(action)
