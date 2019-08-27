# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from ._shared import parse_vault_id
try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Optional
    from datetime import datetime
    from ._shared._generated.v7_0 import models as _models


class SecretAttributes(object):
    """A secret's id and attributes."""

    def __init__(self, attributes, vault_id, **kwargs):
        # type: (_models.SecretAttributes, str, **Any) -> None
        self._attributes = attributes
        self._id = vault_id
        self._vault_id = parse_vault_id(vault_id)
        self._content_type = kwargs.get("content_type", None)
        self._key_id = kwargs.get("key_id", None)
        self._managed = kwargs.get("managed", None)
        self._tags = kwargs.get("tags", None)

    @classmethod
    def _from_secret_bundle(cls, secret_bundle):
        # type: (_models.SecretBundle) -> SecretAttributes
        """Construct a SecretAttributes from an autorest-generated SecretBundle"""
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
        # type: (_models.SecretItem) -> SecretAttributes
        """Construct a SecretAttributes from an autorest-generated SecretItem"""
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
        """:rtype: str"""
        return self._content_type

    @property
    def id(self):
        # type: () -> str
        """:rtype: str"""
        return self._id

    @property
    def key_id(self):
        # type: () -> str
        """
        If this secret backs a certificate, this property is the identifier of the corresponding key.

        :rtype: str
        """
        return self._key_id

    @property
    def enabled(self):
        # type: () -> bool
        """:rtype: bool"""
        return self._attributes.enabled

    @property
    def not_before(self):
        # type: () -> datetime
        """
        Not-before time, in UTC

        :rtype: datetime.datetime
        """
        return self._attributes.not_before

    @property
    def expires(self):
        # type: () -> datetime
        """
        When the secret expires, in UTC

        :rtype: datetime.datetime
        """
        return self._attributes.expires

    @property
    def created(self):
        # type: () -> datetime
        """
        When the secret was created, in UTC

        :rtype: datetime.datetime
        """
        return self._attributes.created

    @property
    def updated(self):
        # type: () -> datetime
        """
        When the secret was last updated, in UTC

        :rtype: datetime.datetime
        """
        return self._attributes.updated

    @property
    def recovery_level(self):
        # type: () -> str
        """
        The vault's deletion recovery level for secrets

        :rtype: str
        """
        return self._attributes.recovery_level

    @property
    def vault_url(self):
        # type: () -> str
        """
        URL of the vault containing the secret

        :rtype: str
        """
        return self._vault_id.vault_url

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
    def tags(self):
        # type: () -> Dict[str, str]
        """
        Application specific metadata in the form of key-value pairs

        :rtype: dict"""
        return self._tags


class Secret(SecretAttributes):
    """All a secret's attributes, and its value."""

    def __init__(self, attributes, vault_id, value, **kwargs):
        super(Secret, self).__init__(attributes, vault_id, **kwargs)
        self._value = value

    @classmethod
    def _from_secret_bundle(cls, secret_bundle):
        # type: (_models.SecretBundle) -> Secret
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
        """
        The secret value

        :rtype: str
        """
        return self._value


class DeletedSecret(SecretAttributes):
    """A deleted secret's attributes, as well as when it will be purged, if soft-delete is enabled for its vault."""

    def __init__(
        self,
        attributes,  # type: _models.SecretAttributes
        vault_id,  # type: str
        deleted_date=None,  # type: Optional[datetime]
        recovery_id=None,  # type: Optional[str]
        scheduled_purge_date=None,  # type: Optional[datetime]
        **kwargs  # type: **Any
    ):
        # type: (...) -> None
        super(DeletedSecret, self).__init__(attributes, vault_id, **kwargs)
        self._deleted_date = deleted_date
        self._recovery_id = recovery_id
        self._scheduled_purge_date = scheduled_purge_date

    @classmethod
    def _from_deleted_secret_bundle(cls, deleted_secret_bundle):
        # type: (_models.DeletedSecretBundle) -> DeletedSecret
        """Construct a DeletedSecret from an autorest-generated DeletedSecretBundle"""
        return cls(
            deleted_secret_bundle.attributes,
            deleted_secret_bundle.id,
            deleted_date=deleted_secret_bundle.deleted_date,
            content_type=deleted_secret_bundle.content_type,
            recovery_id=deleted_secret_bundle.recovery_id,
            scheduled_purge_date=deleted_secret_bundle.scheduled_purge_date,
            key_id=deleted_secret_bundle.kid,
            managed=deleted_secret_bundle.managed,
            tags=deleted_secret_bundle.tags,
        )

    @classmethod
    def _from_deleted_secret_item(cls, deleted_secret_item):
        # type: (_models.DeletedSecretItem) -> DeletedSecret
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
        """
        When the secret was deleted, in UTC

        :rtype: datetime.datetime
        """
        return self._deleted_date

    @property
    def recovery_id(self):
        # type: () -> str
        """
        An identifier used to recover the deleted secret

        :rtype: str
        """
        return self._recovery_id

    @property
    def scheduled_purge_date(self):
        # type: () -> datetime
        """
        When the secret is scheduled to be purged, in UTC

        :rtype: datetime.datetime
        """
        return self._scheduled_purge_date
