# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Any, Optional
from urllib.parse import urlparse
from weakref import ReferenceType

from azure.core.pipeline import PipelineResponse, policies

from azure.monitor.opentelemetry.exporter._quickpulse._constants import _QUICKPULSE_REDIRECT_HEADER_NAME
from azure.monitor.opentelemetry.exporter._quickpulse._generated import QuickpulseClient


# Quickpulse endpoint handles redirects via header instead of status codes
# We use a custom RedirectPolicy to handle this use case
# pylint: disable=protected-access
class _QuickpulseRedirectPolicy(policies.RedirectPolicy):

    def __init__(self, **kwargs: Any) -> None:
        # Weakref to QuickPulseClient instance
        self._qp_client_ref: Optional[ReferenceType[QuickpulseClient]] = None
        super().__init__(**kwargs)

    # Gets the redirect location from header
    def get_redirect_location(self, response: PipelineResponse) -> Optional[str]:
        redirect_location = response.http_response.headers.get(_QUICKPULSE_REDIRECT_HEADER_NAME)
        qp_client = None
        if redirect_location:
            redirected_url = urlparse(redirect_location)
            if redirected_url.scheme and redirected_url.netloc:
                if self._qp_client_ref:
                    qp_client = self._qp_client_ref()
                if qp_client and qp_client._client:
                    # Set new endpoint to redirect location
                    qp_client._client._base_url = f"{redirected_url.scheme}://{redirected_url.netloc}"
        return redirect_location  # type: ignore
