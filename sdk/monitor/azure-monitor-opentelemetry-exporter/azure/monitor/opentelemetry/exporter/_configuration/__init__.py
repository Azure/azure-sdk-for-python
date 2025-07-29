# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Dict, Optional
import logging
from threading import Lock

from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
    _ONE_SETTINGS_PYTHON_KEY,
    _ONE_SETTINGS_CHANGE_URL,
)
from azure.monitor.opentelemetry.exporter._configuration._util import make_onesettings_request

# Set up logger
logger = logging.getLogger(__name__)


class _ConfigurationManager:
    """Singleton class to manage configuration settings."""
    
    _instance = None
    _configuration_worker = None
    _instance_lock = Lock()
    _config_lock = Lock()
    _settings_lock = Lock()
    _version_lock = Lock()
    _etag = None
    # _refresh_interval = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
    _refresh_interval = 5
    _settings_cache: Dict[str, str] = {}
    _version_cache = 0
    
    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super(_ConfigurationManager, cls).__new__(cls)
                # Initialize the instance here to avoid re-initialization
                cls._instance._initialize_worker()
            return cls._instance
    
    def _initialize_worker(self):
        """Initialize the ConfigurationManager and start the configuration worker."""
        # Lazy import to avoid circular import
        from azure.monitor.opentelemetry.exporter._configuration._worker import _ConfigurationWorker
        self._configuration_worker = _ConfigurationWorker(self._refresh_interval)
    
    def get_configuration_and_refresh_interval(self, query_dict: Optional[Dict[str, str]] = None) -> float:
        """Get configuration from OneSettings with optional query parameters.
        The cache will be updated with the latest settings if available.
        
        Args:
            query_dict (Optional[Dict[str, str]]): Optional dictionary of query parameters to include

        """
        query_dict = query_dict or {}
        headers = {}
        
        # Prepare headers with current etag and refresh interval
        with self._config_lock:
            if self._etag:
                headers["If-None-Match"] = self._etag
            if self._refresh_interval:
                headers["x-ms-onesetinterval"] = str(self._refresh_interval)
        
        # Make the OneSettings request
        response = make_onesettings_request(_ONE_SETTINGS_CHANGE_URL, query_dict, headers)
        
        # Update configuration state based on response
        with self._config_lock:
            self._etag = response.etag
            self._refresh_interval = response.refresh_interval

        # Evaluate CONFIG_VERSION to see if we need to fetch new config
        if response.settings:
            with self._version_lock:
                if response.version is not None:
                    # New config published sucessfully, make a call to config endpoint
                    if response.version > self._version_cache:
                        # TODO: Call config endpoint to pull new config
                        # Update latest version
                        self._version_cache = response.version
                    elif response.version == self._version_cache:
                        # No new config has been published, do nothing
                        pass
                    else:
                        # Erroneous state, should not occur under normal circumstances
                        logger.warning(
                            "Latest `CHANGE_VERSION` is less than the current stored version, no configurations updated."
                        )
        return self._refresh_interval

    def shutdown(self) -> None:
        """Shutdown the configuration worker."""
        if self._configuration_worker:
            self._configuration_worker.shutdown()


def _update_configuration_and_get_refresh_interval() -> float:
    targeting = {
        "namespaces": _ONE_SETTINGS_PYTHON_KEY,
    }
    return _ConfigurationManager().get_configuration_and_refresh_interval(targeting)
