# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import re
from typing import Tuple
from urllib.parse import urlparse

from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import SansIOHTTPPolicy

# Allowed recording endpoint host suffixes.
# These are the only domains permitted for recording URLs to prevent credential exfiltration.
ALLOWED_HOST_SUFFIXES: Tuple[str, ...] = (
    ".asm.skype.com",
    ".asyncgw.teams.microsoft.com",
    ".ams.gov.teams.microsoft.us",
)


def _validate_url_characters(url: str, parameter_name: str) -> None:
    if any(char == "\\" or char.isspace() or ord(char) < 32 or 127 <= ord(char) <= 159 for char in url):
        raise ValueError(f"{parameter_name} must not contain backslashes, whitespace, or control characters.")


def validate_recording_url(recording_url: str, parameter_name: str) -> str:
    """
    Validate that a recording URL points to Azure Communication Services
    endpoint before credentials are attached.
    This prevents credential exfiltration via SSRF attacks.

    :param recording_url: The recording URL to validate.
    :type recording_url: str
    :param parameter_name: The parameter name for exception messages.
    :type parameter_name: str
    :return: The validated URL with a canonical ASCII authority.
    :rtype: str
    :raises TypeError: If the recording URL is None or empty.
    :raises ValueError: If the recording URL is not a valid absolute HTTPS URI or not from an allowed domain.
    """
    if not recording_url:
        raise TypeError(f"{parameter_name} cannot be null or undefined.")
    if not isinstance(recording_url, str):
        raise TypeError(f"{parameter_name} must be a string.")

    # Reject syntax that URL parsers may discard or interpret as a different authority.
    _validate_url_characters(recording_url, parameter_name)
    parsed_url = urlparse(recording_url)

    # Validate it's a valid absolute URI
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError(f"{parameter_name} must be a valid absolute URI.")

    # Ensure the URL uses HTTPS
    if parsed_url.scheme.lower() != "https":
        raise ValueError(f"{parameter_name} must use HTTPS scheme for security.")

    if "@" in parsed_url.netloc or not parsed_url.netloc.isascii():
        raise ValueError(f"{parameter_name} must have an ASCII hostname and must not contain user information.")

    host = parsed_url.hostname
    if not host:
        raise ValueError(f"{parameter_name} must have a valid hostname.")

    host_lower = host.lower()
    if len(host_lower) > 253 or not all(
        re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label) for label in host_lower.split(".")
    ):
        raise ValueError(f"{parameter_name} must have a valid DNS hostname.")

    port = parsed_url.port
    if ":" in parsed_url.netloc and not parsed_url.netloc.rsplit(":", 1)[1].isdigit():
        raise ValueError(f"{parameter_name} must have a valid port.")

    # Check against allowed suffixes
    is_valid_endpoint = any(host_lower.endswith(suffix) for suffix in ALLOWED_HOST_SUFFIXES)

    if not is_valid_endpoint:
        raise ValueError(
            f"{parameter_name} host '{host}' is not a valid Azure Communication Services recording endpoint. "
            "Only URLs pointing to *.asm.skype.com, *.asyncgw.teams.microsoft.com are allowed."
        )

    authority = host_lower if port is None else f"{host_lower}:{port}"
    return parsed_url._replace(scheme="https", netloc=authority).geturl()


class RecordingURLValidationPolicy(SansIOHTTPPolicy):
    """Validate recording destinations on every attempt, before authentication."""

    def on_request(self, request: PipelineRequest) -> None:
        parameter_name = request.context.options.pop("_recording_url_parameter_name", None)
        if parameter_name is not None:
            request.context["_recording_url_parameter_name"] = parameter_name
        parameter_name = request.context.get("_recording_url_parameter_name")
        if parameter_name:
            request.http_request.url = validate_recording_url(request.http_request.url, parameter_name)

    def on_response(self, request: PipelineRequest, response: PipelineResponse) -> None:
        parameter_name = request.context.get("_recording_url_parameter_name")
        location = response.http_response.headers.get("location")
        if parameter_name and location and response.http_response.status_code in (300, 301, 302, 303, 307, 308):
            # RedirectPolicy parses Location before the next on_request, potentially discarding controls.
            _validate_url_characters(location, parameter_name)
