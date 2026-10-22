#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# cspell:ignore milli
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta


class MetricAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The aggregation type of the metric."""

    NONE = "None"
    AVERAGE = "Average"
    COUNT = "Count"
    MINIMUM = "Minimum"
    MAXIMUM = "Maximum"
    TOTAL = "Total"
