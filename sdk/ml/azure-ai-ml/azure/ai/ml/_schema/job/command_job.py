# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField, OutputsField
from azure.ai.ml.constants import JobType

from .base_job import BaseJobSchema
from .job_limits import CommandJobLimitsSchema
from .parameterized_command import ParameterizedCommandSchema


class CommandJobSchema(ParameterizedCommandSchema, BaseJobSchema):
    type = StringTransformedEnum(allowed_values=JobType.COMMAND)
    # do not promote it as CommandComponent has no field named 'limits'
    limits = NestedField(CommandJobLimitsSchema)
    parameters = fields.Dict(dump_only=True)
    inputs = InputsField()
    outputs = OutputsField()
