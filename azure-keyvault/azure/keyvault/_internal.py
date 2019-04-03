# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from msrest.serialization import Model

try:
    import urllib.parse as parse
except ImportError:
    import urlparse as parse  # pylint: disable=import-error

from collections import namedtuple


_VaultId = namedtuple('VaultId', ['vault_url', 'collection', 'name', 'version'])


def _parse_vault_id(url):
    try:
        parsed_uri = parse.urlparse(url)
    except Exception: # pylint: disable=broad-except
        raise ValueError("'{}' is not not a valid url".format(url))
    if not (parsed_uri.scheme and parsed_uri.hostname):
        raise ValueError("'{}' is not not a valid url".format(url))

    path = list(filter(None, parsed_uri.path.split('/')))

    if len(path) < 2 or len(path) > 3:
        raise ValueError("'{}' is not not a valid vault url".format(url))

    return _VaultId(vault_url='{}://{}'.format(parsed_uri.scheme, parsed_uri.hostname),
                    collection=path[0],
                    name=path[1],
                    version=path[2] if len(path) == 3 else None)


class _BackupResult(Model):
    """The backup secret result, containing the backup blob.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :ivar value: The backup blob containing the backed up secret.
    :vartype value: bytes
    """

    _validation = {
    }

    _attribute_map = {
        'value': {'key': 'value', 'type': 'base64'},
    }

    def __init__(self, **kwargs):
        super(_BackupResult, self).__init__(**kwargs)
        self.value = None


class _SecretManagementAttributes(Model):
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

    _validation = {"created": {"readonly": True}, "updated": {"readonly": True}, "recovery_level": {"readonly": True}}

    _attribute_map = {
        "enabled": {"key": "enabled", "type": "bool"},
        "not_before": {"key": "nbf", "type": "unix-time"},
        "expires": {"key": "exp", "type": "unix-time"},
        "created": {"key": "created", "type": "unix-time"},
        "updated": {"key": "updated", "type": "unix-time"},
        "recovery_level": {"key": "recoveryLevel", "type": "str"},
    }

    def __init__(self, **kwargs):
        # type: (Mapping[str, Any]) -> None
        super(_SecretManagementAttributes, self).__init__(**kwargs)
        self.enabled = kwargs.get("enabled", None)
        self.not_before = kwargs.get("not_before", None)
        self.expires = kwargs.get("expires", None)
        # self.created = None
        # self.updated = None
        # self.recovery_level = None
