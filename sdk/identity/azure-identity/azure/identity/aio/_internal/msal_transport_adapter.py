# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Adapter to substitute an async azure-core pipeline for Requests in MSAL application token acquisition methods."""

import asyncio
import atexit
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Iterable, Optional
    from azure.core.pipeline.policies import AsyncHTTPPolicy
    from azure.core.pipeline.transport import AsyncHttpTransport

from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import AsyncRetryPolicy, NetworkTraceLoggingPolicy
from azure.core.pipeline.transport import AioHttpTransport, HttpRequest
from azure.core.configuration import Configuration

from azure.identity._internal import MsalTransportResponse


class AsyncMsalTransportAdapter:
    """Wraps an async azure-core pipeline with the shape of a (synchronous) Requests Session"""

    def __init__(
        self,
        config: "Optional[Configuration]" = None,
        policies: "Optional[Iterable[AsyncHTTPPolicy]]" = None,
        transport: "Optional[AsyncHttpTransport]" = None,
        **kwargs: "Any"
    ) -> None:

        config = config or self._create_config(**kwargs)
        policies = policies or [config.retry_policy, config.logging_policy]
        self._transport = transport or AioHttpTransport(configuration=config)
        atexit.register(self._close_transport_session)  # prevent aiohttp warnings
        self._pipeline = AsyncPipeline(transport=self._transport, policies=policies)

        self.loop = None  # type: asyncio.AbstractEventLoop

    def _close_transport_session(self) -> None:
        """If transport has a 'close' method, invoke it."""

        close = getattr(self._transport, "close", None)
        if not callable(close):
            return

        if asyncio.iscoroutinefunction(close):
            # we expect no loop is running because this method should be called only when the interpreter is exiting
            asyncio.new_event_loop().run_until_complete(close())
        else:
            close()

    def get(
        self,
        url: str,
        headers: "Optional[Dict[str, str]]" = None,
        params: "Optional[Dict[str, str]]" = None,
        proxies: "Optional[Dict[str, str]]" = None,
        timeout: "Optional[float]" = None,
        verify: "Optional[bool]" = None,
        **kwargs: "Any"
    ) -> MsalTransportResponse:

        request = HttpRequest("GET", url, headers=headers)
        if params:
            request.format_parameters(params)

        loop = kwargs.pop("loop", None) or self.loop
        future = asyncio.run_coroutine_threadsafe(
            self._pipeline.run(request, connection_timeout=timeout, connection_verify=verify, **kwargs), loop
        )
        response = future.result(timeout=timeout)

        return MsalTransportResponse(response)

    def post(
        self,
        url: str,
        data: "Any" = None,
        headers: "Optional[Dict[str, str]]" = None,
        params: "Optional[Dict[str, str]]" = None,
        timeout: "Optional[float]" = None,
        verify: "Optional[bool]" = None,
        **kwargs: "Any"
    ) -> MsalTransportResponse:

        request = HttpRequest("POST", url, headers=headers)
        if params:
            request.format_parameters(params)
        if data:
            request.headers["Content-Type"] = "application/x-www-form-urlencoded"
            request.set_formdata_body(data)

        loop = kwargs.pop("loop", None) or self.loop
        future = asyncio.run_coroutine_threadsafe(
            self._pipeline.run(request, connection_timeout=timeout, connection_verify=verify, **kwargs), loop
        )
        response = future.result(timeout=timeout)

        return MsalTransportResponse(response)

    @staticmethod
    def _create_config(**kwargs: "Any") -> Configuration:
        config = Configuration(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = AsyncRetryPolicy(**kwargs)
        return config
