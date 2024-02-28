# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum

from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _LONG_PING_INTERVAL_SECONDS,
    _POST_INTERVAL_SECONDS,
    _SHORT_PING_INTERVAL_SECONDS,
)

class _QuickpulseState(Enum):
    """Current state of quickpulse service.
    The numerical value represents the ping/post interval in ms for those states.
    """

    PING_SHORT = _SHORT_PING_INTERVAL_SECONDS
    PING_LONG = _LONG_PING_INTERVAL_SECONDS
    POST_SHORT = _POST_INTERVAL_SECONDS


_GLOBAL_QUICKPULSE_STATE = _QuickpulseState.PING_SHORT


def _set_global_quickpulse_state(state: _QuickpulseState):
    global _GLOBAL_QUICKPULSE_STATE
    _GLOBAL_QUICKPULSE_STATE = state


def _get_global_quickpulse_state() -> _QuickpulseState:
    return _GLOBAL_QUICKPULSE_STATE
