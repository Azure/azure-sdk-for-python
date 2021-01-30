# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials import TokenCredential

from azure.core.credentials import AccessToken

class StaticAccessTokenCredential(object):
    """ Represents a static access token credential.
    This implements the TokenCredential protocol.

    :param str account_id: The Mixed Reality service account identifier.
    :param str endpoint_url: The Mixed Reality STS service endpoint.
    :param TokenCredential credential: The credential used to access the Mixed Reality service.
    """

    def __init__(self, access_token):
        # type: (AccessToken) -> None
        self._access_token = access_token

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        return self._access_token
