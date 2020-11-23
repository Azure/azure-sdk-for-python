# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import (  # pylint: disable=unused-import
    Union,
    Optional,
    Any,
    List,
    Dict,
    TYPE_CHECKING,
)
from functools import partial
from six.moves.urllib.parse import urlparse
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import HttpResponseError
from ._base_client import TextAnalyticsClientBase
from ._request_handlers import _validate_input
from ._response_handlers import (
    process_http_response_error,
    entities_result,
    linked_entities_result,
    key_phrases_result,
    sentiment_result,
    language_result,
    pii_entities_result,
    healthcare_paged_result,
    analyze_paged_result,
    _get_deserialize
)
from ._lro import TextAnalyticsOperationResourcePolling, TextAnalyticsLROPollingMethod

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential, AzureKeyCredential
    from ._models import (
        DetectLanguageInput,
        TextDocumentInput,
        DetectLanguageResult,
        RecognizeEntitiesResult,
        RecognizeLinkedEntitiesResult,
        ExtractKeyPhrasesResult,
        AnalyzeSentimentResult,
        DocumentError,
        RecognizePiiEntitiesResult,
        EntitiesRecognitionTask,
        PiiEntitiesRecognitionTask,
        KeyPhraseExtractionTask,
        AnalyzeHealthcareResultItem,
        TextAnalysisResult
    )


class TextAnalyticsClient(TextAnalyticsClientBase):
    """The Text Analytics API is a suite of text analytics web services built with best-in-class
    Microsoft machine learning algorithms. The API can be used to analyze unstructured text for
    tasks such as sentiment analysis, key phrase extraction, and language detection. No training data
    is needed to use this API - just bring your text data. This API uses advanced natural language
    processing techniques to deliver best in class predictions.

    Further documentation can be found in
    https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview

    :param str endpoint: Supported Cognitive Services or Text Analytics resource
        endpoints (protocol and hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the an instance of AzureKeyCredential if using a
        cognitive services/text analytics API key or a token credential
        from :mod:`azure.identity`.
    :type credential: :class:`~azure.core.credentials.AzureKeyCredential` or
        :class:`~azure.core.credentials.TokenCredential`
    :keyword str default_country_hint: Sets the default country_hint to use for all operations.
        Defaults to "US". If you don't want to use a country hint, pass the string "none".
    :keyword str default_language: Sets the default language to use for all operations.
        Defaults to "en".
    :keyword api_version: The API version of the service to use for requests. It defaults to the
        latest service version. Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str or ~azure.ai.textanalytics.TextAnalyticsApiVersion

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_ta_client_with_key]
            :end-before: [END create_ta_client_with_key]
            :language: python
            :dedent: 8
            :caption: Creating the TextAnalyticsClient with endpoint and API key.

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_ta_client_with_aad]
            :end-before: [END create_ta_client_with_aad]
            :language: python
            :dedent: 8
            :caption: Creating the TextAnalyticsClient with endpoint and token credential from Azure Active Directory.
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Union[AzureKeyCredential, TokenCredential], Any) -> None
        super(TextAnalyticsClient, self).__init__(
            endpoint=endpoint,
            credential=credential,
            **kwargs
        )
        self._default_language = kwargs.pop("default_language", "en")
        self._default_country_hint = kwargs.pop("default_country_hint", "US")
        self._string_code_unit = None if kwargs.get("api_version") == "v3.0" else "UnicodeCodePoint"
        self._deserialize = _get_deserialize()

    @distributed_trace
    def detect_language(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[DetectLanguageInput], List[Dict[str, str]]]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DetectLanguageResult, DocumentError]]
        """Detect language for a batch of documents.

        Returns the detected language and a numeric score between zero and
        one. Scores close to one indicate 100% certainty that the identified
        language is true. See https://aka.ms/talangs for the list of enabled languages.

        See https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview#data-limits
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
        :keyword str model_version: Version of the model used on the service side for scoring,
            e.g. "latest", "2019-10-01". If a model version
            is not specified, the API will default to the latest, non-preview version.
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :return: The combined list of :class:`~azure.ai.textanalytics.DetectLanguageResult` and
            :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents were
            passed in.
        :rtype: list[~azure.ai.textanalytics.DetectLanguageResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_detect_language.py
                :start-after: [START detect_language]
                :end-before: [END detect_language]
                :language: python
                :dedent: 8
                :caption: Detecting language in a batch of documents.
        """
        country_hint_arg = kwargs.pop("country_hint", None)
        country_hint = country_hint_arg if country_hint_arg is not None else self._default_country_hint
        docs = _validate_input(documents, "country_hint", country_hint)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        try:
            return self._client.languages(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=kwargs.pop("cls", language_result),
                **kwargs
            )
        except HttpResponseError as error:
            process_http_response_error(error)

    @distributed_trace
    def recognize_entities(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[RecognizeEntitiesResult, DocumentError]]
        """Recognize entities for a batch of documents.

        Identifies and categorizes entities in your text as people, places,
        organizations, date/time, quantities, percentages, currencies, and more.
        For the list of supported entity types, check: https://aka.ms/taner

        See https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview#data-limits
        for document length limits, maximum batch size, and supported text encoding.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list
            of dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`,
            like `{"id": "1", "language": "en", "text": "hello world"}`.
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
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :return: The combined list of :class:`~azure.ai.textanalytics.RecognizeEntitiesResult` and
            :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents
            were passed in.
        :rtype: list[~azure.ai.textanalytics.RecognizeEntitiesResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_entities.py
                :start-after: [START recognize_entities]
                :end-before: [END recognize_entities]
                :language: python
                :dedent: 8
                :caption: Recognize entities in a batch of documents.
        """
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = _validate_input(documents, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        if self._string_code_unit:
            kwargs.update({"string_index_type": self._string_code_unit})
        try:
            return self._client.entities_recognition_general(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=kwargs.pop("cls", entities_result),
                **kwargs
            )
        except HttpResponseError as error:
            process_http_response_error(error)

    @distributed_trace
    def recognize_pii_entities(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[RecognizePiiEntitiesResult, DocumentError]]
        """Recognize entities containing personal information for a batch of documents.

        Returns a list of personal information entities ("SSN",
        "Bank Account", etc) in the document.  For the list of supported entity types,
        check https://aka.ms/tanerpii

        See https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview#data-limits
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
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :keyword domain_filter: Filters the response entities to ones only included in the specified domain.
            I.e., if set to 'PHI', will only return entities in the Protected Healthcare Information domain.
            See https://aka.ms/tanerpii for more information.
        :paramtype domain_filter: str or ~azure.ai.textanalytics.PiiEntityDomainType
        :return: The combined list of :class:`~azure.ai.textanalytics.RecognizePiiEntitiesResult`
            and :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents
            were passed in.
        :rtype: list[~azure.ai.textanalytics.RecognizePiiEntitiesResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_pii_entities.py
                :start-after: [START recognize_pii_entities]
                :end-before: [END recognize_pii_entities]
                :language: python
                :dedent: 8
                :caption: Recognize personally identifiable information entities in a batch of documents.
        """
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = _validate_input(documents, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        domain_filter = kwargs.pop("domain_filter", None)
        if self._string_code_unit:
            kwargs.update({"string_index_type": self._string_code_unit})
        try:
            return self._client.entities_recognition_pii(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                domain=domain_filter,
                cls=kwargs.pop("cls", pii_entities_result),
                **kwargs
            )
        except ValueError as error:
            if "API version v3.0 does not have operation 'entities_recognition_pii'" in str(error):
                raise ValueError(
                    "'recognize_pii_entities' endpoint is only available for API version v3.1-preview and up"
                )
            raise error
        except HttpResponseError as error:
            process_http_response_error(error)

    @distributed_trace
    def recognize_linked_entities(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[RecognizeLinkedEntitiesResult, DocumentError]]
        """Recognize linked entities from a well-known knowledge base for a batch of documents.

        Identifies and disambiguates the identity of each entity found in text (for example,
        determining whether an occurrence of the word Mars refers to the planet, or to the
        Roman god of war). Recognized entities are associated with URLs to a well-known
        knowledge base, like Wikipedia.

        See https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview#data-limits
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
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :return: The combined list of :class:`~azure.ai.textanalytics.RecognizeLinkedEntitiesResult`
            and :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents
            were passed in.
        :rtype: list[~azure.ai.textanalytics.RecognizeLinkedEntitiesResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_linked_entities.py
                :start-after: [START recognize_linked_entities]
                :end-before: [END recognize_linked_entities]
                :language: python
                :dedent: 8
                :caption: Recognize linked entities in a batch of documents.
        """
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = _validate_input(documents, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        if self._string_code_unit:
            kwargs.update({"string_index_type": self._string_code_unit})
        try:
            return self._client.entities_linking(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=kwargs.pop("cls", linked_entities_result),
                **kwargs
            )
        except HttpResponseError as error:
            process_http_response_error(error)

    def _healthcare_result_callback(self, doc_id_order, raw_response, _, headers, show_stats=False):
        healthcare_result = self._deserialize(
            self._client.models(api_version="v3.1-preview.3").HealthcareJobState,
            raw_response
        )
        return healthcare_paged_result(
            doc_id_order,
            self._client.health_status,
            raw_response,
            healthcare_result,
            headers,
            show_stats=show_stats
        )

    @distributed_trace
    def begin_analyze_healthcare(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]]
        **kwargs  # type: Any
    ):  # type: (...) -> LROPoller[ItemPaged[AnalyzeHealthcareResultItem]]
        """Analyze healthcare entities and identify relationships between these entities in a batch of documents.

        Entities are associated with references that can be found in existing knowledge bases,
        such as UMLS, CHV, MSH, etc.

        Relations are comprised of a pair of entities and a directional relationship.

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
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.textanalytics.AnalyzeHealthcareResultItem`].
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError or NotImplementedError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_analyze_healthcare.py
                :start-after: [START analyze_healthcare]
                :end-before: [END analyze_healthcare]
                :language: python
                :dedent: 8
                :caption: Recognize healthcare entities in a batch of documents.
        """
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = _validate_input(documents, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        polling_interval = kwargs.pop("polling_interval", 5)
        continuation_token = kwargs.pop("continuation_token", None)

        doc_id_order = [doc.get("id") for doc in docs]

        try:
            return self._client.begin_health(
                docs,
                model_version=model_version,
                string_index_type=self._string_code_unit,
                cls=kwargs.pop("cls", partial(self._healthcare_result_callback, doc_id_order, show_stats=show_stats)),
                polling=TextAnalyticsLROPollingMethod(
                    timeout=polling_interval,
                    lro_algorithms=[
                        TextAnalyticsOperationResourcePolling(show_stats=show_stats)
                    ],
                    **kwargs),
                continuation_token=continuation_token,
                **kwargs
            )

        except ValueError as error:
            if "API version v3.0 does not have operation 'begin_health'" in str(error):
                raise ValueError(
                    "'begin_analyze_healthcare' endpoint is only available for API version v3.1-preview.3"
                )
            raise error

        except HttpResponseError as error:
            process_http_response_error(error)

    def begin_cancel_analyze_healthcare(  # type: ignore
        self,
        poller,  # type: LROPoller[ItemPaged[AnalyzeHealthcareResultItem]]
        **kwargs
    ):
        # type: (...) -> LROPoller[None]
        """Cancel an existing health operation.

        :param poller: The LRO poller object associated with the health operation.
        :return: An instance of an LROPoller that returns None.
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError or NotImplementedError:
        """
        polling_interval = kwargs.pop("polling_interval", 5)
        initial_response = getattr(poller._polling_method, "_initial_response") # pylint: disable=protected-access
        operation_location = initial_response.http_response.headers["Operation-Location"]

        job_id = urlparse(operation_location).path.split("/")[-1]

        try:
            return self._client.begin_cancel_health_job(
                job_id,
                polling=TextAnalyticsLROPollingMethod(timeout=polling_interval)
            )

        except HttpResponseError as error:
            process_http_response_error(error)

    @distributed_trace
    def extract_key_phrases(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[ExtractKeyPhrasesResult, DocumentError]]
        """Extract key phrases from a batch of documents.

        Returns a list of strings denoting the key phrases in the input
        text. For example, for the input text "The food was delicious and there
        were wonderful staff", the API returns the main talking points: "food"
        and "wonderful staff"

        See https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview#data-limits
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
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        :return: The combined list of :class:`~azure.ai.textanalytics.ExtractKeyPhrasesResult` and
            :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents were
            passed in.
        :rtype: list[~azure.ai.textanalytics.ExtractKeyPhrasesResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_extract_key_phrases.py
                :start-after: [START extract_key_phrases]
                :end-before: [END extract_key_phrases]
                :language: python
                :dedent: 8
                :caption: Extract the key phrases in a batch of documents.
        """
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = _validate_input(documents, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        try:
            return self._client.key_phrases(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=kwargs.pop("cls", key_phrases_result),
                **kwargs
            )
        except HttpResponseError as error:
            process_http_response_error(error)

    @distributed_trace
    def analyze_sentiment(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[AnalyzeSentimentResult, DocumentError]]
        """Analyze sentiment for a batch of documents. Turn on opinion mining with `show_opinion_mining`.

        Returns a sentiment prediction, as well as sentiment scores for
        each sentiment class (Positive, Negative, and Neutral) for the document
        and each sentence within it.

        See https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview#data-limits
        for document length limits, maximum batch size, and supported text encoding.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of  :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or
            list[dict[str, str]]
        :keyword bool show_opinion_mining: Whether to mine the opinions of a sentence and conduct more
            granular analysis around the aspects of a product or service (also known as
            aspect-based sentiment analysis). If set to true, the returned
            :class:`~azure.ai.textanalytics.SentenceSentiment` objects
            will have property `mined_opinions` containing the result of this analysis. Only available for
            API version v3.1-preview and up.
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Text Analytics API.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
        :keyword bool show_stats: If set to true, response will contain document
            level statistics in the `statistics` field of the document-level response.
        .. versionadded:: v3.1-preview
            The *show_opinion_mining* parameter.
        :return: The combined list of :class:`~azure.ai.textanalytics.AnalyzeSentimentResult` and
            :class:`~azure.ai.textanalytics.DocumentError` in the order the original documents were
            passed in.
        :rtype: list[~azure.ai.textanalytics.AnalyzeSentimentResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_analyze_sentiment.py
                :start-after: [START analyze_sentiment]
                :end-before: [END analyze_sentiment]
                :language: python
                :dedent: 8
                :caption: Analyze sentiment in a batch of documents.
        """
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = _validate_input(documents, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        show_opinion_mining = kwargs.pop("show_opinion_mining", None)
        if self._string_code_unit:
            kwargs.update({"string_index_type": self._string_code_unit})

        if show_opinion_mining is not None:
            kwargs.update({"opinion_mining": show_opinion_mining})
        try:
            return self._client.sentiment(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=kwargs.pop("cls", sentiment_result),
                **kwargs
            )
        except TypeError as error:
            if "opinion_mining" in str(error):
                raise ValueError(
                    "'show_opinion_mining' is only available for API version v3.1-preview and up"
                )
            raise error
        except HttpResponseError as error:
            process_http_response_error(error)

    def _analyze_result_callback(self, doc_id_order, raw_response, _, headers, show_stats=False):
        analyze_result = self._deserialize(
            self._client.models(api_version="v3.1-preview.3").AnalyzeJobState, # pylint: disable=protected-access
            raw_response
        )
        return analyze_paged_result(
            doc_id_order,
            self._client.analyze_status,
            raw_response,
            analyze_result,
            headers,
            show_stats=show_stats
        )

    @distributed_trace
    def begin_analyze(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]]
        entities_recognition_tasks=None,  # type: List[EntitiesRecognitionTask]
        pii_entities_recognition_tasks=None,  # type: List[PiiEntitiesRecognitionTask]
        key_phrase_extraction_tasks=None,  # type: List[KeyPhraseExtractionTask]
        **kwargs  # type: Any
    ):  # type: (...) -> LROPoller[ItemPaged[TextAnalysisResult]]
        """Start a long-running operation to perform a variety of text analysis tasks over a batch of documents.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[:class:`~azure.ai.textanalytics.TextDocumentInput`] or a list of
            dict representations of :class:`~azure.ai.textanalytics.TextDocumentInput`, like
            `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput] or
            list[dict[str, str]]
        :param tasks: A list of tasks to include in the analysis.  Each task object encapsulates the parameters
            used for the particular task type.
        :type tasks: list[Union[~azure.ai.textanalytics.EntitiesRecognitionTask,
            ~azure.ai.textanalytics.PiiEntitiesRecognitionTask, ~azure.ai.textanalytics.EntityLinkingTask,
            ~azure.ai.textanalytics.KeyPhraseExtractionTask, ~azure.ai.textanalytics.SentimentAnalysisTask]]
        :keyword str display_name: An optional display name to set for the requested analysis.
        :keyword str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language. See https://aka.ms/talangs for
            supported languages in Text Analytics API.
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 30 seconds.
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return an instance of TextAnalysisResult.
        :raises ~azure.core.exceptions.HttpResponseError or TypeError or ValueError or NotImplementedError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_analyze.py
                :start-after: [START analyze]
                :end-before: [END analyze]
                :language: python
                :dedent: 8
                :caption: Start a long-running operation to perform a variety of text analysis
                    tasks over a batch of documents.
        """

        display_name = kwargs.pop("display_name", None)
        language_arg = kwargs.pop("language", None)
        language = language_arg if language_arg is not None else self._default_language
        docs = self._client.models(api_version="v3.1-preview.3").MultiLanguageBatchInput(
            documents=_validate_input(documents, "language", language)
        )
        show_stats = kwargs.pop("show_stats", False)
        polling_interval = kwargs.pop("polling_interval", 5)
        continuation_token = kwargs.pop("continuation_token", None)

        doc_id_order = [doc.get("id") for doc in docs.documents]

        try:
            analyze_tasks = self._client.models(api_version='v3.1-preview.3').JobManifestTasks(
                entity_recognition_tasks=[
                    t.to_generated() for t in entities_recognition_tasks
                ] if entities_recognition_tasks else [],
                entity_recognition_pii_tasks=[
                    t.to_generated() for t in pii_entities_recognition_tasks
                ] if pii_entities_recognition_tasks else [],
                key_phrase_extraction_tasks=[
                    t.to_generated() for t in key_phrase_extraction_tasks
                ] if key_phrase_extraction_tasks else []
            )
            analyze_body = self._client.models(api_version='v3.1-preview.3').AnalyzeBatchInput(
                display_name=display_name,
                tasks=analyze_tasks,
                analysis_input=docs
            )
            return self._client.begin_analyze(
                body=analyze_body,
                cls=kwargs.pop("cls", partial(self._analyze_result_callback, doc_id_order, show_stats=show_stats)),
                polling=TextAnalyticsLROPollingMethod(
                    timeout=polling_interval,
                    lro_algorithms=[
                        TextAnalyticsOperationResourcePolling(show_stats=show_stats)
                    ],
                    **kwargs),
                continuation_token=continuation_token,
                **kwargs
            )

        except ValueError as error:
            if "API version v3.0 does not have operation 'begin_analyze'" in str(error):
                raise ValueError(
                    "'begin_analyze' endpoint is only available for API version v3.1-preview.3"
                )
            raise error

        except HttpResponseError as error:
            process_http_response_error(error)
