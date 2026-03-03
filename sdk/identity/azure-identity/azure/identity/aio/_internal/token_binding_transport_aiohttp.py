# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Aiohttp transport class for the asynchronous WorkloadIdentityCredential with token proxy support.
"""
import ssl
from typing import Any

from azure.core.pipeline.transport import (  # pylint: disable=non-abstract-transport-import, no-name-in-module
    AioHttpTransport,
)
from azure.core.rest import HttpRequest

from ..._internal.token_binding_transport_mixin import TokenBindingTransportMixin


class CustomAioHttpTransport(TokenBindingTransportMixin, AioHttpTransport):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ssl_context = ssl.create_default_context(cadata=self._ca_data)

    async def send(self, request: HttpRequest, **kwargs: Any) -> Any:
        self._update_request_url(request)
        kwargs.setdefault("server_hostname", self._sni)

        # Check if CA file has changed and reload ca_data if needed
        if self._ca_file and self._has_ca_file_changed():
            self._load_ca_file_to_data()
            # If ca_data was updated, recreate SSL context with the new data
            if self._ca_data:
                self._ssl_context = ssl.create_default_context(cadata=self._ca_data)

        kwargs.setdefault("ssl", self._ssl_context)
        return await super().send(request, **kwargs)
