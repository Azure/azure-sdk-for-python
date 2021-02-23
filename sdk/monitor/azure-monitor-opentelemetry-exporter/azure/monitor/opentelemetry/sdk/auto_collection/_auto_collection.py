# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
#
from typing import Dict

from opentelemetry.metrics import Meter

from azure.monitor.opentelemetry.sdk.auto_collection._performance_metrics import (
    PerformanceMetrics,
)
from azure.monitor.opentelemetry.sdk.auto_collection._utils import AutoCollectionType


__all__ = [
    "AutoCollection",
    "AutoCollectionType",
    "PerformanceMetrics",
]


class AutoCollection:
    """Starts auto collection of performance counters

    Args:
        meter: OpenTelemetry Meter
        labels: Dictionary of labels
    """

    def __init__(self, meter: Meter, labels: Dict[str, str]):
        col_type = AutoCollectionType.PERF_COUNTER
        self._performance_metrics = PerformanceMetrics(meter, labels, col_type)


def standard_metrics_processor(envelope):
    """A processor for standard metric envelopes.

    Metric envelopes that match specific standard metric names are decorated
    with specific custom dimensions and indicates to the ingestion endpoint
    that these metrics have already been aggregated so aggregation does not
    occur again in the backend.
    """
    data = envelope.data.base_data
    if data.metrics:
        properties = {}
        point = data.metrics[0]
        if point.name == "http.client.duration":
            point.name = "Dependency duration"
            point.kind = "Aggregation"
            properties["_MS.MetricId"] = "dependencies/duration"
            properties["_MS.IsAutocollected"] = "True"
            if envelope.tags:
                properties["cloud/roleName"] = envelope.tags.get("ai.cloud.role", "")
                properties["cloud/roleInstance"] = envelope.tags.get("ai.cloud.roleInstance", "")
            properties["Dependency.Success"] = "False"
            if data.properties.get("http.status_code"):
                try:
                    code = int(data.properties.get("http.status_code"))
                    if 200 <= code < 400:
                        properties["Dependency.Success"] = "True"
                except ValueError:
                    pass
            # TODO: Check other properties if url doesn't exist
            properties["dependency/target"] = data.properties.get("http.url")
            properties["Dependency.Type"] = "HTTP"
            properties["dependency/resultCode"] = data.properties.get(
                "http.status_code"
            )
            # Won't need this once Azure Monitor supports histograms
            # We can't actually get the individual buckets because the bucket
            # collection must happen on the SDK side
            properties["dependency/performanceBucket"] = ""
            # TODO: OT does not have this in semantic conventions for trace
            properties["operation/synthetic"] = ""
        # TODO: Add other std. metrics as implemented
        data.properties = properties


def indicate_processed_by_metric_extractors(envelope):
    """A processor for envelopes that cause generate standard metrics.

    Certain telemetry types went sent will cause Breeze ingestion service to
    aggregate them and generate standard metrics on the server side. This
    processor is added to indicate to Breeze to not perform these aggregations
    and generations, so the sdk could do it. Used together with 
    `standard_metrics_processor`.
    """
    name = "Requests"
    if envelope.data.base_type == "RemoteDependencyData":
        name = "Dependencies"
    envelope.data.base_data.properties["_MS.ProcessedByMetricExtractors"] = (
        "(Name:'" + name + "',Ver:'1.1')"
    )
