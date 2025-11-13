# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import datetime
import locale
from os import environ
from os.path import isdir
import platform
import threading
import time
import warnings
import hashlib
from typing import Callable, Dict, Any, Optional

from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util import ns_to_iso_str
from opentelemetry.util.types import Attributes

from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.monitor.opentelemetry.exporter._generated.models import ContextTagKeys, TelemetryItem
from azure.monitor.opentelemetry.exporter._version import VERSION as ext_version
from azure.monitor.opentelemetry.exporter._constants import (
    _AKS_ARM_NAMESPACE_ID,
    _DEFAULT_AAD_SCOPE,
    _FUNCTIONS_WORKER_RUNTIME,
    _INSTRUMENTATIONS_BIT_MAP,
    _KUBERNETES_SERVICE_HOST,
    _PYTHON_APPLICATIONINSIGHTS_ENABLE_TELEMETRY,
    _WEBSITE_SITE_NAME,
)
from azure.monitor.opentelemetry.exporter._constants import (
    _TYPE_MAP,
    _UNKNOWN,
    _RP_Names,
)

opentelemetry_version = ""

# Workaround for missing version file
try:
    from importlib.metadata import version

    opentelemetry_version = version("opentelemetry-sdk")
except ImportError:
    # Temporary workaround for <Py3.8
    # importlib-metadata causing issues in CI
    import pkg_resources  # type: ignore

    opentelemetry_version = pkg_resources.get_distribution("opentelemetry-sdk").version


# Azure App Service


def _is_on_app_service():
    return environ.get(_WEBSITE_SITE_NAME) is not None


# Functions


def _is_on_functions():
    return environ.get(_FUNCTIONS_WORKER_RUNTIME) is not None


# AKS


def _is_on_aks():
    return _AKS_ARM_NAMESPACE_ID in environ or _KUBERNETES_SERVICE_HOST in environ


# Attach


def _is_attach_enabled():
    if _is_on_functions():
        return environ.get(_PYTHON_APPLICATIONINSIGHTS_ENABLE_TELEMETRY) == "true"
    if _is_on_app_service():
        return isdir("/agents/python/")
    if _is_on_aks():
        return _AKS_ARM_NAMESPACE_ID in environ
    return False


def _get_rp():
    rp = "u"
    if _is_on_functions():
        rp = "f"
    elif _is_on_app_service():
        rp = "a"
    # TODO: Add VM scenario outside statsbeat
    # elif _is_on_vm():
    #     rp = 'v'
    elif _is_on_aks():
        rp = "k"
    return rp


def _get_os():
    os = "u"
    system = platform.system()
    if system == "Linux":
        os = "l"
    elif system == "Windows":
        os = "w"
    return os

def _get_attach_type():
    attach_type = "m"
    if _is_attach_enabled():
        attach_type = "i"
    return attach_type

def _get_sdk_version_prefix():
    sdk_version_prefix = ""
    rp = _get_rp()
    os = _get_os()
    attach_type = _get_attach_type()
    sdk_version_prefix = "{}{}{}_".format(rp, os, attach_type)

    return sdk_version_prefix


def _get_sdk_version():
    return "{}py{}:otel{}:ext{}".format(
        _get_sdk_version_prefix(), platform.python_version(), opentelemetry_version, ext_version
    )


def _getlocale():
    try:
        with warnings.catch_warnings():
            # temporary work-around for https://github.com/python/cpython/issues/82986
            # by continuing to use getdefaultlocale() even though it has been deprecated.
            # we ignore the deprecation warnings to reduce noise
            warnings.simplefilter("ignore", category=DeprecationWarning)
            # pylint: disable=deprecated-method
            return locale.getdefaultlocale()[0]
    except AttributeError:
        # locale.getlocal() has issues on Windows: https://github.com/python/cpython/issues/82986
        # Use this as a fallback if locale.getdefaultlocale() doesn't exist (>Py3.13)
        return locale.getlocale()[0]


azure_monitor_context = {
    ContextTagKeys.AI_DEVICE_ID: platform.node(),
    ContextTagKeys.AI_DEVICE_LOCALE: _getlocale(),
    ContextTagKeys.AI_DEVICE_TYPE: "Other",
    ContextTagKeys.AI_INTERNAL_SDK_VERSION: _get_sdk_version(),
}


def ns_to_duration(nanoseconds: int) -> str:
    value = (nanoseconds + 500000) // 1000000  # duration in milliseconds
    value, milliseconds = divmod(value, 1000)
    value, seconds = divmod(value, 60)
    value, minutes = divmod(value, 60)
    days, hours = divmod(value, 24)
    return "{:d}.{:02d}:{:02d}:{:02d}.{:03d}".format(days, hours, minutes, seconds, milliseconds)


# Replicate .netDateTime.Ticks(), which is the UTC time, expressed as the number
# of 100-nanosecond intervals that have elapsed since 12:00:00 midnight on
# January 1, 0001.
def _ticks_since_dot_net_epoch():
    # Since time.time() is the elapsed time since UTC January 1, 1970, we have
    # to shift this start time, and  then multiply by 10^7 to get the number of
    # 100-nanosecond intervals
    shift_time = int((datetime.datetime(1970, 1, 1, 0, 0, 0) - datetime.datetime(1, 1, 1, 0, 0, 0)).total_seconds()) * (
        10**7
    )
    # Add shift time to 100-ns intervals since time.time()
    return int(time.time() * (10**7)) + shift_time


_INSTRUMENTATIONS_BIT_MASK = 0
_INSTRUMENTATIONS_BIT_MASK_LOCK = threading.Lock()


def get_instrumentations():
    return _INSTRUMENTATIONS_BIT_MASK


def add_instrumentation(instrumentation_name: str):
    with _INSTRUMENTATIONS_BIT_MASK_LOCK:
        global _INSTRUMENTATIONS_BIT_MASK  # pylint: disable=global-statement
        instrumentation_bits = _INSTRUMENTATIONS_BIT_MAP.get(instrumentation_name, 0)
        _INSTRUMENTATIONS_BIT_MASK |= instrumentation_bits


def remove_instrumentation(instrumentation_name: str):
    with _INSTRUMENTATIONS_BIT_MASK_LOCK:
        global _INSTRUMENTATIONS_BIT_MASK  # pylint: disable=global-statement
        instrumentation_bits = _INSTRUMENTATIONS_BIT_MAP.get(instrumentation_name, 0)
        _INSTRUMENTATIONS_BIT_MASK &= ~instrumentation_bits


class PeriodicTask(threading.Thread):
    """Thread that periodically calls a given function.

    :type interval: int or float
    :param interval: Seconds between calls to the function.

    :type function: function
    :param function: The function to call.

    :type args: list
    :param args: The args passed in while calling `function`.

    :type kwargs: dict
    :param args: The kwargs passed in while calling `function`.
    """

    def __init__(self, interval: int, function: Callable, *args: Any, **kwargs: Any):
        super().__init__(name=kwargs.pop("name", None))
        self.interval = interval
        self.function = function
        self.args = args or []  # type: ignore
        self.kwargs = kwargs or {}
        self.finished = threading.Event()

    def run(self):
        wait_time = self.interval
        while not self.finished.wait(wait_time):
            start_time = time.time()
            self.function(*self.args, **self.kwargs)
            elapsed_time = time.time() - start_time
            wait_time = max(self.interval - elapsed_time, 0)

    def cancel(self):
        self.finished.set()


def _create_telemetry_item(timestamp: int) -> TelemetryItem:
    return TelemetryItem(
        name="",
        instrumentation_key="",
        tags=dict(azure_monitor_context),  # type: ignore
        time=ns_to_iso_str(timestamp),  # type: ignore
    )


def _populate_part_a_fields(resource: Resource):
    tags = {}
    if resource and resource.attributes:
        device_id = resource.attributes.get(ResourceAttributes.DEVICE_ID)
        device_model = resource.attributes.get(ResourceAttributes.DEVICE_MODEL_NAME)
        device_make = resource.attributes.get(ResourceAttributes.DEVICE_MANUFACTURER)
        app_version = resource.attributes.get(ResourceAttributes.SERVICE_VERSION)
        tags[ContextTagKeys.AI_CLOUD_ROLE] = _get_cloud_role(resource)
        tags[ContextTagKeys.AI_CLOUD_ROLE_INSTANCE] = _get_cloud_role_instance(resource)
        tags[ContextTagKeys.AI_INTERNAL_NODE_NAME] = tags[ContextTagKeys.AI_CLOUD_ROLE_INSTANCE]
        if device_id:
            tags[ContextTagKeys.AI_DEVICE_ID] = device_id  # type: ignore
        if device_model:
            tags[ContextTagKeys.AI_DEVICE_MODEL] = device_model  # type: ignore
        if device_make:
            tags[ContextTagKeys.AI_DEVICE_OEM_NAME] = device_make  # type: ignore
        if app_version:
            tags[ContextTagKeys.AI_APPLICATION_VER] = app_version  # type: ignore

    return tags


# pylint:disable=too-many-return-statements
def _get_cloud_role(resource: Resource) -> str:
    cloud_role = ""
    service_name = resource.attributes.get(ResourceAttributes.SERVICE_NAME)
    if service_name:
        service_namespace = resource.attributes.get(ResourceAttributes.SERVICE_NAMESPACE)
        if service_namespace:
            cloud_role = str(service_namespace) + "." + str(service_name)
        else:
            cloud_role = str(service_name)
        # If service_name starts with "unknown_service", only use it if kubernetes attributes are not present.
        if not str(service_name).startswith("unknown_service"):
            return cloud_role
    k8s_dep_name = resource.attributes.get(ResourceAttributes.K8S_DEPLOYMENT_NAME)
    if k8s_dep_name:
        return k8s_dep_name  # type: ignore
    k8s_rep_set_name = resource.attributes.get(ResourceAttributes.K8S_REPLICASET_NAME)
    if k8s_rep_set_name:
        return k8s_rep_set_name  # type: ignore
    k8s_stateful_set_name = resource.attributes.get(ResourceAttributes.K8S_STATEFULSET_NAME)
    if k8s_stateful_set_name:
        return k8s_stateful_set_name  # type: ignore
    k8s_job_name = resource.attributes.get(ResourceAttributes.K8S_JOB_NAME)
    if k8s_job_name:
        return k8s_job_name  # type: ignore
    k8s_cronjob_name = resource.attributes.get(ResourceAttributes.K8S_CRONJOB_NAME)
    if k8s_cronjob_name:
        return k8s_cronjob_name  # type: ignore
    k8s_daemonset_name = resource.attributes.get(ResourceAttributes.K8S_DAEMONSET_NAME)
    if k8s_daemonset_name:
        return k8s_daemonset_name  # type: ignore
    # If service_name starts with "unknown_service", only use it if kubernetes attributes are not present.
    return cloud_role


def _get_cloud_role_instance(resource: Resource) -> str:
    service_instance_id = resource.attributes.get(ResourceAttributes.SERVICE_INSTANCE_ID)
    if service_instance_id:
        return service_instance_id  # type: ignore
    k8s_pod_name = resource.attributes.get(ResourceAttributes.K8S_POD_NAME)
    if k8s_pod_name:
        return k8s_pod_name  # type: ignore
    return platform.node()  # hostname default


def _is_synthetic_source(properties: Optional[Any]) -> bool:
    # TODO: Use semconv symbol when released in upstream
    if not properties:
        return False
    synthetic_type = properties.get("user_agent.synthetic.type")  # type: ignore
    return synthetic_type in ("bot", "test")


def _is_synthetic_load(properties: Optional[Any]) -> bool:
    """
    Check if the request is from a synthetic load test by examining the HTTP user agent.

    :param properties: The attributes/properties to check for user agent information
    :type properties: Optional[Any]
    :return: True if the user agent contains "AlwaysOn", False otherwise
    :rtype: bool
    """
    if not properties:
        return False

    # Check both old and new semantic convention attributes for HTTP user agent
    user_agent = (
        properties.get("user_agent.original") or  # type: ignore  # New semantic convention
        properties.get("http.user_agent")  # type: ignore  # Legacy semantic convention
    )

    if user_agent and isinstance(user_agent, str):
        return "AlwaysOn" in user_agent

    return False


def _is_any_synthetic_source(properties: Optional[Any]) -> bool:
    """
    Check if the telemetry should be marked as synthetic from any source.

    :param properties: The attributes/properties to check
    :type properties: Optional[Any]
    :return: True if any synthetic source is detected, False otherwise
    :rtype: bool
    """
    return _is_synthetic_source(properties) or _is_synthetic_load(properties)


# pylint: disable=W0622
def _filter_custom_properties(properties: Attributes, filter=None) -> Dict[str, str]:
    truncated_properties: Dict[str, str] = {}
    if not properties:
        return truncated_properties
    for key, val in properties.items():
        # Apply filter function
        if filter is not None:
            if not filter(key, val):
                continue
        # Apply truncation rules
        # Max key length is 150, value is 8192
        if not key or len(key) > 150 or val is None:
            continue
        truncated_properties[key] = str(val)[:8192]
    return truncated_properties


def _get_auth_policy(credential, default_auth_policy, aad_audience=None):
    if credential:
        if hasattr(credential, "get_token"):
            return BearerTokenCredentialPolicy(
                credential,
                _get_scope(aad_audience),
            )
        raise ValueError("Must pass in valid TokenCredential.")
    return default_auth_policy


def _get_scope(aad_audience=None):
    # The AUDIENCE is a url that identifies Azure Monitor in a specific cloud
    # (For example: "https://monitor.azure.com/").
    # The SCOPE is the audience + the permission
    # (For example: "https://monitor.azure.com//.default").
    return _DEFAULT_AAD_SCOPE if not aad_audience else "{}/.default".format(aad_audience)


class Singleton(type):
    """Metaclass for creating thread-safe singleton instances.
    
    Supports multiple singleton classes by maintaining a separate instance
    for each class that uses this metaclass.
    """
    _instances = {}  # type: ignore
    _lock = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            with cls._lock:
                # Double-check pattern to avoid race conditions
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance  # type: ignore
        return cls._instances[cls]

def _get_telemetry_type(item: TelemetryItem):
    if hasattr(item, "data") and item.data is not None:
        base_type = getattr(item.data, "base_type", None)
        if base_type:
            return _TYPE_MAP.get(base_type, _UNKNOWN)
    return _UNKNOWN

def get_compute_type():
    if _is_on_functions():
        return _RP_Names.FUNCTIONS.value
    if _is_on_app_service():
        return _RP_Names.APP_SERVICE.value
    if _is_on_aks():
        return _RP_Names.AKS.value
    return _RP_Names.UNKNOWN.value

def _get_sha256_hash(input_str: str) -> str:
    return hashlib.sha256(input_str.encode("utf-8")).hexdigest()
