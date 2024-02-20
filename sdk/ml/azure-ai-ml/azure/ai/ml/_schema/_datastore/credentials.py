# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Any, Dict

from marshmallow import ValidationError, fields, post_load, pre_dump, pre_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml.entities._credentials import (
    AccountKeyConfiguration,
    CertificateConfiguration,
    NoneCredentialConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
)


class NoneCredentialsSchema(metaclass=PatchedSchemaMeta):
    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> NoneCredentialConfiguration:
        return NoneCredentialConfiguration(**data)


class AccountKeySchema(metaclass=PatchedSchemaMeta):
    account_key = fields.Str(required=True)

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> AccountKeyConfiguration:
        return AccountKeyConfiguration(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        if not isinstance(data, AccountKeyConfiguration):
            raise ValidationError("Cannot dump non-AccountKeyCredentials object into AccountKeyCredentials")
        return data


class SasTokenSchema(metaclass=PatchedSchemaMeta):
    sas_token = fields.Str(required=True)

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> SasTokenConfiguration:
        return SasTokenConfiguration(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        if not isinstance(data, SasTokenConfiguration):
            raise ValidationError("Cannot dump non-SasTokenCredentials object into SasTokenCredentials")
        return data


class BaseTenantCredentialSchema(metaclass=PatchedSchemaMeta):
    authority_url = fields.Str()
    resource_url = fields.Str()
    tenant_id = fields.Str(required=True)
    client_id = fields.Str(required=True)

    @pre_load
    def accept_backward_compatible_keys(self, data, **kwargs):
        acceptable_keys = [key for key in data.keys() if key in ("authority_url", "authority_uri")]
        if len(acceptable_keys) > 1:
            raise ValidationError(
                "Cannot specify both 'authority_url' and 'authority_uri'. Please use 'authority_url'."
            )
        if acceptable_keys:
            data["authority_url"] = data.pop(acceptable_keys[0])
        return data


class ServicePrincipalSchema(BaseTenantCredentialSchema):
    client_secret = fields.Str(required=True)

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> ServicePrincipalConfiguration:
        return ServicePrincipalConfiguration(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        if not isinstance(data, ServicePrincipalConfiguration):
            raise ValidationError("Cannot dump non-ServicePrincipalCredentials object into ServicePrincipalCredentials")
        return data


class CertificateSchema(BaseTenantCredentialSchema):
    certificate = fields.Str()
    thumbprint = fields.Str(required=True)

    @post_load
    def make(self, data: Dict[str, Any], **kwargs) -> CertificateConfiguration:
        return CertificateConfiguration(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        if not isinstance(data, CertificateConfiguration):
            raise ValidationError("Cannot dump non-CertificateCredentials object into CertificateCredentials")
        return data
