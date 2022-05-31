# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields

from azure.ai.ml._schema import NestedField, UnionField, StringTransformedEnum
from azure.ai.ml._schema._sweep.sweep_sampling_algorithm import (
    RandomSamplingAlgorithmSchema,
    GridSamplingAlgorithmSchema,
    BayesianSamplingAlgorithmSchema,
)
from azure.ai.ml._restclient.v2022_02_01_preview.models import SamplingAlgorithmType


from azure.ai.ml._schema._sweep.search_space import (
    UniformSchema,
    ChoiceSchema,
    NormalSchema,
    QUniformSchema,
    QNormalSchema,
    RandintSchema,
)

from azure.ai.ml._schema._sweep.sweep_termination import (
    BanditPolicySchema,
    MedianStoppingPolicySchema,
    TruncationSelectionPolicySchema,
)


def SamplingAlgorithmField():
    return UnionField(
        [
            SamplingAlgorithmTypeField(),
            NestedField(RandomSamplingAlgorithmSchema()),
            NestedField(GridSamplingAlgorithmSchema()),
            NestedField(BayesianSamplingAlgorithmSchema()),
        ]
    )


def SamplingAlgorithmTypeField():
    return StringTransformedEnum(
        required=True,
        allowed_values=[SamplingAlgorithmType.BAYESIAN, SamplingAlgorithmType.GRID, SamplingAlgorithmType.RANDOM],
        metadata={"description": "The sampling algorithm to use for the hyperparameter sweep."},
    )


def SearchSpaceField():
    return fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            [
                NestedField(ChoiceSchema()),
                NestedField(UniformSchema()),
                NestedField(QUniformSchema()),
                NestedField(NormalSchema()),
                NestedField(QNormalSchema()),
                NestedField(RandintSchema()),
            ]
        ),
        metadata={"description": "The parameters to sweep over the trial."},
    )


def EarlyTerminationField():
    return UnionField(
        [
            NestedField(BanditPolicySchema()),
            NestedField(MedianStoppingPolicySchema()),
            NestedField(TruncationSelectionPolicySchema()),
        ],
        metadata={"description": "The early termination policy to be applied to the Sweep runs."},
    )
