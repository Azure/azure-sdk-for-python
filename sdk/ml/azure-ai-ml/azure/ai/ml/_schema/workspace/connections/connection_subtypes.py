# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2024_04_01_preview.models import ConnectionCategory
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._common import ConnectionTypes
from azure.ai.ml._schema.workspace.connections.one_lake_artifacts import OneLakeArtifactSchema
from azure.ai.ml._schema.workspace.connections.credentials import (
    SasTokenConfigurationSchema,
    ServicePrincipalConfigurationSchema,
    AccountKeyConfigurationSchema,
)
from azure.ai.ml.entities import AadCredentialConfiguration
from .connection import ConnectionSchema


# pylint: disable-next=name-too-long
class AzureBlobStoreConnectionSchema(ConnectionSchema):
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
class MicrosoftOneLakeConnectionSchema(ConnectionSchema):
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
        from azure.ai.ml.entities import MicrosoftOneLakeConnection

        return MicrosoftOneLakeConnection(**data)


# pylint: disable-next=name-too-long
class AzureOpenAIConnectionSchema(ConnectionSchema):
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
class AzureAIServiceConnectionSchema(ConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionTypes.AZURE_AI_SERVICES, casing_transform=camel_to_snake, required=True
    )
    api_key = fields.Str(required=False, allow_none=True)
    endpoint = fields.Str()
    ai_services_resource_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureAIServiceConnection

        return AzureAIServiceConnection(**data)


# pylint: disable-next=name-too-long
class AzureAISearchConnectionSchema(ConnectionSchema):
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
class AzureContentSafetyConnectionSchema(ConnectionSchema):
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
class AzureSpeechServicesConnectionSchema(ConnectionSchema):
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


class APIKeyConnectionSchema(ConnectionSchema):
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
class OpenAIConnectionSchema(ConnectionSchema):
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
class SerpConnectionSchema(ConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(allowed_values=ConnectionCategory.SERP, casing_transform=camel_to_snake, required=True)
    api_key = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import SerpConnection

        return SerpConnection(**data)


# pylint: disable-next=name-too-long
class ServerlessConnectionSchema(ConnectionSchema):
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
