# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Union, Any, TYPE_CHECKING, List
from azure.core.tracing.decorator import distributed_trace
from ._generated import BatchDocumentTranslationClient as _BatchDocumentTranslationClient
from ._helpers import get_authentication_policy
from ._user_agent import USER_AGENT
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

        # submit translation job
        response_headers = self._client.document_translation._submit_batch_request_initial(
            inputs = BatchDocumentInput._to_generated_list(batch),
            cls = lambda x,y,z: z,
            **kwargs
        )

        # get job id from response header
        job_id = response_headers['Operation-Location']

        # get job status
        return self.get_job_status(job_id)


    @distributed_trace
    def get_job_status(self, job_id, **kwargs):
        # type: (str, **Any) -> JobStatusDetail
        """

        :param job_id: guid id for job
        :type job_id: str
        :rtype: ~azure.ai.documenttranslation.JobStatusDetail
        """

        job_status = self._client.document_translation.get_operation_status(job_id, **kwargs)
        return JobStatusDetail._from_generated(job_status)

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
        pass

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

        skip = kwargs.pop('skip', None)
        top = kwargs.pop('top', None)

        def _convert_from_generated_model(generated_model):
            return DocumentStatusDetail._from_generated(generated_model)

        model_conversion_function = kwargs.pop("cls", lambda doc_statuses: [_convert_from_generated_model(doc_status) for doc_status in doc_statuses])

        return self._client.document_translation.get_operation_documents_status(
            top = top,
            skip = skip,
            cls = model_conversion_function,
            **kwargs
        )


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

        result = self._client.document_translation.get_document_status(job_id, document_id, **kwargs)
        return DocumentStatusDetail._from_generated(result)

    @distributed_trace
    def get_supported_storage_sources(self, **kwargs):
        # type: (**Any) -> List[str]
        """

        :rtype: List[str]
        """
        result = self._client.document_translation.get_document_storage_source(**kwargs)
        return result.value

    @distributed_trace
    def get_supported_glossary_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """

        :rtype: List[FileFormat]
        """

        glossary_formats = self._client.document_translation.get_glossary_formats(**kwargs)
        return FileFormat._from_generated_list(glossary_formats)

    @distributed_trace
    def get_supported_document_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """

        :rtype: List[FileFormat]
        """

        document_formats = self._client.document_translation.get_document_formats(**kwargs)
        return FileFormat._from_generated_list(document_formats)
