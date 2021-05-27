#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
from typing import Any

from ._generated.models import (
    QueryResults as InternalQueryResults,
    Table as InternalTable,
    Column as InternalColumn,
    Response as InternalResponse,
    QueryBody as InternalQueryBody,
    BatchResponse as InternalBatchResponse,
    BatchResponseError as InternalBatchResponseError,
    LogQueryRequest as InternalLogQueryRequest,
    MetricNamespace as InternalMetricNamespace,
    MetricDefinition as InternalMetricDefinition,

)


class LogsQueryResultTable(InternalTable):
    """Contains the columns and rows for one table in a query response.

    All required parameters must be populated in order to send to Azure.

    :keyword name: Required. The name of the table.
    :paramtype name: str
    :keyword columns: Required. The list of columns in this table.
    :paramtype columns: list[~azure.monitor.query.LogsQueryResultColumn]
    :keyword rows: Required. The resulting rows from this query.
    :paramtype rows: list[list[str]]
    """

    _validation = {
        "name": {"required": True},
        "columns": {"required": True},
        "rows": {"required": True},
    }

    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "columns": {"key": "columns", "type": "[Column]"},
        "rows": {"key": "rows", "type": "[[str]]"},
    }

    def __init__(self, **kwargs):
        # type: (Any) -> None
        super(LogsQueryResultTable, self).__init__(**kwargs)
        self.name = kwargs["name"]
        self.columns = kwargs["columns"]
        self.rows = kwargs["rows"]


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


class LogsQueryResults(InternalQueryResults):
    """Contains the tables, columns & rows resulting from a query.

    :keyword tables: The list of tables, columns and rows.
    :paramtype tables: list[~monitor_query_client.models.Table]
    :keyword errors:
    :paramtype errors: ~monitor_query_client.models.ErrorDetails
    """

    _attribute_map = {
        "tables": {"key": "tables", "type": "[Table]"},
        "errors": {"key": "errors", "type": "ErrorDetails"},
    }

    def __init__(self, **kwargs):
        # type: (Any) -> None
        super(LogsQueryResults, self).__init__(**kwargs)
        self.tables = kwargs.get("tables", None)
        self.errors = kwargs.get("errors", None)


class MetricsResult(InternalResponse):
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
    :keyword value: Required. the value of the collection.
    :paramtype value: list[~monitor_query_client.models.Metric]
    """

    _validation = {
        "cost": {"minimum": 0},
        "timespan": {"required": True},
        "value": {"required": True},
    }

    _attribute_map = {
        "cost": {"key": "cost", "type": "int"},
        "timespan": {"key": "timespan", "type": "str"},
        "interval": {"key": "interval", "type": "duration"},
        "namespace": {"key": "namespace", "type": "str"},
        "resourceregion": {"key": "resourceregion", "type": "str"},
        "value": {"key": "value", "type": "[Metric]"},
    }

    def __init__(self, **kwargs):
        # type: (Any) -> None
        super(MetricsResult, self).__init__(**kwargs)
        self.cost = kwargs.get("cost", None)
        self.timespan = kwargs["timespan"]
        self.interval = kwargs.get("interval", None)
        self.namespace = kwargs.get("namespace", None)
        self.resourceregion = kwargs.get("resourceregion", None)
        self.value = kwargs["value"]


class LogsQueryRequest(InternalLogQueryRequest):
    """An single request in a batch.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword request_id: The error details.
    :paramtype request_id: str
    :keyword headers: Dictionary of :code:`<string>`.
    :paramtype headers: dict[str, str]
    :keyword body: The Analytics query. Learn more about the `Analytics query syntax
     <https://azure.microsoft.com/documentation/articles/app-insights-analytics-reference/>`_.
    :paramtype body: ~monitor_query_client.models.QueryBody
    :keyword workspace: Workspace Id to be included in the query.
    :paramtype workspace: str
    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        super(LogsQueryRequest, self).__init__(**kwargs)
        self.id = kwargs.get("id", uuid.uuid4())
        self.headers = kwargs.get("headers", {"Content-Type": "application/json"})
        self.body = kwargs.get("body", None)
        self.workspace = kwargs.get("workspace", None)


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

    def __init__(self, query, **kwargs):
        # type: (str, Any) -> None
        super(LogsQueryBody, self).__init__(**kwargs)
        kwargs.setdefault("query", query)
        self.timespan = kwargs.get("timespan", None)
        self.workspaces = kwargs.get("workspaces", None)
        self.qualified_names = kwargs.get("qualified_names", None)
        self.workspace_ids = kwargs.get("workspace_ids", None)
        self.azure_resource_ids = kwargs.get("azure_resource_ids", None)


class LogsBatchResponse(InternalBatchResponse):
    """Response to a batch.

    :keyword responses: An array of responses corresponding to each individual request in a batch.
    :paramtype responses: list[~monitor_query_client.models.LogQueryResponse]
    :keyword error: Error response for a batch request.
    :paramtype error: ~azure.monitor.query.LogsBatchResponseError
    """

    _attribute_map = {
        "responses": {"key": "responses", "type": "[LogQueryResponse]"},
        "error": {"key": "error", "type": "LogsBatchResponseError"},
    }

    def __init__(self, **kwargs):
        # type: (Any) -> None
        super(LogsBatchResponse, self).__init__(**kwargs)
        self.responses = kwargs.get("responses", None)
        self.error = kwargs.get("error", None)


class LogsBatchResponseError(InternalBatchResponseError):
    """Error response for a batch request.

    :param message: The error message describing the cause of the error.
    :type message: str
    :param code: The error code.
    :type code: str
    :param inner_error:
    :type inner_error: ~monitor_query_client.models.BatchResponseErrorInnerError
    """

    _attribute_map = {
        "message": {"key": "message", "type": "str"},
        "code": {"key": "code", "type": "str"},
        "inner_error": {"key": "innerError", "type": "BatchResponseErrorInnerError"},
    }

    def __init__(self, **kwargs):
        # type: (Any) -> None
        super(LogsBatchResponseError, self).__init__(**kwargs)
        self.message = kwargs.get("message", None)
        self.code = kwargs.get("code", None)
        self.inner_error = kwargs.get("inner_error", None)

class MetricNamespace(InternalMetricNamespace):
    """Metric namespace class specifies the metadata for a metric namespace.

    :param id: The ID of the metricNamespace.
    :type id: str
    :param type: The type of the namespace.
    :type type: str
    :param name: The name of the namespace.
    :type name: str
    :param properties: Properties which include the fully qualified namespace name.
    :type properties: ~monitor_query_client.models.MetricNamespaceName
    """

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'type': {'key': 'type', 'type': 'str'},
        'name': {'key': 'name', 'type': 'str'},
        'properties': {'key': 'properties', 'type': 'MetricNamespaceName'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(MetricNamespace, self).__init__(**kwargs)
        self.id = kwargs.get('id', None)
        self.type = kwargs.get('type', None)
        self.name = kwargs.get('name', None)
        self.properties = kwargs.get('properties', None)

class MetricDefinition(InternalMetricDefinition):
    """Metric definition class specifies the metadata for a metric.

    :param is_dimension_required: Flag to indicate whether the dimension is required.
    :type is_dimension_required: bool
    :param resource_id: the resource identifier of the resource that emitted the metric.
    :type resource_id: str
    :param namespace: the namespace the metric belongs to.
    :type namespace: str
    :param name: the name and the display name of the metric, i.e. it is a localizable string.
    :type name: ~monitor_query_client.models.LocalizableString
    :param unit: the unit of the metric. Possible values include: "Count", "Bytes", "Seconds",
     "CountPerSecond", "BytesPerSecond", "Percent", "MilliSeconds", "ByteSeconds", "Unspecified",
     "Cores", "MilliCores", "NanoCores", "BitsPerSecond".
    :type unit: str or ~monitor_query_client.models.Unit
    :param primary_aggregation_type: the primary aggregation type value defining how to use the
     values for display. Possible values include: "None", "Average", "Count", "Minimum", "Maximum",
     "Total".
    :type primary_aggregation_type: str or ~monitor_query_client.models.AggregationType
    :param supported_aggregation_types: the collection of what aggregation types are supported.
    :type supported_aggregation_types: list[str or ~monitor_query_client.models.AggregationType]
    :param metric_availabilities: the collection of what aggregation intervals are available to be
     queried.
    :type metric_availabilities: list[~monitor_query_client.models.MetricAvailability]
    :param id: the resource identifier of the metric definition.
    :type id: str
    :param dimensions: the name and the display name of the dimension, i.e. it is a localizable
     string.
    :type dimensions: list[~monitor_query_client.models.LocalizableString]
    """

    _attribute_map = {
        'is_dimension_required': {'key': 'isDimensionRequired', 'type': 'bool'},
        'resource_id': {'key': 'resourceId', 'type': 'str'},
        'namespace': {'key': 'namespace', 'type': 'str'},
        'name': {'key': 'name', 'type': 'LocalizableString'},
        'unit': {'key': 'unit', 'type': 'str'},
        'primary_aggregation_type': {'key': 'primaryAggregationType', 'type': 'str'},
        'supported_aggregation_types': {'key': 'supportedAggregationTypes', 'type': '[str]'},
        'metric_availabilities': {'key': 'metricAvailabilities', 'type': '[MetricAvailability]'},
        'id': {'key': 'id', 'type': 'str'},
        'dimensions': {'key': 'dimensions', 'type': '[LocalizableString]'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(MetricDefinition, self).__init__(**kwargs)
        self.is_dimension_required = kwargs.get('is_dimension_required', None)
        self.resource_id = kwargs.get('resource_id', None)
        self.namespace = kwargs.get('namespace', None)
        self.name = kwargs.get('name', None)
        self.unit = kwargs.get('unit', None)
        self.primary_aggregation_type = kwargs.get('primary_aggregation_type', None)
        self.supported_aggregation_types = kwargs.get('supported_aggregation_types', None)
        self.metric_availabilities = kwargs.get('metric_availabilities', None)
        self.id = kwargs.get('id', None)
        self.dimensions = kwargs.get('dimensions', None)
