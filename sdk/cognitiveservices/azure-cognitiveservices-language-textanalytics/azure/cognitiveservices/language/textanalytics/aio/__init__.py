# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, Optional, TYPE_CHECKING  # pylint: disable=unused-import
from .._response_handlers import _validate_single_input, process_single_error
from ._text_analytics_client_async import TextAnalyticsClient

if TYPE_CHECKING:
    from .._models import (
        DocumentLanguage,
        DocumentEntities,
        DocumentLinkedEntities,
        DocumentKeyPhrases,
        DocumentSentiment,
    )

__all__ = [
    'TextAnalyticsClient',
    'single_detect_language',
    'single_recognize_entities',
    'single_recognize_pii_entities',
    'single_recognize_linked_entities',
    'single_extract_key_phrases',
    'single_analyze_sentiment',
]


async def single_detect_language(
            endpoint,  # type: str
            credential,  # type: str
            text,  # type: str
            country_hint=None,  # type: Optional[str]
            show_stats=False,   # type: Optional[bool]
            model_version=None,  # type: Optional[str]
            **kwargs  # type: Any
):
    # type: (...) -> DocumentLanguage
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
    :param str text: The single string to detect language from.
    :param str country_hint: The country hint for the text. Accepts two
        letter country codes specified by ISO 3166-1 alpha-2.
    :param bool show_stats: If set to true, response will contain
        document level statistics.
    :param str model_version: This value indicates which model will
        be used for scoring. If a model-version is not specified, the API
        will default to the latest, non-preview version.
    :return: An instance of DocumentLanguage.
    :rtype: ~azure.cognitiveservices.language.textanalytics.DocumentLanguage
    :raises: ~azure.core.exceptions.HttpResponseError
    """
    doc = _validate_single_input(text, "country_hint", country_hint)
    async with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = await client.detect_language(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # DocumentLanguage


async def single_recognize_entities(
        endpoint,  # type: str
        credential,  # type: str
        text,  # type: str
        language=None,  # type: Optional[str]
        show_stats=False,  # type: Optional[bool]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> DocumentEntities
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
    :param str text: The single string to recognize entities from.
    :param str language: The language hint for the text.
    :param bool show_stats: If set to true, response will contain
        document level statistics.
    :param str model_version: This value indicates which model will
        be used for scoring. If a model-version is not specified, the API
        will default to the latest, non-preview version.
    :return: An instance of DocumentEntities.
    :rtype: ~azure.cognitiveservices.language.textanalytics.DocumentEntities
    :raises: ~azure.core.exceptions.HttpResponseError
    """
    doc = _validate_single_input(text, "language", language)
    async with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = await client.recognize_entities(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # DocumentEntities


async def single_recognize_pii_entities(
        endpoint,  # type: str
        credential,  # type: str
        text,  # type: str
        language=None,  # type: Optional[str]
        show_stats=False,  # type: Optional[bool]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> DocumentEntities
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
    :param str text: The single string to recognize entities from.
    :param str language: The language hint for the text.
    :param bool show_stats: If set to true, response will contain
        document level statistics.
    :param str model_version: This value indicates which model will
    be used for scoring. If a model-version is not specified, the API
    will default to the latest, non-preview version.
    :return: An instance of DocumentEntities.
    :rtype: ~azure.cognitiveservices.language.textanalytics.DocumentEntities
    :raises: ~azure.core.exceptions.HttpResponseError
    """
    doc = _validate_single_input(text, "language", language)
    async with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = await client.recognize_pii_entities(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # DocumentEntities


async def single_recognize_linked_entities(
        endpoint,  # type: str
        credential,  # type: str
        text,  # type: str
        language=None,  # type: Optional[str]
        show_stats=False,  # type: Optional[bool]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> DocumentLinkedEntities
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
    :param str text: The single string to recognize entities from.
    :param str language: The optional language hint for the text.
    :param bool show_stats: If set to true, response will contain
        document level statistics.
    :param str model_version: This value indicates which model will
        be used for scoring. If a model-version is not specified, the API
        will default to the latest, non-preview version.
    :return: An instance of DocumentLinkedEntities
    :rtype: ~azure.cognitiveservices.language.textanalytics.DocumentLinkedEntities
    :raises: ~azure.core.exceptions.HttpResponseError
    """
    doc = _validate_single_input(text, "language", language)
    async with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = await client.recognize_linked_entities(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # DocumentLinkedEntities


async def single_extract_key_phrases(
        endpoint,  # type: str
        credential,  # type: str
        text,  # type: str
        language=None,  # type: Optional[str]
        show_stats=False,  # type: Optional[bool]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> DocumentKeyPhrases
    """Extract Key Phrases for a single document.

    The API returns a list of strings denoting the key phrases in the input
    text. See https://aka.ms/talangs for the list of enabled languages.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credential: str or token credential
    :param str text: The single string to extract key phrases from.
    :param str language: The optional language hint for the text.
    :param bool show_stats: If set to true, response will contain
        document level statistics.
    :param str model_version: This value indicates which model will
    be used for scoring. If a model-version is not specified, the API
    will default to the latest, non-preview version.
    :return: An instance of DocumentKeyPhrases
    :rtype: ~azure.cognitiveservices.language.textanalytics.DocumentKeyPhrases
    :raises: ~azure.core.exceptions.HttpResponseError
    """
    doc = _validate_single_input(text, "language", language)
    async with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = await client.extract_key_phrases(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # DocumentKeyPhrases


async def single_analyze_sentiment(
        endpoint,  # type: str
        credential,  # type: str
        text,  # type: str
        language=None,  # type: Optional[str]
        show_stats=False,  # type: Optional[bool]
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
    :param str text: The single string to analyze sentiment from.
    :param str language: The optional language hint for the text.
    :param bool show_stats: If set to true, response will contain
        document level statistics.
    :param str model_version: This value indicates which model will
    be used for scoring. If a model-version is not specified, the API
    will default to the latest, non-preview version.
    :return: DocumentSentiment
    :rtype: ~azure.cognitiveservices.language.textanalytics.DocumentSentiment
    :raises: ~azure.core.exceptions.HttpResponseError
    """
    doc = _validate_single_input(text, "language", language)
    async with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = await client.analyze_sentiment(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # DocumentSentiment
