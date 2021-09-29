# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=too-many-lines

import copy
from typing import Union, Any, List, Dict, TYPE_CHECKING
from functools import partial
from azure.core.async_paging import AsyncItemPaged
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from .._version import DEFAULT_API_VERSION
from ._base_client_async import AsyncTextAnalyticsClientBase
from .._base_client import TextAnalyticsApiVersion
from .._request_handlers import (
    _validate_input,
    _determine_action_type,
    _check_string_index_type_arg,
)
from .._response_handlers import (
    process_http_response_error,
    entities_result,
    linked_entities_result,
    key_phrases_result,
    sentiment_result,
    language_result,
    pii_entities_result,
)
from ._response_handlers_async import healthcare_paged_result, analyze_paged_result
from .._models import (
    DetectLanguageInput,
    TextDocumentInput,
    DetectLanguageResult,
    RecognizeEntitiesResult,
    RecognizeLinkedEntitiesResult,
    ExtractKeyPhrasesResult,
    AnalyzeSentimentResult,
    DocumentError,
    RecognizePiiEntitiesResult,
    RecognizeEntitiesAction,
    RecognizePiiEntitiesAction,
    ExtractKeyPhrasesAction,
    _AnalyzeActionsType,
    RecognizeLinkedEntitiesAction,
    AnalyzeSentimentAction,
    AnalyzeHealthcareEntitiesResult,
    ExtractSummaryAction,
    ExtractSummaryResult,
)
from .._lro import TextAnalyticsOperationResourcePolling
from ._lro_async import (
    AsyncAnalyzeHealthcareEntitiesLROPollingMethod,
    AsyncAnalyzeActionsLROPollingMethod,
    AsyncAnalyzeHealthcareEntitiesLROPoller,
    AsyncAnalyzeActionsLROPoller,
)

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class TextAnalyticsClient(AsyncTextAnalyticsClientBase):
    """The Text Analytics API is a suite of text analytics web services built with best-in-class
    Microsoft machine learning algorithms. The API can be used to analyze unstructured text for
    tasks such as sentiment analysis, key phrase extraction, entities recognition,
    and language detection. No training data is needed to use this API - just bring your text data.
    This API uses advanced natural language processing techniques to deliver best in class predictions.

    Further documentation can be found in
    https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview

    :param str endpoint: Supported Cognitive Services or Text Analytics resource
        endpoints (protocol and hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the an instance of AzureKeyCredential if using a
        cognitive services/text analytics API key or a token credential
        from :mod:`azure.identity`.
    :type credential: :class:`~azure.core.credentials.AzureKeyCredential`
        or :class:`~azure.core.credentials_async.AsyncTokenCredential`
    :keyword str default_country_hint: Sets the default country_hint to use for all operations.
        Defaults to "US". If you don't want to use a country hint, pass the string "none".
    :keyword str default_language: Sets the default language to use for all operations.
        Defaults to "en".
    :keyword api_version: The API version of the service to use for requests. It defaults to the
        latest service version. Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str or ~azure.ai.textanalytics.TextAnalyticsApiVersion

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START create_ta_client_with_key_async]
            :end-before: [END create_ta_client_with_key_async]
            :language: python
            :dedent: 4
            :caption: Creating the TextAnalyticsClient with endpoint and API key.

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START create_ta_client_with_aad_async]
            :end-before: [END create_ta_client_with_aad_async]
            :language: python
            :dedent: 4
            :caption: Creating the TextAnalyticsClient with endpoint and token credential from Azure Active Directory.
    """

    def __init__(  # type: ignore
        self,
        endpoint: str,
        credential: Union["AzureKeyCredential", "AsyncTokenCredential"],
        **kwargs: Any,
    ) -> None:
        super(TextAnalyticsClient, self).__init__(
            endpoint=endpoint, credential=credential, **kwargs
        )
        self._api_version = kwargs.get("api_version", DEFAULT_API_VERSION)
        self._default_language = kwargs.pop("default_language", "en")
        self._default_country_hint = kwargs.pop("default_country_hint", "US")
        self._string_code_unit = (
            None if kwargs.get("api_version") == "v3.0" else "UnicodeCodePoint"
        )

    @distributed_trace_async
    async def detect_language(  # type: ignore
        self,
        documents: Union[List[str], List[DetectLanguageInput], List[Dict[str, str]]],
        **kwargs: Any,
    ) -> List[Union[DetectLanguageResult, DocumentError]]:
        """Detect language for a batch of documents.

        Returns the detected language and a numeric score between zero and
        one. Scores close to one indicate 100% certainty that the identified
        language is true. See https://aka.ms/talangs for the list of enabled languages.

        See https://docs.microsoft.com/azure/cognitive-services/text-analytics/concepts/data-limits?tabs=version-3
        for document length limits, maximum batch size, and supported text encoding.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and country_hint on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.DetectLanguageInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.DetectLanguageInput`, like
            `{"id": "1", "country_hint": "us", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.DetectLanguageInput] or
            list[dict[str, str]]
        :keyword str country_hint: Country of origin hint for the entire batch. Accepts two
            letter country codes specified by ISO 3166-1 alpha-2. Per-document
            country hints will take precedence over whole batch hints. Defaults to
            "US". If you don't want to use a country hint, pass the string "none".
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, Text Analytics logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the Text Analytics natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: The combined list of :class:`~azure.ai.textanalytics.DetectLanguageResult`
            and :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents
            were passed in.
        :rtype: list[~azure.ai.textanalytics.DetectLanguageResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *disable_service_logs* keyword argument.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_detect_language_async.py
                :start-after: [START detect_language_async]
                :end-before: [END detect_language_async]
                :language: python
                :dedent: 4
                :caption: Detecting language in a batch of documents.
        """
        country_hint_arg = kwargs.pop("country_hint", None)
        country_hint = (
            country_hint_arg
            if country_hint_arg is not None
            else self._default_country_hint
        )
        docs = _validate_input(documents, "country_hint", country_hint)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        disable_service_logs = kwargs.pop("disable_service_logs", None)
        if disable_service_logs is not None:
            kwargs["logging_opt_out"] = disable_service_logs
        try:
            return await self._client.languages(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=kwargs.pop("cls", language_result),
                **kwargs,
            )
        except HttpResponseError as error:
            process_http_response_error(error)

    @distributed_trace_async
    async def recognize_entities(  # type: ignore
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        **kwargs: Any,
    ) -> List[Union[RecognizeEntitiesResult, DocumentError]]:
        """Recognize entities for a batch of documents.

        Identifies and categorizes entities in your text as people, places,
        organizations, date/time, quantities, percentages, currencies, and more.
        For the list of supported entity types, check: https://aka.ms/taner

        See https://docs.microsoft.com/azure/cognitive-services/text-analytics/concepts/data-limits?tabs=version-3
        for document length limits, maximum batch size, and supported text encoding.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or
            list[dict[str, str]]
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Text Analytics API.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword str string_index_type: Specifies the method used to interpret string offsets.
            `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
            you can also pass in `Utf16CodePoint` or TextElement_v8`. For additional information
            see https://aka.ms/text-analytics-offsets
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, Text Analytics logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the Text Analytics natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: The combined list of :class:`~azure.ai.textanalytics.RecognizeEntitiesResult` and
            :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents were
            passed in.
        :rtype: list[~azure.ai.textanalytics.RecognizeEntitiesResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *disable_service_logs* and *string_index_type* keyword arguments.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_recognize_entities_async.py
                :start-after: [START recognize_entities_async]
                :end-before: [END recognize_entities_async]
                :language: python
                :dedent: 4
                :caption: Recognize entities in a batch of documents.
        """
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = _validate_input(documents, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        disable_service_logs = kwargs.pop("disable_service_logs", None)
        if disable_service_logs is not None:
            kwargs["logging_opt_out"] = disable_service_logs

        string_index_type = _check_string_index_type_arg(
            kwargs.pop("string_index_type", None),
            self._api_version,
            string_index_type_default=self._string_code_unit,
        )
        if string_index_type:
            kwargs.update({"string_index_type": string_index_type})

        try:
            return await self._client.entities_recognition_general(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=kwargs.pop("cls", entities_result),
                **kwargs,
            )
        except HttpResponseError as error:
            process_http_response_error(error)

    @distributed_trace_async
    async def recognize_pii_entities(  # type: ignore
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        **kwargs: Any,
    ) -> List[Union[RecognizePiiEntitiesResult, DocumentError]]:
        """Recognize entities containing personal information for a batch of documents.

        Returns a list of personal information entities ("SSN",
        "Bank Account", etc) in the document.  For the list of supported entity types,
        check https://aka.ms/tanerpii

        See https://docs.microsoft.com/azure/cognitive-services/text-analytics/concepts/data-limits?tabs=version-3
        for document length limits, maximum batch size, and supported text encoding.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or
            list[dict[str, str]]
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Text Analytics API.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword domain_filter: Filters the response entities to ones only included in the specified domain.
            I.e., if set to 'phi', will only return entities in the Protected Healthcare Information domain.
            See https://aka.ms/tanerpii for more information.
        :paramtype domain_filter: str or ~azure.ai.textanalytics.PiiEntityDomain
        :keyword categories_filter: Instead of filtering over all PII entity categories, you can pass in a list of
            the specific PII entity categories you want to filter out. For example, if you only want to filter out
            U.S. social security numbers in a document, you can pass in
            `[PiiEntityCategory.US_SOCIAL_SECURITY_NUMBER]` for this kwarg.
        :paramtype categories_filter: list[str] or list[~azure.ai.textanalytics.PiiEntityCategory]
        :keyword str string_index_type: Specifies the method used to interpret string offsets.
            `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
            you can also pass in `Utf16CodePoint` or `TextElement_v8`. For additional information
            see https://aka.ms/text-analytics-offsets
        :keyword bool disable_service_logs: Defaults to true, meaning that Text Analytics will not log your
            input text on the service side for troubleshooting. If set to False, Text Analytics logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the Text Analytics natural language processing functions. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: The combined list of :class:`~azure.ai.textanalytics.RecognizePiiEntitiesResult`
            and :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents
            were passed in.
        :rtype: list[~azure.ai.textanalytics.RecognizePiiEntitiesResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *recognize_pii_entities* client method.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_pii_entities.py
                :start-after: [START recognize_pii_entities]
                :end-before: [END recognize_pii_entities]
                :language: python
                :dedent: 4
                :caption: Recognize personally identifiable information entities in a batch of documents.
        """
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = _validate_input(documents, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        domain_filter = kwargs.pop("domain_filter", None)
        categories_filter = kwargs.pop("categories_filter", None)

        string_index_type = _check_string_index_type_arg(
            kwargs.pop("string_index_type", None),
            self._api_version,
            string_index_type_default=self._string_code_unit,
        )
        if string_index_type:
            kwargs.update({"string_index_type": string_index_type})
        disable_service_logs = kwargs.pop("disable_service_logs", None)
        if disable_service_logs is not None:
            kwargs["logging_opt_out"] = disable_service_logs

        try:
            return await self._client.entities_recognition_pii(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                domain=domain_filter,
                pii_categories=categories_filter,
                cls=kwargs.pop("cls", pii_entities_result),
                **kwargs,
            )
        except ValueError as error:
            if (
                "API version v3.0 does not have operation 'entities_recognition_pii'"
                in str(error)
            ):
                raise ValueError(
                    "'recognize_pii_entities' endpoint is only available for API version V3_1 and up"
                )
            raise error
        except HttpResponseError as error:
            process_http_response_error(error)

    @distributed_trace_async
    async def recognize_linked_entities(  # type: ignore
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        **kwargs: Any,
    ) -> List[Union[RecognizeLinkedEntitiesResult, DocumentError]]:
        """Recognize linked entities from a well-known knowledge base for a batch of documents.

        Identifies and disambiguates the identity of each entity found in text (for example,
        determining whether an occurrence of the word Mars refers to the planet, or to the
        Roman god of war). Recognized entities are associated with URLs to a well-known
        knowledge base, like Wikipedia.

        See https://docs.microsoft.com/azure/cognitive-services/text-analytics/concepts/data-limits?tabs=version-3
        for document length limits, maximum batch size, and supported text encoding.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or
            list[dict[str, str]]
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Text Analytics API.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword str string_index_type: Specifies the method used to interpret string offsets.
            `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
            you can also pass in `Utf16CodePoint` or `TextElement_v8`. For additional information
            see https://aka.ms/text-analytics-offsets
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, Text Analytics logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the Text Analytics natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: The combined list of :class:`~azure.ai.textanalytics.RecognizeLinkedEntitiesResult`
            and :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents
            were passed in.
        :rtype: list[~azure.ai.textanalytics.RecognizeLinkedEntitiesResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *disable_service_logs* and *string_index_type* keyword arguments.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_recognize_linked_entities_async.py
                :start-after: [START recognize_linked_entities_async]
                :end-before: [END recognize_linked_entities_async]
                :language: python
                :dedent: 4
                :caption: Recognize linked entities in a batch of documents.
        """
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = _validate_input(documents, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        disable_service_logs = kwargs.pop("disable_service_logs", None)
        if disable_service_logs is not None:
            kwargs["logging_opt_out"] = disable_service_logs

        string_index_type = _check_string_index_type_arg(
            kwargs.pop("string_index_type", None),
            self._api_version,
            string_index_type_default=self._string_code_unit,
        )
        if string_index_type:
            kwargs.update({"string_index_type": string_index_type})

        try:
            return await self._client.entities_linking(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=kwargs.pop("cls", linked_entities_result),
                **kwargs,
            )
        except HttpResponseError as error:
            process_http_response_error(error)

    @distributed_trace_async
    async def extract_key_phrases(  # type: ignore
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        **kwargs: Any,
    ) -> List[Union[ExtractKeyPhrasesResult, DocumentError]]:
        """Extract key phrases from a batch of documents.

        Returns a list of strings denoting the key phrases in the input
        text. For example, for the input text "The food was delicious and there
        were wonderful staff", the API returns the main talking points: "food"
        and "wonderful staff"

        See https://docs.microsoft.com/azure/cognitive-services/text-analytics/concepts/data-limits?tabs=version-3
        for document length limits, maximum batch size, and supported text encoding.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or
            list[dict[str, str]]
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Text Analytics API.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, Text Analytics logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the Text Analytics natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: The combined list of :class:`~azure.ai.textanalytics.ExtractKeyPhrasesResult` and
            :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents were
            passed in.
        :rtype: list[~azure.ai.textanalytics.ExtractKeyPhrasesResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *disable_service_logs* keyword argument.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_extract_key_phrases_async.py
                :start-after: [START extract_key_phrases_async]
                :end-before: [END extract_key_phrases_async]
                :language: python
                :dedent: 4
                :caption: Extract the key phrases in a batch of documents.
        """
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = _validate_input(documents, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        disable_service_logs = kwargs.pop("disable_service_logs", None)
        if disable_service_logs is not None:
            kwargs["logging_opt_out"] = disable_service_logs
        try:
            return await self._client.key_phrases(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=kwargs.pop("cls", key_phrases_result),
                **kwargs,
            )
        except HttpResponseError as error:
            process_http_response_error(error)

    @distributed_trace_async
    async def analyze_sentiment(  # type: ignore
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        **kwargs: Any,
    ) -> List[Union[AnalyzeSentimentResult, DocumentError]]:
        """Analyze sentiment for a batch of documents. Turn on opinion mining with `show_opinion_mining`.

        Returns a sentiment prediction, as well as sentiment scores for
        each sentiment class (Positive, Negative, and Neutral) for the document
        and each sentence within it.

        See https://docs.microsoft.com/azure/cognitive-services/text-analytics/concepts/data-limits?tabs=version-3
        for document length limits, maximum batch size, and supported text encoding.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or
            list[dict[str, str]]
        :keyword bool show_opinion_mining: Whether to mine the opinions of a sentence and conduct more
            granular analysis around the aspects of a product or service (also known as
            aspect-based sentiment analysis). If set to true, the returned
            :class:`~azure.ai.textanalytics.SentenceSentiment` objects
            will have property `mined_opinions` containing the result of this analysis. Only available for
            API version v3.1 and up.
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Text Analytics API.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword str string_index_type: Specifies the method used to interpret string offsets.
            `UnicodeCodePoint`, the Python encoding, is the default. To override the Python default,
            you can also pass in `Utf16CodePoint` or `TextElement_v8`. For additional information
            see https://aka.ms/text-analytics-offsets
        :keyword bool disable_service_logs: If set to true, you opt-out of having your text input
            logged on the service side for troubleshooting. By default, Text Analytics logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the Text Analytics natural language processing functions. Setting this parameter to true,
            disables input logging and may limit our ability to remediate issues that occur. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: The combined list of :class:`~azure.ai.textanalytics.AnalyzeSentimentResult` and
            :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents were
            passed in.
        :rtype: list[~azure.ai.textanalytics.AnalyzeSentimentResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. versionadded:: v3.1
            The *show_opinion_mining*, *disable_service_logs*, and *string_index_type* keyword arguments.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_analyze_sentiment_async.py
                :start-after: [START analyze_sentiment_async]
                :end-before: [END analyze_sentiment_async]
                :language: python
                :dedent: 4
                :caption: Analyze sentiment in a batch of documents.
        """
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = _validate_input(documents, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        show_opinion_mining = kwargs.pop("show_opinion_mining", None)
        disable_service_logs = kwargs.pop("disable_service_logs", None)
        if disable_service_logs is not None:
            kwargs["logging_opt_out"] = disable_service_logs

        string_index_type = _check_string_index_type_arg(
            kwargs.pop("string_index_type", None),
            self._api_version,
            string_index_type_default=self._string_code_unit,
        )
        if string_index_type:
            kwargs.update({"string_index_type": string_index_type})

        if show_opinion_mining is not None:
            if (
                self._api_version == TextAnalyticsApiVersion.V3_0
                and show_opinion_mining
            ):
                raise ValueError(
                    "'show_opinion_mining' is only available for API version v3.1 and up"
                )
            kwargs.update({"opinion_mining": show_opinion_mining})

        try:
            return await self._client.sentiment(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=kwargs.pop("cls", sentiment_result),
                **kwargs,
            )
        except HttpResponseError as error:
            process_http_response_error(error)

    def _healthcare_result_callback(
        self, doc_id_order, raw_response, _, headers, show_stats=False
    ):
        healthcare_result = self._client.models(
            api_version="v3.1"
        ).HealthcareJobState.deserialize(raw_response)
        return healthcare_paged_result(
            doc_id_order,
            self._client.health_status,
            raw_response,
            healthcare_result,
            headers,
            show_stats=show_stats,
        )

    @distributed_trace_async
    async def begin_analyze_healthcare_entities(  # type: ignore
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        **kwargs: Any,
    ) -> AsyncAnalyzeHealthcareEntitiesLROPoller[
        AsyncItemPaged[Union[AnalyzeHealthcareEntitiesResult, DocumentError]]
    ]:
        """Analyze healthcare entities and identify relationships between these entities in a batch of documents.

        Entities are associated with references that can be found in existing knowledge bases,
        such as UMLS, CHV, MSH, etc.

        We also extract the relations found between entities, for example in "The subject took 100 mg of ibuprofen",
        we would extract the relationship between the "100 mg" dosage and the "ibuprofen" medication.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or
            list[dict[str, str]]
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
            See here for more info: https://aka.ms/text-analytics-model-versioning
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :keyword str string_index_type: Specifies the method used to interpret string offsets.
            Can be one of 'UnicodeCodePoint' (default), 'Utf16CodePoint', or 'TextElement_v8'.
            For additional information see https://aka.ms/text-analytics-offsets
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword bool disable_service_logs: Defaults to true, meaning that Text Analytics will not log your
            input text on the service side for troubleshooting. If set to False, Text Analytics logs your
            input text for 48 hours, solely to allow for troubleshooting issues in providing you with
            the Text Analytics natural language processing functions. Please see
            Cognitive Services Compliance and Privacy notes at https://aka.ms/cs-compliance for
            additional details, and Microsoft Responsible AI principles at
            https://www.microsoft.com/ai/responsible-ai.
        :return: An instance of an AsyncAnalyzeHealthcareEntitiesLROPoller. Call `result()` on the poller
            object to return a heterogeneous pageable of
            :class:`~azure.ai.textanalytics.AnalyzeHealthcareEntitiesResult` and
            :class:`~azure.ai.textanalytics.DocumentError`.
        :rtype:
            ~azure.ai.textanalytics.aio.AsyncAnalyzeHealthcareEntitiesLROPoller[~azure.core.paging.AsyncItemPaged[
            Union[~azure.ai.textanalytics.AnalyzeHealthcareEntitiesResult, ~azure.ai.textanalytics.DocumentError]]]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError or NotImplementedError:

        .. versionadded:: v3.1
            The *begin_analyze_healthcare_entities* client method.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_analyze_healthcare_entities_async.py
                :start-after: [START analyze_healthcare_entities_async]
                :end-before: [END analyze_healthcare_entities_async]
                :language: python
                :dedent: 4
                :caption: Analyze healthcare entities in a batch of documents.
        """
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = _validate_input(documents, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        polling_interval = kwargs.pop("polling_interval", 5)
        continuation_token = kwargs.pop("continuation_token", None)
        string_index_type = kwargs.pop("string_index_type", self._string_code_unit)
        disable_service_logs = kwargs.pop("disable_service_logs", None)
        doc_id_order = [doc.get("id") for doc in docs]
        my_cls = kwargs.pop(
            "cls",
            partial(
                self._healthcare_result_callback, doc_id_order, show_stats=show_stats
            ),
        )
        polling_kwargs = kwargs
        operation_kwargs = copy.copy(kwargs)
        if disable_service_logs is not None:
            operation_kwargs["logging_opt_out"] = disable_service_logs

        try:
            return await self._client.begin_health(
                docs,
                model_version=model_version,
                string_index_type=string_index_type,
                cls=my_cls,
                polling=AsyncAnalyzeHealthcareEntitiesLROPollingMethod(
                    text_analytics_client=self._client,
                    timeout=polling_interval,
                    lro_algorithms=[
                        TextAnalyticsOperationResourcePolling(show_stats=show_stats)
                    ],
                    **polling_kwargs,
                ),
                continuation_token=continuation_token,
                **operation_kwargs,
            )

        except ValueError as error:
            if "API version v3.0 does not have operation 'begin_health'" in str(error):
                raise ValueError(
                    "'begin_analyze_healthcare_entities' endpoint is only available for API version V3_1 and up"
                )
            raise error

        except HttpResponseError as error:
            process_http_response_error(error)

    def _analyze_result_callback(
        self, doc_id_order, task_order, raw_response, _, headers, show_stats=False
    ):
        analyze_result = self._client.models(
            api_version=self._api_version
        ).AnalyzeJobState.deserialize(raw_response)
        return analyze_paged_result(
            doc_id_order,
            task_order,
            self._client.analyze_status,
            raw_response,
            analyze_result,
            headers,
            show_stats=show_stats,
        )

    @distributed_trace_async
    async def begin_analyze_actions(  # type: ignore
        self,
        documents: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]],
        actions: List[
            Union[
                RecognizeEntitiesAction,
                RecognizeLinkedEntitiesAction,
                RecognizePiiEntitiesAction,
                ExtractKeyPhrasesAction,
                AnalyzeSentimentAction,
                ExtractSummaryAction,
            ]
        ],  # pylint: disable=line-too-long
        **kwargs: Any,
    ) -> AsyncAnalyzeActionsLROPoller[
        AsyncItemPaged[
            List[
                Union[
                    RecognizeEntitiesResult,
                    RecognizeLinkedEntitiesResult,
                    RecognizePiiEntitiesResult,
                    ExtractKeyPhrasesResult,
                    AnalyzeSentimentResult,
                    ExtractSummaryResult,
                    DocumentError,
                ]
            ]
        ]
    ]:  # pylint: disable=line-too-long
        """Start a long-running operation to perform a variety of text analysis actions over a batch of documents.

        We recommend you use this function if you're looking to analyze larger documents, and / or
        combine multiple Text Analytics actions into one call. Otherwise, we recommend you use
        the action specific endpoints, for example :func:`analyze_sentiment`.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or
            list[dict[str, str]]
        :param actions: A heterogeneous list of actions to perform on the input documents.
            Each action object encapsulates the parameters used for the particular action type.
            The action results will be in the same order of the input actions.
            Duplicate actions in list not supported.
        :type actions:
            list[RecognizeEntitiesAction or RecognizePiiEntitiesAction or ExtractKeyPhrasesAction or
            RecognizeLinkedEntitiesAction or AnalyzeSentimentAction, or ExtractSummaryAction]
        :keyword str display_name: An optional display name to set for the requested analysis.
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Text Analytics API.
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :return: An instance of an AsyncAnalyzeActionsLROPoller. Call `result()` on the poller
            object to return a pageable heterogeneous list of lists. This list of lists is first ordered
            by the documents you input, then ordered by the actions you input. For example,
            if you have documents input ["Hello", "world"], and actions
            :class:`~azure.ai.textanalytics.RecognizeEntitiesAction` and
            :class:`~azure.ai.textanalytics.AnalyzeSentimentAction`, when iterating over the list of lists,
            you will first iterate over the action results for the "Hello" document, getting the
            :class:`~azure.ai.textanalytics.RecognizeEntitiesResult` of "Hello",
            then the :class:`~azure.ai.textanalytics.AnalyzeSentimentResult` of "Hello".
            Then, you will get the :class:`~azure.ai.textanalytics.RecognizeEntitiesResult` and
            :class:`~azure.ai.textanalytics.AnalyzeSentimentResult` of "world".
        :rtype:
            ~azure.ai.textanalytics.aio.AsyncAnalyzeActionsLROPoller[~azure.core.async_paging.AsyncItemPaged[
            list[Union[RecognizeEntitiesResult, RecognizeLinkedEntitiesResult, RecognizePiiEntitiesResult,
            ExtractKeyPhrasesResult, AnalyzeSentimentResult, ExtractSummaryResult, DocumentError]]]]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError or NotImplementedError:

        .. versionadded:: v3.1
            The *begin_analyze_actions* client method.
        .. versionadded:: v3.2-preview
            The *ExtractSummaryAction* input option and *ExtractSummaryResult* result object

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_analyze_actions_async.py
                :start-after: [START analyze_async]
                :end-before: [END analyze_async]
                :language: python
                :dedent: 4
                :caption: Start a long-running operation to perform a variety of text analysis actions over
                    a batch of documents.
        """

        display_name = kwargs.pop("display_name", None)
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = self._client.models(
            api_version=self._api_version
        ).MultiLanguageBatchInput(
            documents=_validate_input(documents, "language", language)
        )
        show_stats = kwargs.pop("show_stats", False)
        polling_interval = kwargs.pop("polling_interval", 5)
        continuation_token = kwargs.pop("continuation_token", None)

        doc_id_order = [doc.get("id") for doc in docs.documents]
        task_order = [_determine_action_type(action) for action in actions]
        if len(task_order) != len(set(task_order)):
            raise ValueError("Multiple of the same action is not currently supported.")

        try:
            analyze_tasks = self._client.models(
                api_version=self._api_version
            ).JobManifestTasks(
                entity_recognition_tasks=[
                    t._to_generated(  # pylint: disable=protected-access
                        self._api_version
                    )
                    for t in [
                        a
                        for a in actions
                        if _determine_action_type(a)
                        == _AnalyzeActionsType.RECOGNIZE_ENTITIES
                    ]
                ],
                entity_recognition_pii_tasks=[
                    t._to_generated(  # pylint: disable=protected-access
                        self._api_version
                    )
                    for t in [
                        a
                        for a in actions
                        if _determine_action_type(a)
                        == _AnalyzeActionsType.RECOGNIZE_PII_ENTITIES
                    ]
                ],
                key_phrase_extraction_tasks=[
                    t._to_generated(  # pylint: disable=protected-access
                        self._api_version
                    )
                    for t in [
                        a
                        for a in actions
                        if _determine_action_type(a)
                        == _AnalyzeActionsType.EXTRACT_KEY_PHRASES
                    ]
                ],
                entity_linking_tasks=[
                    t._to_generated(  # pylint: disable=protected-access
                        self._api_version
                    )
                    for t in [
                        a
                        for a in actions
                        if _determine_action_type(a)
                        == _AnalyzeActionsType.RECOGNIZE_LINKED_ENTITIES
                    ]
                ],
                sentiment_analysis_tasks=[
                    t._to_generated(  # pylint: disable=protected-access
                        self._api_version
                    )
                    for t in [
                        a
                        for a in actions
                        if _determine_action_type(a)
                        == _AnalyzeActionsType.ANALYZE_SENTIMENT
                    ]
                ],
                extractive_summarization_tasks=[
                    t._to_generated(  # pylint: disable=protected-access
                        self._api_version
                    )
                    for t in [
                        a
                        for a in actions
                        if _determine_action_type(a)
                        == _AnalyzeActionsType.EXTRACT_SUMMARY
                    ]
                ],
            )
            analyze_body = self._client.models(
                api_version=self._api_version
            ).AnalyzeBatchInput(
                display_name=display_name, tasks=analyze_tasks, analysis_input=docs
            )
            return await self._client.begin_analyze(
                body=analyze_body,
                cls=kwargs.pop(
                    "cls",
                    partial(
                        self._analyze_result_callback,
                        doc_id_order,
                        task_order,
                        show_stats=show_stats,
                    ),
                ),
                polling=AsyncAnalyzeActionsLROPollingMethod(
                    timeout=polling_interval,
                    lro_algorithms=[
                        TextAnalyticsOperationResourcePolling(show_stats=show_stats)
                    ],
                    **kwargs,
                ),
                continuation_token=continuation_token,
                **kwargs,
            )

        except ValueError as error:
            if "API version v3.0 does not have operation 'begin_analyze'" in str(error):
                raise ValueError(
                    "'begin_analyze_actions' endpoint is only available for API version V3_1 and up"
                )
            raise error

        except HttpResponseError as error:
            process_http_response_error(error)
