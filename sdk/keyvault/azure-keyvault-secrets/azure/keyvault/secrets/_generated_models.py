# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
# pylint: skip-file (avoids crash due to six.with_metaclass https://github.com/PyCQA/astroid/issues/713)

from enum import Enum, EnumMeta
import msrest.serialization
from six import with_metaclass


class Attributes(msrest.serialization.Model):
    """The object attributes managed by the KeyVault service.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param enabled: Determines whether the object is enabled.
    :type enabled: bool
    :param not_before: Not before date in UTC.
    :type not_before: ~datetime.datetime
    :param expires: Expiry date in UTC.
    :type expires: ~datetime.datetime
    :ivar created: Creation time in UTC.
    :vartype created: ~datetime.datetime
    :ivar updated: Last updated time in UTC.
    :vartype updated: ~datetime.datetime
    """

    _validation = {
        'created': {'readonly': True},
        'updated': {'readonly': True},
    }

    _attribute_map = {
        'enabled': {'key': 'enabled', 'type': 'bool'},
        'not_before': {'key': 'nbf', 'type': 'unix-time'},
        'expires': {'key': 'exp', 'type': 'unix-time'},
        'created': {'key': 'created', 'type': 'unix-time'},
        'updated': {'key': 'updated', 'type': 'unix-time'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(Attributes, self).__init__(**kwargs)
        self.enabled = kwargs.get('enabled', None)
        self.not_before = kwargs.get('not_before', None)
        self.expires = kwargs.get('expires', None)
        self.created = None
        self.updated = None


class BackupSecretResult(msrest.serialization.Model):
    """The backup secret result, containing the backup blob.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar value: The backup blob containing the backed up secret.
    :vartype value: bytes
    """

    _validation = {
        'value': {'readonly': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': 'base64'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(BackupSecretResult, self).__init__(**kwargs)
        self.value = None


class SecretBundle(msrest.serialization.Model):
    """A secret consisting of a value, id and its attributes.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param value: The secret value.
    :type value: str
    :param id: The secret id.
    :type id: str
    :param content_type: The content type of the secret.
    :type content_type: str
    :param attributes: The secret management attributes.
    :type attributes: ~azure.keyvault.v7_1.models.SecretAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :ivar kid: If this is a secret backing a KV certificate, then this field specifies the
     corresponding key backing the KV certificate.
    :vartype kid: str
    :ivar managed: True if the secret's lifetime is managed by key vault. If this is a secret
     backing a certificate, then managed will be true.
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
        'kid': {'key': 'kid', 'type': 'str'},
        'managed': {'key': 'managed', 'type': 'bool'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SecretBundle, self).__init__(**kwargs)
        self.value = kwargs.get('value', None)
        self.id = kwargs.get('id', None)
        self.content_type = kwargs.get('content_type', None)
        self.attributes = kwargs.get('attributes', None)
        self.tags = kwargs.get('tags', None)
        self.kid = None
        self.managed = None


class DeletedSecretBundle(SecretBundle):
    # pylint: disable=line-too-long
    """A Deleted Secret consisting of its previous id, attributes and its tags, as well as information on when it will be purged.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param value: The secret value.
    :type value: str
    :param id: The secret id.
    :type id: str
    :param content_type: The content type of the secret.
    :type content_type: str
    :param attributes: The secret management attributes.
    :type attributes: ~azure.keyvault.v7_1.models.SecretAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :ivar kid: If this is a secret backing a KV certificate, then this field specifies the
     corresponding key backing the KV certificate.
    :vartype kid: str
    :ivar managed: True if the secret's lifetime is managed by key vault. If this is a secret
     backing a certificate, then managed will be true.
    :vartype managed: bool
    :param recovery_id: The url of the recovery object, used to identify and recover the deleted
     secret.
    :type recovery_id: str
    :ivar scheduled_purge_date: The time when the secret is scheduled to be purged, in UTC.
    :vartype scheduled_purge_date: ~datetime.datetime
    :ivar deleted_date: The time when the secret was deleted, in UTC.
    :vartype deleted_date: ~datetime.datetime
    """

    _validation = {
        'kid': {'readonly': True},
        'managed': {'readonly': True},
        'scheduled_purge_date': {'readonly': True},
        'deleted_date': {'readonly': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': 'str'},
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

    def __init__(
        self,
        **kwargs
    ):
        super(DeletedSecretBundle, self).__init__(**kwargs)
        self.recovery_id = kwargs.get('recovery_id', None)
        self.scheduled_purge_date = None
        self.deleted_date = None


class SecretItem(msrest.serialization.Model):
    """The secret item containing secret metadata.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param id: Secret identifier.
    :type id: str
    :param attributes: The secret management attributes.
    :type attributes: ~azure.keyvault.v7_1.models.SecretAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :param content_type: Type of the secret value such as a password.
    :type content_type: str
    :ivar managed: True if the secret's lifetime is managed by key vault. If this is a key backing
     a certificate, then managed will be true.
    :vartype managed: bool
    """

    _validation = {
        'managed': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'attributes': {'key': 'attributes', 'type': 'SecretAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'content_type': {'key': 'contentType', 'type': 'str'},
        'managed': {'key': 'managed', 'type': 'bool'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SecretItem, self).__init__(**kwargs)
        self.id = kwargs.get('id', None)
        self.attributes = kwargs.get('attributes', None)
        self.tags = kwargs.get('tags', None)
        self.content_type = kwargs.get('content_type', None)
        self.managed = None


class DeletedSecretItem(SecretItem):
    """The deleted secret item containing metadata about the deleted secret.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param id: Secret identifier.
    :type id: str
    :param attributes: The secret management attributes.
    :type attributes: ~azure.keyvault.v7_1.models.SecretAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :param content_type: Type of the secret value such as a password.
    :type content_type: str
    :ivar managed: True if the secret's lifetime is managed by key vault. If this is a key backing
     a certificate, then managed will be true.
    :vartype managed: bool
    :param recovery_id: The url of the recovery object, used to identify and recover the deleted
     secret.
    :type recovery_id: str
    :ivar scheduled_purge_date: The time when the secret is scheduled to be purged, in UTC.
    :vartype scheduled_purge_date: ~datetime.datetime
    :ivar deleted_date: The time when the secret was deleted, in UTC.
    :vartype deleted_date: ~datetime.datetime
    """

    _validation = {
        'managed': {'readonly': True},
        'scheduled_purge_date': {'readonly': True},
        'deleted_date': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'attributes': {'key': 'attributes', 'type': 'SecretAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'content_type': {'key': 'contentType', 'type': 'str'},
        'managed': {'key': 'managed', 'type': 'bool'},
        'recovery_id': {'key': 'recoveryId', 'type': 'str'},
        'scheduled_purge_date': {'key': 'scheduledPurgeDate', 'type': 'unix-time'},
        'deleted_date': {'key': 'deletedDate', 'type': 'unix-time'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(DeletedSecretItem, self).__init__(**kwargs)
        self.recovery_id = kwargs.get('recovery_id', None)
        self.scheduled_purge_date = None
        self.deleted_date = None


class DeletedSecretListResult(msrest.serialization.Model):
    """The deleted secret list result.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar value: A response message containing a list of the deleted secrets in the vault along
     with a link to the next page of deleted secrets.
    :vartype value: list[~azure.keyvault.v7_1.models.DeletedSecretItem]
    :ivar next_link: The URL to get the next set of deleted secrets.
    :vartype next_link: str
    """

    _validation = {
        'value': {'readonly': True},
        'next_link': {'readonly': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': '[DeletedSecretItem]'},
        'next_link': {'key': 'nextLink', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(DeletedSecretListResult, self).__init__(**kwargs)
        self.value = None
        self.next_link = None


class Error(msrest.serialization.Model):
    """The key vault server error.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar code: The error code.
    :vartype code: str
    :ivar message: The error message.
    :vartype message: str
    :ivar inner_error: The key vault server error.
    :vartype inner_error: ~azure.keyvault.v7_1.models.Error
    """

    _validation = {
        'code': {'readonly': True},
        'message': {'readonly': True},
        'inner_error': {'readonly': True},
    }

    _attribute_map = {
        'code': {'key': 'code', 'type': 'str'},
        'message': {'key': 'message', 'type': 'str'},
        'inner_error': {'key': 'innererror', 'type': 'Error'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(Error, self).__init__(**kwargs)
        self.code = None
        self.message = None
        self.inner_error = None


class KeyVaultError(msrest.serialization.Model):
    """The key vault error exception.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar error: The key vault server error.
    :vartype error: ~azure.keyvault.v7_1.models.Error
    """

    _validation = {
        'error': {'readonly': True},
    }

    _attribute_map = {
        'error': {'key': 'error', 'type': 'Error'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(KeyVaultError, self).__init__(**kwargs)
        self.error = None


class SecretAttributes(Attributes):
    """The secret management attributes.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param enabled: Determines whether the object is enabled.
    :type enabled: bool
    :param not_before: Not before date in UTC.
    :type not_before: ~datetime.datetime
    :param expires: Expiry date in UTC.
    :type expires: ~datetime.datetime
    :ivar created: Creation time in UTC.
    :vartype created: ~datetime.datetime
    :ivar updated: Last updated time in UTC.
    :vartype updated: ~datetime.datetime
    :ivar recoverable_days: softDelete data retention days. Value should be >=7 and <=90 when
     softDelete enabled, otherwise 0.
    :vartype recoverable_days: int
    :ivar recovery_level: Reflects the deletion recovery level currently in effect for secrets in
     the current vault. If it contains 'Purgeable', the secret can be permanently deleted by a
     privileged user; otherwise, only the system can purge the secret, at the end of the retention
     interval. Possible values include: "Purgeable", "Recoverable+Purgeable", "Recoverable",
     "Recoverable+ProtectedSubscription", "CustomizedRecoverable+Purgeable",
     "CustomizedRecoverable", "CustomizedRecoverable+ProtectedSubscription".
    :vartype recovery_level: str or ~azure.keyvault.v7_1.models.DeletionRecoveryLevel
    """

    _validation = {
        'created': {'readonly': True},
        'updated': {'readonly': True},
        'recoverable_days': {'readonly': True},
        'recovery_level': {'readonly': True},
    }

    _attribute_map = {
        'enabled': {'key': 'enabled', 'type': 'bool'},
        'not_before': {'key': 'nbf', 'type': 'unix-time'},
        'expires': {'key': 'exp', 'type': 'unix-time'},
        'created': {'key': 'created', 'type': 'unix-time'},
        'updated': {'key': 'updated', 'type': 'unix-time'},
        'recoverable_days': {'key': 'recoverableDays', 'type': 'int'},
        'recovery_level': {'key': 'recoveryLevel', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SecretAttributes, self).__init__(**kwargs)
        self.recoverable_days = None
        self.recovery_level = None


class SecretListResult(msrest.serialization.Model):
    """The secret list result.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar value: A response message containing a list of secrets in the key vault along with a link
     to the next page of secrets.
    :vartype value: list[~azure.keyvault.v7_1.models.SecretItem]
    :ivar next_link: The URL to get the next set of secrets.
    :vartype next_link: str
    """

    _validation = {
        'value': {'readonly': True},
        'next_link': {'readonly': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': '[SecretItem]'},
        'next_link': {'key': 'nextLink', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SecretListResult, self).__init__(**kwargs)
        self.value = None
        self.next_link = None


class SecretProperties(msrest.serialization.Model):
    """Properties of the key backing a certificate.

    :param content_type: The media type (MIME type).
    :type content_type: str
    """

    _attribute_map = {
        'content_type': {'key': 'contentType', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SecretProperties, self).__init__(**kwargs)
        self.content_type = kwargs.get('content_type', None)


class SecretRestoreParameters(msrest.serialization.Model):
    """The secret restore parameters.

    All required parameters must be populated in order to send to Azure.

    :param secret_bundle_backup: Required. The backup blob associated with a secret bundle.
    :type secret_bundle_backup: bytes
    """

    _validation = {
        'secret_bundle_backup': {'required': True},
    }

    _attribute_map = {
        'secret_bundle_backup': {'key': 'value', 'type': 'base64'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SecretRestoreParameters, self).__init__(**kwargs)
        self.secret_bundle_backup = kwargs['secret_bundle_backup']


class SecretSetParameters(msrest.serialization.Model):
    """The secret set parameters.

    All required parameters must be populated in order to send to Azure.

    :param value: Required. The value of the secret.
    :type value: str
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    :param content_type: Type of the secret value such as a password.
    :type content_type: str
    :param secret_attributes: The secret management attributes.
    :type secret_attributes: ~azure.keyvault.v7_1.models.SecretAttributes
    """

    _validation = {
        'value': {'required': True},
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': 'str'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'content_type': {'key': 'contentType', 'type': 'str'},
        'secret_attributes': {'key': 'attributes', 'type': 'SecretAttributes'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SecretSetParameters, self).__init__(**kwargs)
        self.value = kwargs['value']
        self.tags = kwargs.get('tags', None)
        self.content_type = kwargs.get('content_type', None)
        self.secret_attributes = kwargs.get('secret_attributes', None)


class SecretUpdateParameters(msrest.serialization.Model):
    """The secret update parameters.

    :param content_type: Type of the secret value such as a password.
    :type content_type: str
    :param secret_attributes: The secret management attributes.
    :type secret_attributes: ~azure.keyvault.v7_1.models.SecretAttributes
    :param tags: A set of tags. Application specific metadata in the form of key-value pairs.
    :type tags: dict[str, str]
    """

    _attribute_map = {
        'content_type': {'key': 'contentType', 'type': 'str'},
        'secret_attributes': {'key': 'attributes', 'type': 'SecretAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(SecretUpdateParameters, self).__init__(**kwargs)
        self.content_type = kwargs.get('content_type', None)
        self.secret_attributes = kwargs.get('secret_attributes', None)
        self.tags = kwargs.get('tags', None)


class _CaseInsensitiveEnumMeta(EnumMeta):
    def __getitem__(self, name):
        return super().__getitem__(name.upper())

    def __getattr__(cls, name):
        """Return the enum member matching `name`
        We use __getattr__ instead of descriptors or inserting into the enum
        class' __dict__ in order to support `name` and `value` being both
        properties for enum members (which live in the class' __dict__) and
        enum members themselves.
        """
        try:
            return cls._member_map_[name.upper()]
        except KeyError:
            raise AttributeError(name)


class DeletionRecoveryLevel(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """Reflects the deletion recovery level currently in effect for secrets in the current vault. If
    it contains 'Purgeable', the secret can be permanently deleted by a privileged user; otherwise,
    only the system can purge the secret, at the end of the retention interval.
    """

    #: Denotes a vault state in which deletion is an irreversible operation, without the possibility
    #: for recovery. This level corresponds to no protection being available against a Delete
    #: operation; the data is irretrievably lost upon accepting a Delete operation at the entity level
    #: or higher (vault, resource group, subscription etc.).
    PURGEABLE = "Purgeable"
    #: Denotes a vault state in which deletion is recoverable, and which also permits immediate and
    #: permanent deletion (i.e. purge). This level guarantees the recoverability of the deleted entity
    #: during the retention interval (90 days), unless a Purge operation is requested, or the
    #: subscription is cancelled. System wil permanently delete it after 90 days, if not recovered.
    RECOVERABLE_PURGEABLE = "Recoverable+Purgeable"
    #: Denotes a vault state in which deletion is recoverable without the possibility for immediate
    #: and permanent deletion (i.e. purge). This level guarantees the recoverability of the deleted
    #: entity during the retention interval(90 days) and while the subscription is still available.
    #: System wil permanently delete it after 90 days, if not recovered.
    RECOVERABLE = "Recoverable"
    #: Denotes a vault and subscription state in which deletion is recoverable within retention
    #: interval (90 days), immediate and permanent deletion (i.e. purge) is not permitted, and in
    #: which the subscription itself  cannot be permanently canceled. System wil permanently delete it
    #: after 90 days, if not recovered.
    RECOVERABLE_PROTECTED_SUBSCRIPTION = "Recoverable+ProtectedSubscription"
    #: Denotes a vault state in which deletion is recoverable, and which also permits immediate and
    #: permanent deletion (i.e. purge when 7<= SoftDeleteRetentionInDays < 90). This level guarantees
    #: the recoverability of the deleted entity during the retention interval, unless a Purge
    #: operation is requested, or the subscription is cancelled.
    CUSTOMIZED_RECOVERABLE_PURGEABLE = "CustomizedRecoverable+Purgeable"
    #: Denotes a vault state in which deletion is recoverable without the possibility for immediate
    #: and permanent deletion (i.e. purge when 7<= SoftDeleteRetentionInDays < 90).This level
    #: guarantees the recoverability of the deleted entity during the retention interval and while the
    #: subscription is still available.
    CUSTOMIZED_RECOVERABLE = "CustomizedRecoverable"
    #: Denotes a vault and subscription state in which deletion is recoverable, immediate and
    #: permanent deletion (i.e. purge) is not permitted, and in which the subscription itself cannot
    #: be permanently canceled when 7<= SoftDeleteRetentionInDays < 90. This level guarantees the
    #: recoverability of the deleted entity during the retention interval, and also reflects the fact
    #: that the subscription itself cannot be cancelled.
    CUSTOMIZED_RECOVERABLE_PROTECTED_SUBSCRIPTION = "CustomizedRecoverable+ProtectedSubscription"
