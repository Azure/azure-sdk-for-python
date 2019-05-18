# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime
from typing import Any, Dict, Mapping, Optional
from .._generated.v7_0 import models
from .._internal import _parse_vault_id


class SecretAttributes(object):
    """A secret's id and attributes."""

    def __init__(self, attributes, vault_id, **kwargs):
        # type: (models.SecretAttributes, str, Mapping[str, Any]) -> None
        self._attributes = attributes
        self._id = vault_id
        self._vault_id = _parse_vault_id(vault_id)
        self._content_type = kwargs.get("content_type", None)
        self._key_id = kwargs.get("key_id", None)
        self._managed = kwargs.get("managed", None)
        self._tags = kwargs.get("tags", None)

    @classmethod
    def _from_secret_bundle(cls, secret_bundle):
        # type: (models.SecretBundle) -> SecretAttributes
        """Construct a Secret from an autorest-generated SecretBundle"""
        return cls(
            secret_bundle.attributes,
            secret_bundle.id,
            content_type=secret_bundle.content_type,
            key_id=secret_bundle.kid,
            managed=secret_bundle.managed,
            tags=secret_bundle.tags,
        )

    @classmethod
    def _from_secret_item(cls, secret_item):
        # type: (models.SecretItem) -> SecretAttributes
        """Construct a Secret from an autorest-generated SecretItem"""
        return cls(
            secret_item.attributes,
            secret_item.id,
            content_type=secret_item.content_type,
            managed=secret_item.managed,
            tags=secret_item.tags,
        )

    @property
    def content_type(self):
        # type: () -> str
        """Type of the secret value such as a password
        :rtype: str"""
        return self._content_type

    @property
    def id(self):
        # type: () -> str
        """The secret id
        :rtype: str"""
        return self._id

    @property
    def key_id(self):
        # type: () -> str
        """Specifies the corresponding key id backing the KV certificate
        :rtype: str"""
        return self._key_id

    @property
    def enabled(self):
        # type: () -> bool
        """The Secret's 'enabled' attribute
        :rtype: bool"""
        return self._attributes.enabled

    @property
    def not_before(self):
        # type: () -> datetime
        """The Secret's not_before date in UTC
        :rtype: datetime"""
        return self._attributes.not_before

    @property
    def expires(self):
        # type: () -> datetime
        """The Secret's expiry date in UTC
        :rtype: datetime"""
        return self._attributes.expires

    @property
    def created(self):
        # type: () -> datetime
        """The Secret's creation time in UTC
        :rtype: datetime"""
        return self._attributes.created

    @property
    def updated(self):
        # type: () -> datetime
        """The Secret's last updated time in UTC
        :rtype: datetime"""
        return self._attributes.updated

    @property
    def recovery_level(self):
        # type: () -> str
        """Reflects the deletion recovery level currently in effect for secrets in the current vault
        :rtype: str"""
        return self._attributes.recovery_level

    @property
    def vault_url(self):
        # type: () -> str
        """The url of the vault containing the secret
        :rtype: str"""
        return self._vault_id.vault_url

    @property
    def name(self):
        # type: () -> str
        """The name of the secret
        :rtype: str"""
        return self._vault_id.name

    @property
    def version(self):
        # type: () -> str
        """The version of the secret
        :rtype: str"""
        return self._vault_id.version

    @property
    def tags(self):
        # type: () -> Dict[str, str]
        """Application specific metadata in the form of key-value pairs.
        :rtype: dict"""
        return self._tags


class Secret(SecretAttributes):
    """A secret consisting of all SecretAttributes and value information.
    """

    def __init__(self, attributes, vault_id, value, **kwargs):
        super(Secret, self).__init__(attributes, vault_id, **kwargs)
        self._value = value

    @classmethod
    def _from_secret_bundle(cls, secret_bundle):
        # type: (models.SecretBundle) -> Secret
        """Construct a Secret from an autorest-generated SecretBundle"""
        return cls(
            secret_bundle.attributes,
            secret_bundle.id,
            secret_bundle.value,
            content_type=secret_bundle.content_type,
            key_id=secret_bundle.kid,
            managed=secret_bundle.managed,
            tags=secret_bundle.tags,
        )

    @property
    def value(self):
        # type: () -> str
        """The secret's value.
        :rtype: str"""
        return self._value


class DeletedSecret(SecretAttributes):
    """A Deleted Secret consisting of its id, attributes, and tags, as
    well as when it will be purged, if soft-delete is enabled for the vault.
    """

    def __init__(self, attributes, vault_id, deleted_date=None, recovery_id=None, scheduled_purge_date=None, **kwargs):
        # type: (models.SecretAttributes, str, Optional[datetime], Optional[str], Optional[datetime], Mapping[str, Any]) -> None
        super(DeletedSecret, self).__init__(attributes, vault_id, **kwargs)
        self._deleted_date = deleted_date
        self._recovery_id = recovery_id
        self._scheduled_purge_date = scheduled_purge_date

    @classmethod
    def _from_deleted_secret_bundle(cls, deleted_secret_bundle):
        # type: (models.DeletedSecretBundle) -> DeletedSecret
        """Construct a DeletedSecret from an autorest-generated DeletedSecretBundle"""
        return cls(
            deleted_secret_bundle.attributes,
            deleted_secret_bundle.id,
            content_type=deleted_secret_bundle.content_type,
            key_id=deleted_secret_bundle.kid,
            managed=deleted_secret_bundle.managed,
            tags=deleted_secret_bundle.tags,
        )

    @classmethod
    def _from_deleted_secret_item(cls, deleted_secret_item):
        # type: (models.DeletedSecretItem) -> DeletedSecret
        """Construct a DeletedSecret from an autorest-generated DeletedSecretItem"""
        return cls(
            deleted_secret_item.attributes,
            deleted_secret_item.id,
            deleted_date=deleted_secret_item.deleted_date,
            recovery_id=deleted_secret_item.recovery_id,
            scheduled_purge_date=deleted_secret_item.scheduled_purge_date,
            content_type=deleted_secret_item.content_type,
            managed=deleted_secret_item.managed,
            tags=deleted_secret_item.tags,
        )

    @property
    def deleted_date(self):
        # type: () -> datetime
        """The time when the secret was deleted, in UTC
        :rtype: datetime"""
        return self._deleted_date

    @property
    def recovery_id(self):
        # type: () -> str
        """The url of the recovery object, used to identify and recover the deleted secret
        :rtype: str"""
        return self._recovery_id

    @property
    def scheduled_purge_date(self):
        # type: () -> datetime
        """The time when the secret is scheduled to be purged, in UTC
        :rtype: datetime"""
        return self._scheduled_purge_date
