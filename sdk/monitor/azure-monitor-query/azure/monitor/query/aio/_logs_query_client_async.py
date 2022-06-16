#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta
from typing import Any, Tuple, Union, Sequence, Dict, List, TYPE_CHECKING
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import HttpResponseError

from .._generated.aio._monitor_query_client import MonitorQueryClient

from .._generated.models import BatchRequest, QueryBody as LogsQueryBody
from .._helpers import construct_iso8601, order_results, process_error, process_prefer
from .._models import LogsQueryResult, LogsBatchQuery, LogsQueryPartialResult
from ._helpers_async import get_authentication_policy
from .._exceptions import LogsQueryError

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class LogsQueryClient(object): # pylint: disable=client-accepts-api-version-keyword
    """LogsQueryClient. Use this client to collect and organize log and performance data from
    monitored resources. Data from different sources such as platform logs from Azure services,
    log and performance data from virtual machines agents, and usage and performance data from
    apps can be consolidated into a single Azure Log Analytics workspace.

    The various data types can be analyzed together using the
    [Kusto Query Language](https://docs.microsoft.com/azure/data-explorer/kusto/query/)

    :param credential: The credential to authenticate the client
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword endpoint: The endpoint to connect to. Defaults to 'https://api.loganalytics.io/v1'.
    :paramtype endpoint: str
    """

    def __init__(self, credential: "AsyncTokenCredential", **kwargs: Any) -> None:
        endpoint = kwargs.pop("endpoint", "https://api.loganalytics.io")
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._client = MonitorQueryClient(
            credential=credential,
            authentication_policy=get_authentication_policy(credential, endpoint),
            base_url=self._endpoint.rstrip('/') + "/v1",
            **kwargs
        )
        self._query_op = self._client.query

    @distributed_trace_async
    async def query_workspace(
        self,
        workspace_id: str,
        query: str,
        *,
        timespan: Union[
            timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]
        ],
        **kwargs: Any
    ) -> Union[LogsQueryResult, LogsQueryPartialResult]:
        """Execute an Analytics query.

        Executes an Analytics query for data.

        :param workspace_id: ID of the workspace. This is Workspace ID from the Properties blade in the
         Azure portal.
        :type workspace_id: str
        :param query: The Kusto query. Learn more about the `Kusto query syntax
         <https://docs.microsoft.com/azure/data-explorer/kusto/query/>`_.
        :type query: str
        :keyword timespan: Required. The timespan for which to query the data. This can be a timedelta,
         a timedelta and a start datetime, or a start datetime/end datetime.
        :paramtype timespan: ~datetime.timedelta or tuple[~datetime.datetime, ~datetime.timedelta]
         or tuple[~datetime.datetime, ~datetime.datetime]
        :keyword int server_timeout: the server timeout in seconds. The default timeout is 3 minutes,
         and the maximum timeout is 10 minutes.
        :keyword bool include_statistics: To get information about query statistics.
        :keyword bool include_visualization: In the query language, it is possible to specify different
         visualization options. By default, the API does not return information regarding the type of
         visualization to show. If your client requires this information, specify the preference
        :keyword additional_workspaces: A list of workspaces that are included in the query.
         These can be qualified workspace names, workspace Ids, or Azure resource Ids.
        :paramtype additional_workspaces: list[str]
        :return: LogsQueryResult if there is a success or LogsQueryPartialResult when there is a partial success.
        :rtype: ~azure.monitor.query.LogsQueryResult or ~azure.monitor.query.LogsQueryPartialResult
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        timespan = construct_iso8601(timespan)
        include_statistics = kwargs.pop("include_statistics", False)
        include_visualization = kwargs.pop("include_visualization", False)
        server_timeout = kwargs.pop("server_timeout", None)
        additional_workspaces = kwargs.pop("additional_workspaces", None)

        prefer = process_prefer(
            server_timeout, include_statistics, include_visualization
        )

        body = LogsQueryBody(
            query=query, timespan=timespan, workspaces=additional_workspaces, **kwargs
        )

        try:
            generated_response = (
                await self._query_op.execute(  # pylint: disable=protected-access
                    workspace_id=workspace_id, body=body, prefer=prefer, **kwargs
                )
            )
        except HttpResponseError as err:
            process_error(err, LogsQueryError)
        response = None
        if not generated_response.error:
            response = LogsQueryResult._from_generated( # pylint: disable=protected-access
                generated_response
            )
        else:
            response = LogsQueryPartialResult._from_generated( # pylint: disable=protected-access
                generated_response, LogsQueryError
            )
        return response

    @distributed_trace_async
    async def query_batch(
        self, queries: Union[Sequence[Dict], Sequence[LogsBatchQuery]], **kwargs: Any
    ) -> List[Union[LogsQueryResult, LogsQueryError, LogsQueryPartialResult]]:
        """Execute a list of analytics queries. Each request can be either a LogsBatchQuery
        object or an equivalent serialized model.

        **NOTE**: The response is returned in the same order as that of the requests sent.

        :param queries: The list of Kusto queries to execute.
        :type queries: list[dict] or list[~azure.monitor.query.LogsBatchQuery]
        :return: List of LogsQueryResult, LogsQueryPartialResult and LogsQueryError.
         For a given query, a LogsQueryResult is returned if the response is a success, LogsQueryPartialResult
         is returned when there is a partial success and a LogsQueryError is returned when there is a failure.
         The status of each response can be checked using `LogsQueryStatus` enum.
        :rtype: list[~azure.monitor.query.LogsQueryResult or ~azure.monitor.query.LogsQueryPartialResult
         or ~azure.monitor.query.LogsQueryError]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        try:
            queries = [LogsBatchQuery(**q) for q in queries]  # type: ignore
        except (KeyError, TypeError):
            pass
        queries = [
            q._to_generated() for q in queries # pylint: disable=protected-access
        ]
        try:
            request_order = [req.id for req in queries]
        except AttributeError:
            request_order = [req["id"] for req in queries]
        batch = BatchRequest(requests=queries)
        generated = await self._query_op.batch(batch, **kwargs)
        mapping = {item.id: item for item in generated.responses}
        return order_results(
            request_order,
            mapping,
            obj=LogsQueryResult,
            err=LogsQueryError,
            partial_err=LogsQueryPartialResult,
            raise_with=LogsQueryError,
        )

    async def __aenter__(self) -> "LogsQueryClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.monitor.query.aio.LogsQueryClient` session."""
        await self._client.__aexit__()
