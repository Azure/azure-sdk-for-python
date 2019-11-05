# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
from collections import namedtuple
from ._shared import parse_vault_id
from ._shared._generated.v7_0.models import JsonWebKey as _JsonWebKey

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Optional
    from datetime import datetime
    from ._shared._generated.v7_0 import models as _models

KeyOperationResult = namedtuple("KeyOperationResult", ["id", "value"])


class JsonWebKey(object):
    # pylint:disable=too-many-instance-attributes
    """As of http://tools.ietf.org/html/draft-ietf-jose-json-web-key-18. All parameters are optional.

    :param str kid: Key identifier.
    :param kty: Key Type (kty), as defined in https://tools.ietf.org/html/draft-ietf-jose-json-web-algorithms-40
    :type kty: str or ~azure.keyvault.keys.enums.KeyType
    :param key_ops: Allowed operations for the key
    :type key_ops: list(~azure.keyvault.keys.enums.KeyOperation)
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
    :type crv: str or ~azure.keyvault.keys.enums.KeyCurveName
    :param bytes x: X component of an EC public key.
    :param bytes y: Y component of an EC public key.
    """

    FIELDS = ("kid", "kty", "key_ops", "n", "e", "d", "dp", "dq", "qi", "p", "q", "k", "t", "crv", "x", "y")

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        for field in self.FIELDS:
            setattr(self, field, kwargs.get(field))

    def _to_generated_model(self):
        # type: () -> _JsonWebKey
        jwk = _JsonWebKey()
        for field in self.FIELDS:
            setattr(jwk, field, getattr(self, field))
        return jwk


class KeyProperties(object):
    """A key's id and attributes."""

    def __init__(self, attributes, vault_id, **kwargs):
        # type: (_models.KeyAttributes, str, **Any) -> None
        self._attributes = attributes
        self._id = vault_id
        self._vault_id = parse_vault_id(vault_id)
        self._managed = kwargs.get("managed", None)
        self._tags = kwargs.get("tags", None)

    def __repr__(self):
        # type () -> str
        return "<KeyProperties [{}]>".format(self.id)[:1024]

    @classmethod
    def _from_key_bundle(cls, key_bundle):
        # type: (_models.KeyBundle) -> KeyProperties
        """Construct a KeyProperties from an autorest-generated KeyBundle"""
        return cls(key_bundle.attributes, key_bundle.key.kid, managed=key_bundle.managed, tags=key_bundle.tags)

    @classmethod
    def _from_key_item(cls, key_item):
        # type: (_models.KeyItem) -> KeyProperties
        """Construct a KeyProperties from an autorest-generated KeyItem"""
        return cls(key_item.attributes, key_item.kid, managed=key_item.managed, tags=key_item.tags)

    @property
    def id(self):
        # type: () -> str
        """:rtype: str"""
        return self._id

    @property
    def name(self):
        # type: () -> str
        """:rtype: str"""
        return self._vault_id.name

    @property
    def version(self):
        # type: () -> str
        """:rtype: str"""
        return self._vault_id.version

    @property
    def enabled(self):
        # type: () -> bool
        """:rtype: bool"""
        return self._attributes.enabled

    @property
    def not_before(self):
        # type: () -> datetime
        """
        The key's not-before time, in UTC

        :rtype: datetime.datetime
        """
        return self._attributes.not_before

    @property
    def expires(self):
        # type: () -> datetime
        """
        When the key will expire, in UTC

        :rtype: datetime.datetime
        """
        return self._attributes.expires

    @property
    def created(self):
        # type: () -> datetime
        """
        When the key was created, in UTC

        :rtype: datetime.datetime
        """
        return self._attributes.created

    @property
    def updated(self):
        # type: () -> datetime
        """
        When the key was last updated, in UTC

        :rtype: datetime.datetime
        """
        return self._attributes.updated

    @property
    def vault_endpoint(self):
        # type: () -> str
        """
        URL of the vault containing the key

        :rtype: str
        """
        return self._vault_id.vault_endpoint

    @property
    def recovery_level(self):
        # type: () -> str
        """
        The vault's deletion recovery level for keys

        :rtype: str
        """
        return self._attributes.recovery_level

    @property
    def tags(self):
        # type: () -> Dict[str, str]
        """
        Application specific metadata in the form of key-value pairs

        :rtype: dict
        """
        return self._tags

    @property
    def managed(self):
        # type: () -> bool
        """
        Returns if the key's lifetime is managed by key vault

        :rtype: bool
        """
        return self._managed


class Key(object):
    """A key's attributes and cryptographic material"""

    def __init__(self, properties, key_material):
        # type: (KeyProperties, _models.JsonWebKey, **Any) -> None
        self._properties = properties
        self._key_material = key_material

    def __repr__(self):
        # type () -> str
        return "<Key [{}]>".format(self.id)[:1024]

    @classmethod
    def _from_key_bundle(cls, key_bundle):
        # type: (_models.KeyBundle) -> Key
        """Construct a Key from an autorest-generated KeyBundle"""
        return cls(
            properties=KeyProperties._from_key_bundle(key_bundle),  # pylint: disable=protected-access
            key_material=key_bundle.key,
        )

    @property
    def id(self):
        # type: () -> str
        """:rtype: str"""
        return self._properties.id

    @property
    def name(self):
        # type: () -> str
        """:rtype: str"""
        return self._properties.name

    @property
    def properties(self):
        # type: () -> KeyProperties
        """The key's properties"""
        return self._properties

    @property
    def key_material(self):
        # type: () -> _models.JsonWebKey
        """The JSON web key"""
        return self._key_material


class DeletedKey(Key):
    """A deleted key's id, attributes, and cryptographic material, as well as when it will be purged"""

    def __init__(
        self,
        properties,  # type: KeyProperties
        key_material=None,  # type: _models.JsonWebKey
        deleted_date=None,  # type: Optional[datetime]
        recovery_id=None,  # type: Optional[str]
        scheduled_purge_date=None,  # type: Optional[datetime]
    ):
        # type: (...) -> None
        super(DeletedKey, self).__init__(properties, key_material)
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
        return cls(
            properties=KeyProperties._from_key_bundle(deleted_key_bundle),  # pylint: disable=protected-access
            key_material=deleted_key_bundle.key,
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
            deleted_date=deleted_key_item.deleted_date,
            recovery_id=deleted_key_item.recovery_id,
            scheduled_purge_date=deleted_key_item.scheduled_purge_date,
        )

    @property
    def deleted_date(self):
        # type: () -> datetime
        """
        When the key was deleted, in UTC

        :rtype: datetime.datetime
        """
        return self._deleted_date

    @property
    def recovery_id(self):
        # type: () -> str
        """
        An identifier used to recover the deleted key

        :rtype: str
        """
        return self._recovery_id

    @property
    def scheduled_purge_date(self):
        # type: () -> datetime
        """
        When the key is scheduled to be purged, in UTC

        :rtype: datetime.datetime
        """
        return self._scheduled_purge_date
