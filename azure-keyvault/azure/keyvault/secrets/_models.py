# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from msrest.serialization import Model
from msrest.paging import Paged
from .._internal import _parse_vault_id


class Secret(Model):
    """A secret consisting of a value, id and its attributes.

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

    _validation = {
        'kid': {'readonly': True},
        'managed': {'readonly': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': 'str'},
        'id': {'key': 'id', 'type': 'str'},
        'content_type': {'key': 'contentType', 'type': 'str'},
        'attributes': {'key': 'attributes', 'type': 'SecretAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'key_id': {'key': 'kid', 'type': 'str'},
        'managed': {'key': 'managed', 'type': 'bool'},
    }

    @property
    def vault_url(self):
        """The url to the vault containing the secret"""
        vault_id = self._get_vault_id()
        return vault_id.vault_url if vault_id else None

    @property
    def name(self):
        """The name of the secret"""
        vault_id = self._get_vault_id()
        return vault_id.name if vault_id else None

    @property
    def version(self):
        """The version of the secret"""
        vault_id = self._get_vault_id()
        return vault_id.version if vault_id else None

    def __init__(self, **kwargs):
        super(Secret, self).__init__(**kwargs)
        self.value = kwargs.get('value', None)
        self.id = kwargs.get('id', None)
        self.content_type = kwargs.get('content_type', None)
        self.attributes = kwargs.get('attributes', None)
        self.tags = kwargs.get('tags', None)
        self.key_id = None
        self.managed = None
        self._vault_id = None

    def _get_vault_id(self):
        if not self._vault_id and self.id:
            self._vault_id = _parse_vault_id(self.id)
        return self._vault_id


class SecretAttributes(Model):
    """The secret management attributes.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param bool enabled: Determines whether the object is enabled.
    :param datetime not_before: Not before date in UTC.
    :param datetime expires: Expiry date in UTC.
    :ivar datetime created: Creation time in UTC.
    :ivar datetime updated: Last updated time in UTC.
    :ivar str recovery_level: Reflects the deletion recovery level currently in
     effect for secrets in the current vault. If it contains 'Purgeable', the
     secret can be permanently deleted by a privileged user; otherwise, only
     the system can purge the secret, at the end of the retention interval.
     Possible values include: 'Purgeable', 'Recoverable+Purgeable',
     'Recoverable', 'Recoverable+ProtectedSubscription'
    """

    _validation = {
        'created': {'readonly': True},
        'updated': {'readonly': True},
        'recovery_level': {'readonly': True},
    }

    _attribute_map = {
        'enabled': {'key': 'enabled', 'type': 'bool'},
        'not_before': {'key': 'nbf', 'type': 'unix-time'},
        'expires': {'key': 'exp', 'type': 'unix-time'},
        'created': {'key': 'created', 'type': 'unix-time'},
        'updated': {'key': 'updated', 'type': 'unix-time'},
        'recovery_level': {'key': 'recoveryLevel', 'type': 'str'},
    }

    def __init__(self, **kwargs):
        super(SecretAttributes, self).__init__(**kwargs)
        self.enabled = kwargs.get('enabled', None)
        self.not_before = kwargs.get('not_before', None)
        self.expires = kwargs.get('expires', None)
        self.created = None
        self.updated = None
        self.recovery_level = None


class SecretPaged(Paged):
    """
    A paging container for iterating over a list of :class:`Secret <azure.keyvault.secrets.Secret>` object
    """

    _attribute_map = {
        'next_link': {'key': 'nextLink', 'type': 'str'},
        'current_page': {'key': 'value', 'type': '[Secret]'}
    }

    def __init__(self, *args, **kwargs):

        super(SecretPaged, self).__init__(*args, **kwargs)


class DeletedSecret(Secret):
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

    _validation = {
        'kid': {'readonly': True},
        'managed': {'readonly': True},
        'scheduled_purge_date': {'readonly': True},
        'deleted_date': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'content_type': {'key': 'contentType', 'type': 'str'},
        'attributes': {'key': 'attributes', 'type': 'SecretAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'kid': {'key': 'kid', 'type': 'str'},
        'managed': {'key': 'managed', 'type': 'bool'},
        'recovery_id': {'key': 'recoveryId', 'type': 'str'},
        'scheduled_purge_date': {'key': 'scheduledPurgeDate', 'type': 'unix-time'},
        'deleted_date': {'key': 'deletedDate', 'type': 'unix-time'},
    }

    def __init__(self, **kwargs):
        super(DeletedSecret, self).__init__(**kwargs)
        self.recovery_id = kwargs.get('recovery_id', None)
        self.scheduled_purge_date = None
        self.deleted_date = None
