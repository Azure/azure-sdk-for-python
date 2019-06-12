# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict, Mapping, Optional, Iterator, List
from datetime import datetime
from .._generated.v7_0 import models
from .._internal import _KeyVaultClientBase
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


class CertificateClient(_KeyVaultClientBase):

    def create_certificate(self, name, policy, enabled=None, not_before=None, expires=None, tags=None, **kwargs):
        # type: (str, models.CertificatePolicy, Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> CertificateOperation
        pass

    def get_certificate(self, name, version=None, **kwargs):
        # type: (str, Optional[str], Mapping[str, Any]) -> Certificate
        pass

    def delete_certificate(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedCertificate
        pass

    def get_deleted_certificate(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedCertificate
        pass

    def purge_deleted_certificate(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> None
        pass

    def recover_deleted_certificate(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> Certificate
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
        # type: (str, str, Optional[str], Optional[models.CertificatePolicy], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Certificate
        pass

    def get_certificate_policy(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> CertificatePolicy
        pass

    def update_certificate_policy(self, name, policy, enabled=None, not_before=None, expires=None, tags=None, **kwargs):
        # type: (str, models.CertificatePolicy, Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> CertificatePolicy
        pass

    def update_certificate(self, name, version, not_before=None, expires=None, enabled=None, tags=None, **kwargs):
        # type: (str, str, Optional[datetime], Optional[datetime], Optional[bool], Optional[Dict[str, str]], Mapping[str, Any]) -> Certificate
        pass

    def merge_certificate(
        self, name, x509_certificates, enabled=True, not_before=None, expires=None, tags=None, **kwargs
    ):
        # type: (str, List[str], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Certificate
        pass

    def backup_certificate(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> bytes
        pass

    def restore_certificate(self, backup, **kwargs):
        # type: (bytes, Mapping[str, Any]) -> Certificate
        pass

    def list_deleted_certificates(self, include_pending=None, **kwargs):
        # type: (Optional[bool], Mapping[str, Any]) -> Iterator[DeletedCertificate]
        pass

    def list_certificates(self, include_pending=None, **kwargs):
        # type: (Optional[bool], Mapping[str, Any]) -> Iterator[CertificateBase]
        pass

    def list_certificate_versions(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> Iterator[CertificateBase]
        pass

    def create_contacts(self, contacts, **kwargs):
        # type: (Iterator[Contact], Mapping[str, Any]) -> Iterator[Contact]
        # TODO: rest api includes an id should it be returned?
        pass

    def list_contacts(self, **kwargs):
        # type: (Mapping[str, Any]) -> Iterator[Contact]
        pass

    def delete_contacts(self, **kwargs):
        # type: (Mapping[str, Any]) -> Iterator[Contact]
        pass

    def get_certificate_operation(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> CertificateOperation
        pass

    def delete_certificate_operation(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> CertificateOperation
        pass

    def cancel_certificate_operation(self, name, cancellation_requested, **kwargs):
        # type: (str, bool, Mapping[str, Any]) -> CertificateOperation
        pass

    def get_pending_certificate_signing_request(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> str
        pass

    def get_issuer(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> Issuer
        pass

    def create_issuer(
        self,
        name,
        provider,
        account_id=None,
        password=None,
        organization_id=None,
        admin_details=None,
        enabled=None,
        not_before=None,
        expires=None,
        tags=None,
        **kwargs
    ):
        # type: (str, str, Optional[str], Optional[str], Optional[str], Optional[List[models.AdministratorDetails]], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Issuer
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
        # type: (str, Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Issuer
        pass

    def delete_issuer(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> Issuer
        pass

    def list_issuers(self, **kwargs):
        # type: (Mapping[str, Any]) -> Iterator[IssuerBase]
        pass
