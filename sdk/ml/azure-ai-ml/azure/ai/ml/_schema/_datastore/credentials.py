# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from typing import Any, Dict

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml.entities._datastore.credentials import (
    AccountKeyCredentials,
    CertificateCredentials,
    NoneCredentials,
    SasTokenCredentials,
    ServicePrincipalCredentials,
)


class NoneCredentialsSchema(metaclass=PatchedSchemaMeta):
    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> NoneCredentials:
        return NoneCredentials(**data)


class AccountKeySchema(metaclass=PatchedSchemaMeta):
    account_key = fields.Str(required=True)

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> AccountKeyCredentials:
        return AccountKeyCredentials(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._datastore.credentials import AccountKeyCredentials

        if not isinstance(data, AccountKeyCredentials):
            raise ValidationError("Cannot dump non-AccountKeyCredentials object into AccountKeyCredentials")
        return data


class SasTokenSchema(metaclass=PatchedSchemaMeta):
    sas_token = fields.Str(required=True)

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> SasTokenCredentials:
        return SasTokenCredentials(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._datastore.credentials import SasTokenCredentials

        if not isinstance(data, SasTokenCredentials):
            raise ValidationError("Cannot dump non-SasTokenCredentials object into SasTokenCredentials")
        return data


class BaseTenantCredentialSchema(metaclass=PatchedSchemaMeta):
    authority_url = fields.Str(data_key="authority_uri")
    resource_url = fields.Str()
    tenant_id = fields.Str(required=True)
    client_id = fields.Str(required=True)


class ServicePrincipalSchema(BaseTenantCredentialSchema):
    client_secret = fields.Str(required=True)

    @post_load
    def make(self, data: Dict[str, str], **kwargs) -> ServicePrincipalCredentials:
        return ServicePrincipalCredentials(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._datastore.credentials import ServicePrincipalCredentials

        if not isinstance(data, ServicePrincipalCredentials):
            raise ValidationError("Cannot dump non-ServicePrincipalCredentials object into ServicePrincipalCredentials")
        return data


class CertificateSchema(BaseTenantCredentialSchema):
    certificate = fields.Str()
    thumbprint = fields.Str(required=True)

    @post_load
    def make(self, data: Dict[str, Any], **kwargs) -> CertificateCredentials:
        return CertificateCredentials(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._datastore.credentials import CertificateCredentials

        if not isinstance(data, CertificateCredentials):
            raise ValidationError("Cannot dump non-CertificateCredentials object into CertificateCredentials")
        return data
