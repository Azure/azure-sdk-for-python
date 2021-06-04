#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
from typing import Any, Optional, List

from ._helpers import order_results, construct_iso8601
from ._generated.models import (
    Column as InternalColumn,
    QueryBody as InternalQueryBody,
    LogQueryRequest as InternalLogQueryRequest,
    ErrorDetails as InternalErrorDetails
)


class LogsQueryResultTable(object):
    """Contains the columns and rows for one table in a query response.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. The name of the table.
    :type name: str
    :param columns: Required. The list of columns in this table.
    :type columns: list[~azure.monitor.query.LogsQueryResultColumn]
    :keyword rows: Required. The resulting rows from this query.
    :paramtype rows: list[list[str]]
    """
    def __init__(self, name, columns, rows):
        # type: (str, List[LogsQueryResultColumn], List[List[str]]) -> None
        self.name = name
        self.columns = columns
        self.rows = rows

    @classmethod
    def _from_generated(cls, generated):
        return cls(
            name=generated.name,
            columns=[LogsQueryResultColumn(name=col.name, type=col.type) for col in generated.columns],
            rows=generated.rows
        )


class LogsQueryResultColumn(InternalColumn):
    """A column in a table.

    :keyword name: The name of this column.
    :paramtype name: str
    :keyword type: The data type of this column.
    :paramtype type: str
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


class LogsQueryResults(object):
    """Contains the tables, columns & rows resulting from a query.

    :keyword tables: The list of tables, columns and rows.
    :paramtype tables: list[~azure.monitor.query.LogsQueryResultTable]
    :keyword errors:
    :paramtype errors: ~azure.monitor.query.LogsErrorDetails
    """
    def __init__(self, **kwargs):
        # type: (Any) -> None
        self.tables = kwargs.get("tables", None)
        self.errors = kwargs.get("errors", None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        error = None
        tables = None
        if generated.errors is not None:
            error = LogsErrorDetails(
                code=generated.errors.code,
                message=generated.errors.message,
                target=generated.errors.target
                )
        if generated.tables is not None:
            tables = [
                LogsQueryResultTable._from_generated( # pylint: disable=protected-access
                    table
                    ) for table in generated.tables
                ]
        return cls(
            tables=tables,
            error=error
        )


class MetricsResult(object):
    """The response to a metrics query.

    All required parameters must be populated in order to send to Azure.

    :keyword cost: The integer value representing the cost of the query, for data case.
    :paramtype cost: int
    :keyword timespan: Required. The timespan for which the data was retrieved. Its value consists of
     two datetimes concatenated, separated by '/'.  This may be adjusted in the future and returned
     back from what was originally requested.
    :paramtype timespan: str
    :keyword interval: The interval (window size) for which the metric data was returned in.  This
     may be adjusted in the future and returned back from what was originally requested.  This is
     not present if a metadata request was made.
    :paramtype interval: ~datetime.timedelta
    :keyword namespace: The namespace of the metrics been queried.
    :paramtype namespace: str
    :keyword resourceregion: The region of the resource been queried for metrics.
    :paramtype resourceregion: str
    :keyword metrics: Required. the value of the collection.
    :paramtype metrics: list[~monitor_query_client.models.Metric]
    """
    def __init__(self, **kwargs):
        # type: (Any) -> None
        self.cost = kwargs.get("cost", None)
        self.timespan = kwargs["timespan"]
        self.interval = kwargs.get("interval", None)
        self.namespace = kwargs.get("namespace", None)
        self.resourceregion = kwargs.get("resourceregion", None)
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
            resourceregion=generated.resourceregion,
            metrics=[Metric._from_generated(m) for m in generated.value] # pylint: disable=protected-access
        )

class LogsQueryRequest(InternalLogQueryRequest):
    """A single request in a batch.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param query: The Analytics query. Learn more about the `Analytics query syntax
     <https://azure.microsoft.com/documentation/articles/app-insights-analytics-reference/>`_.
    :type query: str
    :param str duration: The duration for which to query the data. This can also be accompanied
     with either start_time or end_time. If start_time or end_time is not provided, the current time is
     taken as the end time. This should be provided in a ISO8601 string format like 'PT1H', 'P1Y2M10DT2H30M'.
    :keyword datetime start_time: The start time from which to query the data. This should be accompanied
     with either end_time or duration.
    :keyword datetime end_time: The end time till which to query the data. This should be accompanied
     with either start_time or duration.
    :param workspace: Workspace Id to be included in the query.
    :type workspace: str
    :keyword request_id: The error details.
    :paramtype request_id: str
    :keyword headers: Dictionary of :code:`<string>`.
    :paramtype headers: dict[str, str]
    """

    def __init__(self, query, workspace, duration=None, **kwargs):
        # type: (str, str, Optional[str], Any) -> None
        super(LogsQueryRequest, self).__init__(**kwargs)
        start = kwargs.pop('start_time', None)
        end = kwargs.pop('end_time', None)
        timespan = construct_iso8601(start, end, duration)
        self.id = kwargs.get("request_id", str(uuid.uuid4()))
        self.headers = kwargs.get("headers", None)
        self.body = {
            "query": query, "timespan": timespan
        }
        self.workspace = workspace


class LogsQueryBody(InternalQueryBody):
    """The Analytics query. Learn more about the
    `Analytics query syntax <https://azure.microsoft.com/documentation/articles/app-insights-analytics-reference/>`_.

    All required parameters must be populated in order to send to Azure.

    :param query: Required. The query to execute.
    :type query: str
    :keyword timespan: Optional. The timespan over which to query data. This is an ISO8601 time
     period value.  This timespan is applied in addition to any that are specified in the query
     expression.
    :paramtype timespan: str
    :keyword workspaces: A list of workspaces that are included in the query.
    :paramtype workspaces: list[str]
    :keyword qualified_names: A list of qualified workspace names that are included in the query.
    :paramtype qualified_names: list[str]
    :keyword workspace_ids: A list of workspace IDs that are included in the query.
    :paramtype workspace_ids: list[str]
    :keyword azure_resource_ids: A list of Azure resource IDs that are included in the query.
    :paramtype azure_resource_ids: list[str]
    """

    def __init__(self, query, timespan=None, **kwargs):
        # type: (str, Optional[str], Any) -> None
        kwargs.setdefault("query", query)
        kwargs.setdefault("timespan", timespan)
        super(LogsQueryBody, self).__init__(**kwargs)
        self.workspaces = kwargs.get("workspaces", None)
        self.qualified_names = kwargs.get("qualified_names", None)
        self.workspace_ids = kwargs.get("workspace_ids", None)
        self.azure_resource_ids = kwargs.get("azure_resource_ids", None)

class LogsQueryResult(object):
    """The LogsQueryResult.

    :param id:
    :type id: str
    :param status:
    :type status: int
    :param body: Contains the tables, columns & rows resulting from a query.
    :type body: ~azure.monitor.query.LogsQueryResults
    """
    def __init__(
        self,
        **kwargs
    ):
        self.id = kwargs.get('id', None)
        self.status = kwargs.get('status', None)
        self.body = kwargs.get('body', None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            id=generated.id,
            status=generated.status,
            body=LogsQueryResults._from_generated(generated.body) # pylint: disable=protected-access
        )

class LogsBatchResults(object):
    """Response to a batch.

    :keyword responses: An array of responses corresponding to each individual request in a batch.
    :paramtype responses: list[azure.monitor.query.LogsQueryResult]
    :keyword error: Error response for a batch request.
    :paramtype error: ~azure.monitor.query.LogsBatchResultError
    """
    def __init__(self, **kwargs):
        # type: (Any) -> None
        self.responses = kwargs.get("responses", None)
        self.error = kwargs.get("error", None)

    @classmethod
    def _from_generated(cls, generated, request_order):
        if not generated:
            return cls()
        return cls(
            responses=order_results(request_order, [
                LogsQueryResult._from_generated(rsp) for rsp in generated.responses # pylint: disable=protected-access
                ]),
            error=LogsBatchResultError._from_generated(generated.error) # pylint: disable=protected-access
        )


class LogsBatchResultError(object):
    """Error response for a batch request.

    :param message: The error message describing the cause of the error.
    :type message: str
    :param code: The error code.
    :type code: str
    :param details: The details of the error.
    :type inner_error: list[~azure.monitor.query.ErrorDetails]
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

class LogsErrorDetails(InternalErrorDetails):
    """ErrorDetails.

    :param code:
    :type code: str
    :param message:
    :type message: str
    :param target:
    :type target: str
    """

    _attribute_map = {
        'code': {'key': 'code', 'type': 'str'},
        'message': {'key': 'message', 'type': 'str'},
        'target': {'key': 'target', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(LogsErrorDetails, self).__init__(**kwargs)
        self.code = kwargs.get('code', None)
        self.message = kwargs.get('message', None)
        self.target = kwargs.get('target', None)


class MetricNamespace(object):
    """Metric namespace class specifies the metadata for a metric namespace.

    :keyword id: The ID of the metricNamespace.
    :paramtype id: str
    :keyword type: The type of the namespace.
    :paramtype type: str
    :keyword name: The name of the namespace.
    :paramtype name: str
    :keyword metric_namespace_name: The fully qualified namespace name.
    :paramtype properties: str
    """
    def __init__(
        self,
        **kwargs
    ):
        self.id = kwargs.get('id', None)
        self.type = kwargs.get('type', None)
        self.name = kwargs.get('name', None)
        self.metric_namespace_name = kwargs.get('metric_namespace_name', None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        metric_namespace_name = None
        if generated.properties:
            metric_namespace_name = generated.properties.metric_namespace_name
        return cls(
            id=generated.id,
            type=generated.type,
            name=generated.name,
            metric_namespace_name=metric_namespace_name
        )

class MetricDefinition(object):
    """Metric definition class specifies the metadata for a metric.

    :keyword is_dimension_required: Flag to indicate whether the dimension is required.
    :paramtype is_dimension_required: bool
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
        self.is_dimension_required = kwargs.get('is_dimension_required', None) # type: Optional[bool]
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
            is_dimension_required=generated.is_dimension_required,
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

    :keyword time_stamp: Required. the timestamp for the metric value in ISO 8601 format.
    :paramtype time_stamp: ~datetime.datetime
    :keyword average: the average value in the time range.
    :paramtype average: float
    :keyword minimum: the least value in the time range.
    :paramtype minimum: float
    :keyword maximum: the greatest value in the time range.
    :paramtype maximum: float
    :keyword total: the sum of all of the values in the time range.
    :paramtype total: float
    :keyword count: the number of samples in the time range. Can be used to determine the number of
     values that contributed to the average value.
    :paramtype count: float
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

    :keyword id: Required. the metric Id.
    :paramtype id: str
    :keyword type: Required. the resource type of the metric resource.
    :paramtype type: str
    :keyword name: Required. the name of the metric.
    :paramtype name: str
    :keyword unit: Required. the unit of the metric. Possible values include: "Count", "Bytes",
     "Seconds", "CountPerSecond", "BytesPerSecond", "Percent", "MilliSeconds", "ByteSeconds",
     "Unspecified", "Cores", "MilliCores", "NanoCores", "BitsPerSecond".
    :paramtype unit: str
    :keyword timeseries: Required. the time series returned when a data query is performed.
    :paramtype timeseries: list[~monitor_query_client.models.TimeSeriesElement]
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

    :keyword metadata_values: the metadata values returned if $filter was specified in the call.
    :paramtype metadata_values: list[~monitor_query_client.models.MetadataValue]
    :keyword data: An array of data points representing the metric values.  This is only returned if
     a result type of data is specified.
    :paramtype data: list[~monitor_query_client.models.MetricValue]
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

    :keyword name: the name of the metadata.
    :paramtype name: str
    :keyword value: the value of the metadata.
    :paramtype value: str
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

    :keyword time_grain: the time grain specifies the aggregation interval for the metric. Expressed
     as a duration 'PT1M', 'P1D', etc.
    :paramtype time_grain: ~datetime.timedelta
    :keyword retention: the retention period for the metric at the specified timegrain.  Expressed as
     a duration 'PT1M', 'P1D', etc.
    :paramtype retention: ~datetime.timedelta
    """
    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        self.time_grain = kwargs.get('time_grain', None)
        self.retention = kwargs.get('retention', None)

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            time_grain=generated.time_grain,
            retention=generated.retention
        )
