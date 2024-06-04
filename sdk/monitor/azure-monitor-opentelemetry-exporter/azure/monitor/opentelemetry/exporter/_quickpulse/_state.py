# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datetime import datetime
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
_QUICKPULSE_LAST_PROCESS_TIME = 0.0
_QUICKPULSE_PROCESS_ELAPSED_TIME = datetime.now()
_QUICKPULSE_LAST_PROCESS_CPU = 0.0

def _set_global_quickpulse_state(state: _QuickpulseState) -> None:
    # pylint: disable=global-statement
    global _GLOBAL_QUICKPULSE_STATE
    _GLOBAL_QUICKPULSE_STATE = state


def _get_global_quickpulse_state() -> _QuickpulseState:
    return _GLOBAL_QUICKPULSE_STATE


def _set_quickpulse_last_process_time(time: float) -> None:
    # pylint: disable=global-statement
    global _QUICKPULSE_LAST_PROCESS_TIME
    _QUICKPULSE_LAST_PROCESS_TIME = time


def _get_quickpulse_last_process_time() -> float:
    return _QUICKPULSE_LAST_PROCESS_TIME


def _set_quickpulse_process_elapsed_time(time: datetime) -> None:
    # pylint: disable=global-statement
    global _QUICKPULSE_PROCESS_ELAPSED_TIME
    _QUICKPULSE_PROCESS_ELAPSED_TIME = time


def _get_quickpulse_process_elapsed_time() -> datetime:
    return _QUICKPULSE_PROCESS_ELAPSED_TIME


def _set_quickpulse_last_process_cpu(time: float) -> None:
    # pylint: disable=global-statement
    global _QUICKPULSE_LAST_PROCESS_CPU
    _QUICKPULSE_LAST_PROCESS_CPU = time


def _get_quickpulse_last_process_cpu() -> float:
    return _QUICKPULSE_LAST_PROCESS_CPU


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
