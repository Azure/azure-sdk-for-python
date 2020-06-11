#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# pylint: disable=super-init-not-called,no-self-use

import datetime
import logging
import time

from uamqp import Session, c_uamqp, compat, constants, errors, utils
from uamqp.constants import TransportType

from .common import _SASL, AMQPAuth

_logger = logging.getLogger(__name__)


class TokenRetryPolicy(object):
    """Retry policy for sending authentication tokens
    for CBS authentication.

    :param retries: The number of retry attempts for a failed
     PUT token request. The default is 3. This is exclusive of
     the initial attempt.
    :type retries: int
    :param backoff: The time in miliseconds to wait between
     retry attempts.
    :type backoff: int
    """

    def __init__(self, retries=3, backoff=0):
        self.retries = retries
        self.backoff = float(backoff)/1000


class CBSAuthMixin(object):
    """Mixin to handle sending and refreshing CBS auth tokens."""

    def update_token(self):
        """Update a token that is about to expire. This is specific
        to a particular token type, and therefore must be implemented
        in a child class.
        """
        raise errors.TokenExpired(
            "Unable to refresh token - no refresh logic implemented.")

    def create_authenticator(self, connection, debug=False, **kwargs):
        """Create the AMQP session and the CBS channel with which
        to negotiate the token.

        :param connection: The underlying AMQP connection on which
         to create the session.
        :type connection: ~uamqp.connection.Connection
        :param debug: Whether to emit network trace logging events for the
         CBS session. Default is `False`. Logging events are set at INFO level.
        :type debug: bool
        :rtype: uamqp.c_uamqp.CBSTokenAuth
        """
        self._connection = connection
        self._session = Session(connection, **kwargs)

        if self.token_type == b'jwt':  # Initialize the jwt token
            self.update_token()

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
            self._session.destroy()
            raise errors.AMQPConnectionError(
                "Unable to open authentication session on connection {}.\n"
                "Please confirm target hostname exists: {}".format(connection.container_id, connection.hostname))
        return self._cbs_auth

    def close_authenticator(self):
        """Close the CBS auth channel and session."""
        _logger.info("Shutting down CBS session on connection: %r.", self._connection.container_id)
        try:
            _logger.debug("Unlocked CBS to close on connection: %r.", self._connection.container_id)
            self._cbs_auth.destroy()
            _logger.info("Auth closed, destroying session on connection: %r.", self._connection.container_id)
            self._session.destroy()
        finally:
            _logger.info("Finished shutting down CBS session on connection: %r.", self._connection.container_id)

    def handle_token(self):
        """This function is called periodically to check the status of the current
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
            self._connection.lock()
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
                time.sleep(self._retry_policy.backoff)
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
                self.update_token()
                self._cbs_auth.refresh(self.token, int(self.expires_at))
            elif auth_status == constants.CBSAuthStatus.Idle:
                self._cbs_auth.authenticate()
                in_progress = True
            elif auth_status != constants.CBSAuthStatus.Ok:
                raise errors.AuthenticationException("Invalid auth state.")
        except compat.TimeoutException:
            _logger.debug("CBS auth timed out while waiting for lock acquisition.")
            return None, None
        except ValueError as e:
            raise errors.AuthenticationException(
                "Token authentication failed: {}".format(e))
        finally:
            self._connection.release()
        return timeout, in_progress

    def _set_expiry(self, expires_at, expires_in):
        if not expires_at and not expires_in:
            raise ValueError("Must specify either 'expires_at' or 'expires_in'.")
        if not expires_at:
            expires_at = time.time() + expires_in.seconds
        else:
            expires_in_seconds = expires_at - time.time()
            if expires_in_seconds < 1:
                raise ValueError("Token has already expired.")
            expires_in = datetime.timedelta(seconds=expires_in_seconds)
        return expires_at, expires_in


class SASTokenAuth(AMQPAuth, CBSAuthMixin):
    """CBS authentication using SAS tokens.

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

    def __init__(self, audience, uri, token,
                 expires_in=None,
                 expires_at=None,
                 username=None,
                 password=None,
                 port=constants.DEFAULT_AMQPS_PORT,
                 timeout=10,
                 retry_policy=TokenRetryPolicy(),
                 verify=None,
                 token_type=b"servicebus.windows.net:sastoken",
                 http_proxy=None,
                 transport_type=TransportType.Amqp,
                 encoding='UTF-8'):  # pylint: disable=no-member
        self._retry_policy = retry_policy
        self._encoding = encoding
        self.uri = uri
        parsed = compat.urlparse(uri)  # pylint: disable=no-member

        self.cert_file = verify
        self.hostname = parsed.hostname.encode(self._encoding)
        self.username = compat.unquote_plus(parsed.username) if parsed.username else None  # pylint: disable=no-member
        self.password = compat.unquote_plus(parsed.password) if parsed.password else None  # pylint: disable=no-member

        self.username = username or self.username
        self.password = password or self.password
        self.audience = self._encode(audience)
        self.token_type = self._encode(token_type)
        self.token = self._encode(token)
        self.expires_at, self.expires_in = self._set_expiry(expires_at, expires_in)
        self.timeout = timeout
        self.retries = 0
        self.sasl = _SASL()
        self.set_io(self.hostname, port, http_proxy, transport_type)

    def update_token(self):
        """If a username and password are present - attempt to use them to
        request a fresh SAS token.
        """
        if not self.username or not self.password:
            raise errors.TokenExpired("Unable to refresh token - no username or password.")
        encoded_uri = compat.quote_plus(self.uri).encode(self._encoding)  # pylint: disable=no-member
        encoded_key = compat.quote_plus(self.username).encode(self._encoding)  # pylint: disable=no-member
        self.expires_at = time.time() + self.expires_in.seconds
        self.token = utils.create_sas_token(
            encoded_key,
            self.password.encode(self._encoding),
            encoded_uri,
            self.expires_in)

    @classmethod
    def from_shared_access_key(
            cls,
            uri,
            key_name,
            shared_access_key,
            expiry=None,
            port=constants.DEFAULT_AMQPS_PORT,
            timeout=10,
            retry_policy=TokenRetryPolicy(),
            verify=None,
            http_proxy=None,
            transport_type=TransportType.Amqp,
            encoding='UTF-8'):
        """Attempt to create a CBS token session using a Shared Access Key such
        as is used to connect to Azure services.

        :param uri: The AMQP endpoint URI. This must be provided as
         a decoded string.
        :type uri: str
        :param key_name: The SAS token username, also referred to as the key
         name or policy name.
        :type key_name: str
        :param shared_access_key: The SAS token password, also referred to as the key.
        :type shared_access_key: str
        :param expiry: The lifetime in seconds for the generated token. Default is 1 hour.
        :type expiry: int
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
        expires_in = datetime.timedelta(seconds=expiry or constants.AUTH_EXPIRATION_SECS)
        encoded_uri = compat.quote_plus(uri).encode(encoding)  # pylint: disable=no-member
        encoded_key = compat.quote_plus(key_name).encode(encoding)  # pylint: disable=no-member
        expires_at = time.time() + expires_in.seconds
        token = utils.create_sas_token(
            encoded_key,
            shared_access_key.encode(encoding),
            encoded_uri,
            expires_in)
        return cls(
            uri, uri, token,
            expires_in=expires_in,
            expires_at=expires_at,
            username=key_name,
            password=shared_access_key,
            port=port,
            timeout=timeout,
            retry_policy=retry_policy,
            verify=verify,
            http_proxy=http_proxy,
            transport_type=transport_type,
            encoding=encoding)


class JWTTokenAuth(AMQPAuth, CBSAuthMixin):
    """CBS authentication using JWT tokens.

    :param audience: The token audience field. For JWT tokens
     this is usually the URI.
    :type audience: str or bytes
    :param uri: The AMQP endpoint URI. This must be provided as
     a decoded string.
    :type uri: str
    :param get_token: The callback function used for getting and refreshing
     tokens. It should return a valid jwt token each time it is called.
    :type get_token: callable object
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

        if not get_token or not callable(get_token):
            raise ValueError("get_token must be a callable object.")

        self.get_token = get_token
        self.audience = self._encode(audience)
        self.token_type = self._encode(token_type)
        self.token = None
        self.expires_at, self.expires_in = self._set_expiry(expires_at, expires_in)
        self.timeout = timeout
        self.retries = 0
        self.sasl = _SASL()
        self.set_io(self.hostname, port, http_proxy, transport_type)

    def update_token(self):
        access_token = self.get_token()
        self.expires_at = access_token.expires_on
        self.token = self._encode(access_token.token)
