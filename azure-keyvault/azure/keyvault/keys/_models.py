from msrest.paging import Paged
from msrest.serialization import Model
from .._internal import _parse_vault_id


class JsonWebKey(Model):
    """As of http://tools.ietf.org/html/draft-ietf-jose-json-web-key-18.

    :param kid: Key identifier.
    :type kid: str
    :param kty: JsonWebKey Key Type (kty), as defined in
     https://tools.ietf.org/html/draft-ietf-jose-json-web-algorithms-40.
     Possible values include: 'EC', 'EC-HSM', 'RSA', 'RSA-HSM', 'oct'
    :type kty: str or ~azure.keyvault.v7_0.models.JsonWebKeyType
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
    :param crv: Elliptic curve name. For valid values, see
     JsonWebKeyCurveName. Possible values include: 'P-256', 'P-384', 'P-521',
     'P-256K'
    :type crv: str or ~azure.keyvault.v7_0.models.JsonWebKeyCurveName
    :param x: X component of an EC public key.
    :type x: bytes
    :param y: Y component of an EC public key.
    :type y: bytes
    """

    _attribute_map = {
        "kid": {"key": "kid", "type": "str"},
        "kty": {"key": "kty", "type": "str"},
        "key_ops": {"key": "key_ops", "type": "[str]"},
        "n": {"key": "n", "type": "base64"},
        "e": {"key": "e", "type": "base64"},
        "d": {"key": "d", "type": "base64"},
        "dp": {"key": "dp", "type": "base64"},
        "dq": {"key": "dq", "type": "base64"},
        "qi": {"key": "qi", "type": "base64"},
        "p": {"key": "p", "type": "base64"},
        "q": {"key": "q", "type": "base64"},
        "k": {"key": "k", "type": "base64"},
        "t": {"key": "key_hsm", "type": "base64"},
        "crv": {"key": "crv", "type": "str"},
        "x": {"key": "x", "type": "base64"},
        "y": {"key": "y", "type": "base64"},
    }

    def __init__(self, **kwargs):
        super(JsonWebKey, self).__init__(**kwargs)
        self.kid = kwargs.get("kid", None)
        self.kty = kwargs.get("kty", None)
        self.key_ops = kwargs.get("key_ops", None)
        self.n = kwargs.get("n", None)
        self.e = kwargs.get("e", None)
        self.d = kwargs.get("d", None)
        self.dp = kwargs.get("dp", None)
        self.dq = kwargs.get("dq", None)
        self.qi = kwargs.get("qi", None)
        self.p = kwargs.get("p", None)
        self.q = kwargs.get("q", None)
        self.k = kwargs.get("k", None)
        self.t = kwargs.get("t", None)
        self.crv = kwargs.get("crv", None)
        self.x = kwargs.get("x", None)
        self.y = kwargs.get("y", None)


class Key(Model):
    _validation = {"managed": {"readonly": True}}

    _attribute_map = {
        "key_material": {"key": "key", "type": "JsonWebKey"},
        "attributes": {"key": "attributes", "type": "KeyAttributes"},
        "tags": {"key": "tags", "type": "{str}"},
        "managed": {"key": "managed", "type": "bool"},
    }

    def __init__(self, **kwargs):
        super(Key, self).__init__(**kwargs)
        self.attributes = kwargs.get("attributes", None)
        self.tags = kwargs.get("tags", None)
        self.managed = None
        self._vault_id = None

    @property
    def id(self):
        return self.key_material.kid

    @property
    def name(self):
        vault_id = self._get_vault_id()
        return vault_id.name if vault_id else None

    @property
    def vault_url(self):
        vault_id = self._get_vault_id()
        return vault_id.vault_url if vault_id else None

    @property
    def version(self):
        vault_id = self._get_vault_id()
        return vault_id.version if vault_id else None

    def _get_vault_id(self):
        if not self._vault_id and self.key_material and self.key_material.kid:
            self._vault_id = _parse_vault_id(self.key_material.kid)
        return self._vault_id


class DeletedKey(Key):
    """A DeletedKey consisting of a JsonWebKey plus its Attributes and deletion
    info.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param key: The Json web key.
    :type key: ~azure.keyvault.v7_0.models.JsonWebKey
    :param attributes: The key management attributes.
    :type attributes: ~azure.keyvault.v7_0.models.KeyAttributes
    :param tags: Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :ivar managed: True if the key's lifetime is managed by key vault. If this
     is a key backing a certificate, then managed will be true.
    :vartype managed: bool
    :param recovery_id: The url of the recovery object, used to identify and
     recover the deleted key.
    :type recovery_id: str
    :ivar scheduled_purge_date: The time when the key is scheduled to be
     purged, in UTC
    :vartype scheduled_purge_date: datetime
    :ivar deleted_date: The time when the key was deleted, in UTC
    :vartype deleted_date: datetime
    """

    _validation = {
        "managed": {"readonly": True},
        "scheduled_purge_date": {"readonly": True},
        "deleted_date": {"readonly": True},
    }

    _attribute_map = {
        "key": {"key": "key", "type": "JsonWebKey"},
        "attributes": {"key": "attributes", "type": "KeyAttributes"},
        "tags": {"key": "tags", "type": "{str}"},
        "managed": {"key": "managed", "type": "bool"},
        "recovery_id": {"key": "recoveryId", "type": "str"},
        "scheduled_purge_date": {"key": "scheduledPurgeDate", "type": "unix-time"},
        "deleted_date": {"key": "deletedDate", "type": "unix-time"},
    }

    def __init__(self, **kwargs):
        super(DeletedKey, self).__init__(**kwargs)
        self.recovery_id = kwargs.get("recovery_id", None)
        self.scheduled_purge_date = None
        self.deleted_date = None


class KeyAttributes(Model):
    """The attributes of a key managed by the key vault service.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param enabled: Determines whether the object is enabled.
    :type enabled: bool
    :param not_before: Not before date in UTC.
    :type not_before: datetime
    :param expires: Expiry date in UTC.
    :type expires: datetime
    :ivar created: Creation time in UTC.
    :vartype created: datetime
    :ivar updated: Last updated time in UTC.
    :vartype updated: datetime
    :ivar recovery_level: Reflects the deletion recovery level currently in
     effect for keys in the current vault. If it contains 'Purgeable' the key
     can be permanently deleted by a privileged user; otherwise, only the
     system can purge the key, at the end of the retention interval. Possible
     values include: 'Purgeable', 'Recoverable+Purgeable', 'Recoverable',
     'Recoverable+ProtectedSubscription'
    :vartype recovery_level: str or
     ~azure.keyvault.v7_0.models.DeletionRecoveryLevel
    """

    _validation = {
        "created": {"readonly": True},
        "updated": {"readonly": True},
        "recovery_level": {"readonly": True},
    }

    _attribute_map = {
        "enabled": {"key": "enabled", "type": "bool"},
        "not_before": {"key": "nbf", "type": "unix-time"},
        "expires": {"key": "exp", "type": "unix-time"},
        "created": {"key": "created", "type": "unix-time"},
        "updated": {"key": "updated", "type": "unix-time"},
        "recovery_level": {"key": "recoveryLevel", "type": "str"},
    }

    def __init__(self, **kwargs):
        super(KeyAttributes, self).__init__(**kwargs)
        self.enabled = kwargs.get("enabled", None)
        self.not_before = kwargs.get("not_before", None)
        self.expires = kwargs.get("expires", None)
        self.created = None
        self.updated = None
        self.recovery_level = None


class KeyUpdateParameters(Model):
    """The key update parameters.
    :param key_ops: Json web key operations. For more information on possible
     key operations, see JsonWebKeyOperation.
    :type key_ops: list[str or
     ~azure.keyvault.v7_0.models.JsonWebKeyOperation]
    :param key_attributes:
    :type key_attributes: ~azure.keyvault.v7_0.models.KeyAttributes
    :param tags: Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    """

    _attribute_map = {
        "key_ops": {"key": "key_ops", "type": "[str]"},
        "key_attributes": {"key": "attributes", "type": "KeyAttributes"},
        "tags": {"key": "tags", "type": "{str}"},
    }

    def __init__(self, **kwargs):
        super(KeyUpdateParameters, self).__init__(**kwargs)
        self.key_ops = kwargs.get("key_ops", None)
        self.key_attributes = kwargs.get("key_attributes", None)
        self.tags = kwargs.get("tags", None)


class KeyCreateParameters(Model):
    """The key create parameters.

    All required parameters must be populated in order to send to Azure.

    :param kty: Required. The type of key to create. For valid values, see
     JsonWebKeyType. Possible values include: 'EC', 'EC-HSM', 'RSA', 'RSA-HSM',
     'oct'
    :type kty: str or ~azure.keyvault.v7_0.models.JsonWebKeyType
    :param key_size: The key size in bits. For example: 2048, 3072, or 4096
     for RSA.
    :type key_size: int
    :param key_ops:
    :type key_ops: list[str or
     ~azure.keyvault.v7_0.models.JsonWebKeyOperation]
    :param key_attributes:
    :type key_attributes: ~azure.keyvault.v7_0.models.KeyAttributes
    :param tags: Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :param curve: Elliptic curve name. For valid values, see
     JsonWebKeyCurveName. Possible values include: 'P-256', 'P-384', 'P-521',
     'P-256K'
    :type curve: str or ~azure.keyvault.v7_0.models.JsonWebKeyCurveName
    """

    _validation = {"kty": {"required": True, "min_length": 1}}

    _attribute_map = {
        "kty": {"key": "kty", "type": "str"},
        "key_size": {"key": "key_size", "type": "int"},
        "key_ops": {"key": "key_ops", "type": "[str]"},
        "key_attributes": {"key": "attributes", "type": "KeyAttributes"},
        "tags": {"key": "tags", "type": "{str}"},
        "curve": {"key": "crv", "type": "str"},
    }

    def __init__(self, **kwargs):
        super(KeyCreateParameters, self).__init__(**kwargs)
        self.kty = kwargs.get("kty", None)
        self.key_size = kwargs.get("key_size", None)
        self.key_ops = kwargs.get("key_ops", None)
        self.key_attributes = kwargs.get("key_attributes", None)
        self.tags = kwargs.get("tags", None)
        self.curve = kwargs.get("curve", None)


class KeyItem(Model):
    """The key item containing key metadata.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param kid: Key identifier.
    :type kid: str
    :param attributes: The key management attributes.
    :type attributes: ~azure.keyvault.v7_0.models.KeyAttributes
    :param tags: Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :ivar managed: True if the key's lifetime is managed by key vault. If this
     is a key backing a certificate, then managed will be true.
    :vartype managed: bool
    """

    _validation = {"managed": {"readonly": True}}

    _attribute_map = {
        "kid": {"key": "kid", "type": "str"},
        "attributes": {"key": "attributes", "type": "KeyAttributes"},
        "tags": {"key": "tags", "type": "{str}"},
        "managed": {"key": "managed", "type": "bool"},
    }

    def __init__(self, **kwargs):
        super(KeyItem, self).__init__(**kwargs)
        self.kid = kwargs.get("kid", None)
        self.attributes = kwargs.get("attributes", None)
        self.tags = kwargs.get("tags", None)
        self.managed = None


class DeletedKeyItem(KeyItem):
    """The deleted key item containing the deleted key metadata and information
    about deletion.
    Variables are only populated by the server, and will be ignored when
    sending a request.
    :param kid: Key identifier.
    :type kid: str
    :param attributes: The key management attributes.
    :type attributes: ~azure.keyvault.v7_0.models.KeyAttributes
    :param tags: Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :ivar managed: True if the key's lifetime is managed by key vault. If this
     is a key backing a certificate, then managed will be true.
    :vartype managed: bool
    :param recovery_id: The url of the recovery object, used to identify and
     recover the deleted key.
    :type recovery_id: str
    :ivar scheduled_purge_date: The time when the key is scheduled to be
     purged, in UTC
    :vartype scheduled_purge_date: datetime
    :ivar deleted_date: The time when the key was deleted, in UTC
    :vartype deleted_date: datetime
    """

    _validation = {
        "managed": {"readonly": True},
        "scheduled_purge_date": {"readonly": True},
        "deleted_date": {"readonly": True},
    }

    _attribute_map = {
        "kid": {"key": "kid", "type": "str"},
        "attributes": {"key": "attributes", "type": "KeyAttributes"},
        "tags": {"key": "tags", "type": "{str}"},
        "managed": {"key": "managed", "type": "bool"},
        "recovery_id": {"key": "recoveryId", "type": "str"},
        "scheduled_purge_date": {"key": "scheduledPurgeDate", "type": "unix-time"},
        "deleted_date": {"key": "deletedDate", "type": "unix-time"},
    }

    def __init__(self, **kwargs):
        super(DeletedKeyItem, self).__init__(**kwargs)
        self.recovery_id = kwargs.get("recovery_id", None)
        self.scheduled_purge_date = None
        self.deleted_date = None


class DeletedKeyItemPaged(Paged):
    """
    A paging container for iterating over a list of :class:`DeletedKeyItem <azure.keyvault.v7_0.models.DeletedKeyItem>` object
    """

    _attribute_map = {
        "next_link": {"key": "nextLink", "type": "str"},
        "current_page": {"key": "value", "type": "[DeletedKeyItem]"},
    }

    def __init__(self, *args, **kwargs):
        super(DeletedKeyItemPaged, self).__init__(*args, **kwargs)


class KeyItemPaged(Paged):
    """
    A paging container for iterating over a list of :class:`KeyItem <azure.keyvault.v7_0.models.KeyItem>` object
    """

    _attribute_map = {
        "next_link": {"key": "nextLink", "type": "str"},
        "current_page": {"key": "value", "type": "[KeyItem]"},
    }

    def __init__(self, *args, **kwargs):

        super(KeyItemPaged, self).__init__(*args, **kwargs)
