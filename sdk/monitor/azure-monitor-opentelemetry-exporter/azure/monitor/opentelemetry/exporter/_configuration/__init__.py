# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Dict, Optional, Union
import json
import logging
import requests
from threading import Lock

from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
    _ONE_SETTINGS_PYTHON_KEY,
    _ONE_SETTINGS_URL,
)

# Set up logger
logger = logging.getLogger(__name__)


class _ConfigurationManager:
    """Singleton class to manage configuration settings."""
    
    _instance = None
    _instance_lock = Lock()
    _config_lock = Lock()
    _settings_lock = Lock()
    _etag = None
    _refresh_interval = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
    _settings_cache: Dict[str, str] = {}  # TODO: refresh every 30 minutes
    
    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super(_ConfigurationManager, cls).__new__(cls)
            return cls._instance
    
    def get_configuration_and_refresh_interval(self, query_dict: Optional[Dict[str, str]] = None) -> float:
        """Get configuration from OneSettings with optional query parameters.
        The cache witll be updated with the latest settings if available.
        
        Args:
            query_dict (Optional[Dict[str, str]]): Optional dictionary of query parameters to include

        """
        query_dict = query_dict or {}
        headers = {}
        with self._config_lock:
            if self._etag:
                headers = {
                    "If-None-Match": self._etag,
                }
            if self._refresh_interval:
                headers["x-ms-onesetinterval"] = str(self._refresh_interval)
        try:
            url = _ONE_SETTINGS_URL
            result = requests.get(url, params=query_dict, headers=headers, timeout=10)
            result.raise_for_status()  # Raises an exception for 4XX/5XX responses
            if result:
                if result.headers:
                    with self._config_lock:
                        # Update the ETag and refresh interval from the response headers
                        self._etag = result.headers.get("ETag")
                        refresh_interval = result.headers.get("x-ms-onesetinterval")
                        try:
                            self._refresh_interval = float(refresh_interval)
                        except (ValueError, TypeError):
                            logger.warning("Invalid refresh interval format: %s", self._refresh_interval)
                            # If the refresh interval is invalid, return the default value
                            self._refresh_interval = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
                # Check if the response is a 304 Not Modified
                # Cache stays the same in this case
                if result.status_code == 304:
                    pass
                # Check if the response is a 200 OK
                elif result.status_code == 200:
                    if result.content:
                        decoded_string = result.content.decode("utf-8")
                        config = json.loads(decoded_string)
                        settings = config.get("settings")
                        if settings:
                            with self._settings_lock:
                                self._settings_cache.clear()
                                for key, value in settings.items():
                                    self._settings_cache[key] = value
                elif result.status_code == 400:
                    logger.warning("Bad request to OneSettings: %s", result.content)
                elif result.status_code == 404:
                    logger.warning("OneSettings configuration not found: %s", result.content)
                elif result.status_code == 414:
                    logger.warning("OneSettings request URI too long: %s", result.content)
                elif result.status_code == 500:
                    logger.warning("Internal server error from OneSettings: %s", result.content)
            else:
                logger.warning("No settings found in OneSettings response")
        except requests.exceptions.RequestException as ex:
            logger.warning("Failed to fetch configuration from OneSettings: %s", str(ex))
        except json.JSONDecodeError as ex:
            logger.warning("Failed to parse OneSettings response: %s", str(ex))
        except Exception as ex:
            logger.warning("Unexpected error while fetching configuration: %s", str(ex))
        finally:
            return self._refresh_interval
    
    def get_python_configuration_and_refresh_interval(self) -> float:
        """Get configurations from the python namespace."""
        targeting = {
            "namespaces": _ONE_SETTINGS_PYTHON_KEY,
        }
        result = self.get_configuration_and_refresh_interval(targeting)
        return result
    
    def get_cache(self) -> Dict[str, str]:
        """Get cached configuration settings."""
        with self._settings_lock:
            return self._settings_cache.copy()


def _update_configuration_and_get_refresh_interval() -> float:
    return _ConfigurationManager().get_python_configuration_and_refresh_interval()

def _get_configuration() -> Optional[Dict[str, str]]:
    """Get cached configuration settings."""
    return _ConfigurationManager().get_cache()

def _get_is_feature_enabled(key: str) -> bool:
    """Check if feature is enabled."""
    feature_config = _get_configuration_from_one_settings()
    if feature_config:
        if isinstance(feature_config, str):
            return feature_config.lower() == "true"
        elif isinstance(feature_config, bool):
            return feature_config
        elif isinstance(feature_config, Dict):
            enabled_criteria = feature_config.get("enabled")
            if isinstance(enabled_criteria, Dict):
                for criteria, value in enabled_criteria.items():
                    if value == "*":
                        return True
    return False
