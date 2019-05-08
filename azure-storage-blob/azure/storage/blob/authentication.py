# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging

from azure.core.pipeline.policies import SansIOHTTPPolicy

from .constants import DEV_ACCOUNT_NAME, DEV_ACCOUNT_SECONDARY_NAME

logger = logging.getLogger(__name__)


class SharedKeyCredentials(SansIOHTTPPolicy):

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
        uri_path = request.url.split('?')[0]

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

    def _get_canonicalized_resource_query(self, request):
        sorted_queries = [(name, value) for name, value in request.query.items()]
        sorted_queries.sort()

        string_to_sign = ''
        for name, value in sorted_queries:
            if value is not None:
                string_to_sign += '\n' + name.lower() + ':' + value

        return string_to_sign

    def _add_authorization_header(self, request, string_to_sign):
        try:
            signature = _sign_string(self.account_key, string_to_sign)
            auth_string = 'SharedKey ' + self.account_name + ':' + signature
            request.headers['Authorization'] = auth_string
        except Exception as ex:
            # Wrap any error that occurred as signing error
            # Doing so will clarify/locate the source of problem
            # TODO: AzureSigningError
            raise _wrap_exception(ex, AzureSigningError)

    def on_request(self, request, **kwargs):
        string_to_sign = \
            self._get_verb(request) + \
            self._get_headers(
                request,
                [
                    'content-encoding', 'content-language', 'content-length',
                    'content-md5', 'content-type', 'date', 'if-modified-since',
                    'if-match', 'if-none-match', 'if-unmodified-since', 'byte_range'
                ]
            ) + \
            self._get_canonicalized_headers(request) + \
            self._get_canonicalized_resource(request) + \
            self._get_canonicalized_resource_query(request)

        self._add_authorization_header(request, string_to_sign)
        logger.debug("String_to_sign=%s", string_to_sign)
