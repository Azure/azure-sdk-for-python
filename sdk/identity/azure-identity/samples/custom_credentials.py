# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Demonstrates custom credential implementation"""

from typing import TYPE_CHECKING

from azure.core.credentials import AccessToken

if TYPE_CHECKING:
    from typing import Any, Union


class StaticTokenCredential(object):
    """Authenticates with a previously acquired access token

    Note that an access token is valid only for certain resources and eventually expires. This credential is therefore
    quite limited. An application using it must ensure the token is valid and contains all claims required by any
    service client given an instance of this credential.
    """
    def __init__(self, access_token):
        # type: (Union[str, AccessToken]) -> None
        if isinstance(access_token, AccessToken):
            self._token = access_token
        else:
            # setting expires_on in the past causes Azure SDK clients to call get_token every time they need a token
            self._token = AccessToken(token=access_token, expires_on=0)

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """get_token is the only method a credential must implement"""

        return self._token
