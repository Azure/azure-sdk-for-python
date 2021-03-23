# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, TYPE_CHECKING, List
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import LROBasePolling
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from ._generated import BatchDocumentTranslationClient as _BatchDocumentTranslationClient
from ._generated.models import BatchStatusDetail as _BatchStatusDetail
from ._models import (
    JobStatusResult,
    DocumentStatusResult,
    DocumentTranslationInput,
    FileFormat
)
from ._user_agent import USER_AGENT
from ._polling import TranslationPolling
if TYPE_CHECKING:
    from azure.core.paging import ItemPaged

COGNITIVE_KEY_HEADER = "Ocp-Apim-Subscription-Key"


class DocumentTranslationClient(object):  # pylint: disable=r0205
    """DocumentTranslationClient

    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, AzureKeyCredential, **Any) -> None
        """

        :param str endpoint:
        :param credential:
        :type credential: AzureKeyCredential
        :keyword str api_version:
        """
        self._endpoint = endpoint
        self._credential = credential
        self._api_version = kwargs.pop('api_version', None)

        if credential is None:
            raise ValueError("Parameter 'credential' must not be None.")
        authentication_policy = AzureKeyCredentialPolicy(
            name=COGNITIVE_KEY_HEADER, credential=credential
        )
        self._client = _BatchDocumentTranslationClient(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            api_version=self._api_version,
            sdk_moniker=USER_AGENT,
            authentication_policy=authentication_policy,
            **kwargs
        )

    @distributed_trace
    def create_translation_job(self, inputs, **kwargs):
        # type: (List[DocumentTranslationInput], **Any) -> JobStatusResult
        """

        :param inputs:
        :type inputs: List[~azure.ai.documenttranslation.DocumentTranslationInput]
        :return: JobStatusResult
        :rtype: JobStatusResult
        """

        # submit translation job
        response_headers = self._client.document_translation._submit_batch_request_initial(  # pylint: disable=protected-access
            inputs=DocumentTranslationInput._to_generated_list(inputs),  # pylint: disable=protected-access
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )

        def get_job_id(response_headers):
            operation_loc_header = response_headers['Operation-Location']
            return operation_loc_header.split('/')[-1]

        # get job id from response header
        job_id = get_job_id(response_headers)

        # get job status
        return self.get_job_status(job_id)


    @distributed_trace
    def get_job_status(self, job_id, **kwargs):
        # type: (str, **Any) -> JobStatusResult
        """

        :param job_id: guid id for job
        :type job_id: str
        :rtype: ~azure.ai.documenttranslation.JobStatusResult
        """

        job_status = self._client.document_translation.get_operation_status(job_id, **kwargs)
        return JobStatusResult._from_generated(job_status)  # pylint: disable=protected-access

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
        # type: (str, **Any) -> JobStatusResult
        """

        :param job_id: guid id for job
        :type job_id: str
        :return: JobStatusResult
        :rtype: JobStatusResult
        """

        pipeline_response = self._client.document_translation.get_operation_status(
            job_id,
            cls=lambda pipeline_response, _, response_headers: pipeline_response
        )

        def callback(raw_response):
            detail = self._client._deserialize(_BatchStatusDetail, raw_response)  # pylint: disable=protected-access
            return JobStatusResult._from_generated(detail)  # pylint: disable=protected-access

        poller = LROPoller(
            client=self._client._client,  # pylint: disable=protected-access
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
        # type: (**Any) -> ItemPaged[JobStatusResult]
        """

        :keyword int results_per_page:
        :keyword int skip:
        :rtype: ~azure.core.polling.ItemPaged[JobStatusResult]
        """

        skip = kwargs.pop('skip', None)
        results_per_page = kwargs.pop('results_per_page', None)

        def _convert_from_generated_model(generated_model):  # pylint: disable=protected-access
            return JobStatusResult._from_generated(generated_model)  # pylint: disable=protected-access

        model_conversion_function = kwargs.pop(
            "cls",
            lambda job_statuses: [
                _convert_from_generated_model(job_status) for job_status in job_statuses
            ])

        return self._client.document_translation.get_operations(
            top=results_per_page,
            skip=skip,
            cls=model_conversion_function,
            **kwargs
        )

    @distributed_trace
    def list_all_document_statuses(self, job_id, **kwargs):
        # type: (str, **Any) -> ItemPaged[DocumentStatusResult]
        """

        :param job_id: guid id for job
        :type job_id: str
        :keyword int results_per_page:
        :keyword int skip:
        :rtype: ~azure.core.paging.ItemPaged[DocumentStatusResult]
        """

        skip = kwargs.pop('skip', None)
        results_per_page = kwargs.pop('results_per_page', None)

        def _convert_from_generated_model(generated_model):
            return DocumentStatusResult._from_generated(generated_model)  # pylint: disable=protected-access

        model_conversion_function = kwargs.pop(
            "cls",
            lambda doc_statuses: [
                _convert_from_generated_model(doc_status) for doc_status in doc_statuses
            ])

        return self._client.document_translation.get_operation_documents_status(
            id=job_id,
            top=results_per_page,
            skip=skip,
            cls=model_conversion_function,
            **kwargs
        )


    @distributed_trace
    def get_document_status(self, job_id, document_id, **kwargs):
        # type: (str, str, **Any) -> DocumentStatusResult
        """

        :param job_id: guid id for job
        :type job_id: str
        :param document_id: guid id for document
        :type document_id: str
        :rtype: ~azure.ai.documenttranslation.DocumentStatusResult
        """

        document_status = self._client.document_translation.get_document_status(
            job_id,
            document_id,
            **kwargs)
        return DocumentStatusResult._from_generated(document_status)  # pylint: disable=protected-access

    @distributed_trace
    def get_glossary_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """

        :rtype: List[FileFormat]
        """

        glossary_formats = self._client.document_translation.get_glossary_formats(**kwargs)
        return FileFormat._from_generated_list(glossary_formats.value)  # pylint: disable=protected-access

    @distributed_trace
    def get_document_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """

        :rtype: List[FileFormat]
        """

        document_formats = self._client.document_translation.get_document_formats(**kwargs)
        return FileFormat._from_generated_list(document_formats.value)  # pylint: disable=protected-access
