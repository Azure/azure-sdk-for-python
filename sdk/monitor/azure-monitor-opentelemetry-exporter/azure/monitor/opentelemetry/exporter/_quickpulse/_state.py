# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import List

from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _LONG_PING_INTERVAL_SECONDS,
    _POST_INTERVAL_SECONDS,
    _SHORT_PING_INTERVAL_SECONDS,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import DocumentIngress


class _QuickpulseState(Enum):
    """Current state of quickpulse service.
    The numerical value represents the ping/post interval in ms for those states.
    """
    OFFLINE = 0
    PING_SHORT = _SHORT_PING_INTERVAL_SECONDS
    PING_LONG = _LONG_PING_INTERVAL_SECONDS
    POST_SHORT = _POST_INTERVAL_SECONDS


_GLOBAL_QUICKPULSE_STATE = _QuickpulseState.OFFLINE
_QUICKPULSE_DOCUMENTS: List[DocumentIngress] = []

def _set_global_quickpulse_state(state: _QuickpulseState):
    # pylint: disable=global-statement
    global _GLOBAL_QUICKPULSE_STATE
    _GLOBAL_QUICKPULSE_STATE = state


def _get_global_quickpulse_state() -> _QuickpulseState:
    return _GLOBAL_QUICKPULSE_STATE


def is_quickpulse_enabled() -> bool:
    return _get_global_quickpulse_state() is not _QuickpulseState.OFFLINE


def _is_ping_state() -> bool:
    return _get_global_quickpulse_state() in (
        _QuickpulseState.PING_SHORT,
        _QuickpulseState.PING_LONG
    )


def _is_post_state():
    return _get_global_quickpulse_state() is _QuickpulseState.POST_SHORT


def _append_quickpulse_document(document: DocumentIngress):
    # pylint: disable=global-statement,global-variable-not-assigned
    global _QUICKPULSE_DOCUMENTS
    # Limit risk of memory leak by limiting doc length to something manageable
    if len(_QUICKPULSE_DOCUMENTS) > 20:
        try:
            _QUICKPULSE_DOCUMENTS.pop(0)
        except IndexError:
            pass
    _QUICKPULSE_DOCUMENTS.append(document)


def _get_and_clear_quickpulse_documents() -> List[DocumentIngress]:
    # pylint: disable=global-statement
    global _QUICKPULSE_DOCUMENTS
    documents = list(_QUICKPULSE_DOCUMENTS)
    _QUICKPULSE_DOCUMENTS = []
    return documents
