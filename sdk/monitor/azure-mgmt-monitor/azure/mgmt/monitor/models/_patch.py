# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


# the enum is already deprecated in https://github.com/Azure/azure-rest-api-specs/pull/30787,
# but we keep it for CLI compatibility
class ConditionOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Operators allowed in the rule condition."""

    GREATER_THAN = "GreaterThan"
    GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
    LESS_THAN = "LessThan"
    LESS_THAN_OR_EQUAL = "LessThanOrEqual"


# the enum is already deprecated in https://github.com/Azure/azure-rest-api-specs/pull/30787,
# but we keep it for CLI compatibility
class TimeAggregationOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Aggregation operators allowed in a rule."""

    AVERAGE = "Average"
    MINIMUM = "Minimum"
    MAXIMUM = "Maximum"
    TOTAL = "Total"
    LAST = "Last"


__all__: List[str] = [
    "ConditionOperator",
    "TimeAggregationOperator",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
