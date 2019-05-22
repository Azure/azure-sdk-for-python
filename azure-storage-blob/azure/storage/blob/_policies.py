# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import base64
import hashlib
import sys
from time import time
import logging
from wsgiref.handlers import format_date_time
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from azure.core.pipeline.policies import HeadersPolicy, SansIOHTTPPolicy
from azure.core.exceptions import AzureError

try:
    _unicode_type = unicode
except NameError:
    _unicode_type = str


logger = logging.getLogger(__name__)


class StorageBlobSettings(object):

    def __init__(self, **kwargs):
        self.max_single_put_size = kwargs.get('max_single_put_size', 64 * 1024 * 1024)
        self.copy_polling_interval = 2

        # Block blob uploads
        self.max_block_size = kwargs.get('max_block_size', 4 * 1024 * 1024)
        self.min_large_block_upload_threshold = kwargs.get('min_large_block_upload_threshold', 4 * 1024 * 1024 + 1)
        self.use_byte_buffer = False

        # Page blob uploads
        self.max_page_size = 4 * 1024 * 1024

        # Blob downloads
        self.max_single_get_size = 32 * 1024 * 1024
        self.max_chunk_get_size = 4 * 1024 * 1024


class StorageHeadersPolicy(HeadersPolicy):

    def on_request(self, request):
        # type: (PipelineRequest, Any) -> None
        super(StorageHeadersPolicy, self).on_request(request)
        current_time = format_date_time(time())
        request.http_request.headers['x-ms-date'] = current_time


class StorageSecondaryAccount(SansIOHTTPPolicy):

    def on_request(self, request):
        # type: (PipelineRequest, Any) -> None
        use_secondary = request.context.options.pop('secondary_storage', False)
        if use_secondary:
            parsed_url = urlparse(request.http_request.url)
            account = parsed_url.hostname.split(".blob.core.")[0]
            secondary_account = account if account.endswith('-secondary') else account + '-secondary'
            request.http_request.url = request.http_request.url.replace(account, secondary_account, 1)


class StorageContentValidation(SansIOHTTPPolicy):
    """A simple policy that sends the given headers
    with the request.

    This will overwrite any headers already defined in the request.
    """
    header_name = 'Content-MD5'

    def encode_base64(self, data):
        if isinstance(data, _unicode_type):
            data = data.encode('utf-8')
        encoded = base64.b64encode(data)
        return encoded.decode('utf-8')

    def get_content_md5(self, data):
        md5 = hashlib.md5()
        if isinstance(data, bytes):
            md5.update(data)
        elif hasattr(data, 'read'):
            pos = 0
            try:
                pos = data.tell()
            except:
                pass
            for chunk in iter(lambda: data.read(4096), b""):
                md5.update(chunk)
            try:
                data.seek(pos, SEEK_SET)
            except (AttributeError, IOError):
                raise ValueError("Data should be bytes or a seekable file-like object.")
        else:
            raise ValueError("Data should be bytes or a seekable file-like object.")

        return self.encode_base64(md5.digest())

    def on_request(self, request):
        # type: (PipelineRequest, Any) -> None
        validate_content = request.context.options.pop('validate_content', False)
        if validate_content and request.http_request.method != 'GET':
            computed_md5 = self.get_content_md5(request.http_request.data)
            request.http_request.headers[self.header_name] = computed_md5
            request.context['validate_content_md5'] = computed_md5
        request.context['validate_content'] = validate_content

    def on_response(self, request, response):
        if response.context.get('validate_content', False) and response.http_response.headers.get('content-md5'):
            computed_md5 = request.context.get('validate_content_md5') or \
                self.get_content_md5(response.http_response.body())
            if response.http_response.headers['content-md5'] != computed_md5:
               raise AzureError(
                   'MD5 mismatch. Expected value is \'{0}\', computed value is \'{1}\'.'.format(
                       response.http_response.headers['content-md5'],computed_md5),
                   response=response.http_response
               )
