# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import ( # pylint: disable=unused-import
    cast,
    Tuple,
)
import six
from .utils import create_access_token

class CommunicationTokenRefreshOptions(object):
    """Options for refreshing CommunicationTokenCredential.
    :param str token: The token used to authenticate to an Azure Communication service
    :param token_refresher: The token refresher to provide capacity to fetch fresh token
    :raises: TypeError
    """

    def __init__(self,
        token, # type: str
        token_refresher=None
    ):
        # type: (...) -> None
        if not isinstance(token, six.string_types):
            raise TypeError("token must be a string.")
        self._token = token
        self._token_refresher = token_refresher

    def get_token(self):
        """Return the the serialized JWT token."""
        return create_access_token(self._token)

    def get_token_refresher(self):
        """Return the token refresher to provide capacity to fetch fresh token."""
        return self._token_refresher
