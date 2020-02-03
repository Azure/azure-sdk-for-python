# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, Optional, Union, TYPE_CHECKING  # pylint: disable=unused-import
from ._text_analytics_client import TextAnalyticsClient
from ._request_handlers import _validate_single_input
from ._response_handlers import process_single_error
from ._version import VERSION
from ._models import (
    DetectLanguageInput,
    TextDocumentInput,
    DetectedLanguage,
    DocumentError,
    CategorizedEntity,
    LinkedEntity,
    AnalyzeSentimentResult,
    RecognizeEntitiesResult,
    DetectLanguageResult,
    TextAnalyticsError,
    InnerError,
    ExtractKeyPhrasesResult,
    RecognizeLinkedEntitiesResult,
    RecognizePiiEntitiesResult,
    TextDocumentStatistics,
    LinkedEntityMatch,
    TextDocumentBatchStatistics,
    SentenceSentiment,
    SentimentScorePerLabel,
    PiiEntity
)
from ._credential import TextAnalyticsApiKeyCredential

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

__all__ = [
    'TextAnalyticsClient',
    'DetectLanguageInput',
    'TextDocumentInput',
    'single_detect_language',
    'single_recognize_entities',
    'single_recognize_pii_entities',
    'single_recognize_linked_entities',
    'single_extract_key_phrases',
    'single_analyze_sentiment',
    'DetectedLanguage',
    'RecognizeEntitiesResult',
    'RecognizePiiEntitiesResult',
    'DetectLanguageResult',
    'CategorizedEntity',
    'TextAnalyticsError',
    'InnerError',
    'ExtractKeyPhrasesResult',
    'RecognizeLinkedEntitiesResult',
    'AnalyzeSentimentResult',
    'TextDocumentStatistics',
    'DocumentError',
    'LinkedEntity',
    'LinkedEntityMatch',
    'TextDocumentBatchStatistics',
    'SentenceSentiment',
    'SentimentScorePerLabel',
    'TextAnalyticsApiKeyCredential',
    'PiiEntity'
]

__version__ = VERSION


def single_detect_language(
            endpoint,  # type: str
            credential,  # type: Union[TextAnalyticsApiKeyCredential, TokenCredential]
            input_text,  # type: str
            country_hint="US",  # type: Optional[str]
            **kwargs  # type: Any
):
    # type: (...) -> DetectLanguageResult
    """Detect Language for a single document.

    Returns the detected language and a numeric score between zero and
    one. Scores close to one indicate 100% certainty that the identified
    language is true. See https://aka.ms/talangs for the list of enabled languages.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the an instance of TextAnalyticsApiKeyCredential if using a
        cognitive services/text analytics API key or a token credential
        from azure.identity.
    :type credential: ~azure.ai.textanalytics.TextAnalyticsApiKeyCredential or
        ~azure.core.credentials.TokenCredential
    :param str input_text: The single string to detect language from.
        Limit text length to 5120 chars.
    :param str country_hint: The country hint for the text. Accepts two
        letter country codes specified by ISO 3166-1 alpha-2.
        Defaults to "US". If you don't want to use a country hint,
        pass the empty string "".
    :keyword bool show_stats: If set to true, response will contain
        document level statistics.
    :keyword str model_version: This value indicates which model will
        be used for scoring, e.g. "latest", "2019-10-01". If a model-version
        is not specified, the API will default to the latest, non-preview version.
    :return: An instance of DetectLanguageResult.
    :rtype: ~azure.ai.textanalytics.DetectLanguageResult
    :raises ~azure.core.exceptions.HttpResponseError:

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_single_detect_language.py
            :start-after: [START single_detect_language]
            :end-before: [END single_detect_language]
            :language: python
            :dedent: 8
            :caption: Detecting language in a single string.
    """
    doc = _validate_single_input(input_text, "country_hint", country_hint)
    model_version = kwargs.pop("model_version", None)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = client.detect_language(
            inputs=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # DetectLanguageResult


def single_recognize_entities(
        endpoint,  # type: str
        credential,  # type: Union[TextAnalyticsApiKeyCredential, TokenCredential]
        input_text,  # type: str
        language="en",  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> RecognizeEntitiesResult
    """Named Entity Recognition for a single document.

    Returns a list of general named entities in a given document.
    For a list of supported entity types, check: https://aka.ms/taner
    For a list of enabled languages, check: https://aka.ms/talangs

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the an instance of TextAnalyticsApiKeyCredential if using a
        cognitive services/text analytics API key or a token credential
        from azure.identity.
    :type credential: ~azure.ai.textanalytics.TextAnalyticsApiKeyCredential or
        ~azure.core.credentials.TokenCredential
    :param str input_text: The single string to recognize entities from.
        Limit text length to 5120 chars.
    :param str language: This is the 2 letter ISO 639-1 representation
        of a language. For example, use "en" for English; "es" for Spanish etc. If
        not set, uses "en" for English as default.
    :keyword bool show_stats: If set to true, response will contain
        document level statistics.
    :keyword str model_version: This value indicates which model will
        be used for scoring, e.g. "latest", "2019-10-01". If a model-version
        is not specified, the API will default to the latest, non-preview version.
    :return: An instance of RecognizeEntitiesResult.
    :rtype: ~azure.ai.textanalytics.RecognizeEntitiesResult
    :raises ~azure.core.exceptions.HttpResponseError:

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_single_recognize_entities.py
            :start-after: [START single_recognize_entities]
            :end-before: [END single_recognize_entities]
            :language: python
            :dedent: 8
            :caption: Recognize entities in a single string.
    """
    doc = _validate_single_input(input_text, "language", language)
    model_version = kwargs.pop("model_version", None)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = client.recognize_entities(
            inputs=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # RecognizeEntitiesResult


def single_recognize_pii_entities(
        endpoint,  # type: str
        credential,  # type: Union[TextAnalyticsApiKeyCredential, TokenCredential]
        input_text,  # type: str
        language="en",  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> RecognizePiiEntitiesResult
    """Recognize entities containing personal information for a single document.

    Returns a list of personal information entities ("SSN",
    "Bank Account", etc) in the document.  For the list of supported entity types,
    check https://aka.ms/tanerpii. See https://aka.ms/talangs
    for the list of enabled languages.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the an instance of TextAnalyticsApiKeyCredential if using a
        cognitive services/text analytics API key or a token credential
        from azure.identity.
    :type credential: ~azure.ai.textanalytics.TextAnalyticsApiKeyCredential or
        ~azure.core.credentials.TokenCredential
    :param str input_text: The single string to recognize entities from.
        Limit text length to 5120 chars.
    :param str language: This is the 2 letter ISO 639-1 representation
        of a language. For example, use "en" for English; "es" for Spanish etc. If
        not set, uses "en" for English as default.
    :keyword bool show_stats: If set to true, response will contain
        document level statistics.
    :keyword str model_version: This value indicates which model will
        be used for scoring, e.g. "latest", "2019-10-01". If a model-version
        is not specified, the API will default to the latest, non-preview version.
    :return: An instance of RecognizePiiEntitiesResult.
    :rtype: ~azure.ai.textanalytics.RecognizePiiEntitiesResult
    :raises ~azure.core.exceptions.HttpResponseError:

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_single_recognize_pii_entities.py
            :start-after: [START single_recognize_pii_entities]
            :end-before: [END single_recognize_pii_entities]
            :language: python
            :dedent: 8
            :caption: Recognize personally identifiable information entities in a single string.
    """
    doc = _validate_single_input(input_text, "language", language)
    model_version = kwargs.pop("model_version", None)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = client.recognize_pii_entities(
            inputs=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # RecognizePiiEntitiesResult


def single_recognize_linked_entities(
        endpoint,  # type: str
        credential,  # type: Union[TextAnalyticsApiKeyCredential, TokenCredential]
        input_text,  # type: str
        language="en",  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> RecognizeLinkedEntitiesResult
    """Recognize linked entities from a well-known knowledge base
    for a single document.

    Returns a list of recognized entities with links to a
    well-known knowledge base. See https://aka.ms/talangs for
    supported languages in Text Analytics API.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the an instance of TextAnalyticsApiKeyCredential if using a
        cognitive services/text analytics API key or a token credential
        from azure.identity.
    :type credential: ~azure.ai.textanalytics.TextAnalyticsApiKeyCredential or
        ~azure.core.credentials.TokenCredential
    :param str input_text: The single string to recognize entities from.
        Limit text length to 5120 chars.
    :param str language: This is the 2 letter ISO 639-1 representation
        of a language. For example, use "en" for English; "es" for Spanish etc. If
        not set, uses "en" for English as default.
    :keyword bool show_stats: If set to true, response will contain
        document level statistics.
    :keyword str model_version: This value indicates which model will
        be used for scoring, e.g. "latest", "2019-10-01". If a model-version
        is not specified, the API will default to the latest, non-preview version.
    :return: An instance of RecognizeLinkedEntitiesResult
    :rtype: ~azure.ai.textanalytics.RecognizeLinkedEntitiesResult
    :raises ~azure.core.exceptions.HttpResponseError:

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_single_recognize_linked_entities.py
            :start-after: [START single_recognize_linked_entities]
            :end-before: [END single_recognize_linked_entities]
            :language: python
            :dedent: 8
            :caption: Recognize linked entities in a single string.
    """
    doc = _validate_single_input(input_text, "language", language)
    model_version = kwargs.pop("model_version", None)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = client.recognize_linked_entities(
            inputs=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # RecognizeLinkedEntitiesResult


def single_extract_key_phrases(
        endpoint,  # type: str
        credential,  # type: Union[TextAnalyticsApiKeyCredential, TokenCredential]
        input_text,  # type: str
        language="en",  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> ExtractKeyPhrasesResult
    """Extract Key Phrases for a single document.

    Returns a list of strings denoting the key phrases in the input
    text. See https://aka.ms/talangs for the list of enabled
    languages.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the an instance of TextAnalyticsApiKeyCredential if using a
        cognitive services/text analytics API key or a token credential
        from azure.identity.
    :type credential: ~azure.ai.textanalytics.TextAnalyticsApiKeyCredential or
        ~azure.core.credentials.TokenCredential
    :param str input_text: The single string to extract key phrases from.
        Limit text length to 5120 chars.
    :param str language: This is the 2 letter ISO 639-1 representation
        of a language. For example, use "en" for English; "es" for Spanish etc. If
        not set, uses "en" for English as default.
    :keyword bool show_stats: If set to true, response will contain
        document level statistics.
    :keyword str model_version: This value indicates which model will
        be used for scoring, e.g. "latest", "2019-10-01". If a model-version
        is not specified, the API will default to the latest, non-preview version.
    :return: An instance of ExtractKeyPhrasesResult
    :rtype: ~azure.ai.textanalytics.ExtractKeyPhrasesResult
    :raises ~azure.core.exceptions.HttpResponseError:

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_single_extract_key_phrases.py
            :start-after: [START single_extract_key_phrases]
            :end-before: [END single_extract_key_phrases]
            :language: python
            :dedent: 8
            :caption: Extract key phrases in a single string.
    """
    doc = _validate_single_input(input_text, "language", language)
    model_version = kwargs.pop("model_version", None)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = client.extract_key_phrases(
            inputs=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # ExtractKeyPhrasesResult


def single_analyze_sentiment(
        endpoint,  # type: str
        credential,  # type: Union[TextAnalyticsApiKeyCredential, TokenCredential]
        input_text,  # type: str
        language="en",  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> AnalyzeSentimentResult
    """Analyze sentiment in a single document.

    Returns a sentiment prediction, as well as sentiment scores for
    each sentiment class (Positive, Negative, and Neutral) for the document
    and each sentence within it. See https://aka.ms/talangs for the list
    of enabled languages.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the an instance of TextAnalyticsApiKeyCredential if using a
        cognitive services/text analytics API key or a token credential
        from azure.identity.
    :type credential: ~azure.ai.textanalytics.TextAnalyticsApiKeyCredential or
        ~azure.core.credentials.TokenCredential
    :param str input_text: The single string to analyze sentiment from.
        Limit text length to 5120 chars.
    :param str language: This is the 2 letter ISO 639-1 representation
        of a language. For example, use "en" for English; "es" for Spanish etc. If
        not set, uses "en" for English as default.
    :keyword bool show_stats: If set to true, response will contain
        document level statistics.
    :keyword str model_version: This value indicates which model will
        be used for scoring, e.g. "latest", "2019-10-01". If a model-version
        is not specified, the API will default to the latest, non-preview version.
    :return: An instance of AnalyzeSentimentResult
    :rtype: ~azure.ai.textanalytics.AnalyzeSentimentResult
    :raises ~azure.core.exceptions.HttpResponseError:

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_single_analyze_sentiment.py
            :start-after: [START single_analyze_sentiment]
            :end-before: [END single_analyze_sentiment]
            :language: python
            :dedent: 8
            :caption: Analyze sentiment in a single string.
    """
    doc = _validate_single_input(input_text, "language", language)
    model_version = kwargs.pop("model_version", None)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = client.analyze_sentiment(
            inputs=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # AnalyzeSentimentResult
