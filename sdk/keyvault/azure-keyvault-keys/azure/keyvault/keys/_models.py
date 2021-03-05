# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
from collections import namedtuple
from ._shared import parse_key_vault_id
from ._generated.v7_1.models import JsonWebKey as _JsonWebKey

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Optional
    from datetime import datetime
    from ._generated.v7_0 import models as _models
    from ._enums import KeyOperation

KeyOperationResult = namedtuple("KeyOperationResult", ["id", "value"])


class JsonWebKey(object):
    # pylint:disable=too-many-instance-attributes
    """As defined in http://tools.ietf.org/html/draft-ietf-jose-json-web-key-18. All parameters are optional.

    :param str kid: Key identifier.
    :param kty: Key Type (kty), as defined in https://tools.ietf.org/html/draft-ietf-jose-json-web-algorithms-40
    :type kty: ~azure.keyvault.keys.KeyType or str
    :param key_ops: Allowed operations for the key
    :type key_ops: list[str or ~azure.keyvault.keys.KeyOperation]
    :param bytes n: RSA modulus.
    :param bytes e: RSA public exponent.
    :param bytes d: RSA private exponent, or the D component of an EC private key.
    :param bytes dp: RSA private key parameter.
    :param bytes dq: RSA private key parameter.
    :param bytes qi: RSA private key parameter.
    :param bytes p: RSA secret prime.
    :param bytes q: RSA secret prime, with p < q.
    :param bytes k: Symmetric key.
    :param bytes t: HSM Token, used with 'Bring Your Own Key'.
    :param crv: Elliptic curve name.
    :type crv: ~azure.keyvault.keys.KeyCurveName or str
    :param bytes x: X component of an EC public key.
    :param bytes y: Y component of an EC public key.
    """

    _FIELDS = ("kid", "kty", "key_ops", "n", "e", "d", "dp", "dq", "qi", "p", "q", "k", "t", "crv", "x", "y")

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        for field in self._FIELDS:
            setattr(self, field, kwargs.get(field))

    def _to_generated_model(self):
        # type: () -> _JsonWebKey
        jwk = _JsonWebKey()
        for field in self._FIELDS:
            setattr(jwk, field, getattr(self, field))
        return jwk


class KeyProperties(object):
    """A key's id and attributes."""

    def __init__(self, key_id, attributes=None, **kwargs):
        # type: (str, Optional[_models.KeyAttributes], **Any) -> None
        self._attributes = attributes
        self._id = key_id
        self._vault_id = parse_key_vault_id(key_id)
        self._managed = kwargs.get("managed", None)
        self._tags = kwargs.get("tags", None)

    def __repr__(self):
        # type () -> str
        return "<KeyProperties [{}]>".format(self.id)[:1024]

    @classmethod
    def _from_key_bundle(cls, key_bundle):
        # type: (_models.KeyBundle) -> KeyProperties
        """Construct a KeyProperties from an autorest-generated KeyBundle"""
        return cls(
            key_bundle.key.kid, attributes=key_bundle.attributes, managed=key_bundle.managed, tags=key_bundle.tags
        )

    @classmethod
    def _from_key_item(cls, key_item):
        # type: (_models.KeyItem) -> KeyProperties
        """Construct a KeyProperties from an autorest-generated KeyItem"""
        return cls(key_id=key_item.kid, attributes=key_item.attributes, managed=key_item.managed, tags=key_item.tags)

    @property
    def id(self):
        # type: () -> str
        """The key's id

        :rtype: str
        """
        return self._id

    @property
    def name(self):
        # type: () -> str
        """The key's name

        :rtype: str
        """
        return self._vault_id.name

    @property
    def version(self):
        # type: () -> str
        """The key's version

        :rtype: str
        """
        return self._vault_id.version

    @property
    def enabled(self):
        # type: () -> bool
        """Whether the key is enabled for use

        :rtype: bool
        """
        return self._attributes.enabled

    @property
    def not_before(self):
        # type: () -> datetime
        """The time before which the key can not be used, in UTC

        :rtype: ~datetime.datetime
        """
        return self._attributes.not_before

    @property
    def expires_on(self):
        # type: () -> datetime
        """When the key will expire, in UTC

        :rtype: ~datetime.datetime
        """
        return self._attributes.expires

    @property
    def created_on(self):
        # type: () -> datetime
        """When the key was created, in UTC

        :rtype: ~datetime.datetime
        """
        return self._attributes.created

    @property
    def updated_on(self):
        # type: () -> datetime
        """When the key was last updated, in UTC

        :rtype: ~datetime.datetime
        """
        return self._attributes.updated

    @property
    def vault_url(self):
        # type: () -> str
        """URL of the vault containing the key

        :rtype: str
        """
        return self._vault_id.vault_url

    @property
    def recoverable_days(self):
        # type: () -> Optional[int]
        """The number of days the key is retained before being deleted from a soft-delete enabled Key Vault.

        :rtype: int
        """
        # recoverable_days was added in 7.1-preview
        if self._attributes and hasattr(self._attributes, "recoverable_days"):
            return self._attributes.recoverable_days
        return None

    @property
    def recovery_level(self):
        # type: () -> str
        """The vault's deletion recovery level for keys

        :rtype: str
        """
        return self._attributes.recovery_level

    @property
    def tags(self):
        # type: () -> Dict[str, str]
        """Application specific metadata in the form of key-value pairs

        :rtype: dict[str, str]
        """
        return self._tags

    @property
    def managed(self):
        # type: () -> bool
        """Returns whether the key's lifetime is managed by key vault

        :rtype: bool
        """
        return self._managed


class KeyVaultKey(object):
    """A key's attributes and cryptographic material.

    :param str key_id:
        Key Vault's identifier for the key. Typically a URI, e.g. https://myvault.vault.azure.net/keys/my-key/version
    :param jwk:
        The key's cryptographic material as a JSON Web Key (https://tools.ietf.org/html/rfc7517). This may be provided
        as a dictionary or keyword arguments. See :class:`~azure.keyvault.keys.models.JsonWebKey` for field names.

    Providing cryptographic material as keyword arguments:

    .. code-block:: python

        from azure.keyvault.keys.models import KeyVaultKey

        key_id = 'https://myvault.vault.azure.net/keys/my-key/my-key-version'
        key_bytes = os.urandom(32)
        key = KeyVaultKey(key_id, k=key_bytes, kty='oct', key_ops=['unwrapKey', 'wrapKey'])

    Providing cryptographic material as a dictionary:

    .. code-block:: python

        from azure.keyvault.keys.models import KeyVaultKey

        key_id = 'https://myvault.vault.azure.net/keys/my-key/my-key-version'
        key_bytes = os.urandom(32)
        jwk = {'k': key_bytes, 'kty': 'oct', 'key_ops': ['unwrapKey', 'wrapKey']}
        key = KeyVaultKey(key_id, jwk=jwk)

    """

    def __init__(self, key_id, jwk=None, **kwargs):
        # type: (str, Optional[dict], **Any) -> None
        self._properties = kwargs.pop("properties", None) or KeyProperties(key_id, **kwargs)
        if isinstance(jwk, dict):
            if any(field in kwargs for field in JsonWebKey._FIELDS):  # pylint:disable=protected-access
                raise ValueError(
                    "Individual keyword arguments for key material and the 'jwk' argument are mutually exclusive."
                )
            self._key_material = JsonWebKey(**jwk)
        else:
            self._key_material = JsonWebKey(**kwargs)

    def __repr__(self):
        # type () -> str
        return "<KeyVaultKey [{}]>".format(self.id)[:1024]

    @classmethod
    def _from_key_bundle(cls, key_bundle):
        # type: (_models.KeyBundle) -> KeyVaultKey
        """Construct a KeyVaultKey from an autorest-generated KeyBundle"""
        # pylint:disable=protected-access
        return cls(
            key_id=key_bundle.key.kid,
            jwk={field: getattr(key_bundle.key, field, None) for field in JsonWebKey._FIELDS},
            properties=KeyProperties._from_key_bundle(key_bundle),
        )

    @property
    def id(self):
        # type: () -> str
        """The key's id

        :rtype: str
        """
        return self._properties.id

    @property
    def name(self):
        # type: () -> str
        """The key's name

        :rtype: str
        """
        return self._properties.name

    @property
    def properties(self):
        # type: () -> KeyProperties
        """The key's properties

        :rtype: ~azure.keyvault.keys.KeyProperties
        """
        return self._properties

    @property
    def key(self):
        # type: () -> JsonWebKey
        """The JSON web key

        :rtype: ~azure.keyvault.keys.JsonWebKey
        """
        return self._key_material

    @property
    def key_type(self):
        # type: () -> str
        """The key's type. See :class:`~azure.keyvault.keys.KeyType` for possible values.

        :rtype: ~azure.keyvault.keys.KeyType or str
        """
        return self._key_material.kty  # pylint:disable=no-member

    @property
    def key_operations(self):
        # type: () -> list[KeyOperation]
        """Permitted operations. See :class:`~azure.keyvault.keys.KeyOperation` for possible values.

        :rtype: list[~azure.keyvault.keys.KeyOperation or str]
        """
        return self._key_material.key_ops  # pylint:disable=no-member


class DeletedKey(KeyVaultKey):
    """A deleted key's properties, cryptographic material and its deletion information. If soft-delete
    is enabled, returns information about its recovery as well."""

    def __init__(
        self,
        properties,  # type: KeyProperties
        deleted_date=None,  # type: Optional[datetime]
        recovery_id=None,  # type: Optional[str]
        scheduled_purge_date=None,  # type: Optional[datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        super(DeletedKey, self).__init__(properties=properties, **kwargs)
        self._deleted_date = deleted_date
        self._recovery_id = recovery_id
        self._scheduled_purge_date = scheduled_purge_date

    def __repr__(self):
        # type () -> str
        return "<DeletedKey [{}]>".format(self.id)[:1024]

    @classmethod
    def _from_deleted_key_bundle(cls, deleted_key_bundle):
        # type: (_models.DeletedKeyBundle) -> DeletedKey
        """Construct a DeletedKey from an autorest-generated DeletedKeyBundle"""
        # pylint:disable=protected-access
        return cls(
            properties=KeyProperties._from_key_bundle(deleted_key_bundle),
            key_id=deleted_key_bundle.key.kid,
            jwk={field: getattr(deleted_key_bundle.key, field, None) for field in JsonWebKey._FIELDS},
            deleted_date=deleted_key_bundle.deleted_date,
            recovery_id=deleted_key_bundle.recovery_id,
            scheduled_purge_date=deleted_key_bundle.scheduled_purge_date,
        )

    @classmethod
    def _from_deleted_key_item(cls, deleted_key_item):
        # type: (_models.DeletedKeyItem) -> DeletedKey
        """Construct a DeletedKey from an autorest-generated DeletedKeyItem"""
        return cls(
            properties=KeyProperties._from_key_item(deleted_key_item),  # pylint: disable=protected-access
            key_id=deleted_key_item.kid,
            deleted_date=deleted_key_item.deleted_date,
            recovery_id=deleted_key_item.recovery_id,
            scheduled_purge_date=deleted_key_item.scheduled_purge_date,
        )

    @property
    def deleted_date(self):
        # type: () -> datetime
        """When the key was deleted, in UTC

        :rtype: ~datetime.datetime
        """
        return self._deleted_date

    @property
    def recovery_id(self):
        # type: () -> str
        """An identifier used to recover the deleted key. Returns ``None`` if soft-delete is disabled.

        :rtype: str
        """
        return self._recovery_id

    @property
    def scheduled_purge_date(self):
        # type: () -> datetime
        """When the key is scheduled to be purged, in UTC. Returns ``None`` if soft-delete is disabled.

        :rtype: ~datetime.datetime
        """
        return self._scheduled_purge_date
