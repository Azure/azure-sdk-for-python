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
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from azure.core.exceptions import (
    TokenExpiredError,
    TokenInvalidError,
    AuthenticationError,
    ClientRequestError,
    MaxRedirectError,
    raise_with_traceback
)

from .base import HTTPPolicy, RequestHistory


_LOGGER = logging.getLogger(__name__)


class RedirectPolicy(HTTPPolicy):

    REDIRECT_STATUSES = frozenset([301, 302, 303, 307, 308])

    REDIRECT_HEADERS_BLACKLIST = frozenset(['Authorization'])

    def __init__(self, **kwargs):
        self.redirects = kwargs.pop('redirect_max', 30)
        remove_headers = kwargs.pop('redirect_remove_headers', set())
        self.remove_headers_on_redirect = remove_headers.union(self.REDIRECT_HEADERS_BLACKLIST)
        redirect_status = kwargs.pop('redirect_on_status_codes', set())
        self.redirect_on_status_codes = redirect_status.union(self.REDIRECT_STATUSES)
        self.raise_on_redirect = True
        self.history = []

    @classmethod
    def no_redirects(cls):
        return cls(redirect_max=0)

    def get_redirect_location(self, response):
        """
        Should we redirect and where to?
        :returns: Truthy redirect location string if we got a redirect status
            code and valid location. ``None`` if redirect status and no
            location. ``False`` if not a redirect status code.
        """
        if response.http_response.status_code in self.redirect_on_status_codes \
                and response.http_request.method in ['GET', 'HEAD']:
            return response.http_response.headers.get('location')

        return False

    def increment(self, response, redirect_location):
        """ Return a new Retry object with incremented retry counters.

        :param response: A response object, or None, if the server did not
            return a response.
        :type response: :class:`~urllib3.response.HTTPResponse`
        :param Exception error: An error encountered during the request, or
            None if the response was received successfully.

        :return: A new ``Retry`` object.
        """
        # Redirect retry?
        if self.redirects:
            self.redirects -= 1
        self.history.append(RequestHistory(response.http_request, http_response=response.http_response))
        
        redirected = urlparse(redirect_location)
        if not redirected.netloc:
            base_url = urlparse(response.http_request.url)
            response.http_request.url = "{}://{}/{}".format(
                base_url.scheme,
                base_url.netloc,
                redirect_location.lstrip('/'))
        else:
            response.http_request.url = redirect_location
        if response.http_response.status_code == 303:
            response.http_request.method = 'GET'
        for non_redirect_header in self.remove_headers_on_redirect:
            response.http_request.headers.pop(non_redirect_header, None)
        return self.redirects > 0

    def send(self, request, **kwargs):
        retryable = True
        while retryable:
            response = self.next.send(request, **kwargs)
            redirect_location = self.get_redirect_location(response)
            if redirect_location:
                retryable = self.increment(response, redirect_location)
                request.http_request = response.http_request
                continue
            response.history = self.history
            return response

        raise MaxRedirectError(self.history)
