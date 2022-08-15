# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import re
from typing import Union

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml.constants import SearchSpace
from azure.ai.ml.entities._job.sweep.search_space import SweepDistribution


def _convert_to_rest_object(sweep_distribution: Union[bool, int, float, str, SweepDistribution]) -> str:
    if not isinstance(sweep_distribution, SweepDistribution):
        # Convert [bool, int, float, str] types to str
        return str(sweep_distribution)

    rest_object = sweep_distribution._to_rest_object()
    if not isinstance(rest_object, list):
        msg = "Rest Object for sweep distribution should be a list."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.AUTOML,
            error_category=ErrorCategory.USER_ERROR,
        )

    if len(rest_object) <= 1:
        msg = "Rest object for sweep distribution should contain at least two elements."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.AUTOML,
            error_category=ErrorCategory.USER_ERROR,
        )

    sweep_distribution_type = rest_object[0]
    sweep_distribution_args = []

    if not isinstance(rest_object[1], list):
        msg = "The second element of Rest object for sweep distribution should be a list."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.AUTOML,
            error_category=ErrorCategory.USER_ERROR,
        )

    if sweep_distribution_type == SearchSpace.CHOICE:
        # Rest objects for choice distribution are of format ["choice", [[0, 1, 2]]]
        if not isinstance(rest_object[1][0], list):
            msg = "The second element of Rest object for choice distribution should be a list of list."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.AUTOML,
                error_category=ErrorCategory.USER_ERROR,
            )
        for idx, value in enumerate(rest_object[1][0]):
            if isinstance(value, str):
                sweep_distribution_args.append("'" + value + "'")
            else:
                sweep_distribution_args.append(str(value))
    else:
        for idx, value in enumerate(rest_object[1]):
            sweep_distribution_args.append(str(value))

    sweep_distribution_str = sweep_distribution_type + "("
    sweep_distribution_str += ",".join(sweep_distribution_args)
    sweep_distribution_str += ")"
    return sweep_distribution_str


def _is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def _is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def _get_type_inferred_value(value: str) -> Union[bool, int, float, str]:
    value = value.strip()
    if _is_int(value):
        # Int
        return int(value)
    elif _is_float(value):
        # Float
        return float(value)
    elif value in ["True", "False"]:
        # Convert "True", "False" to python boolean literals
        return value == "True"
    else:
        # string value. Remove quotes before returning.
        return value.strip("'\"")


def _convert_from_rest_object(
    sweep_distribution_str: str,
) -> Union[bool, int, float, str, SweepDistribution]:
    # sweep_distribution_str can be a distribution like "choice('vitb16r224', 'vits16r224')" or
    # a single value like "True", "1", "1.0567", "vitb16r224"

    sweep_distribution_str = sweep_distribution_str.strip()
    # Filter by the delimiters and remove splits that are empty strings
    sweep_distribution_separated = list(filter(None, re.split("[ ,()]+", sweep_distribution_str)))

    if len(sweep_distribution_separated) == 1:
        # Single value.
        return _get_type_inferred_value(sweep_distribution_separated[0])

    # Distribution string
    sweep_distribution_type = sweep_distribution_separated[0].strip().lower()
    sweep_distribution_args = []
    for value in sweep_distribution_separated[1:]:
        sweep_distribution_args.append(_get_type_inferred_value(value))

    if sweep_distribution_type == SearchSpace.CHOICE:
        sweep_distribution_args = [sweep_distribution_args]  # Choice values are list of lists

    sweep_distribution = SweepDistribution._from_rest_object([sweep_distribution_type, sweep_distribution_args])
    return sweep_distribution
