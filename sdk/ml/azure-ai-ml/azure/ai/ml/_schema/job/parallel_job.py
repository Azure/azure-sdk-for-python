# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml.constants import JobType
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField, OutputsField

from .base_job import BaseJobSchema
from .parameterized_parallel import ParameterizedParallelSchema


class ParallelJobSchema(ParameterizedParallelSchema, BaseJobSchema):
    type = StringTransformedEnum(allowed_values=JobType.PARALLEL)
    inputs = InputsField()
    outputs = OutputsField()
