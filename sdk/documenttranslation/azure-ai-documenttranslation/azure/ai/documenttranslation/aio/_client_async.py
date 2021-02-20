# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Union, Any, List, TYPE_CHECKING
from azure.core.polling import AsyncLROPoller
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace
from azure.core.async_paging import AsyncItemPaged
from .._generated.aio import BatchDocumentTranslationClient as _BatchDocumentTranslationClient
from .._user_agent import USER_AGENT
from .._models import BatchStatusDetail, DocumentStatusDetail, BatchDocumentInput, FileFormat
from .._helpers import get_authentication_policy
if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.credentials import AzureKeyCredential


class DocumentTranslationClient(object):
    """DocumentTranslationClient

    """

    def __init__(
            self, endpoint: str, credential: Union["AzureKeyCredential", "AsyncTokenCredential"], **kwargs: Any
    ) -> None:
        """

        :param str endpoint:
        :param credential:
        :type credential: Union[AzureKeyCredential, AsyncTokenCredential]
        :keyword str api_version:
        :rtype: None
        """
        self._endpoint = endpoint
        self._credential = credential
        self._api_version = kwargs.pop('api_version', None)

        authentication_policy = get_authentication_policy(credential)
        self._client = _BatchDocumentTranslationClient(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            api_version=self._api_version,
            sdk_moniker=USER_AGENT,
            authentication_policy=authentication_policy,
            polling_interval=5,  # TODO what is appropriate polling interval
            **kwargs
        )

    @distributed_trace_async
    async def begin_batch_translation(self, inputs, **kwargs):
        # type: (List[BatchDocumentInput], **Any) -> AsyncLROPoller[BatchStatusDetail]
        """

        :param inputs:
        :type inputs: List[~azure.ai.documenttranslation.BatchDocumentInput]
        :rtype: ~azure.core.polling.AsyncLROPoller[BatchStatusDetail]
        """
        return await self._client.document_translation.begin_submit_batch_request(
            inputs=inputs,
            polling=True,
            **kwargs
        )

    @distributed_trace_async
    async def get_batch_status(self, batch_id, **kwargs):
        # type: (Union[AsyncLROPoller, str], **Any) -> BatchStatusDetail
        """

        :param batch_id: guid id for batch or poller object
        :type batch_id: Union[~azure.core.polling.AsyncLROPoller, str]
        :rtype: ~azure.ai.documenttranslation.BatchStatusDetail
        """
        if isinstance(batch_id, AsyncLROPoller):
            batch_id = batch_id.batch_id

        return await self._client.document_translation.get_operation_status(batch_id, **kwargs)

    @distributed_trace_async
    async def cancel_batch(self, batch_id, **kwargs):
        # type: (Union[AsyncLROPoller, str], **Any) -> None
        """

        :param batch_id: guid id for batch or poller object
        :type batch_id: Union[~azure.core.polling.AsyncLROPoller, str]
        :rtype: None
        """
        if isinstance(batch_id, AsyncLROPoller):
            batch_id = batch_id.batch_id

        await self._client.document_translation.cancel_operation(batch_id, **kwargs)

    @distributed_trace
    def list_batches(self, **kwargs):
        # type: (**Any) -> AsyncItemPaged[BatchStatusDetail]
        """

        :keyword int results_per_page:
        :keyword int skip:
        :rtype: ~azure.core.async_paging.AsyncItemPaged[BatchStatusDetail]
        """
        return self._client.document_translation.get_operations(**kwargs)

    @distributed_trace
    def list_documents_statuses(self, batch_id, **kwargs):
        # type: (Union[AsyncLROPoller, str], **Any) -> AsyncItemPaged[DocumentStatusDetail]
        """

        :param batch_id: guid id for batch or poller object
        :type batch_id: Union[~azure.core.polling.AsyncLROPoller, str]
        :keyword int results_per_page:
        :keyword int skip:
        :rtype: ~azure.core.async_paging.AsyncItemPaged[DocumentStatusDetail]
        """
        if isinstance(batch_id, AsyncLROPoller):
            batch_id = batch_id.batch_id

        return self._client.document_translation.get_operation_documents_status(batch_id, **kwargs)

    @distributed_trace_async
    async def get_document_status(self, batch_id, document_id, **kwargs):
        # type: (Union[AsyncLROPoller, str], str, **Any) -> DocumentStatusDetail
        """

        :param batch_id: guid id for batch or poller object
        :type batch_id: Union[~azure.core.polling.AsyncLROPoller, str]
        :param document_id: guid id for document
        :type document_id: str
        :rtype: ~azure.ai.documenttranslation.DocumentStatusDetail
        """
        return await self._client.document_translation.get_document_status(batch_id, document_id, **kwargs)

    @distributed_trace_async
    async def get_supported_storage_sources(self, **kwargs):
        # type: (**Any) -> List[str]
        """

        :rtype: list[str]
        """
        return await self._client.document_translation.get_document_storage_source(**kwargs)

    @distributed_trace_async
    async def get_supported_glossary_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """

        :rtype: list[FileFormat]
        """

        return await self._client.document_translation.get_glossary_formats(**kwargs)

    @distributed_trace_async
    async def get_supported_document_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """

        :rtype: list[FileFormat]
        """

        return await self._client.document_translation.get_document_formats(**kwargs)
