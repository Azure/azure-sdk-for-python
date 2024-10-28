# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
from typing import List

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget


def list_sum(lst: List[float]) -> float:
    return sum(lst)


def list_mean(lst: List[float]) -> float:
    return list_sum(lst) / len(lst)


def list_mean_nan_safe(lst: List[float]) -> float:
    msg = "All score values are NaN. The mean cannot be calculated."
    if all(math.isnan(l) for l in lst):
        raise EvaluationException(
            message=msg,
            internal_message=msg,
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.INVALID_VALUE,
            target=ErrorTarget.CONVERSATION,
        )
    return list_mean([l for l in lst if not math.isnan(l)])
