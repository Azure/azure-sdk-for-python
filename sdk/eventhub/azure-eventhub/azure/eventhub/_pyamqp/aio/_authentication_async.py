#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#-------------------------------------------------------------------------
from functools import partial

from ..authentication import (
    _generate_sas_access_token,
    SASTokenAuth,
    JWTTokenAuth
)
from ..constants import AUTH_DEFAULT_EXPIRATION_SECONDS

try:
    from urlparse import urlparse
    from urllib import quote_plus  # type: ignore
except ImportError:
    from urllib.parse import urlparse, quote_plus


async def _generate_sas_token_async(auth_uri, sas_name, sas_key, expiry_in=AUTH_DEFAULT_EXPIRATION_SECONDS):
    return _generate_sas_access_token(auth_uri, sas_name, sas_key, expiry_in=expiry_in)


class JWTTokenAuthAsync(JWTTokenAuth):
    """"""
    # TODO:
    #  1. naming decision, suffix with Auth vs Credential


class SASTokenAuthAsync(SASTokenAuth):
    # TODO:
    #  1. naming decision, suffix with Auth vs Credential
    def __init__(
        self,
        uri,
        audience,
        username,
        password,
        **kwargs
    ):
        """
        CBS authentication using SAS tokens.

        :param uri: The AMQP endpoint URI. This must be provided as
         a decoded string.
        :type uri: str
        :param audience: The token audience field. For SAS tokens
         this is usually the URI.
        :type audience: str
        :param username: The SAS token username, also referred to as the key
         name or policy name. This can optionally be encoded into the URI.
        :type username: str
        :param password: The SAS token password, also referred to as the key.
         This can optionally be encoded into the URI.
        :type password: str
        :param expires_in: The total remaining seconds until the token
         expires.
        :type expires_in: int
        :param expires_on: The timestamp at which the SAS token will expire
         formatted as seconds since epoch.
        :type expires_on: float
        :param token_type: The type field of the token request.
         Default value is `"servicebus.windows.net:sastoken"`.
        :type token_type: str

        """
        super(SASTokenAuthAsync, self).__init__(
            uri,
            audience,
            username,
            password,
            **kwargs
        )
        self.get_token = partial(_generate_sas_token_async, uri, username, password, self.expires_in)
