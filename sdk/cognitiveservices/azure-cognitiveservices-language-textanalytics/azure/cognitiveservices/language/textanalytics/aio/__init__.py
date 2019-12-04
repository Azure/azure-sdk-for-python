# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, Optional, TYPE_CHECKING  # pylint: disable=unused-import
from .._request_handlers import _validate_single_input
from .._response_handlers import process_single_error
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
            country_hint="US",  # type: Optional[str]
            show_stats=False,   # type: Optional[bool]
            model_version=None,  # type: Optional[str]
            **kwargs  # type: Any
):
    # type: (...) -> DocumentLanguage
    """Detect Language for a single document.

    Returns the detected language and a numeric score between zero and
    one. Scores close to one indicate 100% certainty that the identified
    language is true. See https://aka.ms/talangs for the list of enabled languages.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credential: str or token credential
    :param str text: The single string to detect language from.
    :param str country_hint: The country hint for the text. Accepts two
        letter country codes specified by ISO 3166-1 alpha-2.
        Defaults to "US". If you don't want to use a country hint,
        pass the empty string "".
    :param bool show_stats: If set to true, response will contain
        document level statistics.
    :param str model_version: This value indicates which model will
        be used for scoring. If a model-version is not specified, the API
        will default to the latest, non-preview version.
    :return: An instance of DocumentLanguage.
    :rtype: ~azure.cognitiveservices.language.textanalytics.DocumentLanguage
    :raises: ~azure.core.exceptions.HttpResponseError

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_single_detect_language_async.py
            :start-after: [START single_detect_language_async]
            :end-before: [END single_detect_language_async]
            :language: python
            :dedent: 8
            :caption: Detecting language in a single string.
    """
    doc = _validate_single_input(text, "country_hint", country_hint)
    async with TextAnalyticsClient(endpoint, credential=credential, **kwargs) as client:
        response = await client.detect_languages(
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
        language="en",  # type: Optional[str]
        show_stats=False,  # type: Optional[bool]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> DocumentEntities
    """Named Entity Recognition for a single document.

    Returns a list of general named entities in a given document.
    For a list of supported entity types, check: https://aka.ms/taner
    For a list of enabled languages, check: https://aka.ms/talangs

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credential: str or token credential
    :param str text: The single string to recognize entities from.
    :param str language: This is the 2 letter ISO 639-1 representation
        of a language. For example, use "en" for English; "es" for Spanish etc. If
        not set, uses "en" for English as default.
    :param bool show_stats: If set to true, response will contain
        document level statistics.
    :param str model_version: This value indicates which model will
        be used for scoring. If a model-version is not specified, the API
        will default to the latest, non-preview version.
    :return: An instance of DocumentEntities.
    :rtype: ~azure.cognitiveservices.language.textanalytics.DocumentEntities
    :raises: ~azure.core.exceptions.HttpResponseError

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_single_recognize_entities_async.py
            :start-after: [START single_recognize_entities_async]
            :end-before: [END single_recognize_entities_async]
            :language: python
            :dedent: 8
            :caption: Recognize entities in a single string.
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
        language="en",  # type: Optional[str]
        show_stats=False,  # type: Optional[bool]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> DocumentEntities
    """Recognize entities containing personal information for a single document.

    Returns a list of personal information entities ("SSN",
    "Bank Account", etc) in the document.  For the list of supported entity types,
    check https://aka.ms/tanerpii. See https://aka.ms/talangs
    for the list of enabled languages.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credential: str or token credential
    :param str text: The single string to recognize entities from.
    :param str language: This is the 2 letter ISO 639-1 representation
        of a language. For example, use "en" for English; "es" for Spanish etc. If
        not set, uses "en" for English as default.
    :param bool show_stats: If set to true, response will contain
        document level statistics.
    :param str model_version: This value indicates which model will
        be used for scoring. If a model-version is not specified, the API
        will default to the latest, non-preview version.
    :return: An instance of DocumentEntities.
    :rtype: ~azure.cognitiveservices.language.textanalytics.DocumentEntities
    :raises: ~azure.core.exceptions.HttpResponseError

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_single_recognize_pii_entities_async.py
            :start-after: [START single_recognize_pii_entities_async]
            :end-before: [END single_recognize_pii_entities_async]
            :language: python
            :dedent: 8
            :caption: Recognize personally identifiable information entities in a single string.
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
        language="en",  # type: Optional[str]
        show_stats=False,  # type: Optional[bool]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> DocumentLinkedEntities
    """Recognize linked entities from a well-known knowledge base
    for a single document.

    Returns a list of recognized entities with links to a
    well-known knowledge base. See https://aka.ms/talangs for
    supported languages in Text Analytics API.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credential: str or token credential
    :param str text: The single string to recognize entities from.
    :param str language: This is the 2 letter ISO 639-1 representation
        of a language. For example, use "en" for English; "es" for Spanish etc. If
        not set, uses "en" for English as default.
    :param bool show_stats: If set to true, response will contain
        document level statistics.
    :param str model_version: This value indicates which model will
        be used for scoring. If a model-version is not specified, the API
        will default to the latest, non-preview version.
    :return: An instance of DocumentLinkedEntities
    :rtype: ~azure.cognitiveservices.language.textanalytics.DocumentLinkedEntities
    :raises: ~azure.core.exceptions.HttpResponseError

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_single_recognize_linked_entities_async.py
            :start-after: [START single_recognize_linked_entities_async]
            :end-before: [END single_recognize_linked_entities_async]
            :language: python
            :dedent: 8
            :caption: Recognize linked entities in a single string.
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
        language="en",  # type: Optional[str]
        show_stats=False,  # type: Optional[bool]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> DocumentKeyPhrases
    """Extract Key Phrases for a single document.

    Returns a list of strings denoting the key phrases in the input
    text. See https://aka.ms/talangs for the list of enabled
    languages.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and
        hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the cognitive services subscription key or a token credential
        from azure.identity.
    :type credential: str or token credential
    :param str text: The single string to extract key phrases from.
    :param str language: This is the 2 letter ISO 639-1 representation
        of a language. For example, use "en" for English; "es" for Spanish etc. If
        not set, uses "en" for English as default.
    :param bool show_stats: If set to true, response will contain
        document level statistics.
    :param str model_version: This value indicates which model will
        be used for scoring. If a model-version is not specified, the API
        will default to the latest, non-preview version.
    :return: An instance of DocumentKeyPhrases
    :rtype: ~azure.cognitiveservices.language.textanalytics.DocumentKeyPhrases
    :raises: ~azure.core.exceptions.HttpResponseError

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_single_extract_key_phrases_async.py
            :start-after: [START single_extract_key_phrases_async]
            :end-before: [END single_extract_key_phrases_async]
            :language: python
            :dedent: 8
            :caption: Extract key phrases in a single string.
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
        language="en",  # type: Optional[str]
        show_stats=False,  # type: Optional[bool]
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> DocumentSentiment
    """Analyze sentiment in a single document.

    Returns a sentiment prediction, as well as sentiment scores for
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
    :param str language: This is the 2 letter ISO 639-1 representation
        of a language. For example, use "en" for English; "es" for Spanish etc. If
        not set, uses "en" for English as default.
    :param bool show_stats: If set to true, response will contain
        document level statistics.
    :param str model_version: This value indicates which model will
        be used for scoring. If a model-version is not specified, the API
        will default to the latest, non-preview version.
    :return: DocumentSentiment
    :rtype: ~azure.cognitiveservices.language.textanalytics.DocumentSentiment
    :raises: ~azure.core.exceptions.HttpResponseError

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_single_analyze_sentiment_async.py
            :start-after: [START single_analyze_sentiment_async]
            :end-before: [END single_analyze_sentiment_async]
            :language: python
            :dedent: 8
            :caption: Analyze sentiment in a single string.
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
