# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Public platform HTTP header / wire-contract constants.

These constants form the wire contract between the Foundry platform, agent
containers, and downstream storage services. They are shared across the
AgentServer protocol packages (e.g. ``azure-ai-agentserver-responses`` and
``azure-ai-agentserver-invocations``), which compose on top of this core
package; this module is the supported public surface for those constants.

See the module-level documentation of each constant for its wire semantics.
"""
from __future__ import annotations

from ._platform_headers import (
    APIM_REQUEST_ID,
    CLIENT_HEADER_PREFIX,
    CLIENT_REQUEST_ID,
    ERROR_DETAIL,
    ERROR_SOURCE,
    FOUNDRY_CALL_ID,
    MAX_ERROR_DETAIL_LENGTH,
    PLATFORM_ERROR_TAG,
    REQUEST_ID,
    SERVER_VERSION,
    SESSION_ID,
    TRACEPARENT,
    USER_ID,
)

__all__ = [
    "APIM_REQUEST_ID",
    "CLIENT_HEADER_PREFIX",
    "CLIENT_REQUEST_ID",
    "ERROR_DETAIL",
    "ERROR_SOURCE",
    "FOUNDRY_CALL_ID",
    "MAX_ERROR_DETAIL_LENGTH",
    "PLATFORM_ERROR_TAG",
    "REQUEST_ID",
    "SERVER_VERSION",
    "SESSION_ID",
    "TRACEPARENT",
    "USER_ID",
]
