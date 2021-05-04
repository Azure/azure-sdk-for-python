# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials import TokenCredential
    from azure.core.credentials import AccessToken

class StaticAccessTokenCredential(object):
    """ Represents a static access token credential.
    This implements the TokenCredential protocol.

    :param AccessToken access_token: An access token.
    """

    def __init__(self, access_token):
        # type: (AccessToken) -> None
        self._access_token = access_token

    def get_token(self, *scopes, **kwargs): #pylint: disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        return self._access_token
