# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Asyncio Requests transport class for the asynchronous WorkloadIdentityCredential with token proxy support.
"""
from typing import Any, Optional

from requests import Session
from azure.core.pipeline.transport import (  # pylint: disable=non-abstract-transport-import, no-name-in-module
    AsyncioRequestsTransport,
)
from azure.core.rest import HttpRequest

from ..._internal.token_binding_transport_mixin import TokenBindingTransportMixin
from ..._internal.token_binding_transport_requests import SNIAdapter


class CustomAsyncioRequestsTransport(TokenBindingTransportMixin, AsyncioRequestsTransport):

    def __init__(self, *args, **kwargs):
        self.session: Optional[Session] = None
        super().__init__(*args, **kwargs)
        self._update_adaptor()

    def _update_adaptor(self) -> None:
        """Update the session's adapter with the current SNI and CA data."""
        if not self.session:
            self.session = Session()

        adapter = SNIAdapter(self._sni, self._ca_data)
        self.session.mount("https://", adapter)

    async def send(self, request: HttpRequest, **kwargs: Any) -> Any:
        self._update_request_url(request)

        # Check if CA file has changed and reload ca_data if needed
        if self._ca_file and self._has_ca_file_changed():
            self._load_ca_file_to_data()
            # If ca_data was updated, recreate SSL context with the new data
            if self._ca_data:
                self._update_adaptor()

        return await super().send(request, **kwargs)
