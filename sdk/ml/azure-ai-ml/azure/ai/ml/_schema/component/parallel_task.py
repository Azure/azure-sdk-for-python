# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from marshmallow import fields

from azure.ai.ml._schema.assets.environment import AnonymousEnvironmentSchema
from azure.ai.ml._schema.core.fields import ArmVersionedStr, CodeField, NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml.constants import ParallelTaskType
from azure.ai.ml.constants._common import AzureMLResourceType


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
    environment = UnionField(
        [
            NestedField(AnonymousEnvironmentSchema),
            ArmVersionedStr(azureml_type=AzureMLResourceType.ENVIRONMENT, allow_default_version=True),
        ],
        required=True,
    )
