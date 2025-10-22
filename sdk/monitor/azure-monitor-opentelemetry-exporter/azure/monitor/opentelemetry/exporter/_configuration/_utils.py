# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable
from typing import Dict, Optional, Any
import json
import logging
# mypy: disable-error-code="import-untyped"
import requests

from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
    _ONE_SETTINGS_CHANGE_VERSION_KEY,
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

    @classmethod
    def fill(cls, **kwargs) -> None:
        """Update only the class variables that are provided in kwargs and haven't been updated yet."""
        if 'os' in kwargs and cls.os == "":
            cls.os = kwargs['os']
        if 'version' in kwargs and cls.version == "":
            cls.version = kwargs['version']
        if 'component' in kwargs and cls.component == "":
            cls.component = kwargs['component']
        if 'rp' in kwargs and cls.rp == "":
            cls.rp = kwargs['rp']
        if 'attach' in kwargs and cls.attach == "":
            cls.attach = kwargs['attach']
        if 'region' in kwargs and cls.region == "":
            cls.region = kwargs['region']


class OneSettingsResponse:
    """Response object containing OneSettings API response data.

    This class encapsulates the parsed response from a OneSettings API call,
    including configuration settings, version information, error indicators and metadata.

    Attributes:
        etag (Optional[str]): ETag header value for caching and conditional requests
        refresh_interval (int): Interval in seconds for the next configuration refresh
        settings (Dict[str, str]): Dictionary of configuration key-value pairs
        version (Optional[int]): Configuration version number for change tracking
        status_code (int): HTTP status code from the response
        has_exception (bool): True if the request resulted in a transient error (network error, timeout, etc.)
    """

    def __init__(
        self,
        etag: Optional[str] = None,
        refresh_interval: int = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
        settings: Optional[Dict[str, str]] = None,
        version: Optional[int] = None,
        status_code: int = 200,
        has_exception: bool = False
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
            has_exception (bool, optional): Indicates if request failed with a transient error. Defaults to False.
        """
        self.etag = etag
        self.refresh_interval = refresh_interval
        self.settings = settings or {}
        self.version = version
        self.status_code = status_code
        self.has_exception = has_exception


def make_onesettings_request(url: str, query_dict: Optional[Dict[str, str]] = None,
                           headers: Optional[Dict[str, str]] = None) -> OneSettingsResponse:
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
        result.raise_for_status()  # Raises an exception for 4XX/5XX responses

        return _parse_onesettings_response(result)
    except requests.exceptions.Timeout as ex:
        logger.warning("OneSettings request timed out: %s", str(ex))
        return OneSettingsResponse(has_exception=True)
    except requests.exceptions.RequestException as ex:
        logger.warning("Failed to fetch configuration from OneSettings: %s", str(ex))
        return OneSettingsResponse(has_exception=True)
    except json.JSONDecodeError as ex:
        logger.warning("Failed to parse OneSettings response: %s", str(ex))
        return OneSettingsResponse(has_exception=True)
    except Exception as ex:  # pylint: disable=broad-exception-caught
        logger.warning("Unexpected error while fetching configuration: %s", str(ex))
        return OneSettingsResponse(has_exception=True)


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
        "live_metrics": {
            "default": "disabled",  # Feature is disabled by default
            "override": [
                {"os": "w"},  # Enable on Windows (any version)
                {"os": "l", "ver": {"min": "1.0.0b20"}},  # Enable on Linux with version >= 1.0.0b20
                {"component": "ext", "rp": "f"}  # Enable if component is exporter AND rp is functions
            ]
        },
        "sampling": {
            "default": "enabled",  # Feature is enabled by default
            "override": [
                {"os": ["w", "l"]},  # Disable on Windows OR Linux
                {"ver": {"max": "1.0.0"}},  # Disable on versions <= 1.0.0
                # Disable if attach is integratedauto/manual AND region is eastus
                {"attach": ["i", "m"], "region": "eastus"}
            ]
        },
        "profiling": {
            "default": "disabled",
            "override": [
                {"os": "w", "ver": {"min": "2.0.0", "max": "3.0.0"}},  # Enable on Windows with version 2.0.0-3.0.0
                # Enable if component is exporter AND rp is functions/appsvc AND region is westus/eastus
                {"component": "ext", "rp": ["f", "a"], "region": ["westus", "eastus"]}
            ]
        },
        "debug_logging": {
            "default": "enabled",
            "override": [
                {"ver": "1.0.0b1"},  # Disable on exact version 1.0.0b1
                # Disable on Linux with distro component, manual attach, and AKS runtime
                {"os": "l", "component": "dst", "attach": "m", "rp": "k"}
            ]
        }
    }

    Available condition fields:
    - os: Operating system ("w"=windows, "l"=linux, "d"=darwin, "u"=unknown, etc.) - supports single value or list
    - ver: Version constraints - supports exact string match or dict with "min"/"max" keys
    - component: Component type ("ext"=exporter, "dst"=distro) - exact string match
    - rp: Runtime platform ("u"=unknown, "f"=functions, "a"=appsvc, "k"=aks) - supports single value or list
    - region: Host region ("westus", "eastus", etc.) - supports single value or list
    - attach: Attachment type ("m"=manual, "i"=integratedauto) - supports single value or list

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

    :param override_rule: Dictionary of conditions that must all be true
    :type override_rule: Dict[str, Any]
    :return: True if all conditions in the rule match, False otherwise
    :rtype: bool
    """
    # Validate input
    if not override_rule:
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
        # OS condition - check if current OS is in the list
        if isinstance(condition_value, list):
            return profile.os.lower() in [str(os).lower() for os in condition_value]
        return profile.os.lower() == str(condition_value).lower()

    if condition_key == "ver":
        # Version condition - support min/max version checks
        if isinstance(condition_value, dict):
            current_version = profile.version
            if not current_version:
                return False

            # Check minimum version
            if "min" in condition_value:
                min_version = condition_value["min"]
                if not _compare_versions(current_version, str(min_version), ">="):
                    return False

            # Check maximum version
            if "max" in condition_value:
                max_version = condition_value["max"]
                if not _compare_versions(current_version, str(max_version), "<="):
                    return False

            return True
        # Exact version match
        return profile.version == str(condition_value)

    if condition_key == "component":
        # Component condition - exact match
        return profile.component == str(condition_value)

    if condition_key == "rp":
        # Runtime platform condition - check if current RP is in the list
        if isinstance(condition_value, list):
            return profile.rp in [str(rp) for rp in condition_value]
        return profile.rp == str(condition_value)

    if condition_key == "region":
        # Region condition - check if current region is in the list
        if isinstance(condition_value, list):
            return profile.region in [str(region) for region in condition_value]
        return profile.region == str(condition_value)

    if condition_key == "attach":
        # Attach type condition - check if current attach type is in the list
        if isinstance(condition_value, list):
            return profile.attach in [str(attach) for attach in condition_value]
        return profile.attach == str(condition_value)

    # Unknown condition key
    return False


def _compare_versions(version1: str, version2: str, operator: str) -> bool:
    """Compare two version strings using the specified operator.

    Handles standard semantic versioning with beta versions (e.g., "1.0.0b28").

    :param version1: First version string (e.g., "2.9.1", "1.0.0b28")
    :type version1: str
    :param version2: Second version string (e.g., "2.9.0", "1.0.0b20")
    :type version2: str
    :param operator: Comparison operator (">=", "<=", "==", ">", "<")
    :type operator: str
    :return: True if the comparison is satisfied, False otherwise
    :rtype: bool
    """
    try:
        # Parse version strings into comparable tuples
        v1_parts = _parse_version_with_beta(version1)
        v2_parts = _parse_version_with_beta(version2)

        # Compare tuples
        if operator == ">=":
            return v1_parts >= v2_parts
        if operator == "<=":
            return v1_parts <= v2_parts
        if operator == "==":
            return v1_parts == v2_parts
        if operator == ">":
            return v1_parts > v2_parts
        if operator == "<":
            return v1_parts < v2_parts
        return False
    except (ValueError, AttributeError):
        # If version parsing fails, fall back to string comparison
        if operator == ">=":
            return version1 >= version2
        if operator == "<=":
            return version1 <= version2
        if operator == "==":
            return version1 == version2
        if operator == ">":
            return version1 > version2
        if operator == "<":
            return version1 < version2
        return False


def _parse_version_with_beta(version: str) -> tuple:
    """Parse a version string that may contain beta suffix into a comparable tuple.

    Examples:
    - "1.0.0" -> (1, 0, 0, float('inf'))  # Release version sorts after beta
    - "1.0.0b28" -> (1, 0, 0, 28)        # Beta version with number
    - "2.1.5b1" -> (2, 1, 5, 1)          # Beta version with number

    :param version: Version string to parse
    :type version: str
    :return: Tuple representing version for comparison
    :rtype: tuple
    """
    # Check if version contains beta suffix
    if 'b' in version:
        # Split on 'b' to separate base version and beta number
        base_version, beta_part = version.split('b', 1)
        base_parts = [int(x) for x in base_version.split('.')]
        beta_number = int(beta_part) if beta_part.isdigit() else 0
        return tuple(base_parts + [beta_number])
    # Release version - use infinity for beta part so it sorts after beta versions
    base_parts = [int(x) for x in version.split('.')]
    return tuple(base_parts + [float('inf')])

# cSpell:enable
