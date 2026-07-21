# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable
from typing import Dict, Optional, Any
import json
import logging

# mypy: disable-error-code="import-untyped"
import requests  # pylint: disable=networking-import-outside-azure-core-transport

from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
)


logger = logging.getLogger(__name__)


class _ConfigurationProfile:
    """Profile for the current running SDK."""

    os: str = ""
    rp: str = ""
    attach: str = ""
    version: str = ""
    component: str = ""
    region: str = ""
    ikey: str = ""

    @classmethod
    def fill(cls, **kwargs) -> None:
        """Update only the class variables that are provided in kwargs and haven't been updated yet."""
        if "os" in kwargs and cls.os == "":
            cls.os = kwargs["os"]
        if "version" in kwargs and cls.version == "":
            cls.version = kwargs["version"]
        if "component" in kwargs and cls.component == "":
            cls.component = kwargs["component"]
        if "rp" in kwargs and cls.rp == "":
            cls.rp = kwargs["rp"]
        if "attach" in kwargs and cls.attach == "":
            cls.attach = kwargs["attach"]
        if "region" in kwargs and cls.region == "":
            cls.region = kwargs["region"]
        if "ikey" in kwargs and cls.ikey == "":
            cls.ikey = kwargs["ikey"]


class OneSettingsResponse:
    """Response object containing OneSettings API response data.

    This class encapsulates the parsed response from a OneSettings API call,
    including configuration settings, error indicators and metadata.

    Attributes:
        etag (Optional[str]): ETag header value for caching and conditional requests
        refresh_interval_s (int): Interval in seconds for the next configuration refresh
        settings (Dict[str, str]): Dictionary of configuration key-value pairs
        status_code (int): HTTP status code from the response
        has_exception (bool): True if the request resulted in a transient error (network error, timeout, etc.)
    """

    def __init__(
        self,
        etag: Optional[str] = None,
        refresh_interval_s: int = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
        settings: Optional[Dict[str, str]] = None,
        status_code: int = 200,
        has_exception: bool = False,
    ):
        """Initialize OneSettingsResponse with configuration data.

        Args:
            etag (Optional[str], optional): ETag header value for caching. Defaults to None.
            refresh_interval_s (int, optional): Refresh interval in seconds.
                Defaults to _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS.
            settings (Optional[Dict[str, str]], optional): Configuration settings dictionary.
                Defaults to empty dict if None.
            status_code (int, optional): HTTP status code. Defaults to 200.
            has_exception (bool, optional): Indicates if request failed with a transient error. Defaults to False.
        """
        self.etag = etag
        self.refresh_interval_s = refresh_interval_s
        self.settings = settings or {}
        self.status_code = status_code
        self.has_exception = has_exception


def make_onesettings_request(
    url: str, query_dict: Optional[Dict[str, str]] = None, headers: Optional[Dict[str, str]] = None
) -> OneSettingsResponse:
    """Make an HTTP request to the OneSettings API and parse the response.

    This function handles the complete OneSettings request lifecycle including:
    - Making the HTTP GET request with optional query parameters and headers
    - Error handling for network, HTTP, timeout, and JSON parsing errors
    - Parsing the response into a structured OneSettingsResponse object

    :param url: The OneSettings API endpoint URL to request
    :type url: str
    :param query_dict: Query parameters to include
        in the request URL. Defaults to None.
    :type query_dict: Optional[Dict[str, str]]
    :param headers: HTTP headers to include in the request.
    Common headers include 'If-None-Match' for ETag caching. Defaults to None.
    :type headers: Optional[Dict[str, str]]

    :return: Parsed response containing configuration data and metadata, including
            error indicators for exceptions and timeouts.
    :rtype: OneSettingsResponse

    Raises:
        Does not raise exceptions - all errors are caught and logged, returning a
        OneSettingsResponse object with appropriate error indicators set.
    """
    query_dict = query_dict or {}
    headers = headers or {}

    try:
        result = requests.get(url, params=query_dict, headers=headers, timeout=10)
        # Do NOT call raise_for_status(): HTTP error codes (4xx/5xx) are handled by the parser so
        # the real status_code is preserved. This lets callers distinguish retryable errors
        # (see _RETRYABLE_STATUS_CODES) from non-retryable client errors (400/404/414). Only genuine
        # network/timeout failures below are surfaced as has_exception=True (transient).
        return _parse_onesettings_response(result)
    except requests.exceptions.Timeout as ex:
        logger.debug("OneSettings request timed out: %s", str(ex))
        return OneSettingsResponse(has_exception=True)
    except requests.exceptions.RequestException as ex:
        logger.debug("Failed to fetch configuration from OneSettings: %s", str(ex))
        return OneSettingsResponse(has_exception=True)
    except Exception as ex:  # pylint: disable=broad-exception-caught
        # _parse_onesettings_response already swallows JSON/decode errors internally, so nothing
        # here raises json.JSONDecodeError; this catch-all covers any other unexpected failure.
        logger.debug("Unexpected error while fetching configuration: %s", str(ex))
        return OneSettingsResponse(has_exception=True)


def _parse_onesettings_response(response: requests.Response) -> OneSettingsResponse:
    """Parse an HTTP response from OneSettings into a structured response object.

    This function processes the OneSettings API response and extracts:
    - HTTP headers (ETag, refresh interval)
    - Response body (configuration settings)
    - Status code handling (200, 304, 4xx, 5xx)

    The parser handles different HTTP status codes appropriately:
    - 200: New configuration data available, parse settings
    - 304: Not modified, configuration unchanged (empty settings)
    - 400/404/414/500: Various error conditions, logged at debug

    :param response: HTTP response object from the requests library containing
        the OneSettings API response with headers, status code, and content.
    :type response: requests.Response

    :return: Structured response object containing:
        - etag: ETag header value for conditional requests
        - refresh_interval_s: Next refresh interval from headers
        - settings: Configuration key-value pairs (empty for 304/errors)
        - status_code: HTTP status code of the response
    :rtype: OneSettingsResponse
    Note:
        This function logs various error conditions at debug level (config fetching is internal)
        but does not raise exceptions, always returning a valid OneSettingsResponse object.
    """
    etag = None
    refresh_interval_s = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
    settings: Dict[str, str] = {}
    status_code = response.status_code

    # Extract headers
    if response.headers:
        etag = response.headers.get("ETag")
        refresh_interval_header = response.headers.get("x-ms-onesetinterval")
        try:
            # Note: OneSettings refresh interval returned is in minutes, convert to seconds
            if refresh_interval_header:
                refresh_interval_s = int(refresh_interval_header) * 60
        except (ValueError, TypeError):
            logger.debug("Invalid refresh interval format: %s", refresh_interval_header)
            refresh_interval_s = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS

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
            except (UnicodeDecodeError, json.JSONDecodeError) as ex:
                logger.debug("Failed to decode OneSettings response content: %s", str(ex))
    elif status_code == 400:
        logger.debug("Bad request to OneSettings: %s", response.content)
    elif status_code == 404:
        logger.debug("OneSettings configuration not found: %s", response.content)
    elif status_code == 414:
        logger.debug("OneSettings request URI too long: %s", response.content)
    elif status_code == 500:
        logger.debug("Internal server error from OneSettings: %s", response.content)

    return OneSettingsResponse(etag, refresh_interval_s, settings, status_code)


# mypy: disable-error-code="no-any-return"
def evaluate_feature(feature_key: str, settings: Dict[str, Any]) -> Optional[bool]:
    """Evaluate whether a feature should be enabled based on configuration profile and settings.

    This function compares the current _ConfigurationProfile against feature-specific
    override conditions to determine if a feature should be enabled or disabled.

    :param feature_key: The name of the feature to evaluate
    :type feature_key: str
    :param settings: Dictionary containing feature configurations with override conditions
    :type settings: Dict[str, Any]
    :return: True if the feature should be enabled, False if disabled, None if inputs are invalid
    :rtype: Optional[bool]

    Example settings structure:
    {
        "FEATURE_LIVE_METRICS": {
            "default": "disabled",  # Feature is disabled by default
            "override": [
                {"os": "windows"},  # Enable on Windows (any version)
                # Enable on Linux at exact version 1.0.0b21 with the distro component
                {"os": "linux", "ver": "1.0.0b21", "component": "dst"},
                {"ikey": "12345678-1234-1234-1234-123456789abc"},  # Enable for a specific instrumentation key
                {"component": "dst"}  # Enable if component is distro
            ]
        },
        "FEATURE_SDK_STATS": {
            "default": "enabled",  # Feature is enabled by default
            "override": [
                {"os": "linux"},  # Disable on Linux
                # Disable on Linux at exact version 1.0.0b20 with the exporter component
                {"os": "linux", "ver": "1.0.0b20", "component": "ext"}
            ]
        }
    }

    Available condition fields (each override rule is a single-value exact match per field):
    - os: Operating system ("windows", "linux", "darwin", "unknown")
    - ver: Exact version string match (e.g. "1.0.0b21"); when present, "component" is also required
    - rp: Resource provider ("appsvc", "fn", "aks", "unknown")
    - ikey: Instrumentation key (GUID format, case-insensitive)
    - component: Component type ("dst"=distro, "ext"=exporter, "mot"=msft distro)
    - attach: Attach type ("manual", "integratedauto")
    - region: Azure region (e.g. "eastus", "westeurope")

    Override logic:
    - Each item in the override list is an independent rule
    - ALL conditions within a single rule must match for that rule to apply
    - If ANY rule matches completely, the feature state is flipped from default
    - If NO rules match, the default state is returned
    """
    # Validate inputs - return None for invalid inputs
    if not feature_key or not isinstance(settings, dict):
        return None

    if feature_key not in settings:
        return None

    feature_config = settings[feature_key]
    if not isinstance(feature_config, dict):
        return None

    default_state = feature_config.get("default", "disabled").lower() == "enabled"
    override_list = feature_config.get("override", [])

    # If no override conditions, return default state
    if not override_list or not isinstance(override_list, list):
        return default_state

    # Check override conditions - if ANY override rule matches completely, apply override
    for override_rule in override_list:
        if isinstance(override_rule, dict) and _matches_override_rule(override_rule):
            # At least one override rule matched - return opposite of default
            return not default_state

    # No override rules matched - return default state
    return default_state


# mypy: disable-error-code="no-any-return"
def _matches_override_rule(override_rule: Dict[str, Any]) -> bool:
    """Check if all conditions in an override rule match the current configuration profile.

    All conditions within a single override rule must match for the rule to apply.

    A version ("ver") condition is only honored when the rule also carries a "component"
    condition (per the OneSettings schema, "ver" requires "component"). A rule that specifies
    "ver" without "component" is treated as non-matching. Because "component" is a regular
    condition, it is still matched against the current profile like any other field.

    :param override_rule: Dictionary of conditions that must all be true
    :type override_rule: Dict[str, Any]
    :return: True if all conditions in the rule match, False otherwise
    :rtype: bool
    """
    # Validate input
    if not override_rule:
        return False

    # A "ver" condition requires a "component" condition to be present in the same rule.
    if "ver" in override_rule and "component" not in override_rule:
        return False

    # All conditions in this rule must match
    for condition_key, condition_value in override_rule.items():
        if not _matches_condition(condition_key, condition_value):
            # If any condition doesn't match, this rule doesn't apply
            return False

    # All conditions in this rule matched
    return True


# pylint:disable=too-many-return-statements
def _matches_condition(condition_key: str, condition_value: Any) -> bool:
    """Check if a specific condition matches the current configuration profile.

    :param condition_key: The profile attribute to check (os, ver, component, etc.)
    :type condition_key: str
    :param condition_value: The expected value(s) or constraints for the condition
    :type condition_value: Any
    :return: True if the condition matches, False otherwise
    :rtype: bool
    """
    profile = _ConfigurationProfile

    # Validate condition_key
    if not condition_key or condition_value is None:
        return False

    if condition_key == "os":
        # OS condition - exact match (case-insensitive)
        return profile.os.lower() == str(condition_value).lower()

    if condition_key == "ver":
        # Version condition - exact match
        return profile.version == str(condition_value)

    if condition_key == "component":
        # Component condition - exact match
        return profile.component == str(condition_value)

    if condition_key == "rp":
        # Resource provider condition - exact match
        return profile.rp == str(condition_value)

    if condition_key == "region":
        # Region condition - exact match
        return profile.region == str(condition_value)

    if condition_key == "attach":
        # Attach type condition - exact match
        return profile.attach == str(condition_value)

    if condition_key == "ikey":
        # Instrumentation key condition - exact match, case-insensitive (GUIDs are hex)
        return profile.ikey.lower() == str(condition_value).lower()

    # Unknown condition key
    return False


# cSpell:enable
