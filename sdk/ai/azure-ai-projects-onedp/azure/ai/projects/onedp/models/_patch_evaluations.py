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


class EvaluationMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    RELEVANCE = "relevance"
    HATE_UNFAIRNESS = "hate_unfairness"
    VIOLENCE = "violence"
    GROUNDEDNESS = "groundedness"
    GROUNDEDNESS_PRO = "groundedness_pro"
