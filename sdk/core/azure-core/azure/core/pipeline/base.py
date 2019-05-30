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
import xml.etree.ElementTree as ET
try:
    from urlparse import urljoin, urlparse # type: ignore
except ImportError:
    from urllib.parse import urljoin, urlparse
from typing import (TYPE_CHECKING, Generic, TypeVar, cast, IO, List, Union, Any, Mapping, Dict, Optional, # pylint: disable=unused-import
                    Tuple, Callable, Iterator)
from azure.core.pipeline import AbstractContextManager, PipelineRequest, PipelineResponse, PipelineContext
from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline.policies import HTTPPolicy, SansIOHTTPPolicy
HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")
HttpTransportType = TypeVar("HttpTransportType")

_LOGGER = logging.getLogger(__name__)
PoliciesType = List[Union[HTTPPolicy, SansIOHTTPPolicy]]


class _SansIOHTTPPolicyRunner(HTTPPolicy, Generic[HTTPRequestType, HTTPResponseType]):
    """Sync implementation of the SansIO policy.
    """

    def __init__(self, policy):
        # type: (SansIOHTTPPolicy) -> None
        super(_SansIOHTTPPolicyRunner, self).__init__()
        self._policy = policy

    def send(self, request):
        # type: (PipelineRequest) -> PipelineResponse
        self._policy.on_request(request)
        try:
            response = self.next.send(request)
        except Exception: #pylint: disable=broad-except
            if not self._policy.on_exception(request):
                raise
        else:
            self._policy.on_response(request, response)
        return response


class _TransportRunner(HTTPPolicy):

    def __init__(self, sender):
        # type: (HttpTransportType) -> None
        super(_TransportRunner, self).__init__()
        self._sender = sender

    def send(self, request):
        return PipelineResponse(
            request.http_request,
            self._sender.send(request.http_request, **request.context.options),
            context=request.context
        )


class Pipeline(AbstractContextManager, Generic[HTTPRequestType, HTTPResponseType]):
    """A pipeline implementation.

    This is implemented as a context manager, that will activate the context
    of the HTTP sender.
    """

    def __init__(self, transport, policies=None):
        # type: (HttpTransportType, PoliciesType) -> None
        self._impl_policies = []  # type: List[HTTPPolicy]
        self._transport = transport  # type: ignore

        for policy in (policies or []):
            if isinstance(policy, SansIOHTTPPolicy):
                self._impl_policies.append(_SansIOHTTPPolicyRunner(policy))
            elif policy:
                self._impl_policies.append(policy)
        for index in range(len(self._impl_policies)-1):
            self._impl_policies[index].next = self._impl_policies[index+1]
        if self._impl_policies:
            self._impl_policies[-1].next = _TransportRunner(self._transport)

    def __enter__(self):
        # type: () -> Pipeline
        self._transport.__enter__() # type: ignore
        return self

    def __exit__(self, *exc_details):  # pylint: disable=arguments-differ
        self._transport.__exit__(*exc_details)

    def run(self, request, **kwargs):
        # type: (HTTPRequestType, Any) -> PipelineResponse
        context = PipelineContext(self._transport, **kwargs)
        pipeline_request = PipelineRequest(request, context) # type: PipelineRequest
        first_node = self._impl_policies[0] if self._impl_policies else _TransportRunner(self._transport)
        return first_node.send(pipeline_request)  # type: ignore


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

    def _format_url_section(self, template, **kwargs):
        while True:
            try:
                return template.format(**kwargs)
            except KeyError as key:
                components = template.split("/")
                new_components = [c for c in components if "{{{}}}".format(key.args[0]) not in c]
                template = "/".join(new_components)

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
