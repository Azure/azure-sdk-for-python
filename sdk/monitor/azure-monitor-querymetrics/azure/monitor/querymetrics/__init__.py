# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from ._client import MetricsClient
from ._enums import MetricAggregationType
from ._models import MetricsQueryResult, TimeSeriesElement, Metric, MetricValue

from ._version import VERSION

__all__ = [
    "MetricsClient",
    "MetricsQueryResult",
    "TimeSeriesElement",
    "Metric",
    "MetricValue",
    "MetricAggregationType",
]

__version__ = VERSION
