# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import sys
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore



from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import SansIOHTTPPolicy

from azure.table._shared._constants import (
    DEV_ACCOUNT_NAME,
    DEV_ACCOUNT_SECONDARY_NAME
)

from ._common_conversion import (
    _sign_string,
)

from ._error import (
    _wrap_exception,
)

logger = logging.getLogger(__name__)


# wraps a given exception with the desired exception type
def _wrap_exception(ex, desired_type):
    msg = ""
    if ex.args:
        msg = ex.args[0]
    if sys.version_info >= (3,):
        # Automatic chaining in Python 3 means we keep the trace
        return desired_type(msg)
    # There isn't a good solution in 2 for keeping the stack trace
    # in general, or that will not result in an error in 3
    # However, we can keep the previous error type and message
    # TODO: In the future we will log the trace
    return desired_type('{}: {}'.format(ex.__class__.__name__, msg))


class AzureSigningError(ClientAuthenticationError):
    """
    Represents a fatal error when attempting to sign a request.
    In general, the cause of this exception is user error. For example, the given account key is not valid.
    Please visit https://docs.microsoft.com/en-us/azure/storage/common/storage-create-storage-account for more info.
    """


# pylint: disable=no-self-use
class SharedKeyCredentialPolicy(SansIOHTTPPolicy):

    def __init__(self, account_name, account_key, is_emulated=False):
        self.account_name = account_name
        self.account_key = account_key
        self.is_emulated = is_emulated

    def _get_headers(self, request, headers_to_sign):
        headers = dict((name.lower(), value) for name, value in request.headers.items() if value)
        if 'content-length' in headers and headers['content-length'] == '0':
            del headers['content-length']
        return '\n'.join(headers.get(x, '') for x in headers_to_sign) + '\n'

    def _get_verb(self, request):
        return request.method + '\n'

    def _get_canonicalized_resource(self, request):
        # uri_path = request.path.split('?')[0]
        uri_path = urlparse(request.url).path

        # for emulator, use the DEV_ACCOUNT_NAME instead of DEV_ACCOUNT_SECONDARY_NAME
        # as this is how the emulator works
        if self.is_emulated and uri_path.find(DEV_ACCOUNT_SECONDARY_NAME) == 1:
            # only replace the first instance
            uri_path = uri_path.replace(DEV_ACCOUNT_SECONDARY_NAME, DEV_ACCOUNT_NAME, 1)

        return '/' + self.account_name + uri_path

    def _get_canonicalized_headers(self, request):
        string_to_sign = ''
        x_ms_headers = []
        for name, value in request.headers.items():
            if name.startswith('x-ms-'):
                x_ms_headers.append((name.lower(), value))
        x_ms_headers.sort()
        for name, value in x_ms_headers:
            if value is not None:
                string_to_sign += ''.join([name, ':', value, '\n'])
        return string_to_sign

    def _add_authorization_header(self, request, string_to_sign):
        try:
            signature = _sign_string(self.account_key, string_to_sign)
            auth_string = 'SharedKey ' + self.account_name + ':' + signature
            request.headers['Authorization'] = auth_string
        except Exception as ex:
            # Wrap any error that occurred as signing error
            # Doing so will clarify/locate the source of problem
            raise _wrap_exception(ex, AzureSigningError)

    def on_request(self, request):  # type: (PipelineRequest) -> Union[None, Awaitable[None]]
        self.sign_request(request.http_request)

    def sign_request(self, request):
        string_to_sign = \
            self._get_verb(request) + \
            self._get_headers(
                request,
                ['content-md5', 'content-type', 'x-ms-date'],
            ) + \
            self._get_canonicalized_resource(request) + \
            self._get_canonicalized_resource_query(request)
        self._add_authorization_header(request, string_to_sign)
        logger.debug("String_to_sign=%s", string_to_sign)

    def _get_canonicalized_resource_query(self, request):
        for name, value in request.query.items():
            if name == 'comp':
                return '?comp=' + value
        return ''

    # def _get_canonicalized_resource_query(self, request):
    #     sorted_queries = [(name, value) for name, value in request.query.items()]
    #     sorted_queries.sort()
    #
    #     string_to_sign = ''
    #     for name, value in sorted_queries:
    #         if value is not None:
    #             string_to_sign += '\n' + name.lower() + ':' + value
    #     return string_to_sign
