# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import logging
from threading import Lock

from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
    _ONE_SETTINGS_CHANGE_URL,
    _ONE_SETTINGS_CONFIG_URL,
    _ONE_SETTINGS_MAX_REFRESH_INTERVAL_SECONDS,
    _RETRYABLE_STATUS_CODES,
)
from azure.monitor.opentelemetry.exporter._configuration._utils import _ConfigurationProfile, OneSettingsResponse
from azure.monitor.opentelemetry.exporter._configuration._utils import make_onesettings_request
from azure.monitor.opentelemetry.exporter._utils import Singleton


# Set up logger
logger = logging.getLogger(__name__)


@dataclass
class _ConfigurationState:
    """Immutable state object for configuration data."""

    etag: str = ""
    refresh_interval: int = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
    settings_cache: Dict[str, str] = field(default_factory=dict)

    def with_updates(self, **kwargs) -> "_ConfigurationState":  # pylint: disable=C4741,C4742
        """Create a new state object with updated values."""
        return _ConfigurationState(
            etag=kwargs.get("etag", self.etag),
            refresh_interval=kwargs.get("refresh_interval", self.refresh_interval),
            settings_cache=kwargs.get("settings_cache", self.settings_cache.copy()),
        )


class _ConfigurationManager(metaclass=Singleton):
    """Singleton class to manage configuration settings."""

    def __init__(self):
        """Initialize the ConfigurationManager instance."""
        self._configuration_worker = None
        self._state_lock = Lock()  # Single lock for all state
        self._current_state = _ConfigurationState()
        self._callbacks = []
        self._initialized = False

    def initialize(self, **kwargs):
        """Initialize the ConfigurationManager and start the configuration worker."""
        with self._state_lock:
            if self._initialized:
                return

            # Fill the configuration profile with the initializer's parameters
            _ConfigurationProfile.fill(**kwargs)

            # Lazy import to avoid circular import
            from azure.monitor.opentelemetry.exporter._configuration._worker import _ConfigurationWorker

            # Get initial refresh interval from current state
            initial_refresh_interval = self._current_state.refresh_interval

            self._configuration_worker = _ConfigurationWorker(self, initial_refresh_interval)
            self._initialized = True

    def register_callback(self, callback):
        # Register a callback to be invoked when configuration changes.
        if not self._initialized:
            return
        self._callbacks.append(callback)

    def _notify_callbacks(self, settings: Dict[str, str]):
        # Notify all registered callbacks of configuration changes.
        for cb in self._callbacks:
            try:
                cb(settings)
            except Exception as ex:  # pylint: disable=broad-except
                logger.debug("Callback failed: %s", ex)

    def _is_transient_error(self, response: OneSettingsResponse) -> bool:
        """Check if the response indicates a transient error.

        :param response: OneSettingsResponse object from OneSettings request
        :type response: OneSettingsResponse
        :return: True if the error is transient and refresh interval should be increased
        :rtype: bool
        """
        # Check for exception indicator or retryable HTTP status codes
        return response.has_exception or response.status_code in _RETRYABLE_STATUS_CODES

    # pylint: disable=too-many-statements, too-many-branches
    def get_configuration_and_refresh_interval(self, query_dict: Optional[Dict[str, str]] = None) -> int:
        """Fetch configuration from OneSettings and update local cache atomically.

        This method implements the change detection mechanism per the OneSettings spec:
        - Polls CHANGE endpoint (e2) with cached ETag via if-none-match header.
          - If 304 Not Modified: no changes, update refresh interval only.
          - If 200 (new ETag or no cached ETag): fetch from CONFIG endpoint (e1) for settings.

        When transient errors are encountered (timeouts, network exceptions, or retryable
        HTTP status codes) from the CHANGE endpoint, the method doubles the current refresh
        interval (capped at 24 hours) and returns immediately.

        :param query_dict: Optional query parameters to include in the OneSettings request.
        :type query_dict: Optional[Dict[str, str]]

        :return: Updated refresh interval in seconds for the next configuration check.
        :rtype: int
        """
        query_dict = query_dict or {}
        headers: Dict[str, str] = {}

        # Read current state atomically
        with self._state_lock:
            current_state = self._current_state
            if current_state.etag:
                headers["If-None-Match"] = current_state.etag
            if current_state.refresh_interval:
                headers["x-ms-onesetinterval"] = str(current_state.refresh_interval)

        # Poll CHANGE endpoint (e2)
        response = make_onesettings_request(_ONE_SETTINGS_CHANGE_URL, query_dict, headers)

        # Check for transient errors - double interval and return
        if self._is_transient_error(response):
            with self._state_lock:
                doubled_interval = self._current_state.refresh_interval * 2
                current_refresh_interval = min(doubled_interval, _ONE_SETTINGS_MAX_REFRESH_INTERVAL_SECONDS)

            if response.has_exception:
                error_description = "network error"
            else:
                error_description = f"HTTP {response.status_code}"

            logger.debug("OneSettings CHANGE request failed with transient error (%s). Retrying. ", error_description)
            return current_refresh_interval  # type: ignore

        # Prepare new state updates
        new_state_updates: Dict[str, Any] = {}
        if response.etag is not None:
            new_state_updates["etag"] = response.etag
        if response.refresh_interval and response.refresh_interval > 0:  # type: ignore
            new_state_updates["refresh_interval"] = response.refresh_interval  # type: ignore

        if response.status_code == 304:
            # Not modified: no configuration changes published
            pass
        elif response.status_code == 200:
            # New ETag (or first call with no cached ETag) - fetch config from e1
            config_response = make_onesettings_request(_ONE_SETTINGS_CONFIG_URL, query_dict)
            if config_response.status_code == 200 and config_response.settings:
                new_state_updates["settings_cache"] = config_response.settings
            else:
                logger.debug("Unexpected response status from CONFIG endpoint: %d", config_response.status_code)
                # Do not update etag to allow retry on next call
                new_state_updates.pop("etag", None)
        else:
            # Unexpected non-transient status code
            logger.debug("Unexpected response status from CHANGE endpoint: %d", response.status_code)

        notify_callbacks = False
        current_refresh_interval = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
        state_for_callbacks = None

        # Atomic state update
        with self._state_lock:
            latest_state = self._current_state
            self._current_state = latest_state.with_updates(**new_state_updates)
            current_refresh_interval = self._current_state.refresh_interval
            if "settings_cache" in new_state_updates:
                notify_callbacks = True
                state_for_callbacks = self._current_state

        # Handle configuration updates throughout the SDK
        if notify_callbacks and state_for_callbacks is not None and state_for_callbacks.settings_cache:
            self._notify_callbacks(state_for_callbacks.settings_cache)

        return current_refresh_interval  # type: ignore

    def get_settings(self) -> Dict[str, str]:  # pylint: disable=C4741,C4742
        """Get current settings cache."""
        with self._state_lock:
            return self._current_state.settings_cache.copy()  # type: ignore

    def shutdown(self) -> None:
        """Shutdown the configuration worker."""
        if self._configuration_worker:
            self._configuration_worker.shutdown()
            self._configuration_worker = None
        self._initialized = False
        self._callbacks.clear()
        # Clear the singleton instance from the metaclass
        if self.__class__ in _ConfigurationManager._instances:  # pylint: disable=protected-access
            del _ConfigurationManager._instances[self.__class__]  # pylint: disable=protected-access
