# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Callable, List
from azure.ai.evaluation._common.math import list_mean
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._constants import ConversationAggregationType

def GetAggregator(aggregation_type: ConversationAggregationType) -> Callable[[List[float]], float]:
    if (aggregation_type == ConversationAggregationType.SUM):
        return sum
    elif (aggregation_type == ConversationAggregationType.MEAN):
        return list_mean
    elif (aggregation_type == ConversationAggregationType.MAX):
        return max
    elif (aggregation_type == ConversationAggregationType.MIN):
        return min
    else:
        raise EvaluationException(
            message=f"Unaccounted for aggregation type: {aggregation_type}",
            blame=ErrorBlame.UNKNOWN,
            category=ErrorCategory.INVALID_VALUE,
            target=ErrorTarget.EVALUATE
        )
