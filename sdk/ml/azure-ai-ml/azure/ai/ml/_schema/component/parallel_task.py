# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from marshmallow import fields

from azure.ai.ml._schema.core.fields import ArmVersionedStr, NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.assets.environment import AnonymousEnvironmentSchema
from azure.ai.ml.constants import AzureMLResourceType, ParallelTaskType


class ComponentParallelTaskSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=[ParallelTaskType.RUN_FUNCTION, ParallelTaskType.MODEL, ParallelTaskType.FUNCTION],
        required=True,
    )
    code = UnionField(
        [
            ArmVersionedStr(azureml_type=AzureMLResourceType.CODE),
            fields.Url(),
            fields.Str(),
        ],
        metadata={"description": "A local path or http:, https:, azureml: url pointing to a remote location."},
    )
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
