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

    def __init__(
            self, endpoint: str, credential: "AzureKeyCredential", **kwargs: Any
    ) -> None:
        """DocumentTranslationClient is your interface to the Document Translation service.
        Use the client to translate whole documents while preserving source document
        structure and text formatting.

        :param str endpoint: Supported Document Translation endpoint (protocol and hostname, for example:
            https://<resource-name>.cognitiveservices.azure.com/).
        :param credential: Credentials needed for the client to connect to Azure.
            Currently only API key authentication is supported.
        :type credential: :class:`~azure.core.credentials.AzureKeyCredential`
        :keyword api_version:
            The API version of the service to use for requests. It defaults to the latest service version.
            Setting to an older version may result in reduced feature compatibility.
        :paramtype api_version: str or ~azure.ai.documenttranslation.DocumentTranslationApiVersion
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

    async def __aenter__(self) -> "DocumentTranslationClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.ai.documenttranslation.aio.DocumentTranslationClient` session."""
        await self._client.__aexit__()

    @distributed_trace_async
    async def create_translation_job(self, inputs, **kwargs):
        # type: (List[DocumentTranslationInput], **Any) -> JobStatusResult
        """Create a document translation job which translates the document(s) in your source container
        to your target container in the given language.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param inputs: A list of translation inputs. Each individual input can contain a single
            source URL to documents and multiple target URLs (one for each language).
        :type inputs: List[~azure.ai.documenttranslation.DocumentTranslationInput]
        :return: A JobStatusResult with information on the status of the job.
        :rtype: ~azure.ai.documenttranslation.JobStatusResult
        :raises ~azure.core.exceptions.HttpResponseError:
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
        """Gets the status of a translation job.

        The status includes the overall job status, as well as a summary of
        the documents that are being translated as part of that job.

        :param str job_id: The translation job ID.
        :return: A JobStatusResult with information on the status of the job.
        :rtype: ~azure.ai.documenttranslation.JobStatusResult
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        job_status = await self._client.document_translation.get_operation_status(job_id, **kwargs)
        # pylint: disable=protected-access
        return JobStatusResult._from_generated(job_status)

    @distributed_trace_async
    async def cancel_job(self, job_id, **kwargs):
        # type: (str, **Any) -> None
        """Cancel a currently processing or queued job.

        A job will not be cancelled if it is already completed, failed, or cancelling.
        All documents that have completed translation will not be cancelled and will be charged.
        All pending documents will be cancelled if possible.

        :param str job_id: The translation job ID.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        await self._client.document_translation.cancel_operation(job_id, **kwargs)

    @distributed_trace_async
    async def wait_until_done(self, job_id, **kwargs):
        # type: (str, **Any) -> JobStatusResult
        """Wait until the translation job is done.

        A job is considered "done" when it reaches a terminal state like
        Succeeded, Failed, Cancelled.

        :param str job_id: The translation job ID.
        :return: A JobStatusResult with information on the status of the job.
        :rtype: ~azure.ai.documenttranslation.JobStatusResult
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
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
        """List all the submitted translation jobs under the Document Translation resource.

        :keyword int top: Use top to indicate the total number of results you want
            to be returned across all pages.
        :keyword int skip: Use skip to indicate the number of results to skip from the list
            of jobs held by the server based on the sorting method specified. By default,
            this is sorted by descending start time.
        :keyword int results_per_page: Use results_per_page to indicate the maximum number
            of results returned in a page.
        :return: AsyncItemPaged[:class:`~azure.ai.documenttranslation.JobStatusResult`]
        :rtype: ~azure.core.paging.AsyncItemPaged
        :raises ~azure.core.exceptions.HttpResponseError:
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
        """List all the document statuses under a translation job.

        :param str job_id: The translation job ID.
        :keyword int top: Use top to indicate the total number of results you want
            to be returned across all pages.
        :keyword int skip: Use skip to indicate the number of results to skip from the list
            of document statuses held by the server based on the sorting method specified. By default,
            this is sorted by descending start time.
        :keyword int results_per_page: Use results_per_page to indicate the maximum number
            of results returned in a page.
        :return: AsyncItemPaged[:class:`~azure.ai.documenttranslation.DocumentStatusResult`]
        :rtype: ~azure.core.paging.AsyncItemPaged
        :raises ~azure.core.exceptions.HttpResponseError:
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
        """Get the status of an individual document within a translation job.

        :param str job_id: The translation job ID.
        :param str document_id: The ID for the document.
        :return: A DocumentStatusResult with information on the status of the document.
        :rtype: ~azure.ai.documenttranslation.DocumentStatusResult
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """
        document_status = await self._client.document_translation.get_document_status(job_id, document_id, **kwargs)
        # pylint: disable=protected-access
        return DocumentStatusResult._from_generated(document_status)


    @distributed_trace_async
    async def get_glossary_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """Get the list of the glossary formats supported by the Document Translation service.

        :return: A list of supported glossary formats.
        :rtype: List[FileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        glossary_formats = await self._client.document_translation.get_glossary_formats(**kwargs)
        # pylint: disable=protected-access
        return FileFormat._from_generated_list(glossary_formats.value)

    @distributed_trace_async
    async def get_document_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """Get the list of the document formats supported by the Document Translation service.

        :return: A list of supported document formats for translation.
        :rtype: List[FileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        document_formats = await self._client.document_translation.get_document_formats(**kwargs)
        # pylint: disable=protected-access
        return FileFormat._from_generated_list(document_formats.value)
