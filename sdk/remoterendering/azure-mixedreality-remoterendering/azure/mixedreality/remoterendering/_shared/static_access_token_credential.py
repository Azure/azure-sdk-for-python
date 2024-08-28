# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.credentials import AccessToken

class StaticAccessTokenCredential(object):
    """ Represents a static access token credential.
    This implements the TokenCredential protocol.

    :param AccessToken access_token: An access token.
    """

    def __init__(self, access_token: AccessToken) -> None:
        self._access_token = access_token

    def get_token(self, *scopes: str, **kwargs) -> AccessToken: #pylint: disable=unused-argument
        return self._access_token
