from collections.abc import AsyncIterator

from io import BytesIO
from azure.core.exceptions import HttpResponseError
from ._requests_asyncio import AsyncioRequestsTransport
from azure.core.rest._http_response_impl_async import AsyncHttpResponseImpl
from pyodide.http import pyfetch  # pylint: disable=import-error
from pyodide import JsException  # pylint: disable=import-error
from requests.structures import CaseInsensitiveDict  # FIXME

class PyodideTransport(AsyncioRequestsTransport):
    """Implements a basic HTTP sender using the pyodide javascript fetch api."""

    async def send(self, request, **kwargs):  # type: ignore
        """Send request object according to configuration.

        :param request: The request object to be sent.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :return: An HTTPResponse object.
        :rtype: PyodideResponseTransport
        """
        endpoint = request.url
        request_headers = dict(request.headers)
        init = {
            "method": request.method,
            "headers": request_headers,
            "body": request.data,
            "files": request.files,
            "verify": kwargs.pop("connection_verify", self.connection_config.verify),
            "cert": kwargs.pop("connection_cert", self.connection_config.cert),
            "allow_redirects": False,
            **kwargs,
        }

        try:
            response = await pyfetch(endpoint, **init)
        except JsException as error:
            raise HttpResponseError(error, error=error)

        headers = CaseInsensitiveDict(response.js_response.headers)
        transport_response = PyodideTransportResponse(
            request=request,
            internal_response=response,
            block_size=self.connection_config.data_block_size,
            status_code=response.status,
            reason=response.status_text,
            content_type=headers.get("content-type"),
            headers=headers,
            stream_download_generator=PyodideStreamDownloadGenerator,
        )
        await transport_response.read()
        return transport_response


class PyodideTransportResponse(AsyncHttpResponseImpl):
    """Async response object for the pyodide transport."""

    async def close(self):
        """This is kinda weird but AsyncHttpResponseImpl assumed that
        the internal response is a `requests.Reponse` object (I think).

        Also, you can't really close connections at will using pyfetch.
        """
        self._is_closed = True

    async def load_body(self):
        """Load the body of the response."""
        if self._content is None:
            # This line can only be called once. Subsequent calls will raise an `OSError`.
            self._content = await self.internal_response.bytes()


class PyodideStreamDownloadGenerator(AsyncIterator):
    """Simple stream download generator that returns the contents of
    a request.
    """

    def __init__(self, pipeline, response: PyodideTransportResponse, **__) -> None:
        self.pipeline = pipeline
        self.block_size = response.block_size
        self.response = response
        self.stream = None
        self.done = False
    

    async def __anext__(self):
        """Assume that all the data we need is in `_internal_response`."""
        if self.stream is None:
            await self.response.load_body()
            self.stream = BytesIO(self.response.content)
            self.stream.seek(0)

        chunk = self.stream.read(self.block_size)
        if not chunk:
            self.done = True
            raise StopAsyncIteration()
        else:
            return chunk
