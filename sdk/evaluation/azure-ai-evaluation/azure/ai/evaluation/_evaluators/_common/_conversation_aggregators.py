# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Callable, List
from azure.ai.evaluation._common.math import list_mean
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._constants import AggregationType


def GetAggregator(aggregation_type: AggregationType) -> Callable[[List[float]], float]:
    if aggregation_type == AggregationType.SUM:
        return sum
    if aggregation_type == AggregationType.MEAN:
        return list_mean
    if aggregation_type == AggregationType.MAX:
        return max
    if aggregation_type == AggregationType.MIN:
        return min
    raise EvaluationException(
        message=f"Unaccounted for aggregation type: {aggregation_type}",
        blame=ErrorBlame.UNKNOWN,
        category=ErrorCategory.INVALID_VALUE,
        target=ErrorTarget.EVALUATE,
    )
