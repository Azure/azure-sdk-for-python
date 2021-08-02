# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
from typing import Any, TYPE_CHECKING, List, Union, overload
from azure.core.tracing.decorator import distributed_trace
from ._generated import (
    BatchDocumentTranslationClient as _BatchDocumentTranslationClient,
)
from ._models import (
    TranslationStatus,
    DocumentStatus,
    DocumentTranslationInput,
    FileFormat,
)
from ._user_agent import USER_AGENT
from ._polling import TranslationPolling, DocumentTranslationLROPollingMethod
from ._helpers import (
    get_http_logging_policy,
    convert_datetime,
    convert_order_by,
    get_authentication_policy,
    get_translation_input,
    POLLING_INTERVAL,
)

if TYPE_CHECKING:
    from azure.core.paging import ItemPaged
    from azure.core.credentials import TokenCredential, AzureKeyCredential
    from ._polling import DocumentTranslationLROPoller


class DocumentTranslationClient(object):  # pylint: disable=r0205
    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Union[AzureKeyCredential, TokenCredential], Any) -> None
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

            .. literalinclude:: ../samples/sample_authentication.py
                :start-after: [START create_dt_client_with_key]
                :end-before: [END create_dt_client_with_key]
                :language: python
                :dedent: 4
                :caption: Creating the DocumentTranslationClient with an endpoint and API key.

            .. literalinclude:: ../samples/sample_authentication.py
                :start-after: [START create_dt_client_with_aad]
                :end-before: [END create_dt_client_with_aad]
                :language: python
                :dedent: 4
                :caption: Creating the DocumentTranslationClient with a token credential.
        """
        self._endpoint = endpoint
        self._credential = credential
        self._api_version = kwargs.pop("api_version", None)

        authentication_policy = get_authentication_policy(credential)
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        self._client = _BatchDocumentTranslationClient(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            api_version=self._api_version,
            sdk_moniker=USER_AGENT,
            authentication_policy=authentication_policy,
            http_logging_policy=get_http_logging_policy(),
            polling_interval=polling_interval,
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

    @overload
    def begin_translation(self, source_url, target_url, target_language_code, **kwargs):
        # type: (str, str, str, **Any) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]
        pass

    @overload
    def begin_translation(self, inputs, **kwargs):
        # type: (List[DocumentTranslationInput], **Any) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]
        pass

    def begin_translation(
        self, *args, **kwargs
    ):  # pylint: disable=client-method-missing-type-annotations
        """Begin translating the document(s) in your source container to your target container
        in the given language. To perform a single translation from source to target, pass the `source_url`,
        `target_url`, and `target_language_code` parameters including any optional keyword arguments.
        To pass multiple inputs for translation, pass the `inputs` parameter as a list of
        :class:`~azure.ai.translation.document.DocumentTranslationInput`.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param str source_url: The source SAS URL to the Azure Blob container containing the documents
            to be translated. See the service documentation for the supported SAS permissions for accessing
            source storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions
        :param str target_url: The target SAS URL to the Azure Blob container where the translated documents
            should be written. See the service documentation for the supported SAS permissions for accessing
            target storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions
        :param str target_language_code: This is the language you want your documents to be translated to.
            See supported language codes here:
            https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate
        :param inputs: A list of translation inputs. Each individual input has a single
            source URL to documents and can contain multiple TranslationTargets (one for each language)
            for the destination to write translated documents.
        :type inputs: List[~azure.ai.translation.document.DocumentTranslationInput]
        :keyword str source_language_code: Language code for the source documents.
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
        :return: An instance of a DocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: DocumentTranslationLROPoller[ItemPaged[~azure.ai.translation.document.DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_begin_translation.py
                :start-after: [START begin_translation]
                :end-before: [END begin_translation]
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
            return self.list_all_document_statuses(translation_status["id"])

        polling_interval = kwargs.pop(
            "polling_interval",
            self._client._config.polling_interval,  # pylint: disable=protected-access
        )

        pipeline_response = None
        if continuation_token:
            pipeline_response = self._client.document_translation.get_translation_status(
                continuation_token,
                cls=lambda pipeline_response, _, response_headers: pipeline_response,
            )

        callback = kwargs.pop("cls", deserialization_callback)
        return self._client.document_translation.begin_start_translation(
            inputs=inputs if not continuation_token else None,
            polling=DocumentTranslationLROPollingMethod(
                timeout=polling_interval,
                lro_algorithms=[TranslationPolling()],
                cont_token_response=pipeline_response,
                **kwargs
            ),
            cls=callback,
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace
    def get_translation_status(self, translation_id, **kwargs):
        # type: (str, **Any) -> TranslationStatus
        """Gets the status of the translation operation.

        Includes the overall status, as well as a summary of
        the documents that are being translated as part of that translation operation.

        :param str translation_id: The translation operation ID.
        :return: A TranslationStatus with information on the status of the translation operation.
        :rtype: ~azure.ai.translation.document.TranslationStatus
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        translation_status = self._client.document_translation.get_translation_status(
            translation_id, **kwargs
        )
        return TranslationStatus._from_generated(  # pylint: disable=protected-access
            translation_status
        )

    @distributed_trace
    def cancel_translation(self, translation_id, **kwargs):
        # type: (str, **Any) -> None
        """Cancel a currently processing or queued translation operation.

        A translation will not be cancelled if it is already completed, failed, or cancelling.
        All documents that have completed translation will not be cancelled and will be charged.
        If possible, all pending documents will be cancelled.

        :param str translation_id: The translation operation ID.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        self._client.document_translation.cancel_translation(translation_id, **kwargs)

    @distributed_trace
    def list_all_translation_statuses(self, **kwargs):
        # type: (**Any) -> ItemPaged[TranslationStatus]
        """List all the submitted translation operations under the Document Translation resource.

        :keyword int top: the total number of operations to return (across all pages) from all submitted translations.
        :keyword int skip: the number of operations to skip (from beginning of all submitted operations).
            By default, we sort by all submitted operations descendingly by start time.
        :keyword int results_per_page: is the number of operations returned per page.
        :keyword list[str] translation_ids: translation operations ids to filter by.
        :keyword list[str] statuses: translation operation statuses to filter by. Options include
            'NotStarted', 'Running', 'Succeeded', 'Failed', 'Cancelled', 'Cancelling',
            and 'ValidationFailed'.
        :keyword created_after: get operations created after certain datetime.
        :paramtype created_after: Union[str, datetime.datetime]
        :keyword created_before: get operations created before certain datetime.
        :paramtype created_before: Union[str, datetime.datetime]
        :keyword list[str] order_by: the sorting query for the operations returned. Currently only
            'created_on' supported.
            format: ["param1 asc/desc", "param2 asc/desc", ...]
            (ex: 'created_on asc', 'created_on desc').
        :return: A pageable of TranslationStatus.
        :rtype: ~azure.core.paging.ItemPaged[TranslationStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_list_all_translations.py
                :start-after: [START list_all_translations]
                :end-before: [END list_all_translations]
                :language: python
                :dedent: 4
                :caption: List all submitted translations under the resource.
        """

        order_by = convert_order_by(kwargs.pop("order_by", None))
        created_after = kwargs.pop("created_after", None)
        created_before = kwargs.pop("created_before", None)
        created_after = convert_datetime(created_after) if created_after else None
        created_before = convert_datetime(created_before) if created_before else None
        results_per_page = kwargs.pop("results_per_page", None)
        translation_ids = kwargs.pop("translation_ids", None)

        def _convert_from_generated_model(
            generated_model,
        ):  # pylint: disable=protected-access
            return TranslationStatus._from_generated(
                generated_model
            )  # pylint: disable=protected-access

        model_conversion_function = kwargs.pop(
            "cls",
            lambda translation_statuses: [
                _convert_from_generated_model(status) for status in translation_statuses
            ],
        )

        return self._client.document_translation.get_translations_status(
            cls=model_conversion_function,
            maxpagesize=results_per_page,
            created_date_time_utc_start=created_after,
            created_date_time_utc_end=created_before,
            ids=translation_ids,
            order_by=order_by,
            **kwargs
        )

    @distributed_trace
    def list_all_document_statuses(self, translation_id, **kwargs):
        # type: (str, **Any) -> ItemPaged[DocumentStatus]
        """List all the document statuses for a given translation operation.

        :param str translation_id: ID of translation operation to list documents for.
        :keyword int top: the total number of documents to return (across all pages).
        :keyword int skip: the number of documents to skip (from beginning).
            By default, we sort by all documents descendingly by start time.
        :keyword int results_per_page: is the number of documents returned per page.
        :keyword list[str] document_ids: document IDs to filter by.
        :keyword list[str] statuses: document statuses to filter by. Options include
            'NotStarted', 'Running', 'Succeeded', 'Failed', 'Cancelled', 'Cancelling',
            and 'ValidationFailed'.
        :keyword created_after: get document created after certain datetime.
        :paramtype created_after: Union[str, datetime.datetime]
        :keyword created_before: get document created before certain datetime.
        :paramtype created_before: Union[str, datetime.datetime]
        :keyword list[str] order_by: the sorting query for the documents. Currently only
            'created_on' is supported.
            format: ["param1 asc/desc", "param2 asc/desc", ...]
            (ex: 'created_on asc', 'created_on desc').
        :return: A pageable of DocumentStatus.
        :rtype: ~azure.core.paging.ItemPaged[DocumentStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_check_document_statuses.py
                :start-after: [START list_all_document_statuses]
                :end-before: [END list_all_document_statuses]
                :language: python
                :dedent: 4
                :caption: List all the document statuses as they are being translated.
        """

        order_by = convert_order_by(kwargs.pop("order_by", None))
        created_after = kwargs.pop("created_after", None)
        created_before = kwargs.pop("created_before", None)
        created_after = (
            convert_datetime(created_after) if created_after else None
        )
        created_before = (
            convert_datetime(created_before) if created_before else None
        )
        results_per_page = kwargs.pop("results_per_page", None)
        document_ids = kwargs.pop("document_ids", None)

        def _convert_from_generated_model(generated_model):
            return DocumentStatus._from_generated(  # pylint: disable=protected-access
                generated_model
            )

        model_conversion_function = kwargs.pop(
            "cls",
            lambda doc_statuses: [
                _convert_from_generated_model(doc_status) for doc_status in doc_statuses
            ],
        )

        return self._client.document_translation.get_documents_status(
            id=translation_id,
            cls=model_conversion_function,
            maxpagesize=results_per_page,
            created_date_time_utc_start=created_after,
            created_date_time_utc_end=created_before,
            ids=document_ids,
            order_by=order_by,
            **kwargs
        )

    @distributed_trace
    def get_document_status(self, translation_id, document_id, **kwargs):
        # type: (str, str, **Any) -> DocumentStatus
        """Get the status of an individual document within a translation operation.

        :param str translation_id: The translation operation ID.
        :param str document_id: The ID for the document.
        :return: A DocumentStatus with information on the status of the document.
        :rtype: ~azure.ai.translation.document.DocumentStatus
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        document_status = self._client.document_translation.get_document_status(
            translation_id, document_id, **kwargs
        )
        return DocumentStatus._from_generated(  # pylint: disable=protected-access
            document_status
        )

    @distributed_trace
    def get_supported_glossary_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """Get the list of the glossary formats supported by the Document Translation service.

        :return: A list of supported glossary formats.
        :rtype: List[FileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        glossary_formats = (
            self._client.document_translation.get_supported_glossary_formats(**kwargs)
        )
        return FileFormat._from_generated_list(  # pylint: disable=protected-access
            glossary_formats.value
        )

    @distributed_trace
    def get_supported_document_formats(self, **kwargs):
        # type: (**Any) -> List[FileFormat]
        """Get the list of the document formats supported by the Document Translation service.

        :return: A list of supported document formats for translation.
        :rtype: List[FileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        document_formats = (
            self._client.document_translation.get_supported_document_formats(**kwargs)
        )
        return FileFormat._from_generated_list(  # pylint: disable=protected-access
            document_formats.value
        )
