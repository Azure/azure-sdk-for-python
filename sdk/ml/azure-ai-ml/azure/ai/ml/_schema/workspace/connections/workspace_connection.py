# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2023_04_01_preview.models import ConnectionCategory
from azure.ai.ml._schema.core.fields import ArmStr, NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.job import CreationContextSchema
from azure.ai.ml._schema.workspace.connections.credentials import (
    ManagedIdentityConfigurationSchema,
    PatTokenConfigurationSchema,
    SasTokenConfigurationSchema,
    ServicePrincipalConfigurationSchema,
    UsernamePasswordConfigurationSchema,
    AccessKeyConfigurationSchema,
)
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._common import AzureMLResourceType


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
            ConnectionCategory.S3,
            ConnectionCategory.SNOWFLAKE,
            ConnectionCategory.AZURE_SQL_DB,
            ConnectionCategory.AZURE_SYNAPSE_ANALYTICS,
            ConnectionCategory.AZURE_MY_SQL_DB,
            ConnectionCategory.AZURE_POSTGRES_DB,
        ],
        casing_transform=camel_to_snake,
        required=True,
    )
    target = fields.Str()
    credentials = UnionField(
        [
            NestedField(PatTokenConfigurationSchema),
            NestedField(SasTokenConfigurationSchema),
            NestedField(UsernamePasswordConfigurationSchema),
            NestedField(ManagedIdentityConfigurationSchema),
            NestedField(ServicePrincipalConfigurationSchema),
            NestedField(AccessKeyConfigurationSchema),
        ]
    )
    metadata = fields.Dict(required=False, allow_none=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import WorkspaceConnection

        return WorkspaceConnection(**data)
