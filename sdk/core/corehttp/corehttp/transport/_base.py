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
from __future__ import annotations
import abc
import logging
import time
from typing import Generic, TypeVar, Any, ContextManager, Union, Optional, MutableMapping, TYPE_CHECKING

if TYPE_CHECKING:
    from ..rest import HttpResponse

HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")

_LOGGER = logging.getLogger(__name__)


def _create_connection_config(  # pylint: disable=unused-argument
    *,
    connection_timeout: float = 300,
    read_timeout: float = 300,
    connection_verify: Union[bool, str] = True,
    connection_cert: Optional[str] = None,
    connection_data_block_size: int = 4096,
    **kwargs: Any,
) -> MutableMapping[str, Any]:
    """HTTP transport connection configuration settings.

    :keyword float connection_timeout: A single float in seconds for the connection timeout. Defaults to 300 seconds.
    :keyword float read_timeout: A single float in seconds for the read timeout. Defaults to 300 seconds.
    :keyword connection_verify: SSL certificate verification. Enabled by default. Set to False to disable,
     alternatively can be set to the path to a CA_BUNDLE file or directory with certificates of trusted CAs.
    :paramtype connection_verify: bool or str
    :keyword str connection_cert: Client-side certificates. You can specify a local cert to use as client side
     certificate, as a single file (containing the private key and the certificate) or as a tuple of both files' paths.
    :keyword int connection_data_block_size: The block size of data sent over the connection. Defaults to 4096 bytes.

    :return: The connection configuration.
    :rtype: MutableMapping[str, any]
    """
    return {
        "connection_timeout": connection_timeout,
        "read_timeout": read_timeout,
        "connection_verify": connection_verify,
        "connection_cert": connection_cert,
        "data_block_size": connection_data_block_size,
    }


def _handle_non_stream_rest_response(response: HttpResponse) -> None:
    """Handle reading and closing of non stream rest responses.
    For our new rest responses, we have to call .read() and .close() for our non-stream
    responses. This way, we load in the body for users to access.

    :param response: The response to read and close.
    :type response: ~corehttp.rest.HttpResponse
    """
    try:
        response.read()
        response.close()
    except Exception as exc:
        response.close()
        raise exc


class HttpTransport(ContextManager["HttpTransport"], abc.ABC, Generic[HTTPRequestType, HTTPResponseType]):
    """An http sender ABC."""

    @abc.abstractmethod
    def send(self, request: HTTPRequestType, **kwargs: Any) -> HTTPResponseType:
        """Send the request using this HTTP sender.

        :param request: The pipeline request object
        :type request: ~corehttp.rest.HTTPRequest
        :return: The pipeline response object.
        :rtype: ~corehttp.rest.HttpResponse
        """

    @abc.abstractmethod
    def open(self) -> None:
        """Assign new session if one does not already exist."""

    @abc.abstractmethod
    def close(self) -> None:
        """Close the session if it is not externally owned."""

    def sleep(self, duration: float) -> None:
        """Sleep for the specified duration.

        You should always ask the transport to sleep, and not call directly
        the stdlib. This is mostly important in async, as the transport
        may not use asyncio but other implementations like trio and they have their own
        way to sleep, but to keep design
        consistent, it's cleaner to always ask the transport to sleep and let the transport
        implementor decide how to do it.

        :param float duration: The number of seconds to sleep.
        """
        time.sleep(duration)
