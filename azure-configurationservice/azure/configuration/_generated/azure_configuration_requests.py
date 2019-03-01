# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""
This module is the requests implementation of Pipeline ABC
"""
from __future__ import absolute_import  # we have a "requests" module that conflicts with "requests" on Py2.7
import contextlib
import logging
import threading
from typing import TYPE_CHECKING, List, Callable, Iterator, Any, Union, Dict, Optional  # pylint: disable=unused-import
import warnings

from oauthlib import oauth2
import requests
from requests.models import CONTENT_CHUNK_SIZE

from urllib3 import Retry  # Needs requests 2.16 at least to be safe

from msrest.exceptions import (
    TokenExpiredError,
    ClientRequestError,
    raise_with_traceback
)
from msrest.universal_http import ClientRequest, ClientResponse
from msrest.universal_http.requests import BasicRequestsHTTPSender
from msrest.pipeline import HTTPSender, HTTPPolicy, Response, Request

from .utils import parse_connection_string, get_current_utc_time
import hashlib
import base64
import hmac

_LOGGER = logging.getLogger(__name__)


class AzConfigRequestsCredentialsPolicy(HTTPPolicy):
    """Implementation of request-oauthlib except and retry logic.
    """
    def __init__(self, config):
        super(AzConfigRequestsCredentialsPolicy, self).__init__()
        self._config = config

    
    def _signed_session(self, request, session):
        verb = request.http_request.method.upper()
        host, credential, secret = parse_connection_string(self._config.connection_string)

        # Get the path and query from url, which looks like https://host/path/query
        query_url = str(request.http_request.url[len(host) + 8:])

        signed_headers = "x-ms-date;host;x-ms-content-sha256"

        utc_now = get_current_utc_time()
        if request.http_request.body is None:
            request.http_request.body = ''
        content_digest = hashlib.sha256((bytes(request.http_request.body, 'utf-8'))).digest()
        content_hash = base64.b64encode(content_digest).decode('utf-8')

        string_to_sign = verb + '\n' + query_url + '\n' + utc_now + ';' + host + ';' + content_hash

        #decode secret
        decoded_secret = base64.b64decode(secret, validate=True)
        digest = hmac.new(decoded_secret, bytes(string_to_sign, 'utf-8'), hashlib.sha256).digest()
        signature = base64.b64encode(digest).decode('utf-8')

        signature_header = {
            "x-ms-date": utc_now,
            "x-ms-content-sha256": content_hash,
            "Authorization": "HMAC-SHA256 Credential=" + credential + ", SignedHeaders=" + signed_headers + ", Signature=" + signature
        }

        request.http_request.headers.update(signature_header)

        return request

    def send(self, request, **kwargs):
        session = request.context.session
        self._signed_session(request, session)
        return self.next.send(request, **kwargs)
        
class RequestsPatchSession(HTTPPolicy):
    """Implements request level configuration
    that are actually to be done at the session level.

    This is highly deprecated, and is totally legacy.
    The pipeline structure allows way better design for this.
    """
    _protocols = ['http://', 'https://']

    def send(self, request, **kwargs):
        """Patch the current session with Request level operation config.

        This is deprecated, we shouldn't patch the session with
        arguments at the Request, and "config" should be used.
        """
        session = request.context.session

        old_max_redirects = None
        if 'max_redirects' in kwargs:
            warnings.warn("max_redirects in operation kwargs is deprecated, use config.redirect_policy instead",
                          DeprecationWarning)
            old_max_redirects = session.max_redirects
            session.max_redirects = int(kwargs['max_redirects'])

        old_trust_env = None
        if 'use_env_proxies' in kwargs:
            warnings.warn("use_env_proxies in operation kwargs is deprecated, use config.proxies instead",
                          DeprecationWarning)
            old_trust_env = session.trust_env
            session.trust_env = bool(kwargs['use_env_proxies'])

        old_retries = {}
        if 'retries' in kwargs:
            warnings.warn("retries in operation kwargs is deprecated, use config.retry_policy instead",
                          DeprecationWarning)
            max_retries = kwargs['retries']
            for protocol in self._protocols:
                old_retries[protocol] = session.adapters[protocol].max_retries
                session.adapters[protocol].max_retries = max_retries

        try:
            return self.next.send(request, **kwargs)
        finally:
            if old_max_redirects:
                session.max_redirects = old_max_redirects

            if old_trust_env:
                session.trust_env = old_trust_env

            if old_retries:
                for protocol in self._protocols:
                    session.adapters[protocol].max_retries = old_retries[protocol]

class RequestsContext(object):
    def __init__(self, session):
        self.session = session


class PipelineRequestsHTTPSender(HTTPSender):
    """Implements a basic Pipeline, that supports universal HTTP lib "requests" driver.
    """

    def __init__(self, universal_http_requests_driver=None):
        # type: (Optional[BasicRequestsHTTPSender]) -> None
        self.driver = universal_http_requests_driver or BasicRequestsHTTPSender()

    def __enter__(self):
        # type: () -> PipelineRequestsHTTPSender
        self.driver.__enter__()
        return self

    def __exit__(self, *exc_details):  # pylint: disable=arguments-differ
        self.driver.__exit__(*exc_details)

    def close(self):
        self.__exit__()

    def build_context(self):
        # type: () -> RequestsContext
        return RequestsContext(
            session=self.driver.session,
        )

    def send(self, request, **kwargs):
        # type: (Request[ClientRequest], Any) -> Response
        """Send request object according to configuration.

        :param Request request: The request object to be sent.
        """
        if request.context is None:  # Should not happen, but make mypy happy and does not hurt
            request.context = self.build_context()

        if request.context.session is not self.driver.session:
            kwargs['session'] = request.context.session

        return Response(
            request,
            self.driver.send(request.http_request, **kwargs)
        )
