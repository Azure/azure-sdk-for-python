# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=too-many-lines,too-many-public-methods
from . import _generated_models as models
from ._shared import parse_key_vault_id
from ._enums import(
    CertificatePolicyAction,
    KeyUsageType,
    KeyCurveName,
    KeyType,
    CertificateContentType,
    WellKnownIssuerNames
)

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Union, List
    from datetime import datetime


class AdministratorContact(object):
    """Details of the organization administrator of the certificate issuer.

    :param str first_name: First name of the issuer.
    :param str last_name: Last name of the issuer.
    :param str email: email of the issuer.
    :param str phone: phone number of the issuer.
    """

    def __init__(self, first_name=None, last_name=None, email=None, phone=None):
        # type: (Optional[str], Optional[str], Optional[str], Optional[str]) -> None
        self._first_name = first_name
        self._last_name = last_name
        self._phone = phone
        self._email = email

    def __repr__(self):
        # type () -> str
        return "AdministratorContact(first_name={}, last_name={}, email={}, phone={})".format(
            self.first_name, self.last_name, self.email, self.phone
        )[:1024]

    @classmethod
    def _from_admin_detail(cls, admin_detail):
        # type: (models.AdministratorDetails) -> AdministratorContact
        """Construct a AdministratorContact from an autorest-generated AdministratorDetailsBundle"""
        return cls(
            email=admin_detail.email_address,
            first_name=admin_detail.first_name,
            last_name=admin_detail.last_name,
            phone=admin_detail.phone,
        )

    @property
    def email(self):
        # type: () -> Optional[str]
        """:rtype: str or None"""
        return self._email

    @property
    def first_name(self):
        # type: () -> Optional[str]
        """:rtype: str or None"""
        return self._first_name

    @property
    def last_name(self):
        # type: () -> Optional[str]
        """:rtype: str or None"""
        return self._last_name

    @property
    def phone(self):
        # type: () -> Optional[str]
        """:rtype: str or None"""
        return self._phone


class CertificateOperationError(object):
    """The key vault server error.

    :param str code: The error code.
    :param str message: The error message.
    :param inner_error: The error object itself
    :type inner_error: ~azure.keyvault.certificates.CertificateOperationError
    """

    def __init__(self, code, message, inner_error):
        # type: (str, str, CertificateOperationError) -> None
        self._code = code
        self._message = message
        self._inner_error = inner_error

    def __repr__(self):
        # type () -> str
        return "CertificateOperationError({}, {}, {})".format(self.code, self.message, self.inner_error)[:1024]

    @classmethod
    def _from_error_bundle(cls, error_bundle):
        # type: (models.Error) -> CertificateOperationError
        return cls(
            code=error_bundle.code,
            message=error_bundle.message,
            inner_error=cls._from_error_bundle(error_bundle.inner_error)
        )

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
        # type: () -> CertificateOperationError
        """The error itself

        :return ~azure.keyvault.certificates.CertificateOperationError:
        """
        return self._inner_error


class CertificateProperties(object):
    """Certificate properties consists of a certificates metadata.
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self._attributes = kwargs.pop("attributes", None)
        self._id = kwargs.pop("cert_id", None)
        self._vault_id = KeyVaultCertificateIdentifier(self._id)
        self._x509_thumbprint = kwargs.pop("x509_thumbprint", None)
        self._tags = kwargs.pop("tags", None)

    def __repr__(self):
        # type () -> str
        return "<CertificateProperties [{}]>".format(self.id)[:1024]

    @classmethod
    def _from_certificate_item(cls, certificate_item):
        # type: (Union[models.CertificateItem, models.CertificateBundle]) -> CertificateProperties
        """Construct a CertificateProperties from an autorest-generated CertificateItem"""
        return cls(
            attributes=certificate_item.attributes,
            cert_id=certificate_item.id,
            x509_thumbprint=certificate_item.x509_thumbprint,
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

        :rtype: ~datetime.datetime
        """
        return self._attributes.not_before if self._attributes else None

    @property
    def expires_on(self):
        # type: () -> datetime
        """The datetime when the certificate expires.

        :rtype: ~datetime.datetime
        """
        return self._attributes.expires if self._attributes else None

    @property
    def created_on(self):
        # type: () -> datetime
        """The datetime when the certificate is created.

        :rtype: ~datetime.datetime
        """
        return self._attributes.created if self._attributes else None

    @property
    def updated_on(self):
        # type: () -> datetime
        """The datetime when the certificate was last updated.

        :rtype: ~datetime.datetime
        """
        return self._attributes.updated if self._attributes else None

    @property
    def recoverable_days(self):
        # type: () -> Optional[int]
        """The number of days the certificate is retained before being deleted from a soft-delete enabled Key Vault.

        :rtype: int
        """
        # recoverable_days was added in 7.1-preview
        if self._attributes and hasattr(self._attributes, "recoverable_days"):
            return self._attributes.recoverable_days
        return None

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
        """URL of the vault containing the certificate

        :rtype: str
        """
        return self._vault_id.vault_url

    @property
    def x509_thumbprint(self):
        # type: () -> bytes
        """Thumbprint of the certificate.

        :rtype: bytes
        """
        return self._x509_thumbprint

    @property
    def tags(self):
        # type: () -> Dict[str, str]
        """Application specific metadata in the form of key-value pairs.

        :rtype: str
        """
        return self._tags

    @property
    def version(self):
        # type: () -> Optional[str]
        """The version of the certificate

        :rtype: str or None
        """
        return self._vault_id.version


class KeyVaultCertificate(object):
    """Consists of a certificate and its attributes

    :param policy: The management policy for the certificate.
    :type policy: ~azure.keyvault.certificates.CertificatePolicy
    :param properties: The certificate's properties.
    :type properties: ~azure.keyvault.certificates.CertificateProperties
    :param bytearray cer: CER contents of the X509 certificate.
    """

    def __init__(
        self,
        policy=None,  # type: Optional[CertificatePolicy]
        properties=None,  # type: Optional[CertificateProperties]
        cer=None,  # type: Optional[bytes]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        self._properties = properties
        self._key_id = kwargs.get("key_id", None)
        self._secret_id = kwargs.get("secret_id")
        self._policy = policy
        self._cer = cer

    def __repr__(self):
        # type () -> str
        return "<KeyVaultCertificate [{}]>".format(self.id)[:1024]

    @classmethod
    def _from_certificate_bundle(cls, certificate_bundle):
        # type: (models.CertificateBundle) -> KeyVaultCertificate
        """Construct a certificate from an autorest-generated certificateBundle"""
        # pylint:disable=protected-access, line-too-long

        if certificate_bundle.policy:
            policy = CertificatePolicy._from_certificate_policy_bundle(certificate_bundle.policy)  # type: Optional[CertificatePolicy]
        else:
            policy = None

        return cls(
            properties=CertificateProperties._from_certificate_item(certificate_bundle),
            key_id=certificate_bundle.kid,
            secret_id=certificate_bundle.sid,
            policy=policy,
            cer=certificate_bundle.cer,
        )

    @property
    def id(self):
        # type: () -> Optional[str]
        """Certificate identifier.

        :rtype: str or None
        """
        return self._properties.id if self._properties else None

    @property
    def name(self):
        # type: () -> Optional[str]
        """The name of the certificate.

        :rtype: str or None
        """
        return self._properties.name if self._properties else None

    @property
    def properties(self):
        # type: () -> Optional[CertificateProperties]
        """The certificate's properties

        :rtype: ~azure.keyvault.certificates.CertificateProperties or None
        """
        return self._properties

    @property
    def key_id(self):
        # type: () -> str
        """:rtype: str"""
        return self._key_id

    @property
    def secret_id(self):
        # type: () -> Optional[str]
        """:rtype: Any or None"""
        return self._secret_id

    @property
    def policy(self):
        # type: () -> Optional[CertificatePolicy]
        """The management policy of the certificate.

        :rtype: ~azure.keyvault.certificates.CertificatePolicy or None
        """
        return self._policy

    @property
    def cer(self):
        # type: () -> Optional[bytes]
        """The CER contents of the certificate.

        :rtype: bytes or None
        """
        return self._cer


class KeyVaultCertificateIdentifier(object):
    """Information about a KeyVaultCertificate parsed from a certificate ID.

    :param str source_id: the full original identifier of a certificate
    :raises ValueError: if the certificate ID is improperly formatted
    Example:
        .. literalinclude:: ../tests/test_parse_id.py
            :start-after: [START parse_key_vault_certificate_id]
            :end-before: [END parse_key_vault_certificate_id]
            :language: python
            :caption: Parse a certificate's ID
            :dedent: 8
    """

    def __init__(self, source_id):
        # type: (str) -> None
        self._resource_id = parse_key_vault_id(source_id)

    @property
    def source_id(self):
        # type: () -> str
        return self._resource_id.source_id

    @property
    def vault_url(self):
        # type: () -> str
        return self._resource_id.vault_url

    @property
    def name(self):
        # type: () -> str
        return self._resource_id.name

    @property
    def version(self):
        # type: () -> Optional[str]
        return self._resource_id.version


class CertificateOperation(object):
    # pylint:disable=too-many-instance-attributes
    """A certificate operation is returned in case of long running requests.

    :param str cert_operation_id: The certificate id.
    :param issuer_name: Name of the operation's issuer object or reserved names.
    :type issuer_name: str or ~azure.keyvault.certificates.WellKnownIssuerNames
    :param str certificate_type: Type of certificate requested from the issuer provider.
    :param bool certificate_transparency: Indicates if the certificate this operation is
        running for is published to certificate transparency logs.
    :param bytearray csr: The certificate signing request (CSR) that is being used in the certificate
        operation.
    :param bool cancellation_requested: Indicates if cancellation was requested on the certificate
        operation.
    :param str status: Status of the certificate operation.
    :param str status_details: The status details of the certificate operation
    :param error: Error encountered, if any, during the certificate operation.
    :type error: ~azure.keyvault.certificates.CertificateOperationError
    :param str target: Location which contains the result of the certificate operation.
    :param str request_id: Identifier for the certificate operation.
    """

    def __init__(
        self,
        cert_operation_id=None,  # type: Optional[str]
        issuer_name=None,  # type: Optional[Union[str, WellKnownIssuerNames]]
        certificate_type=None,  # type: Optional[str]
        certificate_transparency=False,  # type: Optional[bool]
        csr=None,  # type: Optional[bytes]
        cancellation_requested=False,  # type: Optional[bool]
        status=None,  # type: Optional[str]
        status_details=None,  # type: Optional[str]
        error=None,  # type: Optional[CertificateOperationError]
        target=None,  # type: Optional[str]
        request_id=None,  # type: Optional[str]
    ):
        # type: (...) -> None
        self._id = cert_operation_id
        self._vault_id = parse_key_vault_id(cert_operation_id) if cert_operation_id else None
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

    def __repr__(self):
        # type () -> str
        return "<CertificateOperation [{}]>".format(self.id)[:1024]

    @classmethod
    def _from_certificate_operation_bundle(cls, certificate_operation_bundle):
        # type: (models.CertificateOperation) -> CertificateOperation
        """Construct a CertificateOperation from an autorest-generated CertificateOperation"""

        issuer_parameters = certificate_operation_bundle.issuer_parameters
        return cls(
            cert_operation_id=certificate_operation_bundle.id,
            issuer_name=issuer_parameters.name if issuer_parameters else None,
            certificate_type=(
                certificate_operation_bundle.issuer_parameters.certificate_type
                if certificate_operation_bundle.issuer_parameters
                else None
            ),
            # 2016-10-01 IssuerParameters doesn't have certificate_transparency
            certificate_transparency=getattr(issuer_parameters, "certificate_transparency", None),
            csr=certificate_operation_bundle.csr,
            cancellation_requested=certificate_operation_bundle.cancellation_requested,
            status=certificate_operation_bundle.status,
            status_details=certificate_operation_bundle.status_details,
            error=(CertificateOperationError._from_error_bundle(certificate_operation_bundle.error)  # pylint: disable=protected-access
                   if certificate_operation_bundle.error else None),
            target=certificate_operation_bundle.target,
            request_id=certificate_operation_bundle.request_id,
        )

    @property
    def id(self):
        # type: () -> Optional[str]
        """:rtype: str or None"""
        return self._id

    @property
    def name(self):
        # type: () -> Optional[str]
        """:rtype: str or None"""
        return self._vault_id.name if self._vault_id else None

    @property
    def vault_url(self):
        # type: () -> Optional[str]
        """URL of the vault containing the CertificateOperation

        :rtype: str or None
        """
        return self._vault_id.vault_url if self._vault_id else None

    @property
    def issuer_name(self):
        # type: () -> Union[str, WellKnownIssuerNames, None]
        """The name of the issuer of the certificate.

        :rtype: str or ~azure.keyvault.certificates.WellKnownIssuerNames or None
        """
        return self._issuer_name

    @property
    def certificate_type(self):
        # type: () -> Optional[str]
        """Type of certificate to be requested from the issuer provider.

        :rtype: str or None
        """
        return self._certificate_type

    @property
    def certificate_transparency(self):
        # type: () -> Optional[bool]
        """Whether certificates generated under this policy should be published to certificate
        transparency logs.

        :rtype: bool or None
        """
        return self._certificate_transparency

    @property
    def csr(self):
        # type: () -> Optional[bytes]
        """The certificate signing request that is being used in this certificate operation.

        :rtype: bytes or None
        """
        return self._csr

    @property
    def cancellation_requested(self):
        # type: () -> Optional[bool]
        """Whether cancellation was requested on the certificate operation.

        :rtype: bool or None
        """
        return self._cancellation_requested

    @property
    def status(self):
        # type: () -> Optional[str]
        """:rtype: str or None"""
        return self._status

    @property
    def status_details(self):
        # type: () -> Optional[str]
        """:rtype: str or None"""
        return self._status_details

    @property
    def error(self):
        # type: () -> Optional[CertificateOperationError]
        """:rtype: ~azure.keyvault.certificates.CertificateOperationError or None"""
        return self._error

    @property
    def target(self):
        # type: () -> Optional[str]
        """Location which contains the result of the certificate operation.

        :rtype: str or None
        """
        return self._target

    @property
    def request_id(self):
        # type: () -> Optional[str]
        """Identifier for the certificate operation.

        :rtype: str or None
        """
        return self._request_id


class CertificatePolicy(object):
    """Management policy for a certificate.

    :param Optional[str] issuer_name: Optional. Name of the referenced issuer object or reserved names; for example,
        :attr:`~azure.keyvault.certificates.WellKnownIssuerNames.self` or
        :attr:`~azure.keyvault.certificates.WellKnownIssuerNames.unknown`
    :keyword str subject: The subject name of the certificate. Should be a valid X509
        distinguished name. Either subject or one of the subject alternative name parameters are required for
        creating a certificate. This will be ignored when importing a certificate; the subject will be parsed from
        the imported certificate.
    :keyword Iterable[str] san_emails: Subject alternative emails of the X509 object. Either
        subject or one of the subject alternative name parameters are required for creating a certificate.
    :keyword Iterable[str] san_dns_names: Subject alternative DNS names of the X509 object. Either
        subject or one of the subject alternative name parameters are required for creating a certificate.
    :keyword Iterable[str] san_user_principal_names: Subject alternative user principal names of the X509 object.
        Either subject or one of the subject alternative name parameters are required for creating a certificate.
    :keyword bool exportable: Indicates if the private key can be exported. For valid values,
        see KeyType.
    :keyword key_type: The type of key pair to be used for the certificate.
    :paramtype key_type: str or ~azure.keyvault.certificates.KeyType
    :keyword int key_size: The key size in bits. For example: 2048, 3072, or 4096
        for RSA.
    :keyword bool reuse_key: Indicates if the same key pair will be used on certificate
        renewal.
    :keyword key_curve_name: Elliptic curve name. For valid values, see KeyCurveName.
    :paramtype key_curve_name: str or ~azure.keyvault.certificates.KeyCurveName
    :keyword enhanced_key_usage: The extended ways the key of the certificate can be used.
    :paramtype enhanced_key_usage: list[str]
    :keyword key_usage: List of key usages.
    :paramtype key_usage: list[str or ~azure.keyvault.certificates.KeyUsageType]
    :keyword content_type: The media type (MIME type) of the secret backing the certificate.  If not specified,
        :attr:`CertificateContentType.pkcs12` is assumed.
    :paramtype content_type: str or ~azure.keyvault.certificates.CertificateContentType
    :keyword int validity_in_months: The duration that the certificate is valid in months.
    :keyword lifetime_actions: Actions that will be performed by Key Vault over the lifetime
        of a certificate
    :paramtype lifetime_actions: Iterable[~azure.keyvault.certificates.LifetimeAction]
    :keyword str certificate_type: Type of certificate to be requested from the issuer provider.
    :keyword bool certificate_transparency: Indicates if the certificates generated under this policy
        should be published to certificate transparency logs.

    """

    # pylint:disable=too-many-instance-attributes
    def __init__(
        self,
        issuer_name=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        self._issuer_name = issuer_name
        self._subject = kwargs.pop("subject", None)
        self._attributes = kwargs.pop("attributes", None)
        self._exportable = kwargs.pop("exportable", None)
        self._key_type = kwargs.pop("key_type", None)
        self._key_size = kwargs.pop("key_size", None)
        self._reuse_key = kwargs.pop("reuse_key", None)
        self._key_curve_name = kwargs.pop("key_curve_name", None)
        self._enhanced_key_usage = kwargs.pop("enhanced_key_usage", None)
        self._key_usage = kwargs.pop("key_usage", None)
        self._content_type = kwargs.pop("content_type", None)
        self._validity_in_months = kwargs.pop("validity_in_months", None)
        self._lifetime_actions = kwargs.pop("lifetime_actions", None)
        self._certificate_type = kwargs.pop("certificate_type", None)
        self._certificate_transparency = kwargs.pop("certificate_transparency", None)
        self._san_emails = kwargs.pop("san_emails", None) or None
        self._san_dns_names = kwargs.pop("san_dns_names", None) or None
        self._san_user_principal_names = kwargs.pop("san_user_principal_names", None) or None

    @classmethod
    def get_default(cls):
        return cls(issuer_name=WellKnownIssuerNames.self, subject="CN=DefaultPolicy")

    def __repr__(self):
        # type () -> str
        return "<CertificatePolicy [issuer_name: {}]>".format(self.issuer_name)[:1024]

    def _to_certificate_policy_bundle(self):
        # type: (CertificatePolicy) -> models.CertificatePolicy

        """Construct a version emulating the generated CertificatePolicy from a wrapped CertificatePolicy"""
        if self.issuer_name or self.certificate_type or self.certificate_transparency:
            issuer_parameters = models.IssuerParameters(
                name=self.issuer_name,
                certificate_type=self.certificate_type,
                certificate_transparency=self.certificate_transparency,  # 2016-10-01 model will ignore this
            )  # type: Optional[models.IssuerParameters]
        else:
            issuer_parameters = None

        # pylint:disable=too-many-boolean-expressions
        if (
            self.enabled is not None
            or self.created_on is not None
            or self.updated_on is not None
        ):
            attributes = models.CertificateAttributes(
                enabled=self.enabled,
                created=self.created_on,
                updated=self.updated_on,
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
                            days_before_expiry=lifetime_action.days_before_expiry,
                        ),
                        action=models.Action(action_type=lifetime_action.action),
                    )
                )
        else:
            lifetime_actions = None  # type: ignore

        # pylint:disable=too-many-boolean-expressions
        if (
            self.subject
            or self.enhanced_key_usage
            or self.key_usage
            or self.san_emails
            or self.san_user_principal_names
            or self.san_dns_names
            or self.validity_in_months
        ):
            if self.key_usage:
                key_usage = [
                    k.value if not isinstance(k, str) else k for k in self.key_usage
                ]  # type: Optional[List[Union[str, KeyUsageType]]]
            else:
                key_usage = None

            x509_certificate_properties = models.X509CertificateProperties(
                subject=self.subject,
                ekus=self.enhanced_key_usage,
                subject_alternative_names=models.SubjectAlternativeNames(
                    emails=self.san_emails, upns=self.san_user_principal_names, dns_names=self.san_dns_names
                ),
                key_usage=key_usage,
                validity_in_months=self.validity_in_months,
            )  # type: Optional[models.X509CertificateProperties]
        else:
            x509_certificate_properties = None

        if self.exportable or self.key_type or self.key_size or self.reuse_key or self.key_curve_name:
            key_properties = models.KeyProperties(
                exportable=self.exportable,
                key_type=self.key_type,
                key_size=self.key_size,
                reuse_key=self.reuse_key,
                curve=self.key_curve_name,
            )  # type: Optional[models.KeyProperties]
        else:
            key_properties = None

        if self.content_type:
            secret_properties = models.SecretProperties(
                content_type=self.content_type
            )  # type: Optional[models.SecretProperties]
        else:
            secret_properties = None

        policy_bundle = models.CertificatePolicy(
            key_properties=key_properties,
            secret_properties=secret_properties,
            x509_certificate_properties=x509_certificate_properties,
            lifetime_actions=lifetime_actions,
            issuer_parameters=issuer_parameters,
            attributes=attributes,
        )
        return policy_bundle

    @classmethod
    def _from_certificate_policy_bundle(cls, certificate_policy_bundle):
        # type: (Optional[models.CertificatePolicy]) -> CertificatePolicy
        """Construct a CertificatePolicy from an autorest-generated CertificatePolicy"""
        if certificate_policy_bundle is None:
            return cls()

        if certificate_policy_bundle.lifetime_actions:
            lifetime_actions = [
                LifetimeAction(
                    action=CertificatePolicyAction(item.action.action_type) if item.action else None,
                    lifetime_percentage=item.trigger.lifetime_percentage if item.trigger else None,
                    days_before_expiry=item.trigger.days_before_expiry if item.trigger else None,
                )
                for item in certificate_policy_bundle.lifetime_actions
            ]  # type: Optional[List[LifetimeAction]]
        else:
            lifetime_actions = None
        x509_certificate_properties = certificate_policy_bundle.x509_certificate_properties
        if x509_certificate_properties and x509_certificate_properties.key_usage:
            key_usage = [
                KeyUsageType(k) for k in x509_certificate_properties.key_usage
            ]  # type: Optional[List[KeyUsageType]]
        else:
            key_usage = None
        key_properties = certificate_policy_bundle.key_properties
        curve_name = getattr(key_properties, "curve", None)  # missing from 2016-10-01 KeyProperties
        if curve_name:
            curve_name = KeyCurveName(curve_name)

        issuer_parameters = certificate_policy_bundle.issuer_parameters
        return cls(
            issuer_name=issuer_parameters.name if issuer_parameters else None,
            subject=(x509_certificate_properties.subject if x509_certificate_properties else None),
            certificate_type=issuer_parameters.certificate_type if issuer_parameters else None,
            # 2016-10-01 IssuerParameters doesn't have certificate_transparency
            certificate_transparency=getattr(issuer_parameters, "certificate_transparency", None),
            lifetime_actions=lifetime_actions,
            exportable=key_properties.exportable if key_properties else None,
            key_type=KeyType(key_properties.key_type) if key_properties and key_properties.key_type else None,
            key_size=key_properties.key_size if key_properties else None,
            reuse_key=key_properties.reuse_key if key_properties else None,
            key_curve_name=curve_name,
            enhanced_key_usage=x509_certificate_properties.ekus if x509_certificate_properties else None,
            key_usage=key_usage,
            content_type=(
                CertificateContentType(certificate_policy_bundle.secret_properties.content_type)
                if certificate_policy_bundle.secret_properties and
                certificate_policy_bundle.secret_properties.content_type
                else None
            ),
            attributes=certificate_policy_bundle.attributes,
            san_emails=(
                x509_certificate_properties.subject_alternative_names.emails
                if x509_certificate_properties and x509_certificate_properties.subject_alternative_names
                else None
            ),
            san_user_principal_names=(
                x509_certificate_properties.subject_alternative_names.upns
                if x509_certificate_properties and x509_certificate_properties.subject_alternative_names
                else None
            ),
            san_dns_names=(
                x509_certificate_properties.subject_alternative_names.dns_names
                if x509_certificate_properties and x509_certificate_properties.subject_alternative_names
                else None
            ),
            validity_in_months=(
                x509_certificate_properties.validity_in_months if x509_certificate_properties else None
            ),
        )

    @property
    def exportable(self):
        # type: () -> bool
        """Whether the private key can be exported.

        :rtype: bool
        """
        return self._exportable

    @property
    def key_type(self):
        # type: () -> KeyType
        """The type of key pair to be used for the certificate.

        :rtype: ~azure.keyvault.certificates.KeyType
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
    def key_curve_name(self):
        # type: () -> KeyCurveName
        """Elliptic curve name.

        :rtype: ~azure.keyvault.certificates.KeyCurveName
        """
        return self._key_curve_name

    @property
    def enhanced_key_usage(self):
        # type: () -> List[str]
        """The enhanced key usage.

        :rtype: list[str]
        """
        return self._enhanced_key_usage

    @property
    def key_usage(self):
        # type: () -> List[KeyUsageType]
        """List of key usages.

        :rtype: list[~azure.keyvault.certificates.KeyUsageType]
        """
        return self._key_usage

    @property
    def content_type(self):
        # type: () -> CertificateContentType
        """The media type (MIME type).

        :rtype: ~azure.keyvault.certificates.CertificateContentType
        """
        return self._content_type

    @property
    def subject(self):
        # type: () -> str
        """The subject name of the certificate.

        :rtype: str
        """
        return self._subject

    @property
    def san_emails(self):
        # type: () -> Optional[Any]
        """The subject alternative email addresses.

        :rtype: Any or None
        """
        return self._san_emails

    @property
    def san_dns_names(self):
        # type: () -> Optional[Any]
        """The subject alternative domain names.

        :rtype: Any or None
        """
        return self._san_dns_names

    @property
    def san_user_principal_names(self):
        # type: () -> Optional[Any]
        """The subject alternative user principal names.

        :rtype: Any or None
        """
        return self._san_user_principal_names

    @property
    def validity_in_months(self):
        # type: () -> int
        """The duration that the certificate is valid for in months.

        :rtype: int
        """
        return self._validity_in_months

    @property
    def lifetime_actions(self):
        # type: () -> List[LifetimeAction]
        """Actions and their triggers that will be performed by Key Vault over
        the lifetime of the certificate.

        :rtype: list[~azure.keyvault.certificates.LifetimeAction]
        """
        return self._lifetime_actions

    @property
    def issuer_name(self):
        # type: () -> Optional[str]
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
    def created_on(self):
        # type: () -> datetime
        """The datetime when the certificate is created.

        :rtype: ~datetime.datetime
        """
        return self._attributes.created if self._attributes else None

    @property
    def updated_on(self):
        # type: () -> datetime
        """The datetime when the certificate was last updated.

        :rtype: ~datetime.datetime
        """
        return self._attributes.updated if self._attributes else None


class CertificateContact(object):
    """The contact information for the vault certificates.

    :param str email: Email address of a contact for the certificate.
    :param str name: Name of a contact for the certificate.
    :param str phone: phone number of a contact for the certificate.
    """

    def __init__(self, email=None, name=None, phone=None):
        # type: (Optional[str], Optional[str], Optional[str]) -> None
        self._email = email
        self._name = name
        self._phone = phone

    def __repr__(self):
        # type () -> str
        return "CertificateContact(email={}, name={}, phone={})".format(self.email, self.name, self.phone)[:1024]

    def _to_certificate_contacts_item(self):
        # type: (CertificateContact) -> models.Contact
        return models.Contact(email_address=self.email, name=self.name, phone=self.phone)

    @classmethod
    def _from_certificate_contacts_item(cls, contact_item):
        # type: (models.Contact) -> CertificateContact
        """Construct a CertificateContact from an autorest-generated ContactItem."""
        return cls(email=contact_item.email_address, name=contact_item.name, phone=contact_item.phone)

    @property
    def email(self):
        # type: () -> Optional[str]
        """:rtype: str or None"""
        return self._email

    @property
    def name(self):
        # type: () -> Optional[str]
        """:rtype: str or None"""
        return self._name

    @property
    def phone(self):
        # type: () -> Optional[str]
        """:rtype: str or None"""
        return self._phone


class IssuerProperties(object):
    """The properties of an issuer containing the issuer metadata.

    :param str provider: The issuer provider.
    """

    def __init__(self, provider=None, **kwargs):
        # type: (Optional[str], **Any) -> None
        self._id = kwargs.pop("issuer_id", None)
        self._vault_id = parse_key_vault_id(self._id)
        self._provider = provider

    def __repr__(self):
        # type () -> str
        return "IssuerProperties(issuer_id={}, provider={})".format(self.id, self.provider)[:1024]

    @classmethod
    def _from_issuer_item(cls, issuer_item):
        # type: (Union[models.CertificateIssuerItem, models.IssuerBundle]) -> IssuerProperties
        """Construct a IssuerProperties from an autorest-generated CertificateIssuerItem"""
        return cls(issuer_id=issuer_item.id, provider=issuer_item.provider)

    @property
    def id(self):
        # type: () -> str
        """:rtype: str"""
        return self._id

    @property
    def name(self):
        # type: () -> Optional[str]
        # Issuer name is listed under version under vault_id
        """:rtype: str or None"""
        return self._vault_id.version

    @property
    def provider(self):
        # type: () -> Optional[str]
        """:rtype: str or None"""
        return self._provider


class CertificateIssuer(object):
    """The issuer for a Key Vault certificate.

    :param str provider: The issuer provider
    :param str account_id: The username / account name / account id.
    :param str password: The password / secret / account key.
    :param str organization_id: The ID of the organization.
    :param admin_contacts: Details of the organization administrator.
    :type admin_contacts: list[~azure.keyvault.certificates.AdministratorContact]
    """

    def __init__(
        self,
        provider,  # type: Optional[str]
        attributes=None,  # type: Optional[models.IssuerAttributes]
        account_id=None,  # type: Optional[str]
        password=None,  # type: Optional[str]
        organization_id=None,  # type: Optional[str]
        admin_contacts=None,  # type: Optional[List[AdministratorContact]]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        self._provider = provider
        self._attributes = attributes
        self._account_id = account_id
        self._password = password
        self._organization_id = organization_id
        self._admin_contacts = admin_contacts
        self._id = kwargs.pop("issuer_id", None)
        self._vault_id = parse_key_vault_id(self._id)

    def __repr__(self):
        # type () -> str
        return "<CertificateIssuer [{}]>".format(self.id)[:1024]

    @classmethod
    def _from_issuer_bundle(cls, issuer_bundle):
        # type: (models.IssuerBundle) -> CertificateIssuer
        """Construct a CertificateIssuer from an autorest-generated IssuerBundle"""
        admin_contacts = []
        admin_details = (
            issuer_bundle.organization_details.admin_details if issuer_bundle.organization_details else None
        )
        if admin_details:
            # pylint:disable=protected-access
            for admin_detail in admin_details:
                admin_contacts.append(AdministratorContact._from_admin_detail(admin_detail))
        return cls(
            provider=IssuerProperties._from_issuer_item(issuer_bundle).provider,  # pylint: disable=protected-access
            attributes=issuer_bundle.attributes,
            account_id=issuer_bundle.credentials.account_id if issuer_bundle.credentials else None,
            password=issuer_bundle.credentials.password if issuer_bundle.credentials else None,
            organization_id=issuer_bundle.organization_details.id if issuer_bundle.organization_details else None,
            admin_contacts=admin_contacts,
            issuer_id=issuer_bundle.id,
        )

    @property
    def id(self):
        # type: () -> str
        """:rtype: str"""
        return self._id

    @property
    def name(self):
        # type: () -> Optional[str]
        # Issuer name is listed under version under vault_id.
        # This is because the id we pass to parse_key_vault_id has an extra segment, so where most cases the version of
        # the general pattern is certificates/name/version, but here we have certificates/issuers/name/version.
        # Issuers are not versioned.
        """:rtype: str or None"""
        return self._vault_id.version

    @property
    def provider(self):
        # type: () -> Optional[str]
        """The issuer provider.

        :rtype: str or None
        """
        return self._provider

    @property
    def enabled(self):
        # type: () -> Optional[bool]
        """Whether the certificate is enabled or not.

        :rtype: bool or None
        """
        return self._attributes.enabled if self._attributes else None

    @property
    def created_on(self):
        # type: () -> Optional[datetime]
        """The datetime when the certificate is created.

        :rtype: ~datetime.datetime or None
        """
        return self._attributes.created if self._attributes else None

    @property
    def updated_on(self):
        # type: () -> Optional[datetime]
        """The datetime when the certificate was last updated.

        :rtype: ~datetime.datetime or None
        """
        return self._attributes.updated if self._attributes else None

    @property
    def account_id(self):
        # type: () -> Optional[str]
        """The username/ account name/ account id.

        :rtype: str or None
        """
        return self._account_id

    @property
    def password(self):
        # type: () -> Optional[str]
        """The password / secret / account key.

        :rtype: str or None
        """
        return self._password

    @property
    def organization_id(self):
        # type: () -> Optional[str]
        """:rtype: str or None"""
        return self._organization_id

    @property
    def admin_contacts(self):
        # type: () -> Optional[List[AdministratorContact]]
        """Contact details of the organization administrator of this issuer.

        :rtype: list[~azure.keyvault.certificates.AdministratorContact] or None
        """
        return self._admin_contacts


class LifetimeAction(object):
    """Action and its trigger that will be performed by certificate Vault over the
    lifetime of a certificate.

    :param action: The type of the action. For valid values, see CertificatePolicyAction
    :type action: str or ~azure.keyvault.certificates.CertificatePolicyAction
    :param int lifetime_percentage: Percentage of lifetime at which to trigger. Value
        should be between 1 and 99.
    :param int days_before_expiry: Days before expiry to attempt renewal. Value should be between
        1 and validity_in_months multiplied by 27. I.e., if validity_in_months is 36, then value
        should be between 1 and 972 (36 * 27).
    """

    def __init__(self, action, lifetime_percentage=None, days_before_expiry=None):
        # type: (Optional[CertificatePolicyAction], Optional[int], Optional[int]) -> None
        self._lifetime_percentage = lifetime_percentage
        self._days_before_expiry = days_before_expiry
        self._action = action

    def __repr__(self):
        # type () -> str
        return "LifetimeAction(action={}, lifetime_percentage={}, days_before_expiry={})".format(
            self.action, self.lifetime_percentage, self.days_before_expiry
        )[:1024]

    @property
    def lifetime_percentage(self):
        # type: () -> Optional[int]
        """Percentage of lifetime at which to trigger.

        :rtype: int or None
        """
        return self._lifetime_percentage

    @property
    def days_before_expiry(self):
        # type: () -> Optional[int]
        """Days before expiry to attempt renewal.

        :rtype: int or None
        """
        return self._days_before_expiry

    @property
    def action(self):
        # type: () -> Optional[CertificatePolicyAction]
        """The type of the action that will be executed.
        Valid values are "EmailContacts" and "AutoRenew"

        :rtype: ~azure.keyvault.certificates.CertificatePolicyAction or None
        """
        return self._action


class DeletedCertificate(KeyVaultCertificate):
    """A Deleted Certificate consisting of its previous id, attributes and its
    tags, as well as information on when it will be purged.

    :param policy: The management policy of the deleted certificate.
    :type policy: ~azure.keyvault.certificates.CertificatePolicy
    :param bytearray cer: CER contents of the X509 certificate.
    :param datetime deleted_on: The time when the certificate was deleted, in UTC
    :param str recovery_id: The url of the recovery object, used to identify and
        recover the deleted certificate.
    :param datetime scheduled_purge_date: The time when the certificate is scheduled to
        be purged, in UTC
    """

    def __init__(
        self,
        properties=None,  # type: Optional[CertificateProperties]
        policy=None,  # type: Optional[CertificatePolicy]
        cer=None,  # type: Optional[bytes]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        super(DeletedCertificate, self).__init__(properties=properties, policy=policy, cer=cer, **kwargs)
        self._deleted_on = kwargs.get("deleted_on", None)
        self._recovery_id = kwargs.get("recovery_id", None)
        self._scheduled_purge_date = kwargs.get("scheduled_purge_date", None)

    def __repr__(self):
        # type () -> str
        return "<DeletedCertificate [{}]>".format(self.id)[:1024]

    @classmethod
    def _from_deleted_certificate_item(cls, deleted_certificate_item):
        # type: (models.DeletedCertificateItem) -> DeletedCertificate
        """Construct a DeletedCertificate from an autorest-generated DeletedCertificateItem"""
        return cls(
            properties=CertificateProperties._from_certificate_item(  # pylint: disable=protected-access
                deleted_certificate_item
            ),
            key_id=None,
            secret_id=None,
            policy=None,
            cer=None,
            deleted_on=deleted_certificate_item.deleted_date,
            recovery_id=deleted_certificate_item.recovery_id,
            scheduled_purge_date=deleted_certificate_item.scheduled_purge_date,
        )

    @classmethod
    def _from_deleted_certificate_bundle(cls, deleted_certificate_bundle):
        # type: (models.DeletedCertificateBundle) -> DeletedCertificate
        """Construct a DeletedCertificate from an autorest-generated DeletedCertificateItem"""
        # pylint:disable=protected-access
        return cls(
            properties=CertificateProperties._from_certificate_item(deleted_certificate_bundle),
            key_id=deleted_certificate_bundle.kid,
            secret_id=deleted_certificate_bundle.sid,
            policy=CertificatePolicy._from_certificate_policy_bundle(deleted_certificate_bundle.policy),
            cer=deleted_certificate_bundle.cer,
            deleted_on=deleted_certificate_bundle.deleted_date,
            recovery_id=deleted_certificate_bundle.recovery_id,
            scheduled_purge_date=deleted_certificate_bundle.scheduled_purge_date,
        )

    @property
    def deleted_on(self):
        # type: () -> datetime
        """The datetime that the certificate was deleted.

        :rtype: ~datetime.datetime
        """
        return self._deleted_on

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
