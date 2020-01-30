# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._text_analytics_client import TextAnalyticsClient
from ._version import VERSION
from ._models import (
    DetectLanguageInput,
    TextDocumentInput,
    DetectedLanguage,
    DocumentError,
    NamedEntity,
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
    SentimentConfidenceScorePerLabel
)
from ._credential import TextAnalyticsApiKeyCredential

__all__ = [
    'TextAnalyticsClient',
    'DetectLanguageInput',
    'TextDocumentInput',
    'DetectedLanguage',
    'RecognizeEntitiesResult',
    'RecognizePiiEntitiesResult',
    'DetectLanguageResult',
    'NamedEntity',
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
    'SentimentConfidenceScorePerLabel',
    'TextAnalyticsApiKeyCredential'
]

__version__ = VERSION
