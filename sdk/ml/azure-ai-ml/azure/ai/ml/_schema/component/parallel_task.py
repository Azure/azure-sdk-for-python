# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from marshmallow import fields

from azure.ai.ml._schema.core.fields import CodeField, EnvironmentField, StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml.constants import ParallelTaskType


class ComponentParallelTaskSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=[ParallelTaskType.RUN_FUNCTION, ParallelTaskType.MODEL, ParallelTaskType.FUNCTION],
        required=True,
    )
    code = CodeField()
    entry_script = fields.Str()
    program_arguments = fields.Str()
    model = fields.Str()
    append_row_to = fields.Str()
    environment = EnvironmentField(required=True)
