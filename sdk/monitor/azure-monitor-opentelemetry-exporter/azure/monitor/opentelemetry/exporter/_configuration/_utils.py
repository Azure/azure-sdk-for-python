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
    """Response object containing OneSettings API response data.

    This class encapsulates the parsed response from a OneSettings API call,
    including configuration settings, version information, and metadata.

    Attributes:
        etag (Optional[str]): ETag header value for caching and conditional requests
        refresh_interval (int): Interval in seconds for the next configuration refresh
        settings (Dict[str, str]): Dictionary of configuration key-value pairs
        version (Optional[int]): Configuration version number for change tracking
        status_code (int): HTTP status code from the response
    """

    def __init__(
        self,
        etag: Optional[str] = None,
        refresh_interval: int = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
        settings: Optional[Dict[str, str]] = None,
        version: Optional[int] = None,
        status_code: int = 200,
    ):
        """Initialize OneSettingsResponse with configuration data.

        Args:
            etag (Optional[str], optional): ETag header value for caching. Defaults to None.
            refresh_interval (int, optional): Refresh interval in seconds.
                Defaults to _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS.
            settings (Optional[Dict[str, str]], optional): Configuration settings dictionary.
                Defaults to empty dict if None.
            version (Optional[int], optional): Configuration version number. Defaults to None.
            status_code (int, optional): HTTP status code. Defaults to 200.
        """
        self.etag = etag
        self.refresh_interval = refresh_interval
        self.settings = settings or {}
        self.version = version
        self.status_code = status_code


def make_onesettings_request(
    url: str, query_dict: Optional[Dict[str, str]] = None, headers: Optional[Dict[str, str]] = None
) -> OneSettingsResponse:
    """Make an HTTP request to the OneSettings API and parse the response.

    This function handles the complete OneSettings request lifecycle including:
    - Making the HTTP GET request with optional query parameters and headers
    - Error handling for network, HTTP, and JSON parsing errors
    - Parsing the response into a structured OneSettingsResponse object

    :param url: The OneSettings API endpoint URL to request
    :type url: str
    :param query_dict: Query parameters to include
        in the request URL. Defaults to None.
    :type query_dict: Optional[Dict[str, str]]
    :param headers: HTTP headers to include in the request.
    Common headers include 'If-None-Match' for ETag caching. Defaults to None.
    :type headers: Optional[Dict[str, str]]

    :return: Parsed response containing configuration data and metadata.
            Returns a default response object if the request fails.
    :rtype: OneSettingsResponse

    Raises:
        Does not raise exceptions - all errors are caught and logged, returning a
        default OneSettingsResponse object.
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
    except Exception as ex:  # pylint: disable=broad-exception-caught
        logger.warning("Unexpected error while fetching configuration: %s", str(ex))
        return OneSettingsResponse()


def _parse_onesettings_response(response: requests.Response) -> OneSettingsResponse:
    """Parse an HTTP response from OneSettings into a structured response object.

    This function processes the OneSettings API response and extracts:
    - HTTP headers (ETag, refresh interval)
    - Response body (configuration settings, version)
    - Status code handling (200, 304, 4xx, 5xx)

    The parser handles different HTTP status codes appropriately:
    - 200: New configuration data available, parse settings and version
    - 304: Not modified, configuration unchanged (empty settings)
    - 400/404/414/500: Various error conditions, logged with warnings

    :param response: HTTP response object from the requests library containing
        the OneSettings API response with headers, status code, and content.
    :type response: requests.Response

    :return: Structured response object containing:
        - etag: ETag header value for conditional requests
        - refresh_interval: Next refresh interval from headers
        - settings: Configuration key-value pairs (empty for 304/errors)
        - version: Configuration version number for change tracking
        - status_code: HTTP status code of the response
    :rtype: OneSettingsResponse
    Note:
        This function logs warnings for various error conditions but does not
        raise exceptions, always returning a valid OneSettingsResponse object.
    """
    etag = None
    refresh_interval = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
    settings: Dict[str, str] = {}
    status_code = response.status_code
    version = None

    # Extract headers
    if response.headers:
        etag = response.headers.get("ETag")
        refresh_interval_header = response.headers.get("x-ms-onesetinterval")
        try:
            # Note: OneSettings refresh interval is in minutes, convert to seconds
            if refresh_interval_header:
                refresh_interval = int(refresh_interval_header) * 60
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
                    version = int(settings.get(_ONE_SETTINGS_CHANGE_VERSION_KEY))  # type: ignore
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

    return OneSettingsResponse(etag, refresh_interval, settings, version, status_code)
