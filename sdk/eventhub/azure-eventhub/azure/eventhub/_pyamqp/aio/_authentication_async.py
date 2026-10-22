# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from functools import partial
import time
from typing import Awaitable, Callable, Optional, Tuple, Union, Any

from ..sasl import SASLAnonymousCredential

from ..authentication import _generate_sas_access_token, AccessToken
from ..constants import AUTH_DEFAULT_EXPIRATION_SECONDS, AUTH_TYPE_CBS, TOKEN_TYPE_JWT, TOKEN_TYPE_SASTOKEN


async def _generate_sas_token_async(
    auth_uri: str, sas_name: str, sas_key: str, expiry_in: float = AUTH_DEFAULT_EXPIRATION_SECONDS
) -> AccessToken:
    return _generate_sas_access_token(auth_uri, sas_name, sas_key, expiry_in=expiry_in)


class _CBSAuthAsync:
    # TODO:
    #  1. naming decision, suffix with Auth vs Credential
    auth_type = AUTH_TYPE_CBS

    def __init__(  # pylint: disable=unused-argument
        self,
        uri: str,
        audience: str,
        token_type: Union[str, bytes],
        get_token: Callable[[], Awaitable[AccessToken]],
        *,
        expires_in: Optional[float] = AUTH_DEFAULT_EXPIRATION_SECONDS,
        expires_on: Optional[float] = None,
        **kwargs: Any
    ):
        """
        CBS authentication using JWT tokens.

        :param uri: The AMQP endpoint URI. This must be provided as
         a decoded string.
        :type uri: str
        :param audience: The token audience field. For SAS tokens
         this is usually the URI.
        :type audience: str
        :param get_token: The callback function used for getting and refreshing
         tokens. It should return a valid jwt token each time it is called.
        :type get_token: callable object
        :param token_type: The type field of the token request.
         Default value is `"jwt"`.
        :type token_type: str

        """
        self.sasl = SASLAnonymousCredential()
        self.uri = uri
        self.audience = audience
        self.token_type = token_type
        self.get_token = get_token
        self.expires_in = expires_in
        self.expires_on = expires_on

    @staticmethod
    def _set_expiry(expires_in: Optional[float] = None, expires_on: Optional[float] = None) -> Tuple[float, float]:
        if not expires_on and not expires_in:
            raise ValueError("Must specify either 'expires_on' or 'expires_in'.")

        expires_in_interval: float = 0 if expires_in is None else expires_in
        expires_on_time: float = 0 if expires_on is None else expires_on

        if not expires_on and expires_in:
            expires_on_time = time.time() + expires_in
        elif expires_on and not expires_in:
            expires_in_interval = expires_on - time.time()
            if expires_in_interval < 1:
                raise ValueError("Token has already expired.")

        return expires_in_interval, expires_on_time


class JWTTokenAuthAsync(_CBSAuthAsync):
    # TODO:
    #  1. naming decision, suffix with Auth vs Credential
    def __init__(
        self,
        uri: str,
        audience: str,
        get_token: Callable[[], Awaitable[AccessToken]],
        *,
        token_type: Union[str, bytes] = TOKEN_TYPE_JWT,
        **kwargs: Any
    ):
        """
        CBS authentication using JWT tokens.

        :param uri: The AMQP endpoint URI. This must be provided as
         a decoded string.
        :type uri: str
        :param audience: The token audience field. For SAS tokens
         this is usually the URI.
        :type audience: str
        :param get_token: The callback function used for getting and refreshing
         tokens. It should return a valid jwt token each time it is called.
        :type get_token: callable object
        :param token_type: The type field of the token request.
         Default value is `"jwt"`.
        :type token_type: str or bytes

        """
        super().__init__(uri, audience, token_type, get_token)
        self.get_token = get_token


class SASTokenAuthAsync(_CBSAuthAsync):
    # TODO:
    #  1. naming decision, suffix with Auth vs Credential
    def __init__(
        self,
        uri: str,
        audience: str,
        username: str,
        password: str,
        *,
        expires_in: Optional[float] = AUTH_DEFAULT_EXPIRATION_SECONDS,
        expires_on: Optional[float] = None,
        token_type: Union[str, bytes] = TOKEN_TYPE_SASTOKEN,
        **kwargs: Any
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
        self.username = username
        self.password = password
        expires_in, expires_on = self._set_expiry(expires_in, expires_on)
        self.get_token = partial(_generate_sas_token_async, uri, username, password, expires_in)
        super().__init__(uri, audience, token_type, self.get_token, expires_in=expires_in, expires_on=expires_on)
