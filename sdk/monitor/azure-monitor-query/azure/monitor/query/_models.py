#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum
import uuid
from typing import Any, Optional, List

from ._helpers import construct_iso8601, process_row
from ._generated.models import (
    Column as InternalColumn,
    BatchQueryRequest as InternalLogQueryRequest,
)


class LogsQueryResultTable(object):
    """Contains the columns and rows for one table in a query response.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. The name of the table.
    :type name: str
    :param columns: Required. The list of columns in this table.
    :type columns: list[~azure.monitor.query.LogsQueryResultColumn]
    :param rows: Required. The resulting rows from this query.
    :type rows: list[list[str]]
    """
    def __init__(self, name, columns, rows):
        # type: (str, List[LogsQueryResultColumn], List[List[str]]) -> None
        self.name = name
        self.columns = columns
        self.rows = [process_row(self.columns, row) for row in rows]

    @classmethod
    def _from_generated(cls, generated):
        return cls(
            name=generated.name,
            columns=[LogsQueryResultColumn(name=col.name, type=col.type) for col in generated.columns],
            rows=generated.rows
        )


class LogsQueryResultColumn(InternalColumn):
    """A column in a table.

    :ivar name: The name of this column.
    :vartype name: str
    :ivar type: The data type of this column.
    :vartype type: str
    """

    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "type": {"key": "type", "type": "str"},
    }

    def __init__(self, **kwargs):
        # type: (Any) -> None
        super(LogsQueryResultColumn, self).__init__(**kwargs)
        self.name = kwargs.get("name", None)
        self.type = kwargs.get("type", None)


class LogsQueryResult(object):
    """Contains the tables, columns & rows resulting from a query.

    :ivar tables: The list of tables, columns and rows.
    :vartype tables: list[~azure.monitor.query.LogsQueryResultTable]
    :ivar statistics: This will include a statistics property in the response that describes various
     performance statistics such as query execution time and resource usage.
    :vartype statistics: object
    :ivar visualization: This will include a visualization property in the response that specifies the type of
     visualization selected by the query and any properties for that visualization.
    :vartype visualization: object
    :ivar error: Any error info.
    :vartype error: object
    """
    def __init__(self, **kwargs):
        # type: (Any) -> None
        self.tables = kwargs.get("tables", None)
        self.statistics = kwargs.get("statistics", None)
        self.visualization = kwargs.get("visualization", None)
        self.error = kwargs.get("error", None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        tables = None
        if generated.tables is not None:
            tables = [
                LogsQueryResultTable._from_generated( # pylint: disable=protected-access
                    table
                    ) for table in generated.tables
                ]
        return cls(
            tables=tables,
            statistics=generated.statistics,
            visualization=generated.render,
            error=generated.error
        )


class MetricsResult(object):
    """The response to a metrics query.

    All required parameters must be populated in order to send to Azure.

    :ivar cost: The integer value representing the cost of the query, for data case.
    :vartype cost: int
    :ivar timespan: Required. The timespan for which the data was retrieved. Its value consists of
     two datetimes concatenated, separated by '/'. This may be adjusted in the future and returned
     back from what was originally requested.
    :vartype timespan: str
    :ivar interval: The interval (window size) for which the metric data was returned in. This
     may be adjusted in the future and returned back from what was originally requested. This is
     not present if a metadata request was made.
    :vartype interval: ~datetime.timedelta
    :ivar namespace: The namespace of the metrics that has been queried.
    :vartype namespace: str
    :ivar resource_region: The region of the resource that has been queried for metrics.
    :vartype resource_region: str
    :ivar metrics: Required. The value of the collection.
    :vartype metrics: list[~monitor_query_client.models.Metric]
    """
    def __init__(self, **kwargs):
        # type: (Any) -> None
        self.cost = kwargs.get("cost", None)
        self.timespan = kwargs["timespan"]
        self.interval = kwargs.get("interval", None)
        self.namespace = kwargs.get("namespace", None)
        self.resource_region = kwargs.get("resource_region", None)
        self.metrics = kwargs["metrics"]

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            cost=generated.cost,
            timespan=generated.timespan,
            interval=generated.interval,
            namespace=generated.namespace,
            resource_region=generated.resourceregion,
            metrics=[Metric._from_generated(m) for m in generated.value] # pylint: disable=protected-access
        )

class LogsBatchQuery(object):
    """A single request in a batch.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param workspace_id: Workspace Id to be included in the query.
    :type workspace_id: str
    :param query: The Analytics query. Learn more about the `Analytics query syntax
     <https://azure.microsoft.com/documentation/articles/app-insights-analytics-reference/>`_.
    :type query: str
    :param timespan: The timespan for which to query the data. This can be a timedelta,
     a timedelta and a start datetime, or a start datetime/end datetime.
    :type timespan: ~datetime.timedelta or tuple[~datetime.datetime, ~datetime.timedelta]
     or tuple[~datetime.datetime, ~datetime.datetime]
    :keyword additional_workspaces: A list of workspaces that are included in the query.
     These can be qualified workspace names, workspace Ids, or Azure resource Ids.
    :paramtype additional_workspaces: list[str]
    :keyword request_id: The error details.
    :paramtype request_id: str
    :keyword int server_timeout: the server timeout. The default timeout is 3 minutes,
     and the maximum timeout is 10 minutes.
    :keyword bool include_statistics: To get information about query statistics.
    :keyword bool include_visualization: In the query language, it is possible to specify different
     visualization options. By default, the API does not return information regarding the type of
     visualization to show.
    :keyword headers: Dictionary of :code:`<string>`.
    :paramtype headers: dict[str, str]
    """

    def __init__(self, query, workspace_id, timespan, **kwargs): #pylint: disable=super-init-not-called
        # type: (str, str, Optional[str], Any) -> None
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

        headers = kwargs.get("headers", None)
        try:
            headers['Prefer'] = prefer
        except TypeError:
            headers = {'Prefer': prefer}
        timespan = construct_iso8601(timespan)
        additional_workspaces = kwargs.pop("additional_workspaces", None)
        self.id = kwargs.get("request_id", str(uuid.uuid4()))
        self.body = {
            "query": query, "timespan": timespan, "workspaces": additional_workspaces
        }
        self.headers = headers
        self.workspace = workspace_id

    def _to_generated(self):
        return InternalLogQueryRequest(
            id=self.id,
            body=self.body,
            headers=self.headers,
            workspace=self.workspace
        )

class LogsBatchQueryResult(object):
    """The LogsBatchQueryResult.

    :ivar id: the request id of the request that was sent.
    :vartype id: str
    :ivar status: status code of the response.
    :vartype status: int
    :ivar tables: The list of tables, columns and rows.
    :vartype tables: list[~azure.monitor.query.LogsQueryResultTable]
    :ivar statistics: This will include a statistics property in the response that describes various
     performance statistics such as query execution time and resource usage.
    :vartype statistics: object
    :ivar visualization: This will include a visualization property in the response that specifies the type of
     visualization selected by the query and any properties for that visualization.
    :vartype visualization: object
    :ivar error: Any error info.
    :vartype error: object
    """
    def __init__(
        self,
        **kwargs
    ):
        self.id = kwargs.get('id', None)
        self.status = kwargs.get('status', None)
        self.tables = kwargs.get('tables', None)
        self.error = kwargs.get('error', None)
        self.statistics = kwargs.get('statistics', None)
        self.visualization = kwargs.get('visualization', None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        tables = None
        if generated.body.tables is not None:
            tables = [
                LogsQueryResultTable._from_generated( # pylint: disable=protected-access
                    table
                    ) for table in generated.body.tables
                ]
        return cls(
            id=generated.id,
            status=generated.status,
            tables=tables,
            statistics=generated.body.statistics,
            visualization=generated.body.render,
            error=generated.body.error
        )


class LogsBatchResultError(object):
    """Error response for a batch request.

    :ivar message: The error message describing the cause of the error.
    :vartype message: str
    :param code: The error code.
    :vartype code: str
    :param details: The details of the error.
    :vartype inner_error: list[~azure.monitor.query.ErrorDetails]
    """
    def __init__(self, **kwargs):
        # type: (Any) -> None
        self.message = kwargs.get("message", None)
        self.code = kwargs.get("code", None)
        self.details = kwargs.get("details", None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            message=generated.inner_error.message,
            code=generated.code,
            details=generated.inner_error.details
        )


class MetricNamespace(object):
    """Metric namespace class specifies the metadata for a metric namespace.

    :keyword id: The ID of the metricNamespace.
    :paramtype id: str
    :keyword type: The type of the namespace.
    :paramtype type: str
    :keyword name: The name of the namespace.
    :paramtype name: str
    :keyword fully_qualified_namespace: The fully qualified namespace name.
    :paramtype fully_qualified_namespace: str
    """
    def __init__(
        self,
        **kwargs
    ):
        self.id = kwargs.get('id', None)
        self.type = kwargs.get('type', None)
        self.name = kwargs.get('name', None)
        self.fully_qualified_namespace = kwargs.get('fully_qualified_namespace', None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        fully_qualified_namespace = None
        if generated.properties:
            fully_qualified_namespace = generated.properties.metric_namespace_name
        return cls(
            id=generated.id,
            type=generated.type,
            name=generated.name,
            fully_qualified_namespace=fully_qualified_namespace
        )

class MetricDefinition(object):
    """Metric definition class specifies the metadata for a metric.

    :keyword dimension_required: Flag to indicate whether the dimension is required.
    :paramtype dimension_required: bool
    :keyword resource_id: the resource identifier of the resource that emitted the metric.
    :paramtype resource_id: str
    :keyword namespace: the namespace the metric belongs to.
    :paramtype namespace: str
    :keyword name: the name and the display name of the metric, i.e. it is a localizable string.
    :paramtype name: str
    :keyword unit: the unit of the metric. Possible values include: "Count", "Bytes", "Seconds",
     "CountPerSecond", "BytesPerSecond", "Percent", "MilliSeconds", "ByteSeconds", "Unspecified",
     "Cores", "MilliCores", "NanoCores", "BitsPerSecond".
    :paramtype unit: str or ~monitor_query_client.models.Unit
    :keyword primary_aggregation_type: the primary aggregation type value defining how to use the
     values for display. Possible values include: "None", "Average", "Count", "Minimum", "Maximum",
     "Total".
    :paramtype primary_aggregation_type: str or ~monitor_query_client.models.AggregationType
    :keyword supported_aggregation_types: the collection of what aggregation types are supported.
    :paramtype supported_aggregation_types: list[str or ~monitor_query_client.models.AggregationType]
    :keyword metric_availabilities: the collection of what aggregation intervals are available to be
     queried.
    :paramtype metric_availabilities: list[~monitor_query_client.models.MetricAvailability]
    :keyword id: the resource identifier of the metric definition.
    :paramtype id: str
    :keyword dimensions: the name and the display name of the dimension, i.e. it is a localizable
     string.
    :paramtype dimensions: list[str]
    """
    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        self.dimension_required = kwargs.get('dimension_required', None) # type: Optional[bool]
        self.resource_id = kwargs.get('resource_id', None) # type: Optional[str]
        self.namespace = kwargs.get('namespace', None) # type: Optional[str]
        self.name = kwargs.get('name', None) # type: Optional[str]
        self.unit = kwargs.get('unit', None) # type: Optional[str]
        self.primary_aggregation_type = kwargs.get('primary_aggregation_type', None) # type: Optional[str]
        self.supported_aggregation_types = kwargs.get('supported_aggregation_types', None) # type: Optional[str]
        self.metric_availabilities = kwargs.get('metric_availabilities', None) # type: List[MetricAvailability]
        self.id = kwargs.get('id', None) # type: Optional[str]
        self.dimensions = kwargs.get('dimensions', None) # type: Optional[List[str]]

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        dimensions = None
        if generated.dimensions is not None:
            dimensions = [d.value for d in generated.dimensions]
        return cls(
            dimension_required=generated.is_dimension_required,
            resource_id=generated.resource_id,
            namespace=generated.namespace,
            name=generated.name.value,
            unit=generated.unit,
            primary_aggregation_type=generated.primary_aggregation_type,
            supported_aggregation_types=generated.supported_aggregation_types,
            metric_availabilities=[
                MetricAvailability._from_generated( # pylint: disable=protected-access
                    val
                    ) for val in generated.metric_availabilities
                ],
            id=generated.id,
            dimensions=dimensions
        )

class MetricValue(object):
    """Represents a metric value.

    All required parameters must be populated in order to send to Azure.

    :ivar time_stamp: Required. The timestamp for the metric value in ISO 8601 format.
    :vartype time_stamp: ~datetime.datetime
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
    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        self.time_stamp = kwargs['time_stamp']
        self.average = kwargs.get('average', None)
        self.minimum = kwargs.get('minimum', None)
        self.maximum = kwargs.get('maximum', None)
        self.total = kwargs.get('total', None)
        self.count = kwargs.get('count', None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            time_stamp=generated.time_stamp,
            average=generated.average,
            minimum=generated.minimum,
            maximum=generated.maximum,
            total=generated.total,
            count=generated.count
        )

class Metric(object):
    """The result data of a query.

    All required parameters must be populated in order to send to Azure.

    :ivar id: Required. The metric Id.
    :vartype id: str
    :ivar type: Required. The resource type of the metric resource.
    :vartype type: str
    :ivar name: Required. The name of the metric.
    :vartype name: str
    :ivar unit: Required. The unit of the metric. Possible values include: "Count", "Bytes",
     "Seconds", "CountPerSecond", "BytesPerSecond", "Percent", "MilliSeconds", "ByteSeconds",
     "Unspecified", "Cores", "MilliCores", "NanoCores", "BitsPerSecond".
    :vartype unit: str
    :ivar timeseries: Required. The time series returned when a data query is performed.
    :vartype timeseries: list[~monitor_query_client.models.TimeSeriesElement]
    """
    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        self.id = kwargs['id']
        self.type = kwargs['type']
        self.name = kwargs['name']
        self.unit = kwargs['unit']
        self.timeseries = kwargs['timeseries']

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            id=generated.id,
            type=generated.type,
            name=generated.name.value,
            unit=generated.unit,
            timeseries=[
                TimeSeriesElement._from_generated(t) for t in generated.timeseries # pylint: disable=protected-access
                ]
        )


class TimeSeriesElement(object):
    """A time series result type. The discriminator value is always TimeSeries in this case.

    :ivar metadata_values: The metadata values returned if $filter was specified in the call.
    :vartype metadata_values: list[~monitor_query_client.models.MetadataValue]
    :ivar data: An array of data points representing the metric values. This is only returned if
     a result type of data is specified.
    :vartype data: list[~monitor_query_client.models.MetricValue]
    """

    _attribute_map = {
        'metadata_values': {'key': 'metadata_values', 'type': '[MetadataValue]'},
        'data': {'key': 'data', 'type': '[MetricValue]'},
    }

    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        self.metadata_values = kwargs.get('metadatavalues', None)
        self.data = kwargs.get('data', None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            metadata_values=[
                MetricsMetadataValue._from_generated( # pylint: disable=protected-access
                    mval
                    ) for mval in generated.metadatavalues
                ],
            data=[MetricValue._from_generated(val) for val in generated.data] # pylint: disable=protected-access
        )

class MetricsMetadataValue(object):
    """Represents a metric metadata value.

    :ivar name: The name of the metadata.
    :vartype name: str
    :ivar value: The value of the metadata.
    :vartype value: str
    """
    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        self.name = kwargs.get('name', None)
        self.value = kwargs.get('value', None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            name=generated.name.value,
            value=generated.value
        )


class MetricAvailability(object):
    """Metric availability specifies the time grain (aggregation interval or frequency)
    and the retention period for that time grain.

    :keyword granularity: the time grain specifies the aggregation interval for the metric. Expressed
     as a duration 'PT1M', 'P1D', etc.
    :paramtype granularity: ~datetime.timedelta
    :keyword retention: the retention period for the metric at the specified timegrain. Expressed as
     a duration 'PT1M', 'P1D', etc.
    :paramtype retention: ~datetime.timedelta
    """
    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        self.granularity = kwargs.get('granularity', None)
        self.retention = kwargs.get('retention', None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            granularity=generated.time_grain,
            retention=generated.retention
        )


class AggregationType(str, Enum):
    """The aggregation type of the metric.
    """

    NONE = "None"
    AVERAGE = "Average"
    COUNT = "Count"
    MINIMUM = "Minimum"
    MAXIMUM = "Maximum"
    TOTAL = "Total"
