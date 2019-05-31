# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict, Mapping, Optional
from datetime import datetime

from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport
from azure.security.keyvault._internal import _BearerTokenCredentialPolicy

from .._generated import KeyVaultClient
from ._models import (
    Certificate,
    CertificateBase,
    DeletedCertificate,
    CertificatePolicy,
    Issuer,
    IssuerBase,
    Contact,
    CertificateOperation,
)


class CertificateClient:
    @staticmethod
    def create_config(**kwargs):
        pass  # TODO

    def __init__(self, vault_url, credentials, config=None, api_version=None, **kwargs):
        if not credentials:
            raise ValueError("credentials")

        if not vault_url:
            raise ValueError("vault_url")

        self._vault_url = vault_url

        if api_version is None:
            api_version = KeyVaultClient.DEFAULT_API_VERSION

        config = config or KeyVaultClient.get_configuration_class(api_version)(credentials)

        # TODO generated default pipeline should be fine when token policy isn't necessary
        policies = [
            config.headers_policy,
            config.user_agent_policy,
            config.proxy_policy,
            _BearerTokenCredentialPolicy(credentials),
            config.redirect_policy,
            config.retry_policy,
            config.logging_policy,
        ]
        transport = RequestsTransport(config)
        pipeline = Pipeline(transport, policies=policies)

        self._client = KeyVaultClient(credentials, api_version=api_version, pipeline=pipeline)

    @property
    def vault_url(self):
        # type: () -> str
        return self._vault_url

    def create_certificate(self, name, policy=None, enabled=None, not_before=None, expires=None, tags=None, **kwargs):
        # type: (str, Optional[CertificatePolicy], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Mapping[str, Any]]) -> CertificateOperation
        pass

    def get_certificate(self, name, version=None, **kwargs):
        # type: (str, Optional[str]) -> Certificate
        pass

    def delete_certificate(self, name, **kwargs):
        # type: (str) -> DeletedCertificate
        pass

    def get_deleted_certificate(self, name, **kwargs):
        # type: (str) -> DeletedCertificate
        pass

    def purge_deleted_certificate(self, name, **kwargs):
        # type: (str) -> None
        pass

    def recover_deleted_certificate(self, name, **kwargs):
        # type: (str) -> Certificate
        pass

    def import_certificate(
        self,
        name,
        base64_encoded_certificate,
        password=None,
        policy=None,
        enabled=None,
        not_before=None,
        expires=None,
        tags=None,
        **kwargs
    ):
        # type: (str, str, Optional[str], Optional[Policy], Optional[bool],Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Certificate
        pass

    def get_certificate_policy(self, name, **kwargs):
        # type: (str) -> CertificatePolicy
        pass

    def update_certificate_policy(self, name, policy, enabled=None, not_before=None, expires=None, tags=None, **kwargs):
        # type: (str, CertificatePolicy) -> CertificatePolicy
        pass

    def update_certificate(self, name, version, not_before=None, expires=None, enabled=None, tags=None, **kwargs):
        # type: (str, str, Optional[bool], Optional[Dict[str, str]]) -> Certificate
        pass

    def merge_certificate(
        self, name, x509_certificates, enabled=True, not_before=None, expires=None, tags=None, **kwargs
    ):
        # type: (str, list[str], Optional[bool], Optional[Dict[str, str]]) -> Certificate
        pass

    def backup_certificate(self, name, **kwargs):
        # type: (str) -> bytes
        pass

    def restore_certificate(self, backup, **kwargs):
        # type: (bytes) -> Certificate
        pass

    def list_deleted_certificates(self, include_pending=None, **kwargs):
        # type: (Optional[bool]) -> Iterable[DeletedCertificate]
        pass

    def list_certificates(self, include_pending=None, **kwargs):
        # type: (Optional[bool]) -> Iterable[CertificateBase]
        pass

    def list_certificate_versions(self, name, **kwargs):
        # type: (str) -> Iterable[CertificateBase]
        pass

    def create_contacts(self, contacts, **kwargs):
        # type: (Iterable[Contact]) -> Iterable[Contact]
        # TODO: rest api includes an id should it be returned?
        pass

    def list_contacts(self, **kwargs):
        # type: () -> Iterable[Contact]
        pass

    def delete_contacts(self, **kwargs):
        # type: () -> Iterable[Contact]
        pass

    def get_certificate_operation(self, name, **kwargs):
        # type: (str) -> CertificateOperation
        pass

    def delete_certificate_operation(self, name, **kwargs):
        # type: (str) -> CertificateOperation
        pass

    def cancel_certificate_operation(self, name, **kwargs):
        # type: (str) -> CertificateOperation
        pass

    def get_pending_certificate_signing_request(self, name, **kwargs):
        # type: (str) -> str
        pass

    def get_issuer(self, name, **kwargs):
        # type: (str) -> Issuer
        pass

    #   TODO: params first_name, last_name, email, phone may change on how we want to handle admin_details
    def create_issuer(
        self,
        name,
        provider,
        account_id=None,
        password=None,
        organization_id=None,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        enabled=None,
        not_before=None,
        expires=None,
        tags=None,
        **kwargs
    ):
        # type: (str, str, Optional[str], Optional[str], Optional[organization_id], Optional[str], Optional[str], Optional[str], Optional[str], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Issuer
        pass

    def update_issuer(
        self,
        name,
        provider=None,
        account_id=None,
        password=None,
        organization_id=None,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        enabled=True,
        not_before=None,
        expires=None,
        tags=None,
        **kwargs
    ):
        # type: (str, Optional[str], Optional[str], Optional[str], Optional[organization_id], Optional[str], Optional[str], Optional[str], Optional[str], Optional[bool], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Issuer
        pass

    def delete_issuer(self, name, **kwargs):
        # type: (str) -> Issuer
        pass

    def list_issuers(self, **kwargs):
        # type: () -> Iterable[IssuerBase]
        pass
