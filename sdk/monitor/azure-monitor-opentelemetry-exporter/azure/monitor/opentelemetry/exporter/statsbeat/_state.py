# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import threading

_REQUESTS_LOCK = threading.Lock()
_REQUESTS_MAP = {}

_STATSBEAT_STATE = {
    "INITIAL_FAILURE_COUNT": 0,
    "INITIAL_SUCCESS": False,
    "SHUTDOWN": False,
}
_STATSBEAT_STATE_LOCK = threading.Lock()

# (OpenTelemetry metric name, Statsbeat metric name)
_ATTACH_METRIC_NAME = "Attach"
_FEATURE_METRIC_NAME = "Feature"
_REQ_SUCCESS_NAME = ("statsbeat_success_count", "Request Success Count")
_REQ_FAILURE_NAME = "Request Failure Count"
_REQ_DURATION_NAME = "Request Duration"
_REQ_RETRY_NAME = "Retry Count"
_REQ_THROTTLE_NAME = "Throttle Count"
_REQ_EXCEPTION_NAME = "Exception Count"

_STATSBEAT_METRIC_NAME_MAPPINGS = dict(
    [
        _REQ_SUCCESS_NAME,
    ]
)


def is_statsbeat_enabled():
    return not os.environ.get("APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL")


def increment_statsbeat_initial_failure_count():
    with _STATSBEAT_STATE_LOCK:
        _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"] += 1


def get_statsbeat_initial_failure_count():
    return _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"]


def set_statsbeat_initial_success(success):
    with _STATSBEAT_STATE_LOCK:
        _STATSBEAT_STATE["INITIAL_SUCCESS"] = success


def get_statsbeat_initial_success():
    return _STATSBEAT_STATE["INITIAL_SUCCESS"]


def get_statsbeat_shutdown():
    return _STATSBEAT_STATE["SHUTDOWN"]
