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
import logging
from typing import Iterator, Optional, Any, Union
import urllib3 # type: ignore
from urllib3.util.retry import Retry # type: ignore
import requests


from azure.core.configuration import Configuration
from azure.core.exceptions import (
    ServiceRequestError,
    ServiceResponseError
)
from . import HttpRequest # pylint: disable=unused-import

from .base import (
    HttpTransport,
    HttpResponse,
    _HttpResponseBase
)


_LOGGER = logging.getLogger(__name__)


class _RequestsTransportResponseBase(_HttpResponseBase):
    """Base class for accessing response data.

    :param HttpRequest request: The request.
    :param requests_response: The object returned from the HTTP library.
    :param int block_size: Size in bytes.
    :param int status_code: The status code of the response.
    :param dict headers: The request headers.
    :param str reason: Status reason of response.
    :param str content_type: The content type.
    """
    def __init__(self, request, requests_response, block_size=None):
        super(_RequestsTransportResponseBase, self).__init__(request, requests_response, block_size=block_size)
        self.status_code = requests_response.status_code
        self.headers = requests_response.headers
        self.reason = requests_response.reason
        content_type = requests_response.headers.get('content-type')
        if content_type:
            self.content_type = content_type.split(";")

    def body(self):
        return self.internal_response.content

    def text(self, encoding=None):
        if encoding:
            self.internal_response.encoding = encoding
        return self.internal_response.text


class StreamDownloadGenerator(object):
    """Generator for streaming response data.

    :param response: The response object.
    :param int block_size: Number of bytes to read into memory.
    :param generator iter_content_func: Iterator for response data.
    :param int content_length: size of body in bytes.
    """
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
        retry_active = True
        retry_total = 3
        while retry_active:
            try:
                chunk = next(self.iter_content_func)
                if not chunk:
                    raise StopIteration()
                return chunk
            except StopIteration:
                self.response.close()
                raise StopIteration()
            except ServiceResponseError:
                retry_total -= 1
                if retry_total <= 0:
                    retry_active = False
                continue
            except Exception as err:
                _LOGGER.warning("Unable to stream download: %s", err)
                self.response.close()
                raise
    next = __next__  # Python 2 compatibility.


class RequestsTransportResponse(HttpResponse, _RequestsTransportResponseBase):
    """Streaming of data from the response.
    """
    def stream_download(self):
        # type: () -> Iterator[bytes]
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

    :param configuration: The service configuration.
    :type configuration: ~azure.core.Configuration
    :param session: The session.
    :type session: requests.Session
    :param bool session_owner: Defaults to True.
    """

    _protocols = ['http://', 'https://']

    def __init__(self, configuration=None, session=None, session_owner=True):
        # type: (Optional[Configuration], Optional[requests.Session], bool) -> None
        self._session_owner = session_owner
        self.config = configuration or Configuration()
        self.session = session

    def __enter__(self):
        # type: () -> RequestsTransport
        self.open()
        return self

    def __exit__(self, *args):  # pylint: disable=arguments-differ
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

    def open(self):
        if not self.session and self._session_owner:
            self.session = requests.Session()
            self._init_session(self.session)

    def close(self):
        if self._session_owner:
            self.session.close()
            self._session_owner = False
            self.session = None

    def send(self, request, **kwargs): # type: ignore
        # type: (HttpRequest, Any) -> HttpResponse
        """Send request object according to configuration.

        Allowed kwargs are:
        - session : will override the driver session and use yours. Should NOT be done unless really required.
        - anything else is sent straight to requests.

        :param request: The request object to be sent.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :return: An HTTPResponse object.
        :rtype: ~azure.core.pipeline.transport.HttpResponse
        """
        self.open()
        response = None
        error = None # type: Optional[Union[ServiceRequestError, ServiceResponseError]]
        if self.config.proxy_policy and 'proxies' not in kwargs:
            kwargs['proxies'] = self.config.proxy_policy.proxies

        try:
            response = self.session.request(  # type: ignore
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
            error = ServiceRequestError(err, error=err)
        except requests.exceptions.ReadTimeout as err:
            error = ServiceResponseError(err, error=err)
        except requests.exceptions.ConnectionError as err:
            if err.args and isinstance(err.args[0], urllib3.exceptions.ProtocolError):
                error = ServiceResponseError(err, error=err)
            else:
                error = ServiceRequestError(err, error=err)
        except requests.RequestException as err:
            error = ServiceRequestError(err, error=err)

        if error:
            raise error
        return RequestsTransportResponse(request, response, self.config.connection.data_block_size)
