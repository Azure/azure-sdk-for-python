#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=anomalous-backslash-in-string

from typing import TYPE_CHECKING, Any, List

from azure.core.async_paging import AsyncItemPaged

from .._generated.aio._monitor_query_client import (
    MonitorQueryClient,
)
from .._models import MetricsResult, MetricDefinition, MetricNamespace
from ._helpers_asyc import get_metrics_authentication_policy
from .._helpers import construct_iso8601

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

class MetricsQueryClient(object):
    """MetricsQueryClient

    :param credential: The credential to authenticate the client
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword endpoint: The endpoint to connect to. Defaults to 'https://management.azure.com'.
    :paramtype endpoint: str
    """

    def __init__(self, credential: "AsyncTokenCredential", **kwargs: Any) -> None:
        endpoint = kwargs.pop('endpoint', 'https://management.azure.com')
        self._client = MonitorQueryClient(
            credential=credential,
            base_url=endpoint,
            authentication_policy=get_metrics_authentication_policy(credential),
            **kwargs
        )
        self._metrics_op = self._client.metrics
        self._namespace_op = self._client.metric_namespaces
        self._definitions_op = self._client.metric_definitions

    async def query(self, resource_uri: str, metric_names: List, duration: str = None, **kwargs: Any) -> MetricsResult:
        """Lists the metric values for a resource.

        **Note**: Although the start_time, end_time, duration are optional parameters, it is highly
        recommended to specify the timespan. If not, the entire dataset is queried.

        :param resource_uri: The identifier of the resource.
        :type resource_uri: str
        :param metric_names: The names of the metrics to retrieve.
        :type metric_names: list
        :param str duration: The duration for which to query the data. This can also be accompanied
         with either start_time or end_time. If start_time or end_time is not provided, the current time is
         taken as the end time. This should be provided in a ISO8601 string format like 'PT1H', 'P1Y2M10DT2H30M'.
        :keyword datetime start_time: The start time from which to query the data. This should be accompanied
         with either end_time or duration.
        :keyword datetime end_time: The end time till which to query the data. This should be accompanied
         with either start_time or duration.
        :keyword interval: The interval (i.e. timegrain) of the query.
        :paramtype interval: ~datetime.timedelta
        :keyword aggregation: The list of aggregation types (comma separated) to retrieve.
        :paramtype aggregation: str
        :keyword top: The maximum number of records to retrieve.
         Valid only if $filter is specified.
         Defaults to 10.
        :paramtype top: int
        :keyword orderby: The aggregation to use for sorting results and the direction of the sort.
         Only one order can be specified.
         Examples: sum asc.
        :paramtype orderby: str
        :keyword filter: The **$filter** is used to reduce the set of metric data
         returned.:code:`<br>`Example::code:`<br>`Metric contains metadata A, B and C.:code:`<br>`-
         Return all time series of C where A = a1 and B = b1 or b2:code:`<br>`\ **$filter=A eq ‘a1’ and
         B eq ‘b1’ or B eq ‘b2’ and C eq ‘*’**\ :code:`<br>`- Invalid variant::code:`<br>`\ **$filter=A
         eq ‘a1’ and B eq ‘b1’ and C eq ‘*’ or B = ‘b2’**\ :code:`<br>`This is invalid because the
         logical or operator cannot separate two different metadata names.:code:`<br>`- Return all time
         series where A = a1, B = b1 and C = c1::code:`<br>`\ **$filter=A eq ‘a1’ and B eq ‘b1’ and C eq
         ‘c1’**\ :code:`<br>`- Return all time series where A = a1:code:`<br>`\ **$filter=A eq ‘a1’ and
         B eq ‘\ *’ and C eq ‘*\ ’**.
        :paramtype filter: str
        :keyword result_type: Reduces the set of data collected. The syntax allowed depends on the
         operation. See the operation's description for details.
        :paramtype result_type: str or ~monitor_query_client.models.ResultType
        :keyword metric_namespace: Metric namespace to query metric definitions for.
        :paramtype metric_namespace: str
        :return: Response, or the result of cls(response)
        :rtype: ~azure.monitor.query.MetricsResult
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        start = kwargs.pop('start_time', None)
        end = kwargs.pop('end_time', None)
        timespan = construct_iso8601(start, end, duration)
        kwargs.setdefault("metricnames", ",".join(metric_names))
        kwargs.setdefault("timespan", timespan)
        generated = await self._metrics_op.list(resource_uri, connection_verify=False, **kwargs)
        return MetricsResult._from_generated(generated) # pylint: disable=protected-access

    def list_metric_namespaces(self, resource_uri: str, **kwargs: Any) -> AsyncItemPaged[MetricNamespace]:
        """Lists the metric namespaces for the resource.

        :param resource_uri: The identifier of the resource.
        :type resource_uri: str
        :keyword start_time: The ISO 8601 conform Date start time from which to query for metric
         namespaces.
        :paramtype start_time: str
        :return: An iterator like instance of either MetricNamespaceCollection or the result of cls(response)
        :rtype: ~azure.core.paging.ItemPaged[~azure.monitor.query.MetricNamespace]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._namespace_op.list(
            resource_uri,
            cls=kwargs.pop(
                "cls",
                lambda objs: [
                    MetricNamespace._from_generated(x) for x in objs # pylint: disable=protected-access
                ]
            ),
            **kwargs)

    def list_metric_definitions(
        self,
        resource_uri: str,
        metric_namespace: str = None,
        **kwargs: Any
        ) -> AsyncItemPaged[MetricDefinition]:
        """Lists the metric definitions for the resource.

        :param resource_uri: The identifier of the resource.
        :type resource_uri: str
        :param metric_namespace: Metric namespace to query metric definitions for.
        :type metric_namespace: str
        :return: An iterator like instance of either MetricDefinitionCollection or the result of cls(response)
        :rtype: ~azure.core.paging.ItemPaged[~azure.monitor.query.MetricDefinition]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._definitions_op.list(
            resource_uri,
            metric_namespace,
            cls=kwargs.pop(
                "cls",
                lambda objs: [
                    MetricDefinition._from_generated(x) for x in objs # pylint: disable=protected-access
                ]
            ),
            **kwargs)

    async def __aenter__(self) -> "MetricsQueryClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.monitor.query.aio.MetricsQueryClient` session."""
        await self._client.__aexit__()
