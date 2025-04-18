# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from enum import Enum
from typing import List


class EvaluationMetrics(str, Enum):
    Relevance = "relevance"
    HateUnfairness = "hate_unfairness"
    Violence = "violence"
    Groundedness = "groundedness"
    GroundednessPro = "groundedness_pro"


__all__: List[str] = ["EvaluationMetrics"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
