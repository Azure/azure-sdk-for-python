# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime
from typing import Any, Dict, Mapping, Optional
from collections import namedtuple
from .._internal import _parse_vault_id
from .._generated.v7_0 import models

KeyOperationResult = namedtuple("KeyOperationResult", ["id", "value"])


class KeyBase(object):
    """A key's id and attributes."""

    def __init__(self, attributes, vault_id, **kwargs):
        # type: (models.KeyAttributes, str, Mapping[str, Any]) -> None
        self._attributes = attributes
        self._id = vault_id
        self._vault_id = _parse_vault_id(vault_id)
        self._managed = kwargs.get("managed", None)
        self._tags = kwargs.get("tags", None)

    @classmethod
    def _from_key_bundle(cls, key_bundle):
        # type: (models.KeyBundle) -> KeyBase
        """Construct a key from an autorest-generated KeyBundle"""
        return cls(key_bundle.attributes, key_bundle.key.kid, managed=key_bundle.managed, tags=key_bundle.tags)

    @classmethod
    def _from_key_item(cls, key_item):
        # type: (models.KeyItem) -> KeyBase
        """Construct a Key from an autorest-generated KeyItem"""
        return cls(key_item.attributes, key_item.kid, managed=key_item.managed, tags=key_item.tags)

    @property
    def id(self):
        # type: () -> str
        """The key id
        :rtype: str"""
        return self._id

    @property
    def name(self):
        # type: () -> str
        """The name of the key
        :rtype: str"""
        return self._vault_id.name

    @property
    def version(self):
        # type: () -> str
        """The version of the key
        :rtype: str"""
        return self._vault_id.version

    @property
    def enabled(self):
        # type: () -> bool
        """The Key's 'enabled' attribute
        :rtype: bool"""
        return self._attributes.enabled

    @property
    def not_before(self):
        # type: () -> datetime
        """The Key's not_before date in UTC
        :rtype: datetime"""
        return self._attributes.not_before

    @property
    def expires(self):
        # type: () -> datetime
        """The Key's expiry date in UTC
        :rtype: datetime"""
        return self._attributes.expires

    @property
    def created(self):
        # type: () -> datetime
        """The Key's creation time in UTC
        :rtype: datetime"""
        return self._attributes.created

    @property
    def updated(self):
        # type: () -> datetime
        """The Key's last updated time in UTC
        :rtype: datetime"""
        return self._attributes.updated

    @property
    def vault_url(self):
        # type: () -> str
        """The url of the vault containing the key
        :rtype: str"""
        return self._vault_id.vault_url

    @property
    def recovery_level(self):
        # type: () -> str
        """The vault's deletion recovery level for keys
        :rtype: str"""
        return self._attributes.recovery_level

    @property
    def tags(self):
        # type: () -> Dict[str, str]
        """Application specific metadata in the form of key-value pairs.
        :rtype: dict"""
        return self._tags


class Key(KeyBase):
    """A key consisting of all KeyBase and key_material information.
    """

    def __init__(self, attributes, vault_id, key_material, **kwargs):
        # type: (models.KeyAttributes, str, models.JsonWebKey, Mapping[str, Any]) -> None
        super(Key, self).__init__(attributes, vault_id, **kwargs)
        self._key_material = key_material

    @classmethod
    def _from_key_bundle(cls, key_bundle):
        # type: (models.KeyBundle) -> Key
        """Construct a key from an autorest-generated KeyBundle"""
        return cls(
            attributes=key_bundle.attributes, vault_id=key_bundle.key.kid, key_material=key_bundle.key, managed=key_bundle.managed, tags=key_bundle.tags
        )

    @property
    def key_material(self):
        # type: () -> models.JsonWebKey
        return self._key_material


class DeletedKey(Key):
    """A Deleted key consisting of its id, attributes, and tags, as
    well as when it will be purged, if soft-delete is enabled for the vault.
    """

    def __init__(
        self,
        attributes,
        vault_id,
        key_material=None,
        deleted_date=None,
        recovery_id=None,
        scheduled_purge_date=None,
        **kwargs
    ):
        # type: (models.KeyAttributes, str, models.JsonWebKey, Optional[datetime], Optional[str], Optional[datetime], Mapping[str, Any]) -> None
        super(DeletedKey, self).__init__(attributes, vault_id, key_material, **kwargs)
        self._deleted_date = deleted_date
        self._recovery_id = recovery_id
        self._scheduled_purge_date = scheduled_purge_date

    @classmethod
    def _from_deleted_key_bundle(cls, deleted_key_bundle):
        # type: (models.DeletedKeyBundle) -> DeletedKey
        """Construct a DeletedKey from an autorest-generated DeletedKeyBundle"""
        return cls(
            attributes=deleted_key_bundle.attributes,
            vault_id=deleted_key_bundle.key.kid,
            key_material=deleted_key_bundle.key,
            deleted_date=deleted_key_bundle.deleted_date,
            recovery_id=deleted_key_bundle.recovery_id,
            scheduled_purge_date=deleted_key_bundle.scheduled_purge_date,
            managed=deleted_key_bundle.managed,
            tags=deleted_key_bundle.tags,
        )

    @classmethod
    def _from_deleted_key_item(cls, deleted_key_item):
        # type: (models.DeletedKeyItem) -> DeletedKey
        """Construct a DeletedKey from an autorest-generated DeletedKeyItem"""
        return cls(
            attributes=deleted_key_item.attributes,
            vault_id=deleted_key_item.kid,
            deleted_date=deleted_key_item.deleted_date,
            recovery_id=deleted_key_item.recovery_id,
            scheduled_purge_date=deleted_key_item.scheduled_purge_date,
            managed=deleted_key_item.managed,
            tags=deleted_key_item.tags,
        )

    @property
    def deleted_date(self):
        # type: () -> datetime
        """The time when the key was deleted, in UTC
        :rtype: datetime"""
        return self._deleted_date

    @property
    def recovery_id(self):
        # type: () -> str
        """The url of the recovery object, used to identify and recover the deleted key
        :rtype: str"""
        return self._recovery_id

    @property
    def scheduled_purge_date(self):
        # type: () -> datetime
        """The time when the key is scheduled to be purged, in UTC
        :rtype: datetime"""
        return self._scheduled_purge_date
