# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from azure.ai.ml._schema.core.fields import NestedField, PathAwareSchema

from ..job.job_limits import SweepJobLimitsSchema
from .sweep_fields_provider import EarlyTerminationField, SamplingAlgorithmField, SearchSpaceField
from .sweep_objective import SweepObjectiveSchema


class ParameterizedSweepSchema(PathAwareSchema):
    """Shared schema for standalone and pipeline sweep job."""

    sampling_algorithm = SamplingAlgorithmField()
    search_space = SearchSpaceField()
    objective = NestedField(
        SweepObjectiveSchema,
        required=True,
        metadata={"description": "The name and optimization goal of the primary metric."},
    )
    early_termination = EarlyTerminationField()
    limits = NestedField(
        SweepJobLimitsSchema,
        required=True,
    )
