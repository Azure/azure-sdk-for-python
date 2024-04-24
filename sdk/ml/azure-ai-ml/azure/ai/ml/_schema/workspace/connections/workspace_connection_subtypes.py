# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2024_04_01_preview.models import ConnectionCategory
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._common import WorkspaceConnectionTypes
from azure.ai.ml._schema.workspace.connections.one_lake_artifacts import OneLakeArtifactSchema
from azure.ai.ml._schema.workspace.connections.credentials import (
    SasTokenConfigurationSchema,
    ServicePrincipalConfigurationSchema,
    AccountKeyConfigurationSchema,
)
from azure.ai.ml.entities import NoneCredentialConfiguration
from azure.ai.ml.entities import AadCredentialConfiguration
from .workspace_connection import WorkspaceConnectionSchema

# pylint: disable-next=name-too-long
class AzureBlobStoreWorkspaceConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.AZURE_BLOB, casing_transform=camel_to_snake, required=True
    )
    credentials = UnionField(
        [
            NestedField(SasTokenConfigurationSchema),
            NestedField(AccountKeyConfigurationSchema),
        ],
        required=False,
        load_default=AadCredentialConfiguration()
    )

    url = fields.Str()

    account_name = fields.Str(required=True, allow_none=False)
    container_name = fields.Str(required=True, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureBlobStoreWorkspaceConnection

        return AzureBlobStoreWorkspaceConnection(**data)

# pylint: disable-next=name-too-long
class MicrosoftOneLakeWorkspaceConnectionSchema(WorkspaceConnectionSchema):
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.AZURE_ONE_LAKE, casing_transform=camel_to_snake, required=True
    )
    credentials = NestedField(
        ServicePrincipalConfigurationSchema, required=False, load_default=AadCredentialConfiguration()
    )
    artifact = NestedField(OneLakeArtifactSchema, required=True)

    endpoint = fields.Str()
    one_lake_workspace_name = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import MicrosoftOneLakeWorkspaceConnection

        return MicrosoftOneLakeWorkspaceConnection(**data)


# pylint: disable-next=name-too-long
class AzureOpenAIWorkspaceConnectionSchema(WorkspaceConnectionSchema):
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
        from azure.ai.ml.entities import AzureOpenAIWorkspaceConnection

        return AzureOpenAIWorkspaceConnection(**data)


# pylint: disable-next=name-too-long
class AzureAIServiceWorkspaceConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=WorkspaceConnectionTypes.AZURE_AI_SERVICES, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=False, allow_none=True)
    endpoint = fields.Str()
    ai_services_resource_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureAIServiceWorkspaceConnection

        return AzureAIServiceWorkspaceConnection(**data)


# pylint: disable-next=name-too-long
class AzureAISearchWorkspaceConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=WorkspaceConnectionTypes.AZURE_SEARCH, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=False, allow_none=True)
    endpoint = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureAISearchWorkspaceConnection

        return AzureAISearchWorkspaceConnection(**data)


# pylint: disable-next=name-too-long
class AzureContentSafetyWorkspaceConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=WorkspaceConnectionTypes.AZURE_CONTENT_SAFETY, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=False, allow_none=True)
    endpoint = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureContentSafetyWorkspaceConnection

        return AzureContentSafetyWorkspaceConnection(**data)


# pylint: disable-next=name-too-long
class AzureSpeechServicesWorkspaceConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=WorkspaceConnectionTypes.AZURE_SPEECH_SERVICES, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=False, allow_none=True)
    endpoint = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureSpeechServicesWorkspaceConnection

        return AzureSpeechServicesWorkspaceConnection(**data)


class APIKeyWorkspaceConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.API_KEY, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=True)
    api_base = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import APIKeyWorkspaceConnection

        return APIKeyWorkspaceConnection(**data)


# pylint: disable-next=name-too-long
class OpenAIWorkspaceConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.OPEN_AI, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import OpenAIWorkspaceConnection

        return OpenAIWorkspaceConnection(**data)


# pylint: disable-next=name-too-long
class SerpWorkspaceConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(allowed_values=ConnectionCategory.SERP, casing_transform=camel_to_snake, required=True)
    api_key = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import SerpWorkspaceConnection

        return SerpWorkspaceConnection(**data)


# pylint: disable-next=name-too-long
class ServerlessWorkspaceConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.SERVERLESS, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=True)
    endpoint = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import ServerlessWorkspaceConnection

        return ServerlessWorkspaceConnection(**data)
