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
from __future__ import absolute_import
import contextlib
import requests
import threading
import urllib3
from urllib3.util.retry import Retry

from .base import (
    HttpTransport,
    HttpResponse,
    _HttpResponseBase
)

from azure.core.configuration import Configuration
from azure.core.exceptions import (
    ServiceRequestError,
    ServiceResponseError,
    ConnectError,
    ReadTimeoutError,
    raise_with_traceback
)


class RequestsContext(object):
    def __init__(self, session, transport, **kwargs):
        self.session = session
        self.transport = transport
        self.options = kwargs


class _RequestsTransportResponseBase(_HttpResponseBase):

    def __init__(self, request, requests_response, block_size):
        super(_RequestsTransportResponseBase, self).__init__(request, requests_response, block_size)
        self.status_code = requests_response.status_code
        self.headers = requests_response.headers
        self.reason = requests_response.reason

    def body(self):
        return self.internal_response.content

    def text(self, encoding=None):
        if encoding:
            self.internal_response.encoding = encoding
        return self.internal_response.text


class StreamDownloadGenerator(object):

    def __init__(self, response, block_size):
        self.response = response
        self.block_size = block_size
        self.iter_content_func = self.response.iter_content(self.block_size)
        self.content_length = int(response.headers.get('Content-Length', 0))

    def __len__(self):
        return self.content_length

    def __iter__(self):
        return self

    def __next__(self):
        try:
            chunk = next(self.iter_content_func)
            if not chunk:
                raise StopIteration()
            return chunk
        except StopIteration:
            self.response.close()
            raise StopIteration()
        except Exception as err:
            _LOGGER.warning("Unable to stream download: %s", err)
            self.response.close()
            raise


class RequestsTransportResponse(_RequestsTransportResponseBase, HttpResponse):

    def stream_download(self):
        # type: (Optional[int], Optional[Callable]) -> Iterator[bytes]
        """Generator for streaming request body data."""
        return StreamDownloadGenerator(self.internal_response, self.block_size)


class RequestsTransport(HttpTransport):
    """Implements a basic requests HTTP sender.

    Since requests team recommends to use one session per requests, you should
    not consider this class as thread-safe, since it will use one Session
    per instance.

    In this simple implementation:
    - You provide the configured session if you want to, or a basic session is created.
    - All kwargs received by "send" are sent to session.request directly
    """

    _protocols = ['http://', 'https://']

    def __init__(self, configuration=None, session=None):
        # type: (Optional[requests.Session]) -> None
        self._session_mapping = threading.local()
        self.config = configuration or Configuration()
        self.session = session or requests.Session()

    def __enter__(self):
        # type: () -> RequestsTransport
        self.config.connection.keep_alive = True
        return self

    def __exit__(self, *exc_details):  # pylint: disable=arguments-differ
        self.config.connection.keep_alive = False
        self.close()

    def _init_session(self, session):
        # type: (requests.Session) -> None
        """Init session level configuration of requests.

        This is initialization I want to do once only on a session.
        """
        if self.config.proxy_policy:
            session.trust_env = self.config.proxy_policy.use_env_settings
        disable_retries = Retry(total=False, redirect=False, raise_on_status=False)
        adapter = requests.adapters.HTTPAdapter(max_retries=disable_retries)
        for p in self._protocols:
            session.mount(p, adapter)

    @property  # type: ignore
    def session(self):
        try:
            return self._session_mapping.session
        except AttributeError:
            self._session_mapping.session = requests.Session()
            self._init_session(self._session_mapping.session)
            return self._session_mapping.session

    @session.setter
    def session(self, value):
        self._init_session(value)
        self._session_mapping.session = value

    def build_context(self, **kwargs):
        # type: () -> RequestsContext
        return RequestsContext(session=self.session, transport=self, **kwargs)

    def close(self):
        self.session.close()

    def send(self, request, **kwargs):
        # type: (HttpRequest, Any) -> HttpResponse
        """Send request object according to configuration.

        Allowed kwargs are:
        - session : will override the driver session and use yours. Should NOT be done unless really required.
        - anything else is sent straight to requests.

        :param HttpRequest request: The request object to be sent.
        """
        response = None
        error = None
        if self.config.proxy_policy and 'proxies' not in kwargs:
            kwargs['proxies'] = self.config.proxy_policy.proxies

        try:
            response = self.session.request(
                request.method,
                request.url,
                headers=request.headers,
                data=request.data,
                files=request.files,
                verify=kwargs.get('connection_verify', self.config.connection.verify),
                timeout=kwargs.get('connection_timeout', self.config.connection.timeout),
                cert=kwargs.get('connection_cert', self.config.connection.cert),
                allow_redirects=False,
                **kwargs)

        except urllib3.exceptions.NewConnectionError as err:
            error = ConnectError(err, error=err)
        except requests.exceptions.ReadTimeout as err:
            error = ReadTimeoutError(err, error=err)
        except requests.exceptions.ConnectionError as err:
            if err.args and isinstance(err.args[0], urllib3.exceptions.ProtocolError):
                error = ServiceResponseError(err, error=err)
            else:
                error = ConnectError(err, error=err)
        except requests.RequestException as err:
            error = ServiceRequestError(err, error=err)
        finally:
            if not self.config.connection.keep_alive and (not response or not kwargs['stream']):
                self.session.close()

        if error:
            raise error
        return RequestsTransportResponse(request, response, self.config.connection.data_block_size)
