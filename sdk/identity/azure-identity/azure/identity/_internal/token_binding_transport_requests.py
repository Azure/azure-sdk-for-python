# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Requests transport class for WorkloadIdentityCredential with token proxy support.
"""
import ssl
from typing import Any, Optional

from requests.adapters import HTTPAdapter
from requests import Session
from azure.core.pipeline.transport import (  # pylint: disable=non-abstract-transport-import, no-name-in-module
    RequestsTransport,
)
from azure.core.rest import HttpRequest

from .token_binding_transport_mixin import TokenBindingTransportMixin


class SNIAdapter(HTTPAdapter):
    """A custom HTTPAdapter that allows setting a custom SNI hostname."""

    def __init__(self, server_hostname: Optional[str], ca_data: Optional[str], **kwargs: Any) -> None:
        self.server_hostname = server_hostname
        self.ca_data = ca_data
        super().__init__(**kwargs)

    def init_poolmanager(self, connections: int, maxsize: int, block: bool = False, **pool_kwargs: Any) -> None:
        if self.server_hostname:
            pool_kwargs["server_hostname"] = self.server_hostname
        pool_kwargs["ssl_context"] = ssl.create_default_context(cadata=self.ca_data)
        super().init_poolmanager(connections, maxsize, block, **pool_kwargs)


class CustomRequestsTransport(TokenBindingTransportMixin, RequestsTransport):
    """Custom RequestsTransport with SNI and CA certificate support for WorkloadIdentityCredential."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.session: Optional[Session] = None
        super().__init__(*args, **kwargs)
        self._update_adaptor()

    def _update_adaptor(self) -> None:
        """Update the session's adapter with the current SNI and CA data."""
        if not self.session:
            self.session = Session()

        adapter = SNIAdapter(self._sni, self._ca_data)
        self.session.mount("https://", adapter)

    def send(self, request: HttpRequest, **kwargs: Any) -> Any:
        self._update_request_url(request)

        # Check if CA file has changed and reload ca_data if needed
        if self._ca_file and self._has_ca_file_changed():
            self._load_ca_file_to_data()
            # If ca_data was updated, recreate SSL context with the new data
            if self._ca_data:
                self._update_adaptor()
        return super().send(request, **kwargs)
