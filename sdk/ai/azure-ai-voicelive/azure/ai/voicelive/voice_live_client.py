# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import logging
from copy import deepcopy
from typing import Any, Optional, Union, Dict, List, cast
from typing_extensions import Self

from azure.core import PipelineClient
from azure.core.credentials import TokenCredential
from azure.core.pipeline import policies
from azure.core.rest import HttpRequest, HttpResponse

from .voice_live_configuration import VoiceLiveClientConfiguration
from .connection import VoiceLiveConnectionManager, VoiceLiveConnection
from ._version import VERSION

logger = logging.getLogger(__name__)


class VoiceLiveClient:
    """VoiceClient for real-time audio communication using WebSockets.

    This client provides functionality for establishing WebSocket connections
    for real-time voice analysis and processing.

    :ivar endpoint: The endpoint URL for the VoiceLive service.
    :vartype endpoint: str
    :ivar api_version: API version to use for requests.
    :vartype api_version: str

    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword endpoint: Service host. Default value is "wss://voicelive.azure.com".
    :paramtype endpoint: str
    :keyword api_version: API version to use for requests. Default value is "2023-12-01-preview".
    :paramtype api_version: str
    :keyword transport: Transport type.
    :paramtype transport: ~azure.core.pipeline.transport.HttpTransport
    """

    def __init__(
        self, 
        credential: TokenCredential, 
        **kwargs: Any
    ) -> None:
        endpoint = kwargs.pop("endpoint", "wss://voicelive.azure.com")
        self._config = VoiceLiveClientConfiguration(credential=credential, endpoint=endpoint, **kwargs)
        
        # Create the base REST pipeline
        _policies = kwargs.pop("policies", None)
        if _policies is None:
            _policies = [
                policies.RequestIdPolicy(**kwargs),
                self._config.headers_policy,
                self._config.user_agent_policy,
                self._config.proxy_policy,
                policies.ContentDecodePolicy(**kwargs),
                self._config.redirect_policy,
                self._config.retry_policy,
                self._config.authentication_policy,
                self._config.custom_hook_policy,
                self._config.logging_policy,
                policies.DistributedTracingPolicy(**kwargs),
                policies.SensitiveHeaderCleanupPolicy(**kwargs) if self._config.redirect_policy else None,
                self._config.http_logging_policy,
            ]
        
        # Format endpoint URL
        _endpoint = "{endpoint}"
        
        self._client = PipelineClient(base_url=_endpoint, policies=_policies, **kwargs)
        self._websocket_connection = None
        self._connection_id = None
        
        # Public properties
        self.endpoint = self._config.endpoint
        self.api_version = self._config.api_version

    def connect(self, **kwargs: Any) -> VoiceLiveConnection:
        """Establishes a WebSocket connection to the VoiceLive service.
        
        This method establishes a real-time connection to the VoiceLive service
        for transmitting and receiving audio data. It returns a VoiceLiveConnection
        object that can be used to send and receive events.
        
        :keyword str connection_id: Optional identifier for the connection.
        :keyword Dict[str, str] additional_headers: Optional additional headers to include in the connection request.
        :keyword float connection_timeout: Optional timeout for connection establishment in seconds.
        :return: A connection object for interacting with the VoiceLive service.
        :rtype: ~azure.ai.voicelive.connection.VoiceLiveConnection
        :raises: ~azure.core.exceptions.ServiceRequestError if the connection cannot be established.
        """
        # Extract connection parameters from kwargs
        connection_id = kwargs.get("connection_id", None)
        additional_headers = kwargs.get("additional_headers", {})
        connection_timeout = kwargs.get("connection_timeout", 30.0)
        
        # Create a connection manager
        connection_manager = VoiceLiveConnectionManager(
            credential=self._config.credential,
            endpoint=self.endpoint,
            api_version=self.api_version,
            connection_id=connection_id,
            additional_headers=additional_headers,
            connection_timeout=connection_timeout
        )
        
        # Establish connection and return the connection object
        connection = connection_manager.__enter__()
        self._websocket_connection = connection
        self._connection_id = connection.connection_id
        
        logger.info(f"WebSocket connection established with ID: {self._connection_id}")
        return connection

    def disconnect(self) -> None:
        """Closes the active WebSocket connection.
        
        This method gracefully closes any active WebSocket connection.
        """
        if self._websocket_connection:
            logger.info(f"Closing WebSocket connection with ID: {self._connection_id}")
            self._websocket_connection.close()
            self._websocket_connection = None
            self._connection_id = None

    def send_request(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        """Runs the network request through the client's chained policies.

        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest("GET", "https://www.example.org/")
        <HttpRequest [GET], url: 'https://www.example.org/'>
        >>> response = client.send_request(request)
        <HttpResponse: 200 OK>

        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.HttpResponse
        """
        request_copy = deepcopy(request)
        path_format_arguments = {
            "endpoint": self._config.endpoint,
        }

        request_copy.url = self._client.format_url(request_copy.url, **path_format_arguments)
        return self._client.send_request(request_copy, **kwargs)  # type: ignore

    def close(self) -> None:
        """Close the client session.
        
        This will close any active WebSocket connections and the underlying HTTP client.
        """
        self.disconnect()
        self._client.close()

    def __enter__(self) -> Self:
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._client.__exit__(*exc_details)