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
import asyncio
from collections.abc import AsyncIterator
import functools
import logging
from typing import Any, Callable, Optional, AsyncIterator as AsyncIteratorType

import requests
from requests.models import CONTENT_CHUNK_SIZE

from azure.core.exceptions import (
    TokenExpiredError,
    ClientRequestError,
    raise_with_traceback
)
from azure.core.pipeline.policies import AsyncHTTPPolicy


class AsyncCredentialsPolicy(AsyncHTTPPolicy):
    """Implementation of request-oauthlib except and retry logic.
    """
    def __init__(self, credentials, config=None):
        super(AsyncCredentialsPolicy, self).__init__()
        self._credentials = credentials

    async def send(self, request, **kwargs):
        session = request.context.session
        try:
            self._credentials.signed_session(session)
        except TypeError: # Credentials does not support session injection
            _LOGGER.warning("Your credentials class does not support session injection. Performance will not be optimal.")
            request.context.session = session = self._credentials.signed_session()

        try:
            return await self.next.send(request, **kwargs)
        except (TokenExpiredError, TokenInvalidError) as err:
            _LOGGER.warning("Token expired or is invalid. Attempting to refresh.")

        try:
            self._credentials.refresh_session(session)
        except TypeError: # Credentials does not support session injection
            _LOGGER.warning("Your credentials class does not support session injection. Performance will not be optimal.")
            request.context.session = session = self._credentials.refresh_session()

        return await self.next.send(request, **kwargs)
