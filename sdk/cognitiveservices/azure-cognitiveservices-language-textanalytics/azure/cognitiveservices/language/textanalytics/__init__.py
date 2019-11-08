# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, Optional, List  # pylint: disable=unused-import
from ._text_analytics_client import TextAnalyticsClient
from ._response_handlers import _validate_single_input, process_single_error, process_entities_error
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
            country_hint=None,  # type: str
            model_version=None,  # type: Optional[str]
            **kwargs  # type: Any
):
    # type: (...) -> DetectedLanguage
    doc = _validate_single_input(text, "country_hint", country_hint)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential) as client:
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
        language=None,  # type: str
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> List[Entity]
    doc = _validate_single_input(text, "language", language)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential) as client:
        response = client.recognize_entities(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        try:
            return response[0].entities  # list[Entity]
        except TypeError:
            return process_entities_error(response)


def single_recognize_pii_entities(
        endpoint,  # type: str
        credential,  # type: str
        text,  # type: str
        language=None,  # type: str
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> List[Entity]
    doc = _validate_single_input(text, "language", language)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential) as client:
        response = client.recognize_pii_entities(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        try:
            return response[0].entities  # list[Entity]
        except TypeError:
            return process_entities_error(response)


def single_recognize_linked_entities(
        endpoint,  # type: str
        credential,  # type: str
        text,  # type: str
        language=None,  # type: str
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> List[LinkedEntity]
    doc = _validate_single_input(text, "language", language)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential) as client:
        response = client.recognize_linked_entities(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        try:
            return response[0].entities  # list[Entity]
        except TypeError:
            return process_entities_error(response)


def single_extract_key_phrases(
        endpoint,  # type: str
        credential,  # type: str
        text,  # type: str
        language=None,  # type: str
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> List[str]
    doc = _validate_single_input(text, "language", language)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential) as client:
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
        language=None,  # type: str
        model_version=None,  # type: Optional[str]
        **kwargs  # type: Any
):
    # type: (...) -> DocumentSentiment
    doc = _validate_single_input(text, "language", language)
    show_stats = kwargs.pop("show_stats", False)
    with TextAnalyticsClient(endpoint, credential=credential) as client:
        response = client.analyze_sentiment(
            documents=doc,
            model_version=model_version,
            show_stats=show_stats,
            **kwargs
        )
        if response[0].is_error:
            return process_single_error(response[0])  # DocumentError
        return response[0]  # DocumentSentiment
