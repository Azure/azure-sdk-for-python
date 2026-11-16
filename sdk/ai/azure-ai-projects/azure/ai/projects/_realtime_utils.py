# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Shared transport-option helpers for the handwritten realtime clients."""

from typing import Optional, Union
from urllib.parse import unquote_plus, urlsplit

from .models import VoiceAgentTransport


def _normalize_transport(transport: Optional[Union[str, VoiceAgentTransport]]) -> Optional[str]:
    """Normalize the typed transport option without restricting future service values.

    :param transport: The optional transport selector.
    :type transport: str or ~azure.ai.projects.models.VoiceAgentTransport or None
    :return: The wire value, or None when the option is omitted.
    :rtype: str or None
    :raises TypeError: If the selector is neither a string nor a transport enum.
    """
    if transport is None:
        return None
    if not isinstance(transport, str):
        raise TypeError("transport must be a string or VoiceAgentTransport.")
    return transport.value if isinstance(transport, VoiceAgentTransport) else transport


def _without_transport_query(url: str) -> str:
    """Remove transport parameters before applying an explicit typed selection.

    Preserve unrelated query encodings and repeated values.

    :param str url: The connection URL.
    :return: The URL without existing transport parameters.
    :rtype: str
    """
    parsed = urlsplit(url)
    query = "&".join(part for part in parsed.query.split("&") if unquote_plus(part.partition("=")[0]) != "transport")
    return parsed._replace(query=query).geturl()
