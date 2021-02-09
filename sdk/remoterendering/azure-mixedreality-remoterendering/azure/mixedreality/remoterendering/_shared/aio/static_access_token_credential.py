# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.credentials import AccessToken

class StaticAccessTokenCredential(object):
    """ Represents a static access token credential.
    This implements the AsyncTokenCredential protocol.

    :param AccessToken access_token: An access token.
    """

    def __init__(self, access_token: "AccessToken"):
        self._access_token = access_token

    async def get_token(
        self,
        #pylint: disable=unused-argument
        *scopes: str,
        **kwargs: "Any") -> "AccessToken":
        return self._access_token

    async def close(self) -> None:
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass
