# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, List
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import AsyncLROPoller
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from .._generated.aio import BatchDocumentTranslationClient as _BatchDocumentTranslationClient
from .._user_agent import USER_AGENT
from .._generated.models import (
    BatchStatusDetail as _BatchStatusDetail,
)
from .._models import (
    JobStatusResult,
    DocumentTranslationInput,
    FileFormat,
    DocumentStatusResult
)
from .._polling import TranslationPolling
COGNITIVE_KEY_HEADER = "Ocp-Apim-Subscription-Key"


class DocumentTranslationClient(object):
    """DocumentTranslationClient

    """

    def __init__(
            self, endpoint: str, credential: "AzureKeyCredential", **kwargs: Any
    ) -> None:
        """

        :param str endpoint:
        :param credential:
        :type credential: AzureKeyCredential
        :keyword str api_version:
        :rtype: None
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

    @distributed_trace_async
    async def create_translation_job(self, inputs, **kwargs):
        # type: (List[DocumentTranslationInput], **Any) -> JobStatusResult
        """

        :param inputs:
        :type inputs: List[~azure.ai.documenttranslation.DocumentTranslationInput]
        :return: JobStatusResult
        :rtype: JobStatusResult
        """

        # submit translation job
        response_headers = await self._client.document_translation._submit_batch_request_initial(  # pylint: disable=protected-access
            # pylint: disable=protected-access
            inputs=DocumentTranslationInput._to_generated_list(inputs),
            cls=lambda pipeline_response, _, response_headers: response_headers,
            polling=True,
            **kwargs
        )

        def get_job_id(response_headers):
            # extract job id.
            operation_location_header = response_headers['Operation-Location']
            return operation_location_header.split('/')[-1]

        # get job id from response header
        job_id = get_job_id(response_headers)

        # get job status
        return await self.get_job_status(job_id)


    @distributed_trace_async
    async def get_job_status(self, job_id, **kwargs):
        # type: (str, **Any) -> JobStatusResult
        """

        :param job_id: guid id for job
        :type job_id: str
        :rtype: ~azure.ai.documenttranslation.JobStatusResult
        """

        job_status = await self._client.document_translation.get_operation_status(job_id, **kwargs)
        # pylint: disable=protected-access
        return JobStatusResult._from_generated(job_status)

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
        # type: (str, **Any) -> JobStatusResult
        """

        :param job_id: guid id for job
        :type job_id: str
        :return: JobStatusResult
        :rtype: JobStatusResult
        """
        pipeline_response = await self._client.document_translation.get_operation_status(
            job_id,
            cls=lambda pipeline_response, _, response_headers: pipeline_response
        )

        def callback(raw_response):
            detail = self._client._deserialize(_BatchStatusDetail, raw_response)  # pylint: disable=protected-access
            return JobStatusResult._from_generated(detail)  # pylint: disable=protected-access

        poller = AsyncLROPoller(
            client=self._client._client,  # pylint: disable=protected-access
            initial_response=pipeline_response,
            deserialization_callback=callback,
            polling_method=AsyncLROBasePolling(
                timeout=30,
                lro_algorithms=[TranslationPolling()],
                **kwargs
            ),
        )
        return poller.result()

    @distributed_trace
    def list_submitted_jobs(self, **kwargs):
        # type: (**Any) -> AsyncItemPaged[JobStatusResult]
        """

        :keyword int results_per_page:
        :keyword int skip:
        :rtype: ~azure.core.polling.AsyncItemPaged[JobStatusResult]
        """
        skip = kwargs.pop('skip', None)
        results_per_page = kwargs.pop('results_per_page', None)

        def _convert_from_generated_model(generated_model):
            # pylint: disable=protected-access
            return JobStatusResult._from_generated(generated_model)

        model_conversion_function = kwargs.pop(
            "cls",
            lambda job_statuses: [_convert_from_generated_model(job_status) for job_status in job_statuses]
        )

        return self._client.document_translation.get_operations(
            top=results_per_page,
            skip=skip,
            cls=model_conversion_function,
            **kwargs
        )

    @distributed_trace
    def list_all_document_statuses(self, job_id, **kwargs):
        # type: (str, **Any) -> AsyncItemPaged[DocumentStatusResult]
        """

        :param job_id: guid id for job
        :type job_id: str
        :keyword int results_per_page:
        :keyword int skip:
        :rtype: ~azure.core.paging.AsyncItemPaged[DocumentStatusResult]
        """
        skip = kwargs.pop('skip', None)
        results_per_page = kwargs.pop('results_per_page', None)

        def _convert_from_generated_model(generated_model):
            # pylint: disable=protected-access
            return DocumentStatusResult._from_generated(generated_model)

        model_conversion_function = kwargs.pop(
            "cls",
            lambda doc_statuses: [_convert_from_generated_model(doc_status) for doc_status in doc_statuses]
        )

        return self._client.document_translation.get_operation_documents_status(
            id=job_id,
            top=results_per_page,
            skip=skip,
            cls=model_conversion_function,
            **kwargs
        )


    @distributed_trace_async
    async def get_document_status(self, job_id, document_id, **kwargs):
        # type: (str, str, **Any) -> DocumentStatusResult
        """

        :param job_id: guid id for job
        :type job_id: str
        :param document_id: guid id for document
        :type document_id: str
        :rtype: ~azure.ai.documenttranslation.DocumentStatusResult
        """
        document_status = await self._client.document_translation.get_document_status(job_id, document_id, **kwargs)
        # pylint: disable=protected-access
        return DocumentStatusResult._from_generated(document_status)


    @distributed_trace_async
    async def get_glossary_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """

        :rtype: list[FileFormat]
        """
        glossary_formats = await self._client.document_translation.get_glossary_formats(**kwargs)
        # pylint: disable=protected-access
        return FileFormat._from_generated_list(glossary_formats.value)

    @distributed_trace_async
    async def get_document_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """

        :rtype: list[FileFormat]
        """
        document_formats = await self._client.document_translation.get_document_formats(**kwargs)
        # pylint: disable=protected-access
        return FileFormat._from_generated_list(document_formats.value)
