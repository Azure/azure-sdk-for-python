# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict

from azure.ai.ml._restclient.v2022_01_01_preview.models import ConnectionAuthType
from azure.ai.ml._schema import PatchedSchemaMeta, StringTransformedEnum
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._workspace.connections.credentials import (
    PatTokenCredentials,
    SasTokenCredentials,
    UsernamePasswordCredentials,
    ManagedIdentityCredentials,
    ServicePrincipalCredentials,
)
from marshmallow import fields, post_load


class WorkspaceCredentialsSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str()


class PatTokenCredentialsSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(allowed_values=ConnectionAuthType.PAT, casing_transform=camel_to_snake, required=True)
    pat = fields.Str()

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> PatTokenCredentials:
        return PatTokenCredentials(**data)


class SasTokenCredentialsSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(allowed_values=ConnectionAuthType.SAS, casing_transform=camel_to_snake, required=True)
    pat = fields.Str()

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> SasTokenCredentials:
        return SasTokenCredentials(**data)


class UsernamePasswordCredentialsSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=ConnectionAuthType.USERNAME_PASSWORD, casing_transform=camel_to_snake, required=True
    )
    username = fields.Str()
    password = fields.Str()

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> UsernamePasswordCredentials:
        return UsernamePasswordCredentials(**data)


class ManagedIdentityCredentialsSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=ConnectionAuthType.MANAGED_IDENTITY, casing_transform=camel_to_snake, required=True
    )
    client_id = fields.Str()
    resource_id = fields.Str()

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> ManagedIdentityCredentials:
        return ManagedIdentityCredentials(**data)


class ServicePrincipalCredentialsSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=ConnectionAuthType.SERVICE_PRINCIPAL, casing_transform=camel_to_snake, required=True
    )

    client_id = fields.Str()
    client_secret = fields.Str()
    tenant_id = fields.Str()

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> ServicePrincipalCredentials:
        return ServicePrincipalCredentials(**data)
