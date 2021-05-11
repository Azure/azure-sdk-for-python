#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Any, Union, Sequence

from ._generated._monitor_query_client import (
    MonitorQueryClient
)

from ._generated.models import BatchRequest, QueryBody
from ._helpers import get_authentication_policy
from ._models import LogsQueryResults, LogsQueryRequest, LogsQueryBody

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from ._generated.models import BatchResponse

class LogsClient(object):
    """LogsClient

    :param credential: The credential to authenticate the client
    :type credential: ~azure.core.credentials.TokenCredential
    """

    def __init__(self, credential, **kwargs):
        # type: (TokenCredential, Any) -> None
        self._client = MonitorQueryClient(
            credential=credential,
            authentication_policy=get_authentication_policy(credential),
            **kwargs
        )
        self._query_op = self._client.query

    def query(self, workspace_id, query, **kwargs):
        # type: (str, str, Any) -> LogsQueryResults
        """Execute an Analytics query.

        Executes an Analytics query for data.

        :param workspace_id: ID of the workspace. This is Workspace ID from the Properties blade in the
         Azure portal.
        :type workspace_id: str
        :param query: The Analytics query. Learn more about the `Analytics query syntax
         <https://azure.microsoft.com/documentation/articles/app-insights-analytics-reference/>`_.
        :type query: str
        :keyword ~datetime.timedelta timespan: Optional. The timespan over which to query data. This is an ISO8601 time
         period value.  This timespan is applied in addition to any that are specified in the query
         expression.
        :keyword int timeout: the server timeout. The default timeout is 3 minutes,
         and the maximum timeout is 10 minutes.
        :keyword bool include_statistics: To get information about query statistics.
        :keyword bool include_render: In the query language, it is possible to specify different render options.
         By default, the API does not return information regarding the type of visualization to show.
         If your client requires this information, specify the preference
        :return: QueryResults, or the result of cls(response)
        :rtype: ~azure.monitor.query.LogsQueryResults
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        timespan = kwargs.pop("timespan", None)
        include_statistics = kwargs.pop("include_statistics", False)
        include_render = kwargs.pop("include_render", False)
        timeout = kwargs.pop("timeout", None)
        
        prefer = ""
        if timeout:
            prefer += "wait=" + str(timeout)
        if include_statistics:
            prefer += " include-statistics=true"
        if include_render:
            prefer += " include-render=true"
        
        if prefer:
            kwargs.setdefault("prefer", prefer)
            return self._query_op.execute(
                workspace_id,
                LogsQueryBody(query, workspace_ids=[workspace_id]),
                **kwargs
                )

        kwargs.setdefault("timespan", timespan)
        return self._query_op.get(workspace_id, query, **kwargs)

    def batch_query(self, queries, **kwargs):
        # type: (Union[Sequence[Dict], Sequence[LogsQueryRequest], Any) -> LogsBatchResponse
        """Execute an Analytics query.

        Executes an Analytics query for data.

        :param queries: The list of queries that should be processed
        :type queries: list[dict] or list[~azure.monitor.query.LogsQueryRequest]
        :return: BatchResponse, or the result of cls(response)
        :rtype: ~azure.monitor.query.LogsBatchResponse
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        try:
            queries = [LogsQueryRequest(**q) for q in queries]
        except (KeyError, TypeError):
            pass
        batch = BatchRequest(requests=queries)
        return self._query_op.batch(batch, **kwargs)

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.monitor.query.LogsClient` session."""
        return self._client.close()

    def __enter__(self):
        # type: () -> LogsClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
