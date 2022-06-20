# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml._schema import NestedField, PathAwareSchema
from .sweep_fields_provider import SamplingAlgorithmField, SearchSpaceField, EarlyTerminationField
from .sweep_objective import SweepObjectiveSchema
from ..job.job_limits import SweepJobLimitsSchema


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
