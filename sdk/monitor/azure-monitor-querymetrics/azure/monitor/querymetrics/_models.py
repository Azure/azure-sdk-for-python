# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# cspell:ignore milli
from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import Any, Optional, List, Dict

from ._utils.serialization import Deserializer


JSON = Mapping[str, Any]


class MetricValue:
    """Represents a metric value."""

    timestamp: datetime
    """The timestamp for the metric value."""
    average: Optional[float] = None
    """The average value in the time range."""
    minimum: Optional[float] = None
    """The least value in the time range."""
    maximum: Optional[float] = None
    """The greatest value in the time range."""
    total: Optional[float] = None
    """The sum of all of the values in the time range."""
    count: Optional[float] = None
    """The number of samples in the time range. Can be used to determine the number of values that
    contributed to the average value."""

    def __init__(self, **kwargs: Any) -> None:
        self.timestamp = kwargs["timestamp"]
        self.average = kwargs.get("average", None)
        self.minimum = kwargs.get("minimum", None)
        self.maximum = kwargs.get("maximum", None)
        self.total = kwargs.get("total", None)
        self.count = kwargs.get("count", None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            timestamp=Deserializer.deserialize_iso(generated.get("timeStamp")),
            average=generated.get("average"),
            minimum=generated.get("minimum"),
            maximum=generated.get("maximum"),
            total=generated.get("total"),
            count=generated.get("count"),
        )


class TimeSeriesElement:
    """A time series result type. The discriminator value is always TimeSeries in this case."""

    metadata_values: Dict[str, str]
    """The metadata values returned if $filter was specified in the call."""
    data: List[MetricValue]
    """An array of data points representing the metric values. This is only returned if a result
    type of data is specified."""

    def __init__(self, **kwargs: Any) -> None:
        self.metadata_values = kwargs.get("metadata_values", {})
        self.data = kwargs.get("data", [])

    @classmethod
    def _from_generated(cls, generated) -> "TimeSeriesElement":
        if not generated:
            return cls()
        return cls(
            metadata_values={obj["name"]["value"]: obj.get("value") for obj in generated.get("metadatavalues", [])},
            data=[
                MetricValue._from_generated(val)  # pylint: disable=protected-access
                for val in generated.get("data", [])
            ],
        )


class Metric:
    """The result data of a single metric name."""

    id: str
    """The metric ID."""
    type: str
    """The resource type of the metric resource."""
    name: str
    """The name of the metric."""
    unit: str
    """The unit of the metric. To access these values, use the MetricUnit enum.
    Possible values include "Count", "Bytes", "Seconds", "CountPerSecond", "BytesPerSecond", "Percent",
    "MilliSeconds", "ByteSeconds", "Unspecified", "Cores", "MilliCores", "NanoCores", "BitsPerSecond"."""
    timeseries: List[TimeSeriesElement]
    """The time series returned when a data query is performed."""
    display_description: str
    """Detailed description of this metric."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs["id"]
        self.type = kwargs["type"]
        self.name = kwargs["name"]
        self.unit = kwargs["unit"]
        self.timeseries = kwargs["timeseries"]
        self.display_description = kwargs["display_description"]

    @classmethod
    def _from_generated(cls, generated) -> "Metric":
        if not generated:
            return cls()
        return cls(
            id=generated.get("id"),
            type=generated.get("type"),
            name=generated.get("name", {}).get("value"),
            unit=generated.get("unit"),
            timeseries=[
                TimeSeriesElement._from_generated(t)  # pylint: disable=protected-access
                for t in generated.get("timeseries", [])
            ],
            display_description=generated.get("displayDescription"),
        )


class MetricsQueryResult:
    """The response to a metrics query."""

    timespan: str
    """Required. The timespan for which the data was retrieved. Its value consists of two datetimes
    concatenated, separated by '/'. This may be adjusted in the future and returned back from what
    was originally requested."""
    metrics: List[Metric]
    """Required. The value of the collection."""
    granularity: Optional[timedelta] = None
    """The granularity (window size) for which the metric data was returned in. This may be adjusted
    in the future and returned back from what was originally requested. This is not present if a
    metadata request was made."""
    namespace: Optional[str] = None
    """The namespace of the metrics that has been queried."""
    resource_region: Optional[str] = None
    """The region of the resource that has been queried for metrics."""
    cost: Optional[int] = None
    """The integer value representing the cost of the query, for data case."""

    def __init__(self, **kwargs: Any) -> None:
        self.timespan = kwargs["timespan"]
        self.metrics = kwargs["metrics"]
        self.granularity = kwargs.get("granularity", None)
        self.namespace = kwargs.get("namespace", None)
        self.resource_region = kwargs.get("resource_region", None)
        self.cost = kwargs.get("cost", None)

    @classmethod
    def _from_generated(cls, generated) -> "MetricsQueryResult":
        if not generated:
            return cls()
        granularity = None
        if generated.get("interval"):
            granularity = Deserializer.deserialize_duration(generated.get("interval"))
        if not generated.get("timespan"):
            generated["timespan"] = f"{generated.get('starttime')}/{generated.get('endtime')}"
        return cls(
            cost=generated.get("cost"),
            timespan=generated.get("timespan"),
            granularity=granularity,
            namespace=generated.get("namespace"),
            resource_region=generated.get("resourceregion"),
            metrics=MetricsList(
                metrics=[
                    Metric._from_generated(m) for m in generated.get("value", [])  # pylint: disable=protected-access
                ]
            ),
        )


class MetricsList(list):
    """Custom list for metrics."""

    def __init__(self, **kwargs: Any) -> None:
        self._metrics = kwargs["metrics"]
        self._metric_names = {val.name: ind for ind, val in enumerate(self._metrics)}

    def __iter__(self):
        return iter(self._metrics)

    def __len__(self):
        return len(self._metrics)

    def __repr__(self):
        return repr(self._metrics)

    def __getitem__(self, metric):
        try:
            return self._metrics[metric]
        except TypeError:  # TypeError: list indices must be integers or slices, not str
            return self._metrics[self._metric_names[metric]]
