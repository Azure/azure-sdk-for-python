# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml._schema._sweep.parameterized_sweep import ParameterizedSweepSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum, NestedField
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField, OutputsField
from azure.ai.ml.constants import JobType
from azure.ai.ml._schema.job import BaseJobSchema, ParameterizedCommandSchema


# This is meant to match the yaml definition NOT the models defined in _restclient


class SweepJobSchema(BaseJobSchema, ParameterizedSweepSchema):
    type = StringTransformedEnum(required=True, allowed_values=JobType.SWEEP)
    trial = NestedField(ParameterizedCommandSchema, required=True)
    inputs = InputsField()
    outputs = OutputsField()
