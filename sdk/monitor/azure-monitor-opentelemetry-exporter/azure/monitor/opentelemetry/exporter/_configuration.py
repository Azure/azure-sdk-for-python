# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Dict, Optional, Union
import json
import logging
import requests
from threading import Lock

from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_PYTHON_KEY,
    _ONE_SETTINGS_URL,
    _ONE_SETTINGS_CNAME,
    _ONE_SETTINGS_PATH
)

# Set up logger
logger = logging.getLogger(__name__)


class _ConfigurationManager:
    """Singleton class to manage configuration settings."""
    
    _instance = None
    _instance_lock = Lock()
    _settings_lock = Lock()
    _etag = None
    _refresh_interval = None
    _settings_cache: Dict[str, str] = {}  # TODO: refresh every 30 minutes
    
    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super(_ConfigurationManager, cls).__new__(cls)
            return cls._instance
    
    def get_configuration(self, query_dict: Optional[Dict[str, str]] = None) -> Optional[Dict[str, str]]:
        """Get configuration from OneSettings with optional query parameters."""
        query_dict = query_dict or {}
        headers = {}
        if self._etag:
            headers = {
                "If-None-Match": self._etag,
            }
        if self._refresh_interval:
            headers["x-ms-onesetinterval"] = self._refresh_interval
        try:
            url = _ONE_SETTINGS_URL
            result = requests.get(url, params=query_dict, headers=headers, timeout=10)
            result.raise_for_status()  # Raises an exception for 4XX/5XX responses
            if result:
                if result.headers:
                    self._etag = result.headers.get("ETag")
                    self._refresh_interval = result.headers.get("x-ms-onesetinterval")
                # Check if the response is a 304 Not Modified
                # Use cached result if settings not modified
                if result.status_code == 304:
                    return self._settings_cache
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
                            return self._settings_cache
                return None
            else:
                logger.warning("No settings found in OneSettings response")
                return None
        except requests.exceptions.RequestException as ex:
            logger.warning("Failed to fetch configuration from OneSettings: %s", str(ex))
            return None
        except json.JSONDecodeError as ex:
            logger.warning("Failed to parse OneSettings response: %s", str(ex))
            return None
        except Exception as ex:
            logger.warning("Unexpected error while fetching configuration: %s", str(ex))
        return None
    
    def get_python_configuration(self) -> Optional[Dict[str, str]]:
        """Get a specific configuration value by key from the python namespace."""
        with self._settings_lock:
            if self._settings_cache:
                return self._settings_cache
        targeting = {
            "namespaces": _ONE_SETTINGS_PYTHON_KEY,
        }
        result = self.get_configuration(targeting)
        return result


def _get_configuration_from_one_settings() -> Optional[Union[str, int, float, bool, Dict]]:
    return _ConfigurationManager().get_python_configuration()


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
