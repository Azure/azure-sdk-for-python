# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields

from ..._schema import NestedField
from ..._schema.core.fields import DumpableEnumField, EnvironmentField
from ..._schema.job import ParameterizedCommandSchema, ParameterizedParallelSchema
from ..._schema.job.job_limits import CommandJobLimitsSchema
from .._schema.node import InternalBaseNodeSchema, NodeType


class CommandSchema(InternalBaseNodeSchema, ParameterizedCommandSchema):
    class Meta:
        exclude = ["code", "distribution"]  # internal command doesn't have code & distribution

    environment = EnvironmentField()
    type = DumpableEnumField(allowed_values=[NodeType.COMMAND])
    limits = NestedField(CommandJobLimitsSchema)


class DistributedSchema(CommandSchema):
    class Meta:
        exclude = ["code"]  # need to enable distribution comparing to CommandSchema

    type = DumpableEnumField(allowed_values=[NodeType.DISTRIBUTED])


class ParallelSchema(InternalBaseNodeSchema, ParameterizedParallelSchema):
    class Meta:
        # partition_keys can still be used with unknown warning, but need to do dump before setting
        exclude = ["task", "input_data", "mini_batch_error_threshold", "partition_keys"]

    type = DumpableEnumField(allowed_values=[NodeType.PARALLEL])
    compute = fields.Str()
    environment = fields.Str()
    limits = NestedField(CommandJobLimitsSchema)
