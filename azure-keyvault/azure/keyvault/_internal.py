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