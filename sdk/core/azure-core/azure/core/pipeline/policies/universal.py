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
import json
import logging
import os
import platform
import xml.etree.ElementTree as ET
import types
import re
from typing import cast, IO

from azure.core import __version__  as azcore_version
from azure.core.exceptions import (
    DecodeError,
    raise_with_traceback
)

from .base import SansIOHTTPPolicy


_LOGGER = logging.getLogger(__name__)


class HeadersPolicy(SansIOHTTPPolicy):
    """A simple policy that sends the given headers with the request.

    This will overwrite any headers already defined in the request. Headers can be
    configured up front, where any custom headers will be applied to all outgoing
    operations, and additional headers can also be added dynamically per operation.

    .. code-block:: python
        config = FooService.create_config()
        config.headers_policy.headers = {'CustomValue': 'Foo'}

        # Or headers can be added per operation. These headers will supplement existing headers
        # or those defined in the config headers policy. They will also overwrite existing
        # identical headers.
        result = client.get_operation(headers={'CustomValue': 'Bar'})

    :param dict base_headers: Headers to send with the request.
    """
    def __init__(self, base_headers=None, **kwargs):
        # type: (Mapping[str, str]) -> None
        self._headers = base_headers or {}
        self._headers.update(kwargs.pop('headers', {}))

    @property
    def headers(self):
        """The current headers collection."""
        return self._headers

    def add_header(self, key, value):
        """Add a header to the configuration to be applied to all requests.

        :param str key: The header.
        :param str value: The header's value.
        """
        self._headers[key] = value

    def on_request(self, request, **kwargs):
        # type: (PipelineRequest, Any) -> None
        """Updates with the given headers before sending the request to the next policy.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        request.http_request.headers.update(self.headers)
        additional_headers = request.context.options.pop('headers', {})
        if additional_headers:
            request.http_request.headers.update(additional_headers)


class UserAgentPolicy(SansIOHTTPPolicy):
    """User-Agent Policy. Allows custom values to be added to the User-Agent header.

    .. code-block:: python
        config = FooService.create_config()

        # The user-agent policy allows you to append a custom value to the header.
        config.user_agent_policy.add_user_agent("CustomValue")

        # You can also pass in a custom value per operation to append to the end of the user-agent.
        # This can be used together with the policy configuration to append multiple values.
        result = client.get_operation(user_agent="AnotherValue")

    :param str base_user_agent: Sets the base user agent value.
    :param bool user_agent_overwrite: Overwrites User-Agent when True. Defaults to False.
    :param bool user_agent_use_env: Gets user-agent from environment. Defaults to True.
    """
    _USERAGENT = "User-Agent"
    _ENV_ADDITIONAL_USER_AGENT = 'AZURE_HTTP_USER_AGENT'

    def __init__(self, base_user_agent=None, **kwargs):
        # type: (Optional[str], bool) -> None
        self.overwrite = kwargs.pop('user_agent_overwrite', False)
        self.use_env = kwargs.pop('user_agent_use_env', True)

        if base_user_agent is None:
            self._user_agent = "python/{} ({}) azure-core/{}".format(
                platform.python_version(),
                platform.platform(),
                azcore_version
            )
        else:
            self._user_agent = base_user_agent

    @property
    def user_agent(self):
        # type: () -> str
        """The current user agent value."""
        if self.use_env:
            add_user_agent_header = os.environ.get(self._ENV_ADDITIONAL_USER_AGENT, None)
            if add_user_agent_header is not None:
                return "{} {}".format(self._user_agent, add_user_agent_header)
        return self._user_agent

    def add_user_agent(self, value):
        # type: (str) -> None
        """Add value to current user agent with a space.
        :param str value: value to add to user agent.
        """
        self._user_agent = "{} {}".format(self._user_agent, value)

    def on_request(self, request, **kwargs):
        # type: (PipelineRequest, Any) -> None
        """Modifies the User-Agent header before the request is sent.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        http_request = request.http_request
        options = request.context.options
        if 'user_agent' in options:
            user_agent = options.pop('user_agent')
            if options.pop('user_agent_overwrite', self.overwrite):
                http_request.headers[self._USERAGENT] = user_agent
            else:
                user_agent = "{} {}".format(self.user_agent, user_agent)
                http_request.headers[self._USERAGENT] = user_agent

        elif self.overwrite or self._USERAGENT not in http_request.headers:
            http_request.headers[self._USERAGENT] = self.user_agent


class NetworkTraceLoggingPolicy(SansIOHTTPPolicy):
    """The logging policy in the pipeline is used to output HTTP network trace to the configured logger.

    This accepts both global configuration, and per-request level with "enable_http_logger"

    .. code-block:: python

        import sys
        import logging

        # Create a logger for the 'azure' SDK
        logger = logging.getLogger("azure")
        logger.set_level(logging.DEBUG)

        # Configure a console output
        handler = logging.StreamHandler(stream=sys.stdout)
        logger.addHandler(handler)

        # Configure a file output
        file_handler = logging.FileHandler(filename)
        logger.addHandler(file_handler)

        # Enable network trace logging. This will be logged at DEBUG level.
        # By default, logging is disabled.
        config = FooService.create_config()
        config.logging_policy.enable_http_logger = True

    The logger can also be enabled per operation.

    .. code-block:: python

        result = client.get_operation(logging_enable=True)

    :param bool logging_enable: Use to enable per operation. Defaults to False. 
    :param bool enable_http_logger: Enables network trace logging at DEBUG level.
     Defaults to False.
    """
    def __init__(self, logging_enable=False, **kwargs): # pylint: disable=unused-argument
        self.enable_http_logger = logging_enable

    def on_request(self, request, **kwargs):
        # type: (PipelineRequest, Any) -> None
        """Logs HTTP request to the DEBUG logger.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        http_request = request.http_request
        options = request.context.options
        if options.pop("logging_enable", self.enable_http_logger):
            request.context["logging_enable"] = True
            if not _LOGGER.isEnabledFor(logging.DEBUG):
                return

            try:
                _LOGGER.debug("Request URL: %r", http_request.url)
                _LOGGER.debug("Request method: %r", http_request.method)
                _LOGGER.debug("Request headers:")
                for header, value in http_request.headers.items():
                    if header.lower() == 'authorization':
                        value = '*****'
                    _LOGGER.debug("    %r: %r", header, value)
                _LOGGER.debug("Request body:")

                # We don't want to log the binary data of a file upload.
                if isinstance(http_request.body, types.GeneratorType):
                    _LOGGER.debug("File upload")
                else:
                    _LOGGER.debug(str(http_request.body))
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.debug("Failed to log request: %r", err)

    def on_response(self, request, response, **kwargs):
        # type: (PipelineRequest, PipelineResponse, Any) -> None
        """Logs HTTP response to the DEBUG logger.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: The PipelineResponse object.
        :type response: ~azure.core.pipeline.PipelineResponse
        """
        if response.context.pop("logging_enable", self.enable_http_logger):
            if not _LOGGER.isEnabledFor(logging.DEBUG):
                return

            try:
                _LOGGER.debug("Response status: %r", response.http_response.status_code)
                _LOGGER.debug("Response headers:")
                for res_header, value in response.http_response.headers.items():
                    _LOGGER.debug("    %r: %r", res_header, value)

                # We don't want to log binary data if the response is a file.
                _LOGGER.debug("Response content:")
                pattern = re.compile(r'attachment; ?filename=["\w.]+', re.IGNORECASE)
                header = response.http_response.headers.get('content-disposition')

                if header and pattern.match(header):
                    filename = header.partition('=')[2]
                    _LOGGER.debug("File attachments: %s", filename)
                elif response.http_response.headers.get("content-type", "").endswith("octet-stream"):
                    _LOGGER.debug("Body contains binary data.")
                elif response.http_response.headers.get("content-type", "").startswith("image"):
                    _LOGGER.debug("Body contains image data.")
                else:
                    if response.context.options.get('stream', False):
                        _LOGGER.debug("Body is streamable")
                    else:
                        _LOGGER.debug(response.http_response.text())
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.debug("Failed to log response: %s", repr(err))


class ContentDecodePolicy(SansIOHTTPPolicy):
    """Policy for decoding unstreamed response content.
    """
    JSON_MIMETYPES = [
        'application/json',
        'text/json' # Because we're open minded people...
    ]
    # Name used in context
    CONTEXT_NAME = "deserialized_data"

    @classmethod
    def deserialize_from_text(cls, response, content_type=None):
        # type: (Optional[Union[AnyStr, IO]], Optional[str]) -> Any
        """Decode response data according to content-type.
        Accept a stream of data as well, but will be load at once in memory for now.
        If no content-type, will return the string version (not bytes, not stream)
        :param response: The HTTP response.
        :type response: ~azure.core.pipeline.transport.HttpResponse
        :param str content_type: The content type.
        """
        data = response.text()
        if not data:
            return None

        if hasattr(data, 'read'):
            # Assume a stream
            data = cast(IO, data).read()

        if isinstance(data, bytes):
            data_as_str = data.decode(encoding='utf-8-sig')
        else:
            # Explain to mypy the correct type.
            data_as_str = cast(str, data)

        if content_type is None:
            return data

        if content_type in cls.JSON_MIMETYPES:
            try:
                return json.loads(data_as_str)
            except ValueError as err:
                raise DecodeError(message="JSON is invalid: {}".format(err), response=response, error=err)
        elif "xml" in (content_type or []):
            try:
                return ET.fromstring(data_as_str)
            except ET.ParseError:
                # It might be because the server has an issue, and returned JSON with
                # content-type XML....
                # So let's try a JSON load, and if it's still broken
                # let's flow the initial exception
                def _json_attemp(data):
                    try:
                        return True, json.loads(data)
                    except ValueError:
                        return False, None # Don't care about this one
                success, json_result = _json_attemp(data)
                if success:
                    return json_result
                # If i'm here, it's not JSON, it's not XML, let's scream
                # and raise the last context in this block (the XML exception)
                # The function hack is because Py2.7 messes up with exception
                # context otherwise.
                _LOGGER.critical("Wasn't XML not JSON, failing")
                raise_with_traceback(DecodeError, message="XML is invalid", response=response)
        raise DecodeError("Cannot deserialize content-type: {}".format(content_type))

    @classmethod
    def deserialize_from_http_generics(cls, response):
        # type: (Optional[Union[AnyStr, IO]], Mapping) -> Any
        """Deserialize from HTTP response.
        Use bytes and headers to NOT use any requests/aiohttp or whatever
        specific implementation.
        Headers will tested for "content-type"

        :param response: The HTTP response.
        :type response: ~azure.core.pipeline.transport.HttpResponse
        """
        # Try to use content-type from headers if available
        content_type = None
        if response.content_type:
            content_type = response.content_type[0].strip().lower()

        # Ouch, this server did not declare what it sent...
        # Let's guess it's JSON...
        # Also, since Autorest was considering that an empty body was a valid JSON,
        # need that test as well....
        else:
            content_type = "application/json"

        return cls.deserialize_from_text(response, content_type)

    def on_response(self, request, response, **kwargs):
        # type: (PipelineRequest, PipelineResponse, Any) -> None
        """Extract data from the body of a REST response object.
        This will load the entire payload in memory.
        Will follow Content-Type to parse.
        We assume everything is UTF8 (BOM acceptable).
        :param raw_data: Data to be processed.
        :param content_type: How to parse if raw_data is a string/bytes.
        :raises JSONDecodeError: If JSON is requested and parsing is impossible.
        :raises UnicodeDecodeError: If bytes is not UTF8
        :raises xml.etree.ElementTree.ParseError: If bytes is not valid XML
        """
        # If response was asked as stream, do NOT read anything and quit now
        if response.context.options.get("stream", True):
            return

        response.context[self.CONTEXT_NAME] = self.deserialize_from_http_generics(response.http_response)


class ProxyPolicy(SansIOHTTPPolicy):
    """A proxy policy.

    Dictionary mapping protocol or protocol and host to the URL of the proxy
    to be used on each Request.

    .. code-block:: python

        config = FooService.create_config()

        # Examples
        config.proxy_policy.proxies = {'http': 'foo.bar:3128'}
        config.proxy_policy.proxies= {'http://host.name': 'foo.bar:4012'}

    :param dict proxies: Dictionary mapping protocol or protocol and
     hostname to the URL of the proxy.
    :param bool proxies_use_env_settings: Use proxy settings from environment.
     Defaults to True.
    """
    def __init__(self, proxies=None, **kwargs):
        self.proxies = proxies
        self.use_env_settings = kwargs.pop('proxies_use_env_settings', True)
