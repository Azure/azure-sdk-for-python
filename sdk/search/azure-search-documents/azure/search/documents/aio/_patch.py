# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
# pylint: too-many-instance-attributes
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Union, List, Dict, Optional, cast
import asyncio

from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import ServiceResponseTimeoutError

from ._client import SearchClient as _SearchClient
from ._operations._patch import AsyncSearchItemPaged
from ..models._patch import RequestEntityTooLargeError, IndexDocumentsBatch
from ..models import IndexAction, IndexingResult
from ..indexes.aio import SearchIndexClient
from .._patch import DEFAULT_VERSION, is_retryable_status_code


class SearchClient(_SearchClient):
    """SearchClient.

    :param endpoint: Service host. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a key
        credential type or a token credential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
        ~azure.core.credentials_async.AsyncTokenCredential
    :param index_name: The name of the index. Required.
    :type index_name: str
    :keyword api_version: The API version to use for this operation. Default value is
        "2025-11-01-preview". Note that overriding this default value may result in unsupported
        behavior.
    :paramtype api_version: str
    """

    def __init__(
        self, endpoint: str, index_name: str, credential: Union[AzureKeyCredential, AsyncTokenCredential], **kwargs: Any
    ) -> None:
        super().__init__(endpoint=endpoint, credential=credential, index_name=index_name, **kwargs)


class SearchIndexingBufferedSender:
    """A buffered sender for document indexing actions (async version).

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param index_name: The name of the index to connect to
    :type index_name: str
    :param credential: A credential to authorize search client requests
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials_async.AsyncTokenCredential
    :keyword bool auto_flush: Whether to automatically flush the batch. Default is True.
    :keyword int auto_flush_interval: How many max seconds between 2 flushes. This only takes effect
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
    :keyword str audience: Sets the Audience to use for authentication with Microsoft Entra ID.
    """

    _DEFAULT_AUTO_FLUSH_INTERVAL = 60
    _DEFAULT_INITIAL_BATCH_ACTION_COUNT = 512
    _DEFAULT_MAX_RETRIES = 3

    def __init__(
        self, endpoint: str, index_name: str, credential: Union[AzureKeyCredential, AsyncTokenCredential], **kwargs: Any
    ) -> None:
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._auto_flush = kwargs.pop("auto_flush", True)
        self._batch_action_count = kwargs.pop("initial_batch_action_count", self._DEFAULT_INITIAL_BATCH_ACTION_COUNT)
        self._auto_flush_interval = kwargs.pop("auto_flush_interval", self._DEFAULT_AUTO_FLUSH_INTERVAL)
        if self._auto_flush_interval <= 0:
            raise ValueError("auto_flush_interval must be a positive number.")
        self._max_retries_per_action = kwargs.pop("max_retries_per_action", self._DEFAULT_MAX_RETRIES)
        self._endpoint = endpoint
        self._index_name = index_name
        self._index_key: Optional[str] = None
        self._credential = credential
        self._on_new = kwargs.pop("on_new", None)
        self._on_progress = kwargs.pop("on_progress", None)
        self._on_error = kwargs.pop("on_error", None)
        self._on_remove = kwargs.pop("on_remove", None)
        self._retry_counter: Dict[str, int] = {}

        self._index_documents_batch = IndexDocumentsBatch()

        # Create the search client
        self._client = _SearchClient(
            endpoint=endpoint, index_name=index_name, credential=credential, api_version=self._api_version, **kwargs
        )
        self._auto_flush_task: Optional[asyncio.Task] = None
        if self._auto_flush:
            self._schedule_auto_flush()

    def _schedule_auto_flush(self) -> None:
        """Schedule the auto flush task."""
        if self._auto_flush_task and not self._auto_flush_task.done():
            self._auto_flush_task.cancel()

        async def auto_flush_worker():
            await asyncio.sleep(self._auto_flush_interval)
            await self._process()

        try:
            loop = asyncio.get_event_loop()
            self._auto_flush_task = loop.create_task(auto_flush_worker())
        except RuntimeError:
            # If no event loop is running, we'll schedule when processing happens
            self._auto_flush_task = None

    async def _cleanup(self, flush: bool = True) -> None:
        """Clean up the client.

        :param bool flush: Flush the actions queue before shutdown the client. Default to True.
        """
        if flush:
            await self.flush()
        if self._auto_flush_task and not self._auto_flush_task.done():
            self._auto_flush_task.cancel()

    def __repr__(self) -> str:
        return "<SearchIndexingBufferedSender [endpoint={}, index={}]>".format(
            repr(self._endpoint), repr(self._index_name)
        )[:1024]

    @property
    def actions(self) -> List[IndexAction]:
        """The list of currently index actions in queue to index.

        :rtype: list[IndexAction]
        """
        return self._index_documents_batch.actions if self._index_documents_batch.actions else []

    @distributed_trace_async
    async def close(self, **kwargs) -> None:  # pylint: disable=unused-argument
        """Close the session.

        :return: None
        :rtype: None
        """
        await self._cleanup(flush=True)
        await self._client.close()

    @distributed_trace_async
    async def flush(self, timeout: int = 86400, **kwargs: Any) -> bool:  # pylint:disable=unused-argument
        """Flush the batch.

        :param int timeout: Time out setting. Default is 86400s (one day)
        :return: True if there are errors. Else False
        :rtype: bool
        :raises ~azure.core.exceptions.ServiceResponseTimeoutError:
        """
        has_error = False
        begin_time = asyncio.get_event_loop().time()
        while len(self.actions) > 0:
            now = asyncio.get_event_loop().time()
            remaining = timeout - (now - begin_time)
            if remaining < 0:
                if self._on_error:
                    actions = self._index_documents_batch.dequeue_actions()
                    for action in actions:
                        if asyncio.iscoroutinefunction(self._on_error):
                            await self._on_error(action)
                        else:
                            self._on_error(action)
                raise ServiceResponseTimeoutError("Service response time out")
            result = await self._process(timeout=remaining, raise_error=False)
            if result:
                has_error = True
        return has_error

    async def _process(self, timeout: int = 86400, **kwargs) -> bool:
        raise_error = kwargs.pop("raise_error", True)
        actions = self._index_documents_batch.dequeue_actions()
        has_error = False

        if not self._index_key:
            try:
                credential = cast(Union[AzureKeyCredential, AsyncTokenCredential], self._credential)
                client = SearchIndexClient(self._endpoint, credential)
                index_result = await client.get_index(self._index_name)
                if index_result:
                    for field in index_result.fields:
                        if field.key:
                            self._index_key = field.name
                            break
                await client.close()
            except Exception:  # pylint: disable=broad-except
                pass

        self._schedule_auto_flush()

        try:
            results = await self._index_documents_actions(actions=actions, timeout=timeout)
            for result in results:
                try:
                    assert self._index_key is not None  # Hint for mypy
                    action = next(x for x in actions if x and str(x.get(self._index_key)) == result.key)
                    if result.succeeded:
                        await self._callback_succeed(action)
                    elif is_retryable_status_code(result.status_code):
                        self._retry_action(action)
                        has_error = True
                    else:
                        await self._callback_fail(action)
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

    async def _process_if_needed(self) -> bool:
        """Check if processing is needed and process if necessary.

        :return: True if process had errors, False otherwise
        :rtype: bool
        """
        if not self._auto_flush:
            return False

        if (
            len(self._index_documents_batch.actions if self._index_documents_batch.actions else [])
            < self._batch_action_count
        ):
            return False

        return await self._process(raise_error=False)

    @distributed_trace_async
    async def upload_documents(self, documents: List[Dict], **kwargs) -> None:  # pylint: disable=unused-argument
        """Queue upload documents actions.

        :param documents: A list of documents to upload.
        :type documents: list[dict]
        """
        actions = self._index_documents_batch.add_upload_actions(documents)
        await self._callback_new(actions)
        await self._process_if_needed()

    @distributed_trace_async
    async def delete_documents(self, documents: List[Dict], **kwargs) -> None:  # pylint: disable=unused-argument
        """Queue delete documents actions

        :param documents: A list of documents to delete.
        :type documents: list[dict]
        """
        actions = self._index_documents_batch.add_delete_actions(documents)
        await self._callback_new(actions)
        await self._process_if_needed()

    @distributed_trace_async
    async def merge_documents(self, documents: List[Dict], **kwargs) -> None:  # pylint: disable=unused-argument
        """Queue merge documents actions

        :param documents: A list of documents to merge.
        :type documents: list[dict]
        """
        actions = self._index_documents_batch.add_merge_actions(documents)
        await self._callback_new(actions)
        await self._process_if_needed()

    @distributed_trace_async
    async def merge_or_upload_documents(self, documents: List[Dict], **kwargs) -> None:
        # pylint: disable=unused-argument
        """Queue merge documents or upload documents actions

        :param documents: A list of documents to merge or upload.
        :type documents: list[dict]
        """
        actions = self._index_documents_batch.add_merge_or_upload_actions(documents)
        await self._callback_new(actions)
        await self._process_if_needed()

    @distributed_trace_async
    async def index_documents(self, batch: IndexDocumentsBatch, **kwargs) -> List[IndexingResult]:
        """Specify a document operations to perform as a batch.

        :param batch: A batch of document operations to perform.
        :type batch: IndexDocumentsBatch
        :return: Indexing result of each action in the batch.
        :rtype: list[IndexingResult]
        :raises ~azure.search.documents.RequestEntityTooLargeError: The request is too large.
        """
        return await self._index_documents_actions(actions=batch.actions if batch.actions else [], **kwargs)

    async def _index_documents_actions(self, actions: List[IndexAction], **kwargs) -> List[IndexingResult]:
        timeout = kwargs.pop("timeout", 86400)
        begin_time = asyncio.get_event_loop().time()

        batch = IndexDocumentsBatch(actions=actions)
        try:
            batch_response = await self._client.index_documents(batch=batch, **kwargs)
            return cast(List[IndexingResult], batch_response)
        except RequestEntityTooLargeError as ex:
            if len(actions) == 1:
                raise
            pos = round(len(actions) / 2)
            if pos < self._batch_action_count:
                self._index_documents_batch.enqueue_actions(actions)
            now = asyncio.get_event_loop().time()
            remaining = timeout - (now - begin_time)
            if remaining < 0:
                raise ServiceResponseTimeoutError("Service response time out") from ex
            batch_response_first_half = await self._index_documents_actions(
                actions=actions[:pos], timeout=remaining, **kwargs
            )
            result_first_half = list(batch_response_first_half) if batch_response_first_half else []

            now = asyncio.get_event_loop().time()
            remaining = timeout - (now - begin_time)
            if remaining < 0:
                raise ServiceResponseTimeoutError("Service response time out") from ex
            batch_response_second_half = await self._index_documents_actions(
                actions=actions[pos:], timeout=remaining, **kwargs
            )
            result_second_half = list(batch_response_second_half) if batch_response_second_half else []

            result_first_half.extend(result_second_half)
            return result_first_half

    async def __aenter__(self) -> "SearchIndexingBufferedSender":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
        await self._client.__aexit__(*args)

    def _retry_action(self, action: IndexAction) -> None:
        if not self._index_key:
            asyncio.create_task(self._callback_fail(action))
            return
        key = cast(str, action.get(self._index_key) if action else "")
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
            asyncio.create_task(self._callback_fail(action))

    async def _callback_succeed(self, action: IndexAction) -> None:
        if self._on_remove:
            if asyncio.iscoroutinefunction(self._on_remove):
                await self._on_remove(action)
            else:
                self._on_remove(action)
        if self._on_progress:
            if asyncio.iscoroutinefunction(self._on_progress):
                await self._on_progress(action)
            else:
                self._on_progress(action)

    async def _callback_fail(self, action: IndexAction) -> None:
        if self._on_remove:
            if asyncio.iscoroutinefunction(self._on_remove):
                await self._on_remove(action)
            else:
                self._on_remove(action)
        if self._on_error:
            if asyncio.iscoroutinefunction(self._on_error):
                await self._on_error(action)
            else:
                self._on_error(action)

    async def _callback_new(self, actions: List[IndexAction]) -> None:
        if self._on_new:
            for action in actions:
                if asyncio.iscoroutinefunction(self._on_new):
                    await self._on_new(action)
                else:
                    self._on_new(action)


__all__: list[str] = [
    "SearchClient",
    "AsyncSearchItemPaged",
    "SearchIndexingBufferedSender",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
