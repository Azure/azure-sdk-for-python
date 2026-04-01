# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Tuple
from urllib.parse import urlparse


# Allowed recording endpoint host suffixes.
# These are the only domains permitted for recording URLs to prevent credential exfiltration.
ALLOWED_HOST_SUFFIXES: Tuple[str, ...] = (
    ".asm.skype.com",
    ".asyncgw.teams.microsoft.com",
    ".gov.teams.microsoft.us",
)


def validate_recording_url(recording_url: str, parameter_name: str) -> None:
    """
    Validate that a recording URL points to Azure Communication Services
    endpoint before credentials are attached.
    This prevents credential exfiltration via SSRF attacks.

    :param recording_url: The recording URL to validate.
    :type recording_url: str
    :param parameter_name: The parameter name for exception messages.
    :type parameter_name: str
    :raises TypeError: If the recording URL is None or empty.
    :raises ValueError: If the recording URL is not a valid absolute HTTPS URI or not from an allowed domain.
    """
    if not recording_url:
        raise TypeError(f"{parameter_name} cannot be null or undefined.")

    parsed_url = urlparse(recording_url)

    # Validate it's a valid absolute URI
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError(f"{parameter_name} must be a valid absolute URI.")

    # Ensure the URL uses HTTPS
    if parsed_url.scheme.lower() != "https":
        raise ValueError(f"{parameter_name} must use HTTPS scheme for security.")

    host = parsed_url.hostname
    if not host:
        raise ValueError(f"{parameter_name} must have a valid hostname.")

    host_lower = host.lower()

    # Check against allowed suffixes
    is_valid_endpoint = any(host_lower.endswith(suffix) for suffix in ALLOWED_HOST_SUFFIXES)

    if not is_valid_endpoint:
        raise ValueError(
            f"{parameter_name} host '{host}' is not a valid Azure Communication Services recording endpoint. "
            "Only URLs pointing to *.asm.skype.com, *.asyncgw.teams.microsoft.com are allowed."
        )
