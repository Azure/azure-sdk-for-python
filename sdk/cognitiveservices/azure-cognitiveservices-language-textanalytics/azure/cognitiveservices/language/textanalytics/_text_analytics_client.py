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
from ._generated.models import ErrorException
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
)

if TYPE_CHECKING:
    from ._models import (
        LanguageInput,
        MultiLanguageInput,
        DocumentLanguage,
        DocumentEntities,
        DocumentLinkedEntities,
        DocumentKeyPhrases,
        DocumentSentiment,
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
        This can be the cognitive services/text analytics subscription key or a token credential
        from azure.identity.
    :type credential: str or token credential

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_ta_client_with_key]
            :end-before: [END create_ta_client_with_key]
            :language: python
            :dedent: 8
            :caption: Creating the TextAnalyticsClient with endpoint and subscription key.

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

    @distributed_trace
    def detect_language(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[LanguageInput], List[Dict[str, str]]]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        country_hint="US",  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentLanguage, DocumentError]]
        """Detect Language for a batch of documents.

        Returns the detected language and a numeric score between zero and
        one. Scores close to one indicate 100% certainty that the identified
        language is true. See https://aka.ms/talangs for the list of enabled languages.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and country_hint on a per-item basis you must
            use as input a list[LanguageInput] or a list of dict representations of
            LanguageInput, like `{"id": "1", "country_hint": "us", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.cognitiveservices.language.textanalytics.LanguageInput]
        :param str model_version: This value indicates which model will
            be used for scoring. If a model-version is not specified, the API
            will default to the latest, non-preview version.
        :param bool show_stats: If set to true, response will contain document
            level statistics.
        :param str country_hint: A country hint for the entire batch. Accepts two
            letter country codes specified by ISO 3166-1 alpha-2. Per-document
            country hints will take precedence over whole batch hints. Defaults to
            "US". If you don't want to use a country hint, pass the empty string "".
        :return: The combined list of DocumentLanguage and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.cognitiveservices.language.textanalytics.DocumentLanguage,
            ~azure.cognitiveservices.language.textanalytics.DocumentError]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_detect_language.py
                :start-after: [START batch_detect_language]
                :end-before: [END batch_detect_language]
                :language: python
                :dedent: 8
                :caption: Detecting language in a batch of documents.
        """
        docs = _validate_batch_input(documents, "country_hint", country_hint)
        try:
            return self._client.languages(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=language_result,
                **kwargs
            )
        except ErrorException as error:
            process_batch_error(error)

    @distributed_trace
    def recognize_entities(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[MultiLanguageInput], List[Dict[str, str]]]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        language="en",  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentEntities, DocumentError]]
        """Named Entity Recognition for a batch of documents.

        Returns a list of general named entities in a given document.
        For a list of supported entity types, check: https://aka.ms/taner
        For a list of enabled languages, check: https://aka.ms/talangs

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[MultiLanguageInput] or a list of dict representations of
            MultiLanguageInput, like `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.cognitiveservices.language.textanalytics.MultiLanguageInput]
        :param str model_version: This value indicates which model will
            be used for scoring. If a model-version is not specified, the API
            will default to the latest, non-preview version.
        :param bool show_stats: If set to true, response will contain document level statistics.
        :param str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language.
        :return: The combined list of DocumentEntities and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.cognitiveservices.language.textanalytics.DocumentEntities,
            ~azure.cognitiveservices.language.textanalytics.DocumentError]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_entities.py
                :start-after: [START batch_recognize_entities]
                :end-before: [END batch_recognize_entities]
                :language: python
                :dedent: 8
                :caption: Recognize entities in a batch of documents.
        """
        docs = _validate_batch_input(documents, "language", language)
        try:
            return self._client.entities_recognition_general(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=entities_result,
                **kwargs
            )
        except ErrorException as error:
            process_batch_error(error)

    @distributed_trace
    def recognize_pii_entities(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[MultiLanguageInput], List[Dict[str, str]]]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        language="en",  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentEntities, DocumentError]]
        """Recognize entities containing personal information for a batch of documents.

        Returns a list of personal information entities ("SSN",
        "Bank Account", etc) in the document.  For the list of supported entity types,
        check https://aka.ms/tanerpii. See https://aka.ms/talangs
        for the list of enabled languages.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[MultiLanguageInput] or a list of dict representations of
            MultiLanguageInput, like `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.cognitiveservices.language.textanalytics.MultiLanguageInput]
        :param str model_version: This value indicates which model will
            be used for scoring. If a model-version is not specified, the API
            will default to the latest, non-preview version.
        :param bool show_stats: If set to true, response will contain document level statistics.
        :param str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language.
        :return: The combined list of DocumentEntities and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.cognitiveservices.language.textanalytics.DocumentEntities,
            ~azure.cognitiveservices.language.textanalytics.DocumentError]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_pii_entities.py
                :start-after: [START batch_recognize_pii_entities]
                :end-before: [END batch_recognize_pii_entities]
                :language: python
                :dedent: 8
                :caption: Recognize personally identifiable information entities in a batch of documents.
        """
        docs = _validate_batch_input(documents, "language", language)
        try:
            return self._client.entities_recognition_pii(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=entities_result,
                **kwargs
            )
        except ErrorException as error:
            process_batch_error(error)

    @distributed_trace
    def recognize_linked_entities(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[MultiLanguageInput], List[Dict[str, str]]]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        language="en",  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentLinkedEntities, DocumentError]]
        """Recognize linked entities from a well-known knowledge base for a batch of documents.

        Returns a list of recognized entities with links to a
        well-known knowledge base. See https://aka.ms/talangs for
        supported languages in Text Analytics API.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[MultiLanguageInput] or a list of dict representations of
            MultiLanguageInput, like `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.cognitiveservices.language.textanalytics.MultiLanguageInput]
        :param str model_version: This value indicates which model will
            be used for scoring. If a model-version is not specified, the API
            will default to the latest, non-preview version.
        :param bool show_stats: If set to true, response will contain document level statistics.
        :param str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language.
        :return: The combined list of DocumentLinkedEntities and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.cognitiveservices.language.textanalytics.DocumentLinkedEntities,
            ~azure.cognitiveservices.language.textanalytics.DocumentError]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_linked_entities.py
                :start-after: [START batch_recognize_linked_entities]
                :end-before: [END batch_recognize_linked_entities]
                :language: python
                :dedent: 8
                :caption: Recognize linked entities in a batch of documents.
        """
        docs = _validate_batch_input(documents, "language", language)
        try:
            return self._client.entities_linking(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=linked_entities_result,
                **kwargs
            )
        except ErrorException as error:
            process_batch_error(error)

    @distributed_trace
    def extract_key_phrases(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[MultiLanguageInput], List[Dict[str, str]]]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        language="en",  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentKeyPhrases, DocumentError]]
        """Extract Key Phrases from a batch of documents.

        Returns a list of strings denoting the key phrases in the input
        text. See https://aka.ms/talangs for the list of enabled
        languages.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[MultiLanguageInput] or a list of dict representations of
            MultiLanguageInput, like `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.cognitiveservices.language.textanalytics.MultiLanguageInput]
        :param str model_version: This value indicates which model will
            be used for scoring. If a model-version is not specified, the API
            will default to the latest, non-preview version.
        :param bool show_stats: If set to true, response will contain document level statistics.
        :param str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language.
        :return: The combined list of DocumentKeyPhrases and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.cognitiveservices.language.textanalytics.DocumentKeyPhrases,
            ~azure.cognitiveservices.language.textanalytics.DocumentError]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_extract_key_phrases.py
                :start-after: [START batch_extract_key_phrases]
                :end-before: [END batch_extract_key_phrases]
                :language: python
                :dedent: 8
                :caption: Extract the key phrases in a batch of documents.
        """
        docs = _validate_batch_input(documents, "language", language)
        try:
            return self._client.key_phrases(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=key_phrases_result,
                **kwargs
            )
        except ErrorException as error:
            process_batch_error(error)

    @distributed_trace
    def analyze_sentiment(  # type: ignore
        self,
        documents,  # type: Union[List[str], List[MultiLanguageInput], List[Dict[str, str]]]
        model_version=None,  # type: Optional[str]
        show_stats=False,  # type:  Optional[bool]
        language="en",  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> List[Union[DocumentSentiment, DocumentError]]
        """Analyze sentiment for a batch of documents.

        Returns a sentiment prediction, as well as sentiment scores for
        each sentiment class (Positive, Negative, and Neutral) for the document
        and each sentence within it. See https://aka.ms/talangs for the list
        of enabled languages.

        :param documents: The set of documents to process as part of this batch.
            If you wish to specify the ID and language on a per-item basis you must
            use as input a list[MultiLanguageInput] or a list of dict representations of
            MultiLanguageInput, like `{"id": "1", "language": "en", "text": "hello world"}`.
        :type documents:
            list[str] or list[~azure.cognitiveservices.language.textanalytics.MultiLanguageInput]
        :param str model_version: This value indicates which model will
            be used for scoring. If a model-version is not specified, the API
            will default to the latest, non-preview version.
        :param bool show_stats: If set to true, response will contain document level statistics.
        :param str language: The 2 letter ISO 639-1 representation of language for the
            entire batch. For example, use "en" for English; "es" for Spanish etc.
            If not set, uses "en" for English as default. Per-document language will
            take precedence over whole batch language.
        :return: The combined list of DocumentSentiment and DocumentErrors in the order
            the original documents were passed in.
        :rtype: list[~azure.cognitiveservices.language.textanalytics.DocumentSentiment,
            ~azure.cognitiveservices.language.textanalytics.DocumentError]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_analyze_sentiment.py
                :start-after: [START batch_analyze_sentiment]
                :end-before: [END batch_analyze_sentiment]
                :language: python
                :dedent: 8
                :caption: Analyze sentiment in a batch of documents.
        """
        docs = _validate_batch_input(documents, "language", language)
        try:
            return self._client.sentiment(
                documents=docs,
                model_version=model_version,
                show_stats=show_stats,
                cls=sentiment_result,
                **kwargs
            )
        except ErrorException as error:
            process_batch_error(error)
