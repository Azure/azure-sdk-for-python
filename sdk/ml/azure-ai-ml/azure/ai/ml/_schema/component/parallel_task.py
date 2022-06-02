# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from marshmallow import fields, INCLUDE
from azure.ai.ml._schema import StringTransformedEnum, UnionField, NestedField

from azure.ai.ml._schema import PatchedSchemaMeta, ArmVersionedStr
from azure.ai.ml.constants import (
    ParallelTaskType,
    AzureMLResourceType,
)
from azure.ai.ml._schema.assets.environment import AnonymousEnvironmentSchema


class ComponentParallelTaskSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=[ParallelTaskType.FUNCTION, ParallelTaskType.MODEL],
        Required=True,
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
    args = fields.Str()
    model = fields.Str()
    append_row_to = fields.Str()
    environment = UnionField(
        [
            NestedField(AnonymousEnvironmentSchema),
            ArmVersionedStr(azureml_type=AzureMLResourceType.ENVIRONMENT, allow_default_version=True),
        ],
        required=True,
    )
