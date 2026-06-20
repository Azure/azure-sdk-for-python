# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore cafile
import os
import urllib.parse
from typing import Optional, Any

from azure.core.rest import HttpRequest


class TokenBindingTransportMixin:
    """Mixin class providing URL validation, CA file tracking, and proxy URL functionality for transport classes."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize CA file tracking and proxy attributes."""
        self._ca_file = kwargs.pop("ca_file", None)
        self._ca_data = kwargs.pop("ca_data", None)
        self._proxy_endpoint = kwargs.pop("proxy_endpoint", None)
        self._sni = kwargs.pop("sni", None)

        self._ca_file_mtime: Optional[float] = None

        if self._ca_file and self._ca_data:
            raise ValueError("Both ca_file and ca_data are set. Only one should be set")

        if self._proxy_endpoint:
            self._validate_url(self._proxy_endpoint)

        # If we have a ca_file, read it once and store as ca_data
        if self._ca_file:
            self._load_ca_file_to_data()

        super().__init__()

    def _validate_url(self, url: str) -> None:
        """Validate that a URL meets security requirements for HTTPS connections.

        :param url: The URL to validate.
        :type url: str
        :raises ValueError: If the URL does not meet security requirements.
        """
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.scheme != "https":
            raise ValueError(f"Endpoint URL ({url}) must use the 'https' scheme. Got '{parsed_url.scheme}' instead.")
        if parsed_url.username or parsed_url.password:
            raise ValueError(f"Endpoint URL ({url}) must not contain username or password.")
        if parsed_url.fragment:
            raise ValueError(f"Endpoint URL ({url}) must not contain a fragment.")
        if parsed_url.query:
            raise ValueError(f"Endpoint URL ({url}) must not contain query parameters.")

    def _load_ca_file_to_data(self) -> None:
        """Load CA file content into ca_data and track modification time.

        :raises ValueError: If the CA file is empty on first read.
        """
        try:
            with open(self._ca_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if the file is empty
            if not content:
                # If no prior ca_data exists (first read), fail
                if self._ca_data is None:
                    raise ValueError(f"CA file ({self._ca_file}) is empty. Cannot establish secure connection.")
                # If we had prior ca_data, keep it (mid-rotation scenario)
                return

            # File has content, update ca_data and tracking
            self._ca_data = content
            self._ca_file_mtime = os.path.getmtime(self._ca_file)
        except (OSError, IOError) as e:
            # If no prior ca_data exists (first read), fail
            if self._ca_data is None:
                raise ValueError(f"Failed to read CA file ({self._ca_file}): {e}") from e
            # If we can't read the file, keep existing ca_data but clear mtime
            # so we'll try to reload on the next change check
            self._ca_file_mtime = None

    def _has_ca_file_changed(self) -> bool:
        """Check if the CA file has changed since last load.

        :return: True if the CA file has changed, False otherwise.
        :rtype: bool
        """
        if not self._ca_file:
            return False

        if not os.path.exists(self._ca_file):
            # File was deleted, consider this a change if we had data before
            return self._ca_data is not None or self._ca_file_mtime is not None

        try:
            # Check modification time
            current_mtime = os.path.getmtime(self._ca_file)
            return self._ca_file_mtime != current_mtime
        except (OSError, IOError):
            # If we can't read the file stats, assume it changed
            return True

    def _update_request_url(self, request: HttpRequest) -> None:
        """Update the request URL to use proxy endpoint if configured.

        :param request: The HTTP request object to update.
        :type request: ~azure.core.rest.HttpRequest
        """
        if self._proxy_endpoint:
            parsed_request_url = urllib.parse.urlparse(request.url)
            parsed_proxy_url = urllib.parse.urlparse(self._proxy_endpoint)
            combined_path = parsed_proxy_url.path.rstrip("/") + "/" + parsed_request_url.path.lstrip("/")
            new_url = urllib.parse.urlunparse(
                (
                    parsed_proxy_url.scheme,
                    parsed_proxy_url.netloc,
                    combined_path,
                    parsed_request_url.params,
                    parsed_request_url.query,
                    parsed_request_url.fragment,
                )
            )
            request.url = new_url
