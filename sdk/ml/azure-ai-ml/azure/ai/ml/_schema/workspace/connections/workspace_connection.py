# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2022_01_01_preview.models import ConnectionCategory
from azure.ai.ml._schema.core.fields import ArmStr, NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.job import CreationContextSchema
from azure.ai.ml._schema.workspace.connections.credentials import (
    ManagedIdentityCredentialsSchema,
    PatTokenCredentialsSchema,
    SasTokenCredentialsSchema,
    ServicePrincipalCredentialsSchema,
    UsernamePasswordCredentialsSchema,
)
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import AzureMLResourceType


class WorkspaceConnectionSchema(PathAwareSchema):
    name = fields.Str()
    id = ArmStr(azureml_type=AzureMLResourceType.WORKSPACE_CONNECTION, dump_only=True)
    creation_context = NestedField(CreationContextSchema, dump_only=True)
    type = StringTransformedEnum(
        allowed_values=[
            ConnectionCategory.GIT,
            ConnectionCategory.CONTAINER_REGISTRY,
            ConnectionCategory.PYTHON_FEED,
            ConnectionCategory.FEATURE_STORE,
        ],
        casing_transform=camel_to_snake,
        required=True,
    )
    target = fields.Str()
    credentials = UnionField(
        [
            NestedField(PatTokenCredentialsSchema),
            NestedField(SasTokenCredentialsSchema),
            NestedField(UsernamePasswordCredentialsSchema),
            NestedField(ManagedIdentityCredentialsSchema),
            NestedField(ServicePrincipalCredentialsSchema),
        ]
    )
    metadata = fields.Dict(required=False, allow_none=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import WorkspaceConnection

        return WorkspaceConnection(**data)
