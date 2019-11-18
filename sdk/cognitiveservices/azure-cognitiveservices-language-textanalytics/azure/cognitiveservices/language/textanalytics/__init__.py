# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, Optional, List  # pylint: disable=unused-import
from ._text_analytics_client import TextAnalyticsClient
from ._response_handlers import _validate_single_input, process_single_error
from ._version import VERSION
from ._models import (
    LanguageInput,
    MultiLanguageInput,
    DetectedLanguage,
    DocumentError,
    Entity,
    LinkedEntity,
    DocumentSentiment,
    DocumentEntities,
    DocumentLanguage,
    Error,
    InnerError,
    DocumentKeyPhrases,
    DocumentLinkedEntities,
    DocumentStatistics,
    Match,
    RequestStatistics,
    SentenceSentiment
)

__all__ = [
    'TextAnalyticsClient',
    'LanguageInput',
    'MultiLanguageInput',
    'single_detect_language',
    'single_recognize_entities',
    'single_recognize_pii_entities',
    'single_recognize_linked_entities',
    'single_extract_key_phrases',
    'single_analyze_sentiment',
    'DetectedLanguage',
    'DocumentEntities',
    'DocumentLanguage',
    'Entity',
    'Error',
    'InnerError',
    'DocumentKeyPhrases',
    'DocumentLinkedEntities',
    'DocumentSentiment',
    'DocumentStatistics',
    'DocumentError',
    'LinkedEntity',
    'Match',
    'RequestStatistics',
    'SentenceSentiment',
]

__version__ = VERSION


def single_detect_language(
            endpoint,  # type: str
            credential,  # type: str
            text,  # type: str
            country_hint=None,  # type: Optional[str]
            model_version=None,  # type: Optional[str]
            **kwargs  # type: Any
):
    # type: (...) -> DetectedLanguage
    """Detect Language for a single document.

    The API returns the detected language and a numeric score between 0 and
    1. Scores close to 1 indicate 100% certainty that the identified
    language is true. See https://aka.ms/talangs for the
    list of enabled languages.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credential: str or token credential
    :param text: The single string to detect language from.
    :type text: str
    :param country_hint: The optional country hint for the text.
    :type country_hint: str
    :param model_version: This value indicates which model will
        be used for scoring. If a model-version is not specified, the API
        will default to the latest, non-preview version.
    :type model_version: str
    :return: An instance of DetectedLanguage.
    :rtype: ~azure.cognitiveservices.language.textanalytics.DetectedLanguage
    :raises: ~azure.core.exceptions.HttpResponseError
    """
    doc = _validate_single_input(text, "country_hint", country_hint)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = client.detect_language(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0].detected_languages[0]  # DetectedLanguage


def single_recognize_entities(
        endpoint,  # type: str
        credential,  # type: str
        text,  # type: str
        language=None,  # type: Optional[str]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> List[Entity]
    """Named Entity Recognition for a single document.

    The API returns a list of general named entities in a given document.
    For the list of supported entity types, check:
    https://aka.ms/taner
    API</a>. For the list of enabled languages, check:
    https://aka.ms/talangs

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credential: str or token credential
    :param text: The single string to recognize entities from.
    :type text: str
    :param language: The optional language hint for the text.
    :type language: str
    :param model_version: This value indicates which model will
        be used for scoring. If a model-version is not specified, the API
        will default to the latest, non-preview version.
    :type model_version: str
    :return: A list of Entity
    :rtype: list[~azure.cognitiveservices.language.textanalytics.Entity]
    :raises: ~azure.core.exceptions.HttpResponseError
    """
    doc = _validate_single_input(text, "language", language)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = client.recognize_entities(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0].entities  # list[Entity]


def single_recognize_pii_entities(
        endpoint,  # type: str
        credential,  # type: str
        text,  # type: str
        language=None,  # type: Optional[str]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> List[Entity]
    """Recognize entities containing personal information for a single document.

    The API returns a list of personal information entities ("SSN",
    "Bank Account", etc) in the document. See https://aka.ms/talangs for the
    list of enabled languages.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credential: str or token credential
    :param text: The single string to recognize entities from.
    :type text: str
    :param language: The optional language hint for the text.
    :type language: str
    :param model_version: This value indicates which model will
    be used for scoring. If a model-version is not specified, the API
    will default to the latest, non-preview version.
    :type model_version: str
    :return: A list of Entity
    :rtype: list[~azure.cognitiveservices.language.textanalytics.Entity]
    :raises: ~azure.core.exceptions.HttpResponseError
    """
    doc = _validate_single_input(text, "language", language)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = client.recognize_pii_entities(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0].entities  # list[Entity]


def single_recognize_linked_entities(
        endpoint,  # type: str
        credential,  # type: str
        text,  # type: str
        language=None,  # type: Optional[str]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> List[LinkedEntity]
    """Recognize linked entities from a well-known knowledge base
    for a single document.

    The API returns a list of recognized entities with links to a
    well-known knowledge base. See https://aka.ms/talangs for the list of enabled languages.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credential: str or token credential
    :param text: The single string to recognize entities from.
    :type text: str
    :param language: The optional language hint for the text.
    :type language: str
    :param model_version: This value indicates which model will
    be used for scoring. If a model-version is not specified, the API
    will default to the latest, non-preview version.
    :type model_version: str
    :return: A list of LinkedEntity
    :rtype: list[~azure.cognitiveservices.language.textanalytics.LinkedEntity]
    :raises: ~azure.core.exceptions.HttpResponseError
    """
    doc = _validate_single_input(text, "language", language)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = client.recognize_linked_entities(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0].entities  # list[LinkedEntity]


def single_extract_key_phrases(
        endpoint,  # type: str
        credential,  # type: str
        text,  # type: str
        language=None,  # type: Optional[str]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> List[str]
    """Extract Key Phrases for a single document.

    The API returns a list of strings denoting the key phrases in the input
    text. See https://aka.ms/talangs for the list of enabled languages.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credential: str or token credential
    :param text: The single string to extract key phrases from.
    :type text: str
    :param language: The optional language hint for the text.
    :type language: str
    :param model_version: This value indicates which model will
    be used for scoring. If a model-version is not specified, the API
    will default to the latest, non-preview version.
    :type model_version: str
    :return: A list of key phrases found in the text.
    :rtype: list[str]
    :raises: ~azure.core.exceptions.HttpResponseError
    """
    doc = _validate_single_input(text, "language", language)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = client.extract_key_phrases(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0].key_phrases  # list[str]


def single_analyze_sentiment(
        endpoint,  # type: str
        credential,  # type: str
        text,  # type: str
        language=None,  # type: Optional[str]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> DocumentSentiment
    """Analyze sentiment in a single document.

    The API returns a sentiment prediction, as well as sentiment scores for
    each sentiment class (Positive, Negative, and Neutral) for the document
    and each sentence within it. See https://aka.ms/talangs for the list
    of enabled languages.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credential: str or token credential
    :param text: The single string to analyze sentiment from.
    :type text: str
    :param language: The optional language hint for the text.
    :type language: str
    :param model_version: This value indicates which model will
    be used for scoring. If a model-version is not specified, the API
    will default to the latest, non-preview version.
    :type model_version: str
    :return: DocumentSentiment
    :rtype: ~azure.cognitiveservices.language.textanalytics.DocumentSentiment
    :raises: ~azure.core.exceptions.HttpResponseError
    """
    doc = _validate_single_input(text, "language", language)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = client.analyze_sentiment(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # DocumentSentiment
