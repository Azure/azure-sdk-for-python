# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
from typing import Any

from aiohttp import TCPConnector, ClientRequest, tracing, ClientTimeout, ClientConnectorError, client_proto


class ProxiedTCPConnector(TCPConnector):
    """
    A TCP connector that proxies all connections through a specified host and port.

    This class extends TrackedTCPConnector to override connection behavior,
    routing all traffic through a specified proxy server using non-encrypted http.
    """

    def __init__(
            self,
            *,
            proxy_host: str,
            proxy_port: int,
            **kwargs: Any,
    ) -> None:
        """
        Initialize the ProxiedTCPConnector.

        Args:
            proxy_host (str): The hostname of the proxy server.
            proxy_port (int): The port number of the proxy server.
            **kwargs: Additional keyword arguments passed to the base TCPConnector.
        """
        super().__init__(**kwargs)
        self.__proxy_host = proxy_host
        self.__proxy_port = proxy_port

    async def _create_direct_connection(
            self,
            req: ClientRequest,
            traces: list[tracing.Trace],
            timeout: ClientTimeout,
            *,
            client_error: type[Exception] = ClientConnectorError,
    ) -> tuple[asyncio.Transport, client_proto.ResponseHandler]:
        """Override host, port, and schema to use proxy"""
        req.url = (
            req.url.with_host(self.__proxy_host).with_port(self.__proxy_port).with_scheme("http")
        )
        return await super()._create_direct_connection(
            req,
            traces,
            timeout,
            client_error=client_error,
        )