# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2023_06_01_preview.models import ConnectionCategory
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._schema.workspace.connections.credentials import ApiKeyConfigurationSchema
from azure.ai.ml._utils.utils import camel_to_snake
from .workspace_connection import WorkspaceConnectionSchema


class OpenAIWorkspaceConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.AZURE_OPEN_AI, casing_transform=camel_to_snake, required=True
    )
    credentials = NestedField(ApiKeyConfigurationSchema)

    api_version = fields.Str(required=True, allow_none=False)
    api_type = fields.Str(required=False, allow_none=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureOpenAIWorkspaceConnection

        return AzureOpenAIWorkspaceConnection(**data)


class AzureAISearchWorkspaceConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.COGNITIVE_SEARCH, casing_transform=camel_to_snake, required=True
    )
    credentials = NestedField(ApiKeyConfigurationSchema)

    api_version = fields.Str(required=True, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureAISearchWorkspaceConnection

        return AzureAISearchWorkspaceConnection(**data)


# pylint: disable-next=name-too-long
class AzureAIServiceWorkspaceConnectionSchema(WorkspaceConnectionSchema):
    # type and credentials limited
    type = StringTransformedEnum(
        allowed_values=ConnectionCategory.COGNITIVE_SERVICE, casing_transform=camel_to_snake, required=True
    )
    credentials = NestedField(ApiKeyConfigurationSchema)

    api_version = fields.Str(required=True, allow_none=False)
    kind = fields.Str(required=True, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AzureAIServiceWorkspaceConnection

        return AzureAIServiceWorkspaceConnection(**data)
