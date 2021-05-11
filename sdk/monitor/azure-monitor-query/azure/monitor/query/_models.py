#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
from ._generated.models import (
    QueryResults,
    Table,
    Column,
    Response,
    QueryBody,
    BatchResponse,
    LogQueryRequest as InternalLogQueryRequest
)

class LogsQueryResultTable(Table):
    """Contains the columns and rows for one table in a query response.

    All required parameters must be populated in order to send to Azure.

    :keyword name: Required. The name of the table.
    :paramtype name: str
    :keyword columns: Required. The list of columns in this table.
    :paramtype columns: list[~monitor_query_client.models.Column]
    :keyword rows: Required. The resulting rows from this query.
    :paramtype rows: list[list[str]]
    """

    _validation = {
        'name': {'required': True},
        'columns': {'required': True},
        'rows': {'required': True},
    }

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'columns': {'key': 'columns', 'type': '[Column]'},
        'rows': {'key': 'rows', 'type': '[[str]]'},
    }

    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        super(LogsQueryResultTable, self).__init__(**kwargs)
        self.name = kwargs['name']
        self.columns = kwargs['columns']
        self.rows = kwargs['rows']


class LogsQueryResultColumn(Column):
    """A column in a table.

    :keyword name: The name of this column.
    :paramtype name: str
    :keyword type: The data type of this column.
    :paramtype type: str
    """

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'type': {'key': 'type', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        super(LogsQueryResultColumn, self).__init__(**kwargs)
        self.name = kwargs.get('name', None)
        self.type = kwargs.get('type', None)


class LogsQueryResults(QueryResults):
    """Contains the tables, columns & rows resulting from a query.

    :keyword tables: The list of tables, columns and rows.
    :paramtype tables: list[~monitor_query_client.models.Table]
    :keyword errors:
    :paramtype errors: ~monitor_query_client.models.ErrorDetails
    """

    _attribute_map = {
        'tables': {'key': 'tables', 'type': '[Table]'},
        'errors': {'key': 'errors', 'type': 'ErrorDetails'},
    }

    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        super(LogsQueryResults, self).__init__(**kwargs)
        self.tables = kwargs.get('tables', None)
        self.errors = kwargs.get('errors', None)

class MetricsResponse(Response):
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
        'cost': {'minimum': 0},
        'timespan': {'required': True},
        'value': {'required': True},
    }

    _attribute_map = {
        'cost': {'key': 'cost', 'type': 'int'},
        'timespan': {'key': 'timespan', 'type': 'str'},
        'interval': {'key': 'interval', 'type': 'duration'},
        'namespace': {'key': 'namespace', 'type': 'str'},
        'resourceregion': {'key': 'resourceregion', 'type': 'str'},
        'value': {'key': 'value', 'type': '[Metric]'},
    }

    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        super(MetricsResponse, self).__init__(**kwargs)
        self.cost = kwargs.get('cost', None)
        self.timespan = kwargs['timespan']
        self.interval = kwargs.get('interval', None)
        self.namespace = kwargs.get('namespace', None)
        self.resourceregion = kwargs.get('resourceregion', None)
        self.value = kwargs['value']

class LogsQueryRequest(InternalLogQueryRequest):
    """An single request in a batch.

    Variables are only populated by the server, and will be ignored when sending a request.

    :keyword id: The error details.
    :paramtype id: str
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
        self.id = kwargs.get('id', uuid.uuid4())
        self.headers = kwargs.get('headers', {
            "Content-Type": "application/json"
        })
        self.body = kwargs.get('body', None)
        self.workspace = kwargs.get('workspace', None)


class LogsQueryBody(QueryBody):
    """The Analytics query. Learn more about the `Analytics query syntax <https://azure.microsoft.com/documentation/articles/app-insights-analytics-reference/>`_.

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
        super(QueryBody, self).__init__(**kwargs)
        kwargs.setdefault("query", query)
        self.timespan = kwargs.get('timespan', None)
        self.workspaces = kwargs.get('workspaces', None)
        self.qualified_names = kwargs.get('qualified_names', None)
        self.workspace_ids = kwargs.get('workspace_ids', None)
        self.azure_resource_ids = kwargs.get('azure_resource_ids', None)

class LogsBatchResponse(BatchResponse):
    """Response to a batch.

    :keyword responses: An array of responses corresponding to each individual request in a batch.
    :paramtype responses: list[~monitor_query_client.models.LogQueryResponse]
    :keyword error: Error response for a batch request.
    :paramtype error: ~monitor_query_client.models.BatchResponseError
    """

    _attribute_map = {
        'responses': {'key': 'responses', 'type': '[LogQueryResponse]'},
        'error': {'key': 'error', 'type': 'BatchResponseError'},
    }

    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        super(LogsBatchResponse, self).__init__(**kwargs)
        self.responses = kwargs.get('responses', None)
        self.error = kwargs.get('error', None)
