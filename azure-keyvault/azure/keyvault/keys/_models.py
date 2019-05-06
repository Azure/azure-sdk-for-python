# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime
from typing import Any, Dict, Mapping, Optional
from .._generated.v7_0 import models
from .._internal import _parse_vault_id


class KeyAttributes(object):
    """A key's id and attributes."""

    def __init__(self, attributes, vault_id, **kwargs):
        # type: (models.KeyAttributes, str, Mapping[str, Any]) -> None
        self._attributes = attributes
        self._id = vault_id     # we don't want to call this kid, right?
        self._vault_id = _parse_vault_id(vault_id)
        self._managed = kwargs.get("managed", None)
        self._tags = kwargs.get("tags", None)

    @classmethod
    def _from_key_bundle(cls, key_bundle):
        # type: (models.KeyBundle) -> KeyAttributes
        """Construct a key from an autorest-generated KeyBundle"""
        return cls(
            key_bundle.attributes,
            key_bundle.key.kid,
            managed=None,
            tags=key_bundle.tags,
        )

    @classmethod
    def _from_key_item(cls, key_item):
        # type: (models.KeyItem) -> KeyAttributes
        """Construct a Key from an autorest-generated KeyItem"""
        return cls(
            key_item.attributes,
            key_item.kid,
            managed=key_item.managed,
            tags=key_item.tags,
        )

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
        """Reflects the deletion recovery level currently in effect for keys in the current vault
        :rtype: str"""
        return self._attributes.recovery_level

    @property
    def tags(self):
        # type: () -> Dict[str, str]
        """Application specific metadata in the form of key-value pairs.
        :rtype: dict"""
        return self._tags


class Key(KeyAttributes):
    """A key consisting of all KeyAttributes and key_material information.
    """

    def __init__(self, attributes, key, **kwargs):
        super(Key, self).__init__(attributes, key.kid, **kwargs)
        self._key_material = key

    @classmethod
    def _from_key_bundle(cls, key_bundle):
        # type: (models.KeyBundle) -> key
        """Construct a key from an autorest-generated KeyBundle"""
        return cls(
            key_bundle.attributes,
            key_bundle.key,
            managed=key_bundle.managed,
            tags=key_bundle.tags,
        )

    @property
    def key_material(self):
        # type: () -> Dict[str, str]
        return self._key_material


class DeletedKey(KeyAttributes):
    """A Deleted key consisting of its id, attributes, and tags, as
    well as when it will be purged, if soft-delete is enabled for the vault.
    """

    def __init__(self, attributes, vault_id, deleted_date=None, recovery_id=None, scheduled_purge_date=None, **kwargs):
        # type: (models.KeyAttributes, str, Optional[datetime], Optional[str], Optional[datetime], Mapping[str, Any]) -> None
        super(DeletedKey, self).__init__(attributes, vault_id, **kwargs)
        self._deleted_date = deleted_date
        self._recovery_id = recovery_id
        self._scheduled_purge_date = scheduled_purge_date
        # self._key_material = key # we don't expose the key i.e jsonWebKey just like we don't expose the value on deleted secret? why?

    @classmethod
    def _from_deleted_key_bundle(cls, deleted_key_bundle):
        # type: (models.DeletedKeyBundle) -> DeletedKey
        """Construct a DeletedKey from an autorest-generated DeletedKeyBundle"""
        return cls(
            deleted_key_bundle.attributes,
            deleted_key_bundle.key.kid,
            deleted_key_bundle.deleted_date,
            deleted_key_bundle.recovery_id,
            deleted_key_bundle.scheduled_purge_date,
            managed=deleted_key_bundle.managed,
            tags=deleted_key_bundle.tags,
            # deleted_key_bundle.key, 
            # TODO: deleted key item doesn't have the jsonWebKey.
            # Option 1 - Is it fine if DeletedKey does not have the jsonWebKey property OR
            # Option 2- Should we just have the other deletedKey properties such as deleted_date, recovery_id, scheduled_purge_date as None initialy on KeyATtributes class and
            # have the "new" DeletedKey class to have the jsonWebKey + KeyAttributes properties
        )

    @classmethod
    def _from_deleted_key_item(cls, deleted_key_item):
        # type: (models.DeletedKeyItem) -> DeletedKey
        """Construct a DeletedKey from an autorest-generated DeletedKeyItem"""
        return cls(
            deleted_key_item.attributes,
            deleted_key_item.kid,
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

    # @property
    # def key_material(self):
    #     return self._key_material
