# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
# pylint: skip-file (avoids crash due to six.with_metaclass https://github.com/PyCQA/astroid/issues/713)

from enum import Enum, EnumMeta
import msrest.serialization
from six import with_metaclass


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


class BackupKeyResult(msrest.serialization.Model):
    """The backup key result, containing the backup blob.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar value: The backup blob containing the backed up key.
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
        super(BackupKeyResult, self).__init__(**kwargs)
        self.value = None


class KeyBundle(msrest.serialization.Model):
    """A KeyBundle consisting of a WebKey plus its attributes.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param key: The Json web key.
    :type key: ~azure.keyvault.v7_1.models.JsonWebKey
    :param attributes: The key management attributes.
    :type attributes: ~azure.keyvault.v7_1.models.KeyAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :ivar managed: True if the key's lifetime is managed by key vault. If this is a key backing a
     certificate, then managed will be true.
    :vartype managed: bool
    """

    _validation = {
        'managed': {'readonly': True},
    }

    _attribute_map = {
        'key': {'key': 'key', 'type': 'JsonWebKey'},
        'attributes': {'key': 'attributes', 'type': 'KeyAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'managed': {'key': 'managed', 'type': 'bool'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyBundle, self).__init__(**kwargs)
        self.key = kwargs.get('key', None)
        self.attributes = kwargs.get('attributes', None)
        self.tags = kwargs.get('tags', None)
        self.managed = None


class DeletedKeyBundle(KeyBundle):
    """A DeletedKeyBundle consisting of a WebKey plus its Attributes and deletion info.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param key: The Json web key.
    :type key: ~azure.keyvault.v7_1.models.JsonWebKey
    :param attributes: The key management attributes.
    :type attributes: ~azure.keyvault.v7_1.models.KeyAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :ivar managed: True if the key's lifetime is managed by key vault. If this is a key backing a
     certificate, then managed will be true.
    :vartype managed: bool
    :param recovery_id: The url of the recovery object, used to identify and recover the deleted
     key.
    :type recovery_id: str
    :ivar scheduled_purge_date: The time when the key is scheduled to be purged, in UTC.
    :vartype scheduled_purge_date: ~datetime.datetime
    :ivar deleted_date: The time when the key was deleted, in UTC.
    :vartype deleted_date: ~datetime.datetime
    """

    _validation = {
        'managed': {'readonly': True},
        'scheduled_purge_date': {'readonly': True},
        'deleted_date': {'readonly': True},
    }

    _attribute_map = {
        'key': {'key': 'key', 'type': 'JsonWebKey'},
        'attributes': {'key': 'attributes', 'type': 'KeyAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'managed': {'key': 'managed', 'type': 'bool'},
        'recovery_id': {'key': 'recoveryId', 'type': 'str'},
        'scheduled_purge_date': {'key': 'scheduledPurgeDate', 'type': 'unix-time'},
        'deleted_date': {'key': 'deletedDate', 'type': 'unix-time'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(DeletedKeyBundle, self).__init__(**kwargs)
        self.recovery_id = kwargs.get('recovery_id', None)
        self.scheduled_purge_date = None
        self.deleted_date = None


class KeyItem(msrest.serialization.Model):
    """The key item containing key metadata.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param kid: Key identifier.
    :type kid: str
    :param attributes: The key management attributes.
    :type attributes: ~azure.keyvault.v7_1.models.KeyAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :ivar managed: True if the key's lifetime is managed by key vault. If this is a key backing a
     certificate, then managed will be true.
    :vartype managed: bool
    """

    _validation = {
        'managed': {'readonly': True},
    }

    _attribute_map = {
        'kid': {'key': 'kid', 'type': 'str'},
        'attributes': {'key': 'attributes', 'type': 'KeyAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'managed': {'key': 'managed', 'type': 'bool'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyItem, self).__init__(**kwargs)
        self.kid = kwargs.get('kid', None)
        self.attributes = kwargs.get('attributes', None)
        self.tags = kwargs.get('tags', None)
        self.managed = None


class DeletedKeyItem(KeyItem):
    """The deleted key item containing the deleted key metadata and information about deletion.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param kid: Key identifier.
    :type kid: str
    :param attributes: The key management attributes.
    :type attributes: ~azure.keyvault.v7_1.models.KeyAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :ivar managed: True if the key's lifetime is managed by key vault. If this is a key backing a
     certificate, then managed will be true.
    :vartype managed: bool
    :param recovery_id: The url of the recovery object, used to identify and recover the deleted
     key.
    :type recovery_id: str
    :ivar scheduled_purge_date: The time when the key is scheduled to be purged, in UTC.
    :vartype scheduled_purge_date: ~datetime.datetime
    :ivar deleted_date: The time when the key was deleted, in UTC.
    :vartype deleted_date: ~datetime.datetime
    """

    _validation = {
        'managed': {'readonly': True},
        'scheduled_purge_date': {'readonly': True},
        'deleted_date': {'readonly': True},
    }

    _attribute_map = {
        'kid': {'key': 'kid', 'type': 'str'},
        'attributes': {'key': 'attributes', 'type': 'KeyAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'managed': {'key': 'managed', 'type': 'bool'},
        'recovery_id': {'key': 'recoveryId', 'type': 'str'},
        'scheduled_purge_date': {'key': 'scheduledPurgeDate', 'type': 'unix-time'},
        'deleted_date': {'key': 'deletedDate', 'type': 'unix-time'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(DeletedKeyItem, self).__init__(**kwargs)
        self.recovery_id = kwargs.get('recovery_id', None)
        self.scheduled_purge_date = None
        self.deleted_date = None


class DeletedKeyListResult(msrest.serialization.Model):
    """A list of keys that have been deleted in this vault.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar value: A response message containing a list of deleted keys in the vault along with a
     link to the next page of deleted keys.
    :vartype value: list[~azure.keyvault.v7_1.models.DeletedKeyItem]
    :ivar next_link: The URL to get the next set of deleted keys.
    :vartype next_link: str
    """

    _validation = {
        'value': {'readonly': True},
        'next_link': {'readonly': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': '[DeletedKeyItem]'},
        'next_link': {'key': 'nextLink', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(DeletedKeyListResult, self).__init__(**kwargs)
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


class JsonWebKey(msrest.serialization.Model):
    # pylint: disable=too-many-instance-attributes
    """As of http://tools.ietf.org/html/draft-ietf-jose-json-web-key-18.

    :param kid: Key identifier.
    :type kid: str
    :param kty: JsonWebKey Key Type (kty), as defined in
     https://tools.ietf.org/html/draft-ietf-jose-json-web-algorithms-40. Possible values include:
     "EC", "EC-HSM", "RSA", "RSA-HSM", "oct".
    :type kty: str or ~azure.keyvault.v7_1.models.JsonWebKeyType
    :param key_ops:
    :type key_ops: list[str]
    :param n: RSA modulus.
    :type n: bytes
    :param e: RSA public exponent.
    :type e: bytes
    :param d: RSA private exponent, or the D component of an EC private key.
    :type d: bytes
    :param dp: RSA private key parameter.
    :type dp: bytes
    :param dq: RSA private key parameter.
    :type dq: bytes
    :param qi: RSA private key parameter.
    :type qi: bytes
    :param p: RSA secret prime.
    :type p: bytes
    :param q: RSA secret prime, with p < q.
    :type q: bytes
    :param k: Symmetric key.
    :type k: bytes
    :param t: HSM Token, used with 'Bring Your Own Key'.
    :type t: bytes
    :param crv: Elliptic curve name. For valid values, see JsonWebKeyCurveName. Possible values
     include: "P-256", "P-384", "P-521", "P-256K".
    :type crv: str or ~azure.keyvault.v7_1.models.JsonWebKeyCurveName
    :param x: X component of an EC public key.
    :type x: bytes
    :param y: Y component of an EC public key.
    :type y: bytes
    """

    _attribute_map = {
        'kid': {'key': 'kid', 'type': 'str'},
        'kty': {'key': 'kty', 'type': 'str'},
        'key_ops': {'key': 'key_ops', 'type': '[str]'},
        'n': {'key': 'n', 'type': 'base64'},
        'e': {'key': 'e', 'type': 'base64'},
        'd': {'key': 'd', 'type': 'base64'},
        'dp': {'key': 'dp', 'type': 'base64'},
        'dq': {'key': 'dq', 'type': 'base64'},
        'qi': {'key': 'qi', 'type': 'base64'},
        'p': {'key': 'p', 'type': 'base64'},
        'q': {'key': 'q', 'type': 'base64'},
        'k': {'key': 'k', 'type': 'base64'},
        't': {'key': 'key_hsm', 'type': 'base64'},
        'crv': {'key': 'crv', 'type': 'str'},
        'x': {'key': 'x', 'type': 'base64'},
        'y': {'key': 'y', 'type': 'base64'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(JsonWebKey, self).__init__(**kwargs)
        self.kid = kwargs.get('kid', None)
        self.kty = kwargs.get('kty', None)
        self.key_ops = kwargs.get('key_ops', None)
        self.n = kwargs.get('n', None)
        self.e = kwargs.get('e', None)
        self.d = kwargs.get('d', None)
        self.dp = kwargs.get('dp', None)
        self.dq = kwargs.get('dq', None)
        self.qi = kwargs.get('qi', None)
        self.p = kwargs.get('p', None)
        self.q = kwargs.get('q', None)
        self.k = kwargs.get('k', None)
        self.t = kwargs.get('t', None)
        self.crv = kwargs.get('crv', None)
        self.x = kwargs.get('x', None)
        self.y = kwargs.get('y', None)


class KeyAttributes(Attributes):
    """The attributes of a key managed by the key vault service.

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
    :ivar recovery_level: Reflects the deletion recovery level currently in effect for keys in the
     current vault. If it contains 'Purgeable' the key can be permanently deleted by a privileged
     user; otherwise, only the system can purge the key, at the end of the retention interval.
     Possible values include: "Purgeable", "Recoverable+Purgeable", "Recoverable",
     "Recoverable+ProtectedSubscription", "CustomizedRecoverable+Purgeable",
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
        super(KeyAttributes, self).__init__(**kwargs)
        self.recoverable_days = None
        self.recovery_level = None


class KeyCreateParameters(msrest.serialization.Model):
    """The key create parameters.

    All required parameters must be populated in order to send to Azure.

    :param kty: Required. The type of key to create. For valid values, see JsonWebKeyType. Possible
     values include: "EC", "EC-HSM", "RSA", "RSA-HSM", "oct".
    :type kty: str or ~azure.keyvault.v7_1.models.JsonWebKeyType
    :param key_size: The key size in bits. For example: 2048, 3072, or 4096 for RSA.
    :type key_size: int
    :param key_ops:
    :type key_ops: list[str or ~azure.keyvault.v7_1.models.JsonWebKeyOperation]
    :param key_attributes: The attributes of a key managed by the key vault service.
    :type key_attributes: ~azure.keyvault.v7_1.models.KeyAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :param curve: Elliptic curve name. For valid values, see JsonWebKeyCurveName. Possible values
     include: "P-256", "P-384", "P-521", "P-256K".
    :type curve: str or ~azure.keyvault.v7_1.models.JsonWebKeyCurveName
    """

    _validation = {
        'kty': {'required': True},
    }

    _attribute_map = {
        'kty': {'key': 'kty', 'type': 'str'},
        'key_size': {'key': 'key_size', 'type': 'int'},
        'key_ops': {'key': 'key_ops', 'type': '[str]'},
        'key_attributes': {'key': 'attributes', 'type': 'KeyAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'curve': {'key': 'crv', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyCreateParameters, self).__init__(**kwargs)
        self.kty = kwargs['kty']
        self.key_size = kwargs.get('key_size', None)
        self.key_ops = kwargs.get('key_ops', None)
        self.key_attributes = kwargs.get('key_attributes', None)
        self.tags = kwargs.get('tags', None)
        self.curve = kwargs.get('curve', None)


class KeyImportParameters(msrest.serialization.Model):
    """The key import parameters.

    All required parameters must be populated in order to send to Azure.

    :param hsm: Whether to import as a hardware key (HSM) or software key.
    :type hsm: bool
    :param key: Required. The Json web key.
    :type key: ~azure.keyvault.v7_1.models.JsonWebKey
    :param key_attributes: The key management attributes.
    :type key_attributes: ~azure.keyvault.v7_1.models.KeyAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    """

    _validation = {
        'key': {'required': True},
    }

    _attribute_map = {
        'hsm': {'key': 'Hsm', 'type': 'bool'},
        'key': {'key': 'key', 'type': 'JsonWebKey'},
        'key_attributes': {'key': 'attributes', 'type': 'KeyAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyImportParameters, self).__init__(**kwargs)
        self.hsm = kwargs.get('hsm', None)
        self.key = kwargs['key']
        self.key_attributes = kwargs.get('key_attributes', None)
        self.tags = kwargs.get('tags', None)


class KeyListResult(msrest.serialization.Model):
    """The key list result.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar value: A response message containing a list of keys in the key vault along with a link to
     the next page of keys.
    :vartype value: list[~azure.keyvault.v7_1.models.KeyItem]
    :ivar next_link: The URL to get the next set of keys.
    :vartype next_link: str
    """

    _validation = {
        'value': {'readonly': True},
        'next_link': {'readonly': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': '[KeyItem]'},
        'next_link': {'key': 'nextLink', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyListResult, self).__init__(**kwargs)
        self.value = None
        self.next_link = None


class KeyOperationResult(msrest.serialization.Model):
    """The key operation result.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar kid: Key identifier.
    :vartype kid: str
    :ivar result:
    :vartype result: bytes
    """

    _validation = {
        'kid': {'readonly': True},
        'result': {'readonly': True},
    }

    _attribute_map = {
        'kid': {'key': 'kid', 'type': 'str'},
        'result': {'key': 'value', 'type': 'base64'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyOperationResult, self).__init__(**kwargs)
        self.kid = None
        self.result = None


class KeyOperationsParameters(msrest.serialization.Model):
    """The key operations parameters.

    All required parameters must be populated in order to send to Azure.

    :param algorithm: Required. algorithm identifier. Possible values include: "RSA-OAEP",
     "RSA-OAEP-256", "RSA1_5".
    :type algorithm: str or ~azure.keyvault.v7_1.models.JsonWebKeyEncryptionAlgorithm
    :param value: Required.
    :type value: bytes
    """

    _validation = {
        'algorithm': {'required': True},
        'value': {'required': True},
    }

    _attribute_map = {
        'algorithm': {'key': 'alg', 'type': 'str'},
        'value': {'key': 'value', 'type': 'base64'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyOperationsParameters, self).__init__(**kwargs)
        self.algorithm = kwargs['algorithm']
        self.value = kwargs['value']


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


class KeyRestoreParameters(msrest.serialization.Model):
    """The key restore parameters.

    All required parameters must be populated in order to send to Azure.

    :param key_bundle_backup: Required. The backup blob associated with a key bundle.
    :type key_bundle_backup: bytes
    """

    _validation = {
        'key_bundle_backup': {'required': True},
    }

    _attribute_map = {
        'key_bundle_backup': {'key': 'value', 'type': 'base64'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyRestoreParameters, self).__init__(**kwargs)
        self.key_bundle_backup = kwargs['key_bundle_backup']


class KeySignParameters(msrest.serialization.Model):
    """The key operations parameters.

    All required parameters must be populated in order to send to Azure.

    :param algorithm: Required. The signing/verification algorithm identifier. For more information
     on possible algorithm types, see JsonWebKeySignatureAlgorithm. Possible values include:
     "PS256", "PS384", "PS512", "RS256", "RS384", "RS512", "RSNULL", "ES256", "ES384", "ES512",
     "ES256K".
    :type algorithm: str or ~azure.keyvault.v7_1.models.JsonWebKeySignatureAlgorithm
    :param value: Required.
    :type value: bytes
    """

    _validation = {
        'algorithm': {'required': True},
        'value': {'required': True},
    }

    _attribute_map = {
        'algorithm': {'key': 'alg', 'type': 'str'},
        'value': {'key': 'value', 'type': 'base64'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeySignParameters, self).__init__(**kwargs)
        self.algorithm = kwargs['algorithm']
        self.value = kwargs['value']


class KeyUpdateParameters(msrest.serialization.Model):
    """The key update parameters.

    :param key_ops: Json web key operations. For more information on possible key operations, see
     JsonWebKeyOperation.
    :type key_ops: list[str or ~azure.keyvault.v7_1.models.JsonWebKeyOperation]
    :param key_attributes: The attributes of a key managed by the key vault service.
    :type key_attributes: ~azure.keyvault.v7_1.models.KeyAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    """

    _attribute_map = {
        'key_ops': {'key': 'key_ops', 'type': '[str]'},
        'key_attributes': {'key': 'attributes', 'type': 'KeyAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyUpdateParameters, self).__init__(**kwargs)
        self.key_ops = kwargs.get('key_ops', None)
        self.key_attributes = kwargs.get('key_attributes', None)
        self.tags = kwargs.get('tags', None)


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


class KeyVerifyParameters(msrest.serialization.Model):
    """The key verify parameters.

    All required parameters must be populated in order to send to Azure.

    :param algorithm: Required. The signing/verification algorithm. For more information on
     possible algorithm types, see JsonWebKeySignatureAlgorithm. Possible values include: "PS256",
     "PS384", "PS512", "RS256", "RS384", "RS512", "RSNULL", "ES256", "ES384", "ES512", "ES256K".
    :type algorithm: str or ~azure.keyvault.v7_1.models.JsonWebKeySignatureAlgorithm
    :param digest: Required. The digest used for signing.
    :type digest: bytes
    :param signature: Required. The signature to be verified.
    :type signature: bytes
    """

    _validation = {
        'algorithm': {'required': True},
        'digest': {'required': True},
        'signature': {'required': True},
    }

    _attribute_map = {
        'algorithm': {'key': 'alg', 'type': 'str'},
        'digest': {'key': 'digest', 'type': 'base64'},
        'signature': {'key': 'value', 'type': 'base64'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyVerifyParameters, self).__init__(**kwargs)
        self.algorithm = kwargs['algorithm']
        self.digest = kwargs['digest']
        self.signature = kwargs['signature']


class KeyVerifyResult(msrest.serialization.Model):
    """The key verify result.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar value: True if the signature is verified, otherwise false.
    :vartype value: bool
    """

    _validation = {
        'value': {'readonly': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': 'bool'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyVerifyResult, self).__init__(**kwargs)
        self.value = None


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


class DeletionRecoveryLevel(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """Reflects the deletion recovery level currently in effect for keys in the current vault. If it
    contains 'Purgeable' the key can be permanently deleted by a privileged user; otherwise, only
    the system can purge the key, at the end of the retention interval.
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

    #: The NIST P-256 elliptic curve, AKA SECG curve SECP256R1.
    P256 = "P-256"
    #: The NIST P-384 elliptic curve, AKA SECG curve SECP384R1.
    P384 = "P-384"
    #: The NIST P-521 elliptic curve, AKA SECG curve SECP521R1.
    P521 = "P-521"
    #: The SECG SECP256K1 elliptic curve.
    P256_K = "P-256K"

class JsonWebKeyEncryptionAlgorithm(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """algorithm identifier
    """

    RSA_OAEP = "RSA-OAEP"
    RSA_OAEP256 = "RSA-OAEP-256"
    RSA1_5 = "RSA1_5"

class JsonWebKeyOperation(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """JSON web key operations. For more information, see JsonWebKeyOperation.
    """

    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SIGN = "sign"
    VERIFY = "verify"
    WRAP_KEY = "wrapKey"
    UNWRAP_KEY = "unwrapKey"
    IMPORT_ENUM = "import"

class JsonWebKeySignatureAlgorithm(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The signing/verification algorithm identifier. For more information on possible algorithm
    types, see JsonWebKeySignatureAlgorithm.
    """

    #: RSASSA-PSS using SHA-256 and MGF1 with SHA-256, as described in
    #: https://tools.ietf.org/html/rfc7518.
    PS256 = "PS256"
    #: RSASSA-PSS using SHA-384 and MGF1 with SHA-384, as described in
    #: https://tools.ietf.org/html/rfc7518.
    PS384 = "PS384"
    #: RSASSA-PSS using SHA-512 and MGF1 with SHA-512, as described in
    #: https://tools.ietf.org/html/rfc7518.
    PS512 = "PS512"
    #: RSASSA-PKCS1-v1_5 using SHA-256, as described in https://tools.ietf.org/html/rfc7518.
    RS256 = "RS256"
    #: RSASSA-PKCS1-v1_5 using SHA-384, as described in https://tools.ietf.org/html/rfc7518.
    RS384 = "RS384"
    #: RSASSA-PKCS1-v1_5 using SHA-512, as described in https://tools.ietf.org/html/rfc7518.
    RS512 = "RS512"
    #: Reserved.
    RSNULL = "RSNULL"
    #: ECDSA using P-256 and SHA-256, as described in https://tools.ietf.org/html/rfc7518.
    ES256 = "ES256"
    #: ECDSA using P-384 and SHA-384, as described in https://tools.ietf.org/html/rfc7518.
    ES384 = "ES384"
    #: ECDSA using P-521 and SHA-512, as described in https://tools.ietf.org/html/rfc7518.
    ES512 = "ES512"
    #: ECDSA using P-256K and SHA-256, as described in https://tools.ietf.org/html/rfc7518.
    ES256_K = "ES256K"

class JsonWebKeyType(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """JsonWebKey Key Type (kty), as defined in
    https://tools.ietf.org/html/draft-ietf-jose-json-web-algorithms-40.
    """

    #: Elliptic Curve.
    EC = "EC"
    #: Elliptic Curve with a private key which is not exportable from the HSM.
    EC_HSM = "EC-HSM"
    #: RSA (https://tools.ietf.org/html/rfc3447).
    RSA = "RSA"
    #: RSA with a private key which is not exportable from the HSM.
    RSA_HSM = "RSA-HSM"
    #: Not supported in this version. Octet sequence (used to represent symmetric keys).
    OCT = "oct"
