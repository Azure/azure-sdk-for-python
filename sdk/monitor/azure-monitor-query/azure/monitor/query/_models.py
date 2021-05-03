#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._generated.models import (
    QueryResults,
    Table,
    Column,
    Response,
)

class LogQueryResultTable(Table):
    """Contains the columns and rows for one table in a query response.

    All required parameters must be populated in order to send to Azure.

    :param name: Required. The name of the table.
    :type name: str
    :param columns: Required. The list of columns in this table.
    :type columns: list[~monitor_query_client.models.Column]
    :param rows: Required. The resulting rows from this query.
    :type rows: list[list[str]]
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
        super(LogQueryResultTable, self).__init__(**kwargs)
        self.name = kwargs['name']
        self.columns = kwargs['columns']
        self.rows = kwargs['rows']


class LogQueryResultColumn(Column):
    """A column in a table.

    :param name: The name of this column.
    :type name: str
    :param type: The data type of this column.
    :type type: str
    """

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'type': {'key': 'type', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(LogQueryResultColumn, self).__init__(**kwargs)
        self.name = kwargs.get('name', None)
        self.type = kwargs.get('type', None)


class LogQueryResults(QueryResults):
    """Contains the tables, columns & rows resulting from a query.

    :param tables: The list of tables, columns and rows.
    :type tables: list[~monitor_query_client.models.Table]
    :param errors:
    :type errors: ~monitor_query_client.models.ErrorDetails
    """

    _attribute_map = {
        'tables': {'key': 'tables', 'type': '[Table]'},
        'errors': {'key': 'errors', 'type': 'ErrorDetails'},
    }

    def __init__(
        self,
        **kwargs
    ):
        super(LogQueryResults, self).__init__(**kwargs)
        self.tables = kwargs.get('tables', None)
        self.errors = kwargs.get('errors', None)

class MetricsResponse(Response):
    """The response to a metrics query.

    All required parameters must be populated in order to send to Azure.

    :param cost: The integer value representing the cost of the query, for data case.
    :type cost: int
    :param timespan: Required. The timespan for which the data was retrieved. Its value consists of
     two datetimes concatenated, separated by '/'.  This may be adjusted in the future and returned
     back from what was originally requested.
    :type timespan: str
    :param interval: The interval (window size) for which the metric data was returned in.  This
     may be adjusted in the future and returned back from what was originally requested.  This is
     not present if a metadata request was made.
    :type interval: ~datetime.timedelta
    :param namespace: The namespace of the metrics been queried.
    :type namespace: str
    :param resourceregion: The region of the resource been queried for metrics.
    :type resourceregion: str
    :param value: Required. the value of the collection.
    :type value: list[~monitor_query_client.models.Metric]
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
        super(MetricsResponse, self).__init__(**kwargs)
        self.cost = kwargs.get('cost', None)
        self.timespan = kwargs['timespan']
        self.interval = kwargs.get('interval', None)
        self.namespace = kwargs.get('namespace', None)
        self.resourceregion = kwargs.get('resourceregion', None)
        self.value = kwargs['value']
