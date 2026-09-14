# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Client-owned item defaults and response headers, independent of transport."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from azure.core.utils import CaseInsensitiveDict


@dataclass(frozen=True)
class ItemClientDefaults:
    """Immutable Python request defaults captured at client construction."""

    no_response_on_write: bool = False


@dataclass
class ResponseHeaderState:
    """Latest headers recorded for a client, replaced as responses are parsed.

    This is not a response history or per-operation storage. Concurrent calls
    share this state; use a result's headers or response hook for a specific call.
    It owns no transport or service metadata cache.
    """

    last_response_headers: CaseInsensitiveDict = field(default_factory=CaseInsensitiveDict)


@dataclass(frozen=True)
class ItemClientContext:
    """Passed directly from client to database to container, never via a connection."""

    backend: Any
    defaults: ItemClientDefaults = field(default_factory=ItemClientDefaults)
    response_state: ResponseHeaderState = field(default_factory=ResponseHeaderState)
