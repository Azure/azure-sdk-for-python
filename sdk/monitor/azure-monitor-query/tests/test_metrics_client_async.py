# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import timedelta
import sys
from unittest import mock

import pytest

from azure.monitor.query import MetricAggregationType, Metric
from azure.monitor.query.aio import MetricsQueryClient

from base_testcase import AzureMonitorQueryMetricsTestCase


METRIC_NAME = "requests/count"
METRIC_RESOURCE_PROVIDER = "Microsoft.Insights/components"


class TestMetricsClientAsync(AzureMonitorQueryMetricsTestCase):

    @pytest.mark.asyncio
    async def test_metrics_auth(self, recorded_test, monitor_info):
        client = self.get_client(
            MetricsQueryClient, self.get_credential(MetricsQueryClient, is_async=True))
        async with client:
            response = await client.query_resource(
                monitor_info['metrics_resource_id'],
                metric_names=[METRIC_NAME],
                timespan=timedelta(days=1),
                aggregations=[MetricAggregationType.COUNT]
                )
            assert response
            assert response.metrics

    @pytest.mark.asyncio
    async def test_metrics_granularity(self, recorded_test, monitor_info):
        client = self.get_client(
            MetricsQueryClient, self.get_credential(MetricsQueryClient, is_async=True))
        async with client:
            response = await client.query_resource(
                monitor_info['metrics_resource_id'],
                metric_names=[METRIC_NAME],
                timespan=timedelta(days=1),
                granularity=timedelta(minutes=5),
                aggregations=[MetricAggregationType.COUNT]
                )
            assert response
            assert response.granularity == timedelta(minutes=5)
            metric = response.metrics[METRIC_NAME]
            assert metric.timeseries
            for t in metric.timeseries:
                assert t.metadata_values is not None

    @pytest.mark.asyncio
    async def test_metrics_filter(self, recorded_test, monitor_info):
        client = self.get_client(
            MetricsQueryClient, self.get_credential(MetricsQueryClient, is_async=True))
        async with client:
            response = await client.query_resource(
                monitor_info['metrics_resource_id'],
                metric_names=[METRIC_NAME],
                timespan=timedelta(days=1),
                granularity=timedelta(minutes=5),
                filter="request/success eq '0'",
                aggregations=[MetricAggregationType.COUNT]
                )
            assert response
            metric = response.metrics[METRIC_NAME]
            for t in metric.timeseries:
                assert t.metadata_values is not None

    @pytest.mark.asyncio
    async def test_metrics_list(self, recorded_test, monitor_info):
        client = self.get_client(
            MetricsQueryClient, self.get_credential(MetricsQueryClient, is_async=True))
        async with client:
            response = await client.query_resource(
                monitor_info['metrics_resource_id'],
                metric_names=[METRIC_NAME],
                timespan=timedelta(days=1),
                granularity=timedelta(minutes=5),
                aggregations=[MetricAggregationType.COUNT]
                )
            assert response
            metrics = response.metrics
            assert len(metrics) == 1
            assert metrics[0].__class__ == Metric
            assert metrics[METRIC_NAME].__class__ == Metric
            assert metrics[METRIC_NAME] == metrics[0]

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.version_info < (3, 8), reason="async mocks work differently in Python <= 3.7")
    async def test_metrics_list_with_commas(self):
        """Commas in metric names should be encoded as %2."""

        with mock.patch("azure.monitor.query._generated.metrics.aio.operations.MetricsOperations.list") as mock_list:
            mock_list.return_value = {"foo": "bar"}
            client = self.get_client(
                MetricsQueryClient, self.get_credential(MetricsQueryClient, is_async=True))
            async with client:
                await client.query_resource(
                    "resource",
                    metric_names=["metric1,metric2", "foo,test,test"],
                    timespan=timedelta(days=1),
                    granularity=timedelta(minutes=5),
                    aggregations=[MetricAggregationType.COUNT]
                )

        assert "metricnames" in mock_list.call_args[1]
        assert mock_list.call_args[1]['metricnames'] == "metric1%2metric2,foo%2test%2test"

    @pytest.mark.asyncio
    async def test_metrics_namespaces(self, recorded_test, monitor_info):
        client = self.get_client(
            MetricsQueryClient, self.get_credential(MetricsQueryClient, is_async=True))

        async with client:
            response = client.list_metric_namespaces(monitor_info['metrics_resource_id'])

            assert response is not None
            async for item in response:
                assert item

    @pytest.mark.asyncio
    async def test_metrics_definitions(self, recorded_test, monitor_info):
        client = self.get_client(
            MetricsQueryClient, self.get_credential(MetricsQueryClient, is_async=True))

        async with client:
            response = client.list_metric_definitions(
                monitor_info['metrics_resource_id'], namespace=METRIC_RESOURCE_PROVIDER)

            assert response is not None
            async for item in response:
                assert item

    @pytest.mark.asyncio
    async def test_client_different_endpoint(self):
        credential = self.get_credential(MetricsQueryClient)
        endpoint = "https://management.chinacloudapi.cn"
        client = MetricsQueryClient(credential, endpoint=endpoint)

        assert client._endpoint == endpoint
        assert f"{endpoint}/.default" in client._client._config.authentication_policy._scopes
