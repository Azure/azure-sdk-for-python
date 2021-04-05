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

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, AzureKeyCredential, **Any) -> None
        """DocumentTranslationClient is your interface to the Document Translation service.
        Use the client to translate whole documents while preserving source document
        structure and text formatting.

        :param str endpoint: Supported Document Translation endpoint (protocol and hostname, for example:
            https://<resource-name>.cognitiveservices.azure.com/).
        :param credential: Credential needed for the client to connect to Azure.
            Currently only API key authentication is supported.
        :type credential: :class:`~azure.core.credentials.AzureKeyCredential`
        :keyword api_version:
            The API version of the service to use for requests. It defaults to the latest service version.
            Setting to an older version may result in reduced feature compatibility.
        :paramtype api_version: str or ~azure.ai.translation.document.DocumentTranslationApiVersion

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_authentication.py
                :start-after: [START create_dt_client_with_key]
                :end-before: [END create_dt_client_with_key]
                :language: python
                :dedent: 4
                :caption: Creating the DocumentTranslationClient with an endpoint and API key.
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

    def __enter__(self):
        # type: () -> DocumentTranslationClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.ai.translation.document.DocumentTranslationClient` session."""
        return self._client.close()

    @distributed_trace
    def create_translation_job(self, inputs, **kwargs):
        # type: (List[DocumentTranslationInput], **Any) -> JobStatusResult
        """Create a document translation job which translates the document(s) in your source container
        to your TranslationTarget(s) in the given language.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param inputs: A list of translation inputs. Each individual input has a single
            source URL to documents and can contain multiple TranslationTargets (one for each language)
            for the destination to write translated documents.
        :type inputs: List[~azure.ai.translation.document.DocumentTranslationInput]
        :return: A JobStatusResult with information on the status of the translation job.
        :rtype: ~azure.ai.translation.document.JobStatusResult
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_check_document_statuses.py
                :start-after: [START create_translation_job]
                :end-before: [END create_translation_job]
                :language: python
                :dedent: 4
                :caption: Create a translation job.
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
        """Gets the status of a translation job.

        The status includes the overall job status, as well as a summary of
        the documents that are being translated as part of that translation job.

        :param str job_id: The translation job ID.
        :return: A JobStatusResult with information on the status of the translation job.
        :rtype: ~azure.ai.translation.document.JobStatusResult
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        job_status = self._client.document_translation.get_operation_status(job_id, **kwargs)
        return JobStatusResult._from_generated(job_status)  # pylint: disable=protected-access

    @distributed_trace
    def cancel_job(self, job_id, **kwargs):
        # type: (str, **Any) -> None
        """Cancel a currently processing or queued job.

        A job will not be cancelled if it is already completed, failed, or cancelling.
        All documents that have completed translation will not be cancelled and will be charged.
        If possible, all pending documents will be cancelled.

        :param str job_id: The translation job ID.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        self._client.document_translation.cancel_operation(job_id, **kwargs)

    @distributed_trace
    def wait_until_done(self, job_id, **kwargs):
        # type: (str, **Any) -> JobStatusResult
        """Wait until the translation job is done.

        A job is considered "done" when it reaches a terminal state like
        Succeeded, Failed, Cancelled.

        :param str job_id: The translation job ID.
        :return: A JobStatusResult with information on the status of the translation job.
        :rtype: ~azure.ai.translation.document.JobStatusResult
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
            Will raise if validation fails on the input. E.g. insufficient permissions on the blob containers.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_translation_job.py
                :start-after: [START wait_until_done]
                :end-before: [END wait_until_done]
                :language: python
                :dedent: 4
                :caption: Create a translation job and wait until it is done.
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
                timeout=self._client._config.polling_interval,  # pylint: disable=protected-access
                lro_algorithms=[TranslationPolling()],
                **kwargs
            ),
        )
        return poller.result()

    @distributed_trace
    def list_submitted_jobs(self, **kwargs):
        # type: (**Any) -> ItemPaged[JobStatusResult]
        """List all the submitted translation jobs under the Document Translation resource.

        :return: ~azure.core.paging.ItemPaged[:class:`~azure.ai.translation.document.JobStatusResult`]
        :rtype: ~azure.core.paging.ItemPaged
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_list_all_submitted_jobs.py
                :start-after: [START list_all_jobs]
                :end-before: [END list_all_jobs]
                :language: python
                :dedent: 4
                :caption: List all submitted jobs under the resource.
        """

        def _convert_from_generated_model(generated_model):  # pylint: disable=protected-access
            return JobStatusResult._from_generated(generated_model)  # pylint: disable=protected-access

        model_conversion_function = kwargs.pop(
            "cls",
            lambda job_statuses: [
                _convert_from_generated_model(job_status) for job_status in job_statuses
            ])

        return self._client.document_translation.get_operations(
            cls=model_conversion_function,
            **kwargs
        )

    @distributed_trace
    def list_all_document_statuses(self, job_id, **kwargs):
        # type: (str, **Any) -> ItemPaged[DocumentStatusResult]
        """List all the document statuses under a translation job.

        :param str job_id: The translation job ID.
        :return: ~azure.core.paging.ItemPaged[:class:`~azure.ai.translation.document.DocumentStatusResult`]
        :rtype: ~azure.core.paging.ItemPaged
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_create_translation_job.py
                :start-after: [START list_all_document_statuses]
                :end-before: [END list_all_document_statuses]
                :language: python
                :dedent: 4
                :caption: List all the document statuses under the translation job.
        """

        def _convert_from_generated_model(generated_model):
            return DocumentStatusResult._from_generated(generated_model)  # pylint: disable=protected-access

        model_conversion_function = kwargs.pop(
            "cls",
            lambda doc_statuses: [
                _convert_from_generated_model(doc_status) for doc_status in doc_statuses
            ])

        return self._client.document_translation.get_operation_documents_status(
            id=job_id,
            cls=model_conversion_function,
            **kwargs
        )

    @distributed_trace
    def get_document_status(self, job_id, document_id, **kwargs):
        # type: (str, str, **Any) -> DocumentStatusResult
        """Get the status of an individual document within a translation job.

        :param str job_id: The translation job ID.
        :param str document_id: The ID for the document.
        :return: A DocumentStatusResult with information on the status of the document.
        :rtype: ~azure.ai.translation.document.DocumentStatusResult
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        document_status = self._client.document_translation.get_document_status(
            job_id,
            document_id,
            **kwargs)
        return DocumentStatusResult._from_generated(document_status)  # pylint: disable=protected-access

    @distributed_trace
    def get_glossary_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """Get the list of the glossary formats supported by the Document Translation service.

        :return: A list of supported glossary formats.
        :rtype: List[FileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        glossary_formats = self._client.document_translation.get_glossary_formats(**kwargs)
        return FileFormat._from_generated_list(glossary_formats.value)  # pylint: disable=protected-access

    @distributed_trace
    def get_document_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """Get the list of the document formats supported by the Document Translation service.

        :return: A list of supported document formats for translation.
        :rtype: List[FileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        document_formats = self._client.document_translation.get_document_formats(**kwargs)
        return FileFormat._from_generated_list(document_formats.value)  # pylint: disable=protected-access
