# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

try:
    import urllib.parse as parse
except ImportError:
    import urlparse as parse  # pylint: disable=import-error

from collections import namedtuple


VaultId = namedtuple('VaultId', ['vault_url', 'collection', 'name', 'version'])


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

    return VaultId(vault_url='{}://{}'.format(parsed_uri.scheme, parsed_uri.hostname),
                   collection=path[0],
                   name=path[1],
                   version=path[2] if len(path) == 3 else None)