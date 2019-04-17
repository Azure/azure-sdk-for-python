# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.pipeline.policies import HTTPPolicy

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


# TODO: integrate with azure.core
class _BearerTokenCredentialPolicy(HTTPPolicy):
    def __init__(self, credentials):
        self._credentials = credentials

    def send(self, request, **kwargs):
        auth_header = 'Bearer ' + self._credentials.token['access_token']
        request.http_request.headers['Authorization'] = auth_header

        return self.next.send(request, **kwargs)