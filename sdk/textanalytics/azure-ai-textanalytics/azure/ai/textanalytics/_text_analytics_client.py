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
from azure.core.tracing.decorator import distributed_trace
from ._generated.models import TextAnalyticsErrorException
from ._generated._text_analytics_client import TextAnalyticsClient as TextAnalytics
from ._base_client import TextAnalyticsClientBase
from ._request_handlers import _validate_batch_input
from ._response_handlers import (
    process_batch_error,
    entities_result,
    linked_entities_result,
    key_phrases_result,
    sentiment_result,
    language_result,
    pii_entities_result
)

if TYPE_CHECKING:
    from ._models import (
        DetectLanguageInput,
        TextDocumentInput,
        DetectLanguageResult,
        RecognizeEntitiesResult,
        RecognizeLinkedEntitiesResult,
        ExtractKeyPhrasesResult,
        AnalyzeSentimentResult,
        RecognizePiiEntitiesResult,
        DocumentError,
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
        This can be the an instance of TextAnalyticsApiKeyCredential if using a
        cognitive services/text analytics API key or a token credential
        from azure.identity.
    :type credential: ~azure.ai.textanalytics.TextAnalyticsApiKeyCredential or
        ~azure.core.credentials.TokenCredential
    :keyword str default_country_hint: Sets the default country_hint to use for all operations.
        Defaults to "US". If you don't want to use a country hint, pass the empty string "".
    :keyword str default_language: Sets the default language to use for all operations.
        Defaults to "en".

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
        # type: (str, Any, Any) -> None
        super(TextAnalyticsClient, self).__init__(credential=credential, **kwargs)
        self._client = TextAnalytics(
            endpoint=endpoint, credentials=credential, pipeline=self._pipeline
        )
        self._default_language = kwargs.pop("default_language", "en")
        self._default_country_hint = kwargs.pop("default_country_hint", "US")

    @distributed_trace
    def detect_languages(  # type: ignore
        self,
        inputs,  # type: Union[List[str], List[DetectLanguageInput], List[Dict[str, str]]]
        country_hint=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DetectLanguageResult, DocumentError]]
        """Detects Language for a batch of documents.

        Returns the detected language and a numeric score between zero and
        one. Scores close to one indicate 100% certainty that the identified
        language is true. See https://aka.ms/talangs for the list of enabled languages.

        :param inputs: The set of documents to process as part of this batch.
            If you wish to specify the ID and country_hint on a per-item basis you must
            use as input a list[DetectLanguageInput] or a list of dict representations of
            DetectLanguageInput, like `{"id": "1", "country_hint": "us", "text": "hello world"}`.
        :type inputs:
            list[str] or list[~azure.ai.textanalytics.DetectLanguageInput]
        :param str country_hint: A country hint for the entire batch. Accepts two
            letter country codes specified by ISO 3166-1 alpha-2. Per-document
            country hints will take precedence over whole batch hints. Defaults to
            "US". If you don't want to use a country hint, pass the empty string "".
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
        :keyword bool show_stats: If set to true, response will contain document
            level statistics.
        :return: The combined list of DetectLanguageResults and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.ai.textanalytics.DetectLanguageResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_detect_languages.py
                :start-after: [START batch_detect_languages]
                :end-before: [END batch_detect_languages]
                :language: python
                :dedent: 8
                :caption: Detecting language in a batch of documents.
        """
        country_hint = country_hint if country_hint is not None else self._default_country_hint
        docs = _validate_batch_input(inputs, "country_hint", country_hint)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        try:
            return self._client.languages(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=language_result,
                **kwargs
            )
        except TextAnalyticsErrorException as error:
            process_batch_error(error)

    @distributed_trace
    def recognize_entities(  # type: ignore
        self,
        inputs,  # type: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]]
        language=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[RecognizeEntitiesResult, DocumentError]]
        """Named Entity Recognition for a batch of documents.

        Returns a list of general named entities in a given document.
        For a list of supported entity types, check: https://aka.ms/taner
        For a list of enabled languages, check: https://aka.ms/talangs

        :param inputs: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[TextDocumentInput] or a list of dict representations of
            TextDocumentInput, like `{"id": "1", "language": "en", "text": "hello world"}`.
        :type inputs:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput]
        :param str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
        :keyword bool show_stats: If set to true, response will contain document
            level statistics.
        :return: The combined list of RecognizeEntitiesResults and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.ai.textanalytics.RecognizeEntitiesResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_entities.py
                :start-after: [START batch_recognize_entities]
                :end-before: [END batch_recognize_entities]
                :language: python
                :dedent: 8
                :caption: Recognize entities in a batch of documents.
        """
        language = language if language is not None else self._default_language
        docs = _validate_batch_input(inputs, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        try:
            return self._client.entities_recognition_general(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=entities_result,
                **kwargs
            )
        except TextAnalyticsErrorException as error:
            process_batch_error(error)

    @distributed_trace
    def recognize_pii_entities(  # type: ignore
        self,
        inputs,  # type: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]]
        language=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[RecognizePiiEntitiesResult, DocumentError]]
        """Recognize entities containing personal information for a batch of documents.

        Returns a list of personal information entities ("SSN",
        "Bank Account", etc) in the document.  For the list of supported entity types,
        check https://aka.ms/tanerpii. See https://aka.ms/talangs
        for the list of enabled languages.

        :param inputs: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[TextDocumentInput] or a list of dict representations of
            TextDocumentInput, like `{"id": "1", "language": "en", "text": "hello world"}`.
        :type inputs:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput]
        :param str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :return: The combined list of RecognizePiiEntitiesResults and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.ai.textanalytics.RecognizePiiEntitiesResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_pii_entities.py
                :start-after: [START batch_recognize_pii_entities]
                :end-before: [END batch_recognize_pii_entities]
                :language: python
                :dedent: 8
                :caption: Recognize personally identifiable information entities in a batch of documents.
        """
        language = language if language is not None else self._default_language
        docs = _validate_batch_input(inputs, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        try:
            return self._client.entities_recognition_pii(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=pii_entities_result,
                **kwargs
            )
        except TextAnalyticsErrorException as error:
            process_batch_error(error)

    @distributed_trace
    def recognize_linked_entities(  # type: ignore
        self,
        inputs,  # type: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]]
        language=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[RecognizeLinkedEntitiesResult, DocumentError]]
        """Recognize linked entities from a well-known knowledge base for a batch of documents.

        Returns a list of recognized entities with links to a
        well-known knowledge base. See https://aka.ms/talangs for
        supported languages in Text Analytics API.

        :param inputs: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[TextDocumentInput] or a list of dict representations of
            TextDocumentInput, like `{"id": "1", "language": "en", "text": "hello world"}`.
        :type inputs:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput]
        :param str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :return: The combined list of RecognizeLinkedEntitiesResults and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.ai.textanalytics.RecognizeLinkedEntitiesResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_linked_entities.py
                :start-after: [START batch_recognize_linked_entities]
                :end-before: [END batch_recognize_linked_entities]
                :language: python
                :dedent: 8
                :caption: Recognize linked entities in a batch of documents.
        """
        language = language if language is not None else self._default_language
        docs = _validate_batch_input(inputs, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        try:
            return self._client.entities_linking(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=linked_entities_result,
                **kwargs
            )
        except TextAnalyticsErrorException as error:
            process_batch_error(error)

    @distributed_trace
    def extract_key_phrases(  # type: ignore
        self,
        inputs,  # type: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]]
        language=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[ExtractKeyPhrasesResult, DocumentError]]
        """Extract Key Phrases from a batch of documents.

        Returns a list of strings denoting the key phrases in the input
        text. See https://aka.ms/talangs for the list of enabled
        languages.

        :param inputs: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[TextDocumentInput] or a list of dict representations of
            TextDocumentInput, like `{"id": "1", "language": "en", "text": "hello world"}`.
        :type inputs:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput]
        :param str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :return: The combined list of ExtractKeyPhrasesResults and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.ai.textanalytics.ExtractKeyPhrasesResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_extract_key_phrases.py
                :start-after: [START batch_extract_key_phrases]
                :end-before: [END batch_extract_key_phrases]
                :language: python
                :dedent: 8
                :caption: Extract the key phrases in a batch of documents.
        """
        language = language if language is not None else self._default_language
        docs = _validate_batch_input(inputs, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        try:
            return self._client.key_phrases(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=key_phrases_result,
                **kwargs
            )
        except TextAnalyticsErrorException as error:
            process_batch_error(error)

    @distributed_trace
    def analyze_sentiment(  # type: ignore
        self,
        inputs,  # type: Union[List[str], List[TextDocumentInput], List[Dict[str, str]]]
        language=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[AnalyzeSentimentResult, DocumentError]]
        """Analyze sentiment for a batch of documents.

        Returns a sentiment prediction, as well as sentiment scores for
        each sentiment class (Positive, Negative, and Neutral) for the document
        and each sentence within it. See https://aka.ms/talangs for the list
        of enabled languages.

        :param inputs: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[TextDocumentInput] or a list of dict representations of
            TextDocumentInput, like `{"id": "1", "language": "en", "text": "hello world"}`.
        :type inputs:
            list[str] or list[~azure.ai.textanalytics.TextDocumentInput]
        :param str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language.
        :keyword str model_version: This value indicates which model will
            be used for scoring, e.g. "latest", "2019-10-01". If a model-version
            is not specified, the API will default to the latest, non-preview version.
        :keyword bool show_stats: If set to true, response will contain document level statistics.
        :return: The combined list of AnalyzeSentimentResults and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.ai.textanalytics.AnalyzeSentimentResult,
            ~azure.ai.textanalytics.DocumentError]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_analyze_sentiment.py
                :start-after: [START batch_analyze_sentiment]
                :end-before: [END batch_analyze_sentiment]
                :language: python
                :dedent: 8
                :caption: Analyze sentiment in a batch of documents.
        """
        language = language if language is not None else self._default_language
        docs = _validate_batch_input(inputs, "language", language)
        model_version = kwargs.pop("model_version", None)
        show_stats = kwargs.pop("show_stats", False)
        try:
            return self._client.sentiment(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=sentiment_result,
                **kwargs
            )
        except TextAnalyticsErrorException as error:
            process_batch_error(error)
