# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
from typing import List, Callable, Any

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget


def list_sum(lst: List[float]) -> float:
    """Given a list of floats, return the sum of the values.

    :param lst: A list of floats.
    :type lst: List[float]
    :return: The sum of the values in the list.
    :rtype: float
    """

    return sum(lst)


def list_mean(lst: List[float]) -> float:
    """Given a list of floats, calculate the mean of the values.

    :param lst: A list of floats.
    :type lst: List[float]
    :return: The mean of the values in the list.
    :rtype: float
    """

    return list_sum(lst) / len(lst)


def list_mean_nan_safe(lst: List[float]) -> float:
    """Given a list of floats, remove all nan or None values, then calculate the mean of the remaining values.

    :param lst: A list of floats.
    :type lst: List[float]
    :return: The mean of the values in the list.
    :rtype: float
    """

    msg = "All score values are NaN. The mean cannot be calculated."
    if all(math.isnan(l) for l in lst):
        raise EvaluationException(
            message=msg,
            internal_message=msg,
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.INVALID_VALUE,
            target=ErrorTarget.CONVERSATION,
        )
    return list_mean([l for l in lst if not is_none_or_nan(l)])


def apply_transform_nan_safe(lst: List[float], transform_fn: Callable[[float], Any]) -> List[Any]:
    """Given a list of floats, remove all nan values, then apply the inputted transform function
    to the remaining values, and return the resulting list of outputted values.

    :param lst: A list of floats.
    :type lst: List[float]
    :param transform_fn: A function that produces something when applied to a float.
    :type transform_fn: Callable[[float], Any]
    :return: A list of the transformed values.
    :rtype: List[Any]
    """

    msg = "All score values are NaN. The mean cannot be calculated."
    if all(math.isnan(l) for l in lst):
        raise EvaluationException(
            message=msg,
            internal_message=msg,
            blame=ErrorBlame.USER_ERROR,
            category=ErrorCategory.INVALID_VALUE,
            target=ErrorTarget.CONVERSATION,
        )
    return [transform_fn(l) for l in lst if not is_none_or_nan(l)]


def is_none_or_nan(val: float) -> bool:
    """math.isnan raises an error if None is inputted. This is a more robust wrapper.

    :param val: The value to check.
    :type val: float
    :return: Whether the value is None or NaN.
    :rtype: bool
    """

    return val is None or math.isnan(val)
