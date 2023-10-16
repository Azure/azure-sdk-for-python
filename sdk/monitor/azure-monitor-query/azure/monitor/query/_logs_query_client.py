#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import timedelta, datetime
from typing import Any, Union, Sequence, Dict, List, cast, Tuple, Optional, MutableMapping
from urllib.parse import urlparse

from azure.core.credentials import TokenCredential
from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace

from ._generated._client import MonitorQueryClient
from ._helpers import (
    get_authentication_policy,
    construct_iso8601,
    order_results,
    process_error,
    process_prefer,
)
from ._models import LogsBatchQuery, LogsQueryResult, LogsQueryPartialResult
from ._exceptions import LogsQueryError

JSON = MutableMapping[str, Any]


class LogsQueryClient(object):  # pylint: disable=client-accepts-api-version-keyword
    """LogsQueryClient. Use this client to collect and organize log and performance data from
    monitored resources. Data from different sources such as platform logs from Azure services,
    log and performance data from virtual machines agents, and usage and performance data from
    apps can be consolidated into a single Azure Log Analytics workspace.

    The various data types can be analyzed together using the
    [Kusto Query Language](https://learn.microsoft.com/azure/data-explorer/kusto/query/)

    :param credential: The credential to authenticate the client.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword endpoint: The endpoint to connect to. Defaults to 'https://api.loganalytics.io/v1'.
    :paramtype endpoint: Optional[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_logs_query_client]
            :end-before: [END create_logs_query_client]
            :language: python
            :dedent: 4
            :caption: Creating the LogsQueryClient with a TokenCredential.
    """

    def __init__(self, credential: TokenCredential, **kwargs: Any) -> None:
        endpoint = kwargs.pop("endpoint", "https://api.loganalytics.io/v1")
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        parsed_endpoint = urlparse(endpoint)
        audience = kwargs.pop("audience", f"{parsed_endpoint.scheme}://{parsed_endpoint.netloc}")
        self._endpoint = endpoint
        auth_policy = kwargs.pop("authentication_policy", None)
        self._client = MonitorQueryClient(
            credential=credential,
            authentication_policy=auth_policy or get_authentication_policy(credential, audience),
            endpoint=self._endpoint,
            **kwargs,
        )
        self._query_op = self._client.query

    @distributed_trace
    def query_workspace(
        self,
        workspace_id: str,
        query: str,
        *,
        timespan: Optional[Union[timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]]],
        server_timeout: Optional[int] = None,
        include_statistics: bool = False,
        include_visualization: bool = False,
        additional_workspaces: Optional[Sequence[str]] = None,
        **kwargs: Any,
    ) -> Union[LogsQueryResult, LogsQueryPartialResult]:
        """Execute a Kusto query.

        Executes a Kusto query for data.

        :param workspace_id: ID of the workspace. This is Workspace ID from the Properties blade in the
         Azure portal.
        :type workspace_id: str
        :param query: The Kusto query. Learn more about the `Kusto query syntax
         <https://learn.microsoft.com/azure/data-explorer/kusto/query/>`_.
        :type query: str
        :keyword timespan: Required. The timespan for which to query the data. This can be a timedelta,
         a timedelta and a start datetime, or a start datetime/end datetime. Set to None to not constrain
         the query to a timespan.
        :paramtype timespan: ~datetime.timedelta or tuple[~datetime.datetime, ~datetime.timedelta]
         or tuple[~datetime.datetime, ~datetime.datetime] or None
        :keyword int server_timeout: the server timeout in seconds. The default timeout is 3 minutes,
         and the maximum timeout is 10 minutes.
        :keyword bool include_statistics: To get information about query statistics.
        :keyword bool include_visualization: In the query language, it is possible to specify different
         visualization options. By default, the API does not return information regarding the type of
         visualization to show. If your client requires this information, specify the preference.
        :keyword additional_workspaces: A list of workspaces that are included in the query.
         These can be qualified workspace names, workspace IDs, or Azure resource IDs.
        :paramtype additional_workspaces: Optional[list[str]]
        :return: LogsQueryResult if there is a success or LogsQueryPartialResult when there is a partial success.
        :rtype: Union[~azure.monitor.query.LogsQueryResult, ~azure.monitor.query.LogsQueryPartialResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_logs_single_query.py
                :start-after: [START send_logs_query]
                :end-before: [END send_logs_query]
                :language: python
                :dedent: 0
                :caption: Get a response for a single log query.
        """
        timespan_iso = construct_iso8601(timespan)
        prefer = process_prefer(server_timeout, include_statistics, include_visualization)

        body = {"query": query, "timespan": timespan_iso, "workspaces": additional_workspaces}

        generated_response: JSON = {}
        try:
            generated_response = self._query_op.execute(  # pylint: disable=protected-access
                workspace_id=workspace_id, body=body, prefer=prefer, **kwargs
            )
        except HttpResponseError as err:
            process_error(err, LogsQueryError)

        response: Union[LogsQueryResult, LogsQueryPartialResult]
        if not generated_response.get("error"):
            response = LogsQueryResult._from_generated(generated_response)  # pylint: disable=protected-access
        else:
            response = LogsQueryPartialResult._from_generated(  # pylint: disable=protected-access
                generated_response, LogsQueryError
            )
        return response

    @distributed_trace
    def query_batch(
        self, queries: Union[Sequence[Dict], Sequence[LogsBatchQuery]], **kwargs: Any
    ) -> List[Union[LogsQueryResult, LogsQueryError, LogsQueryPartialResult]]:
        """Execute a list of Kusto queries. Each request can be either a LogsBatchQuery
        object or an equivalent serialized model.

        **NOTE**: The response is returned in the same order as that of the requests sent.

        :param queries: The list of Kusto queries to execute.
        :type queries: list[dict] or list[~azure.monitor.query.LogsBatchQuery]
        :return: List of LogsQueryResult, LogsQueryPartialResult and LogsQueryError.
         For a given query, a LogsQueryResult is returned if the response is a success, LogsQueryPartialResult
         is returned when there is a partial success and a LogsQueryError is returned when there is a failure.
         The status of each response can be checked using `LogsQueryStatus` enum.
        :rtype: list[Union[~azure.monitor.query.LogsQueryResult, ~azure.monitor.query.LogsQueryPartialResult,
         ~azure.monitor.query.LogsQueryError]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_batch_query.py
                :start-after: [START send_query_batch]
                :end-before: [END send_query_batch]
                :language: python
                :dedent: 0
                :caption: Execute multiple queries in a batch.
        """
        try:
            queries = [LogsBatchQuery(**cast(Dict, q)) for q in queries]
        except (KeyError, TypeError):
            pass
        queries = [cast(LogsBatchQuery, q)._to_generated() for q in queries]  # pylint: disable=protected-access
        request_order = [req["id"] for req in queries]
        batch = {"requests": queries}
        generated = self._query_op.batch(batch, **kwargs)
        mapping = {item["id"]: item for item in generated["responses"]}
        return order_results(
            request_order,
            mapping,
            obj=LogsQueryResult,
            err=LogsQueryError,
            partial_err=LogsQueryPartialResult,
            raise_with=LogsQueryError,
        )

    @distributed_trace
    def query_resource(
        self,
        resource_id: str,
        query: str,
        *,
        timespan: Optional[Union[timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]]],
        server_timeout: Optional[int] = None,
        include_statistics: bool = False,
        include_visualization: bool = False,
        additional_workspaces: Optional[Sequence[str]] = None,
        **kwargs: Any,
    ) -> Union[LogsQueryResult, LogsQueryPartialResult]:
        """Execute a Kusto query on a resource.

        Returns all the Azure Monitor logs matching the given Kusto query for an Azure resource.

        :param resource_id: The identifier of the resource. The expected format is
         '/subscriptions/<sid>/resourceGroups/<rg>/providers/<providerName>/<resourceType>/<resourceName>'.
        :type resource_id: str
        :param query: The Kusto query. Learn more about the `Kusto query syntax
         <https://learn.microsoft.com/azure/data-explorer/kusto/query/>`_.
        :type query: str
        :keyword timespan: Required. The timespan for which to query the data. This can be a timedelta,
         a timedelta and a start datetime, or a start datetime/end datetime. Set to None to not constrain
         the query to a timespan.
        :paramtype timespan: ~datetime.timedelta or tuple[~datetime.datetime, ~datetime.timedelta]
         or tuple[~datetime.datetime, ~datetime.datetime] or None
        :keyword int server_timeout: the server timeout in seconds. The default timeout is 3 minutes,
         and the maximum timeout is 10 minutes.
        :keyword bool include_statistics: To get information about query statistics.
        :keyword bool include_visualization: In the query language, it is possible to specify different
         visualization options. By default, the API does not return information regarding the type of
         visualization to show. If your client requires this information, specify the preference.
        :keyword additional_workspaces: A list of workspaces that are included in the query.
         These can be qualified workspace names, workspace IDs, or Azure resource IDs.
        :paramtype additional_workspaces: Optional[list[str]]
        :return: LogsQueryResult if there is a success or LogsQueryPartialResult when there is a partial success.
        :rtype: Union[~azure.monitor.query.LogsQueryResult, ~azure.monitor.query.LogsQueryPartialResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_resource_logs_query.py
                :start-after: [START resource_logs_query]
                :end-before: [END resource_logs_query]
                :language: python
                :dedent: 0
                :caption: Get a response for a single query on a resource's logs.
        """
        timespan_iso = construct_iso8601(timespan)
        prefer = process_prefer(server_timeout, include_statistics, include_visualization)

        body = {"query": query, "timespan": timespan_iso, "workspaces": additional_workspaces}

        generated_response: JSON = {}
        try:
            generated_response = self._query_op.resource_execute(  # pylint: disable=protected-access
                resource_id=resource_id, body=body, prefer=prefer, **kwargs
            )
        except HttpResponseError as err:
            process_error(err, LogsQueryError)

        response: Union[LogsQueryResult, LogsQueryPartialResult]
        if not generated_response.get("error"):
            response = LogsQueryResult._from_generated(generated_response)  # pylint: disable=protected-access
        else:
            response = LogsQueryPartialResult._from_generated(  # pylint: disable=protected-access
                generated_response, LogsQueryError
            )
        return response

    def close(self) -> None:
        """Close the :class:`~azure.monitor.query.LogsQueryClient` session."""
        return self._client.close()

    def __enter__(self) -> "LogsQueryClient":
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.__exit__(*args)  # pylint:disable=no-member
