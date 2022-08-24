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
