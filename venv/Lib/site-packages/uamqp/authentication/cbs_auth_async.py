#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# pylint: disable=super-init-not-called,no-self-use

import asyncio
import datetime
import logging

from uamqp import c_uamqp, compat, constants, errors
from uamqp.utils import get_running_loop
from uamqp.async_ops import SessionAsync
from uamqp.constants import TransportType

from .cbs_auth import CBSAuthMixin, SASTokenAuth, JWTTokenAuth, TokenRetryPolicy

from .common import _SASL


_logger = logging.getLogger(__name__)


def is_coroutine(get_token):
    try:
        if asyncio.iscoroutinefunction(get_token.func):
            return True
    except AttributeError:
        if asyncio.iscoroutinefunction(get_token):
            return True
    raise ValueError("get_token must be a coroutine function")


class CBSAsyncAuthMixin(CBSAuthMixin):
    """Mixin to handle sending and refreshing CBS auth tokens asynchronously."""

    async def create_authenticator_async(self, connection, debug=False, loop=None, **kwargs):
        """Create the async AMQP session and the CBS channel with which
        to negotiate the token.

        :param connection: The underlying AMQP connection on which
         to create the session.
        :type connection: ~uamqp.async_ops.connection_async.ConnectionAsync
        :param debug: Whether to emit network trace logging events for the
         CBS session. Default is `False`. Logging events are set at INFO level.
        :type debug: bool
        :param loop: A user specified event loop.
        :type loop: ~asycnio.AbstractEventLoop
        :rtype: uamqp.c_uamqp.CBSTokenAuth
        """
        self.loop = loop or get_running_loop()
        self._connection = connection
        self._session = SessionAsync(connection, loop=self.loop, **kwargs)

        if self.token_type == b'jwt':  # Async initialize the jwt token
            await self.update_token()

        try:
            self._cbs_auth = c_uamqp.CBSTokenAuth(
                self.audience,
                self.token_type,
                self.token,
                int(self.expires_at),
                self._session._session,  # pylint: disable=protected-access
                self.timeout,
                self._connection.container_id)
            self._cbs_auth.set_trace(debug)
        except ValueError:
            await self._session.destroy_async()
            raise errors.AMQPConnectionError(
                "Unable to open authentication session on connection {}.\n"
                "Please confirm target hostname exists: {}".format(
                    connection.container_id, connection.hostname)) from None
        return self._cbs_auth

    async def close_authenticator_async(self):
        """Close the CBS auth channel and session asynchronously."""
        _logger.info("Shutting down CBS session on connection: %r.", self._connection.container_id)
        try:
            self._cbs_auth.destroy()
            _logger.info("Auth closed, destroying session on connection: %r.", self._connection.container_id)
            await self._session.destroy_async()
        finally:
            _logger.info("Finished shutting down CBS session on connection: %r.", self._connection.container_id)

    async def handle_token_async(self):
        """This coroutine is called periodically to check the status of the current
        token if there is one, and request a new one if needed.
        If the token request fails, it will be retried according to the retry policy.
        A token refresh will be attempted if the token will expire soon.

        This function will return a tuple of two booleans. The first represents whether
        the token authentication has not completed within it's given timeout window. The
        second indicates whether the token negotiation is still in progress.

        :raises: ~uamqp.errors.AuthenticationException if the token authentication fails.
        :raises: ~uamqp.errors.TokenExpired if the token has expired and cannot be
         refreshed.
        :rtype: tuple[bool, bool]
        """
        # pylint: disable=protected-access
        timeout = False
        in_progress = False
        try:
            await self._connection.lock_async()
            if self._connection._closing or self._connection._error:
                return timeout, in_progress
            auth_status = self._cbs_auth.get_status()
            auth_status = constants.CBSAuthStatus(auth_status)
            if auth_status == constants.CBSAuthStatus.Error:
                if self.retries >= self._retry_policy.retries:  # pylint: disable=no-member
                    _logger.warning("Authentication Put-Token failed. Retries exhausted.")
                    raise errors.TokenAuthFailure(*self._cbs_auth.get_failure_info())
                error_code, error_description = self._cbs_auth.get_failure_info()
                _logger.info("Authentication status: %r, description: %r", error_code, error_description)
                _logger.info("Authentication Put-Token failed. Retrying.")
                self.retries += 1  # pylint: disable=no-member
                await asyncio.sleep(self._retry_policy.backoff, loop=self.loop)
                self._cbs_auth.authenticate()
                in_progress = True
            elif auth_status == constants.CBSAuthStatus.Failure:
                raise errors.AuthenticationException("Failed to open CBS authentication link.")
            elif auth_status == constants.CBSAuthStatus.Expired:
                raise errors.TokenExpired("CBS Authentication Expired.")
            elif auth_status == constants.CBSAuthStatus.Timeout:
                timeout = True
            elif auth_status == constants.CBSAuthStatus.InProgress:
                in_progress = True
            elif auth_status == constants.CBSAuthStatus.RefreshRequired:
                _logger.info("Token on connection %r will expire soon - attempting to refresh.",
                             self._connection.container_id)
                await self.update_token()
                self._cbs_auth.refresh(self.token, int(self.expires_at))
            elif auth_status == constants.CBSAuthStatus.Idle:
                self._cbs_auth.authenticate()
                in_progress = True
            elif auth_status != constants.CBSAuthStatus.Ok:
                raise ValueError("Invalid auth state.")
        except asyncio.TimeoutError:
            _logger.debug("CBS auth timed out while waiting for lock acquisition.")
            return None, None
        except ValueError as e:
            raise errors.AuthenticationException(
                "Token authentication failed: {}".format(e))
        finally:
            self._connection.release_async()
        return timeout, in_progress


class SASTokenAsync(SASTokenAuth, CBSAsyncAuthMixin):
    """Asynchronous CBS authentication using SAS tokens.

    :param audience: The token audience field. For SAS tokens
     this is usually the URI.
    :type audience: str or bytes
    :param uri: The AMQP endpoint URI. This must be provided as
     a decoded string.
    :type uri: str
    :param token: The SAS token.
    :type token: str or bytes.
    :param expires_in: The total remaining seconds until the token
     expires.
    :type expires_in: ~datetime.timedelta
    :param expires_at: The timestamp at which the SAS token will expire
     formatted as seconds since epoch.
    :type expires_at: float
    :param username: The SAS token username, also referred to as the key
     name or policy name. This can optionally be encoded into the URI.
    :type username: str
    :param password: The SAS token password, also referred to as the key.
     This can optionally be encoded into the URI.
    :type password: str
    :param port: The TLS port - default for AMQP is 5671.
    :type port: int
    :param timeout: The timeout in seconds in which to negotiate the token.
     The default value is 10 seconds.
    :type timeout: float
    :param retry_policy: The retry policy for the PUT token request. The default
     retry policy has 3 retries.
    :type retry_policy: ~uamqp.authentication.cbs_auth.TokenRetryPolicy
    :param verify: The path to a user-defined certificate.
    :type verify: str
    :param token_type: The type field of the token request.
     Default value is `b"servicebus.windows.net:sastoken"`.
    :type token_type: bytes
    :param http_proxy: HTTP proxy configuration. This should be a dictionary with
     the following keys present: 'proxy_hostname' and 'proxy_port'. Additional optional
     keys are 'username' and 'password'.
    :type http_proxy: dict
    :param transport_type: The transport protocol type - default is ~uamqp.TransportType.Amqp.
     ~uamqp.TransportType.AmqpOverWebsocket is applied when http_proxy is set or the
     transport type is explicitly requested.
    :type transport_type: ~uamqp.TransportType
    :param encoding: The encoding to use if hostname is provided as a str.
     Default is 'UTF-8'.
    :type encoding: str
    """
    async def update_token(self):  # pylint: disable=useless-super-delegation
        super(SASTokenAsync, self).update_token()


class JWTTokenAsync(JWTTokenAuth, CBSAsyncAuthMixin):
    """CBS authentication using JWT tokens.

    :param audience: The token audience field. For JWT tokens
     this is usually the URI.
    :type audience: str or bytes
    :param uri: The AMQP endpoint URI. This must be provided as
     a decoded string.
    :type uri: str
    :param get_token: The callback function used for getting and refreshing
     tokens. It should return a valid jwt token each time it is called.
    :type get_token: coroutine function
    :param expires_in: The total remaining seconds until the token
     expires - default for JWT token generated by AAD is 3600s (1 hour).
    :type expires_in: ~datetime.timedelta
    :param expires_at: The timestamp at which the JWT token will expire
     formatted as seconds since epoch.
    :type expires_at: float
    :param port: The TLS port - default for AMQP is 5671.
    :type port: int
    :param timeout: The timeout in seconds in which to negotiate the token.
     The default value is 10 seconds.
    :type timeout: float
    :param retry_policy: The retry policy for the PUT token request. The default
     retry policy has 3 retries.
    :type retry_policy: ~uamqp.authentication.cbs_auth.TokenRetryPolicy
    :param verify: The path to a user-defined certificate.
    :type verify: str
    :param token_type: The type field of the token request.
     Default value is `b"jwt"`.
    :type token_type: bytes
    :param http_proxy: HTTP proxy configuration. This should be a dictionary with
     the following keys present: 'proxy_hostname' and 'proxy_port'. Additional optional
     keys are 'username' and 'password'.
    :type http_proxy: dict
    :param transport_type: The transport protocol type - default is ~uamqp.TransportType.Amqp.
     ~uamqp.TransportType.AmqpOverWebsocket is applied when http_proxy is set or the
     transport type is explicitly requested.
    :type transport_type: ~uamqp.TransportType
    :param encoding: The encoding to use if hostname is provided as a str.
     Default is 'UTF-8'.
    :type encoding: str
    """

    def __init__(self, audience, uri,
                 get_token,
                 expires_in=datetime.timedelta(seconds=constants.AUTH_EXPIRATION_SECS),
                 expires_at=None,
                 port=constants.DEFAULT_AMQPS_PORT,
                 timeout=10,
                 retry_policy=TokenRetryPolicy(),
                 verify=None,
                 token_type=b"jwt",
                 http_proxy=None,
                 transport_type=TransportType.Amqp,
                 encoding='UTF-8'):  # pylint: disable=no-member
        self._retry_policy = retry_policy
        self._encoding = encoding
        self.uri = uri
        parsed = compat.urlparse(uri)  # pylint: disable=no-member

        self.cert_file = verify
        self.hostname = parsed.hostname.encode(self._encoding)

        is_coroutine(get_token)

        self.get_token = get_token
        self.audience = self._encode(audience)
        self.token_type = self._encode(token_type)
        self.token = None
        self.expires_at, self.expires_in = self._set_expiry(expires_at, expires_in)
        self.timeout = timeout
        self.retries = 0
        self.sasl = _SASL()
        self.set_io(self.hostname, port, http_proxy, transport_type)

    async def update_token(self):
        access_token = await self.get_token()
        self.expires_at = access_token.expires_on
        self.token = self._encode(access_token.token)
