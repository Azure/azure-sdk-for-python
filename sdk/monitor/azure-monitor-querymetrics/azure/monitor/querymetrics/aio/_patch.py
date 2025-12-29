# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from datetime import timedelta, datetime
from json import loads
from typing import Any, List, MutableMapping, Sequence, Optional, Union, Tuple, TYPE_CHECKING

import isodate
from azure.core.tracing.decorator_async import distributed_trace_async

from .._enums import MetricAggregationType
from .._models import MetricsQueryResult
from .._helpers import get_timespan_iso8601_endpoints, get_subscription_id_from_resource

from ._client import MetricsClient as GeneratedClient
from .._sdk_moniker import SDK_MONIKER

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


__all__: List[str] = ["MetricsClient"]  # Add all objects you want publicly available to users at this package level


JSON = MutableMapping[str, Any]


class MetricsClient(GeneratedClient):
    """MetricsClient should be used for performing metrics queries on multiple monitored resources in the
    same region. A credential with authorization at the subscription level is required when using this client.

    :param str endpoint: The regional endpoint to use, for example
        https://eastus.metrics.monitor.azure.com. The region should match the region of the requested
        resources. For global resources, the region should be 'global'. Required.
    :param credential: The credential to authenticate the client.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword audience: The audience to use when requesting tokens for Microsoft Entra ID. Defaults to the public
        cloud audience (https://metrics.monitor.azure.com).
    :paramtype audience: str
    :keyword api_version: The API version to use for this operation. Default value is "2024-02-01".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication_async.py
            :start-after: [START create_metrics_client_async]
            :end-before: [END create_metrics_client_async]
            :language: python
            :dedent: 4
            :caption: Creating the asynchronous MetricsClient with a credential.

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication_async.py
            :start-after: [START create_metrics_client_sovereign_cloud_async]
            :end-before: [END create_metrics_client_sovereign_cloud_async]
            :language: python
            :dedent: 4
            :caption: Creating the MetricsClient for use with a sovereign cloud (i.e. non-public cloud).
    """

    def __init__(self, endpoint: str, credential: "AsyncTokenCredential", **kwargs: Any) -> None:
        self._endpoint = endpoint
        if not self._endpoint.startswith("https://") and not self._endpoint.startswith("http://"):
            self._endpoint = "https://" + self._endpoint
        audience = kwargs.pop("audience", "https://metrics.monitor.azure.com")
        scope = audience.rstrip("/") + "/.default"
        credential_scopes = kwargs.pop("credential_scopes", [scope])

        kwargs.setdefault("sdk_moniker", SDK_MONIKER)
        super().__init__(endpoint=self._endpoint, credential=credential, credential_scopes=credential_scopes, **kwargs)

    @distributed_trace_async
    async def query_resources(
        self,
        *,
        resource_ids: Sequence[str],
        metric_namespace: str,
        metric_names: Sequence[str],
        timespan: Optional[Union[timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]]] = None,
        granularity: Optional[timedelta] = None,
        aggregations: Optional[Sequence[Union[MetricAggregationType, str]]] = None,
        max_results: Optional[int] = None,
        order_by: Optional[str] = None,
        filter: Optional[str] = None,
        roll_up_by: Optional[str] = None,
        **kwargs: Any,
    ) -> List[MetricsQueryResult]:
        """Lists the metric values for multiple resources.

        :keyword resource_ids: A list of resource IDs to query metrics for. Required.
        :paramtype resource_ids: list[str]
        :keyword metric_namespace: Metric namespace that contains the requested metric names. Required.
        :paramtype metric_namespace: str
        :keyword metric_names: The names of the metrics to retrieve. Required.
        :paramtype metric_names: list[str]
        :keyword timespan: The timespan for which to query the data. This can be a timedelta,
            a tuple of a start datetime with timedelta, or a tuple with start and end datetimes.
        :paramtype timespan: Optional[Union[~datetime.timedelta, tuple[~datetime.datetime, ~datetime.timedelta],
            tuple[~datetime.datetime, ~datetime.datetime]]]
        :keyword granularity: The granularity (i.e. timegrain) of the query.
        :paramtype granularity: Optional[~datetime.timedelta]
        :keyword aggregations: The list of aggregation types to retrieve. Use
            `azure.monitor.querymetrics.MetricAggregationType` enum to get each aggregation type.
        :paramtype aggregations: Optional[list[Union[~azure.monitor.querymetrics.MetricAggregationType, str]]]
        :keyword max_results: The maximum number of records to retrieve.
            Valid only if 'filter' is specified. Defaults to 10.
        :paramtype max_results: Optional[int]
        :keyword order_by: The aggregation to use for sorting results and the direction of the sort.
            Only one order can be specified. Examples: 'sum asc', 'maximum desc'.
        :paramtype order_by: Optional[str]
        :keyword filter: The **filter** is used to reduce the set of metric data returned. Default value is None.

            Example: Metric contains metadata A, B and C.

            - Return all time series of C where A = a1 and B = b1 or b2:

              **filter="A eq 'a1' and B eq 'b1' or B eq 'b2' and C eq '*'"**

            - Invalid variant:

              **filter="A eq 'a1' and B eq 'b1' and C eq '*' or B = 'b2'"**. This is invalid because the
              logical 'or' operator cannot separate two different metadata names.

            - Return all time series where A = a1, B = b1 and C = c1:

              **filter="A eq 'a1' and B eq 'b1' and C eq 'c1'"**

            - Return all time series where A = a1:

              **filter="A eq 'a1' and B eq '*' and C eq '*'"**

            - Special case: When dimension name or dimension value uses round brackets. Example: When dimension name
              is **dim (test) 1**, instead of using **filter="dim (test) 1 eq '*'"** use
              **filter="dim %2528test%2529 1 eq '*'"**.

              When dimension name is **dim (test) 3** and dimension value is
              **dim3 (test) val**, instead of using **filter="dim (test) 3 eq 'dim3 (test) val'"**, use **filter="dim
              %2528test%2529 3 eq 'dim3 %2528test%2529 val'"**.
        :paramtype filter: str
        :keyword roll_up_by: Dimension name(s) to rollup results by. For example if you only want to see
            metric values with a filter like 'City eq Seattle or City eq Tacoma' but don't want to see
            separate values for each city, you can specify 'City' to see the results for Seattle
            and Tacoma rolled up into one timeseries.
        :paramtype roll_up_by: str
        :return: A list of MetricsQueryResult objects.
        :rtype: list[~azure.monitor.querymetrics.MetricsQueryResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_metrics_query_async.py
                :start-after: [START send_metrics_batch_query_async]
                :end-before: [END send_metrics_batch_query_async]
                :language: python
                :caption: Get a response for a batch metrics query.
        """
        if not resource_ids:
            raise ValueError("'resource_ids' must be provided and must not be empty.")

        # Metric names with commas need to be encoded.
        metric_names = [x.replace(",", "%2") for x in metric_names]

        start_time, end_time = get_timespan_iso8601_endpoints(timespan)
        resource_id_json: JSON = {"resourceids": list(resource_ids)}
        subscription_id = get_subscription_id_from_resource(resource_ids[0])
        interval = isodate.duration_isoformat(granularity) if granularity else None

        generated = await self._query_resources(
            subscription_id=subscription_id,
            batch_request=resource_id_json,
            metric_namespace=metric_namespace,
            metric_names=metric_names,
            start_time=start_time,
            end_time=end_time,
            interval=interval,
            aggregation=",".join(aggregations) if aggregations else None,
            top=max_results,
            order_by=order_by,
            filter=filter,
            roll_up_by=roll_up_by,  # cspell:ignore rollupby
            **kwargs,
        )

        # In rare cases, the generated value is a JSON string instead of a dict. This potentially stems from a bug in
        # the service. This check handles that case.
        if isinstance(generated, str):
            generated = loads(generated)

        return [
            MetricsQueryResult._from_generated(value)  # pylint: disable=protected-access
            for value in generated["values"]
        ]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
