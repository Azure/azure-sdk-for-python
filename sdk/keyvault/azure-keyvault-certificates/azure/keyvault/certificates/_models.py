# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime
from typing import Any, Dict, Mapping, Optional
from ._internal import _parse_vault_id
from ._generated.v7_0 import models


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

    def __init__(self, first_name, last_name, email, phone):
        # type: (str, str, str, str) -> None
        self._first_name = first_name
        self._last_name = last_name
        self._phone = phone
        self._email = email

    @classmethod
    def _from_admin_details_bundle(cls, admin_details_bundle):
        # type: (models.IssuerBundle) -> Issuer
        """Construct a AdministratorDetails from an autorest-generated AdministratorDetailsBundle"""
        return cls(
            email=admin_details_bundle.email,
            first_name=admin_details_bundle.first_name,
            last_name=admin_details_bundle.admin_details_bundle.last_name,
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

    def __init__(self, code, message, inner_error):
        # type: (str, str, models.Error, Mapping[str, Any]) -> None
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
        # type: (models.CertificateAttributes, Optional[str], Mapping[str, Any]) -> None
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
        return self._id

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

    @property
    def version(self):
        # type: () -> str
        """The version of the certificate
        :rtype: str"""
        return self._vault_id.version


class Certificate(CertificateBase):
    def __init__(self, attributes, cert_id, thumbprint, kid, sid, policy, cer, **kwargs):
        # type: (models.CertificateAttributes, str, str, str, models.CertificatePolicy, bytes, Mapping[str, Any]) -> None
        super(Certificate, self).__init__(attributes, cert_id, thumbprint, **kwargs)
        self._kid = kid
        self._sid = sid
        self._policy = policy
        self._cer = cer

    @classmethod
    def _from_certificate_bundle(cls, certificate_bundle):
        # type: (models.CertificateBundle) -> Certificate
        """Construct a certificate from an autorest-generated certificateBundle"""
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
    ):
        # type: (str, str, str, str, bool, str, bool, str, str, models.Error, str, str, Mapping[str, Any]) -> None
        self._id = cert_operation_id
        self._vault_id = _parse_vault_id(cert_operation_id)
        self._issuer_name = issuer_name
        self._certificate_type = certificate_type
        self._certificate_transparency = certificate_transparency
        self._csr = csr
        self._cancellation_requested = cancellation_requested
        self._status = status
        self._status_details = status_details
        self._error = error
        self._target = target
        self._request_id = request_id

    @classmethod
    def _from_certificate_operation_bundle(cls, certificate_operation_bundle):
        # type: (models.CertificateOperation) -> CertificateOperation
        """Construct a CertificateOperation from an autorest-generated CertificateOperation"""
        return cls(
            cert_operation_id=certificate_operation_bundle.id,
            issuer_name=certificate_operation_bundle.issuer_parameters.name,
            certificate_type=certificate_operation_bundle.issuer_parameters.certificate_type,
            certificate_transparency=certificate_operation_bundle.issuer_parameters.certificate_transparency,
            csr=certificate_operation_bundle.csr,
            cancellation_requested=certificate_operation_bundle.cancellation_requested,
            status=certificate_operation_bundle.status,
            status_details=certificate_operation_bundle.status_details,
            error=certificate_operation_bundle.error,
            target=certificate_operation_bundle.target,
            request_id=certificate_operation_bundle.request_id,
        )

    @property
    def id(self):
        # type: () -> str
        return self._id

    @property
    def name(self):
        # type: () -> str
        return self._vault_id.name

    @property
    def issuer_name(self):
        # type: () -> str
        return self._issuer_name

    @property
    def certificate_type(self):
        # type: () -> str
        return self._certificate_type

    @property
    def certificate_transparency(self):
        # type: () -> bool
        return self._certificate_transparency

    @property
    def csr(self):
        # type: () -> str
        return self._csr

    @property
    def cancellation_requested(self):
        # type: () -> bool
        return self._cancellation_requested

    @property
    def status(self):
        # type: () -> str
        return self._status

    @property
    def status_details(self):
        # type: () -> str
        return self._status_details

    @property
    def error(self):
        # type: () -> models.Error
        return self._error

    @property
    def target(self):
        # type: () -> str
        return self._target

    @property
    def request_id(self):
        # type: () -> str
        return self._request_id


class CertificatePolicy(object):
    """Management policy for a certificate."""

    def __init__(
        self,
        attributes,
        cert_policy_id,
        key_properties,
        content_type,
        subject_name,
        sans_emails,
        sans_dns_names,
        sans_upns,
        validity_in_months,
        lifetime_actions,
        issuer_name,
        certificate_type,
        certificate_transparency,
    ):
        # type: (models.CertificatePolicy, str, models.KeyProperties, str, str, list[str], list[str], list[str], int, list[models.LifeTimeAction], str, str, bool, Mapping[str, Any]) -> None
        self._attributes = attributes
        self._id = cert_policy_id
        self._key_properties = key_properties
        self._content_type = content_type
        self._subject_name = subject_name
        self._sans_emails = sans_emails
        self._sans_dns_names = sans_dns_names
        self._sans_upns = sans_upns
        self._validity_in_months = validity_in_months
        self._lifetime_actions = lifetime_actions
        self._issuer_name = issuer_name
        self._certificate_type = certificate_type
        self._certificate_transparency = certificate_transparency

    @classmethod
    def _from_certificate_policy_bundle(cls, certificate_policy_bundle):
        # type: (models.CertificatePolicy) -> CertificatePolicy
        """Construct a CertificatePolicy from an autorest-generated CertificatePolicy"""
        return cls(
            attributes=certificate_policy_bundle.attributes,
            cert_policy_id=certificate_policy_bundle.id,
            issuer_name=certificate_policy_bundle.issuer_parameters.name,
            certificate_type=certificate_policy_bundle.issuer_parameters.certificate_type,
            certificate_transparency=certificate_policy_bundle.issuer_parameters.certificate_transparency,
            lifetime_actions=[
                LifetimeAction(
                    action_type=item.action.action_type,
                    lifetime_percentage=item.trigger.lifetime_percentage or None,
                    days_before_expiry=item.trigger.days_before_expiry or None,
                )
                for item in certificate_policy_bundle.lifetime_actions
            ],
            subject_name=certificate_policy_bundle.x509_certificate_properties.subject,
            sans_emails=certificate_policy_bundle.x509_certificate_properties.subject_alternative_names.emails,
            sans_upns=certificate_policy_bundle.x509_certificate_properties.subject_alternative_names.upns,
            sans_dns_names=certificate_policy_bundle.x509_certificate_properties.subject_alternative_names.dns_names,
            validity_in_months=certificate_policy_bundle.x509_certificate_properties.validity_in_months,
            key_properties=KeyProperties(
                exportable=certificate_policy_bundle.key_properties.exportable,
                key_type=certificate_policy_bundle.key_properties.key_type,
                key_size=certificate_policy_bundle.key_properties.key_size,
                reuse_key=certificate_policy_bundle.key_properties.reuse_key,
                curve=certificate_policy_bundle.key_properties.curve,
                ekus=certificate_policy_bundle.x509_certificate_properties.ekus,
                key_usage=certificate_policy_bundle.x509_certificate_properties.key_usage,
            ),
            content_type=certificate_policy_bundle.secret_properties.content_type,
        )

    @property
    def id(self):
        # type: () -> str
        return self._id

    @property
    def key_properties(self):
        # type: () -> models.KeyProperties
        return self._key_properties

    @property
    def content_type(self):
        # type: () -> str
        return self._content_type

    @property
    def subject_name(self):
        # type: () -> str
        return self._subject_name

    @property
    def sans_emails(self):
        # type: () -> list[str]
        return self._sans_emails

    @property
    def sans_dns_names(self):
        # type: () -> list[str]
        return self._sans_dns_names

    @property
    def sans_upns(self):
        # type: () -> list[str]
        return self._sans_upns

    @property
    def validity_in_months(self):
        # type: () -> int
        return self._validity_in_months

    @property
    def lifetime_actions(self):
        return self._lifetime_actions  # need to spread this out?

    @property
    def issuer_name(self):
        # type: () -> str
        return self._issuer_name

    @property
    def certificate_type(self):
        # type: () -> str
        return self._certificate_type

    @property
    def certificate_transparency(self):
        # type: () -> bool
        return self._certificate_transparency

    @property
    def created(self):
        # type: () -> bool
        return self._attributes.created

    @property
    def updated(self):
        # type: () -> bool
        return self._attributes.updated

    @property
    def enabled(self):
        # type: () -> bool
        return self._attributes.enabled


class Contact:
    """The contact information for the vault certificates.
    """

    def __init__(self, email, name, phone):
        # type: (str, str, str) -> None
        self._email = email
        self._name = name
        self._phone = phone

    @classmethod
    def _from_certificate_contacts_item(cls, contact_item):
        # type: (list[models.Contact]) -> Contact
        """Construct a Contact from an autorest-generated ContactItem"""
        return cls(email=contact_item.email, name=contact_item.name, phone=contact_item.phone)

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
    def __init__(self, attributes, issuer_id, provider):
        # type: (models.IssuerAttributes, str, str) -> None
        self._attributes = attributes
        self._id = issuer_id
        self._vault_id = _parse_vault_id(issuer_id)
        self._provider = provider

    @classmethod
    def _from_issuer_item(cls, issuer_item):
        # type: (models.IssuerItem) -> IssuerBase
        """Construct a IssuerBase from an autorest-generated IssuerItem"""
        return cls(attributes=issuer_item.attributes, issuer_id=issuer_item.id, provider=issuer_item.provider)

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
    def __init__(
        self, attributes, issuer_id, provider, account_id, password, organization_id=None, admin_details=None, **kwargs
    ):
        # type: (models.IssuerAttributes, str, str, str, str, Optional[str], Optional[List[[str]], Mapping[str, Any]) -> None
        super(Issuer, self).__init__(attributes, issuer_id, provider, admin_details, **kwargs)
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
            account_id=issuer_bundle.account_id,
            password=issuer_bundle.password,
            organization_id=issuer_bundle.organization_details.id,
            admin_details=[AdministratorDetails._from_admin_details_bundle(item) for item in issuer_bundle],
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
        # type: () -> str
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
    def reuse_key(self):
        return self._reuse_key

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
        # type: (int, int, models.ActionType) -> None
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
        **kwargs
    ):
        # type: (models.CertificateAttributes, str, Optional[str], Optional[str], Optional[str], Optional[models.CertificatePolicy], Optional[bytes], optional[datetime], Optional[str], Optional[datetime], Mapping[str, Mapping[str, Any]) -> None
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
            kid=None,
            sid=None,
            policy=None,
            cer=None,
            recovery_id=deleted_certificate_item.recovery_id,
            scheduled_purge_date=deleted_certificate_item.scheduled_purge_date,
            tags=deleted_certificate_item.tags,
        )

    @classmethod
    def _from_deleted_certificate_bundle(cls, deleted_certificate_bundle):
        # type: (models.DeletedCertificateBundle) -> DeletedCertificate
        """Construct a DeletedCertificate from an autorest-generated DeletedCertificateItem"""
        return cls(
            attributes=deleted_certificate_bundle.attributes,
            cert_id=deleted_certificate_bundle.id,
            thumbprint=deleted_certificate_bundle.x509_thumbprint,
            kid=deleted_certificate_bundle.kid,
            sid=deleted_certificate_bundle.sid,
            policy=CertificatePolicy._from_certificate_policy_bundle(deleted_certificate_bundle.policy),
            cer=deleted_certificate_bundle.cer,
            recovery_id=deleted_certificate_bundle.recovery_id,
            scheduled_purge_date=deleted_certificate_bundle.scheduled_purge_date,
            tags=deleted_certificate_bundle.tags,
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