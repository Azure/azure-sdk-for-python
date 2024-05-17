# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# mypy: disable-error-code="attr-defined"

import json
import datetime
from typing import Any, List, Union, overload, Optional, cast, Tuple, TypeVar
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace
from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential

from azure.core.polling import AsyncLROPoller
from azure.core.polling.base_polling import (
    OperationFailed,
    _raise_if_bad_http_status_and_method,
)
from azure.core.polling.async_base_polling import AsyncLROBasePolling

from azure.ai.translation.document import (
    DocumentTranslationInput,
    DocumentTranslationFileFormat,
    TranslationGlossary,
    TranslationStatus,
    DocumentStatus,
    StorageInputType,
)

from ..models._models import (
    TranslationStatus as _TranslationStatus,
    DocumentStatus as _DocumentStatus,
    StartTranslationDetails,
)
from ...document._patch import (
    get_http_logging_policy,
    get_translation_input,
    convert_datetime,
    convert_order_by,
    TranslationPolling,
    convert_status,
)

POLLING_INTERVAL = 1
PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)
_FINISHED = frozenset(["succeeded", "cancelled", "cancelling", "failed"])
_FAILED = frozenset(["validationfailed"])


class AsyncDocumentTranslationLROPoller(AsyncLROPoller[PollingReturnType_co]):
    """An async custom poller implementation for Document Translation. Call `result()` on the poller to return
    a pageable of :class:`~azure.ai.translation.document.DocumentStatus`."""

    @property
    def id(self) -> str:
        """The ID for the translation operation

        :return: The str ID for the translation operation.
        :rtype: str
        """
        if self._polling_method._current_body:  # pylint: disable=protected-access
            return self._polling_method._current_body.id  # pylint: disable=protected-access
        return self._polling_method._get_id_from_headers()  # pylint: disable=protected-access

    @property
    def details(self) -> TranslationStatus:
        """The details for the translation operation

        :return: The details for the translation operation.
        :rtype: ~azure.ai.translation.document.TranslationStatus
        """
        if self._polling_method._current_body:  # pylint: disable=protected-access
            return TranslationStatus._from_generated(  # pylint: disable=protected-access
                self._polling_method._current_body  # pylint: disable=protected-access
            )
        return TranslationStatus(id=self._polling_method._get_id_from_headers())  # pylint: disable=protected-access

    @classmethod
    def from_continuation_token(  # pylint: disable=docstring-missing-return,docstring-missing-param,docstring-missing-rtype
        cls, polling_method, continuation_token, **kwargs
    ):
        """
        :meta private:
        """
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)


class AsyncDocumentTranslationLROPollingMethod(AsyncLROBasePolling):
    """A custom polling method implementation for Document Translation."""

    def __init__(self, *args, **kwargs):
        self._cont_token_response = kwargs.pop("cont_token_response")
        super().__init__(*args, **kwargs)

    @property
    def _current_body(self) -> _TranslationStatus:
        try:
            return _TranslationStatus(self._pipeline_response.http_response.json())
        except json.decoder.JSONDecodeError:
            return _TranslationStatus()  # type: ignore[call-overload]

    def _get_id_from_headers(self) -> str:
        return (
            self._initial_response.http_response.headers["Operation-Location"]
            .split("/batches/")[1]
            .split("?api-version")[0]
        )

    def finished(self) -> bool:
        """Is this polling finished?

        :return: True/False for whether polling is complete.
        :rtype: bool
        """
        return self._finished(self.status())

    @staticmethod
    def _finished(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FINISHED

    @staticmethod
    def _failed(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FAILED

    def get_continuation_token(self) -> str:
        if self._current_body:
            return self._current_body.id
        return self._get_id_from_headers()

    # pylint: disable=arguments-differ
    def from_continuation_token(self, continuation_token: str, **kwargs: Any) -> Tuple:  # type: ignore[override]
        try:
            client = kwargs["client"]
        except KeyError as exc:
            raise ValueError("Need kwarg 'client' to be recreated from continuation_token") from exc

        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError as exc:
            raise ValueError("Need kwarg 'deserialization_callback' to be recreated from continuation_token") from exc

        return client, self._cont_token_response, deserialization_callback

    async def _poll(self) -> None:
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :raises: OperationFailed if operation status 'Failed' or 'Canceled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """
        while not self.finished():
            await self.update_status()
        while not self.finished():
            await self._delay()
            await self.update_status()

        if self._failed(self.status()):
            raise OperationFailed("Operation failed or canceled")

        final_get_url = self._operation.get_final_get_url(self._pipeline_response)
        if final_get_url:
            self._pipeline_response = await self.request_status(final_get_url)
            _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)


class DocumentTranslationClient:
    """DocumentTranslationClient.

    :param endpoint: Supported document Translation endpoint, protocol and hostname, for example:
     https://{TranslatorResourceName}.cognitiveservices.azure.com/translator. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: The API version to use for this operation. Default value is "2024-05-01".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, AsyncTokenCredential],  # pylint: disable=used-before-assignment
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
        except AttributeError as exc:
            raise ValueError("Parameter 'endpoint' must be a string.") from exc
        self._credential = credential
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        from ._client import DocumentTranslationClient as _BatchDocumentTranslationClient

        self._client = _BatchDocumentTranslationClient(
            endpoint=self._endpoint,
            credential=credential,
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
        :type inputs: List[~azure.ai.translation.document.DocumentTranslationInput]
        :return: An instance of a AsyncDocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: AsyncDocumentTranslationLROPoller[~azure.core.async_paging.AsyncItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_translation(  # pylint: disable=docstring-missing-param
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

        def deserialization_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            translation_status = json.loads(raw_response.http_response.text())
            return self.list_document_statuses(translation_status["id"])

        polling_interval = kwargs.pop(
            "polling_interval",
            self._client._config.polling_interval,  # pylint: disable=protected-access
        )

        pipeline_response = None
        if continuation_token:
            pipeline_response = await self._client.get_translation_status(
                continuation_token,
                cls=lambda pipeline_response, _, response_headers: pipeline_response,
            )

        callback = kwargs.pop("cls", deserialization_callback)
        return cast(
            AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]],
            await self._client.begin_start_translation(
                body=StartTranslationDetails(inputs=inputs),
                polling=AsyncDocumentTranslationLROPollingMethod(
                    timeout=polling_interval,
                    lro_algorithms=[TranslationPolling()],
                    cont_token_response=pipeline_response,
                    **kwargs
                ),
                cls=callback,
                continuation_token=continuation_token,
                **kwargs
            ),
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

        translation_status = await self._client.get_translation_status(translation_id, **kwargs)
        return TranslationStatus._from_generated(  # pylint: disable=protected-access
            _TranslationStatus(translation_status)  # type: ignore[call-overload]
        )

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

        await self._client.cancel_translation(translation_id, **kwargs)

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
            return TranslationStatus._from_generated(_TranslationStatus(generated_model))

        model_conversion_function = kwargs.pop(
            "cls",
            lambda translation_statuses: [_convert_from_generated_model(status) for status in translation_statuses],
        )

        return cast(
            AsyncItemPaged[TranslationStatus],
            self._client.get_translations_status(
                cls=model_conversion_function,
                created_date_time_utc_start=created_after,
                created_date_time_utc_end=created_before,
                ids=translation_ids,
                orderby=order_by,
                statuses=statuses,
                top=top,
                skip=skip,
                **kwargs
            ),
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
        created_after = convert_datetime(created_after) if created_after else None
        created_before = convert_datetime(created_before) if created_before else None

        def _convert_from_generated_model(generated_model):
            # pylint: disable=protected-access
            return DocumentStatus._from_generated(_DocumentStatus(generated_model))

        model_conversion_function = kwargs.pop(
            "cls",
            lambda doc_statuses: [_convert_from_generated_model(doc_status) for doc_status in doc_statuses],
        )

        return cast(
            AsyncItemPaged[DocumentStatus],
            self._client.get_documents_status(
                id=translation_id,
                cls=model_conversion_function,
                created_date_time_utc_start=created_after,
                created_date_time_utc_end=created_before,
                ids=document_ids,
                orderby=order_by,
                statuses=statuses,
                top=top,
                skip=skip,
                **kwargs
            ),
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
        document_status = await self._client.get_document_status(translation_id, document_id, **kwargs)
        # pylint: disable=protected-access
        return DocumentStatus._from_generated(_DocumentStatus(document_status))  # type: ignore[call-overload]

    @distributed_trace_async
    async def get_supported_glossary_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]:
        """Get the list of the glossary formats supported by the Document Translation service.

        :return: A list of supported glossary formats.
        :rtype: List[DocumentTranslationFileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        glossary_formats = await self._client.get_supported_formats(type="glossary", **kwargs)
        # pylint: disable=protected-access
        return DocumentTranslationFileFormat._from_generated_list(glossary_formats.value)

    @distributed_trace_async
    async def get_supported_document_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]:
        """Get the list of the document formats supported by the Document Translation service.

        :return: A list of supported document formats for translation.
        :rtype: List[DocumentTranslationFileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        document_formats = await self._client.get_supported_formats(type="document", **kwargs)
        # pylint: disable=protected-access
        return DocumentTranslationFileFormat._from_generated_list(document_formats.value)


__all__: List[str] = [
    "DocumentTranslationClient",
    "AsyncDocumentTranslationLROPoller",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
