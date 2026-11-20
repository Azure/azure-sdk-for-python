# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Capability advertisement and negotiation shared by both SDK clients."""

from __future__ import annotations

from collections.abc import Mapping

_CAPABILITIES_REQUEST_HEADER = "X-Loom-Client-Capabilities"


class _AdvertisedCapabilities:
    """Capability tokens advertised by the SDK."""

    COMPLETION_FEED = "use_completion_feed"


class _NegotiatedCapabilityHeaders:
    """Service response headers for negotiated capabilities."""

    COMPLETION_FEED = "x-loom-use-completion-feed"


def _completion_feed_negotiated(headers: Mapping[str, str]) -> bool:
    return (
        next(
            (value for key, value in headers.items() if key.lower() == _NegotiatedCapabilityHeaders.COMPLETION_FEED),
            None,
        )
        == "true"
    )
