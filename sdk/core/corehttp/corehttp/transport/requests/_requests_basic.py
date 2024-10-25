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
from typing import Optional, Union, TypeVar, cast, MutableMapping, TYPE_CHECKING
from urllib3.util.retry import Retry
from urllib3.exceptions import (
    ProtocolError,
    NewConnectionError,
    ConnectTimeoutError,
)
import requests  # pylint: disable=networking-import-outside-azure-core-transport

from ...exceptions import (
    ServiceRequestError,
    ServiceResponseError,
    IncompleteReadError,
    HttpResponseError,
)

from .._base import HttpTransport, _create_connection_config, _handle_non_stream_rest_response
from ._bigger_block_size_http_adapters import BiggerBlockSizeHTTPAdapter
from ...rest._requests_basic import RestRequestsTransportResponse

if TYPE_CHECKING:
    from ...rest import HttpRequest as RestHttpRequest, HttpResponse as RestHttpResponse

BaseErrorUnion = Union[
    ServiceRequestError,
    ServiceResponseError,
    IncompleteReadError,
    HttpResponseError,
]

PipelineType = TypeVar("PipelineType")

_LOGGER = logging.getLogger(__name__)


class RequestsTransport(HttpTransport):
    """Implements a basic requests HTTP sender.

    Since requests team recommends to use one session per requests, you should
    not consider this class as thread-safe, since it will use one Session
    per instance.

    In this simple implementation:
    - You provide the configured session if you want to, or a basic session is created.
    - All kwargs received by "send" are sent to session.request directly

    :keyword requests.Session session: Request session to use instead of the default one.
    :keyword bool session_owner: Decide if the session provided by user is owned by this transport. Default to True.
    :keyword bool use_env_settings: Uses proxy settings from environment. Defaults to True.
    """

    _protocols = ["http://", "https://"]

    def __init__(self, **kwargs) -> None:
        self.session = kwargs.get("session", None)
        self._session_owner = kwargs.get("session_owner", True)
        if not self._session_owner and not self.session:
            raise ValueError("session_owner cannot be False if no session is provided")
        self.connection_config = _create_connection_config(**kwargs)
        self._use_env_settings = kwargs.pop("use_env_settings", True)

    def __enter__(self) -> "RequestsTransport":
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def _init_session(self, session: requests.Session) -> None:
        """Init session level configuration of requests.

        This is initialization I want to do once only on a session.

        :param requests.Session session: The session object.
        """
        session.trust_env = self._use_env_settings
        disable_retries = Retry(total=False, redirect=False, raise_on_status=False)
        adapter = BiggerBlockSizeHTTPAdapter(max_retries=disable_retries)
        for p in self._protocols:
            session.mount(p, adapter)

    def open(self):
        if not self.session and self._session_owner:
            self.session = requests.Session()
            self._init_session(self.session)
        # pyright has trouble to understand that self.session is not None, since we raised at worst in the init
        self.session = cast(requests.Session, self.session)

    def close(self):
        if self._session_owner and self.session:
            self.session.close()
            self._session_owner = False
            self.session = None

    def send(
        self,
        request: "RestHttpRequest",
        *,
        stream: bool = False,
        proxies: Optional[MutableMapping[str, str]] = None,
        **kwargs
    ) -> "RestHttpResponse":
        """Send request object according to configuration.

        :param request: The request object to be sent.
        :type request:  ~corehttp.rest.HttpRequest
        :keyword bool stream: Defaults to False.
        :keyword MutableMapping proxies: dict of proxies to use based on protocol. Proxy is a dict (protocol, url).
        :return: An HTTPResponse object.
        :rtype: ~corehttp.rest.HttpResponse
        """
        self.open()
        response = None
        error: Optional[BaseErrorUnion] = None

        try:
            connection_timeout = kwargs.pop("connection_timeout", self.connection_config.get("connection_timeout"))

            if isinstance(connection_timeout, tuple):
                if "read_timeout" in kwargs:
                    raise ValueError("Cannot set tuple connection_timeout and read_timeout together")
                timeout = connection_timeout
            else:
                read_timeout = kwargs.pop("read_timeout", self.connection_config.get("read_timeout"))
                timeout = (connection_timeout, read_timeout)
            response = self.session.request(  # type: ignore
                request.method,
                request.url,
                headers=request.headers,
                data=request._data,  # pylint: disable=protected-access
                files=request._files,  # pylint: disable=protected-access
                verify=kwargs.pop("connection_verify", self.connection_config.get("connection_verify")),
                timeout=timeout,
                cert=kwargs.pop("connection_cert", self.connection_config.get("connection_cert")),
                allow_redirects=False,
                stream=stream,
                proxies=proxies,
                **kwargs
            )
            response.raw.enforce_content_length = True

        except (
            NewConnectionError,
            ConnectTimeoutError,
        ) as err:
            error = ServiceRequestError(err, error=err)
        except requests.exceptions.ReadTimeout as err:
            error = ServiceResponseError(err, error=err)
        except requests.exceptions.ConnectionError as err:
            if err.args and isinstance(err.args[0], ProtocolError):
                error = ServiceResponseError(err, error=err)
            else:
                error = ServiceRequestError(err, error=err)
        except requests.exceptions.ChunkedEncodingError as err:
            msg = err.__str__()
            if "IncompleteRead" in msg:
                _LOGGER.warning("Incomplete download: %s", err)
                error = IncompleteReadError(err, error=err)
            else:
                _LOGGER.warning("Unable to stream download: %s", err)
                error = HttpResponseError(err, error=err)
        except requests.RequestException as err:
            error = ServiceRequestError(err, error=err)

        if error:
            raise error

        retval: RestHttpResponse = RestRequestsTransportResponse(
            request=request,
            internal_response=response,
            block_size=self.connection_config.get("data_block_size"),
        )
        if not stream:
            _handle_non_stream_rest_response(retval)
        return retval
