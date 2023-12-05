# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import locale
from os import environ
from os.path import isdir
import platform
import threading
import time
import warnings
from typing import Callable, Dict, Any

from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util import ns_to_iso_str
from opentelemetry.util.types import Attributes

from azure.monitor.opentelemetry.exporter._generated.models import ContextTagKeys, TelemetryItem
from azure.monitor.opentelemetry.exporter._version import VERSION as ext_version
from azure.monitor.opentelemetry.exporter._constants import _INSTRUMENTATIONS_BIT_MAP


opentelemetry_version = ""

# Workaround for missing version file
try:
    from importlib.metadata import version
    opentelemetry_version = version("opentelemetry-sdk")
except ImportError:
    # Temporary workaround for <Py3.8
    # importlib-metadata causing issues in CI
    import pkg_resources # type: ignore
    opentelemetry_version = pkg_resources.get_distribution(
        "opentelemetry-sdk"
    ).version


def _is_on_app_service():
    return "WEBSITE_SITE_NAME" in environ


def _is_attach_enabled():
    return isdir("/agents/python/")


def _get_sdk_version_prefix():
    sdk_version_prefix = ''
    if _is_on_app_service() and _is_attach_enabled():
        os = 'u'
        system = platform.system()
        if system == "Linux":
            os = 'l'
        elif system == "Windows":
            os = 'w'
        sdk_version_prefix = "a{}_".format(os)
    return sdk_version_prefix


def _getlocale():
    try:
        with warnings.catch_warnings():
            # temporary work-around for https://github.com/python/cpython/issues/82986
            # by continuing to use getdefaultlocale() even though it has been deprecated.
            # we ignore the deprecation warnings to reduce noise
            warnings.simplefilter('ignore', category=DeprecationWarning)
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
    ContextTagKeys.AI_INTERNAL_SDK_VERSION: "{}py{}:otel{}:ext{}".format(
        _get_sdk_version_prefix(), platform.python_version(), opentelemetry_version, ext_version
    ),
}


def ns_to_duration(nanoseconds: int):
    value = (nanoseconds + 500000) // 1000000  # duration in milliseconds
    value, microseconds = divmod(value, 1000)
    value, seconds = divmod(value, 60)
    value, minutes = divmod(value, 60)
    days, hours = divmod(value, 24)
    return "{:d}.{:02d}:{:02d}:{:02d}.{:03d}".format(
        days, hours, minutes, seconds, microseconds
    )

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
        super().__init__(name=kwargs.pop('name', None))
        self.interval = interval
        self.function = function
        self.args = args or [] # type: ignore
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
        tags=dict(azure_monitor_context), # type: ignore
        time=ns_to_iso_str(timestamp), # type: ignore
    )

def _populate_part_a_fields(resource: Resource):
    tags = {}
    if resource and resource.attributes:
        service_name = resource.attributes.get(ResourceAttributes.SERVICE_NAME)
        service_namespace = resource.attributes.get(ResourceAttributes.SERVICE_NAMESPACE)
        service_instance_id = resource.attributes.get(ResourceAttributes.SERVICE_INSTANCE_ID)
        if service_name:
            if service_namespace:
                tags[ContextTagKeys.AI_CLOUD_ROLE] = str(service_namespace) + \
                    "." + str(service_name)
            else:
                tags[ContextTagKeys.AI_CLOUD_ROLE] = service_name # type: ignore
        if service_instance_id:
            tags[ContextTagKeys.AI_CLOUD_ROLE_INSTANCE] = service_instance_id # type: ignore
        else:
            tags[ContextTagKeys.AI_CLOUD_ROLE_INSTANCE] = platform.node()  # hostname default
        tags[ContextTagKeys.AI_INTERNAL_NODE_NAME] = tags[ContextTagKeys.AI_CLOUD_ROLE_INSTANCE]
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
