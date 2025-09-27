# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from dataclasses import dataclass, field
from typing import Dict, Optional
import logging
from threading import Lock

from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
    _ONE_SETTINGS_CHANGE_URL,
    _ONE_SETTINGS_CONFIG_URL,
)
from azure.monitor.opentelemetry.exporter._configuration._utils import _ConfigurationProfile
from azure.monitor.opentelemetry.exporter._configuration._utils import make_onesettings_request
from azure.monitor.opentelemetry.exporter._utils import Singleton

# Set up logger
logger = logging.getLogger(__name__)


@dataclass
class _ConfigurationState:
    """Immutable state object for configuration data."""
    etag: str = ""
    refresh_interval: int = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
    version_cache: int = -1
    settings_cache: Dict[str, str] = field(default_factory=dict)

    def with_updates(self, **kwargs) -> '_ConfigurationState':  # pylint: disable=C4741,C4742
        """Create a new state object with updated values."""
        return _ConfigurationState(
            etag=kwargs.get('etag', self.etag),
            refresh_interval=kwargs.get('refresh_interval', self.refresh_interval),
            version_cache=kwargs.get('version_cache', self.version_cache),
            settings_cache=kwargs.get('settings_cache', self.settings_cache.copy())
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
                logger.warning("Callback failed: %s", ex)

    # pylint: disable=too-many-statements
    def get_configuration_and_refresh_interval(self, query_dict: Optional[Dict[str, str]] = None) -> int:
        """Fetch configuration from OneSettings and update local cache atomically.
        
        This method performs a conditional HTTP request to OneSettings using the
        current ETag for efficient caching. It atomically updates the local configuration
        state with any new settings and manages version tracking for change detection.
        
        The method implements a check-and-set pattern for thread safety:
        1. Reads current state atomically to prepare request headers
        2. Makes HTTP request to OneSettings CHANGE endpoint outside locks
        3. Re-reads current state to make version comparison decisions
        4. Conditionally fetches from CONFIG endpoint if version increased
        5. Updates all state fields atomically in a single operation
        
        Version comparison logic:
        - Version increase: New configuration available, fetches and caches new settings
        - Version same: No changes detected, ETag and refresh interval updated safely
        - Version decrease: Unexpected rollback state, logged as warning, no updates applied
        
        Error handling:
        - CONFIG endpoint failure: ETag not updated to preserve retry capability on next call
        - Network failures: Handled by make_onesettings_request, returns default values
        - Missing settings/version: Logged as warning, only ETag and refresh interval updated

        :param query_dict: Optional query parameters to include in the OneSettings request.
            Commonly used for targeting specific configuration namespaces or environments.
            If None, defaults to empty dictionary.
        :type query_dict: Optional[Dict[str, str]]

        :return: Updated refresh interval in seconds for the next configuration check.
            This value comes from the OneSettings response and determines how frequently
            the background worker should call this method.
        :rtype: int
        
        Thread Safety:
            This method is thread-safe using atomic state updates. Multiple threads can
            call this method concurrently without data corruption. The implementation uses
            a single state lock with minimal critical sections to reduce lock contention.
            
            HTTP requests are performed outside locks to prevent blocking other threads
            during potentially slow network operations.
        
        Caching Behavior:
            The method automatically includes ETag headers for conditional requests to
            minimize unnecessary data transfer. If the server responds with 304 Not Modified,
            only the refresh interval is updated while preserving existing configuration.
            
            On CONFIG endpoint failures, the ETag is intentionally not updated to ensure
            the next request can retry fetching the same configuration version.
            
        State Consistency:
            All configuration state (ETag, refresh interval, version, settings) is updated
            atomically using immutable state objects. This prevents race conditions where
            different threads might observe inconsistent combinations of these values.
        """
        query_dict = query_dict or {}
        headers = {}

        # Read current state atomically
        with self._state_lock:
            current_state = self._current_state
            if current_state.etag:
                headers["If-None-Match"] = current_state.etag
            if current_state.refresh_interval:
                headers["x-ms-onesetinterval"] = str(current_state.refresh_interval)

        # Make the OneSettings request
        response = make_onesettings_request(_ONE_SETTINGS_CHANGE_URL, query_dict, headers)

        # Prepare new state updates
        new_state_updates = {}
        if response.etag is not None:
            new_state_updates['etag'] = response.etag
        if response.refresh_interval and response.refresh_interval > 0:
            new_state_updates['refresh_interval'] = response.refresh_interval  # type: ignore

        if response.status_code == 304:
            # Not modified: Settings unchanged, but update etag and refresh interval if provided
            pass
        # Handle version and settings updates
        elif response.settings and response.version is not None:
            needs_config_fetch = False
            with self._state_lock:
                current_state = self._current_state

                if response.version > current_state.version_cache:
                    # Version increase: new config available
                    needs_config_fetch = True
                elif response.version < current_state.version_cache:
                    # Version rollback: Erroneous state
                    logger.warning("Fetched version is lower than cached version. No configurations updated.")
                    needs_config_fetch = False
                else:
                    # Version unchanged: No new config
                    needs_config_fetch = False

            # Fetch config
            if needs_config_fetch:
                config_response = make_onesettings_request(_ONE_SETTINGS_CONFIG_URL, query_dict)
                if config_response.status_code == 200 and config_response.settings:
                    # Validate that the versions from change and config match
                    if config_response.version == response.version:
                        new_state_updates.update({
                            'version_cache': response.version,  # type: ignore
                            'settings_cache': config_response.settings  # type: ignore
                        })
                    else:
                        logger.warning("Version mismatch between change and config responses." \
                        "No configurations updated.")
                        # We do not update etag to allow retry on next call
                        new_state_updates.pop('etag', None)
                else:
                    logger.warning("Unexpected response status: %d", config_response.status_code)
                    # We do not update etag to allow retry on next call
                    new_state_updates.pop('etag', None)
        else:
            # No settings or version provided
            logger.warning("No settings or version provided in config response. Config not updated.")


        notify_callbacks = False
        current_refresh_interval = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
        state_for_callbacks = None

        # Atomic state update
        with self._state_lock:
            latest_state = self._current_state  # Always use latest state
            self._current_state = latest_state.with_updates(**new_state_updates)
            current_refresh_interval = self._current_state.refresh_interval
            if 'settings_cache' in new_state_updates:
                notify_callbacks = True
                state_for_callbacks = self._current_state

        # Handle configuration updates throughout the SDK
        if notify_callbacks and state_for_callbacks is not None and state_for_callbacks.settings_cache:
            self._notify_callbacks(state_for_callbacks.settings_cache)

        return current_refresh_interval

    def get_settings(self) -> Dict[str, str]:  # pylint: disable=C4741,C4742
        """Get current settings cache."""
        with self._state_lock:
            return self._current_state.settings_cache.copy()  # type: ignore

    def get_current_version(self) -> int:  # pylint: disable=C4741,C4742
        """Get current version."""
        with self._state_lock:
            return self._current_state.version_cache  # type: ignore

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
