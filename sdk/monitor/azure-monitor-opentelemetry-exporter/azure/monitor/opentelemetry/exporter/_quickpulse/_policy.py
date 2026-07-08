# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import logging
from typing import Any, Optional
from urllib.parse import urlparse
from weakref import ReferenceType

from azure.core.pipeline import PipelineResponse, policies

from azure.monitor.opentelemetry.exporter._constants import (
    _ALLOWED_REDIRECT_DOMAIN_SUFFIXES,
)
from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _QUICKPULSE_REDIRECT_HEADER_NAME,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.livemetrics import (
    LiveMetricsClient,
)

_logger = logging.getLogger(__name__)


def _is_redirect_target_allowed(netloc: str) -> bool:
    """Validate that the redirect target host belongs to a known Azure Monitor domain.

    :param str netloc: The network location (host:port) from the parsed redirect URL.
    :return: True if the host is in an allowed Azure Monitor domain, False otherwise.
    :rtype: bool
    """
    # Use urlparse to safely extract the hostname, which handles port stripping
    # and detects userinfo (username/password) that could be used to spoof the host.
    parsed = urlparse(f"//{netloc}")
    if parsed.username is not None or parsed.password is not None:
        return False
    host = parsed.hostname
    if host is None:
        return False
    return any(host.endswith(suffix) for suffix in _ALLOWED_REDIRECT_DOMAIN_SUFFIXES)


# Quickpulse endpoint handles redirects via header instead of status codes
# We use a custom RedirectPolicy to handle this use case
# pylint: disable=protected-access
class _QuickpulseRedirectPolicy(policies.RedirectPolicy):
    def __init__(self, **kwargs: Any) -> None:
        # Weakref to LiveMetricsClient instance
        self._qp_client_ref: Optional[ReferenceType[LiveMetricsClient]] = None
        super().__init__(**kwargs)

    # Gets the redirect location from header
    def get_redirect_location(self, response: PipelineResponse) -> Optional[str]:
        redirect_location = response.http_response.headers.get(_QUICKPULSE_REDIRECT_HEADER_NAME)
        qp_client = None
        if redirect_location:
            redirected_url = urlparse(redirect_location)
            if redirected_url.scheme and redirected_url.netloc:
                # Only allow HTTPS redirects to trusted Azure Monitor domains
                if redirected_url.scheme.lower() != "https":
                    _logger.warning(
                        "QuickPulse redirect rejected: non-HTTPS scheme '%s' in redirect target.",
                        redirected_url.scheme,
                    )
                    return None
                if not _is_redirect_target_allowed(redirected_url.netloc):
                    _logger.warning(
                        "QuickPulse redirect rejected: host '%s' is not in the allowed domain list.",
                        redirected_url.netloc,
                    )
                    return None
                if self._qp_client_ref:
                    qp_client = self._qp_client_ref()
                if qp_client and qp_client._client:
                    # Set new endpoint to redirect location
                    qp_client._client._base_url = f"{redirected_url.scheme}://{redirected_url.netloc}"
        return redirect_location  # type: ignore
