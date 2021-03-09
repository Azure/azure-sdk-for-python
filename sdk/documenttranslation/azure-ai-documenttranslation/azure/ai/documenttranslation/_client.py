# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Union, Any, TYPE_CHECKING, List
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import LROBasePolling
from ._generated import BatchDocumentTranslationClient as _BatchDocumentTranslationClient
from ._generated.models import BatchStatusDetail
from ._helpers import get_authentication_policy
from ._user_agent import USER_AGENT
from ._polling import TranslationPolling
if TYPE_CHECKING:
    from azure.core.paging import ItemPaged
    from azure.core.credentials import AzureKeyCredential, TokenCredential
    from ._models import JobStatusDetail, DocumentStatusDetail, BatchDocumentInput, FileFormat


class DocumentTranslationClient(object):
    """DocumentTranslationClient

    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Union[AzureKeyCredential, TokenCredential], **Any) -> None
        """

        :param str endpoint:
        :param credential:
        :type credential: Union[AzureKeyCredential, TokenCredential]
        :keyword str api_version:
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

    @distributed_trace
    def create_translation_job(self, batch, **kwargs):
        # type: (List[BatchDocumentInput], **Any) -> JobStatusDetail
        """

        :param batch:
        :type batch: List[~azure.ai.documenttranslation.BatchDocumentInput]
        :return: JobStatusDetail
        :rtype: JobStatusDetail
        """

        response_headers = self._client.document_translation._submit_batch_request_initial(
            inputs=batch,
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        job_id = response_headers["Operation-Location"].split("/batches/")[1]
        return self.get_job_status(job_id)

    @distributed_trace
    def get_job_status(self, job_id, **kwargs):
        # type: (str, **Any) -> JobStatusDetail
        """

        :param job_id: guid id for job
        :type job_id: str
        :rtype: ~azure.ai.documenttranslation.JobStatusDetail
        """

        return self._client.document_translation.get_operation_status(job_id, **kwargs)

    @distributed_trace
    def cancel_job(self, job_id, **kwargs):
        # type: (str, **Any) -> None
        """

        :param job_id: guid id for job
        :type job_id: str
        :rtype: None
        """

        self._client.document_translation.cancel_operation(job_id, **kwargs)

    @distributed_trace
    def wait_until_done(self, job_id, **kwargs):
        # type: (str, **Any) -> JobStatusDetail
        """

        :param job_id: guid id for job
        :type job_id: str
        :return: JobStatusDetail
        :rtype: JobStatusDetail
        """

        pipeline_response = self.get_job_status(
            job_id,
            cls=lambda pipeline_response, _, response_headers: pipeline_response
        )

        def callback(raw_response):
            detail = self._client._deserialize(BatchStatusDetail, raw_response)
            # return JobStatusDetail._from_generated(detail)
            return detail

        poller = LROPoller(
            client=self._client._client,
            initial_response=pipeline_response,
            deserialization_callback=callback,
            polling_method=LROBasePolling(
                timeout=30,
                lro_algorithms=[TranslationPolling()],
                **kwargs
            ),
        )
        return poller.result()

    @distributed_trace
    def list_submitted_jobs(self, **kwargs):
        # type: (**Any) -> ItemPaged[JobStatusDetail]
        """

        :keyword int results_per_page:
        :keyword int skip:
        :rtype: ~azure.core.polling.ItemPaged[JobStatusDetail]
        """
        return self._client.document_translation.get_operations(**kwargs)

    @distributed_trace
    def list_documents_statuses(self, job_id, **kwargs):
        # type: (str, **Any) -> ItemPaged[DocumentStatusDetail]
        """

        :param job_id: guid id for job
        :type job_id: str
        :keyword int results_per_page:
        :keyword int skip:
        :rtype: ~azure.core.paging.ItemPaged[DocumentStatusDetail]
        """

        return self._client.document_translation.get_operation_documents_status(job_id, **kwargs)

    @distributed_trace
    def get_document_status(self, job_id, document_id, **kwargs):
        # type: (str, str, **Any) -> DocumentStatusDetail
        """

        :param job_id: guid id for job
        :type job_id: str
        :param document_id: guid id for document
        :type document_id: str
        :rtype: ~azure.ai.documenttranslation.DocumentStatusDetail
        """
        return self._client.document_translation.get_document_status(job_id, document_id, **kwargs)

    @distributed_trace
    def get_supported_storage_sources(self, **kwargs):
        # type: (**Any) -> List[str]
        """

        :rtype: List[str]
        """
        return self._client.document_translation.get_document_storage_source(**kwargs)

    @distributed_trace
    def get_supported_glossary_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """

        :rtype: List[FileFormat]
        """

        return self._client.document_translation.get_glossary_formats(**kwargs)

    @distributed_trace
    def get_supported_document_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """

        :rtype: List[FileFormat]
        """

        return self._client.document_translation.get_document_formats(**kwargs)
