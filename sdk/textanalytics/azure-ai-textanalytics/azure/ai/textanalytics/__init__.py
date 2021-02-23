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
    TargetSentiment,
    AssessmentSentiment,
    RecognizePiiEntitiesResult,
    PiiEntity,
    PiiEntityDomainType,
    AnalyzeHealthcareEntitiesResultItem,
    HealthcareEntity,
    HealthcareEntityDataSource,
    RecognizeEntitiesAction,
    RecognizePiiEntitiesAction,
    ExtractKeyPhrasesAction,
    AnalyzeBatchActionsResult,
    RequestStatistics,
    AnalyzeBatchActionsType,
    AnalyzeBatchActionsError,
)
from ._paging import AnalyzeHealthcareEntitiesResult

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
    'TargetSentiment',
    'AssessmentSentiment',
    'RecognizePiiEntitiesResult',
    'PiiEntity',
    'PiiEntityDomainType',
    'AnalyzeHealthcareEntitiesResultItem',
    'AnalyzeHealthcareEntitiesResult',
    'HealthcareEntity',
    'HealthcareEntityDataSource',
    'RecognizeEntitiesAction',
    'RecognizePiiEntitiesAction',
    'ExtractKeyPhrasesAction',
    'AnalyzeBatchActionsResult',
    'RequestStatistics',
    'AnalyzeBatchActionsType',
    "AnalyzeBatchActionsError",
]

__version__ = VERSION
