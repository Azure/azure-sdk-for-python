# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Callable, List
from azure.ai.evaluation._common.math import list_mean
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._constants import _AggregationType


def GetAggregator(aggregation_type: _AggregationType) -> Callable[[List[float]], float]:
    if aggregation_type == _AggregationType.SUM:
        return sum
    if aggregation_type == _AggregationType.MEAN:
        return list_mean
    if aggregation_type == _AggregationType.MAX:
        return max
    if aggregation_type == _AggregationType.MIN:
        return min
    if aggregation_type == _AggregationType.CUSTOM:
        msg = (
            "Cannot 'get' aggregator function associated with custom aggregation enum."
            + " This enum value should only be outputted as an indicator of an injected"
            + " aggregation function, not inputted directly"
        )
        raise EvaluationException(
            message=msg,
            blame=ErrorBlame.UNKNOWN,
            category=ErrorCategory.INVALID_VALUE,
            target=ErrorTarget.EVALUATE,
        )
    raise EvaluationException(
        message=f"Unaccounted for aggregation type: {aggregation_type}",
        blame=ErrorBlame.UNKNOWN,
        category=ErrorCategory.INVALID_VALUE,
        target=ErrorTarget.EVALUATE,
    )


def GetAggregatorType(aggregation_function: Callable) -> _AggregationType:
    if aggregation_function == sum:  # pylint: disable=comparison-with-callable
        return _AggregationType.SUM
    if aggregation_function == list_mean:  # pylint: disable=comparison-with-callable
        return _AggregationType.MEAN
    if aggregation_function == max:  # pylint: disable=comparison-with-callable
        return _AggregationType.MAX
    if aggregation_function == min:  # pylint: disable=comparison-with-callable
        return _AggregationType.MIN
    return _AggregationType.CUSTOM
