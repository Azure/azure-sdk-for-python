# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from enum import Enum

class EvaluationMetrics(str, Enum):
    Relevance = "relevance"
    HateUnfairness = "hate_unfairness"
    Violence = "violence"
    Groundedness = "groundedness"
    GroundednessPro = "groundedness_pro"
