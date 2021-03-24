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
    RecognizeLinkedEntitiesAction,
    RecognizePiiEntitiesAction,
    ExtractKeyPhrasesAction,
    AnalyzeBatchActionsResult,
    RequestStatistics,
    AnalyzeBatchActionsType,
    AnalyzeBatchActionsError,
    HealthcareEntityRelationRoleType,
    HealthcareRelation,
    HealthcareRelationRole,
    HealthcareEntityAssertion,
)
from ._paging import AnalyzeHealthcareEntitiesResult
from ._generated.v3_1_preview_4.models import (
    PiiCategory as PiiEntityCategoryType,
    RelationType as HealthcareEntityRelationType
)

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
    'RecognizeLinkedEntitiesAction',
    'RecognizePiiEntitiesAction',
    'ExtractKeyPhrasesAction',
    'AnalyzeBatchActionsResult',
    'RequestStatistics',
    'AnalyzeBatchActionsType',
    "AnalyzeBatchActionsError",
    "PiiEntityCategoryType",
    "HealthcareEntityRelationType",
    "HealthcareEntityRelationRoleType",
    "HealthcareRelation",
    "HealthcareRelationRole",
    "HealthcareEntityAssertion",
]

__version__ = VERSION
