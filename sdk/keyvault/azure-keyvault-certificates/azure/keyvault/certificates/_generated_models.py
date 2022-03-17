# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
# pylint: skip-file (avoids crash due to six.with_metaclass https://github.com/PyCQA/astroid/issues/713)
# pylint: disable=too-many-lines

from enum import Enum, EnumMeta
import msrest.serialization
from six import with_metaclass


class Action(msrest.serialization.Model):
    """The action that will be executed.

    :param action_type: The type of the action. Possible values include: "EmailContacts",
     "AutoRenew".
    :type action_type: str or ~azure.keyvault.v7_1.models.ActionType
    """

    _attribute_map = {
        'action_type': {'key': 'action_type', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(Action, self).__init__(**kwargs)
        self.action_type = kwargs.get('action_type', None)


class AdministratorDetails(msrest.serialization.Model):
    """Details of the organization administrator of the certificate issuer.

    :param first_name: First name.
    :type first_name: str
    :param last_name: Last name.
    :type last_name: str
    :param email_address: Email address.
    :type email_address: str
    :param phone: Phone number.
    :type phone: str
    """

    _attribute_map = {
        'first_name': {'key': 'first_name', 'type': 'str'},
        'last_name': {'key': 'last_name', 'type': 'str'},
        'email_address': {'key': 'email', 'type': 'str'},
        'phone': {'key': 'phone', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(AdministratorDetails, self).__init__(**kwargs)
        self.first_name = kwargs.get('first_name', None)
        self.last_name = kwargs.get('last_name', None)
        self.email_address = kwargs.get('email_address', None)
        self.phone = kwargs.get('phone', None)


class Attributes(msrest.serialization.Model):
    """The object attributes managed by the KeyVault service.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param enabled: Determines whether the object is enabled.
    :type enabled: bool
    :param not_before: Not before date in UTC.
    :type not_before: ~datetime.datetime
    :param expires: Expiry date in UTC.
    :type expires: ~datetime.datetime
    :ivar created: Creation time in UTC.
    :vartype created: ~datetime.datetime
    :ivar updated: Last updated time in UTC.
    :vartype updated: ~datetime.datetime
    """

    _validation = {
        'created': {'readonly': True},
        'updated': {'readonly': True},
    }

    _attribute_map = {
        'enabled': {'key': 'enabled', 'type': 'bool'},
        'not_before': {'key': 'nbf', 'type': 'unix-time'},
        'expires': {'key': 'exp', 'type': 'unix-time'},
        'created': {'key': 'created', 'type': 'unix-time'},
        'updated': {'key': 'updated', 'type': 'unix-time'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(Attributes, self).__init__(**kwargs)
        self.enabled = kwargs.get('enabled', None)
        self.not_before = kwargs.get('not_before', None)
        self.expires = kwargs.get('expires', None)
        self.created = None
        self.updated = None


class BackupCertificateResult(msrest.serialization.Model):
    """The backup certificate result, containing the backup blob.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar value: The backup blob containing the backed up certificate.
    :vartype value: bytes
    """

    _validation = {
        'value': {'readonly': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': 'base64'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(BackupCertificateResult, self).__init__(**kwargs)
        self.value = None


class CertificateAttributes(Attributes):
    """The certificate management attributes.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param enabled: Determines whether the object is enabled.
    :type enabled: bool
    :param not_before: Not before date in UTC.
    :type not_before: ~datetime.datetime
    :param expires: Expiry date in UTC.
    :type expires: ~datetime.datetime
    :ivar created: Creation time in UTC.
    :vartype created: ~datetime.datetime
    :ivar updated: Last updated time in UTC.
    :vartype updated: ~datetime.datetime
    :ivar recoverable_days: softDelete data retention days. Value should be >=7 and <=90 when
     softDelete enabled, otherwise 0.
    :vartype recoverable_days: int
    :ivar recovery_level: Reflects the deletion recovery level currently in effect for certificates
     in the current vault. If it contains 'Purgeable', the certificate can be permanently deleted by
     a privileged user; otherwise, only the system can purge the certificate, at the end of the
     retention interval. Possible values include: "Purgeable", "Recoverable+Purgeable",
     "Recoverable", "Recoverable+ProtectedSubscription", "CustomizedRecoverable+Purgeable",
     "CustomizedRecoverable", "CustomizedRecoverable+ProtectedSubscription".
    :vartype recovery_level: str or ~azure.keyvault.v7_1.models.DeletionRecoveryLevel
    """

    _validation = {
        'created': {'readonly': True},
        'updated': {'readonly': True},
        'recoverable_days': {'readonly': True},
        'recovery_level': {'readonly': True},
    }

    _attribute_map = {
        'enabled': {'key': 'enabled', 'type': 'bool'},
        'not_before': {'key': 'nbf', 'type': 'unix-time'},
        'expires': {'key': 'exp', 'type': 'unix-time'},
        'created': {'key': 'created', 'type': 'unix-time'},
        'updated': {'key': 'updated', 'type': 'unix-time'},
        'recoverable_days': {'key': 'recoverableDays', 'type': 'int'},
        'recovery_level': {'key': 'recoveryLevel', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateAttributes, self).__init__(**kwargs)
        self.recoverable_days = None
        self.recovery_level = None


class CertificateBundle(msrest.serialization.Model):
    """A certificate bundle consists of a certificate (X509) plus its attributes.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: The certificate id.
    :vartype id: str
    :ivar kid: The key id.
    :vartype kid: str
    :ivar sid: The secret id.
    :vartype sid: str
    :ivar x509_thumbprint: Thumbprint of the certificate.
    :vartype x509_thumbprint: bytes
    :ivar policy: The management policy.
    :vartype policy: ~azure.keyvault.v7_1.models.CertificatePolicy
    :param cer: CER contents of x509 certificate.
    :type cer: bytearray
    :param content_type: The content type of the secret.
    :type content_type: str
    :param attributes: The certificate attributes.
    :type attributes: ~azure.keyvault.v7_1.models.CertificateAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    """

    _validation = {
        'id': {'readonly': True},
        'kid': {'readonly': True},
        'sid': {'readonly': True},
        'x509_thumbprint': {'readonly': True},
        'policy': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'kid': {'key': 'kid', 'type': 'str'},
        'sid': {'key': 'sid', 'type': 'str'},
        'x509_thumbprint': {'key': 'x5t', 'type': 'base64'},
        'policy': {'key': 'policy', 'type': 'CertificatePolicy'},
        'cer': {'key': 'cer', 'type': 'bytearray'},
        'content_type': {'key': 'contentType', 'type': 'str'},
        'attributes': {'key': 'attributes', 'type': 'CertificateAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateBundle, self).__init__(**kwargs)
        self.id = None
        self.kid = None
        self.sid = None
        self.x509_thumbprint = None
        self.policy = None
        self.cer = kwargs.get('cer', None)
        self.content_type = kwargs.get('content_type', None)
        self.attributes = kwargs.get('attributes', None)
        self.tags = kwargs.get('tags', None)


class CertificateCreateParameters(msrest.serialization.Model):
    """The certificate create parameters.

    :param certificate_policy: The management policy for the certificate.
    :type certificate_policy: ~azure.keyvault.v7_1.models.CertificatePolicy
    :param certificate_attributes: The attributes of the certificate (optional).
    :type certificate_attributes: ~azure.keyvault.v7_1.models.CertificateAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    """

    _attribute_map = {
        'certificate_policy': {'key': 'policy', 'type': 'CertificatePolicy'},
        'certificate_attributes': {'key': 'attributes', 'type': 'CertificateAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateCreateParameters, self).__init__(**kwargs)
        self.certificate_policy = kwargs.get('certificate_policy', None)
        self.certificate_attributes = kwargs.get('certificate_attributes', None)
        self.tags = kwargs.get('tags', None)


class CertificateImportParameters(msrest.serialization.Model):
    """The certificate import parameters.

    All required parameters must be populated in order to send to Azure.

    :param base64_encoded_certificate: Required. A PEM file or a base64-encoded PFX file.  PEM
     files need to contain the private key.
    :type base64_encoded_certificate: str
    :param password: If the private key in base64EncodedCertificate is encrypted, the password used
     for encryption.
    :type password: str
    :param certificate_policy: The management policy for the certificate.
    :type certificate_policy: ~azure.keyvault.v7_1.models.CertificatePolicy
    :param certificate_attributes: The attributes of the certificate (optional).
    :type certificate_attributes: ~azure.keyvault.v7_1.models.CertificateAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    """

    _validation = {
        'base64_encoded_certificate': {'required': True},
    }

    _attribute_map = {
        'base64_encoded_certificate': {'key': 'value', 'type': 'str'},
        'password': {'key': 'pwd', 'type': 'str'},
        'certificate_policy': {'key': 'policy', 'type': 'CertificatePolicy'},
        'certificate_attributes': {'key': 'attributes', 'type': 'CertificateAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateImportParameters, self).__init__(**kwargs)
        self.base64_encoded_certificate = kwargs['base64_encoded_certificate']
        self.password = kwargs.get('password', None)
        self.certificate_policy = kwargs.get('certificate_policy', None)
        self.certificate_attributes = kwargs.get('certificate_attributes', None)
        self.tags = kwargs.get('tags', None)


class CertificateIssuerItem(msrest.serialization.Model):
    """The certificate issuer item containing certificate issuer metadata.

    :param id: Certificate Identifier.
    :type id: str
    :param provider: The issuer provider.
    :type provider: str
    """

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'provider': {'key': 'provider', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateIssuerItem, self).__init__(**kwargs)
        self.id = kwargs.get('id', None)
        self.provider = kwargs.get('provider', None)


class CertificateIssuerListResult(msrest.serialization.Model):
    """The certificate issuer list result.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar value: A response message containing a list of certificate issuers in the key vault along
     with a link to the next page of certificate issuers.
    :vartype value: list[~azure.keyvault.v7_1.models.CertificateIssuerItem]
    :ivar next_link: The URL to get the next set of certificate issuers.
    :vartype next_link: str
    """

    _validation = {
        'value': {'readonly': True},
        'next_link': {'readonly': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': '[CertificateIssuerItem]'},
        'next_link': {'key': 'nextLink', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateIssuerListResult, self).__init__(**kwargs)
        self.value = None
        self.next_link = None


class CertificateIssuerSetParameters(msrest.serialization.Model):
    """The certificate issuer set parameters.

    All required parameters must be populated in order to send to Azure.

    :param provider: Required. The issuer provider.
    :type provider: str
    :param credentials: The credentials to be used for the issuer.
    :type credentials: ~azure.keyvault.v7_1.models.IssuerCredentials
    :param organization_details: Details of the organization as provided to the issuer.
    :type organization_details: ~azure.keyvault.v7_1.models.OrganizationDetails
    :param attributes: Attributes of the issuer object.
    :type attributes: ~azure.keyvault.v7_1.models.IssuerAttributes
    """

    _validation = {
        'provider': {'required': True},
    }

    _attribute_map = {
        'provider': {'key': 'provider', 'type': 'str'},
        'credentials': {'key': 'credentials', 'type': 'IssuerCredentials'},
        'organization_details': {'key': 'org_details', 'type': 'OrganizationDetails'},
        'attributes': {'key': 'attributes', 'type': 'IssuerAttributes'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateIssuerSetParameters, self).__init__(**kwargs)
        self.provider = kwargs['provider']
        self.credentials = kwargs.get('credentials', None)
        self.organization_details = kwargs.get('organization_details', None)
        self.attributes = kwargs.get('attributes', None)


class CertificateIssuerUpdateParameters(msrest.serialization.Model):
    """The certificate issuer update parameters.

    :param provider: The issuer provider.
    :type provider: str
    :param credentials: The credentials to be used for the issuer.
    :type credentials: ~azure.keyvault.v7_1.models.IssuerCredentials
    :param organization_details: Details of the organization as provided to the issuer.
    :type organization_details: ~azure.keyvault.v7_1.models.OrganizationDetails
    :param attributes: Attributes of the issuer object.
    :type attributes: ~azure.keyvault.v7_1.models.IssuerAttributes
    """

    _attribute_map = {
        'provider': {'key': 'provider', 'type': 'str'},
        'credentials': {'key': 'credentials', 'type': 'IssuerCredentials'},
        'organization_details': {'key': 'org_details', 'type': 'OrganizationDetails'},
        'attributes': {'key': 'attributes', 'type': 'IssuerAttributes'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateIssuerUpdateParameters, self).__init__(**kwargs)
        self.provider = kwargs.get('provider', None)
        self.credentials = kwargs.get('credentials', None)
        self.organization_details = kwargs.get('organization_details', None)
        self.attributes = kwargs.get('attributes', None)


class CertificateItem(msrest.serialization.Model):
    """The certificate item containing certificate metadata.

    :param id: Certificate identifier.
    :type id: str
    :param attributes: The certificate management attributes.
    :type attributes: ~azure.keyvault.v7_1.models.CertificateAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :param x509_thumbprint: Thumbprint of the certificate.
    :type x509_thumbprint: bytes
    """

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'attributes': {'key': 'attributes', 'type': 'CertificateAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'x509_thumbprint': {'key': 'x5t', 'type': 'base64'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateItem, self).__init__(**kwargs)
        self.id = kwargs.get('id', None)
        self.attributes = kwargs.get('attributes', None)
        self.tags = kwargs.get('tags', None)
        self.x509_thumbprint = kwargs.get('x509_thumbprint', None)


class CertificateListResult(msrest.serialization.Model):
    """The certificate list result.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar value: A response message containing a list of certificates in the key vault along with a
     link to the next page of certificates.
    :vartype value: list[~azure.keyvault.v7_1.models.CertificateItem]
    :ivar next_link: The URL to get the next set of certificates.
    :vartype next_link: str
    """

    _validation = {
        'value': {'readonly': True},
        'next_link': {'readonly': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': '[CertificateItem]'},
        'next_link': {'key': 'nextLink', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateListResult, self).__init__(**kwargs)
        self.value = None
        self.next_link = None


class CertificateMergeParameters(msrest.serialization.Model):
    """The certificate merge parameters.

    All required parameters must be populated in order to send to Azure.

    :param x509_certificates: Required. The certificate or the certificate chain to merge.
    :type x509_certificates: list[bytearray]
    :param certificate_attributes: The attributes of the certificate (optional).
    :type certificate_attributes: ~azure.keyvault.v7_1.models.CertificateAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    """

    _validation = {
        'x509_certificates': {'required': True},
    }

    _attribute_map = {
        'x509_certificates': {'key': 'x5c', 'type': '[bytearray]'},
        'certificate_attributes': {'key': 'attributes', 'type': 'CertificateAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateMergeParameters, self).__init__(**kwargs)
        self.x509_certificates = kwargs['x509_certificates']
        self.certificate_attributes = kwargs.get('certificate_attributes', None)
        self.tags = kwargs.get('tags', None)


class CertificateOperation(msrest.serialization.Model):
    """A certificate operation is returned in case of asynchronous requests.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: The certificate id.
    :vartype id: str
    :param issuer_parameters: Parameters for the issuer of the X509 component of a certificate.
    :type issuer_parameters: ~azure.keyvault.v7_1.models.IssuerParameters
    :param csr: The certificate signing request (CSR) that is being used in the certificate
     operation.
    :type csr: bytearray
    :param cancellation_requested: Indicates if cancellation was requested on the certificate
     operation.
    :type cancellation_requested: bool
    :param status: Status of the certificate operation.
    :type status: str
    :param status_details: The status details of the certificate operation.
    :type status_details: str
    :param error: Error encountered, if any, during the certificate operation.
    :type error: ~azure.keyvault.v7_1.models.Error
    :param target: Location which contains the result of the certificate operation.
    :type target: str
    :param request_id: Identifier for the certificate operation.
    :type request_id: str
    """

    _validation = {
        'id': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'issuer_parameters': {'key': 'issuer', 'type': 'IssuerParameters'},
        'csr': {'key': 'csr', 'type': 'bytearray'},
        'cancellation_requested': {'key': 'cancellation_requested', 'type': 'bool'},
        'status': {'key': 'status', 'type': 'str'},
        'status_details': {'key': 'status_details', 'type': 'str'},
        'error': {'key': 'error', 'type': 'Error'},
        'target': {'key': 'target', 'type': 'str'},
        'request_id': {'key': 'request_id', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateOperation, self).__init__(**kwargs)
        self.id = None
        self.issuer_parameters = kwargs.get('issuer_parameters', None)
        self.csr = kwargs.get('csr', None)
        self.cancellation_requested = kwargs.get('cancellation_requested', None)
        self.status = kwargs.get('status', None)
        self.status_details = kwargs.get('status_details', None)
        self.error = kwargs.get('error', None)
        self.target = kwargs.get('target', None)
        self.request_id = kwargs.get('request_id', None)


class CertificateOperationUpdateParameter(msrest.serialization.Model):
    """The certificate operation update parameters.

    All required parameters must be populated in order to send to Azure.

    :param cancellation_requested: Required. Indicates if cancellation was requested on the
     certificate operation.
    :type cancellation_requested: bool
    """

    _validation = {
        'cancellation_requested': {'required': True},
    }

    _attribute_map = {
        'cancellation_requested': {'key': 'cancellation_requested', 'type': 'bool'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateOperationUpdateParameter, self).__init__(**kwargs)
        self.cancellation_requested = kwargs['cancellation_requested']


class CertificatePolicy(msrest.serialization.Model):
    """Management policy for a certificate.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: The certificate id.
    :vartype id: str
    :param key_properties: Properties of the key backing a certificate.
    :type key_properties: ~azure.keyvault.v7_1.models.KeyProperties
    :param secret_properties: Properties of the secret backing a certificate.
    :type secret_properties: ~azure.keyvault.v7_1.models.SecretProperties
    :param x509_certificate_properties: Properties of the X509 component of a certificate.
    :type x509_certificate_properties: ~azure.keyvault.v7_1.models.X509CertificateProperties
    :param lifetime_actions: Actions that will be performed by Key Vault over the lifetime of a
     certificate.
    :type lifetime_actions: list[~azure.keyvault.v7_1.models.LifetimeAction]
    :param issuer_parameters: Parameters for the issuer of the X509 component of a certificate.
    :type issuer_parameters: ~azure.keyvault.v7_1.models.IssuerParameters
    :param attributes: The certificate attributes.
    :type attributes: ~azure.keyvault.v7_1.models.CertificateAttributes
    """

    _validation = {
        'id': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'key_properties': {'key': 'key_props', 'type': 'KeyProperties'},
        'secret_properties': {'key': 'secret_props', 'type': 'SecretProperties'},
        'x509_certificate_properties': {'key': 'x509_props', 'type': 'X509CertificateProperties'},
        'lifetime_actions': {'key': 'lifetime_actions', 'type': '[LifetimeAction]'},
        'issuer_parameters': {'key': 'issuer', 'type': 'IssuerParameters'},
        'attributes': {'key': 'attributes', 'type': 'CertificateAttributes'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificatePolicy, self).__init__(**kwargs)
        self.id = None
        self.key_properties = kwargs.get('key_properties', None)
        self.secret_properties = kwargs.get('secret_properties', None)
        self.x509_certificate_properties = kwargs.get('x509_certificate_properties', None)
        self.lifetime_actions = kwargs.get('lifetime_actions', None)
        self.issuer_parameters = kwargs.get('issuer_parameters', None)
        self.attributes = kwargs.get('attributes', None)


class CertificateRestoreParameters(msrest.serialization.Model):
    """The certificate restore parameters.

    All required parameters must be populated in order to send to Azure.

    :param certificate_bundle_backup: Required. The backup blob associated with a certificate
     bundle.
    :type certificate_bundle_backup: bytes
    """

    _validation = {
        'certificate_bundle_backup': {'required': True},
    }

    _attribute_map = {
        'certificate_bundle_backup': {'key': 'value', 'type': 'base64'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateRestoreParameters, self).__init__(**kwargs)
        self.certificate_bundle_backup = kwargs['certificate_bundle_backup']


class CertificateUpdateParameters(msrest.serialization.Model):
    """The certificate update parameters.

    :param certificate_policy: The management policy for the certificate.
    :type certificate_policy: ~azure.keyvault.v7_1.models.CertificatePolicy
    :param certificate_attributes: The attributes of the certificate (optional).
    :type certificate_attributes: ~azure.keyvault.v7_1.models.CertificateAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    """

    _attribute_map = {
        'certificate_policy': {'key': 'policy', 'type': 'CertificatePolicy'},
        'certificate_attributes': {'key': 'attributes', 'type': 'CertificateAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(CertificateUpdateParameters, self).__init__(**kwargs)
        self.certificate_policy = kwargs.get('certificate_policy', None)
        self.certificate_attributes = kwargs.get('certificate_attributes', None)
        self.tags = kwargs.get('tags', None)


class Contact(msrest.serialization.Model):
    """The contact information for the vault certificates.

    :param email_address: Email address.
    :type email_address: str
    :param name: Name.
    :type name: str
    :param phone: Phone number.
    :type phone: str
    """

    _attribute_map = {
        'email_address': {'key': 'email', 'type': 'str'},
        'name': {'key': 'name', 'type': 'str'},
        'phone': {'key': 'phone', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(Contact, self).__init__(**kwargs)
        self.email_address = kwargs.get('email_address', None)
        self.name = kwargs.get('name', None)
        self.phone = kwargs.get('phone', None)


class Contacts(msrest.serialization.Model):
    """The contacts for the vault certificates.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: Identifier for the contacts collection.
    :vartype id: str
    :param contact_list: The contact list for the vault certificates.
    :type contact_list: list[~azure.keyvault.v7_1.models.Contact]
    """

    _validation = {
        'id': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'contact_list': {'key': 'contacts', 'type': '[Contact]'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(Contacts, self).__init__(**kwargs)
        self.id = None
        self.contact_list = kwargs.get('contact_list', None)


class DeletedCertificateBundle(CertificateBundle):
    # pylint: disable=line-too-long
    """A Deleted Certificate consisting of its previous id, attributes and its tags, as well as information on when it will be purged.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: The certificate id.
    :vartype id: str
    :ivar kid: The key id.
    :vartype kid: str
    :ivar sid: The secret id.
    :vartype sid: str
    :ivar x509_thumbprint: Thumbprint of the certificate.
    :vartype x509_thumbprint: bytes
    :ivar policy: The management policy.
    :vartype policy: ~azure.keyvault.v7_1.models.CertificatePolicy
    :param cer: CER contents of x509 certificate.
    :type cer: bytearray
    :param content_type: The content type of the secret.
    :type content_type: str
    :param attributes: The certificate attributes.
    :type attributes: ~azure.keyvault.v7_1.models.CertificateAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :param recovery_id: The url of the recovery object, used to identify and recover the deleted
     certificate.
    :type recovery_id: str
    :ivar scheduled_purge_date: The time when the certificate is scheduled to be purged, in UTC.
    :vartype scheduled_purge_date: ~datetime.datetime
    :ivar deleted_date: The time when the certificate was deleted, in UTC.
    :vartype deleted_date: ~datetime.datetime
    """

    _validation = {
        'id': {'readonly': True},
        'kid': {'readonly': True},
        'sid': {'readonly': True},
        'x509_thumbprint': {'readonly': True},
        'policy': {'readonly': True},
        'scheduled_purge_date': {'readonly': True},
        'deleted_date': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'kid': {'key': 'kid', 'type': 'str'},
        'sid': {'key': 'sid', 'type': 'str'},
        'x509_thumbprint': {'key': 'x5t', 'type': 'base64'},
        'policy': {'key': 'policy', 'type': 'CertificatePolicy'},
        'cer': {'key': 'cer', 'type': 'bytearray'},
        'content_type': {'key': 'contentType', 'type': 'str'},
        'attributes': {'key': 'attributes', 'type': 'CertificateAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'recovery_id': {'key': 'recoveryId', 'type': 'str'},
        'scheduled_purge_date': {'key': 'scheduledPurgeDate', 'type': 'unix-time'},
        'deleted_date': {'key': 'deletedDate', 'type': 'unix-time'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(DeletedCertificateBundle, self).__init__(**kwargs)
        self.recovery_id = kwargs.get('recovery_id', None)
        self.scheduled_purge_date = None
        self.deleted_date = None


class DeletedCertificateItem(CertificateItem):
    """The deleted certificate item containing metadata about the deleted certificate.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param id: Certificate identifier.
    :type id: str
    :param attributes: The certificate management attributes.
    :type attributes: ~azure.keyvault.v7_1.models.CertificateAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :param x509_thumbprint: Thumbprint of the certificate.
    :type x509_thumbprint: bytes
    :param recovery_id: The url of the recovery object, used to identify and recover the deleted
     certificate.
    :type recovery_id: str
    :ivar scheduled_purge_date: The time when the certificate is scheduled to be purged, in UTC.
    :vartype scheduled_purge_date: ~datetime.datetime
    :ivar deleted_date: The time when the certificate was deleted, in UTC.
    :vartype deleted_date: ~datetime.datetime
    """

    _validation = {
        'scheduled_purge_date': {'readonly': True},
        'deleted_date': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'attributes': {'key': 'attributes', 'type': 'CertificateAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'x509_thumbprint': {'key': 'x5t', 'type': 'base64'},
        'recovery_id': {'key': 'recoveryId', 'type': 'str'},
        'scheduled_purge_date': {'key': 'scheduledPurgeDate', 'type': 'unix-time'},
        'deleted_date': {'key': 'deletedDate', 'type': 'unix-time'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(DeletedCertificateItem, self).__init__(**kwargs)
        self.recovery_id = kwargs.get('recovery_id', None)
        self.scheduled_purge_date = None
        self.deleted_date = None


class DeletedCertificateListResult(msrest.serialization.Model):
    """A list of certificates that have been deleted in this vault.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar value: A response message containing a list of deleted certificates in the vault along
     with a link to the next page of deleted certificates.
    :vartype value: list[~azure.keyvault.v7_1.models.DeletedCertificateItem]
    :ivar next_link: The URL to get the next set of deleted certificates.
    :vartype next_link: str
    """

    _validation = {
        'value': {'readonly': True},
        'next_link': {'readonly': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': '[DeletedCertificateItem]'},
        'next_link': {'key': 'nextLink', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(DeletedCertificateListResult, self).__init__(**kwargs)
        self.value = None
        self.next_link = None


class Error(msrest.serialization.Model):
    """The key vault server error.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar code: The error code.
    :vartype code: str
    :ivar message: The error message.
    :vartype message: str
    :ivar inner_error: The key vault server error.
    :vartype inner_error: ~azure.keyvault.v7_1.models.Error
    """

    _validation = {
        'code': {'readonly': True},
        'message': {'readonly': True},
        'inner_error': {'readonly': True},
    }

    _attribute_map = {
        'code': {'key': 'code', 'type': 'str'},
        'message': {'key': 'message', 'type': 'str'},
        'inner_error': {'key': 'innererror', 'type': 'Error'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(Error, self).__init__(**kwargs)
        self.code = None
        self.message = None
        self.inner_error = None


class IssuerAttributes(msrest.serialization.Model):
    """The attributes of an issuer managed by the Key Vault service.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param enabled: Determines whether the issuer is enabled.
    :type enabled: bool
    :ivar created: Creation time in UTC.
    :vartype created: ~datetime.datetime
    :ivar updated: Last updated time in UTC.
    :vartype updated: ~datetime.datetime
    """

    _validation = {
        'created': {'readonly': True},
        'updated': {'readonly': True},
    }

    _attribute_map = {
        'enabled': {'key': 'enabled', 'type': 'bool'},
        'created': {'key': 'created', 'type': 'unix-time'},
        'updated': {'key': 'updated', 'type': 'unix-time'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(IssuerAttributes, self).__init__(**kwargs)
        self.enabled = kwargs.get('enabled', None)
        self.created = None
        self.updated = None


class IssuerBundle(msrest.serialization.Model):
    """The issuer for Key Vault certificate.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: Identifier for the issuer object.
    :vartype id: str
    :param provider: The issuer provider.
    :type provider: str
    :param credentials: The credentials to be used for the issuer.
    :type credentials: ~azure.keyvault.v7_1.models.IssuerCredentials
    :param organization_details: Details of the organization as provided to the issuer.
    :type organization_details: ~azure.keyvault.v7_1.models.OrganizationDetails
    :param attributes: Attributes of the issuer object.
    :type attributes: ~azure.keyvault.v7_1.models.IssuerAttributes
    """

    _validation = {
        'id': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'provider': {'key': 'provider', 'type': 'str'},
        'credentials': {'key': 'credentials', 'type': 'IssuerCredentials'},
        'organization_details': {'key': 'org_details', 'type': 'OrganizationDetails'},
        'attributes': {'key': 'attributes', 'type': 'IssuerAttributes'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(IssuerBundle, self).__init__(**kwargs)
        self.id = None
        self.provider = kwargs.get('provider', None)
        self.credentials = kwargs.get('credentials', None)
        self.organization_details = kwargs.get('organization_details', None)
        self.attributes = kwargs.get('attributes', None)


class IssuerCredentials(msrest.serialization.Model):
    """The credentials to be used for the certificate issuer.

    :param account_id: The user name/account name/account id.
    :type account_id: str
    :param password: The password/secret/account key.
    :type password: str
    """

    _attribute_map = {
        'account_id': {'key': 'account_id', 'type': 'str'},
        'password': {'key': 'pwd', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(IssuerCredentials, self).__init__(**kwargs)
        self.account_id = kwargs.get('account_id', None)
        self.password = kwargs.get('password', None)


class IssuerParameters(msrest.serialization.Model):
    """Parameters for the issuer of the X509 component of a certificate.

    :param name: Name of the referenced issuer object or reserved names; for example, 'Self' or
     'Unknown'.
    :type name: str
    :param certificate_type: Certificate type as supported by the provider (optional); for example
     'OV-SSL', 'EV-SSL'.
    :type certificate_type: str
    :param certificate_transparency: Indicates if the certificates generated under this policy
     should be published to certificate transparency logs.
    :type certificate_transparency: bool
    """

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'certificate_type': {'key': 'cty', 'type': 'str'},
        'certificate_transparency': {'key': 'cert_transparency', 'type': 'bool'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(IssuerParameters, self).__init__(**kwargs)
        self.name = kwargs.get('name', None)
        self.certificate_type = kwargs.get('certificate_type', None)
        self.certificate_transparency = kwargs.get('certificate_transparency', None)


class KeyProperties(msrest.serialization.Model):
    """Properties of the key pair backing a certificate.

    :param exportable: Not supported in this version. Indicates if the private key can be exported.
    :type exportable: bool
    :param key_type: The type of key pair to be used for the certificate. Possible values include:
     "EC", "EC-HSM", "RSA", "RSA-HSM", "oct".
    :type key_type: str or ~azure.keyvault.v7_1.models.JsonWebKeyType
    :param key_size: The key size in bits. For example: 2048, 3072, or 4096 for RSA.
    :type key_size: int
    :param reuse_key: Indicates if the same key pair will be used on certificate renewal.
    :type reuse_key: bool
    :param curve: Elliptic curve name. For valid values, see JsonWebKeyCurveName. Possible values
     include: "P-256", "P-384", "P-521", "P-256K".
    :type curve: str or ~azure.keyvault.v7_1.models.JsonWebKeyCurveName
    """

    _attribute_map = {
        'exportable': {'key': 'exportable', 'type': 'bool'},
        'key_type': {'key': 'kty', 'type': 'str'},
        'key_size': {'key': 'key_size', 'type': 'int'},
        'reuse_key': {'key': 'reuse_key', 'type': 'bool'},
        'curve': {'key': 'crv', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyProperties, self).__init__(**kwargs)
        self.exportable = kwargs.get('exportable', None)
        self.key_type = kwargs.get('key_type', None)
        self.key_size = kwargs.get('key_size', None)
        self.reuse_key = kwargs.get('reuse_key', None)
        self.curve = kwargs.get('curve', None)


class KeyVaultError(msrest.serialization.Model):
    """The key vault error exception.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar error: The key vault server error.
    :vartype error: ~azure.keyvault.v7_1.models.Error
    """

    _validation = {
        'error': {'readonly': True},
    }

    _attribute_map = {
        'error': {'key': 'error', 'type': 'Error'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyVaultError, self).__init__(**kwargs)
        self.error = None


class LifetimeAction(msrest.serialization.Model):
    """Action and its trigger that will be performed by Key Vault over the lifetime of a certificate.

    :param trigger: The condition that will execute the action.
    :type trigger: ~azure.keyvault.v7_1.models.Trigger
    :param action: The action that will be executed.
    :type action: ~azure.keyvault.v7_1.models.Action
    """

    _attribute_map = {
        'trigger': {'key': 'trigger', 'type': 'Trigger'},
        'action': {'key': 'action', 'type': 'Action'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(LifetimeAction, self).__init__(**kwargs)
        self.trigger = kwargs.get('trigger', None)
        self.action = kwargs.get('action', None)


class OrganizationDetails(msrest.serialization.Model):
    """Details of the organization of the certificate issuer.

    :param id: Id of the organization.
    :type id: str
    :param admin_details: Details of the organization administrator.
    :type admin_details: list[~azure.keyvault.v7_1.models.AdministratorDetails]
    """

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'admin_details': {'key': 'admin_details', 'type': '[AdministratorDetails]'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(OrganizationDetails, self).__init__(**kwargs)
        self.id = kwargs.get('id', None)
        self.admin_details = kwargs.get('admin_details', None)


class PendingCertificateSigningRequestResult(msrest.serialization.Model):
    """The pending certificate signing request result.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar value: The pending certificate signing request as Base64 encoded string.
    :vartype value: str
    """

    _validation = {
        'value': {'readonly': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(PendingCertificateSigningRequestResult, self).__init__(**kwargs)
        self.value = None


class SecretProperties(msrest.serialization.Model):
    """Properties of the key backing a certificate.

    :param content_type: The media type (MIME type).
    :type content_type: str
    """

    _attribute_map = {
        'content_type': {'key': 'contentType', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SecretProperties, self).__init__(**kwargs)
        self.content_type = kwargs.get('content_type', None)


class SubjectAlternativeNames(msrest.serialization.Model):
    """The subject alternate names of a X509 object.

    :param emails: Email addresses.
    :type emails: list[str]
    :param dns_names: Domain names.
    :type dns_names: list[str]
    :param upns: User principal names.
    :type upns: list[str]
    """

    _attribute_map = {
        'emails': {'key': 'emails', 'type': '[str]'},
        'dns_names': {'key': 'dns_names', 'type': '[str]'},
        'upns': {'key': 'upns', 'type': '[str]'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SubjectAlternativeNames, self).__init__(**kwargs)
        self.emails = kwargs.get('emails', None)
        self.dns_names = kwargs.get('dns_names', None)
        self.upns = kwargs.get('upns', None)


class Trigger(msrest.serialization.Model):
    """A condition to be satisfied for an action to be executed.

    :param lifetime_percentage: Percentage of lifetime at which to trigger. Value should be between
     1 and 99.
    :type lifetime_percentage: int
    :param days_before_expiry: Days before expiry to attempt renewal. Value should be between 1 and
     validity_in_months multiplied by 27. If validity_in_months is 36, then value should be between
     1 and 972 (36 * 27).
    :type days_before_expiry: int
    """

    _validation = {
        'lifetime_percentage': {'maximum': 99, 'minimum': 1},
    }

    _attribute_map = {
        'lifetime_percentage': {'key': 'lifetime_percentage', 'type': 'int'},
        'days_before_expiry': {'key': 'days_before_expiry', 'type': 'int'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(Trigger, self).__init__(**kwargs)
        self.lifetime_percentage = kwargs.get('lifetime_percentage', None)
        self.days_before_expiry = kwargs.get('days_before_expiry', None)


class X509CertificateProperties(msrest.serialization.Model):
    """Properties of the X509 component of a certificate.

    :param subject: The subject name. Should be a valid X509 distinguished Name.
    :type subject: str
    :param ekus: The enhanced key usage.
    :type ekus: list[str]
    :param subject_alternative_names: The subject alternative names.
    :type subject_alternative_names: ~azure.keyvault.v7_1.models.SubjectAlternativeNames
    :param key_usage: List of key usages.
    :type key_usage: list[str or ~azure.keyvault.v7_1.models.KeyUsageType]
    :param validity_in_months: The duration that the certificate is valid in months.
    :type validity_in_months: int
    """

    _validation = {
        'validity_in_months': {'minimum': 0},
    }

    _attribute_map = {
        'subject': {'key': 'subject', 'type': 'str'},
        'ekus': {'key': 'ekus', 'type': '[str]'},
        'subject_alternative_names': {'key': 'sans', 'type': 'SubjectAlternativeNames'},
        'key_usage': {'key': 'key_usage', 'type': '[str]'},
        'validity_in_months': {'key': 'validity_months', 'type': 'int'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(X509CertificateProperties, self).__init__(**kwargs)
        self.subject = kwargs.get('subject', None)
        self.ekus = kwargs.get('ekus', None)
        self.subject_alternative_names = kwargs.get('subject_alternative_names', None)
        self.key_usage = kwargs.get('key_usage', None)
        self.validity_in_months = kwargs.get('validity_in_months', None)


class _CaseInsensitiveEnumMeta(EnumMeta):
    def __getitem__(self, name):
        return super().__getitem__(name.upper())

    def __getattr__(cls, name):
        """Return the enum member matching `name`
        We use __getattr__ instead of descriptors or inserting into the enum
        class' __dict__ in order to support `name` and `value` being both
        properties for enum members (which live in the class' __dict__) and
        enum members themselves.
        """
        try:
            return cls._member_map_[name.upper()]
        except KeyError:
            raise AttributeError(name)


class ActionType(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The type of the action.
    """

    EMAIL_CONTACTS = "EmailContacts"
    AUTO_RENEW = "AutoRenew"

class DeletionRecoveryLevel(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """Reflects the deletion recovery level currently in effect for certificates in the current vault.
    If it contains 'Purgeable', the certificate can be permanently deleted by a privileged user;
    otherwise, only the system can purge the certificate, at the end of the retention interval.
    """

    #: Denotes a vault state in which deletion is an irreversible operation, without the possibility
    #: for recovery. This level corresponds to no protection being available against a Delete
    #: operation; the data is irretrievably lost upon accepting a Delete operation at the entity level
    #: or higher (vault, resource group, subscription etc.).
    PURGEABLE = "Purgeable"
    #: Denotes a vault state in which deletion is recoverable, and which also permits immediate and
    #: permanent deletion (i.e. purge). This level guarantees the recoverability of the deleted entity
    #: during the retention interval (90 days), unless a Purge operation is requested, or the
    #: subscription is cancelled. System wil permanently delete it after 90 days, if not recovered.
    RECOVERABLE_PURGEABLE = "Recoverable+Purgeable"
    #: Denotes a vault state in which deletion is recoverable without the possibility for immediate
    #: and permanent deletion (i.e. purge). This level guarantees the recoverability of the deleted
    #: entity during the retention interval(90 days) and while the subscription is still available.
    #: System wil permanently delete it after 90 days, if not recovered.
    RECOVERABLE = "Recoverable"
    #: Denotes a vault and subscription state in which deletion is recoverable within retention
    #: interval (90 days), immediate and permanent deletion (i.e. purge) is not permitted, and in
    #: which the subscription itself  cannot be permanently canceled. System wil permanently delete it
    #: after 90 days, if not recovered.
    RECOVERABLE_PROTECTED_SUBSCRIPTION = "Recoverable+ProtectedSubscription"
    #: Denotes a vault state in which deletion is recoverable, and which also permits immediate and
    #: permanent deletion (i.e. purge when 7<= SoftDeleteRetentionInDays < 90). This level guarantees
    #: the recoverability of the deleted entity during the retention interval, unless a Purge
    #: operation is requested, or the subscription is cancelled.
    CUSTOMIZED_RECOVERABLE_PURGEABLE = "CustomizedRecoverable+Purgeable"
    #: Denotes a vault state in which deletion is recoverable without the possibility for immediate
    #: and permanent deletion (i.e. purge when 7<= SoftDeleteRetentionInDays < 90).This level
    #: guarantees the recoverability of the deleted entity during the retention interval and while the
    #: subscription is still available.
    CUSTOMIZED_RECOVERABLE = "CustomizedRecoverable"
    #: Denotes a vault and subscription state in which deletion is recoverable, immediate and
    #: permanent deletion (i.e. purge) is not permitted, and in which the subscription itself cannot
    #: be permanently canceled when 7<= SoftDeleteRetentionInDays < 90. This level guarantees the
    #: recoverability of the deleted entity during the retention interval, and also reflects the fact
    #: that the subscription itself cannot be cancelled.
    CUSTOMIZED_RECOVERABLE_PROTECTED_SUBSCRIPTION = "CustomizedRecoverable+ProtectedSubscription"

class JsonWebKeyCurveName(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """Elliptic curve name. For valid values, see JsonWebKeyCurveName.
    """

    P256 = "P-256"
    P384 = "P-384"
    P521 = "P-521"
    P256_K = "P-256K"

class JsonWebKeyType(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The type of key pair to be used for the certificate.
    """

    EC = "EC"
    EC_HSM = "EC-HSM"
    RSA = "RSA"
    RSA_HSM = "RSA-HSM"
    OCT = "oct"

class KeyUsageType(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):

    DIGITAL_SIGNATURE = "digitalSignature"
    NON_REPUDIATION = "nonRepudiation"
    KEY_ENCIPHERMENT = "keyEncipherment"
    DATA_ENCIPHERMENT = "dataEncipherment"
    KEY_AGREEMENT = "keyAgreement"
    KEY_CERT_SIGN = "keyCertSign"
    C_RL_SIGN = "cRLSign"
    ENCIPHER_ONLY = "encipherOnly"
    DECIPHER_ONLY = "decipherOnly"
