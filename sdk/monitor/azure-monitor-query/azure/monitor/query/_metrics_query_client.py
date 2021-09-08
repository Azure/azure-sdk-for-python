#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=anomalous-backslash-in-string

from typing import TYPE_CHECKING, Any, Optional
from msrest.serialization import Serializer
from azure.core.tracing.decorator import distributed_trace

from ._generated._monitor_query_client import (
    MonitorQueryClient,
)

from ._models import MetricsResult, MetricDefinition, MetricNamespace
from ._helpers import get_metrics_authentication_policy, construct_iso8601

if TYPE_CHECKING:
    from datetime import timedelta
    from azure.core.credentials import TokenCredential
    from azure.core.paging import ItemPaged


class MetricsQueryClient(object):
    """MetricsQueryClient

    .. admonition:: Example:

    .. literalinclude:: ../samples/sample_metrics_query_client.py
        :start-after: [START metrics_client_auth_with_token_cred]
        :end-before: [END metrics_client_auth_with_token_cred]
        :language: python
        :dedent: 0
        :caption: Creating the MetricsQueryClient with a TokenCredential.

    :param credential: The credential to authenticate the client.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword endpoint: The endpoint to connect to. Defaults to 'https://management.azure.com'.
    :paramtype endpoint: str
    """

    def __init__(self, credential, **kwargs):
        # type: (TokenCredential, Any) -> None
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

    @distributed_trace
    def query(self, resource_uri, metric_names, **kwargs):
        # type: (str, list, Optional[timedelta], Any) -> MetricsResult
        """Lists the metric values for a resource.

        :param resource_uri: The identifier of the resource.
        :type resource_uri: str
        :param metric_names: The names of the metrics to retrieve.
        :type metric_names: list[str]
        :keyword timespan: The timespan for which to query the data. This can be a timedelta,
         a timedelta and a start datetime, or a start datetime/end datetime.
        :paramtype timespan: ~datetime.timedelta or tuple[~datetime.datetime, ~datetime.timedelta]
         or tuple[~datetime.datetime, ~datetime.datetime]
        :keyword granularity: The granularity (i.e. timegrain) of the query.
        :paramtype granularity: ~datetime.timedelta
        :keyword aggregations: The list of aggregation types to retrieve. Use
         `azure.monitor.query.MetricAggregationType` enum to get each aggregation type.
        :paramtype aggregations: list[str]
        :keyword max_results: The maximum number of records to retrieve.
         Valid only if $filter is specified.
         Defaults to 10.
        :paramtype max_results: int
        :keyword order_by: The aggregation to use for sorting results and the direction of the sort.
         Only one order can be specified.
         Examples: sum asc.
        :paramtype order_by: str
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
        :keyword metric_namespace: Metric namespace to query metric definitions for.
        :paramtype metric_namespace: str
        :return: Response, or the result of cls(response)
        :rtype: ~azure.monitor.query.MetricsResult
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
        kwargs.setdefault("metricnames", ",".join(metric_names))
        kwargs.setdefault("timespan", timespan)
        kwargs.setdefault("top", kwargs.pop("max_results", None))
        kwargs.setdefault("interval", kwargs.pop("granularity", None))
        kwargs.setdefault("orderby", kwargs.pop("order_by", None))
        generated = self._metrics_op.list(resource_uri, connection_verify=False, **kwargs)
        return MetricsResult._from_generated(generated) # pylint: disable=protected-access

    @distributed_trace
    def list_metric_namespaces(self, resource_uri, **kwargs):
        # type: (str, Any) -> ItemPaged[MetricNamespace]
        """Lists the metric namespaces for the resource.

        :param resource_uri: The identifier of the resource.
        :type resource_uri: str
        :keyword start_time: The start time from which to query for metric
         namespaces. This should be provided as a datetime object.
        :paramtype start_time: ~datetime.datetime
        :return: An iterator like instance of either MetricNamespace or the result of cls(response)
        :rtype: ~azure.core.paging.ItemPaged[~azure.monitor.query.MetricNamespace]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        start_time = kwargs.pop('start_time', None)
        if start_time:
            start_time = Serializer.serialize_iso(start_time)
        return self._namespace_op.list(
            resource_uri,
            start_time,
            cls=kwargs.pop(
                "cls",
                lambda objs: [
                    MetricNamespace._from_generated(x) for x in objs # pylint: disable=protected-access
                ]
            ),
            **kwargs)

    @distributed_trace
    def list_metric_definitions(self, resource_uri, metric_namespace=None, **kwargs):
        # type: (str, str, Any) -> ItemPaged[MetricDefinition]
        """Lists the metric definitions for the resource.

        :param resource_uri: The identifier of the resource.
        :type resource_uri: str
        :keyword namespace: Metric namespace to query metric definitions for.
        :paramtype namespace: str
        :return: An iterator like instance of either MetricDefinitionCollection or the result of cls(response)
        :rtype: ~azure.core.paging.ItemPaged[~azure.monitor.query.MetricDefinition]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        metric_namespace = kwargs.pop('namespace', None)
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

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.monitor.query.MetricsQueryClient` session."""
        return self._client.close()

    def __enter__(self):
        # type: () -> MetricsQueryClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
