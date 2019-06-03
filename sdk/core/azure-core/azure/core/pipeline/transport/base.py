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
import abc
import json
import logging
import os
import time
try:
    from urlparse import urljoin, urlparse # type: ignore
except ImportError:
    from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

from typing import (TYPE_CHECKING, Generic, TypeVar, cast, IO, List, Union, Any, Mapping, Dict, # pylint: disable=unused-import
                    Optional, Tuple, Callable, Iterator)

# This file is NOT using any "requests" HTTP implementation
# However, the CaseInsensitiveDict is handy.
# If one day we reach the point where "requests" can be skip totally,
# might provide our own implementation
from requests.structures import CaseInsensitiveDict
from azure.core.pipeline import ABC, AbstractContextManager, PipelineRequest, PipelineResponse


HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")

_LOGGER = logging.getLogger(__name__)


class HttpTransport(AbstractContextManager, ABC, Generic[HTTPRequestType, HTTPResponseType]): # type: ignore
    """An http sender ABC.
    """

    @abc.abstractmethod
    def send(self, request, **kwargs):
        # type: (PipelineRequest, Any) -> PipelineResponse
        """Send the request using this HTTP sender.
        """

    @abc.abstractmethod
    def open(self):
        """Assign new session if one does not already exist."""

    @abc.abstractmethod
    def close(self):
        """Close the session if it is not externally owned."""

    def sleep(self, duration): #pylint: disable=no-self-use
        time.sleep(duration)


class HttpRequest(object):
    """Represents a HTTP request.

    URL can be given without query parameters, to be added later using "format_parameters".

    :param str method: HTTP method (GET, HEAD, etc.)
    :param str url: At least complete scheme/host/path
    :param dict[str,str] headers: HTTP headers
    :param files: Files list.
    :param data: Body to be sent.
    :type data: bytes or str.
    """
    def __init__(self, method, url, headers=None, files=None, data=None):
        # type: (str, str, Mapping[str, str], Any, Any) -> None
        self.method = method
        self.url = url
        self.headers = CaseInsensitiveDict(headers)
        self.files = files
        self.data = data

    def __repr__(self):
        return '<HttpRequest [%s]>' % (self.method)

    @property
    def query(self):
        """The query parameters of the request as a dict."""
        query = urlparse(self.url).query
        if query:
            return {p[0]: p[-1] for p in [p.partition('=') for p in query.split('&')]}
        return {}

    @property
    def body(self):
        """Alias to data."""
        return self.data

    @body.setter
    def body(self, value):
        self.data = value

    @staticmethod
    def _format_data(data):
        # type: (Union[str, IO]) -> Union[Tuple[None, str], Tuple[Optional[str], IO, str]]
        """Format field data according to whether it is a stream or
        a string for a form-data request.

        :param data: The request field data.
        :type data: str or file-like object.
        """
        if hasattr(data, 'read'):
            data = cast(IO, data)
            data_name = None
            try:
                if data.name[0] != '<' and data.name[-1] != '>':
                    data_name = os.path.basename(data.name)
            except (AttributeError, TypeError):
                pass
            return (data_name, data, "application/octet-stream")
        return (None, cast(str, data))

    def format_parameters(self, params):
        # type: (Dict[str, str]) -> None
        """Format parameters into a valid query string.
        It's assumed all parameters have already been quoted as
        valid URL strings.

        :param dict params: A dictionary of parameters.
        """
        query = urlparse(self.url).query
        if query:
            self.url = self.url.partition('?')[0]
            existing_params = {
                p[0]: p[-1]
                for p in [p.partition('=') for p in query.split('&')]
            }
            params.update(existing_params)
        query_params = ["{}={}".format(k, v) for k, v in params.items()]
        query = '?' + '&'.join(query_params)
        self.url = self.url + query

    def set_streamed_data_body(self, data):
        """Set a streamable data body.

        :param data: The request field data.
        """
        if not any(hasattr(data, attr) for attr in ["read", "__iter__", "__aiter__"]):
            raise TypeError("A streamable data source must be an open file-like object or iterable.")
        self.data = data
        self.files = None

    def set_xml_body(self, data):
        """Set an XML element tree as the body of the request.

        :param data: The request field data.
        """
        if data is None:
            self.data = None
        else:
            bytes_data = ET.tostring(data, encoding="utf8")
            self.data = bytes_data.replace(b"encoding='utf8'", b"encoding='utf-8'")
            self.headers['Content-Length'] = str(len(self.data))
        self.files = None

    def set_json_body(self, data):
        """Set a JSON-friendly object as the body of the request.
        
        :param data: The request field data.
        """
        if data is None:
            self.data = None
        else:
            self.data = json.dumps(data)
            self.headers['Content-Length'] = str(len(self.data))
        self.files = None

    def set_formdata_body(self, data=None):
        """Set form-encoded data as the body of the request.

        :param data: The request field data.
        """
        if data is None:
            data = {}
        content_type = self.headers.pop('Content-Type', None) if self.headers else None

        if content_type and content_type.lower() == 'application/x-www-form-urlencoded':
            self.data = {f: d for f, d in data.items() if d is not None}
            self.files = None
        else: # Assume "multipart/form-data"
            self.files = {f: self._format_data(d) for f, d in data.items() if d is not None}
            self.data = None

    def set_bytes_body(self, data):
        """Set generic bytes as the body of the request.
        
        :param data: The request field data.
        """
        if data:
            self.headers['Content-Length'] = str(len(data))
        self.data = data
        self.files = None


class _HttpResponseBase(object):
    """Represent a HTTP response.

    No body is defined here on purpose, since async pipeline
    will provide async ways to access the body
    Full in-memory using "body" as bytes.

    :param request: The request.
    :type request: ~azure.core.pipeline.transport.HttpRequest
    :param internal_response: The object returned from the HTTP library.
    :param int status_code: The status code of the response
    :param dict headers: The request headers.
    :param str reason: Status reason of response.
    :param str content_type: The content type.
    :param int block_size: Defaults to 4096 bytes.
    """
    def __init__(self, request, internal_response, block_size=None):
        # type: (HttpRequest, Any, Optional[int]) -> None
        self.request = request
        self.internal_response = internal_response
        self.status_code = None  # type: Optional[int]
        self.headers = {}  # type: Dict[str, str]
        self.reason = None  # type: Optional[str]
        self.content_type = None  # type: Optional[str]
        self.block_size = block_size or 4096  # Default to same as Requests


    def body(self):
        # type: () -> bytes
        """Return the whole body as bytes in memory.
        """

    def text(self, encoding=None):
        # type: (str) -> str
        """Return the whole body as a string.

        :param str encoding: The encoding to apply. If None, use "utf-8".
         Implementation can be smarter if they want (using headers).
        """
        return self.body().decode(encoding or "utf-8")


class HttpResponse(_HttpResponseBase):
    def stream_download(self):
        # type: () -> Iterator[bytes]
        """Generator for streaming request body data.

        Should be implemented by sub-classes if streaming download
        is supported.
        """


class PipelineClientBase(object):
    """Base class for pipeline clients.

    :param str base_url: URL for the request.
    """

    def __init__(self, base_url):
        self._base_url = base_url

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
        :param str method: HTTP method (GET, HEAD, etc.)
        :param str url: URL for the request.
        :param dict params: URL query parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
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

    @staticmethod
    def _format_url_section(template, **kwargs):
        components = template.split("/")
        while components:
            try:
                return template.format(**kwargs)
            except KeyError as key:
                formatted_components = template.split("/")
                components = [c for c in formatted_components if "{{{}}}".format(key.args[0]) not in c]
                template = "/".join(components)
        # No URL sections left - returning None

    def format_url(self, url_template, **kwargs):
        # type: (str, Any) -> str
        """Format request URL with the client base URL, unless the
        supplied URL is already absolute.
        :param str url_template: The request URL to be formatted if necessary.
        """
        url = self._format_url_section(url_template, **kwargs)
        if url:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                url = url.lstrip('/')
                base = self._base_url.format(**kwargs).rstrip('/')
                url = urljoin(base + '/', url)
        else:
            url = self._base_url.format(**kwargs)
        return url

    def get(
            self, url, # type: str
            params=None, # type: Optional[Dict[str, str]]
            headers=None, # type: Optional[Dict[str, str]]
            content=None, # type: Any
            form_content=None # type: Optional[Dict[str, Any]]
        ):
        # type: (...) -> HttpRequest
        """Create a GET request object.
        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
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
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
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
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
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
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
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
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
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
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
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
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        request = self._request('MERGE', url, params, headers, content, form_content, None)
        return request
