# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime
from typing import Any, Dict, Mapping, Optional

from ._shared import parse_vault_id
from ._shared._generated.v7_0 import models


class AdministratorDetails(object):
    """Details of the organization administrator of the certificate issuer."""

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
            phone=admin_details_bundle.phone
        )

    @property
    def email(self):
        # type: () -> str
        """The email of the issuer.
        :rtype: str
        """
        return self._email

    @property
    def first_name(self):
        # type: () -> str
        """The first name of the issuer.
        :rtype: str
        """
        return self._first_name

    @property
    def last_name(self):
        # type: () -> str
        """The last name of the issuer.
        :rtype: str
        """
        return self._last_name

    @property
    def phone(self):
        # type: () -> str
        """The phone number of the issuer.
        :rtype: str
        """
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
        """The error code.
        :rtype: str
        """
        return self._code

    @property
    def message(self):
        # type: () -> str
        """The error message.
        :rtype: str
        """
        return self._message

    @property
    def inner_error(self):
        # type: () -> models.Error
        """The error itself
        :return models.Error:
        """
        return self._inner_error


class CertificateBase(object):
    """Certificate base consists of a certificates metadata."""
    def __init__(self, attributes=None, cert_id=None, thumbprint=None, **kwargs):
        # type: (Optional[models.CertificateAttributes], Optional[str], Optional[bytes], Mapping[str, Any]) -> None
        self._attributes = attributes
        self._id = cert_id
        self._vault_id = parse_vault_id(cert_id)
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
        """Certificate identifier.
        :rtype: str
        """
        return self._id

    @property
    def name(self):
        # type: () -> str
        """The name of the certificate.
        :rtype: str
        """
        return self._vault_id.name

    @property
    def enabled(self):
        # type: () -> bool
        """Whether the certificate is enabled or not.
        :rtype: bool
        """
        return self._attributes.enabled if self._attributes else None

    @property
    def not_before(self):
        # type: () -> datetime
        """The datetime before which the certificate is not valid.
        :rtype: datetime
        """
        return self._attributes.not_before if self._attributes else None

    @property
    def expires(self):
        # type: () -> datetime
        """The datetime when the certificate expires.
        :rtype: datetime
        """
        return self._attributes.expires if self._attributes else None

    @property
    def created(self):
        # type: () -> datetime
        """The datetime when the certificate is created.
        :rtype: datetime
        """
        return self._attributes.created if self._attributes else None

    @property
    def updated(self):
        # type: () -> datetime
        """The datetime when the certificate was last updated.
        :rtype: datetime
        """
        return self._attributes.updated if self._attributes else None

    @property
    def recovery_level(self):
        # type: () -> models.DeletionRecoveryLevel
        """The deletion recovery level currently in effect for the certificate.
        :rtype: models.DeletionRecoveryLevel
        """
        return self._attributes.recovery_level if self._attributes else None

    @property
    def vault_url(self):
        # type: () -> str
        """The name of the vault that the certificate is created in.
        :rtype: str
        """
        return self._vault_id.vault_url

    @property
    def thumbprint(self):
        # type: () -> bytes
        """Thumbprint of the certificate.
        :rtype: bytes
        """
        return self._thumbprint

    @property
    def tags(self):
        # type: () -> Dict[str, str]
        """Application specific metadata in the form of key-value pairs.
        :rtype: str
        """
        return self._tags

    @property
    def version(self):
        # type: () -> str
        """The version of the certificate
        :rtype: str
        """
        return self._vault_id.version


class Certificate(CertificateBase):
    """Consists of a certificate and its attributes"""
    def __init__(self, policy, cert_id, thumbprint=None, key_id=None, secret_id=None, attributes=None, cer=None, **kwargs):
        # type: (models.CertificatePolicy, Optional[str], Optional[bytes], Optional[str], Optional[str], Optional[CertificateAttributes], Optional[bytes], Mapping[str, Any]) -> None
        super(Certificate, self).__init__(attributes=attributes, cert_id=cert_id, thumbprint=thumbprint, **kwargs)
        self._key_id = key_id
        self._secret_id = secret_id
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
            key_id=certificate_bundle.kid,
            secret_id=certificate_bundle.sid,
            policy=CertificatePolicy._from_certificate_policy_bundle(certificate_bundle.policy),
            cer=certificate_bundle.cer,
            tags=certificate_bundle.tags,
        )

    @property
    def key_id(self):
        # type: () -> str
        """The key id.
        :rtype: str
        """
        return self._key_id

    @property
    def secret_id(self):
        # type: () -> str
        """The secret id.
        :rtype: str
        """
        return self._secret_id

    @property
    def policy(self):
        # type: () -> CertificatePolicy
        """The management policy of the certificate.
        :rtype: CertificatePolicy
        """
        return self._policy

    @property
    def cer(self):
        # type: () -> bytes
        """The CER contents of the certificate.
        :rtype: bytes
        """
        return self._cer


class CertificateOperation(object):
    """A certificate operation is returned in case of asynchronous requests. """
    def __init__(
        self,
        cert_operation_id=None,
        issuer_name=None,
        certificate_type=None,
        certificate_transparency=False,
        csr=None,
        cancellation_requested=False,
        status=None,
        status_details=None,
        error=None,
        target=None,
        request_id=None,
        **kwargs
    ):
        # type: (Optional[str], Optional[str], Optional[str], Optional[bool], Optional[bytes], Optional[bool], Optional[str], Optional[str], Optional[models.Error], Optional[str], Optional[str], Mapping[str, Any]) -> None
        self._id = cert_operation_id
        self._vault_id = parse_vault_id(cert_operation_id)
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
            issuer_name=certificate_operation_bundle.issuer_parameters.name if certificate_operation_bundle.issuer_parameters else None,
            certificate_type=certificate_operation_bundle.issuer_parameters.certificate_type if certificate_operation_bundle.issuer_parameters else None,
            certificate_transparency=certificate_operation_bundle.issuer_parameters.certificate_transparency if certificate_operation_bundle.issuer_parameters else None,
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
        """The id of the certificate with this operation.
        :rtype: str
        """
        return self._id

    @property
    def name(self):
        # type: () -> str
        """The name of the certificate with this operation.
        :rtype: str
        """
        return self._vault_id.name

    @property
    def issuer_name(self):
        # type: () -> str
        """The name of the issuer of the certificate.
        :rtype: str
        """
        return self._issuer_name

    @property
    def certificate_type(self):
        # type: () -> str
        """Type of certificate to be requested from the issuer provider.
        :rtype: str
        """
        return self._certificate_type

    @property
    def certificate_transparency(self):
        # type: () -> bool
        """Whether certificates generated under this policy should be published to certificate
        transparency logs.
        :rtype: bool
        """
        return self._certificate_transparency

    @property
    def csr(self):
        # type: () -> bytes
        """The certificate signing request that is being used in this certificate operation.
        :rtype: bytes
        """
        return self._csr

    @property
    def cancellation_requested(self):
        # type: () -> bool
        """Whether cancellation was requested on the certificate operation.
        :rtype: bool
        """
        return self._cancellation_requested

    @property
    def status(self):
        # type: () -> str
        """Status of the certificate operation.
        :rtype: str
        """
        return self._status

    @property
    def status_details(self):
        # type: () -> str
        """Status details of the certificate operation.
        :rtype: str
        """
        return self._status_details

    @property
    def error(self):
        # type: () -> models.Error
        """Error encountered, if any, during the certificate operation.
        :rtype: models.Error
        """
        return self._error

    @property
    def target(self):
        # type: () -> str
        """Location which contains the result of the certificate operation.
        :rtype: str
        """
        return self._target

    @property
    def request_id(self):
        # type: () -> str
        """Identifier for the certificate operation.
        :rtype: str
        """
        return self._request_id


class CertificatePolicy(object):
    """Management policy for a certificate."""
    def __init__(
        self,
        attributes=None,
        cert_policy_id=None,
        key_properties=None,
        content_type=None,
        subject_name=None,
        san_emails=None,
        san_dns_names=None,
        san_upns=None,
        validity_in_months=None,
        lifetime_actions=None,
        issuer_name=None,
        certificate_type=None,
        certificate_transparency=None,
    ):
        # type: (Optional[models.CertificateAttributes], Optional[str], Optional[KeyProperties], Optional[str], Optional[str], Optional[list[str]], Optional[list[str]], Optional[list[str]], Optional[int], Optional[list[LifetimeAction]], Optional[str], Optional[str], Optional[bool], Mapping[str, Any]) -> None
        self._attributes = attributes
        self._id = cert_policy_id
        self._key_properties = key_properties
        self._content_type = content_type
        self._subject_name = subject_name
        self._san_emails = san_emails
        self._san_dns_names = san_dns_names
        self._san_upns = san_upns
        self._validity_in_months = validity_in_months
        self._lifetime_actions = lifetime_actions
        self._issuer_name = issuer_name
        self._certificate_type = certificate_type
        self._certificate_transparency = certificate_transparency

    def _to_certificate_policy_bundle(self):
        # type: (CertificatePolicy) -> models.CertificatePolicy

        """Construct a version emulating the generated CertificatePolicy from a wrapped CertificatePolicy"""
        if self.issuer_name or self.certificate_type or self.certificate_transparency:
            issuer_parameters = models.IssuerParameters(
                name=self.issuer_name,
                certificate_type=self.certificate_type,
                certificate_transparency=self.certificate_transparency
            )
        else:
            issuer_parameters = None

        if self.enabled is not None or self.not_before is not None or self.expires is not None or self.created is not None or self.updated is not None or self.recovery_level:
            attributes = models.CertificateAttributes(
                enabled=self.enabled,
                not_before=self.not_before,
                expires=self.expires,
                created=self.enabled,
                updated=self.updated,
                recovery_level=self.recovery_level
            )
        else:
            attributes = None

        if self.lifetime_actions:
            lifetime_actions = []
            for lifetime_action in self.lifetime_actions:
                lifetime_actions.append(
                    models.LifetimeAction(
                        trigger=models.Trigger(
                            lifetime_percentage=lifetime_action.lifetime_percentage,
                            days_before_expiry=lifetime_action.days_before_expiry
                        ),
                        action=models.Action(action_type=lifetime_action.action_type)
                    )
                )
        else:
            lifetime_actions = None

        if self.subject_name or self.key_properties.ekus or self.key_properties.key_usage or self.san_emails or self.san_upns or self.san_dns_names or self.validity_in_months:
            x509_certificate_properties=models.X509CertificateProperties(
                subject=self.subject_name,
                ekus=self.key_properties.ekus,
                subject_alternative_names=models.SubjectAlternativeNames(
                    emails=self.san_emails,
                    upns=self.san_upns,
                    dns_names=self.san_dns_names
                ),
                key_usage=self.key_properties.key_usage,
                validity_in_months=self.validity_in_months
            )
        else:
            x509_certificate_properties = None

        if self.key_properties.exportable or self.key_properties.key_type or self.key_properties.key_size or self.key_properties.reuse_key or self.key_properties.curbe:
            key_properties = models.KeyProperties(
                exportable=self.key_properties.exportable,
                key_type=self.key_properties.key_type,
                key_size=self.key_properties.key_size,
                reuse_key=self.key_properties.reuse_key,
                curve=self.key_properties.curve
            )
        else:
            key_properties = None

        if self.content_type:
            secret_properties = models.SecretProperties(content_type=self.content_type)
        else:
            secret_properties = None

        policy_bundle = models.CertificatePolicy(
            id=self.id,
            key_properties=key_properties,
            secret_properties=secret_properties,
            x509_certificate_properties=x509_certificate_properties,
            lifetime_actions=lifetime_actions,
            issuer_parameters=issuer_parameters,
            attributes=attributes
        )
        return policy_bundle

    @classmethod
    def _from_certificate_policy_bundle(cls, certificate_policy_bundle):
        # type: (models.CertificatePolicy) -> CertificatePolicy
        """Construct a CertificatePolicy from an autorest-generated CertificatePolicy"""
        if certificate_policy_bundle.lifetime_actions:
            lifetime_actions = [
                LifetimeAction(
                    action_type=item.action.action_type,
                    lifetime_percentage=item.trigger.lifetime_percentage,
                    days_before_expiry=item.trigger.days_before_expiry,
                )
                for item in certificate_policy_bundle.lifetime_actions
            ]
        else:
            lifetime_actions = None
        key_properties_bundle = certificate_policy_bundle.key_properties
        if key_properties_bundle and (key_properties_bundle.exportable or key_properties_bundle.key_type or key_properties_bundle.key_size or key_properties_bundle.reuse_key or key_properties_bundle.curve or key_properties_bundle.ekus or key_properties_bundle.key_usage):
            key_properties = KeyProperties(
                exportable=certificate_policy_bundle.key_properties.exportable,
                key_type=certificate_policy_bundle.key_properties.key_type,
                key_size=certificate_policy_bundle.key_properties.key_size,
                reuse_key=certificate_policy_bundle.key_properties.reuse_key,
                curve=certificate_policy_bundle.key_properties.curve,
                ekus=certificate_policy_bundle.x509_certificate_properties.ekus if certificate_policy_bundle.x509_certificate_properties else None,
                key_usage=certificate_policy_bundle.x509_certificate_properties.key_usage if certificate_policy_bundle.x509_certificate_properties else None,
            )
        else:
            key_properties = None
        return cls(
            attributes=certificate_policy_bundle.attributes,
            cert_policy_id=certificate_policy_bundle.id,
            issuer_name=certificate_policy_bundle.issuer_parameters.name if certificate_policy_bundle.issuer_parameters else None,
            certificate_type=certificate_policy_bundle.issuer_parameters.certificate_type if certificate_policy_bundle.issuer_parameters else None,
            certificate_transparency=certificate_policy_bundle.issuer_parameters.certificate_transparency if certificate_policy_bundle.issuer_parameters else None,
            lifetime_actions=lifetime_actions,
            subject_name=certificate_policy_bundle.x509_certificate_properties.subject if certificate_policy_bundle.x509_certificate_properties else None,
            san_emails=certificate_policy_bundle.x509_certificate_properties.subject_alternative_names.emails if certificate_policy_bundle.x509_certificate_properties and certificate_policy_bundle.x509_certificate_properties.subject_alternative_names else None,
            san_upns=certificate_policy_bundle.x509_certificate_properties.subject_alternative_names.upns if certificate_policy_bundle.x509_certificate_properties and certificate_policy_bundle.x509_certificate_properties.subject_alternative_names else None,
            san_dns_names=certificate_policy_bundle.x509_certificate_properties.subject_alternative_names.dns_names if certificate_policy_bundle.x509_certificate_properties and certificate_policy_bundle.x509_certificate_properties.subject_alternative_names else None,
            validity_in_months=certificate_policy_bundle.x509_certificate_properties.validity_in_months if certificate_policy_bundle.x509_certificate_properties else None,
            key_properties=key_properties,
            content_type=certificate_policy_bundle.secret_properties.content_type if certificate_policy_bundle.secret_properties else None,
        )

    @property
    def id(self):
        # type: () -> str
        """The certificate id.
        :rtype: str
        """
        return self._id

    @property
    def key_properties(self):
        # type: () -> models.KeyProperties
        """Properties of the key backing the certificate.
        :rtype: KeyProperties
        """
        return self._key_properties

    @property
    def content_type(self):
        # type: () -> str
        """The media type (MIME type).
        :rtype: str
        """
        return self._content_type

    @property
    def subject_name(self):
        # type: () -> str
        """The subject name.
        :rtype: str
        """
        return self._subject_name

    @property
    def san_emails(self):
        # type: () -> list[str]
        """The subject alternative email addresses.
        :rtype: list[str]
        """
        return self._san_emails

    @property
    def san_dns_names(self):
        # type: () -> list[str]
        """The subject alternative domain names.
        :rtype: list[str]
        """
        return self._san_dns_names

    @property
    def san_upns(self):
        # type: () -> list[str]
        """The subject alternative user principal names.
        :rtype: list[str]
        """
        return self._san_upns

    @property
    def validity_in_months(self):
        # type: () -> int
        """The duration that the certificate is valid for in months.
        :rtype: int
        """
        return self._validity_in_months

    @property
    def lifetime_actions(self):
        # type: () -> list[LifetimeAction]
        """Actions and their triggers that will be performed by Key Vault over
        the lifetime of the certificate.
        :rtype: list[LifetimeAction]
        """
        return self._lifetime_actions

    @property
    def issuer_name(self):
        # type: () -> str
        """Name of the referenced issuer object or reserved names for the issuer
        of the certificate.
        :rtype: str
        """
        return self._issuer_name

    @property
    def certificate_type(self):
        # type: () -> str
        """Type of certificate requested from the issuer provider.
        :rtype: str
        """
        return self._certificate_type

    @property
    def certificate_transparency(self):
        # type: () -> bool
        """Whether the certificates generated under this policy should be published
        to certificate transparency logs.
        :rtype: bool
        """
        return self._certificate_transparency

    @property
    def enabled(self):
        # type: () -> bool
        """Whether the certificate is enabled or not.
        :rtype: bool
        """
        return self._attributes.enabled if self._attributes else None

    @property
    def not_before(self):
        # type: () -> datetime
        """The datetime before which the certificate is not valid.
        :rtype: datetime
        """
        return self._attributes.not_before if self._attributes else None

    @property
    def expires(self):
        # type: () -> datetime
        """The datetime when the certificate expires.
        :rtype: datetime
        """
        return self._attributes.expires if self._attributes else None

    @property
    def created(self):
        # type: () -> datetime
        """The datetime when the certificate is created.
        :rtype: datetime
        """
        return self._attributes.created if self._attributes else None

    @property
    def updated(self):
        # type: () -> datetime
        """The datetime when the certificate was last updated.
        :rtype: datetime
        """
        return self._attributes.updated if self._attributes else None

    @property
    def recovery_level(self):
        # type: () -> models.DeletionRecoveryLevel
        """The deletion recovery level currently in effect for the certificate.
        :rtype: models.DeletionRecoveryLevel
        """
        return self._attributes.recovery_level if self._attributes else None


class Contact:
    """The contact information for the vault certificates."""

    def __init__(self, email=None, name=None, phone=None):
        # type: (Optional[str], Optional[str], Optional[str]) -> None
        self._email = email
        self._name = name
        self._phone = phone

    @classmethod
    def _from_certificate_contacts_item(cls, contact_item):
        # type: (models.Contact) -> Contact
        """Construct a Contact from an autorest-generated ContactItem."""
        return cls(email=contact_item.email_address, name=contact_item.name, phone=contact_item.phone)

    @property
    def email(self):
        # type: () -> str
        """Email address.
        :rtype: str
        """
        return self._email

    @property
    def name(self):
        # type: () -> str
        """Name.
        :rtype: str
        """
        return self._name

    @property
    def phone(self):
        # type: () -> str
        """Phone number.
        :rtype: str
        """
        return self._phone


class IssuerBase(object):
    """The base for the issuer containing the issuer metadata."""
    def __init__(self, issuer_id=None, provider=None):
        # type: (Optional[str], Optional[str]) -> None
        self._id = issuer_id
        self._vault_id = parse_vault_id(issuer_id)
        self._provider = provider

    @classmethod
    def _from_issuer_item(cls, issuer_item):
        # type: (models.CertificateIssuerItem) -> IssuerBase
        """Construct a IssuerBase from an autorest-generated CertificateIssuerItem"""
        return cls(issuer_id=issuer_item.id, provider=issuer_item.provider)

    @property
    def id(self):
        # type: () -> str
        """Certificate identifier.
        :rtype: str
        """
        return self._id

    @property
    def name(self):
        # type: () -> str
        # Issuer name is listed under version under vault_id
        """Name of the issuer.
        :rtype: str
        """
        return self._vault_id.version

    @property
    def provider(self):
        # type: () -> str
        """The issuer provider.
        :rtype: str
        """
        return self._provider

    @property
    def vault_url(self):
        # type: () -> str
        """The name of the vault with this issuer.
        :rtype: str
        """
        return self._vault_id.vault_url


class Issuer(IssuerBase):
    def __init__(
        self, attributes=None, provider=None, issuer_id=None, account_id=None, password=None, organization_id=None, admin_details=None, **kwargs
    ):
        # type: (Optional[models.IssuerAttributes], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[List[AdministratorDetails]], Mapping[str, Any]) -> None
        super(Issuer, self).__init__(issuer_id=issuer_id, provider=provider, **kwargs)
        self._attributes = attributes
        self._account_id = account_id
        self._password = password
        self._organization_id = organization_id
        self._admin_details = admin_details

    @classmethod
    def _from_issuer_bundle(cls, issuer_bundle):
        # type: (models.IssuerBundle) -> Issuer
        """Construct a Issuer from an autorest-generated IssuerBundle"""
        admin_details = []
        admin_details_service = issuer_bundle.organization_details.admin_details
        for admin_detail in admin_details_service:
            admin_details.append(AdministratorDetails._from_admin_details_bundle(admin_detail))
        return cls(
            attributes=issuer_bundle.attributes,
            issuer_id=issuer_bundle.id,
            provider=issuer_bundle.provider,
            account_id=issuer_bundle.credentials.account_id if issuer_bundle.credentials else None,
            password=issuer_bundle.credentials.password if issuer_bundle.credentials else None,
            organization_id=issuer_bundle.organization_details.id if issuer_bundle.organization_details else None,
            admin_details=admin_details
        )

    @property
    def enabled(self):
        # type: () -> bool
        """Whether the certificate is enabled or not.
        :rtype: bool
        """
        return self._attributes.enabled if self._attributes else None

    @property
    def created(self):
        # type: () -> datetime
        """The datetime when the certificate is created.
        :rtype: datetime
        """
        return self._attributes.created if self._attributes else None

    @property
    def updated(self):
        # type: () -> datetime
        """The datetime when the certificate was last updated.
        :rtype: datetime
        """
        return self._attributes.updated if self._attributes else None

    @property
    def account_id(self):
        # type: () -> str
        """THe username/ account name/ account id.
        :rtype: str
        """
        return self._account_id

    @property
    def password(self):
        # type: () -> str
        """The password / secret / account key.
        :rtype: str
        """
        return self._password

    @property
    def organization_id(self):
        # type: () -> str
        """Id of the organization.
        :rtype: str
        """
        return self._organization_id

    @property
    def admin_details(self):
        # type: () -> List[AdministratorDetails]
        """Details of the organization administrator of this issuer.
        :rtype: List[AdministratorDetails]
        """
        return self._admin_details


class KeyProperties(object):
    """Properties of the key pair backing a certificate."""
    def __init__(self, exportable=None, key_type=None, key_size=None, reuse_key=None, curve=None, ekus=None, key_usage=None):
        # type: (Optional[bool], Optional[str], Optional[int], Optional[bool], Optional[str], Optional[list[str]], Optional[list[str]]) -> None
        self._exportable = exportable
        self._key_type = key_type
        self._key_size = key_size
        self._reuse_key = reuse_key
        self._curve = curve
        self._ekus = ekus
        self._key_usage = key_usage

    @property
    def exportable(self):
        # type: () -> bool
        """Whether the private key can be exported.
        :rtype: bool
        """
        return self._exportable

    @property
    def key_type(self):
        # type: () -> models.JsonWebKeyType
        """The type of key pair to be used for the certificate.
        :rtype: models.JsonWebKeyType
        """
        return self._key_type

    @property
    def key_size(self):
        # type: () -> int
        """The key size in bits.
        :rtype: int
        """
        return self._key_size

    @property
    def reuse_key(self):
        # type: () -> bool
        """Whether the same key pair will be used on certificate renewal.
        :rtype: bool
        """
        return self._reuse_key

    @property
    def curve(self):
        # type: () -> models.JsonWebKeyCurveName
        """Elliptic curve name.
        :rtype: models.JsonWebKeyCurveName
        """
        return self._curve

    @property
    def ekus(self):
        # type: () -> list[str]
        """The enhanced key usage.
        :rtype: list[str]
        """
        return self._ekus

    @property
    def key_usage(self):
        # type: () -> list[str]
        """List of key usages.
        :rtype: list[str]
        """
        return self._key_usage


class LifetimeAction(object):
    """Action and its trigger that will be performed by certificate Vault over the
    lifetime of a certificate.
    """

    def __init__(self, action_type, lifetime_percentage=None, days_before_expiry=None):
        # type: (str, Optional[int], Optional[int]) -> None
        self._lifetime_percentage = lifetime_percentage
        self._days_before_expiry = days_before_expiry
        self._action_type = action_type

    @property
    def lifetime_percentage(self):
        # type: () -> int
        """Percentage of lifetime at which to trigger.
        :rtype: int
        """
        return self._lifetime_percentage

    @property
    def days_before_expiry(self):
        # type: () -> int
        """Days before expiry to attempt renewal.
        :rtype: int
        """
        return self._days_before_expiry

    @property
    def action_type(self):
        # type: () -> str
        """The type of the action that will be executed.
        Valid values are "EmailContacts" and "AutoRenew"
        :rtype: str or models.ActionType
        """
        return self._action_type


class DeletedCertificate(Certificate):
    """A Deleted Certificate consisting of its previous id, attributes and its
    tags, as well as information on when it will be purged."""

    def __init__(
        self,
        attributes=None,
        cert_id=None,
        thumbprint=None,
        key_id=None,
        secret_id=None,
        policy=None,
        cer=None,
        deleted_date=None,
        recovery_id=None,
        scheduled_purge_date=None,
        **kwargs
    ):
        # type: (Optional[models.CertificateAttributes], Optional[str], Optional[bytes], Optional[str], Optional[str], Optional[models.CertificatePolicy], Optional[bytes], optional[datetime], Optional[str], Optional[datetime], Mapping[str, Mapping[str, Any]) -> None
        super(DeletedCertificate, self).__init__(policy=policy, cert_id=cert_id, thumbprint=thumbprint, key_id=key_id, secret_id=secret_id, attributes=attributes, cer=cer, **kwargs)
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
            key_id=None,
            secret_id=None,
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
            key_id=deleted_certificate_bundle.kid,
            secret_id=deleted_certificate_bundle.sid,
            policy=CertificatePolicy._from_certificate_policy_bundle(deleted_certificate_bundle.policy),
            cer=deleted_certificate_bundle.cer,
            recovery_id=deleted_certificate_bundle.recovery_id,
            scheduled_purge_date=deleted_certificate_bundle.scheduled_purge_date,
            tags=deleted_certificate_bundle.tags,
        )

    @property
    def deleted_date(self):
        # type: () -> datetime
        """The datetime that the certificate was deleted.
        :rtype: datetime
        """
        return self._deleted_date

    @property
    def recovery_id(self):
        # type: () -> str
        """The url of the recovery object, used to identify and recover the deleted certificate.
        :rtype: str
        """
        return self._recovery_id

    @property
    def scheduled_purge_date(self):
        # type: () -> datetime
        """The datetime when the certificate is scheduled to be purged.
        :rtype: str
        """
        return self._scheduled_purge_date