# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from msrest.serialization import Model
from msrest.paging import Paged
from .._internal import _parse_vault_id, _SecretManagementAttributes
from datetime import datetime
from typing import Any, Mapping

class SecretAttributes(Model):
    """A secret's id and attributes.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param str id: The secret id.
    :param str content_type: The content type of the secret.
    :param tags: Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :ivar str key_id: If this is a secret backing a KV certificate, then this field
     specifies the corresponding key backing the KV certificate.
    :ivar bool managed: True if the secret's lifetime is managed by key vault. If
     this is a secret backing a certificate, then managed will be true.
    """

    _validation = {
        'key_id': {'readonly': True},
        'managed': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'content_type': {'key': 'contentType', 'type': 'str'},
        '_management_attributes': {'key': 'attributes', 'type': '_SecretManagementAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'key_id': {'key': 'kid', 'type': 'str'},
        'managed': {'key': 'managed', 'type': 'bool'},
    }

    def __init__(self, **kwargs):
        # type: (Mapping[str, Any]) -> None
        super(SecretAttributes, self).__init__(**kwargs)
        self.id = kwargs.get('id', None)
        if self.id:
            self._vault_id = _parse_vault_id(self.id)
        self.content_type = kwargs.get('content_type', None)
        self._management_attributes = kwargs.get('_management_attributes', None)
        self.tags = kwargs.get('tags', None)
        self.key_id = None
        self.managed = None

    @property
    def enabled(self):
        # type: () -> bool
        """Gets the Secret's 'enabled' attribute"""
        return self._management_attributes.enabled

    @property
    def not_before(self):
        # type: () -> datetime
        """Gets the Secret's 'not_before' attribute"""
        return self._management_attributes.not_before

    @property
    def expires(self):
        # type: () -> datetime
        """Gets the Secret's 'expires' attribute"""
        return self._management_attributes.expires

    @property
    def created(self):
        # type: () -> datetime
        """Gets the Secret's 'created' attribute"""
        return self._management_attributes.created

    @property
    def updated(self):
        # type: () -> datetime
        """Gets the Secret's 'updated' attribute"""
        return self._management_attributes.updated

    @property
    def recovery_level(self):
        # type: () -> str
        """Gets the Secret's 'recovery_level' attribute"""
        return self._management_attributes.recovery_level

    @property
    def vault_url(self):
        # type: () -> str
        """The url of the vault containing the secret"""
        return self._vault_id.vault_url if self._vault_id else None

    @property
    def name(self):
        # type: () -> str
        """The name of the secret"""
        return self._vault_id.name if self._vault_id else None

    @property
    def version(self):
        # type: () -> str
        """The version of the secret"""
        return self._vault_id.version if self._vault_id else None


class Secret(SecretAttributes):
    """A secret consisting of its attributes, a value, and id.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param str value: The secret value.
    :param str id: The secret id.
    :param str content_type: The content type of the secret.
    :param attributes: The secret management attributes.
    :type attributes: ~azure.keyvault.v7_0.models.SecretAttributes
    :param tags: Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :ivar str kid: If this is a secret backing a KV certificate, then this field
     specifies the corresponding key backing the KV certificate.
    :ivar bool managed: True if the secret's lifetime is managed by key vault. If
     this is a secret backing a certificate, then managed will be true.
    """

    # i.e., Secret is SecretAttributes plus a value
    _attribute_map = dict({
        'value': {'key': 'value', 'type': 'str'}
    }, **SecretAttributes._attribute_map)

    def __init__(self, **kwargs):
        # type: (Mapping[str, Any]) -> None
        super(Secret, self).__init__(**kwargs)
        self.value = kwargs.get('value', None)


class SecretAttributesPaged(Paged):
    """A paging container for iterating over a list of :class:`SecretAttributes <azure.keyvault.secrets.SecretAttributes>` objects
    """

    _attribute_map = {
        'next_link': {'key': 'nextLink', 'type': 'str'},
        'current_page': {'key': 'value', 'type': '[SecretAttributes]'}
    }

    def __init__(self, *args, **kwargs):
        super(SecretAttributesPaged, self).__init__(*args, **kwargs)


class DeletedSecret(SecretAttributes):
    """A Deleted Secret consisting of its previous id, attributes and its tags, as
    well as information on when it will be purged.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param str id: The secret id.
    :param content_type: The content type of the secret.
    :type content_type: str
    :param attributes: The secret management attributes.
    :type attributes: ~azure.keyvault.v7_0.models.SecretAttributes
    :param tags: Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :ivar kid: If this is a secret backing a KV certificate, then this field
     specifies the corresponding key backing the KV certificate.
    :vartype kid: str
    :ivar managed: True if the secret's lifetime is managed by key vault. If
     this is a secret backing a certificate, then managed will be true.
    :vartype managed: bool
    :param recovery_id: The url of the recovery object, used to identify and
     recover the deleted secret.
    :type recovery_id: str
    :ivar scheduled_purge_date: The time when the secret is scheduled to be
     purged, in UTC
    :vartype scheduled_purge_date: datetime
    :ivar deleted_date: The time when the secret was deleted, in UTC
    :vartype deleted_date: datetime
    """

    _validation = dict(
        {
        'scheduled_purge_date': {'readonly': True},
        'deleted_date': {'readonly': True},
        },
        **SecretAttributes._validation
    )

    # DeletedSecret is SecretAttributes plus deletion info
    _attribute_map = dict(
        {
            "recovery_id": {"key": "recoveryId", "type": "str"},
            "scheduled_purge_date": {"key": "scheduledPurgeDate", "type": "unix-time"},
            "deleted_date": {"key": "deletedDate", "type": "unix-time"},
        },
        **SecretAttributes._attribute_map
    )

    def __init__(self, **kwargs):
        # type: (Mapping[str, Any]) -> None
        super(DeletedSecret, self).__init__(**kwargs)
        self.recovery_id = kwargs.get('recovery_id', None)
        self.scheduled_purge_date = None
        self.deleted_date = None


class DeletedSecretPaged(Paged):
    """A paging container for iterating over a list of :class:`DeletedSecret <azure.keyvault.secrets.DeletedSecret>` objects
    """

    _attribute_map = {
        "next_link": {"key": "nextLink", "type": "str"},
        "current_page": {"key": "value", "type": "[DeletedSecret]"},
    }

    def __init__(self, *args, **kwargs):
        super(DeletedSecretPaged, self).__init__(*args, **kwargs)
