#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# cspell:ignore milli
from collections.abc import Mapping
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional, List, Union, Tuple, Dict, Iterator, Literal

from ._enums import LogsQueryStatus
from ._exceptions import LogsQueryError
from ._helpers import construct_iso8601, process_row


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
        """This will iterate over the row directly.

        :return: An iterator over the row.
        :rtype: Iterator
        """
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
        :return: The value of the column or the element in the row.
        :rtype: Any
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
        self.columns_types = kwargs.pop("columns_types", [])
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
            columns_types=[col["type"] for col in generated.get("columns", [])],
            rows=generated.get("rows"),
        )


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
        timespan: Optional[Union[timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]]],
        **kwargs: Any,
    ) -> None:
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
        self.id: str = str(uuid.uuid4())
        self.body: Dict[str, Any] = {
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
            "method": "POST",
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
    status: Literal[LogsQueryStatus.SUCCESS]
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
                LogsTable._from_generated(table) for table in generated["tables"]  # pylint: disable=protected-access
            ]
        return cls(
            tables=tables,
            statistics=generated.get("statistics"),
            visualization=generated.get("render"),
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
    status: Literal[LogsQueryStatus.PARTIAL]
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
                LogsTable._from_generated(table) for table in generated["tables"]  # pylint: disable=protected-access
            ]
        return cls(
            partial_data=partial_data,
            partial_error=error._from_generated(generated.get("error")),  # pylint: disable=protected-access
            statistics=generated.get("statistics"),
            visualization=generated.get("render"),
        )
