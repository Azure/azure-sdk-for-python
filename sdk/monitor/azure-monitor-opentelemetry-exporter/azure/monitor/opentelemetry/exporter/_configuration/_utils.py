# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Dict, Optional
import json
import logging
import requests

from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
    _ONE_SETTINGS_CHANGE_VERSION_KEY,
)

logger = logging.getLogger(__name__)


class OneSettingsResponse:
    """Response object containing OneSettings response data."""
    
    def __init__(self, etag: Optional[str] = None, refresh_interval: float = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS, 
                 settings: Optional[Dict[str, str]] = None, version: Optional[int] = None):
        self.etag = etag
        self.refresh_interval = refresh_interval
        self.settings = settings or {}
        self.version = version


def make_onesettings_request(url: str, query_dict: Optional[Dict[str, str]] = None, 
                           headers: Optional[Dict[str, str]] = None) -> OneSettingsResponse:
    """Make a request to OneSettings and handle the response.
    
    Args:
        url (str): The OneSettings URL to request
        query_dict (Optional[Dict[str, str]]): Optional query parameters
        headers (Optional[Dict[str, str]]): Optional request headers
        
    Returns:
        OneSettingsResponse: Parsed response with settings and metadata
    """
    query_dict = query_dict or {}
    headers = headers or {}
    
    try:
        result = requests.get(url, params=query_dict, headers=headers, timeout=10)
        result.raise_for_status()  # Raises an exception for 4XX/5XX responses
        
        return _parse_onesettings_response(result)
        
    except requests.exceptions.RequestException as ex:
        logger.warning("Failed to fetch configuration from OneSettings: %s", str(ex))
        return OneSettingsResponse()
    except json.JSONDecodeError as ex:
        logger.warning("Failed to parse OneSettings response: %s", str(ex))
        return OneSettingsResponse()
    except Exception as ex:
        logger.warning("Unexpected error while fetching configuration: %s", str(ex))
        return OneSettingsResponse()

def _parse_onesettings_response(response) -> OneSettingsResponse:
    """Parse a OneSettings HTTP response into a structured response object.
    
    Args:
        response: HTTP response object from requests
        
    Returns:
        OneSettingsResponse: Parsed response data
    """
    etag = None
    refresh_interval = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
    settings = {}
    status_code = response.status_code
    version = None
    
    if not response:
        logger.warning("No settings found in OneSettings response")
        return OneSettingsResponse(etag, refresh_interval, settings, status_code)
    
    # Extract headers
    if response.headers:
        etag = response.headers.get("ETag")
        refresh_interval_header = response.headers.get("x-ms-onesetinterval")
        try:
            refresh_interval = float(refresh_interval_header) if refresh_interval_header else refresh_interval
        except (ValueError, TypeError):
            logger.warning("Invalid refresh interval format: %s", refresh_interval_header)
            refresh_interval = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
    
    # Handle different status codes
    if status_code == 304:
        # 304 Not Modified - cache stays the same
        pass
    elif status_code == 200:
        # 200 OK - parse new settings
        if response.content:
            try:
                decoded_string = response.content.decode("utf-8")
                config = json.loads(decoded_string)
                settings = config.get("settings", {})
                if settings and settings.get(_ONE_SETTINGS_CHANGE_VERSION_KEY) is not None:
                   version = int(settings.get(_ONE_SETTINGS_CHANGE_VERSION_KEY))
            except (UnicodeDecodeError, json.JSONDecodeError) as ex:
                logger.warning("Failed to decode OneSettings response content: %s", str(ex))
            except ValueError as ex:
                logger.warning("Failed to parse OneSettings change version: %s", str(ex))
    elif status_code == 400:
        logger.warning("Bad request to OneSettings: %s", response.content)
    elif status_code == 404:
        logger.warning("OneSettings configuration not found: %s", response.content)
    elif status_code == 414:
        logger.warning("OneSettings request URI too long: %s", response.content)
    elif status_code == 500:
        logger.warning("Internal server error from OneSettings: %s", response.content)
    
    return OneSettingsResponse(etag, refresh_interval, settings, version)
