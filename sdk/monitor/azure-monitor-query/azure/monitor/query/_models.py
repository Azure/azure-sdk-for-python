#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum
import uuid
from datetime import datetime, timedelta
import sys
from typing import Any, Optional, List, Union, Tuple, Dict, Iterator

from azure.core import CaseInsensitiveEnumMeta

from ._generated._serialization import Deserializer
from ._helpers import construct_iso8601, process_row

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # pylint: disable=ungrouped-imports


JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


class LogsTable:
    """Contains the columns and rows for one table in a query response.

    All required parameters must be populated in order to send to Azure.

    :ivar name: Required. The name of the table.
    :vartype name: str
    :ivar columns: The labels of columns in this table.
    :vartype columns: list[str]
    :ivar column_types: The types of columns in this table.
    :vartype column_types: list[object]
    :ivar rows: Required. The resulting rows from this query.
    :vartype rows: list[~azure.monitor.query.LogsTableRow]
    """

    def __init__(self, **kwargs: Any) -> None:
        self.name: str = kwargs.pop("name", "")
        self.columns: Optional[List[str]] = kwargs.pop("columns", None)
        self.columns_types: Optional[List[Any]] = kwargs.pop("column_types", None)
        _rows = kwargs.pop("rows", None)
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


class LogsTableRow:
    """Represents a single row in logs table.
    This type is gettable by both column name and column index.

    :ivar int index: The index of the row in the table
    """

    def __init__(self, **kwargs: Any) -> None:
        _col_types = kwargs["col_types"]
        row = kwargs["row"]
        self._row = process_row(_col_types, row)
        self.index: int = kwargs["row_index"]
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
            return self._row[column]


class MetricsQueryResult:
    """The response to a metrics query.

    :ivar cost: The integer value representing the cost of the query, for data case.
    :vartype cost: int
    :ivar timespan: Required. The timespan for which the data was retrieved. Its value consists of
     two datetimes concatenated, separated by '/'. This may be adjusted in the future and returned
     back from what was originally requested.
    :vartype timespan: str
    :ivar granularity: The granularity (window size) for which the metric data was returned in. This
     may be adjusted in the future and returned back from what was originally requested. This is
     not present if a metadata request was made.
    :vartype granularity: ~datetime.timedelta
    :ivar namespace: The namespace of the metrics that has been queried.
    :vartype namespace: str
    :ivar resource_region: The region of the resource that has been queried for metrics.
    :vartype resource_region: str
    :ivar metrics: Required. The value of the collection.
    :vartype metrics: list[~azure.monitor.query.Metric]
    """

    def __init__(self, **kwargs: Any) -> None:
        self.cost: Optional[int] = kwargs.get("cost", None)
        self.timespan: str = kwargs["timespan"]
        self.granularity: Optional[timedelta] = kwargs.get("granularity", None)
        self.namespace: Optional[str] = kwargs.get("namespace", None)
        self.resource_region: Optional[str] = kwargs.get("resource_region", None)
        self.metrics: Metric = kwargs["metrics"]

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
    """Custom list for metrics
    """
    def __init__(self, **kwargs: Any): # pylint: disable=super-init-not-called
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

    :param workspace_id: Workspace Id to be included in the query.
    :type workspace_id: str
    :param query: The Analytics query. Learn more about the `Analytics query syntax
     <https://azure.microsoft.com/documentation/articles/app-insights-analytics-reference/>`_.
    :type query: str
    :keyword timespan: Required. The timespan for which to query the data. This can be a timedelta,
     a timedelta and a start datetime, or a start datetime/end datetime.
    :paramtype timespan: ~datetime.timedelta or tuple[~datetime.datetime, ~datetime.timedelta]
     or tuple[~datetime.datetime, ~datetime.datetime]
    :keyword additional_workspaces: A list of workspaces that are included in the query.
     These can be qualified workspace names, workspace Ids, or Azure resource Ids.
    :paramtype additional_workspaces: list[str]
    :keyword int server_timeout: the server timeout. The default timeout is 3 minutes,
     and the maximum timeout is 10 minutes.
    :keyword bool include_statistics: To get information about query statistics.
    :keyword bool include_visualization: In the query language, it is possible to specify different
     visualization options. By default, the API does not return information regarding the type of
     visualization to show.
    """

    def __init__(
        self,
        workspace_id: str,
        query: str,
        *,
        timespan: Union[
            timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]
        ],
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
        timespan = construct_iso8601(timespan)
        additional_workspaces = kwargs.pop("additional_workspaces", None)
        self.id: str = str(uuid.uuid4())
        self.body: Dict[str, Any] = {
            "query": query,
            "timespan": timespan,
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
    """The LogsQueryResult type is returned when the response of a query is a success.

    :ivar tables: The list of tables, columns and rows.
    :vartype tables: list[~azure.monitor.query.LogsTable]
    :ivar statistics: This will include a statistics property in the response that describes various
     performance statistics such as query execution time and resource usage.
    :vartype statistics: JSON
    :ivar visualization: This will include a visualization property in the response that specifies the type of
     visualization selected by the query and any properties for that visualization.
    :vartype visualization: JSON
    :ivar status: The status of the result.
     Always 'Success' for an instance of a LogsQueryResult.
    :vartype status: ~azure.monitor.query.LogsQueryStatus
    """

    def __init__(self, **kwargs: Any):
        self.tables: List[LogsTable] = kwargs.get("tables", None)
        self.statistics: Optional[JSON] = kwargs.get("statistics", None)
        self.visualization: Optional[JSON] = kwargs.get("visualization", None)
        self.status = LogsQueryStatus.SUCCESS

    def __iter__(self) -> Iterator[LogsTable]:
        return iter(self.tables)

    @classmethod
    def _from_generated(cls, generated) -> "LogsQueryResult":
        if not generated:
            return cls()
        tables = None
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


class MetricNamespaceClassification(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Kind of namespace"""

    PLATFORM = "Platform"
    CUSTOM = "Custom"
    QOS = "Qos"


class MetricNamespace:
    """Metric namespace class specifies the metadata for a metric namespace.

    :ivar id: The ID of the metricNamespace.
    :vartype id: str
    :ivar type: The type of the namespace.
    :vartype type: str
    :ivar name: The name of the namespace.
    :vartype name: str
    :ivar fully_qualified_namespace: The fully qualified namespace name.
    :vartype fully_qualified_namespace: str
    :ivar namespace_classification: Kind of namespace. Possible values include: "Platform", "Custom", "Qos".
    :vartype namespace_classification: str or ~azure.monitor.query.MetricNamespaceClassification
    """

    def __init__(self, **kwargs: Any) -> None:
        self.id: Optional[str] = kwargs.get("id", None)
        self.type: Optional[str] = kwargs.get("type", None)
        self.name: Optional[str] = kwargs.get("name", None)
        self.fully_qualified_namespace: Optional[str] = kwargs.get("fully_qualified_namespace", None)
        self.namespace_classification: Optional[Union[str, MetricNamespaceClassification]] = \
            kwargs.get("namespace_classification", None)

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


class MetricClass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The class of the metric."""

    AVAILABILITY = "Availability"
    TRANSACTIONS = "Transactions"
    ERRORS = "Errors"
    LATENCY = "Latency"
    SATURATION = "Saturation"


class MetricDefinition:  # pylint: disable=too-many-instance-attributes
    """Metric definition class specifies the metadata for a metric.

    :ivar dimension_required: Flag to indicate whether the dimension is required.
    :vartype dimension_required: bool
    :ivar resource_id: the resource identifier of the resource that emitted the metric.
    :vartype resource_id: str
    :ivar namespace: the namespace the metric belongs to.
    :vartype namespace: str
    :ivar name: the name and the display name of the metric, i.e. it is a localizable string.
    :vartype name: str
    :ivar unit: the unit of the metric. Possible values include: "Count", "Bytes", "Seconds",
     "CountPerSecond", "BytesPerSecond", "Percent", "MilliSeconds", "ByteSeconds", "Unspecified",
     "Cores", "MilliCores", "NanoCores", "BitsPerSecond".
    :vartype unit: str or ~azure.monitor.query.MetricUnit
    :ivar primary_aggregation_type: the primary aggregation type value defining how to use the
     values for display. Possible values include: "None", "Average", "Count", "Minimum", "Maximum",
     "Total".
    :vartype primary_aggregation_type: str or ~azure.monitor.query.MetricAggregationType
    :ivar metric_class: The class of the metric. Possible values include: "Availability",
     "Transactions", "Errors", "Latency", "Saturation".
    :vartype metric_class: str or ~azure.monitor.query.MetricClass
    :ivar supported_aggregation_types: the collection of what aggregation types are supported.
    :vartype supported_aggregation_types: list[str or ~azure.monitor.query.MetricAggregationType]
    :ivar metric_availabilities: the collection of what aggregation intervals are available to be
     queried.
    :vartype metric_availabilities: list[~azure.monitor.query.MetricAvailability]
    :ivar id: the resource identifier of the metric definition.
    :vartype id: str
    :ivar dimensions: the name and the display name of the dimension, i.e. it is a localizable
     string.
    :vartype dimensions: list[str]
    """

    def __init__(self, **kwargs: Any) -> None:
        self.dimension_required: Optional[bool] = kwargs.get("dimension_required", None)
        self.resource_id: Optional[str] = kwargs.get("resource_id", None)
        self.namespace: Optional[str] = kwargs.get("namespace", None)
        self.name: Optional[str] = kwargs.get("name", None)
        self.unit: Optional[Union[str, MetricUnit]] = kwargs.get("unit", None)
        self.primary_aggregation_type: Optional[Union[str, MetricAggregationType]] = \
            kwargs.get("primary_aggregation_type", None)
        self.supported_aggregation_types: Optional[List[Union[str, MetricAggregationType]]] = \
            kwargs.get("supported_aggregation_types", None)
        self.metric_availabilities: List[MetricAvailability] = kwargs.get("metric_availabilities", None)
        self.id: Optional[str] = kwargs.get("id", None)
        self.dimensions: Optional[List[str]] = kwargs.get("dimensions", None)
        self.metric_class: Optional[Union[str, MetricClass]] = kwargs.get("metric_class", None)

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


class MetricValue:
    """Represents a metric value.

    :ivar timestamp: The timestamp for the metric value.
    :vartype timestamp: ~datetime.datetime
    :ivar average: The average value in the time range.
    :vartype average: float
    :ivar minimum: The least value in the time range.
    :vartype minimum: float
    :ivar maximum: The greatest value in the time range.
    :vartype maximum: float
    :ivar total: The sum of all of the values in the time range.
    :vartype total: float
    :ivar count: The number of samples in the time range. Can be used to determine the number of
     values that contributed to the average value.
    :vartype count: float
    """

    def __init__(self, **kwargs: Any) -> None:
        self.timestamp: datetime = kwargs["timestamp"]
        self.average: Optional[float] = kwargs.get("average", None)
        self.minimum: Optional[float] = kwargs.get("minimum", None)
        self.maximum: Optional[float] = kwargs.get("maximum", None)
        self.total: Optional[float] = kwargs.get("total", None)
        self.count: Optional[float] = kwargs.get("count", None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            timestamp=Deserializer.deserialize_iso(generated.get("time_stamp")),
            average=generated.get("average"),
            minimum=generated.get("minimum"),
            maximum=generated.get("maximum"),
            total=generated.get("total"),
            count=generated.get("count"),
        )


class Metric:
    """The result data of a single metric name.

    :ivar id: The metric Id.
    :vartype id: str
    :ivar type: The resource type of the metric resource.
    :vartype type: str
    :ivar name: The name of the metric.
    :vartype name: str
    :ivar unit: The unit of the metric. To access these values, use the MetricUnit enum.
     Possible values include: "Count", "Bytes",
     "Seconds", "CountPerSecond", "BytesPerSecond", "Percent", "MilliSeconds", "ByteSeconds",
     "Unspecified", "Cores", "MilliCores", "NanoCores", "BitsPerSecond".
    :vartype unit: str
    :ivar timeseries: The time series returned when a data query is performed.
    :vartype timeseries: list[~azure.monitor.query.TimeSeriesElement]
    :ivar display_description: Detailed description of this metric.
    :vartype display_description: str
    """

    def __init__(self, **kwargs: Any) -> None:
        self.id: str = kwargs["id"]
        self.type: str = kwargs["type"]
        self.name: str = kwargs["name"]
        self.unit: str = kwargs["unit"]
        self.timeseries: TimeSeriesElement = kwargs["timeseries"]
        self.display_description: str = kwargs["display_description"]

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


class TimeSeriesElement:
    """A time series result type. The discriminator value is always TimeSeries in this case.

    :ivar metadata_values: The metadata values returned if $filter was specified in the call.
    :vartype metadata_values: dict(str, str)
    :ivar data: An array of data points representing the metric values. This is only returned if
     a result type of data is specified.
    :vartype data: list[~azure.monitor.query.MetricValue]
    """
    def __init__(self, **kwargs: Any) -> None:
        self.metadata_values: Optional[Dict[str, str]] = kwargs.get("metadata_values", None)
        self.data: Optional[List[MetricValue]] = kwargs.get("data", None)

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


class MetricAvailability:
    """Metric availability specifies the time grain (aggregation interval or frequency)
    and the retention period for that time grain.

    :ivar granularity: the time grain specifies the aggregation interval for the metric.
    :vartype granularity: ~datetime.timedelta
    :ivar retention: the retention period for the metric at the specified timegrain.
    :vartype retention: ~datetime.timedelta
    """

    def __init__(self, **kwargs: Any) -> None:
        self.granularity: Optional[timedelta] = kwargs.get("granularity", None)
        self.retention: Optional[timedelta] = kwargs.get("retention", None)

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


class MetricAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The aggregation type of the metric."""

    NONE = "None"
    AVERAGE = "Average"
    COUNT = "Count"
    MINIMUM = "Minimum"
    MAXIMUM = "Maximum"
    TOTAL = "Total"


class MetricUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The unit of the metric."""

    COUNT = "Count"
    BYTES = "Bytes"
    SECONDS = "Seconds"
    COUNT_PER_SECOND = "CountPerSecond"
    BYTES_PER_SECOND = "BytesPerSecond"
    PERCENT = "Percent"
    MILLI_SECONDS = "MilliSeconds"
    BYTE_SECONDS = "ByteSeconds"
    UNSPECIFIED = "Unspecified"
    CORES = "Cores"
    MILLI_CORES = "MilliCores"
    NANO_CORES = "NanoCores"
    BITS_PER_SECOND = "BitsPerSecond"


class LogsQueryPartialResult:
    """The LogsQueryPartialResult type is returned when the response of a query is a
    partial success (or partial failure).

    :ivar partial_data: The list of tables, columns and rows.
    :vartype partial_data: list[~azure.monitor.query.LogsTable]
    :ivar statistics: This will include a statistics property in the response that describes various
     performance statistics such as query execution time and resource usage.
    :vartype statistics: JSON
    :ivar visualization: This will include a visualization property in the response that specifies the type of
     visualization selected by the query and any properties for that visualization.
    :vartype visualization: JSON
    :ivar partial_error: The partial error info
    :vartype partial_error: ~azure.monitor.query.LogsQueryError
    :ivar status: The status of the result. Always 'PartialError' for an instance of a LogsQueryPartialResult.
    :vartype status: ~azure.monitor.query.LogsQueryStatus
    """

    def __init__(self, **kwargs: Any) -> None:
        self.partial_data: List[LogsTable] = kwargs.get("partial_data", None)
        self.partial_error: Any = kwargs.get("partial_error", None)
        self.statistics: Optional[JSON] = kwargs.get("statistics", None)
        self.visualization: Optional[JSON] = kwargs.get("visualization", None)
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


class LogsQueryStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The status of the result object."""

    PARTIAL = "PartialError"
    SUCCESS = "Success"
    FAILURE = "Failure"
