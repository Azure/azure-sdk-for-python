# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, TypeVar
import json
import logging

# mypy: disable-error-code="import-untyped"
import requests  # pylint: disable=networking-import-outside-azure-core-transport

from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


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
        # requests honors standard proxy environment variables (HTTP_PROXY/HTTPS_PROXY/NO_PROXY)
        # automatically, so no explicit proxy configuration is needed here.
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


@dataclass(frozen=True)
class _OverrideRule:
    """Parsed OneSettings override rule."""

    conditions: Dict[str, Any]
    value: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Any) -> Optional["_OverrideRule"]:
        """Parse an override rule and separate its result value from profile conditions."""
        if not isinstance(data, dict):
            return None

        conditions = {key: value for key, value in data.items() if key != "value"}
        if not conditions:
            return None

        value = data.get("value")
        if "value" in data and not isinstance(value, str):
            return None

        return cls(conditions=conditions, value=value)


@dataclass(frozen=True)
class _FeatureConfig:
    """Parsed OneSettings feature configuration."""

    default: str
    overrides: List[_OverrideRule]

    @classmethod
    def parse(cls, data: Any) -> Optional["_FeatureConfig"]:
        """Parse a feature configuration from its JSON string."""
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                logger.debug("Failed to decode OneSettings feature configuration: %s", data)
                return None

        # Accept dictionaries for compatibility with callers that construct settings in memory.
        if not isinstance(data, dict) or not isinstance(data.get("default"), str):
            return None

        raw_overrides = data.get("override", [])
        if not isinstance(raw_overrides, list):
            raw_overrides = []

        overrides = []
        for raw_override in raw_overrides:
            override = _OverrideRule.from_dict(raw_override)
            if override is not None:
                overrides.append(override)

        return cls(default=data["default"], overrides=overrides)


# mypy: disable-error-code="no-any-return"
def evaluate_feature(
    feature_key: str,
    settings: Dict[str, str],
    value_type: Optional[Callable[[str], T]] = None,
) -> Any:
    """Evaluate a setting based on the configuration profile and override rules.

    This function compares the current _ConfigurationProfile against feature-specific
    override conditions and returns either the matching override value or the default.
    The legacy enabled/disabled format is converted to booleans.

    :param feature_key: The name of the feature to evaluate
    :type feature_key: str
    :param settings: Dictionary containing JSON-encoded feature configurations
    :type settings: Dict[str, str]
    :param value_type: Optional converter applied to the default or matching override value
    :type value_type: Optional[Callable[[str], T]]
    :return: The evaluated setting value, or None if inputs are invalid
    :rtype: Any

    Example cached settings:
    settings = {
        "FEATURE_LIVE_METRICS": json.dumps({
            "default": "disabled",
            "override": [
                {"os": "windows"},
                {"os": "linux", "ver": "1.0.0b21", "component": "dst"},
                {"ikey": "12345678-1234-1234-1234-123456789abc"},
                {"component": "dst"}
            ]
        }),
        "EXPORT_INTERVAL_SECONDS": json.dumps({
            "default": "60",
            "override": [
                {"rp": ["aks"], "region": ["eastus"], "value": "300"}
            ]
        })
    }

    Available condition fields (each field accepts one value or a list of values):
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
    - If ANY rule matches completely, its "value" is returned
    - Legacy rules without "value" flip enabled/disabled defaults
    - If NO rules match, the default state is returned
    """
    # Validate inputs - return None for invalid inputs
    if not feature_key or not isinstance(settings, dict):
        return None

    if feature_key not in settings:
        return None

    # Feature setting values are JSON strings containing their default and override rules.
    feature_config = _FeatureConfig.parse(settings[feature_key])
    if feature_config is None:
        return None

    default_value = _normalize_setting_value(feature_config.default, value_type)

    # If no override conditions, return the default value.
    if not feature_config.overrides:
        return default_value

    # Check override conditions - if ANY override rule matches completely, apply its value.
    for override_rule in feature_config.overrides:
        if _matches_override_rule(override_rule.conditions):
            # Example: {"rp": ["aks"], "region": ["eastus"], "value": "300"}
            if override_rule.value is not None:
                override_value = _normalize_setting_value(override_rule.value, value_type)
                return default_value if override_value is None else override_value
            # For boolean settings, a matching legacy rule without a value uses the
            # complement of the default.
            if isinstance(default_value, bool):
                return not default_value
            return default_value

    # No override rules matched - return the default value.
    return default_value


def _normalize_setting_value(value: Any, value_type: Optional[Callable[[str], T]] = None) -> Any:
    """Convert a setting with the requested type or normalize legacy feature-state strings."""
    if value_type is not None:
        if not isinstance(value, str):
            return None
        try:
            return value_type(value)
        except (TypeError, ValueError):
            logger.debug("Failed to convert OneSettings value %r using %s", value, value_type)
            return None

    if isinstance(value, str):
        if value.lower() == "enabled":
            return True
        if value.lower() == "disabled":
            return False
    return value


# mypy: disable-error-code="no-any-return"
def _matches_override_rule(conditions: Dict[str, Any]) -> bool:
    """Check if all conditions in an override rule match the current configuration profile.

    All conditions within a single override rule must match for the rule to apply.

    A version ("ver") condition is only honored when the rule also carries a "component"
    condition (per the OneSettings schema, "ver" requires "component"). A rule that specifies
    "ver" without "component" is treated as non-matching. Because "component" is a regular
    condition, it is still matched against the current profile like any other field.

    :param conditions: Dictionary of conditions that must all be true
    :type conditions: Dict[str, Any]
    :return: True if all conditions in the rule match, False otherwise
    :rtype: bool
    """
    if not isinstance(conditions, dict) or not conditions:
        return False

    # A "ver" condition requires a "component" condition to be present in the same rule.
    if "ver" in conditions and "component" not in conditions:
        return False

    # All conditions in this rule must match
    for condition_key, condition_value in conditions.items():
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

    if isinstance(condition_value, list):
        return bool(condition_value) and any(
            _matches_condition(condition_key, candidate) for candidate in condition_value
        )

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
