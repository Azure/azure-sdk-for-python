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

import requests
from requests.models import CONTENT_CHUNK_SIZE

from urllib3 import Retry  # Needs requests 2.16 at least to be safe

from azure.core.exceptions import (
    TokenExpiredError,
    TokenInvalidError,
    AuthenticationError,
    ClientRequestError,
    raise_with_traceback
)

from .base import HTTPPolicy


_LOGGER = logging.getLogger(__name__)


class CredentialsPolicy(HTTPPolicy):
    # TODO: This is deprecated: Need to remove

    def __init__(self, credentials, config=None):
        super(CredentialsPolicy, self).__init__()
        self._credentials = credentials

    def send(self, request, **kwargs):
        session = request.context.session
        try:
            self._credentials.signed_session(session)
        except TypeError: # Credentials does not support session injection
            _LOGGER.warning("Your credentials class does not support session injection. Performance will not be optimal.")
            request.context.session = session = self._credentials.signed_session()

        try:
            return self.next.send(request, **kwargs)
        except (TokenExpiredError, TokenInvalidError) as err:
            _LOGGER.warning("Token expired or is invalid. Attempting to refresh.")

        try:
            self._credentials.refresh_session(session)
        except TypeError: # Credentials does not support session injection
            _LOGGER.warning("Your credentials class does not support session injection. Performance will not be optimal.")
            request.context.session = session = self._credentials.refresh_session()

        return self.next.send(request, **kwargs)