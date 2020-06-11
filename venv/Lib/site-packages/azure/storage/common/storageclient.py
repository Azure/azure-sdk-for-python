# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import requests
from abc import ABCMeta
import logging
from time import sleep
import sys

from azure.common import (
    AzureException,
    AzureHttpError,
)

from ._constants import (
    DEFAULT_SOCKET_TIMEOUT,
    DEFAULT_X_MS_VERSION,
    DEFAULT_USER_AGENT_STRING,
    USER_AGENT_STRING_PREFIX,
    USER_AGENT_STRING_SUFFIX,
    _AUTHORIZATION_HEADER_NAME,
    _REDACTED_VALUE,
    _COPY_SOURCE_HEADER_NAME,
)
from ._error import (
    _ERROR_DECRYPTION_FAILURE,
    _http_error_handler,
    _wrap_exception,
    AzureSigningError,
)
from ._http import HTTPError
from ._http.httpclient import _HTTPClient
from ._serialization import (
    _update_request,
    _add_date_header,
)
from .models import (
    RetryContext,
    LocationMode,
    _OperationContext,
)
from .retry import ExponentialRetry
from io import UnsupportedOperation
from .sharedaccesssignature import _QueryStringConstants

if sys.version_info >= (3,):
    from urllib.parse import (
        urlparse,
        parse_qsl,
        urlunparse,
        urlencode,
    )
else:
    from urlparse import (
        urlparse,
        parse_qsl,
        urlunparse,
    )
    from urllib import urlencode
logger = logging.getLogger(__name__)


class StorageClient(object):
    '''
    This is the base class for service objects. Service objects are used to do 
    all requests to Storage. This class cannot be instantiated directly.

    :ivar str account_name:
        The storage account name. This is used to authenticate requests 
        signed with an account key and to construct the storage endpoint. It 
        is required unless a connection string is given, or if a custom 
        domain is used with anonymous authentication.
    :ivar str account_key:
        The storage account key. This is used for shared key authentication. 
        If neither account key or sas token is specified, anonymous access 
        will be used.
    :ivar str sas_token:
        A shared access signature token to use to authenticate requests 
        instead of the account key. If account key and sas token are both 
        specified, account key will be used to sign. If neither are 
        specified, anonymous access will be used.
    :ivar str primary_endpoint:
        The endpoint to send storage requests to.
    :ivar str secondary_endpoint:
        The secondary endpoint to read storage data from. This will only be a 
        valid endpoint if the storage account used is RA-GRS and thus allows 
        reading from secondary.
    :ivar function(context) retry:
        A function which determines whether to retry. Takes as a parameter a 
        :class:`~azure.storage.common.models.RetryContext` object. Returns the number
        of seconds to wait before retrying the request, or None to indicate not 
        to retry.
    :ivar ~azure.storage.common.models.LocationMode location_mode:
        The host location to use to make requests. Defaults to LocationMode.PRIMARY.
        Note that this setting only applies to RA-GRS accounts as other account 
        types do not allow reading from secondary. If the location_mode is set to 
        LocationMode.SECONDARY, read requests will be sent to the secondary endpoint. 
        Write requests will continue to be sent to primary.
    :ivar str protocol:
        The protocol to use for requests. Defaults to https.
    :ivar requests.Session request_session:
        The session object to use for http requests.
    :ivar function(request) request_callback:
        A function called immediately before each request is sent. This function 
        takes as a parameter the request object and returns nothing. It may be 
        used to added custom headers or log request data.
    :ivar function() response_callback:
        A function called immediately after each response is received. This 
        function takes as a parameter the response object and returns nothing. 
        It may be used to log response data.
    :ivar function() retry_callback:
        A function called immediately after retry evaluation is performed. This 
        function takes as a parameter the retry context object and returns nothing. 
        It may be used to detect retries and log context information.
    '''

    __metaclass__ = ABCMeta

    def __init__(self, connection_params):
        '''
        :param obj connection_params: The parameters to use to construct the client.
        '''
        self.account_name = connection_params.account_name
        self.account_key = connection_params.account_key
        self.sas_token = connection_params.sas_token
        self.token_credential = connection_params.token_credential
        self.is_emulated = connection_params.is_emulated

        self.primary_endpoint = connection_params.primary_endpoint
        self.secondary_endpoint = connection_params.secondary_endpoint

        protocol = connection_params.protocol
        request_session = connection_params.request_session or requests.Session()
        socket_timeout = connection_params.socket_timeout or DEFAULT_SOCKET_TIMEOUT
        self._httpclient = _HTTPClient(
            protocol=protocol,
            session=request_session,
            timeout=socket_timeout,
        )

        self.retry = ExponentialRetry().retry
        self.location_mode = LocationMode.PRIMARY

        self.request_callback = None
        self.response_callback = None
        self.retry_callback = None
        self._X_MS_VERSION = DEFAULT_X_MS_VERSION
        self._USER_AGENT_STRING = DEFAULT_USER_AGENT_STRING

    def _update_user_agent_string(self, service_package_version):
        self._USER_AGENT_STRING = '{}{} {}'.format(USER_AGENT_STRING_PREFIX,
                                                   service_package_version,
                                                   USER_AGENT_STRING_SUFFIX)

    @property
    def socket_timeout(self):
        return self._httpclient.timeout

    @socket_timeout.setter
    def socket_timeout(self, value):
        self._httpclient.timeout = value

    @property
    def protocol(self):
        return self._httpclient.protocol

    @protocol.setter
    def protocol(self, value):
        self._httpclient.protocol = value

    @property
    def request_session(self):
        return self._httpclient.session

    @request_session.setter
    def request_session(self, value):
        self._httpclient.session = value

    def set_proxy(self, host, port, user=None, password=None):
        '''
        Sets the proxy server host and port for the HTTP CONNECT Tunnelling.

        :param str host: Address of the proxy. Ex: '192.168.0.100'
        :param int port: Port of the proxy. Ex: 6000
        :param str user: User for proxy authorization.
        :param str password: Password for proxy authorization.
        '''
        self._httpclient.set_proxy(host, port, user, password)

    def _get_host_locations(self, primary=True, secondary=False):
        locations = {}
        if primary:
            locations[LocationMode.PRIMARY] = self.primary_endpoint
        if secondary:
            locations[LocationMode.SECONDARY] = self.secondary_endpoint
        return locations

    def _apply_host(self, request, operation_context, retry_context):
        if operation_context.location_lock and operation_context.host_location:
            # If this is a location locked operation and the location is set, 
            # override the request location and host_location.
            request.host_locations = operation_context.host_location
            request.host = list(operation_context.host_location.values())[0]
            retry_context.location_mode = list(operation_context.host_location.keys())[0]
        elif len(request.host_locations) == 1:
            # If only one location is allowed, use that location.
            request.host = list(request.host_locations.values())[0]
            retry_context.location_mode = list(request.host_locations.keys())[0]
        else:
            # If multiple locations are possible, choose based on the location mode.
            request.host = request.host_locations.get(self.location_mode)
            retry_context.location_mode = self.location_mode

    @staticmethod
    def extract_date_and_request_id(retry_context):
        if getattr(retry_context, 'response', None) is None:
            return ""
        resp = retry_context.response

        if 'date' in resp.headers and 'x-ms-request-id' in resp.headers:
            return str.format("Server-Timestamp={0}, Server-Request-ID={1}",
                              resp.headers['date'], resp.headers['x-ms-request-id'])
        elif 'date' in resp.headers:
            return str.format("Server-Timestamp={0}", resp.headers['date'])
        elif 'x-ms-request-id' in resp.headers:
            return str.format("Server-Request-ID={0}", resp.headers['x-ms-request-id'])
        else:
            return ""

    @staticmethod
    def _scrub_headers(headers):
        # make a copy to avoid contaminating the request
        clean_headers = headers.copy()

        if _AUTHORIZATION_HEADER_NAME in clean_headers:
            clean_headers[_AUTHORIZATION_HEADER_NAME] = _REDACTED_VALUE

        # in case of copy operations, there could be a SAS signature present in the header value
        if _COPY_SOURCE_HEADER_NAME in clean_headers \
                and _QueryStringConstants.SIGNED_SIGNATURE + "=" in clean_headers[_COPY_SOURCE_HEADER_NAME]:
            # take the url apart and scrub away the signed signature
            scheme, netloc, path, params, query, fragment = urlparse(clean_headers[_COPY_SOURCE_HEADER_NAME])
            parsed_qs = dict(parse_qsl(query))
            parsed_qs[_QueryStringConstants.SIGNED_SIGNATURE] = _REDACTED_VALUE

            # the SAS needs to be put back together
            clean_headers[_COPY_SOURCE_HEADER_NAME] = urlunparse(
                (scheme, netloc, path, params, urlencode(parsed_qs), fragment))
        return clean_headers

    @staticmethod
    def _scrub_query_parameters(query):
        # make a copy to avoid contaminating the request
        clean_queries = query.copy()

        if _QueryStringConstants.SIGNED_SIGNATURE in clean_queries:
            clean_queries[_QueryStringConstants.SIGNED_SIGNATURE] = _REDACTED_VALUE
        return clean_queries

    def _perform_request(self, request, parser=None, parser_args=None, operation_context=None, expected_errors=None):
        '''
        Sends the request and return response. Catches HTTPError and hands it
        to error handler
        '''
        operation_context = operation_context or _OperationContext()
        retry_context = RetryContext()
        retry_context.is_emulated = self.is_emulated

        # if request body is a stream, we need to remember its current position in case retries happen
        if hasattr(request.body, 'read'):
            try:
                retry_context.body_position = request.body.tell()
            except (AttributeError, UnsupportedOperation):
                # if body position cannot be obtained, then retries will not work
                pass

        # Apply the appropriate host based on the location mode
        self._apply_host(request, operation_context, retry_context)

        # Apply common settings to the request
        _update_request(request, self._X_MS_VERSION, self._USER_AGENT_STRING)
        client_request_id_prefix = str.format("Client-Request-ID={0}", request.headers['x-ms-client-request-id'])

        while True:
            try:
                try:
                    # Execute the request callback 
                    if self.request_callback:
                        self.request_callback(request)

                    # Add date and auth after the callback so date doesn't get too old and 
                    # authentication is still correct if signed headers are added in the request 
                    # callback. This also ensures retry policies with long back offs 
                    # will work as it resets the time sensitive headers.
                    _add_date_header(request)

                    try:
                        # request can be signed individually
                        self.authentication.sign_request(request)
                    except AttributeError:
                        # session can also be signed
                        self.request_session = self.authentication.signed_session(self.request_session)

                    # Set the request context
                    retry_context.request = request

                    # Log the request before it goes out
                    # Avoid unnecessary scrubbing if the logger is not on
                    if logger.isEnabledFor(logging.INFO):
                        logger.info("%s Outgoing request: Method=%s, Path=%s, Query=%s, Headers=%s.",
                                    client_request_id_prefix,
                                    request.method,
                                    request.path,
                                    self._scrub_query_parameters(request.query),
                                    str(self._scrub_headers(request.headers)).replace('\n', ''))

                    # Perform the request
                    response = self._httpclient.perform_request(request)

                    # Execute the response callback
                    if self.response_callback:
                        self.response_callback(response)

                    # Set the response context
                    retry_context.response = response

                    # Log the response when it comes back
                    logger.info("%s Receiving Response: "
                                "%s, HTTP Status Code=%s, Message=%s, Headers=%s.",
                                client_request_id_prefix,
                                self.extract_date_and_request_id(retry_context),
                                response.status,
                                response.message,
                                str(response.headers).replace('\n', ''))

                    # Parse and wrap HTTP errors in AzureHttpError which inherits from AzureException
                    if response.status >= 300:
                        # This exception will be caught by the general error handler
                        # and raised as an azure http exception
                        _http_error_handler(
                            HTTPError(response.status, response.message, response.headers, response.body))

                    # Parse the response
                    if parser:
                        if parser_args:
                            args = [response]
                            args.extend(parser_args)
                            return parser(*args)
                        else:
                            return parser(response)
                    else:
                        return
                except AzureException as ex:
                    retry_context.exception = ex
                    raise ex
                except Exception as ex:
                    retry_context.exception = ex
                    raise _wrap_exception(ex, AzureException)

            except AzureException as ex:
                # only parse the strings used for logging if logging is at least enabled for CRITICAL
                exception_str_in_one_line = ''
                status_code = ''
                timestamp_and_request_id = ''
                if logger.isEnabledFor(logging.CRITICAL):
                    exception_str_in_one_line = str(ex).replace('\n', '')
                    status_code = retry_context.response.status if retry_context.response is not None else 'Unknown'
                    timestamp_and_request_id = self.extract_date_and_request_id(retry_context)

                # if the http error was expected, we should short-circuit
                if isinstance(ex, AzureHttpError) and expected_errors is not None and ex.error_code in expected_errors:
                    logger.info("%s Received expected http error: "
                                "%s, HTTP status code=%s, Exception=%s.",
                                client_request_id_prefix,
                                timestamp_and_request_id,
                                status_code,
                                exception_str_in_one_line)
                    raise ex
                elif isinstance(ex, AzureSigningError):
                    logger.info("%s Unable to sign the request: Exception=%s.",
                                client_request_id_prefix,
                                exception_str_in_one_line)
                    raise ex

                logger.info("%s Operation failed: checking if the operation should be retried. "
                            "Current retry count=%s, %s, HTTP status code=%s, Exception=%s.",
                            client_request_id_prefix,
                            retry_context.count if hasattr(retry_context, 'count') else 0,
                            timestamp_and_request_id,
                            status_code,
                            exception_str_in_one_line)

                # Decryption failures (invalid objects, invalid algorithms, data unencrypted in strict mode, etc)
                # will not be resolved with retries.
                if str(ex) == _ERROR_DECRYPTION_FAILURE:
                    logger.error("%s Encountered decryption failure: this cannot be retried. "
                                 "%s, HTTP status code=%s, Exception=%s.",
                                 client_request_id_prefix,
                                 timestamp_and_request_id,
                                 status_code,
                                 exception_str_in_one_line)
                    raise ex

                # Determine whether a retry should be performed and if so, how 
                # long to wait before performing retry.
                retry_interval = self.retry(retry_context)
                if retry_interval is not None:
                    # Execute the callback
                    if self.retry_callback:
                        self.retry_callback(retry_context)

                    logger.info(
                        "%s Retry policy is allowing a retry: Retry count=%s, Interval=%s.",
                        client_request_id_prefix,
                        retry_context.count,
                        retry_interval)

                    # Sleep for the desired retry interval
                    sleep(retry_interval)
                else:
                    logger.error("%s Retry policy did not allow for a retry: "
                                 "%s, HTTP status code=%s, Exception=%s.",
                                 client_request_id_prefix,
                                 timestamp_and_request_id,
                                 status_code,
                                 exception_str_in_one_line)
                    raise ex
            finally:
                # If this is a location locked operation and the location is not set, 
                # this is the first request of that operation. Set the location to 
                # be used for subsequent requests in the operation.
                if operation_context.location_lock and not operation_context.host_location:
                    # note: to cover the emulator scenario, the host_location is grabbed
                    # from request.host_locations(which includes the dev account name)
                    # instead of request.host(which at this point no longer includes the dev account name)
                    operation_context.host_location = {
                        retry_context.location_mode: request.host_locations[retry_context.location_mode]}
