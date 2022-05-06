# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import locale
import platform
import threading
import time

import pkg_resources

from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.util import ns_to_iso_str

from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem
from azure.monitor.opentelemetry.exporter._version import VERSION as ext_version


# Workaround for missing version file
opentelemetry_version = pkg_resources.get_distribution(
    "opentelemetry-sdk"
).version

azure_monitor_context = {
    "ai.device.id": platform.node(),
    "ai.device.locale": locale.getdefaultlocale()[0],
    "ai.device.osVersion": platform.version(),
    "ai.device.type": "Other",
    "ai.internal.sdkVersion": "py{}:otel{}:ext{}".format(
        platform.python_version(), opentelemetry_version, ext_version
    ),
}


def ns_to_duration(nanoseconds):
    value = (nanoseconds + 500000) // 1000000  # duration in milliseconds
    value, microseconds = divmod(value, 1000)
    value, seconds = divmod(value, 60)
    value, minutes = divmod(value, 60)
    days, hours = divmod(value, 24)
    return "{:d}.{:02d}:{:02d}:{:02d}.{:03d}".format(
        days, hours, minutes, seconds, microseconds
    )


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

    def __init__(self, interval, function, *args, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.interval = interval
        self.function = function
        self.args = args or []
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

def _create_telemetry_item(timestamp):
    return TelemetryItem(
        name="",
        instrumentation_key="",
        tags=dict(azure_monitor_context),
        time=ns_to_iso_str(timestamp),
    )

def _populate_part_a_fields(resource):
    tags = {}
    if resource and resource.attributes:
        service_name = resource.attributes.get(ResourceAttributes.SERVICE_NAME)
        service_namespace = resource.attributes.get(ResourceAttributes.SERVICE_NAMESPACE)
        service_instance_id = resource.attributes.get(ResourceAttributes.SERVICE_INSTANCE_ID)
        if service_name:
            if service_namespace:
                tags["ai.cloud.role"] = service_namespace + \
                    "." + service_name
            else:
                tags["ai.cloud.role"] = service_name
        if service_instance_id:
            tags["ai.cloud.roleInstance"] = service_instance_id
        else:
            tags["ai.cloud.roleInstance"] = platform.node()  # hostname default
        tags["ai.internal.nodeName"] = tags["ai.cloud.roleInstance"]
    return tags
