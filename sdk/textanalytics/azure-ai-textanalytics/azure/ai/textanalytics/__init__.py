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
    CategorizedEntity,
    LinkedEntity,
    AnalyzeSentimentResult,
    RecognizeEntitiesResult,
    DetectLanguageResult,
    TextAnalyticsError,
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

__all__ = [
    'TextAnalyticsClient',
    'DetectLanguageInput',
    'TextDocumentInput',
    'DetectedLanguage',
    'RecognizeEntitiesResult',
    'RecognizePiiEntitiesResult',
    'DetectLanguageResult',
    'CategorizedEntity',
    'TextAnalyticsError',
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
