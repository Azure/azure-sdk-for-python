# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load
from marshmallow.exceptions import ValidationError
from marshmallow.decorators import pre_load

from azure.ai.ml._restclient.v2024_04_01_preview.models import ConnectionCategory
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._common import ConnectionTypes
from azure.ai.ml._schema.workspace.connections.one_lake_artifacts import OneLakeArtifactSchema
from azure.ai.ml._schema.workspace.connections.credentials import (
    SasTokenConfigurationSchema,
    ServicePrincipalConfigurationSchema,
    AccountKeyConfigurationSchema,
    AadCredentialConfigurationSchema,
)
from azure.ai.ml.entities import AadCredentialConfiguration
from .workspace_connection import WorkspaceConnectionSchema


# pylint: disable-next=name-too-long
class AzureBlobStoreConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.AZURE_BLOB, casing_transform=camel_to_snake, required=True
    )
    credentials = UnionField(
        [
            NestedField(SasTokenConfigurationSchema),
            NestedField(AccountKeyConfigurationSchema),
            NestedField(AadCredentialConfigurationSchema),
        ],
        required=False,
        load_default=AadCredentialConfiguration(),
    )

    url = fields.Str()

    account_name = fields.Str(required=True, allow_none=False)
    container_name = fields.Str(required=True, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureBlobStoreConnection

        return AzureBlobStoreConnection(**data)


# pylint: disable-next=name-too-long
class MicrosoftOneLakeConnectionSchema(WorkspaceConnectionSchema):
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.AZURE_ONE_LAKE, casing_transform=camel_to_snake, required=True
    )
    credentials = UnionField(
        [NestedField(ServicePrincipalConfigurationSchema), NestedField(AadCredentialConfigurationSchema)],
        required=False,
        load_default=AadCredentialConfiguration(),
    )
    artifact = NestedField(OneLakeArtifactSchema, required=False, allow_none=True)

    endpoint = fields.Str(required=False)
    one_lake_workspace_name = fields.Str(required=False)

    @pre_load
    def check_for_target(self, data, **kwargs):
        target = data.get("target", None)
        artifact = data.get("artifact", None)
        endpoint = data.get("endpoint", None)
        one_lake_workspace_name = data.get("one_lake_workspace_name", None)
        # If the user is using a target, then they don't need the artifact and one lake workspace name.
        # This is distinct from when the user set's the 'endpoint' value, which is also used to construct
        # the target. If the target is already present, then the loaded connection YAML was probably produced
        # by dumping an extant connection.
        if target is None:
            if artifact is None:
                raise ValidationError("If target is unset, then artifact must be set")
            if endpoint is None:
                raise ValidationError("If target is unset, then endpoint must be set")
            if one_lake_workspace_name is None:
                raise ValidationError("If target is unset, then one_lake_workspace_name must be set")
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import MicrosoftOneLakeConnection

        return MicrosoftOneLakeConnection(**data)


# pylint: disable-next=name-too-long
class AzureOpenAIConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.AZURE_OPEN_AI, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=False, allow_none=True)
    api_version = fields.Str(required=False, allow_none=True)

    azure_endpoint = fields.Str()
    open_ai_resource_id = fields.Str(required=False, allow_none=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureOpenAIConnection

        return AzureOpenAIConnection(**data)


# pylint: disable-next=name-too-long
class AzureAIServicesConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionTypes.AZURE_AI_SERVICES, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=False, allow_none=True)
    endpoint = fields.Str()
    ai_services_resource_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureAIServicesConnection

        return AzureAIServicesConnection(**data)


# pylint: disable-next=name-too-long
class AzureAISearchConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionTypes.AZURE_SEARCH, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=False, allow_none=True)
    endpoint = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureAISearchConnection

        return AzureAISearchConnection(**data)


# pylint: disable-next=name-too-long
class AzureContentSafetyConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionTypes.AZURE_CONTENT_SAFETY, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=False, allow_none=True)
    endpoint = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureContentSafetyConnection

        return AzureContentSafetyConnection(**data)


# pylint: disable-next=name-too-long
class AzureSpeechServicesConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionTypes.AZURE_SPEECH_SERVICES, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=False, allow_none=True)
    endpoint = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureSpeechServicesConnection

        return AzureSpeechServicesConnection(**data)


class APIKeyConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.API_KEY, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=True)
    api_base = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import APIKeyConnection

        return APIKeyConnection(**data)


# pylint: disable-next=name-too-long
class OpenAIConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.OPEN_AI, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import OpenAIConnection

        return OpenAIConnection(**data)


# pylint: disable-next=name-too-long
class SerpConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(allowed_values=ConnectionCategory.SERP, casing_transform=camel_to_snake, required=True)
    api_key = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import SerpConnection

        return SerpConnection(**data)


# pylint: disable-next=name-too-long
class ServerlessConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.SERVERLESS, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=True)
    endpoint = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import ServerlessConnection

        return ServerlessConnection(**data)
