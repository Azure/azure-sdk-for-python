# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Union, Any, List, TYPE_CHECKING
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace
from azure.core.async_paging import AsyncItemPaged
from .._generated.aio import BatchDocumentTranslationClient as _BatchDocumentTranslationClient
from .._user_agent import USER_AGENT
from .._models import JobStatusDetail, DocumentStatusDetail, BatchDocumentInput, FileFormat
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
        polling_interval = kwargs.pop("polling_interval", 30)

        authentication_policy = get_authentication_policy(credential)
        self._client = _BatchDocumentTranslationClient(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            api_version=self._api_version,
            sdk_moniker=USER_AGENT,
            authentication_policy=authentication_policy,
            polling_interval=polling_interval,
            **kwargs
        )

    @distributed_trace_async
    async def create_translation_job(self, batch, **kwargs):
        # type: (List[BatchDocumentInput], **Any) -> JobStatusDetail
        """

        :param batch:
        :type batch: List[~azure.ai.documenttranslation.BatchDocumentInput]
        :return: JobStatusDetail
        :rtype: JobStatusDetail
        """

        return await self._client.document_translation.begin_submit_batch_request(
            inputs=batch,
            polling=True,
            **kwargs
        )

    @distributed_trace_async
    async def get_job_status(self, job_id, **kwargs):
        # type: (str, **Any) -> JobStatusDetail
        """

        :param job_id: guid id for job
        :type job_id: str
        :rtype: ~azure.ai.documenttranslation.JobStatusDetail
        """

        return await self._client.document_translation.get_operation_status(job_id, **kwargs)

    @distributed_trace_async
    async def cancel_job(self, job_id, **kwargs):
        # type: (str, **Any) -> None
        """

        :param job_id: guid id for job
        :type job_id: str
        :rtype: None
        """

        await self._client.document_translation.cancel_operation(job_id, **kwargs)

    @distributed_trace_async
    async def wait_until_done(self, job_id, **kwargs):
        # type: (str, **Any) -> JobStatusDetail
        """

        :param job_id: guid id for job
        :type job_id: str
        :return: JobStatusDetail
        :rtype: JobStatusDetail
        """
        pass

    @distributed_trace
    def list_submitted_jobs(self, **kwargs):
        # type: (**Any) -> AsyncItemPaged[JobStatusDetail]
        """

        :keyword int results_per_page:
        :keyword int skip:
        :rtype: ~azure.core.polling.AsyncItemPaged[JobStatusDetail]
        """
        return self._client.document_translation.get_operations(**kwargs)

    @distributed_trace
    def list_documents_statuses(self, job_id, **kwargs):
        # type: (str, **Any) -> AsyncItemPaged[DocumentStatusDetail]
        """

        :param job_id: guid id for job
        :type job_id: str
        :keyword int results_per_page:
        :keyword int skip:
        :rtype: ~azure.core.paging.AsyncItemPaged[DocumentStatusDetail]
        """

        return self._client.document_translation.get_operation_documents_status(job_id, **kwargs)

    @distributed_trace_async
    async def get_document_status(self, job_id, document_id, **kwargs):
        # type: (str, str, **Any) -> DocumentStatusDetail
        """

        :param job_id: guid id for job
        :type job_id: str
        :param document_id: guid id for document
        :type document_id: str
        :rtype: ~azure.ai.documenttranslation.DocumentStatusDetail
        """
        return await self._client.document_translation.get_document_status(job_id, document_id, **kwargs)

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
