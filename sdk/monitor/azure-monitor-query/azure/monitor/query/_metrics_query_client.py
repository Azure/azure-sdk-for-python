#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=anomalous-backslash-in-string

from typing import TYPE_CHECKING, Any, Union

from ._generated._monitor_query_client import (
    MonitorQueryClient,
)

from ._helpers import get_authentication_policy

if TYPE_CHECKING:
    from azure.identity import DefaultAzureCredential
    from azure.core.credentials import TokenCredential
    from azure.core.paging import ItemPaged
    from ._models import MetricsResponse
    from ._generated.models import MetricNamespaceCollection

class MetricsClient(object):
    """MetricsClient

    :param credential: The credential to authenticate the client
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.identity.DefaultAzureCredential
    """

    def __init__(self, credential, **kwargs):
        # type: (TokenCredential, Any) -> None
        self._client = MonitorQueryClient(
            credential=credential,
            authentication_policy=get_authentication_policy(credential),
            **kwargs
        )
        self._metrics_op = self._client.metrics
        self._namespace_op = self._client.metric_namespaces

    def query(self, resource_uri, metricnames, **kwargs):
        # type: (str, str, Any) -> MetricsResponse
        """Lists the metric values for a resource.

        :param resource_uri: The identifier of the resource.
        :type resource_uri: str
        :param metricnames: The names of the metrics (comma separated) to retrieve.
        :type metricnames: str
        :keyword timespan: The timespan of the query. It is a string with the following format
         'startDateTime_ISO/endDateTime_ISO'.
        :paramtype timespan: str
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
        :keyword metricnamespace: Metric namespace to query metric definitions for.
        :paramtype metricnamespace: str
        :return: Response, or the result of cls(response)
        :rtype: ~azure.monitor.query.MetricsResponse
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._metrics_op.list(resource_uri, connection_verify=False, **kwargs)

    def get_metric_namespaces(self, resource_uri, **kwargs):
        # type: (str, Any) -> ItemPaged[MetricNamespaceCollection]
        """Lists the metric namespaces for the resource.

        :param resource_uri: The identifier of the resource.
        :type resource_uri: str
        :keyword start_time: The ISO 8601 conform Date start time from which to query for metric
         namespaces.
        :paramtype start_time: str
        :return: An iterator like instance of either MetricNamespaceCollection or the result of cls(response)
        :rtype: ~azure.core.paging.ItemPaged[~azure.monitor.query.MetricNamespaceCollection]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._namespace_op.list(resource_uri)

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.monitor.query.MetricsClient` session."""
        return self._client.close()

    def __enter__(self):
        # type: () -> MetricsClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
