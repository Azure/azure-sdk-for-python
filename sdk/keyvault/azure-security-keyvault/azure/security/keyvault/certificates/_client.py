# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict, Generator, Mapping, Optional
from datetime import datetime

from azure.core import Configuration
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import RetryPolicy, RedirectPolicy, UserAgentPolicy
from azure.core.pipeline.transport import RequestsTransport
from azure.security.keyvault._internal import _BearerTokenCredentialPolicy

from .._generated import KeyVaultClient
from ._models import Secret, DeletedSecret, SecretAttributes


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

        self._client = KeyVaultClient(credentials, api_version=self._api_version, pipeline=pipeline)

    @property
    def vault_url(self):
        # type: () -> str
        return self._vault_url

    def create_certificate(name, policy=None, enabled=None, not_before=None, expires=None, tags=None, **kwargs):
        # type: (str, Optional[CertificatePolicy], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> CertificateOperation
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.CertificateAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None
        bundle = self._client.create_certificate(name, certificate_policy=policy, certificate_attributes=attributes, tags=None, **kwargs)
        return bundle

    def get_certificate(self, name, version=None):
        # type: (str, Optional[str]) -> Certificate
        bundle = self._client.get_certificate(self._vault_url, name, version, error_map={404: ResourceNotFoundError})
        return bundle

    def delete_certificate(self, name, **kwargs):
        # type: (str) -> Certificate
        bundle = self._client.delete_certificate(name)
        return bundle

    def get_deleted_certificate(self, name, **kwargs):
        # type: (str) -> Certificate
        bundle = self._client.get_deleted_certificate(name)
        return bundle

    def purge_deleted_certificate(self, name, **kwargs):
        # type: (str) -> None
        bundle = self._client.purge_deleted_certificate(name)
        pass

    def recover_deleted_certificate(self, name, **kwargs):
        # type: (str) -> Certificate
        pass

    def import_certificate(self, name, base64_encoded_certificate, policy=None, enabled=None, password=None, not_before=None, expires=None, tags=None, **kwargs):
        # type: (str, str, Optional[str], Optional[Policy], Optional[bool], Optional[Dict[str, str]]) -> Certificate
        pass

    def get_certificate_policy(self, name, policy):
        # type: (str) -> CertificatePolicy
        pass

    def update_certificate_policy(self, name, policy):
        # type: (str, CertificatePolicy) -> CertificatePolicy
        # TODO: does the new policy affect the most recent cert or take effect at next issue?
        pass

    def update_certificate(self, name, version, policy=None, enabled=None, tags=None):
        # type: (str, str, Optional[Policy], Optional[bool], Optional[Dict[str, str]]) -> Certificate
        # TODO: does this immediately issue a new cert under the new policy?
        #       why would I change the policy for an old version?
        pass

    def merge_certificate(self, name, x509_certificates, enabled=True, not_before=None, expires=None, tags=None):
        # type: (str, bytes, Optional[bool], Optional[Dict[str, str]]) -> Certificate
        pass

    def backup_certificate(self, name):
        # type: (str) -> bytes
        pass

    def restore_certificate(self, certificate_backup):
        # type: (bytes) -> Certificate
        pass
    
    # What is this include_pending?
    def list_deleted_certificates(self, include_pending=None):
        # type: (Optional[bool]) -> Iterable[CertificateBase]
        pass

    def list_certificates(self, include_pending=None):
        # type: (Optional[bool]) -> Iterable[CertificateBase]
        pass

    def list_certificate_versions(self, name):
        # type: (str) -> Iterable[CertificateBase]
        pass
    
    def get_issuer(self, name):
        # type: (str) -> Issuer
        pass

    def create_issuer(self, name, provider, account_id=None, password=None, organization_id=None, admin_details=None, enabled=None):
        # type: (str, str, Optional[str], Optional[str], Optional[organization_id], , Optional[admin_details], Optional[bool]) -> Issuer
        pass

    def update_issuer(self, name, provider=None, account_id=None, password=None, organization_id=None, admin_details=None, enabled=True):
        # type: (str, Optional[str], Optional[str], Optional[str], Optional[organization_id], , Optional[admin_details], Optional[bool]) -> Issuer
        pass

    def delete_issuer(self, name):
        # type: (str) -> Issuer
        pass

    def list_issuers(self):
        # type: () -> Iterable[IssuerBase]
        pass

    # contacts are vault-wide
    def set_contacts(self, contacts):
        # type: (Iterable[Contact]) -> Iterable[Contact]
        # TODO: rest api includes an id which doesn't look useful for anything; should it be returned anyway?
        pass
    
    def list_contacts(self):
        # type: () -> Iterable[Contact]
        pass

    def delete_contacts(self):
        # type: () -> Iterable[Contact]
        pass
    
    def get_certificate_operation(self, name):
        # type: (str) -> CertificateOperation
        pass

    def delete_certificate_operation(self, name):
        # type: (str) -> Operation
        # TODO: what distinguishes this from canceling an operation?
        pass

    def cancel_certificate_operation(self, name):
        # type: (str) -> Operation
        pass

    # TODO:

    def disable_certificate(self, name):
        # type: (str) -> Certificate
        # wraps update cert
        pass

    def enable_certificate(self, name):
        # type: (str) -> Certificate
        # wraps update cert
        pass


