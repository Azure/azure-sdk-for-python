#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=anomalous-backslash-in-string
from typing import Any, cast, List

from azure.core.credentials import TokenCredential
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace

from ._generated._serialization import Serializer
from ._generated.metrics._client import MonitorMetricsClient
from ._models import MetricsQueryResult, MetricDefinition, MetricNamespace
from ._helpers import get_authentication_policy, construct_iso8601


class MetricsQueryClient(object):  # pylint: disable=client-accepts-api-version-keyword
    """MetricsQueryClient should be used to collect numeric data from monitored resources into a
    time series database. Metrics are numerical values that are collected at regular intervals and
    describe some aspect of a system at a particular time. Metrics are lightweight and capable of
    supporting near real-time scenarios, making them particularly useful for alerting and
    fast detection of issues.

    .. admonition:: Example:

    .. literalinclude:: ../samples/sample_metrics_query.py
        :start-after: [START metrics_client_auth_with_token_cred]
        :end-before: [END metrics_client_auth_with_token_cred]
        :language: python
        :dedent: 0
        :caption: Creating the MetricsQueryClient with a TokenCredential.

    :param credential: The credential to authenticate the client.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword endpoint: The endpoint to connect to. Defaults to 'https://management.azure.com'.
    :paramtype endpoint: Optional[str]
    """

    def __init__(self, credential: TokenCredential, **kwargs: Any) -> None:
        endpoint = kwargs.pop("endpoint", "https://management.azure.com")
        audience = kwargs.pop("audience", endpoint)
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        auth_policy = kwargs.pop("authentication_policy", None)
        self._client = MonitorMetricsClient(
            credential=credential,
            endpoint=self._endpoint,
            authentication_policy=auth_policy or get_authentication_policy(credential, audience),
            **kwargs
        )
        self._metrics_op = self._client.metrics
        self._namespace_op = self._client.metric_namespaces
        self._definitions_op = self._client.metric_definitions

    @distributed_trace
    def query_resource(self, resource_uri: str, metric_names: List[str], **kwargs: Any) -> MetricsQueryResult:
        """Lists the metric values for a resource.

        :param resource_uri: The identifier of the resource.
        :type resource_uri: str
        :param metric_names: The names of the metrics to retrieve.
        :type metric_names: list[str]
        :keyword timespan: The timespan for which to query the data. This can be a timedelta,
         a timedelta and a start datetime, or a start datetime/end datetime.
        :paramtype timespan: Optional[Union[~datetime.timedelta, tuple[~datetime.datetime, ~datetime.timedelta],
            tuple[~datetime.datetime, ~datetime.datetime]]]
        :keyword granularity: The granularity (i.e. timegrain) of the query.
        :paramtype granularity: Optional[~datetime.timedelta]
        :keyword aggregations: The list of aggregation types to retrieve. Use
         `azure.monitor.query.MetricAggregationType` enum to get each aggregation type.
        :paramtype aggregations: Optional[list[str]]
        :keyword max_results: The maximum number of records to retrieve.
         Valid only if $filter is specified.
         Defaults to 10.
        :paramtype max_results: Optional[int]
        :keyword order_by: The aggregation to use for sorting results and the direction of the sort.
         Only one order can be specified.
         Examples: sum asc.
        :paramtype order_by: Optional[str]
        :keyword filter: The **$filter** is used to reduce the set of metric data returned. Example:
         Metric contains metadata A, B and C. - Return all time series of C where A = a1 and B = b1 or
         b2 **$filter=A eq 'a1' and B eq 'b1' or B eq 'b2' and C eq '*'** - Invalid variant: **$filter=A
         eq 'a1' and B eq 'b1' and C eq '*' or B = 'b2'** This is invalid because the logical or
         operator cannot separate two different metadata names. - Return all time series where A = a1, B
         = b1 and C = c1: **$filter=A eq 'a1' and B eq 'b1' and C eq 'c1'** - Return all time series
         where A = a1 **$filter=A eq 'a1' and B eq '*' and C eq '*'**. Special case: When dimension
         name or dimension value uses round brackets. Eg: When dimension name is **dim (test) 1**
         Instead of using **$filter= "dim (test) 1 eq '*'"** use **$filter= "dim %2528test%2529 1 eq '*'"**.
         When dimension name is **dim (test) 3** and dimension value is **dim3 (test) val**, instead of using
         **$filter= "dim (test) 3 eq 'dim3 (test) val'"** use **$filter= "dim
         %2528test%2529 3 eq 'dim3 %2528test%2529 val'"**. Default value is None.
        :paramtype filter: Optional[str]
        :keyword metric_namespace: Metric namespace to query metric definitions for.
        :paramtype metric_namespace: Optional[str]
        :return: A MetricsQueryResult object.
        :rtype: ~azure.monitor.query.MetricsQueryResult
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

        .. literalinclude:: ../samples/sample_metrics_query_client.py
            :start-after: [START send_metrics_query]
            :end-before: [END send_metrics_query]
            :language: python
            :dedent: 0
            :caption: Get a response for a single Metrics Query
        """

        aggregations = kwargs.pop("aggregations", None)
        if aggregations:
            kwargs.setdefault("aggregation", ",".join(aggregations))
        timespan = construct_iso8601(kwargs.pop("timespan", None))
        # Metric names with commas need to be encoded.
        metric_names = [x.replace(",", "%2") for x in metric_names]
        kwargs.setdefault("metricnames", ",".join(metric_names))
        kwargs.setdefault("timespan", timespan)
        kwargs.setdefault("top", kwargs.pop("max_results", None))
        kwargs.setdefault("interval", kwargs.pop("granularity", None))
        kwargs.setdefault("orderby", kwargs.pop("order_by", None))
        kwargs.setdefault("metricnamespace", kwargs.pop("metric_namespace", None))
        generated = self._metrics_op.list(resource_uri, connection_verify=False, **kwargs)
        return MetricsQueryResult._from_generated(generated)  # pylint: disable=protected-access

    @distributed_trace
    def list_metric_namespaces(self, resource_uri: str, **kwargs: Any) -> ItemPaged[MetricNamespace]:
        """Lists the metric namespaces for the resource.

        :param resource_uri: The identifier of the resource.
        :type resource_uri: str
        :keyword start_time: The start time from which to query for metric
         namespaces. This should be provided as a datetime object.
        :paramtype start_time: Optional[~datetime.datetime]
        :return: An iterator like instance of either MetricNamespace or the result of cls(response)
        :rtype: ~azure.core.paging.ItemPaged[~azure.monitor.query.MetricNamespace]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        start_time = kwargs.pop("start_time", None)
        if start_time:
            start_time = Serializer.serialize_iso(start_time)
        res = self._namespace_op.list(
            resource_uri,
            start_time=start_time,
            cls=kwargs.pop(
                "cls",
                lambda objs: [MetricNamespace._from_generated(x) for x in objs],  # pylint: disable=protected-access
            ),
            **kwargs
        )
        return cast(ItemPaged[MetricNamespace], res)

    @distributed_trace
    def list_metric_definitions(self, resource_uri: str, **kwargs: Any) -> ItemPaged[MetricDefinition]:
        """Lists the metric definitions for the resource.

        :param resource_uri: The identifier of the resource.
        :type resource_uri: str
        :keyword namespace: Metric namespace to query metric definitions for.
        :paramtype namespace: Optional[str]
        :return: An iterator like instance of either MetricDefinition or the result of cls(response)
        :rtype: ~azure.core.paging.ItemPaged[~azure.monitor.query.MetricDefinition]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        metric_namespace = kwargs.pop("namespace", None)
        res = self._definitions_op.list(
            resource_uri,
            metricnamespace=metric_namespace,
            cls=kwargs.pop(
                "cls",
                lambda objs: [MetricDefinition._from_generated(x) for x in objs],  # pylint: disable=protected-access
            ),
            **kwargs
        )
        return cast(ItemPaged[MetricDefinition], res)

    def close(self) -> None:
        """Close the :class:`~azure.monitor.query.MetricsQueryClient` session."""
        return self._client.close()

    def __enter__(self) -> "MetricsQueryClient":
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.__exit__(*args)  # pylint:disable=no-member
