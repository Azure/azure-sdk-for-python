# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
import random
import time
import datetime
from importlib.metadata import version, PackageNotFoundError
from threading import Lock
import logging
from typing import (
    Any,
    Dict,
    Mapping,
    Optional,
    overload,
    List,
    Tuple,
    Union,
    Iterator,
    KeysView,
    ItemsView,
    ValuesView,
    TypeVar,
)
from ._models import SettingSelector
from ._constants import (
    REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE,
    ServiceFabricEnvironmentVariable,
    AzureFunctionEnvironmentVariable,
    AzureWebAppEnvironmentVariable,
    ContainerAppEnvironmentVariable,
    KubernetesEnvironmentVariable,
    EMPTY_LABEL,
    CUSTOM_FILTER_KEY,
    PERCENTAGE_FILTER_KEY,
    TIME_WINDOW_FILTER_KEY,
    TARGETING_FILTER_KEY,
)

JSON = Mapping[str, Any]
_T = TypeVar("_T")
logger = logging.getLogger(__name__)

min_uptime = 5


def delay_failure(start_time: datetime.datetime) -> None:
    # We want to make sure we are up a minimum amount of time before we kill the process. Otherwise, we could get stuck
    # in a quick restart loop.
    min_time = datetime.timedelta(seconds=min_uptime)
    current_time = datetime.datetime.now()
    if current_time - start_time < min_time:
        time.sleep((min_time - (current_time - start_time)).total_seconds())


def update_correlation_context_header(
    headers,
    request_type,
    replica_count,
    uses_feature_flags,
    feature_filters_used,
    uses_key_vault,
    uses_load_balancing,
    is_failover_request,
) -> Dict[str, str]:
    if os.environ.get(REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE, default="").lower() == "true":
        return headers
    correlation_context = "RequestType=" + request_type

    if len(feature_filters_used) > 0:
        filters_used = ""
        if CUSTOM_FILTER_KEY in feature_filters_used:
            filters_used = CUSTOM_FILTER_KEY
        if PERCENTAGE_FILTER_KEY in feature_filters_used:
            filters_used += ("+" if filters_used else "") + PERCENTAGE_FILTER_KEY
        if TIME_WINDOW_FILTER_KEY in feature_filters_used:
            filters_used += ("+" if filters_used else "") + TIME_WINDOW_FILTER_KEY
        if TARGETING_FILTER_KEY in feature_filters_used:
            filters_used += ("+" if filters_used else "") + TARGETING_FILTER_KEY
        correlation_context += ",Filters=" + filters_used

    correlation_context += _uses_feature_flags(uses_feature_flags)

    if uses_key_vault:
        correlation_context += ",UsesKeyVault"
    host_type = ""
    if AzureFunctionEnvironmentVariable in os.environ:
        host_type = "AzureFunction"
    elif AzureWebAppEnvironmentVariable in os.environ:
        host_type = "AzureWebApp"
    elif ContainerAppEnvironmentVariable in os.environ:
        host_type = "ContainerApp"
    elif KubernetesEnvironmentVariable in os.environ:
        host_type = "Kubernetes"
    elif ServiceFabricEnvironmentVariable in os.environ:
        host_type = "ServiceFabric"
    if host_type:
        correlation_context += ",Host=" + host_type

    if replica_count > 0:
        correlation_context += ",ReplicaCount=" + str(replica_count)

    if is_failover_request:
        correlation_context += ",Failover"

    if uses_load_balancing:
        correlation_context += ",Features=LB"

    headers["Correlation-Context"] = correlation_context
    return headers


def _uses_feature_flags(uses_feature_flags):
    if not uses_feature_flags:
        return ""
    package_name = "featuremanagement"
    try:
        feature_management_version = version(package_name)
        if feature_management_version:
            return ",FMPyVer=" + feature_management_version
    except PackageNotFoundError:
        pass
    return ""


def is_json_content_type(content_type: str) -> bool:
    if not content_type:
        return False

    content_type = content_type.strip().lower()
    mime_type = content_type.split(";")[0].strip()

    type_parts = mime_type.split("/")
    if len(type_parts) != 2:
        return False

    (main_type, sub_type) = type_parts
    if main_type != "application":
        return False

    sub_types = sub_type.split("+")
    if "json" in sub_types:
        return True

    return False


def _build_sentinel(setting: Union[str, Tuple[str, str]]) -> Tuple[str, str]:
    try:
        key, label = setting  # type:ignore
    except IndexError:
        key = setting
        label = EMPTY_LABEL
    if "*" in key or "*" in label:
        raise ValueError("Wildcard key or label filters are not supported for refresh.")
    return key, label


def sdk_allowed_kwargs(kwargs):
    allowed_kwargs = [
        "headers",
        "request_id",
        "user_agent",
        "logging_enable",
        "logger",
        "response_encoding",
        "raw_request_hook",
        "raw_response_hook",
        "network_span_namer",
        "tracing_attributes",
        "permit_redirects",
        "redirect_max",
        "retry_total",
        "retry_connect",
        "retry_read",
        "retry_status",
        "retry_backoff_factor",
        "retry_backoff_max",
        "retry_mode",
        "timeout",
        "connection_timeout",
        "read_timeout",
        "connection_verify",
        "connection_cert",
        "proxies",
        "cookies",
        "connection_data_block_size",
    ]
    return {k: v for k, v in kwargs.items() if k in allowed_kwargs}


class _RefreshTimer:
    """
    A timer that tracks the next refresh time and the number of attempts.
    """

    def __init__(self, **kwargs):
        self._interval: int = kwargs.pop("refresh_interval", 30)
        if self._interval < 1:
            raise ValueError("Refresh interval must be greater than or equal to 1 second.")
        self._next_refresh_time: float = time.time() + self._interval
        self._attempts: int = 1
        self._min_backoff: int = (
            kwargs.get("min_backoff", 30) if kwargs.get("min_backoff", 30) <= self._interval else self._interval
        )
        self._max_backoff: int = 600 if 600 <= self._interval else self._interval

    def reset(self) -> None:
        self._next_refresh_time = time.time() + self._interval
        self._attempts = 1

    def backoff(self) -> None:
        self._next_refresh_time = time.time() + self._calculate_backoff() / 1000
        self._attempts += 1

    def needs_refresh(self) -> bool:
        return time.time() >= self._next_refresh_time

    def _calculate_backoff(self) -> float:
        max_attempts = 63
        millisecond = 1000  # 1 Second in milliseconds

        min_backoff_milliseconds = self._min_backoff * millisecond
        max_backoff_milliseconds = self._max_backoff * millisecond

        if self._max_backoff <= self._min_backoff:
            return min_backoff_milliseconds

        calculated_milliseconds = max(1, min_backoff_milliseconds) * (1 << min(self._attempts, max_attempts))

        if calculated_milliseconds > max_backoff_milliseconds or calculated_milliseconds <= 0:
            calculated_milliseconds = max_backoff_milliseconds

        return min_backoff_milliseconds + (
            random.uniform(0.0, 1.0) * (calculated_milliseconds - min_backoff_milliseconds)  # nosec
        )


class AzureAppConfigurationProviderBase(Mapping[str, Union[str, JSON]]):  # pylint: disable=too-many-instance-attributes
    """
    Provides a dictionary-like interface to Azure App Configuration settings. Enables loading of sets of configuration
    settings from Azure App Configuration into a Python application. Enables trimming of prefixes from configuration
    keys. Enables resolution of Key Vault references in configuration settings.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._origin_endpoint = kwargs.get("endpoint", None)
        self._dict: Dict[str, Any] = {}
        self._selects: List[SettingSelector] = kwargs.pop(
            "selects", [SettingSelector(key_filter="*", label_filter=EMPTY_LABEL)]
        )

        trim_prefixes: List[str] = kwargs.pop("trim_prefixes", [])
        self._trim_prefixes: List[str] = sorted(trim_prefixes, key=len, reverse=True)

        refresh_on: List[Tuple[str, str]] = kwargs.pop("refresh_on", None) or []
        self._refresh_on: Mapping[Tuple[str, str], Optional[str]] = {_build_sentinel(s): None for s in refresh_on}
        self._refresh_timer: _RefreshTimer = _RefreshTimer(**kwargs)
        self._keyvault_credential = kwargs.pop("keyvault_credential", None)
        self._secret_resolver = kwargs.pop("secret_resolver", None)
        self._keyvault_client_configs = kwargs.pop("keyvault_client_configs", {})
        self._uses_key_vault = (
            self._keyvault_credential is not None
            or (self._keyvault_client_configs is not None and len(self._keyvault_client_configs) > 0)
            or self._secret_resolver is not None
        )
        self._feature_flag_enabled = kwargs.pop("feature_flag_enabled", False)
        self._feature_flag_selectors = kwargs.pop("feature_flag_selectors", [SettingSelector(key_filter="*")])
        self._refresh_on_feature_flags: Mapping[Tuple[str, str], Optional[str]] = {}
        self._feature_flag_refresh_timer: _RefreshTimer = _RefreshTimer(**kwargs)
        self._feature_flag_refresh_enabled = kwargs.pop("feature_flag_refresh_enabled", False)
        self._feature_filter_usage: Mapping[str, bool] = {}
        self._uses_load_balancing = kwargs.pop("load_balancing_enabled", False)
        self._update_lock = Lock()
        self._refresh_lock = Lock()

    def _process_key_name(self, config):
        trimmed_key = config.key
        # Trim the key if it starts with one of the prefixes provided
        for trim in self._trim_prefixes:
            if config.key.startswith(trim):
                trimmed_key = config.key[len(trim) :]
                break
        return trimmed_key

    def __getitem__(self, key: str) -> Any:
        # pylint:disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
        """
        Returns the value of the specified key.
        """
        with self._update_lock:
            return self._dict[key]

    def __iter__(self) -> Iterator[str]:
        return self._dict.__iter__()

    def __len__(self) -> int:
        return len(self._dict)

    def __contains__(self, __x: object) -> bool:
        # pylint:disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
        """
        Returns True if the configuration settings contains the specified key.
        """
        return self._dict.__contains__(__x)

    def keys(self) -> KeysView[str]:
        """
        Returns a list of keys loaded from Azure App Configuration.

        :return: A list of keys loaded from Azure App Configuration.
        :rtype: KeysView[str]
        """
        with self._update_lock:
            return self._dict.keys()

    def items(self) -> ItemsView[str, Union[str, Mapping[str, Any]]]:
        """
        Returns a set-like object of key-value pairs loaded from Azure App Configuration. Any values that are Key Vault
         references will be resolved.

        :return: A set-like object of key-value pairs loaded from Azure App Configuration.
        :rtype: ItemsView[str, Union[str, Mapping[str, Any]]]
        """
        with self._update_lock:
            return self._dict.items()

    def values(self) -> ValuesView[Union[str, Mapping[str, Any]]]:
        """
        Returns a list of values loaded from Azure App Configuration. Any values that are Key Vault references will be
        resolved.

        :return: A list of values loaded from Azure App Configuration. The values are either Strings or JSON objects,
         based on there content type.
        :rtype: ValuesView[Union[str, Mapping[str, Any]]]
        """
        with self._update_lock:
            return (self._dict).values()

    @overload
    def get(self, key: str, default: None = None) -> Union[str, JSON, None]: ...

    @overload
    def get(self, key: str, default: Union[str, JSON, _T]) -> Union[str, JSON, _T]:  # pylint: disable=signature-differs
        ...

    def get(self, key: str, default: Optional[Union[str, JSON, _T]] = None) -> Union[str, JSON, _T, None]:
        """
        Returns the value of the specified key. If the key does not exist, returns the default value.

        :param str key: The key of the value to get.
        :param default: The default value to return.
        :type: str or None
        :return: The value of the specified key.
        :rtype: Union[str, JSON]
        """
        with self._update_lock:
            return self._dict.get(key, default)

    def __ne__(self, other: Any) -> bool:
        return not self == other
