# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
from typing import Any, List, Union, TYPE_CHECKING, overload
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace
from azure.core.async_paging import AsyncItemPaged
from .._generated.aio import BatchDocumentTranslationClient as _BatchDocumentTranslationClient
from .._generated.models import (
    BatchRequest as _BatchRequest,
    SourceInput as _SourceInput,
    TargetInput as _TargetInput,
)
from .._user_agent import USER_AGENT
from .._models import (
    JobStatusResult,
    DocumentTranslationInput,
    FileFormat,
    DocumentStatusResult
)
from .._helpers import get_http_logging_policy, convert_datetime, get_authentication_policy
from ._async_polling import AsyncDocumentTranslationLROPollingMethod, AsyncDocumentTranslationPoller
from .._polling import TranslationPolling
if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential
    from azure.core.credentials_async import AsyncTokenCredential


class DocumentTranslationClient(object):

    def __init__(
            self, endpoint: str, credential: Union["AzureKeyCredential", "AsyncTokenCredential"], **kwargs: Any
    ) -> None:
        """DocumentTranslationClient is your interface to the Document Translation service.
        Use the client to translate whole documents while preserving source document
        structure and text formatting.

        :param str endpoint: Supported Document Translation endpoint (protocol and hostname, for example:
            https://<resource-name>.cognitiveservices.azure.com/).
        :param credential: Credentials needed for the client to connect to Azure.
            This is an instance of AzureKeyCredential if using an API key or a token
            credential from :mod:`azure.identity`.
        :type credential: :class:`~azure.core.credentials.AzureKeyCredential` or
            :class:`~azure.core.credentials.TokenCredential`
        :keyword api_version:
            The API version of the service to use for requests. It defaults to the latest service version.
            Setting to an older version may result in reduced feature compatibility.
        :paramtype api_version: str or ~azure.ai.translation.document.DocumentTranslationApiVersion

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
                :start-after: [START create_dt_client_with_key_async]
                :end-before: [END create_dt_client_with_key_async]
                :language: python
                :dedent: 4
                :caption: Creating the DocumentTranslationClient with an endpoint and API key.

            .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
                :start-after: [START create_dt_client_with_aad_async]
                :end-before: [END create_dt_client_with_aad_async]
                :language: python
                :dedent: 4
                :caption: Creating the DocumentTranslationClient with a token credential.
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
            http_logging_policy=get_http_logging_policy(),
            **kwargs
        )

    async def __aenter__(self) -> "DocumentTranslationClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.ai.translation.document.aio.DocumentTranslationClient` session."""
        await self._client.__aexit__()

    @overload
    async def begin_translation(
        self, source_url: str,
        target_url: str,
        target_language_code: str,
        **kwargs: Any
    ) -> AsyncDocumentTranslationPoller[AsyncItemPaged[DocumentStatusResult]]:
        ...

    @overload
    async def begin_translation(
        self, inputs: List[DocumentTranslationInput],
        **kwargs: Any
    ) -> AsyncDocumentTranslationPoller[AsyncItemPaged[DocumentStatusResult]]:
        ...

    @distributed_trace_async
    async def begin_translation(self, *args, **kwargs):
        """Begin translating the document(s) in your source container to your target container
        in the given language. To perform a single translation from source to target, pass the `source_url`,
        `target_url`, and `target_language_code` parameters. To pass multiple inputs for translation, including
         other translation options, pass the `inputs` parameter as a list of DocumentTranslationInput.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param str source_url: The source SAS URL to the Azure Blob container containing the documents
            to be translated. Requires read and list permissions at the minimum.
        :param str target_url: The target SAS URL to the Azure Blob container where the translated documents
            should be written. Requires write and list permissions at the minimum.
        :param str target_language_code: This is the language you want your documents to be translated to.
            See supported language codes here:
            https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate
        :param inputs: A list of translation inputs. Each individual input has a single
            source URL to documents and can contain multiple TranslationTargets (one for each language)
            for the destination to write translated documents.
        :type inputs: List[~azure.ai.translation.document.DocumentTranslationInput]
        :return: An instance of a DocumentTranslationPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatusResult. A DocumentStatusResult will be
            returned for each translation on a document.
        :rtype: AsyncDocumentTranslationPoller[AsyncItemPaged[~azure.ai.translation.document.DocumentStatusResult]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_begin_translation_async.py
                :start-after: [START begin_translation_async]
                :end-before: [END begin_translation_async]
                :language: python
                :dedent: 4
                :caption: Translate the documents in your storage container.
        """

        continuation_token = kwargs.pop("continuation_token", None)

        try:
            inputs = kwargs.pop('inputs', None)
            if not inputs:
                inputs = args[0]
            inputs = DocumentTranslationInput._to_generated_list(inputs) if not continuation_token else None
        except (AttributeError, TypeError, IndexError):
            try:
                source_url = kwargs.pop('source_url', None)
                if not source_url:
                    source_url = args[0]
                target_url = kwargs.pop("target_url", None)
                if not target_url:
                    target_url = args[1]
                target_language_code = kwargs.pop("target_language_code", None)
                if not target_language_code:
                    target_language_code = args[2]
                inputs = [
                    _BatchRequest(
                        source=_SourceInput(
                            source_url=source_url
                        ),
                        targets=[_TargetInput(
                            target_url=target_url,
                            language=target_language_code
                        )]
                    )
                ]
            except (AttributeError, TypeError, IndexError):
                raise ValueError("Pass either 'inputs' or 'source_url', 'target_url', and 'target_language_code'")

        def deserialization_callback(
            raw_response, _, headers
        ):  # pylint: disable=unused-argument
            translation_status = json.loads(raw_response.http_response.text())
            return self.list_all_document_statuses(translation_status["id"])

        polling_interval = kwargs.pop(
            "polling_interval", self._client._config.polling_interval  # pylint: disable=protected-access
        )

        pipeline_response = None
        if continuation_token:
            pipeline_response = await self._client.document_translation.get_translation_status(
                continuation_token,
                cls=lambda pipeline_response, _, response_headers: pipeline_response,
            )

        callback = kwargs.pop("cls", deserialization_callback)
        return await self._client.document_translation.begin_start_translation(
            inputs=inputs if not continuation_token else None,
            polling=AsyncDocumentTranslationLROPollingMethod(
                timeout=polling_interval,
                lro_algorithms=[
                    TranslationPolling()
                ],
                cont_token_response=pipeline_response,
                **kwargs),
            cls=callback,
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace_async
    async def get_job_status(self, job_id, **kwargs):
        # type: (str, **Any) -> JobStatusResult
        """Gets the status of a translation job.

        The status includes the overall job status, as well as a summary of
        the documents that are being translated as part of that translation job.

        :param str job_id: The translation job ID.
        :return: A JobStatusResult with information on the status of the translation job.
        :rtype: ~azure.ai.translation.document.JobStatusResult
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        job_status = await self._client.document_translation.get_translation_status(job_id, **kwargs)
        # pylint: disable=protected-access
        return JobStatusResult._from_generated(job_status)

    @distributed_trace_async
    async def cancel_job(self, job_id, **kwargs):
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

        await self._client.document_translation.cancel_translation(job_id, **kwargs)

    @distributed_trace
    def list_submitted_jobs(self, **kwargs):
        # type: (**Any) -> AsyncItemPaged[JobStatusResult]
        """List all the submitted translation jobs under the Document Translation resource.

        :keyword int top: the total number of jobs to return (across all pages) from all submitted jobs.
        :keyword int skip: the number of jobs to skip (from beginning of the all submitted jobs).
            By default, we sort by all submitted jobs descendingly by start time.
        :keyword int results_per_page: is the number of jobs returned per page.
        :keyword list[str] job_ids: job ids to filter by.
        :keyword list[str] statuses: job statuses to filter by.
        :keyword Union[str, datetime.datetime] created_after: get jobs created after certain datetime.
        :keyword Union[str, datetime.datetime] created_before: get jobs created before certain datetime.
        :keyword list[str] order_by: the sorting query for the jobs returned.
            format: ["parm1 asc/desc", "parm2 asc/desc", ...]
            (ex: 'createdDateTimeUtc asc', 'createdDateTimeUtc desc').
        :return: ~azure.core.paging.AsyncItemPaged[:class:`~azure.ai.translation.document.JobStatusResult`]
        :rtype: ~azure.core.paging.AsyncItemPaged
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_list_all_submitted_jobs_async.py
                :start-after: [START list_all_jobs_async]
                :end-before: [END list_all_jobs_async]
                :language: python
                :dedent: 4
                :caption: List all submitted jobs under the resource.
        """

        created_after = kwargs.pop("created_after", None)
        created_before = kwargs.pop("created_before", None)
        created_after = convert_datetime(created_after) if created_after else None
        created_before = convert_datetime(created_before) if created_before else None
        results_per_page = kwargs.pop("results_per_page", None)
        job_ids = kwargs.pop("job_ids", None)

        def _convert_from_generated_model(generated_model):
            # pylint: disable=protected-access
            return JobStatusResult._from_generated(generated_model)

        model_conversion_function = kwargs.pop(
            "cls",
            lambda job_statuses: [_convert_from_generated_model(job_status) for job_status in job_statuses]
        )

        return self._client.document_translation.get_translations_status(
            cls=model_conversion_function,
            maxpagesize=results_per_page,
            created_date_time_utc_start=created_after,
            created_date_time_utc_end=created_before,
            ids=job_ids,
            **kwargs
        )

    @distributed_trace
    def list_all_document_statuses(self, job_id, **kwargs):
        # type: (str, **Any) -> AsyncItemPaged[DocumentStatusResult]
        """List all the document statuses for a given translation job.

        :param str job_id: ID of translation job to list documents for.
        :keyword int top: the total number of documents to return (across all pages).
        :keyword int skip: the number of documents to skip (from beginning).
            By default, we sort by all documents descendingly by start time.
        :keyword int results_per_page: is the number of documents returned per page.
        :keyword list[str] document_ids: document IDs to filter by.
        :keyword list[str] statuses: document statuses to filter by.
        :keyword Union[str, datetime.datetime] translated_after: get document translated after certain datetime.
        :keyword Union[str, datetime.datetime] translated_before: get document translated before certain datetime.
        :keyword list[str] order_by: the sorting query for the documents.
            format: ["parm1 asc/desc", "parm2 asc/desc", ...]
            (ex: 'createdDateTimeUtc asc', 'createdDateTimeUtc desc').
        :return: ~azure.core.paging.AsyncItemPaged[:class:`~azure.ai.translation.document.DocumentStatusResult`]
        :rtype: ~azure.core.paging.AsyncItemPaged
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_check_document_statuses_async.py
                :start-after: [START list_all_document_statuses_async]
                :end-before: [END list_all_document_statuses_async]
                :language: python
                :dedent: 8
                :caption: List all the document statuses as they are being translated.
        """
        translated_after = kwargs.pop("translated_after", None)
        translated_before = kwargs.pop("translated_before", None)
        translated_after = convert_datetime(translated_after) if translated_after else None
        translated_before = convert_datetime(translated_before) if translated_before else None
        results_per_page = kwargs.pop("results_per_page", None)
        document_ids = kwargs.pop("document_ids", None)

        def _convert_from_generated_model(generated_model):
            # pylint: disable=protected-access
            return DocumentStatusResult._from_generated(generated_model)

        model_conversion_function = kwargs.pop(
            "cls",
            lambda doc_statuses: [_convert_from_generated_model(doc_status) for doc_status in doc_statuses]
        )

        return self._client.document_translation.get_documents_status(
            id=job_id,
            cls=model_conversion_function,
            maxpagesize=results_per_page,
            created_date_time_utc_start=translated_after,
            created_date_time_utc_end=translated_before,
            ids=document_ids,
            **kwargs
        )

    @distributed_trace_async
    async def get_document_status(self, job_id, document_id, **kwargs):
        # type: (str, str, **Any) -> DocumentStatusResult
        """Get the status of an individual document within a translation job.

        :param str job_id: The translation job ID.
        :param str document_id: The ID for the document.
        :return: A DocumentStatusResult with information on the status of the document.
        :rtype: ~azure.ai.translation.document.DocumentStatusResult
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
        glossary_formats = await self._client.document_translation.get_supported_glossary_formats(**kwargs)
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
        document_formats = await self._client.document_translation.get_supported_document_formats(**kwargs)
        # pylint: disable=protected-access
        return FileFormat._from_generated_list(document_formats.value)
