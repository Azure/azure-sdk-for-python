# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._text_analytics_client import TextAnalyticsClient
from ._version import VERSION
from ._base_client import TextAnalyticsApiVersion
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
    TextAnalyticsWarning,
    ExtractKeyPhrasesResult,
    RecognizeLinkedEntitiesResult,
    TextDocumentStatistics,
    LinkedEntityMatch,
    TextDocumentBatchStatistics,
    SentenceSentiment,
    SentimentConfidenceScores,
    MinedOpinion,
    AspectSentiment,
    OpinionSentiment,
    RecognizePiiEntitiesResult,
    PiiEntity,
    PiiEntityDomainType,
    AnalyzeHealthcareResultItem,
    HealthcareEntity,
    HealthcareRelation,
    HealthcareEntityLink,
    EntitiesRecognitionTask,
    PiiEntitiesRecognitionTask,
    KeyPhraseExtractionTask,
    TextAnalysisResult,
    RequestStatistics
)
from._paging import AnalyzeHealthcareResult

__all__ = [
    'TextAnalyticsApiVersion',
    'TextAnalyticsClient',
    'DetectLanguageInput',
    'TextDocumentInput',
    'DetectedLanguage',
    'RecognizeEntitiesResult',
    'DetectLanguageResult',
    'CategorizedEntity',
    'TextAnalyticsError',
    'TextAnalyticsWarning',
    'ExtractKeyPhrasesResult',
    'RecognizeLinkedEntitiesResult',
    'AnalyzeSentimentResult',
    'TextDocumentStatistics',
    'DocumentError',
    'LinkedEntity',
    'LinkedEntityMatch',
    'TextDocumentBatchStatistics',
    'SentenceSentiment',
    'SentimentConfidenceScores',
    'MinedOpinion',
    'AspectSentiment',
    'OpinionSentiment',
    'RecognizePiiEntitiesResult',
    'PiiEntity',
    'PiiEntityDomainType',
    'AnalyzeHealthcareResultItem',
    'AnalyzeHealthcareResult',
    'HealthcareEntity',
    'HealthcareRelation',
    'HealthcareEntityLink',
    'EntitiesRecognitionTask',
    'PiiEntitiesRecognitionTask',
    'KeyPhraseExtractionTask',
    'TextAnalysisResult',
    'RequestStatistics'
]

__version__ = VERSION
