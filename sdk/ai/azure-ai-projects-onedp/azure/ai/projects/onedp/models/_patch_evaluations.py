# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta


class EvaluatorIds(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    RELEVANCE = "azureai://built-in/evaluators/relevance"
    HATE_UNFAIRNESS = "azureai://built-in/evaluators/hate_unfairness"
    VIOLENCE = "azureai://built-in/evaluators/violence"
    GROUNDEDNESS = "azureai://built-in/evaluators/groundedness"
    GROUNDEDNESS_PRO = "azureai://built-in/evaluators/groundedness_pro"
    BLUE_SCORE = "azureai://built-in/evaluators/blue_score",
    CODE_VULNERABILITY = "azureai://built-in/evaluators/code_vulnerability",
    COHERENCE = "azureai://built-in/evaluators/coherence",
    CONTENT_SAFETY = "azureai://built-in/evaluators/content_safety",
    F1_SCORE = "azureai://built-in/evaluators/f1_score",
    FLUENCY = "azureai://built-in/evaluators/fluency",
    GLEU_SCORE = "azureai://built-in/evaluators/gleu_score",
    INDIRECT_ATTACK = "azureai://built-in/evaluators/indirect_attack",
    # INTENT_RESOLUTION = "azureai://built-in/evaluators/intent_resolution",
    METEOR_SCORE = "azureai://built-in/evaluators/meteor_score",
    PROTECTED_MATERIAL = "azureai://built-in/evaluators/protected_material",
    RETRIEVAL = "azureai://built-in/evaluators/retrieval",
    ROUGE_SCORE = "azureai://built-in/evaluators/rouge_score",
    SELF_HARM = "azureai://built-in/evaluators/self_harm",
    SEXUAL = "azureai://built-in/evaluators/sexual",
    SIMILARITY_SCORE = "azureai://built-in/evaluators/similarity_score",
    # TASK_ADHERENCE = "azureai://built-in/evaluators/task_adherence",
    # TOOL_CALL_ACCURACY = "azureai://built-in/evaluators/tool_call_accuracy",
    UNGROUNDED_ATTRIBUTES = "azureai://built-in/evaluators/ungrounded_attributes",
    RESPONSE_COMPLETENESS = "azureai://built-in/evaluators/response_completeness",


