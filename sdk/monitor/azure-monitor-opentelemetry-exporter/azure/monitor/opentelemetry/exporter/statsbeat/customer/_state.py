# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._manager import CustomerSdkStatsManager

# Global singleton instance for easy access throughout the codebase
_customer_stats_manager = None

def get_customer_stats_manager() -> "CustomerSdkStatsManager":  # type: ignore
    # Get the global CustomerSdkStatsManager singleton instance.

    # This provides a single access point to the manager and handles lazy initialization
    # to avoid circular import issues.

    global _customer_stats_manager  # pylint: disable=global-statement
    if _customer_stats_manager is None:
        from ._manager import CustomerSdkStatsManager
        _customer_stats_manager = CustomerSdkStatsManager()
    return _customer_stats_manager

# TODO: Move to a storage manager

_LOCAL_STORAGE_SETUP_STATE = {
    "READONLY": False,
    "EXCEPTION_OCCURRED": ""
}

_LOCAL_STORAGE_SETUP_STATE_LOCK = threading.Lock()


def get_local_storage_setup_state_readonly():
    return _LOCAL_STORAGE_SETUP_STATE["READONLY"]


def set_local_storage_setup_state_readonly():
    with _LOCAL_STORAGE_SETUP_STATE_LOCK:
        _LOCAL_STORAGE_SETUP_STATE["READONLY"] = True


def get_local_storage_setup_state_exception():
    return _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"]


def set_local_storage_setup_state_exception(value):
    with _LOCAL_STORAGE_SETUP_STATE_LOCK:
        _LOCAL_STORAGE_SETUP_STATE["EXCEPTION_OCCURRED"] = value
