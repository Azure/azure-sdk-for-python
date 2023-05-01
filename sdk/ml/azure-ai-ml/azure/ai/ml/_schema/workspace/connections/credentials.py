# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from typing import Dict

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2023_04_01_preview.models import ConnectionAuthType
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._credentials import (
    ManagedIdentityConfiguration,
    PatTokenConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
    UsernamePasswordConfiguration,
    AccessKeyConfiguration,
)


class WorkspaceCredentialsSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str()


class PatTokenConfigurationSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=ConnectionAuthType.PAT,
        casing_transform=camel_to_snake,
        required=True,
    )
    pat = fields.Str()

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> PatTokenConfiguration:
        data.pop("type")
        return PatTokenConfiguration(**data)


class SasTokenConfigurationSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=ConnectionAuthType.SAS,
        casing_transform=camel_to_snake,
        required=True,
    )
    pat = fields.Str()

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> SasTokenConfiguration:
        data.pop("type")
        return SasTokenConfiguration(**data)


class UsernamePasswordConfigurationSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=ConnectionAuthType.USERNAME_PASSWORD,
        casing_transform=camel_to_snake,
        required=True,
    )
    username = fields.Str()
    password = fields.Str()

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> UsernamePasswordConfiguration:
        data.pop("type")
        return UsernamePasswordConfiguration(**data)


class ManagedIdentityConfigurationSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=ConnectionAuthType.MANAGED_IDENTITY,
        casing_transform=camel_to_snake,
        required=True,
    )
    client_id = fields.Str()
    resource_id = fields.Str()

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> ManagedIdentityConfiguration:
        data.pop("type")
        return ManagedIdentityConfiguration(**data)


class ServicePrincipalConfigurationSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=ConnectionAuthType.SERVICE_PRINCIPAL,
        casing_transform=camel_to_snake,
        required=True,
    )

    client_id = fields.Str()
    client_secret = fields.Str()
    tenant_id = fields.Str()

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> ServicePrincipalConfiguration:
        data.pop("type")
        return ServicePrincipalConfiguration(**data)


class AccessKeyConfigurationSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=ConnectionAuthType.ACCESS_KEY,
        casing_transform=camel_to_snake,
        required=True,
    )
    access_key_id = fields.Str()
    secret_access_key = fields.Str()

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> AccessKeyConfiguration:
        data.pop("type")
        return AccessKeyConfiguration(**data)
