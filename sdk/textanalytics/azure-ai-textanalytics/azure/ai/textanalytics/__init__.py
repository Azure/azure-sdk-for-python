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
    AnalyzeHealthcareEntitiesResult,
    HealthcareEntity,
    HealthcareEntityDataSource,
    RecognizeEntitiesAction,
    RecognizeLinkedEntitiesAction,
    RecognizePiiEntitiesAction,
    ExtractKeyPhrasesAction,
    _AnalyzeActionsType,
    HealthcareEntityRelationRoleType,
    HealthcareRelation,
    HealthcareRelationRole,
    HealthcareEntityAssertion,
    AnalyzeSentimentAction
)
from ._generated.v3_1_preview_5.models import (
    PiiCategory as PiiEntityCategoryType,
    RelationType as HealthcareEntityRelationType,
    Conditionality as EntityConditionality,
    Certainty as EntityCertainty,
    Association as EntityAssociation
)
from ._lro import AnalyzeHealthcareEntitiesLROPoller, AnalyzeActionsLROPoller

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
    'AnalyzeHealthcareEntitiesResult',
    'HealthcareEntity',
    'HealthcareEntityDataSource',
    'RecognizeEntitiesAction',
    'RecognizeLinkedEntitiesAction',
    'RecognizePiiEntitiesAction',
    'ExtractKeyPhrasesAction',
    '_AnalyzeActionsType',
    "PiiEntityCategoryType",
    "HealthcareEntityRelationType",
    "HealthcareEntityRelationRoleType",
    "HealthcareRelation",
    "HealthcareRelationRole",
    "HealthcareEntityAssertion",
    "EntityConditionality",
    "EntityCertainty",
    "EntityAssociation",
    "AnalyzeSentimentAction",
    "AnalyzeHealthcareEntitiesLROPoller",
    "AnalyzeActionsLROPoller",
]

__version__ = VERSION
