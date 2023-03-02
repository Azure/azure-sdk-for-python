#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
from datetime import datetime, timedelta
import sys
from typing import Any, Optional, List, Union, Tuple, Dict, Iterator

from ._enums import LogsQueryStatus, MetricAggregationType, MetricClass, MetricNamespaceClassification, MetricUnit
from ._exceptions import LogsQueryError
from ._generated._serialization import Deserializer
from ._helpers import construct_iso8601, process_row

if sys.version_info >= (3, 9):
    from collections.abc import Mapping
else:
    from typing import Mapping  # pylint: disable=ungrouped-imports


JSON = Mapping[str, Any]  # pylint: disable=unsubscriptable-object


class LogsTableRow:
    """Represents a single row in logs table.

    This type is gettable by both column name and column index.
    """

    index: int
    """The index of the row in the table"""

    def __init__(self, **kwargs: Any) -> None:
        _col_types = kwargs["col_types"]
        row = kwargs["row"]
        self._row = process_row(_col_types, row)
        self.index = kwargs["row_index"]
        _columns = kwargs["columns"]
        self._row_dict = {_columns[i]: self._row[i] for i in range(len(self._row))}

    def __iter__(self) -> Iterator[Any]:
        """This will iterate over the row directly."""
        return iter(self._row)

    def __len__(self) -> int:
        return len(self._row)

    def __repr__(self) -> str:
        return repr(self._row)

    def __getitem__(self, column: Union[str, int]) -> Any:
        """This type must be subscriptable directly to row.
        Must be gettable by both column name and row index

        :param column: The name of the column or the index of the element in a row.
        :type column: str or int
        """
        try:
            return self._row_dict[column]
        except KeyError:
            return self._row[int(column)]


class LogsTable:
    """Contains the columns and rows for one table in a query response.

    All required parameters must be populated in order to send to Azure.
    """

    name: str
    """Required. The name of the table."""
    rows: List[LogsTableRow]
    """Required. The resulting rows from this query."""
    columns: List[str]
    """Required. The labels of columns in this table."""
    columns_types: List[str]
    """Required. The types of columns in this table."""

    def __init__(self, **kwargs: Any) -> None:
        self.name = kwargs.pop("name", "")
        self.columns = kwargs.pop("columns", [])
        self.columns_types = kwargs.pop("column_types", [])
        _rows = kwargs.pop("rows", [])
        self.rows: List[LogsTableRow] = [
            LogsTableRow(
                row=row,
                row_index=ind,
                col_types=self.columns_types,
                columns=self.columns,
            )
            for ind, row in enumerate(_rows)
        ]

    @classmethod
    def _from_generated(cls, generated) -> "LogsTable":
        return cls(
            name=generated.get("name"),
            columns=[col["name"] for col in generated.get("columns", [])],
            column_types=[col["type"] for col in generated.get("columns", [])],
            rows=generated.get("rows"),
        )


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
            metadata_values={
                obj["name"]["value"]: obj.get("value") for obj in generated.get("metadatavalues", [])
            },
            data=[
                MetricValue._from_generated(val) for val in generated.get("data", []) # pylint: disable=protected-access
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
                TimeSeriesElement._from_generated(t) # pylint: disable=protected-access
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
        self.metrics= kwargs["metrics"]
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
        return cls(
            cost=generated.get("cost"),
            timespan=generated.get("timespan"),
            granularity=granularity,
            namespace=generated.get("namespace"),
            resource_region=generated.get("resourceregion"),
            metrics=MetricsList(metrics=[
                Metric._from_generated(m) for m in generated.get("value", []) # pylint: disable=protected-access
            ]),
        )


class MetricsList(list):
    """Custom list for metrics."""

    def __init__(self, **kwargs: Any) -> None: # pylint: disable=super-init-not-called
        self._metrics = kwargs['metrics']
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
        except TypeError: # TypeError: list indices must be integers or slices, not str
            return self._metrics[self._metric_names[metric]]


class LogsBatchQuery:
    """A single request in a batch. The batch query API accepts a list of these objects.

    :param workspace_id: Workspace ID to be included in the query.
    :type workspace_id: str
    :param query: The Analytics query. Learn more about the `Analytics query syntax
     <https://azure.microsoft.com/documentation/articles/app-insights-analytics-reference/>`_.
    :type query: str
    :keyword timespan: Required. The timespan for which to query the data. This can be a timedelta,
     a timedelta and a start datetime, or a start datetime/end datetime. Set to None to not constrain
     the query to a timespan.
    :paramtype timespan: ~datetime.timedelta or tuple[~datetime.datetime, ~datetime.timedelta]
     or tuple[~datetime.datetime, ~datetime.datetime] or None
    :keyword additional_workspaces: A list of workspaces that are included in the query.
     These can be qualified workspace names, workspace IDs, or Azure resource IDs.
    :paramtype additional_workspaces: Optional[list[str]]
    :keyword server_timeout: the server timeout. The default timeout is 3 minutes,
     and the maximum timeout is 10 minutes.
    :paramtype server_timeout: Optional[int]
    :keyword include_statistics: To get information about query statistics.
    :paramtype include_statistics: Optional[bool]
    :keyword include_visualization: In the query language, it is possible to specify different
     visualization options. By default, the API does not return information regarding the type of
     visualization to show.
    :paramtype include_visualization: Optional[bool]
    """

    def __init__(
        self,
        workspace_id: str,
        query: str,
        *,
        timespan: Optional[Union[
            timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]
        ]],
        **kwargs: Any
    ) -> None:  # pylint: disable=super-init-not-called
        include_statistics = kwargs.pop("include_statistics", False)
        include_visualization = kwargs.pop("include_visualization", False)
        server_timeout = kwargs.pop("server_timeout", None)
        prefer = ""
        if server_timeout:
            prefer += "wait=" + str(server_timeout)
        if include_statistics:
            if len(prefer) > 0:
                prefer += ","
            prefer += "include-statistics=true"
        if include_visualization:
            if len(prefer) > 0:
                prefer += ","
            prefer += "include-render=true"

        headers = {"Prefer": prefer}
        timespan_iso = construct_iso8601(timespan)
        additional_workspaces = kwargs.pop("additional_workspaces", None)
        self.id = str(uuid.uuid4())
        self.body = {
            "query": query,
            "timespan": timespan_iso,
            "workspaces": additional_workspaces,
        }
        self.headers = headers
        self.workspace = workspace_id

    def _to_generated(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "body": self.body,
            "headers": self.headers,
            "workspace": self.workspace,
            "path": "/query",
            "method": "POST"
        }


class LogsQueryResult:
    """The LogsQueryResult type is returned when the response of a query is a success."""

    tables: List[LogsTable]
    """The list of tables, columns and rows."""
    statistics: Optional[JSON] = None
    """This will include a statistics property in the response that describes various performance
    statistics such as query execution time and resource usage."""
    visualization: Optional[JSON] = None
    """This will include a visualization property in the response that specifies the type of visualization selected
    by the query and any properties for that visualization."""
    status: LogsQueryStatus
    """The status of the result. Always 'Success' for an instance of a LogsQueryResult."""

    def __init__(self, **kwargs: Any) -> None:
        self.tables = kwargs.get("tables", [])
        self.statistics = kwargs.get("statistics", None)
        self.visualization = kwargs.get("visualization", None)
        self.status = LogsQueryStatus.SUCCESS

    def __iter__(self) -> Iterator[LogsTable]:
        return iter(self.tables)

    @classmethod
    def _from_generated(cls, generated) -> "LogsQueryResult":
        if not generated:
            return cls()
        tables = []
        if "body" in generated:
            generated = generated["body"]
        if generated.get("tables"):
            tables = [
                LogsTable._from_generated(table)  # pylint: disable=protected-access
                for table in generated["tables"]
            ]
        return cls(
            tables=tables,
            statistics=generated.get("statistics"),
            visualization=generated.get("render"),
        )


class MetricNamespace:
    """Metric namespace class specifies the metadata for a metric namespace."""

    id: Optional[str] = None
    """The ID of the metricNamespace."""
    type: Optional[str] = None
    """The type of the namespace."""
    name: Optional[str] = None
    """The name of the namespace."""
    fully_qualified_namespace: Optional[str] = None
    """The fully qualified namespace name."""
    namespace_classification: Optional[Union[str, MetricNamespaceClassification]] = None
    """Kind of namespace. Possible values include "Platform", "Custom", "Qos"."""


    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", None)
        self.type = kwargs.get("type", None)
        self.name = kwargs.get("name", None)
        self.fully_qualified_namespace = kwargs.get("fully_qualified_namespace", None)
        self.namespace_classification = kwargs.get("namespace_classification", None)

    @classmethod
    def _from_generated(cls, generated) -> "MetricNamespace":
        if not generated:
            return cls()
        fully_qualified_namespace = None
        if generated.get("properties"):
            fully_qualified_namespace = generated["properties"].get("metricNamespaceName")
        return cls(
            id=generated.get("id"),
            type=generated.get("type"),
            name=generated.get("name"),
            fully_qualified_namespace=fully_qualified_namespace,
            namespace_classification=generated.get("classification"),
        )


class MetricAvailability:
    """Metric availability specifies the time grain (aggregation interval or frequency)
    and the retention period for that time grain.
    """

    granularity: Optional[timedelta] = None
    """The time grain specifies the aggregation interval for the metric."""
    retention: Optional[timedelta] = None
    """The retention period for the metric at the specified timegrain."""

    def __init__(self, **kwargs: Any) -> None:
        self.granularity = kwargs.get("granularity", None)
        self.retention = kwargs.get("retention", None)

    @classmethod
    def _from_generated(cls, generated) -> "MetricAvailability":
        if not generated:
            return cls()
        granularity, retention = None, None
        if generated.get("timeGrain"):
            granularity = Deserializer.deserialize_duration(generated["timeGrain"])
        if generated.get("retention"):
            retention = Deserializer.deserialize_duration(generated["retention"])
        return cls(
            granularity=granularity,
            retention=retention
        )


class MetricDefinition:  # pylint: disable=too-many-instance-attributes
    """Metric definition class specifies the metadata for a metric."""

    dimension_required: Optional[bool] = None
    """Flag to indicate whether the dimension is required."""
    resource_id: Optional[str] = None
    """The resource identifier of the resource that emitted the metric."""
    namespace: Optional[str] = None
    """The namespace the metric belongs to."""
    name: Optional[str] = None
    """The name and the display name of the metric, i.e. it is a localizable string."""
    unit: Optional[Union[str, MetricUnit]] = None
    """The unit of the metric. Possible values include "Count", "Bytes", "Seconds", "CountPerSecond",
    "BytesPerSecond", "Percent", "MilliSeconds", "ByteSeconds", "Unspecified", "Cores", "MilliCores",
    "NanoCores", "BitsPerSecond"."""
    primary_aggregation_type: Optional[Union[str, MetricAggregationType]] = None
    """The primary aggregation type value defining how to use the values for display. Possible values
    include "None", "Average", "Count", "Minimum", "Maximum", "Total"."""
    metric_class: Optional[Union[str, MetricClass]] = None
    """The class of the metric. Possible values include "Availability", "Transactions", "Errors",
    "Latency", "Saturation"."""
    supported_aggregation_types: Optional[List[Union[str, MetricAggregationType]]] = None
    """The collection of what aggregation types are supported."""
    metric_availabilities: Optional[List[MetricAvailability]] = None
    """The collection of what aggregation intervals are available to be queried."""
    id: Optional[str] = None
    """The resource identifier of the metric definition."""
    dimensions: Optional[List[str]] = None
    """The name and the display name of the dimension, i.e. it is a localizable string."""


    def __init__(self, **kwargs: Any) -> None:
        self.dimension_required = kwargs.get("dimension_required", None)
        self.resource_id = kwargs.get("resource_id", None)
        self.namespace = kwargs.get("namespace", None)
        self.name = kwargs.get("name", None)
        self.unit = kwargs.get("unit", None)
        self.primary_aggregation_type = kwargs.get("primary_aggregation_type", None)
        self.supported_aggregation_types =kwargs.get("supported_aggregation_types", None)
        self.metric_availabilities = kwargs.get("metric_availabilities", None)
        self.id = kwargs.get("id", None)
        self.dimensions = kwargs.get("dimensions", None)
        self.metric_class = kwargs.get("metric_class", None)

    @classmethod
    def _from_generated(cls, generated) -> "MetricDefinition":
        if not generated:
            return cls()
        dimensions, metric_class = None, None
        if generated.get("dimensions"):
            dimensions = [d["value"] for d in generated["dimensions"]]
        if generated.get("metricClass"):
            metric_class = MetricClass(generated["metricClass"])
        return cls(
            dimension_required=generated.get("isDimensionRequired"),
            resource_id=generated.get("resourceId"),
            namespace=generated.get("namespace"),
            name=generated.get("name", {}).get("value"),
            unit=generated.get("unit"),
            primary_aggregation_type=generated.get("primaryAggregationType"),
            supported_aggregation_types=generated.get("supportedAggregationTypes"),
            metric_class=metric_class,
            metric_availabilities=[
                MetricAvailability._from_generated(  # pylint: disable=protected-access
                    val
                )
                for val in generated.get("metricAvailabilities", [])
            ],
            id=generated.get("id"),
            dimensions=dimensions,
        )


class LogsQueryPartialResult:
    """The LogsQueryPartialResult type is returned when the response of a query is a
    partial success (or partial failure).
    """

    partial_data: List[LogsTable]
    """The list of tables, columns and rows."""
    statistics: Optional[JSON] = None
    """This will include a statistics property in the response that describes various performance statistics
    such as query execution time and resource usage."""
    visualization: Optional[JSON] = None
    """This will include a visualization property in the response that specifies the type of visualization
    selected by the query and any properties for that visualization."""
    partial_error: Optional[LogsQueryError] = None
    """The partial error info."""
    status: LogsQueryStatus
    """The status of the result. Always 'PartialError' for an instance of a LogsQueryPartialResult."""


    def __init__(self, **kwargs: Any) -> None:
        self.partial_data = kwargs.get("partial_data", [])
        self.partial_error = kwargs.get("partial_error", None)
        self.statistics = kwargs.get("statistics", None)
        self.visualization = kwargs.get("visualization", None)
        self.status = LogsQueryStatus.PARTIAL

    def __iter__(self) -> Iterator[LogsTable]:
        return iter(self.partial_data)

    @classmethod
    def _from_generated(cls, generated, error) -> "LogsQueryPartialResult":
        if not generated:
            return cls()
        partial_data = None
        if "body" in generated:
            generated = generated["body"]
        if generated.get("tables"):
            partial_data = [
                LogsTable._from_generated(table)  # pylint: disable=protected-access
                for table in generated["tables"]
            ]
        return cls(
            partial_data=partial_data,
            partial_error=error._from_generated(generated.get("error")), # pylint: disable=protected-access
            statistics=generated.get("statistics"),
            visualization=generated.get("render"),
        )
