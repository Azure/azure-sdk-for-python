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
from typing import Callable, Dict, Any

from opentelemetry.semconv.attributes.service_attributes import SERVICE_NAME
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util import ns_to_iso_str
from opentelemetry.util.types import Attributes

from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.monitor.opentelemetry.exporter._generated.models import ContextTagKeys, TelemetryItem
from azure.monitor.opentelemetry.exporter._version import VERSION as ext_version
from azure.monitor.opentelemetry.exporter._constants import (
    _AKS_ARM_NAMESPACE_ID,
    _APPLICATION_INSIGHTS_RESOURCE_SCOPE,
    _PYTHON_ENABLE_OPENTELEMETRY,
    _INSTRUMENTATIONS_BIT_MAP,
    _FUNCTIONS_WORKER_RUNTIME,
    _WEBSITE_SITE_NAME,
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
    return _AKS_ARM_NAMESPACE_ID in environ


# Attach


def _is_attach_enabled():
    if _is_on_app_service():
        return isdir("/agents/python/")
    if _is_on_functions():
        return environ.get(_PYTHON_ENABLE_OPENTELEMETRY) == "true"
    return False


def _get_sdk_version_prefix():
    sdk_version_prefix = ""
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

    os = "u"
    system = platform.system()
    if system == "Linux":
        os = "l"
    elif system == "Windows":
        os = "w"

    attach_type = "m"
    if _is_attach_enabled():
        attach_type = "i"
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
            return locale.getdefaultlocale()[0]
    except AttributeError:
        # locale.getlocal() has issues on Windows: https://github.com/python/cpython/issues/82986
        # Use this as a fallback if locale.getdefaultlocale() doesn't exist (>Py3.13)
        return locale.getlocale()[0]


azure_monitor_context = {
    ContextTagKeys.AI_DEVICE_ID: platform.node(),
    ContextTagKeys.AI_DEVICE_LOCALE: _getlocale(),
    ContextTagKeys.AI_DEVICE_OS_VERSION: platform.version(),
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
        service_name = resource.attributes.get(SERVICE_NAME)
        service_namespace = resource.attributes.get(ResourceAttributes.SERVICE_NAMESPACE)
        service_instance_id = resource.attributes.get(ResourceAttributes.SERVICE_INSTANCE_ID)
        device_id = resource.attributes.get(ResourceAttributes.DEVICE_ID)
        device_model = resource.attributes.get(ResourceAttributes.DEVICE_MODEL_NAME)
        device_make = resource.attributes.get(ResourceAttributes.DEVICE_MANUFACTURER)
        app_version = resource.attributes.get(ResourceAttributes.SERVICE_VERSION)
        if service_name:
            if service_namespace:
                tags[ContextTagKeys.AI_CLOUD_ROLE] = str(service_namespace) + "." + str(service_name)
            else:
                tags[ContextTagKeys.AI_CLOUD_ROLE] = service_name  # type: ignore
        if service_instance_id:
            tags[ContextTagKeys.AI_CLOUD_ROLE_INSTANCE] = service_instance_id  # type: ignore
        else:
            tags[ContextTagKeys.AI_CLOUD_ROLE_INSTANCE] = platform.node()  # hostname default
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


def _get_auth_policy(credential, default_auth_policy):
    if credential:
        if hasattr(credential, "get_token"):
            return BearerTokenCredentialPolicy(
                credential,
                _APPLICATION_INSIGHTS_RESOURCE_SCOPE,
            )
        raise ValueError("Must pass in valid TokenCredential.")
    return default_auth_policy


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance
