# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import re
from typing import Any, List, Union

from marshmallow import fields

from azure.ai.ml._schema._sweep.search_space import (
    ChoiceSchema,
    NormalSchema,
    QNormalSchema,
    QUniformSchema,
    RandintSchema,
    UniformSchema,
)
from azure.ai.ml._schema.core.fields import DumpableIntegerField, DumpableStringField, NestedField, UnionField
from azure.ai.ml._utils.utils import float_to_str
from azure.ai.ml.constants._job.sweep import SearchSpace
from azure.ai.ml.entities._job.sweep.search_space import (
    Choice,
    LogNormal,
    LogUniform,
    Normal,
    QLogNormal,
    QLogUniform,
    QNormal,
    QUniform,
    Randint,
    SweepDistribution,
    Uniform,
)
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


def _convert_to_rest_object(sweep_distribution: Union[bool, int, float, str, SweepDistribution]) -> str:
    if isinstance(sweep_distribution, float):
        # Float requires some special handling for small values that get auto-represented with scientific notation.
        res: str = float_to_str(sweep_distribution)
        return res
    if not isinstance(sweep_distribution, SweepDistribution):
        # Convert [bool, float, str] types to str
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
        for value in rest_object[1][0]:
            if isinstance(value, str):
                sweep_distribution_args.append("'" + value + "'")
            elif isinstance(value, float):
                sweep_distribution_args.append(float_to_str(value))
            else:
                sweep_distribution_args.append(str(value))
    else:
        for value in rest_object[1]:
            if isinstance(value, float):
                sweep_distribution_args.append(float_to_str(value))
            else:
                sweep_distribution_args.append(str(value))

    sweep_distribution_str: str = sweep_distribution_type + "("
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
    if _is_float(value):
        # Float
        return float(value)
    if value in ["True", "False"]:
        # Convert "True", "False" to python boolean literals
        return value == "True"
    # string value. Remove quotes before returning.
    return value.strip("'\"")


def _convert_from_rest_object(
    sweep_distribution_str: str,
) -> Any:
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
    sweep_distribution_args: List = []
    for value in sweep_distribution_separated[1:]:
        sweep_distribution_args.append(_get_type_inferred_value(value))

    if sweep_distribution_type == SearchSpace.CHOICE:
        sweep_distribution_args = [sweep_distribution_args]  # Choice values are list of lists

    sweep_distribution = SweepDistribution._from_rest_object([sweep_distribution_type, sweep_distribution_args])
    return sweep_distribution


def _convert_sweep_dist_dict_to_str_dict(sweep_distribution: dict) -> dict:
    for k, sweep_dist_dict in sweep_distribution.items():
        if sweep_dist_dict is not None:
            sweep_distribution[k] = _convert_sweep_dist_dict_item_to_str(sweep_dist_dict)
    return sweep_distribution


class ChoicePlusSchema(ChoiceSchema):
    """Choice schema that allows boolean values also"""

    values = fields.List(
        UnionField(
            [
                DumpableIntegerField(strict=True),
                DumpableStringField(),
                fields.Float(),
                fields.Dict(
                    keys=fields.Str(),
                    values=UnionField(
                        [
                            NestedField("ChoicePlusSchema"),
                            NestedField(NormalSchema()),
                            NestedField(QNormalSchema()),
                            NestedField(RandintSchema()),
                            NestedField(UniformSchema()),
                            NestedField(QUniformSchema()),
                            DumpableIntegerField(strict=True),
                            fields.Float(),
                            fields.Str(),
                            fields.Boolean(),
                        ]
                    ),
                ),
                fields.Boolean(),
            ]
        )
    )


def _convert_sweep_dist_dict_item_to_str(sweep_distribution: Union[bool, int, float, str, dict]) -> str:
    # Convert a Sweep Distribution dict to Sweep Distribution string
    # Eg. {type: 'choice', values: ['vitb16r224','vits16r224']} => "Choice('vitb16r224','vits16r224')"
    if isinstance(sweep_distribution, dict):
        sweep_dist_type = sweep_distribution["type"]
        if sweep_dist_type == SearchSpace.CHOICE:
            sweep_dist_obj = ChoicePlusSchema().load(sweep_distribution)  # pylint: disable=no-member
        elif sweep_dist_type in SearchSpace.UNIFORM_LOGUNIFORM:
            sweep_dist_obj = UniformSchema().load(sweep_distribution)  # pylint: disable=no-member
        elif sweep_dist_type in SearchSpace.NORMAL_LOGNORMAL:
            sweep_dist_obj = NormalSchema().load(sweep_distribution)  # pylint: disable=no-member
        elif sweep_dist_type in SearchSpace.QUNIFORM_QLOGUNIFORM:
            sweep_dist_obj = QUniformSchema().load(sweep_distribution)  # pylint: disable=no-member
        elif sweep_dist_type in SearchSpace.QNORMAL_QLOGNORMAL:
            sweep_dist_obj = QNormalSchema().load(sweep_distribution)  # pylint: disable=no-member
        elif sweep_dist_type in SearchSpace.RANDINT:
            sweep_dist_obj = RandintSchema().load(sweep_distribution)  # pylint: disable=no-member
        else:
            msg = f"Unsupported sweep distribution type {sweep_dist_type}"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.AUTOML,
                error_category=ErrorCategory.USER_ERROR,
            )
    else:  # Case for other primitive types
        sweep_dist_obj = sweep_distribution

    sweep_dist_str = _convert_to_rest_object(sweep_dist_obj)
    return sweep_dist_str


def _convert_sweep_dist_str_to_dict(sweep_dist_str_list: dict) -> dict:
    for k, val in sweep_dist_str_list.items():
        if isinstance(val, str):
            sweep_dist_str_list[k] = _convert_sweep_dist_str_item_to_dict(val)
    return sweep_dist_str_list


def _convert_sweep_dist_str_item_to_dict(
    sweep_distribution_str: str,
) -> Union[bool, int, float, str, dict]:
    # sweep_distribution_str can be a distribution like "choice('vitb16r224', 'vits16r224')"
    # return type is {type: 'choice', values: ['vitb16r224', 'vits16r224']}
    sweep_dist_obj = _convert_from_rest_object(sweep_distribution_str)
    sweep_dist: Union[bool, int, float, str, dict] = ""
    if isinstance(sweep_dist_obj, SweepDistribution):
        if isinstance(sweep_dist_obj, Choice):
            sweep_dist = ChoicePlusSchema().dump(sweep_dist_obj)  # pylint: disable=no-member
        elif isinstance(sweep_dist_obj, (QNormal, QLogNormal)):
            sweep_dist = QNormalSchema().dump(sweep_dist_obj)  # pylint: disable=no-member
        elif isinstance(sweep_dist_obj, (QUniform, QLogUniform)):
            sweep_dist = QUniformSchema().dump(sweep_dist_obj)  # pylint: disable=no-member
        elif isinstance(sweep_dist_obj, (Uniform, LogUniform)):
            sweep_dist = UniformSchema().dump(sweep_dist_obj)  # pylint: disable=no-member
        elif isinstance(sweep_dist_obj, (Normal, LogNormal)):
            sweep_dist = NormalSchema().dump(sweep_dist_obj)  # pylint: disable=no-member
        elif isinstance(sweep_dist_obj, Randint):
            sweep_dist = RandintSchema().dump(sweep_dist_obj)  # pylint: disable=no-member
        else:
            msg = "Invalid sweep distribution {}"
            raise ValidationException(
                message=msg.format(sweep_distribution_str),
                no_personal_data_message=msg,
                target=ErrorTarget.AUTOML,
                error_category=ErrorCategory.USER_ERROR,
            )
    else:  # Case for other primitive types
        sweep_dist = sweep_dist_obj

    return sweep_dist
