# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datetime import datetime
from enum import Enum
from typing import Dict, List, Tuple

from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _LONG_PING_INTERVAL_SECONDS,
    _POST_INTERVAL_SECONDS,
    _QUICKPULSE_PROJECTION_MAX_VALUE,
    _QUICKPULSE_PROJECTION_MIN_VALUE,
    _SHORT_PING_INTERVAL_SECONDS,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    AggregationType,
    DerivedMetricInfo,
    DocumentIngress,
    TelemetryType,
)


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
# Filtering
_QUICKPULSE_ETAG = ""
_QUICKPULSE_DERIVED_METRIC_INFOS: Dict[TelemetryType, List[DerivedMetricInfo]] = {}
_QUICKPULSE_PROJECTION_MAP: Dict[str, Tuple[AggregationType, float, int]] = {}


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
    return _get_global_quickpulse_state() in (_QuickpulseState.PING_SHORT, _QuickpulseState.PING_LONG)


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


# Filtering


# Used for etag configuration
def _set_quickpulse_etag(etag: str) -> None:
    # pylint: disable=global-statement
    global _QUICKPULSE_ETAG
    _QUICKPULSE_ETAG = etag


def _get_quickpulse_etag() -> str:
    return _QUICKPULSE_ETAG


# Used for updating filter configuration when etag has changed
# Contains filter and projection to apply for each telemetry type if exists
def _set_quickpulse_derived_metric_infos(filters: Dict[TelemetryType, List[DerivedMetricInfo]]) -> None:
    # pylint: disable=global-statement
    global _QUICKPULSE_DERIVED_METRIC_INFOS
    _QUICKPULSE_DERIVED_METRIC_INFOS = filters


def _get_quickpulse_derived_metric_infos() -> Dict[TelemetryType, List[DerivedMetricInfo]]:
    return _QUICKPULSE_DERIVED_METRIC_INFOS


# Used for initializing and setting projections when span/logs are recorded
def _set_quickpulse_projection_map(metric_id: str, aggregation_type: AggregationType, value: float, count: int):
    # pylint: disable=global-statement
    # pylint: disable=global-variable-not-assigned
    global _QUICKPULSE_PROJECTION_MAP
    _QUICKPULSE_PROJECTION_MAP[metric_id] = (aggregation_type, value, count)


def _get_quickpulse_projection_map() -> Dict[str, Tuple[AggregationType, float, int]]:
    return _QUICKPULSE_PROJECTION_MAP


# Resets projections per derived metric info for next quickpulse interval
# Called processing of previous quickpulse projections are finished/exported
def _reset_quickpulse_projection_map():
    # pylint: disable=global-statement
    global _QUICKPULSE_PROJECTION_MAP
    new_map = {}
    if _QUICKPULSE_PROJECTION_MAP:
        for id, projection in _QUICKPULSE_PROJECTION_MAP.items():
            value = 0
            if projection[0] == AggregationType.MIN:
                value = _QUICKPULSE_PROJECTION_MAX_VALUE
            elif projection[0] == AggregationType.MAX:
                value = _QUICKPULSE_PROJECTION_MIN_VALUE
            new_map[id] = (projection[0], value, 0)
        _QUICKPULSE_PROJECTION_MAP.clear()
        _QUICKPULSE_PROJECTION_MAP = new_map


# clears the projection map, usually called when config changes
def _clear_quickpulse_projection_map():
    # pylint: disable=global-statement
    # pylint: disable=global-variable-not-assigned
    global _QUICKPULSE_PROJECTION_MAP
    _QUICKPULSE_PROJECTION_MAP.clear()
