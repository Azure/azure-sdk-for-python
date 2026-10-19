# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import re
from dataclasses import dataclass
from ipaddress import IPv6Address
from urllib.parse import urlsplit

from opentelemetry.util.types import Attributes

from azure.monitor.opentelemetry.exporter._constants import (
    _MICROSOFT_INGESTION_AUTH,
    _MICROSOFT_INGESTION_ENDPOINT,
    _MICROSOFT_INSTRUMENTATION_KEY,
    _MICROSOFT_MULTI_ENDPOINT_CLOUD_ROLE,
)

_MAX_INSTRUMENTATION_KEY_LENGTH = 200
_MAX_INGESTION_ENDPOINT_LENGTH = 2048


@dataclass(frozen=True)
class _Route:
    """Validated per-item routing metadata, separate from its transport grouping key."""

    instrumentation_key: str
    ingestion_endpoint: str
    cloud_role: str
    is_aad: bool

    @property
    def transport_key(self) -> tuple[str, bool]:
        """Group by endpoint and authentication, not instrumentation key or cloud role.

        :return: The normalized ingestion endpoint and AAD flag.
        :rtype: tuple[str, bool]
        """
        return self.ingestion_endpoint, self.is_aad


def _get_instrumentation_key(attributes: Attributes) -> str:
    """Validate a routed key independently of connection-string UUID validation.

    :param attributes: The telemetry item's attributes.
    :type attributes: ~opentelemetry.util.types.Attributes
    :return: The trimmed instrumentation key.
    :rtype: str
    :raises ValueError: If the key is missing, invalid, or longer than 200 characters.
    """
    key = attributes.get(_MICROSOFT_INSTRUMENTATION_KEY) if attributes else None
    if not isinstance(key, str):
        raise ValueError("Routing instrumentation key must be a nonempty string.")
    if len(key) > _MAX_INSTRUMENTATION_KEY_LENGTH:
        raise ValueError("Routing instrumentation key must not exceed 200 characters.")
    key = key.strip()
    if not key:
        raise ValueError("Routing instrumentation key must be a nonempty string.")
    return key


def _get_ingestion_endpoint(attributes: Attributes) -> str:
    """Validate a trusted HTTPS destination and normalize its route key.

    IDNA validation and conversion are left to the HTTP transport.

    :param attributes: The telemetry item's attributes.
    :type attributes: ~opentelemetry.util.types.Attributes
    :return: The normalized ingestion endpoint with a trailing slash.
    :rtype: str
    :raises ValueError: If the endpoint is missing, invalid, or longer than 2048 characters.
    """
    endpoint = attributes.get(_MICROSOFT_INGESTION_ENDPOINT) if attributes else None
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise ValueError("Routing ingestion endpoint must be a nonempty string.")
    if len(endpoint) > _MAX_INGESTION_ENDPOINT_LENGTH:
        raise ValueError("Routing ingestion endpoint must not exceed 2048 characters.")
    endpoint = endpoint.strip()
    try:
        if any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in endpoint) or "\\" in endpoint:
            raise ValueError("Invalid URL characters.")
        parsed = urlsplit(endpoint)
        host = parsed.hostname
        if parsed.scheme != "https" or not host or "@" in parsed.netloc or "?" in endpoint or "#" in endpoint:
            raise ValueError("Invalid HTTPS destination.")
        authority_match = re.fullmatch(r"(\[[0-9a-f:.]+\]|[^\[\]:]+)(?::[0-9]+)?", parsed.netloc, re.IGNORECASE)
        if not authority_match:
            raise ValueError("Invalid URL authority.")
        port = parsed.port
        # parsed.hostname lowercases Unicode, which can change its subsequent IDNA conversion.
        authority = _normalize_endpoint_host(authority_match.group(1))
        if port is not None and port != 443:
            authority += f":{port}"
        return f"https://{authority}{parsed.path.rstrip('/')}/"
    except ValueError:
        raise ValueError(
            "Routing ingestion endpoint must be an absolute HTTPS URL without credentials, query, or fragment."
        ) from None


def _normalize_endpoint_host(host: str) -> str:
    if host.startswith("["):
        return f"[{IPv6Address(host[1:-1]).compressed}]"
    host = host.rstrip(".")
    if not host or any(char.isascii() and not (char.isalnum() or char in "._-") for char in host):
        raise ValueError("Invalid URL host.")
    return host.lower() if host.isascii() else host


def _get_cloud_role(attributes: Attributes) -> str:
    """Resolve a per-item cloud role without falling back to the host resource.

    :param attributes: The telemetry item's attributes.
    :type attributes: ~opentelemetry.util.types.Attributes
    :return: The trimmed role, or ``unknown_service`` for missing, blank, or non-string values.
    :rtype: str
    """
    role = attributes.get(_MICROSOFT_MULTI_ENDPOINT_CLOUD_ROLE) if attributes else None
    if not isinstance(role, str):
        return "unknown_service"
    return role.strip() or "unknown_service"


def _is_aad_route(attributes: Attributes) -> bool:
    """Read the explicit per-item AAD marker; this does not validate credentials.

    :param attributes: The telemetry item's attributes.
    :type attributes: ~opentelemetry.util.types.Attributes
    :return: Whether the authentication value is a trimmed, case-insensitive ``aad`` string.
    :rtype: bool
    """
    auth = attributes.get(_MICROSOFT_INGESTION_AUTH) if attributes else None
    return isinstance(auth, str) and auth.strip().lower() == "aad"


def _get_route(attributes: Attributes) -> _Route:
    """Read one item's route without falling back to exporter-level settings.

    :param attributes: The telemetry item's attributes.
    :type attributes: ~opentelemetry.util.types.Attributes
    :return: An immutable snapshot of the validated routing metadata.
    :rtype: ~azure.monitor.opentelemetry.exporter._routing._Route
    :raises ValueError: If either required routing attribute is missing or invalid.
    """
    return _Route(
        instrumentation_key=_get_instrumentation_key(attributes),
        ingestion_endpoint=_get_ingestion_endpoint(attributes),
        cloud_role=_get_cloud_role(attributes),
        is_aad=_is_aad_route(attributes),
    )
