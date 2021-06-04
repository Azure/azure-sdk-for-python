#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Union, Sequence, Dict, TYPE_CHECKING
from azure.core.exceptions import HttpResponseError
from .._generated.aio._monitor_query_client import MonitorQueryClient

from .._generated.models import BatchRequest
from .._helpers import process_error, construct_iso8601
from .._models import LogsQueryResults, LogsQueryRequest, LogsQueryBody, LogsBatchResults
from ._helpers_asyc import get_authentication_policy

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class LogsQueryClient(object):
    """LogsQueryClient

    :param credential: The credential to authenticate the client
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword endpoint: The endpoint to connect to. Defaults to 'https://api.loganalytics.io/v1'.
    :paramtype endpoint: str
    """

    def __init__(self, credential: "AsyncTokenCredential", **kwargs: Any) -> None:
        self._endpoint = kwargs.pop('endpoint', 'https://api.loganalytics.io/v1')
        self._client = MonitorQueryClient(
            credential=credential,
            authentication_policy=get_authentication_policy(credential),
            base_url=self._endpoint,
            **kwargs
        )
        self._query_op = self._client.query

    async def query(
        self,
        workspace_id: str,
        query: str,
        duration: str = None,
        **kwargs: Any) -> LogsQueryResults:
        """Execute an Analytics query.

        Executes an Analytics query for data.

        **Note**: Although the start_time, end_time, duration are optional parameters, it is highly
        recommended to specify the timespan. If not, the entire dataset is queried.

        :param workspace_id: ID of the workspace. This is Workspace ID from the Properties blade in the
         Azure portal.
        :type workspace_id: str
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
        :keyword int server_timeout: the server timeout. The default timeout is 3 minutes,
         and the maximum timeout is 10 minutes.
        :keyword bool include_statistics: To get information about query statistics.
        :keyword bool include_render: In the query language, it is possible to specify different render options.
         By default, the API does not return information regarding the type of visualization to show.
         If your client requires this information, specify the preference
        :keyword workspaces: A list of workspaces that are included in the query.
        :paramtype workspaces: list[str]
        :keyword qualified_names: A list of qualified workspace names that are included in the query.
        :paramtype qualified_names: list[str]
        :keyword workspace_ids: A list of workspace IDs that are included in the query.
        :paramtype workspace_ids: list[str]
        :keyword azure_resource_ids: A list of Azure resource IDs that are included in the query.
        :paramtype azure_resource_ids: list[str]
        :return: QueryResults, or the result of cls(response)
        :rtype: ~azure.monitor.query.LogsQueryResults
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        start = kwargs.pop('start_time', None)
        end = kwargs.pop('end_time', None)
        timespan = construct_iso8601(start, end, duration)
        include_statistics = kwargs.pop("include_statistics", False)
        include_render = kwargs.pop("include_render", False)
        server_timeout = kwargs.pop("server_timeout", None)

        prefer = ""
        if server_timeout:
            prefer += "wait=" + str(server_timeout)
        if include_statistics:
            if len(prefer) > 0:
                prefer += ";"
            prefer += "include-statistics=true"
        if include_render:
            if len(prefer) > 0:
                prefer += ";"
            prefer += "include-render=true"

        body = LogsQueryBody(
            query=query,
            timespan=timespan,
            **kwargs
        )

        try:
            return LogsQueryResults._from_generated(await self._query_op.execute( # pylint: disable=protected-access
                workspace_id=workspace_id,
                body=body,
                prefer=prefer,
                **kwargs
            ))
        except HttpResponseError as e:
            process_error(e)

    async def batch_query(
        self,
        queries: Union[Sequence[Dict], Sequence[LogsQueryRequest]],
        **kwargs: Any
        ) -> LogsBatchResults:
        """Execute a list of analytics queries. Each request can be either a LogQueryRequest
        object or an equivalent serialized model.

        The response is returned in the same order as that of the requests sent.

        :param queries: The list of queries that should be processed
        :type queries: list[dict] or list[~azure.monitor.query.LogsQueryRequest]
        :return: BatchResponse, or the result of cls(response)
        :rtype: ~azure.monitor.query.LogsBatchResults
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        try:
            queries = [LogsQueryRequest(**q) for q in queries]
        except (KeyError, TypeError):
            pass
        try:
            request_order = [req.id for req in queries]
        except AttributeError:
            request_order = [req['id'] for req in queries]
        batch = BatchRequest(requests=queries)
        return LogsBatchResults._from_generated( # pylint: disable=protected-access
            await self._query_op.batch(batch, **kwargs), request_order
            )

    async def __aenter__(self) -> "LogsQueryClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.monitor.query.aio.LogsQueryClient` session."""
        await self._client.__aexit__()
