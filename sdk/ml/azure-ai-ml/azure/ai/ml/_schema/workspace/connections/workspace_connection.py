# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2024_04_01_preview.models import ConnectionCategory
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.resource import ResourceSchema
from azure.ai.ml._schema.job import CreationContextSchema
from azure.ai.ml._schema.workspace.connections.credentials import (
    AccountKeyConfigurationSchema,
    ManagedIdentityConfigurationSchema,
    PatTokenConfigurationSchema,
    SasTokenConfigurationSchema,
    ServicePrincipalConfigurationSchema,
    UsernamePasswordConfigurationSchema,
    AccessKeyConfigurationSchema,
    ApiKeyConfigurationSchema,
    AadCredentialConfigurationSchema,
    NoneCredentialConfigurationSchema,
)
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._common import ConnectionTypes
from azure.ai.ml.entities import NoneCredentialConfiguration, AadCredentialConfiguration


class WorkspaceConnectionSchema(ResourceSchema):
    # Inherits name, id, tags, and description fields from ResourceSchema
    creation_context = NestedField(CreationContextSchema, dump_only=True)
    type = StringTransformedEnum(
        allowed_values=[
            ConnectionCategory.GIT,
            ConnectionCategory.CONTAINER_REGISTRY,
            ConnectionCategory.PYTHON_FEED,
            ConnectionCategory.S3,
            ConnectionCategory.SNOWFLAKE,
            ConnectionCategory.AZURE_SQL_DB,
            ConnectionCategory.AZURE_SYNAPSE_ANALYTICS,
            ConnectionCategory.AZURE_MY_SQL_DB,
            ConnectionCategory.AZURE_POSTGRES_DB,
            ConnectionTypes.CUSTOM,
            ConnectionTypes.AZURE_DATA_LAKE_GEN_2,
        ],
        casing_transform=camel_to_snake,
        required=True,
    )

    # Sorta false, some connection types require this field, some don't.
    # And some rename it... for client familiarity reasons.
    target = fields.Str(required=False)

    credentials = UnionField(
        [
            NestedField(PatTokenConfigurationSchema),
            NestedField(SasTokenConfigurationSchema),
            NestedField(UsernamePasswordConfigurationSchema),
            NestedField(ManagedIdentityConfigurationSchema),
            NestedField(ServicePrincipalConfigurationSchema),
            NestedField(AccessKeyConfigurationSchema),
            NestedField(ApiKeyConfigurationSchema),
            NestedField(AccountKeyConfigurationSchema),
            NestedField(AadCredentialConfigurationSchema),
            NestedField(NoneCredentialConfigurationSchema),
        ],
        required=False,
        load_default=NoneCredentialConfiguration(),
    )

    is_shared = fields.Bool(load_default=True)
    metadata = fields.Dict(required=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import WorkspaceConnection

        # Most non-subclassed connections default to a none credential if none
        # is provided. ALDS Gen 2 connections default to AAD with this code.
        if (
            data.get("type", None) == ConnectionTypes.AZURE_DATA_LAKE_GEN_2
            and data.get("credentials", None) == NoneCredentialConfiguration()
        ):
            data["credentials"] = AadCredentialConfiguration()
        return WorkspaceConnection(**data)
