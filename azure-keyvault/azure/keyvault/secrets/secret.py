# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from msrest.serialization import Model
from ..vault_id import _parse_vault_id
class Secret(Model):
    """A secret consisting of a value, id and its attributes.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param value: The secret value.
    :type value: str
    :param id: The secret id.
    :type id: str
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
        vault_id = self._get_vault_id()
        return vault_id.vault_url if vault_id else None

    @property
    def name(self):
        vault_id = self._get_vault_id()
        return vault_id.name if vault_id else None

    @property
    def version(self):
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
