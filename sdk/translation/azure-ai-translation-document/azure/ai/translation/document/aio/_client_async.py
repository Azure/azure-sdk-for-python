# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
import datetime
from typing import Any, List, Union, TYPE_CHECKING, overload, Optional, cast
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace
from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AzureKeyCredential
from .._generated.aio import (
    BatchDocumentTranslationClient as _BatchDocumentTranslationClient,
)
from .._user_agent import USER_AGENT
from .._models import (
    TranslationStatus,
    DocumentTranslationInput,
    DocumentTranslationFileFormat,
    DocumentStatus,
    convert_status,
    StorageInputType,
    TranslationGlossary
)
from .._helpers import (
    get_http_logging_policy,
    convert_datetime,
    convert_order_by,
    get_authentication_policy,
    get_translation_input,
    POLLING_INTERVAL,
)
from ._async_polling import (
    AsyncDocumentTranslationLROPollingMethod,
    AsyncDocumentTranslationLROPoller,
)
from .._polling import TranslationPolling

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class DocumentTranslationClient:
    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "AsyncTokenCredential"],
        **kwargs: Any
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
        try:
            self._endpoint = endpoint.rstrip("/")
        except AttributeError:
            raise ValueError("Parameter 'endpoint' must be a string.")
        self._credential = credential
        self._api_version = kwargs.pop("api_version", None)

        authentication_policy = get_authentication_policy(credential)
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        self._client = _BatchDocumentTranslationClient(
            endpoint=self._endpoint,
            credential=credential,  # type: ignore
            api_version=self._api_version,
            sdk_moniker=USER_AGENT,
            authentication_policy=kwargs.pop("authentication_policy", authentication_policy),
            http_logging_policy=kwargs.pop("http_logging_policy", get_http_logging_policy()),
            polling_interval=polling_interval,
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
        self,
        source_url: str,
        target_url: str,
        target_language: str,
        *,
        source_language: Optional[str] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        storage_type: Optional[Union[str, StorageInputType]] = None,
        category_id: Optional[str] = None,
        glossaries: Optional[List[TranslationGlossary]] = None,
        **kwargs: Any
    ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language. There are two ways to call this method:

        1) To perform translation on documents from a single source container to a single target container, pass the
        `source_url`, `target_url`, and `target_language` parameters including any optional keyword arguments.

        2) To pass multiple inputs for translation (multiple sources or targets), pass the `inputs` parameter
        as a list of :class:`~azure.ai.translation.document.DocumentTranslationInput`.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param str source_url: The source SAS URL to the Azure Blob container containing the documents
            to be translated. See the service documentation for the supported SAS permissions for accessing
            source storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions
        :param str target_url: The target SAS URL to the Azure Blob container where the translated documents
            should be written. See the service documentation for the supported SAS permissions for accessing
            target storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions
        :param str target_language: This is the language code you want your documents to be translated to.
            See supported language codes here:
            https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate
        :keyword str source_language: Language code for the source documents.
            If none is specified, the source language will be auto-detected for each document.
        :keyword str prefix: A case-sensitive prefix string to filter documents in the source path for
            translation. For example, when using a Azure storage blob Uri, use the prefix to restrict
            sub folders for translation.
        :keyword str suffix: A case-sensitive suffix string to filter documents in the source path for
            translation. This is most often use for file extensions.
        :keyword storage_type: Storage type of the input documents source string. Possible values
            include: "Folder", "File".
        :paramtype storage_type: str or ~azure.ai.translation.document.StorageInputType
        :keyword str category_id: Category / custom model ID for using custom translation.
        :keyword glossaries: Glossaries to apply to translation.
        :paramtype glossaries: list[~azure.ai.translation.document.TranslationGlossary]
        :return: An instance of an AsyncDocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: AsyncDocumentTranslationLROPoller[~azure.core.async_paging.AsyncItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_translation(
        self, inputs: List[DocumentTranslationInput], **kwargs: Any
    ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language. There are two ways to call this method:

        1) To perform translation on documents from a single source container to a single target container, pass the
        `source_url`, `target_url`, and `target_language` parameters including any optional keyword arguments.

        2) To pass multiple inputs for translation (multiple sources or targets), pass the `inputs` parameter
        as a list of :class:`~azure.ai.translation.document.DocumentTranslationInput`.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param inputs: A list of translation inputs. Each individual input has a single
            source URL to documents and can contain multiple TranslationTargets (one for each language)
            for the destination to write translated documents.
        :paramtype inputs: List[~azure.ai.translation.document.DocumentTranslationInput]
        :return: An instance of an AsyncDocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: AsyncDocumentTranslationLROPoller[~azure.core.async_paging.AsyncItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_translation(
        self, *args: Union[str, List[DocumentTranslationInput]], **kwargs: Any
    ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language. There are two ways to call this method:

        1) To perform translation on documents from a single source container to a single target container, pass the
        `source_url`, `target_url`, and `target_language` parameters including any optional keyword arguments.

        2) To pass multiple inputs for translation (multiple sources or targets), pass the `inputs` parameter
        as a list of :class:`~azure.ai.translation.document.DocumentTranslationInput`.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param str source_url: The source URL to the Azure Blob container containing the documents to be translated.
            This can be a SAS URL (see the service documentation for the supported SAS permissions for accessing
            source storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions) or a managed
            identity can be created and used to access documents in your storage account
            (see https://aka.ms/azsdk/documenttranslation/managed-identity).
        :param str target_url: The target URL to the Azure Blob container where the translated documents
            should be written. This can be a SAS URL (see the service documentation for the supported SAS permissions
            for accessing target storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions)
            or a managed identity can be created and used to access documents in your storage account
            (see https://aka.ms/azsdk/documenttranslation/managed-identity).
        :param str target_language: This is the language code you want your documents to be translated to.
            See supported language codes here:
            https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate
        :param inputs: A list of translation inputs. Each individual input has a single
            source URL to documents and can contain multiple TranslationTargets (one for each language)
            for the destination to write translated documents.
        :type inputs: List[~azure.ai.translation.document.DocumentTranslationInput]
        :keyword str source_language: Language code for the source documents.
            If none is specified, the source language will be auto-detected for each document.
        :keyword str prefix: A case-sensitive prefix string to filter documents in the source path for
            translation. For example, when using a Azure storage blob Uri, use the prefix to restrict
            sub folders for translation.
        :keyword str suffix: A case-sensitive suffix string to filter documents in the source path for
            translation. This is most often use for file extensions.
        :keyword storage_type: Storage type of the input documents source string. Possible values
            include: "Folder", "File".
        :paramtype storage_type: str or ~azure.ai.translation.document.StorageInputType
        :keyword str category_id: Category / custom model ID for using custom translation.
        :keyword glossaries: Glossaries to apply to translation.
        :paramtype glossaries: list[~azure.ai.translation.document.TranslationGlossary]
        :return: An instance of an AsyncDocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: AsyncDocumentTranslationLROPoller[~azure.core.async_paging.AsyncItemPaged[DocumentStatus]]
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

        inputs = get_translation_input(args, kwargs, continuation_token)

        def deserialization_callback(
            raw_response, _, headers
        ):  # pylint: disable=unused-argument
            translation_status = json.loads(raw_response.http_response.text())
            return self.list_document_statuses(translation_status["id"])

        polling_interval = kwargs.pop(
            "polling_interval",
            self._client._config.polling_interval,  # pylint: disable=protected-access
        )

        pipeline_response = None
        if continuation_token:
            pipeline_response = await self._client.document_translation.get_translation_status(
                continuation_token,
                cls=lambda pipeline_response, _, response_headers: pipeline_response,
            )

        callback = kwargs.pop("cls", deserialization_callback)
        return cast(AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]],
            await self._client.document_translation.begin_start_translation(
                inputs=inputs if not continuation_token else None,
                polling=AsyncDocumentTranslationLROPollingMethod(
                    timeout=polling_interval,
                    lro_algorithms=[TranslationPolling()],
                    cont_token_response=pipeline_response,
                    **kwargs
                ),
                cls=callback,
                continuation_token=continuation_token,
                **kwargs
            )
        )

    @distributed_trace_async
    async def get_translation_status(self, translation_id: str, **kwargs: Any) -> TranslationStatus:
        """Gets the status of the translation operation.

        Includes the overall status, as well as a summary of
        the documents that are being translated as part of that translation operation.

        :param str translation_id: The translation operation ID.
        :return: A TranslationStatus with information on the status of the translation operation.
        :rtype: ~azure.ai.translation.document.TranslationStatus
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        translation_status = (
            await self._client.document_translation.get_translation_status(
                translation_id, **kwargs
            )
        )
        # pylint: disable=protected-access
        return TranslationStatus._from_generated(translation_status)

    @distributed_trace_async
    async def cancel_translation(self, translation_id: str, **kwargs: Any) -> None:
        """Cancel a currently processing or queued translation operation.

        A translation will not be canceled if it is already completed, failed, or canceling.
        All documents that have completed translation will not be canceled and will be charged.
        If possible, all pending documents will be canceled.

        :param str translation_id: The translation operation ID.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        await self._client.document_translation.cancel_translation(
            translation_id, **kwargs
        )

    @distributed_trace
    def list_translation_statuses(
        self,
        *,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        translation_ids: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        created_after: Optional[Union[str, datetime.datetime]] = None,
        created_before: Optional[Union[str, datetime.datetime]] = None,
        order_by: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[TranslationStatus]:
        """List all the submitted translation operations under the Document Translation resource.

        :keyword int top: The total number of operations to return (across all pages) from all submitted translations.
        :keyword int skip: The number of operations to skip (from beginning of all submitted operations).
            By default, we sort by all submitted operations in descending order by start time.
        :keyword list[str] translation_ids: Translation operations ids to filter by.
        :keyword list[str] statuses: Translation operation statuses to filter by. Options include
            'NotStarted', 'Running', 'Succeeded', 'Failed', 'Canceled', 'Canceling',
            and 'ValidationFailed'.
        :keyword created_after: Get operations created after a certain datetime.
        :paramtype created_after: str or ~datetime.datetime
        :keyword created_before: Get operations created before a certain datetime.
        :paramtype created_before: str or ~datetime.datetime
        :keyword list[str] order_by: The sorting query for the operations returned. Currently only
            'created_on' supported.
            format: ["param1 asc/desc", "param2 asc/desc", ...]
            (ex: 'created_on asc', 'created_on desc').
        :return: A pageable of TranslationStatus.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[TranslationStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_list_translations_async.py
                :start-after: [START list_translations_async]
                :end-before: [END list_translations_async]
                :language: python
                :dedent: 4
                :caption: List all submitted translations under the resource.
        """

        if statuses:
            statuses = [convert_status(status, ll=True) for status in statuses]
        order_by = convert_order_by(order_by)
        created_after = convert_datetime(created_after) if created_after else None
        created_before = convert_datetime(created_before) if created_before else None

        def _convert_from_generated_model(generated_model):
            # pylint: disable=protected-access
            return TranslationStatus._from_generated(generated_model)

        model_conversion_function = kwargs.pop(
            "cls",
            lambda translation_statuses: [
                _convert_from_generated_model(status) for status in translation_statuses
            ],
        )

        return cast(AsyncItemPaged[TranslationStatus],
            self._client.document_translation.get_translations_status(
                cls=model_conversion_function,
                created_date_time_utc_start=created_after,
                created_date_time_utc_end=created_before,
                ids=translation_ids,
                order_by=order_by,
                statuses=statuses,
                top=top,
                skip=skip,
                **kwargs
            )
        )

    @distributed_trace
    def list_document_statuses(
        self,
        translation_id: str,
        *,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        document_ids: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        created_after: Optional[Union[str, datetime.datetime]] = None,
        created_before: Optional[Union[str, datetime.datetime]] = None,
        order_by: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[DocumentStatus]:
        """List all the document statuses for a given translation operation.

        :param str translation_id: ID of translation operation to list documents for.
        :keyword int top: The total number of documents to return (across all pages).
        :keyword int skip: The number of documents to skip (from beginning).
            By default, we sort by all documents in descending order by start time.
        :keyword list[str] document_ids: Document IDs to filter by.
        :keyword list[str] statuses: Document statuses to filter by. Options include
            'NotStarted', 'Running', 'Succeeded', 'Failed', 'Canceled', 'Canceling',
            and 'ValidationFailed'.
        :keyword created_after: Get documents created after a certain datetime.
        :paramtype created_after: str or ~datetime.datetime
        :keyword created_before: Get documents created before a certain datetime.
        :paramtype created_before: str or ~datetime.datetime
        :keyword list[str] order_by: The sorting query for the documents. Currently only
            'created_on' is supported.
            format: ["param1 asc/desc", "param2 asc/desc", ...]
            (ex: 'created_on asc', 'created_on desc').
        :return: A pageable of DocumentStatus.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[DocumentStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_check_document_statuses_async.py
                :start-after: [START list_document_statuses_async]
                :end-before: [END list_document_statuses_async]
                :language: python
                :dedent: 4
                :caption: List all the document statuses as they are being translated.
        """

        if statuses:
            statuses = [convert_status(status, ll=True) for status in statuses]
        order_by = convert_order_by(order_by)
        created_after = (
            convert_datetime(created_after) if created_after else None
        )
        created_before = (
            convert_datetime(created_before) if created_before else None
        )

        def _convert_from_generated_model(generated_model):
            # pylint: disable=protected-access
            return DocumentStatus._from_generated(generated_model)

        model_conversion_function = kwargs.pop(
            "cls",
            lambda doc_statuses: [
                _convert_from_generated_model(doc_status) for doc_status in doc_statuses
            ],
        )

        return cast(AsyncItemPaged[DocumentStatus],
            self._client.document_translation.get_documents_status(
                id=translation_id,
                cls=model_conversion_function,
                created_date_time_utc_start=created_after,
                created_date_time_utc_end=created_before,
                ids=document_ids,
                order_by=order_by,
                statuses=statuses,
                top=top,
                skip=skip,
                **kwargs
            )
        )

    @distributed_trace_async
    async def get_document_status(self, translation_id: str, document_id: str, **kwargs: Any) -> DocumentStatus:
        """Get the status of an individual document within a translation operation.

        :param str translation_id: The translation operation ID.
        :param str document_id: The ID for the document.
        :return: A DocumentStatus with information on the status of the document.
        :rtype: ~azure.ai.translation.document.DocumentStatus
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """
        document_status = await self._client.document_translation.get_document_status(
            translation_id, document_id, **kwargs
        )
        # pylint: disable=protected-access
        return DocumentStatus._from_generated(document_status)

    @distributed_trace_async
    async def get_supported_glossary_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]:
        """Get the list of the glossary formats supported by the Document Translation service.

        :return: A list of supported glossary formats.
        :rtype: List[DocumentTranslationFileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        glossary_formats = (
            await self._client.document_translation.get_supported_glossary_formats(
                **kwargs
            )
        )
        # pylint: disable=protected-access
        return DocumentTranslationFileFormat._from_generated_list(glossary_formats.value)

    @distributed_trace_async
    async def get_supported_document_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]:
        """Get the list of the document formats supported by the Document Translation service.

        :return: A list of supported document formats for translation.
        :rtype: List[DocumentTranslationFileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        document_formats = (
            await self._client.document_translation.get_supported_document_formats(
                **kwargs
            )
        )
        # pylint: disable=protected-access
        return DocumentTranslationFileFormat._from_generated_list(document_formats.value)
