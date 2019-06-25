# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime
from typing import Any, Dict, Mapping, Optional, List
from .._internal import _parse_vault_id
from .._generated.v7_0 import models


class AdministratorDetails(object):
    """Details of the organization administrator of the certificate issuer.
    :param first_name: First name.
    :type first_name: str
    :param last_name: Last name.
    :type last_name: str
    :param email: Email address.
    :type email: str
    :param phone: Phone number.
    :type phone: str
    """

    def __init__(self, first_name=None, last_name=None, email=None, phone=None):
        # type: (Optional[str], Optional[str], Optional[str], Optional[str]) -> None
        self._first_name = first_name
        self._last_name = last_name
        self._phone = phone
        self._email = email

    @classmethod
    def _from_admin_details_bundle(cls, admin_details_bundle):
        # type: (models.AdministratorDetails) -> AdministratorDetails
        """Construct a AdministratorDetails from an autorest-generated AdministratorDetailsBundle"""
        return cls(
            email=admin_details_bundle.email_address,
            first_name=admin_details_bundle.first_name,
            last_name=admin_details_bundle.last_name,
            phone=admin_details_bundle.phone,
        )

    @property
    def email(self):
        # type: () -> str
        return self._email

    @property
    def first_name(self):
        # type: () -> str
        return self._first_name

    @property
    def last_name(self):
        # type: () -> str
        return self._last_name

    @property
    def phone(self):
        # type: () -> str
        return self._phone


class Error(object):
    """The key vault server error."""

    def __init__(self, code=None, message=None, inner_error=None):
        # type: (Optional[str], Optional[str], Optional[models.Error]) -> None
        self._code = code
        self._message = message
        self._inner_error = inner_error

    @property
    def code(self):
        # type: () -> str
        return self._code

    @property
    def message(self):
        # type: () -> str
        return self._message

    @property
    def inner_error(self):
        # type: () -> models.Error
        return self._inner_error


class CertificateBase(object):
    def __init__(self, attributes, cert_id, thumbprint, **kwargs):
        # type: (models.CertificateAttributes, str, bytes, Mapping[str, Any]) -> None
        self._attributes = attributes
        self._id = cert_id
        self._vault_id = _parse_vault_id(cert_id)
        self._thumbprint = thumbprint
        self._tags = kwargs.get("tags", None)

    @classmethod
    def _from_certificate_item(cls, certificate_item):
        # type: (models.CertificateItem) -> Certificate
        """Construct a Certificate from an autorest-generated CertificateItem"""
        return cls(
            attributes=certificate_item.attributes,
            cert_id=certificate_item.id,
            thumbprint=certificate_item.x509_thumbprint,
            tags=certificate_item.tags,
        )

    @property
    def id(self):
        # type: () -> str
        pass

    @property
    def name(self):
        # type: () -> str
        return self._vault_id.name

    @property
    def thumbprint(self):
        # type: () -> bytes
        return self._thumbprint

    @property
    def enabled(self):
        # type: () -> bool
        return self._attributes.enabled

    @property
    def not_before(self):
        # type: () -> datetime
        return self._attributes.not_before

    @property
    def expires(self):
        # type: () -> datetime
        return self._attributes.expires

    @property
    def created(self):
        # type: () -> datetime
        return self._attributes.created

    @property
    def updated(self):
        # type: () -> datetime
        return self._attributes.updated

    @property
    def recovery_level(self):
        # type: () -> str
        return self._attributes.recovery_level

    @property
    def vault_url(self):
        # type: () -> str
        return self._vault_id.vault_url

    @property
    def tags(self):
        # type: () -> Dict[str, str]
        return self._tags


class Certificate(CertificateBase):
    def __init__(self, attributes, cert_id, thumbprint, kid, sid, policy, cer, **kwargs):
        # type: (models.CertificateAttributes, str, bytes, str, str, CertificatePolicy, bytes, Mapping[str, Any]) -> None
        super(Certificate, self).__init__(attributes, cert_id, thumbprint, **kwargs)
        self._kid = kid
        self._sid = sid
        self._policy = policy
        self._cer = cer

    @classmethod
    def _from_certificate_bundle(cls, certificate_bundle):
        # type: (models.CertificateBundle) -> Certificate
        """Construct a Certificate from an autorest-generated CertificateBundle"""
        return cls(
            attributes=certificate_bundle.attributes,
            cert_id=certificate_bundle.id,
            thumbprint=certificate_bundle.x509_thumbprint,
            kid=certificate_bundle.kid,
            sid=certificate_bundle.sid,
            policy=CertificatePolicy._from_certificate_policy_bundle(certificate_bundle.policy),
            cer=certificate_bundle.cer,
            tags=certificate_bundle.tags,
        )

    @property
    def kid(self):
        # type: () -> str
        return self._kid

    @property
    def sid(self):
        # type: () -> str
        return self._sid

    @property
    def policy(self):
        # type: () -> models.CertificatePolicy
        return self._policy

    @property
    def cer(self):
        # type: () -> bytes
        return self._cer


class CertificateOperation(object):
    """A certificate operation is returned in case of asynchronous requests. """

    def __init__(
        self,
        cert_operation_id,
        issuer_name,
        certificate_type,
        certificate_transparency,
        csr,
        cancellation_requested,
        status,
        status_details,
        error,
        target,
        request_id,
        **kwargs,
    ):
        # type: (str, str, str, bool, str, bool, str, str, models.Error, str, str, Mapping[str, Any]) -> None
        pass

    @property
    def id(self):
        # type: () -> str
        pass

    @property
    def issuer_name(self):
        # type: () -> str
        pass

    @property
    def certificate_type(self):
        # type: () -> str
        pass

    @property
    def certificate_transparency(self):
        # type: () -> bool
        pass

    @property
    def csr(self):
        # type: () -> str
        pass

    @property
    def cancellation_requested(self):
        # type: () -> bool
        pass

    @property
    def status(self):
        # type: () -> str
        pass

    @property
    def status_details(self):
        # type: () -> str
        pass

    @property
    def error(self):
        # type: () -> models.Error
        pass

    @property
    def target(self):
        # type: () -> str
        pass

    @property
    def request_id(self):
        # type: () -> str
        pass


class CertificatePolicy(object):
    """Management policy for a certificate."""

    def __init__(
        self,
        cert_policy_id,
        key_properties,
        content_type,
        subject_name,
        subject_alternative_emails,
        subject_alternative_dns_names,
        subject_alternative_upns,
        validity_in_months,
        lifetime_actions,
        issuer_name,
        certificate_type,
        certificate_transparency,
        **kwargs,
    ):
        # type: (str, models.KeyProperties, str, str, list[str], list[str], list[str], int, list[models.LifetimeAction], str, str, bool, Mapping[str, Any]) -> None
        pass

    @classmethod
    def _from_certificate_policy_bundle(cls, certificate_policy_bundle):
        # type: (models.CertificatePolicy) -> CertificatePolicy
        """Construct a CertificatePolicy from an autorest-generated CertificatePolicy bundle"""
        pass

    @property
    def id(self):
        # type: () -> str
        pass

    @property
    def name(self):
        # type: () -> str
        pass

    @property
    def content_type(self):
        # type: () -> str
        pass

    @property
    def subject_name(self):
        # type: () -> str
        pass

    @property
    def subject_alternative_emails(self):
        # type: () -> list[str]
        pass

    @property
    def subject_alternative_dns_names(self):
        # type: () -> list[str]
        pass

    @property
    def subject_alternative_upns(self):
        # type: () -> list[str]
        pass

    @property
    def validity_in_months(self):
        # type: () -> int
        pass

    @property
    def lifetime_actions(self):
        pass

    @property
    def issuer_name(self):
        # type: () -> str
        pass

    @property
    def certificate_type(self):
        # type: () -> str
        pass

    @property
    def certificate_transparency(self):
        # type: () -> bool
        pass

    @property
    def created(self):
        # type: () -> datetime
        pass

    @property
    def enabled(self):
        # type: () -> bool
        pass

    @property
    def updated(self):
        # type: () -> datetime
        pass


class Contact:
    """The contact information for the vault certificates.
    """

    def __init__(self, email, name, phone):
        # type: (str, str, str) -> None
        self._email = email
        self._name = name
        self._phone = phone

    @property
    def email(self):
        # type: () -> str
        return self._email

    @property
    def name(self):
        # type: () -> str
        return self._name

    @property
    def phone(self):
        # type: () -> str
        return self._phone


class IssuerBase(object):
    def __init__(self, issuer_id, provider, attributes=None):
        # type: (str, str, Optional[models.IssuerAttributes]) -> None
        self._attributes = attributes
        self._id = issuer_id
        self._vault_id = _parse_vault_id(issuer_id)
        self._provider = provider

    @classmethod
    def _from_issuer_item(cls, issuer_item):
        # type: (models.CertificateIssuerItem) -> IssuerBase
        """Construct a IssuerBase from an autorest-generated IssuerItem"""
        return cls(issuer_id=issuer_item.id, provider=issuer_item.provider)

    @property
    def enabled(self):
        # type: () -> bool
        return self._attributes.enabled

    @property
    def created(self):
        # type: () -> datetime
        return self._attributes.created

    @property
    def updated(self):
        # type: () -> datetime
        return self._attributes.updated

    @property
    def id(self):
        # type: () -> str
        return self._id

    @property
    def name(self):
        # type: () -> str
        return self._vault_id.name

    @property
    def provider(self):
        # type: () -> str
        return self._provider

    @property
    def vault_url(self):
        # type: () -> str
        return self._vault_id.vault_url


class Issuer(IssuerBase):
    def __init__(self, attributes, issuer_id, provider=None, account_id=None, password=None, organization_id=None, admin_details=None):
        # type: (models.IssuerAttributes, str, Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[List[AdministratorDetails]]) -> None
        super(Issuer, self).__init__(attributes, issuer_id, provider)
        self._account_id = account_id
        self._password = password
        self._organization_id = organization_id
        self._admin_details = admin_details

    @classmethod
    def _from_issuer_bundle(cls, issuer_bundle):
        # type: (models.IssuerBundle) -> Issuer
        """Construct a Issuer from an autorest-generated IssuerBundle"""
        return cls(
            attributes=issuer_bundle.attributes,
            issuer_id=issuer_bundle.id,
            provider=issuer_bundle.provider,
            account_id=issuer_bundle.credentials.account_id,
            password=issuer_bundle.credentials.password,
            organization_id=issuer_bundle.organization_details.id,
            admin_details=[
                AdministratorDetails._from_admin_details_bundle(item)
                for item in issuer_bundle.organization_details.admin_details
            ],
        )

    @property
    def account_id(self):
        # type: () -> str
        return self._account_id

    @property
    def password(self):
        # type: () -> str
        return self._password

    @property
    def organization_id(self):
        # type: () -> str
        return self._organization_id

    @property
    def admin_details(self):
        # type: () -> List[AdministratorDetails]
        return self._admin_details


class KeyProperties(object):
    def __init__(self, exportable, key_type, key_size, reuse_key, curve, ekus, key_usage):
        # type: (bool, str, int, bool, str, list[str], list[str]) -> None
        self._exportable = exportable
        self._key_type = key_type
        self._key_size = key_size
        self._reuse_key = reuse_key
        self._curve = curve
        self._ekus = ekus
        self._key_usage = key_usage

    @property
    def exportable(self):
        return self._exportable

    @property
    def key_type(self):
        return self._key_type

    @property
    def key_size(self):
        return self._key_size

    @property
    def curve(self):
        return self._curve

    @property
    def ekus(self):
        return self._ekus

    @property
    def key_usage(self):
        return self._key_usage


class LifetimeAction(object):
    """Action and its trigger that will be performed by certificate Vault over the
    lifetime of a certificate.
    """

    def __init__(self, action_type, lifetime_percentage=None, days_before_expiry=None):
        # type: (models.ActionType, Optional[int], Optional[int]) -> None
        self._lifetime_percentage = lifetime_percentage
        self._days_before_expiry = days_before_expiry
        self._action_type = action_type

    @property
    def lifetime_percentage(self):
        # type: () -> int
        return self._lifetime_percentage

    @property
    def days_before_expiry(self):
        # type: () -> int
        return self._days_before_expiry

    @property
    def action_type(self):
        # type: () -> models.ActionType
        return self._action_type


class DeletedCertificate(Certificate):
    """A Deleted Certificate consisting of its previous id, attributes and its
    tags, as well as information on when it will be purged."""

    def __init__(
        self,
        attributes,
        cert_id,
        thumbprint,
        kid=None,
        sid=None,
        policy=None,
        cer=None,
        deleted_date=None,
        recovery_id=None,
        scheduled_purge_date=None,
        **kwargs,
    ):
        # type: (models.CertificateAttributes, str, bytes, Optional[str], Optional[str], Optional[models.CertificatePolicy], Optional[bytes], Optional[datetime], Optional[str], Optional[datetime], Mapping[str, Any]) -> None
        super(DeletedCertificate, self).__init__(attributes, cert_id, thumbprint, kid, sid, policy, cer, **kwargs)
        self._deleted_date = deleted_date
        self._recovery_id = recovery_id
        self._scheduled_purge_date = scheduled_purge_date

    @classmethod
    def _from_deleted_certificate_item(cls, deleted_certificate_item):
        # type: (models.DeletedCertificateItem) -> DeletedCertificate
        """Construct a DeletedCertificate from an autorest-generated DeletedCertificateItem"""
        return cls(
            attributes=deleted_certificate_item.attributes,
            cert_id=deleted_certificate_item.id,
            thumbprint=deleted_certificate_item.x509_thumbprint,
            recovery_id=deleted_certificate_item.recovery_id,
            scheduled_purge_date=deleted_certificate_item.scheduled_purge_date,
            tags=deleted_certificate_item.tags,
        )

    @property
    def deleted_date(self):
        # type: () -> datetime
        return self._deleted_date

    @property
    def recovery_id(self):
        # type: () -> str
        return self._recovery_id

    @property
    def scheduled_purge_date(self):
        # type: () -> datetime
        return self._scheduled_purge_date
