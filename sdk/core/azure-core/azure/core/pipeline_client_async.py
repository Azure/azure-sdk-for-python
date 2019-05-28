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

import logging
try:
    from urlparse import urljoin, urlparse # type: ignore
except ImportError:
    from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

from typing import List, Any, Dict, Union, IO, Tuple, Optional, Callable, Iterator, cast, TYPE_CHECKING  # pylint: disable=unused-import

from .pipeline import AsyncPipeline
from .pipeline.policies import ContentDecodePolicy
from .pipeline.transport import HttpRequest, AioHttpTransport

_LOGGER = logging.getLogger(__name__)

class AsyncPipelineClient(object):
    """Service client core methods.

    This contains methods are sans I/O and not tight to sync or async implementation.
    :param Configuration config: Service configuration.
    """

    def __init__(self, base_url, config, **kwargs):
        if config is None:
            raise ValueError("Config is a required parameter")
        self._config = config
        self._base_url = base_url
        if kwargs.get('pipeline'):
            self._pipeline = kwargs['pipeline']
        else:
            transport = kwargs.get('transport')
            if not transport:
                transport = AioHttpTransport(config, **kwargs)
            self._pipeline = self._build_pipeline(config, transport)

    def _build_pipeline(self, config, transport): # pylint: disable=no-self-use
        policies = [
            config.headers_policy,
            config.user_agent_policy,
            config.authentication_policy,
            ContentDecodePolicy(),
            config.redirect_policy,
            config.retry_policy,
            config.custom_hook_policy,
            config.logging_policy,
        ]
        return AsyncPipeline(transport, policies)

    def _request(
            self, method, # type: str
            url, # type: str
            params, # type: Optional[Dict[str, str]]
            headers, # type: Optional[Dict[str, str]]
            content, # type: Any
            form_content, # type: Optional[Dict[str, Any]]
            stream_content, # type: Any
        ):
        # type: (...) -> HttpRequest
        """Create HttpRequest object.

        :param str url: URL for the request.
        :param dict params: URL query parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = HttpRequest(method, self.format_url(url))

        if params:
            request.format_parameters(params)

        if headers:
            request.headers.update(headers)

        if content is not None:
            if isinstance(content, ET.Element):
                request.set_xml_body(content)
            else:
                try:
                    request.set_json_body(content)
                except TypeError:
                    request.data = content

        if form_content:
            request.set_formdata_body(form_content)
        elif stream_content:
            request.set_streamed_data_body(stream_content)

        return request

    def format_url(self, url_template, **kwargs):
        # type: (str, Any) -> str
        """Format request URL with the client base URL, unless the
        supplied URL is already absolute.

        :param str url_template: The request URL to be formatted if necessary.
        """
        url = url_template.format(**kwargs)
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            url = url.lstrip('/')
            base = self._base_url.format(**kwargs).rstrip('/')
            url = urljoin(base + '/', url)
        return url

    def get(
            self, url, # type: str
            params=None, # type: Optional[Dict[str, str]]
            headers=None, # type: Optional[Dict[str, str]]
            content=None, # type: Any
            form_content=None, # type: Optional[Dict[str, Any]]
        ):
        # type: (...) -> HttpRequest
        """Create a GET request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request('GET', url, params, headers, content, form_content, None)
        request.method = 'GET'
        return request

    def put(
            self, url, # type: str
            params=None, # type: Optional[Dict[str, str]]
            headers=None, # type: Optional[Dict[str, str]]
            content=None, # type: Any
            form_content=None, # type: Optional[Dict[str, Any]]
            stream_content=None # type: Any
        ):
        # type: (...) -> HttpRequest
        """Create a PUT request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request('PUT', url, params, headers, content, form_content, stream_content)
        return request

    def post(
            self, url, # type: str
            params=None, # type: Optional[Dict[str, str]]
            headers=None, # type: Optional[Dict[str, str]]
            content=None, # type: Any
            form_content=None, # type: Optional[Dict[str, Any]]
            stream_content=None # type: Any
        ):
        # type: (...) -> HttpRequest
        """Create a POST request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request('POST', url, params, headers, content, form_content, stream_content)
        return request

    def head(
            self, url, # type: str
            params=None, # type: Optional[Dict[str, str]]
            headers=None, # type: Optional[Dict[str, str]]
            content=None, # type: Any
            form_content=None, # type: Optional[Dict[str, Any]]
            stream_content=None # type: Any
        ):
        # type: (...) -> HttpRequest
        """Create a HEAD request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request('HEAD', url, params, headers, content, form_content, stream_content)
        return request

    def patch(
            self, url, # type: str
            params=None, # type: Optional[Dict[str, str]]
            headers=None, # type: Optional[Dict[str, str]]
            content=None, # type: Any
            form_content=None, # type: Optional[Dict[str, Any]]
            stream_content=None # type: Any
        ):
        # type: (...) -> HttpRequest
        """Create a PATCH request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request('PATCH', url, params, headers, content, form_content, stream_content)
        return request

    def delete(self, url, params=None, headers=None, content=None, form_content=None):
        # type: (str, Optional[Dict[str, str]], Optional[Dict[str, str]], Any, Optional[Dict[str, Any]]) -> HttpRequest
        """Create a DELETE request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request('DELETE', url, params, headers, content, form_content, None)
        return request

    def merge(self, url, params=None, headers=None, content=None, form_content=None):
        # type: (str, Optional[Dict[str, str]], Optional[Dict[str, str]], Any, Optional[Dict[str, Any]]) -> HttpRequest
        """Create a MERGE request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request('MERGE', url, params, headers, content, form_content, None)
        return request

    async def __aenter__(self):
        await self._pipeline.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self):
        await self._pipeline.__aexit__()
