# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import base64
import json
from datetime import datetime
from msrest.serialization import TZ_UTC
import six

from azure.core.credentials import AccessToken
from ._datetime_utils import convert_datetime_to_utc_int


class CommunicationTokenRefreshOptions(object):
    """Options for refreshing CommunicationTokenCredential.

    :param token: The token used to authenticate to an Azure Communication service.
    :type token: str
    :param token_refresher: The token refresher to provide capacity to fetch fresh token.
    :raises: TypeError
    """

    def __init__(
        self,
        token,  # type: str
        token_refresher=None,
    ):
        # type: (...) -> None

        if not isinstance(token, six.string_types):
            raise TypeError("token must be a string.")
        self._token = token
        self._token_refresher = token_refresher

    def get_token(self):
        """Returns the serialized JWT token."""

        token_parse_err_msg = "Token is not formatted correctly"
        parts = self._token.split(".")

        if len(parts) < 3:
            raise ValueError(token_parse_err_msg)

        try:
            padded_base64_payload = base64.b64decode(parts[1] + "==").decode("ascii")
            payload = json.loads(padded_base64_payload)
            return AccessToken(
                self._token,
                convert_datetime_to_utc_int(
                    datetime.fromtimestamp(payload["exp"]).replace(tzinfo=TZ_UTC)
                ),
            )
        except ValueError:
            raise ValueError(token_parse_err_msg)

    def get_token_refresher(self):
        """Returns the token refresher to provide capacity to fetch fresh token."""
        return self._token_refresher
