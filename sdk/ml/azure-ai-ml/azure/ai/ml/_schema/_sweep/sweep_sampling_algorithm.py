# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._restclient.v2023_02_01_preview.models import RandomSamplingAlgorithmRule, SamplingAlgorithmType
from azure.ai.ml._schema.core.fields import StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake

module_logger = logging.getLogger(__name__)


class RandomSamplingAlgorithmSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        required=True,
        allowed_values=SamplingAlgorithmType.RANDOM,
        casing_transform=camel_to_snake,
    )

    seed = fields.Int()

    logbase = UnionField(
        [
            fields.Number(),
            fields.Str(),
        ],
        data_key="logbase",
    )

    rule = StringTransformedEnum(
        allowed_values=[
            RandomSamplingAlgorithmRule.RANDOM,
            RandomSamplingAlgorithmRule.SOBOL,
        ],
        casing_transform=camel_to_snake,
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import RandomSamplingAlgorithm

        data.pop("type")
        return RandomSamplingAlgorithm(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.sweep import RandomSamplingAlgorithm

        if not isinstance(data, RandomSamplingAlgorithm):
            raise ValidationError("Cannot dump non-RandomSamplingAlgorithm object into RandomSamplingAlgorithm")
        return data


class GridSamplingAlgorithmSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        required=True,
        allowed_values=SamplingAlgorithmType.GRID,
        casing_transform=camel_to_snake,
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import GridSamplingAlgorithm

        data.pop("type")
        return GridSamplingAlgorithm(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.sweep import GridSamplingAlgorithm

        if not isinstance(data, GridSamplingAlgorithm):
            raise ValidationError("Cannot dump non-GridSamplingAlgorithm object into GridSamplingAlgorithm")
        return data


class BayesianSamplingAlgorithmSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        required=True,
        allowed_values=SamplingAlgorithmType.BAYESIAN,
        casing_transform=camel_to_snake,
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import BayesianSamplingAlgorithm

        data.pop("type")
        return BayesianSamplingAlgorithm(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.sweep import BayesianSamplingAlgorithm

        if not isinstance(data, BayesianSamplingAlgorithm):
            raise ValidationError("Cannot dump non-BayesianSamplingAlgorithm object into BayesianSamplingAlgorithm")
        return data
