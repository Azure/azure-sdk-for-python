# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import timedelta

import pytest

from azure.monitor.query import MetricAggregationType
from azure.monitor.query.aio import MetricsBatchQueryClient

from base_testcase import AzureMonitorQueryBatchMetricsTestCase


METRIC_NAME = "requests/count"
METRIC_RESOURCE_PROVIDER = "Microsoft.Insights/components"


class TestMetricsClientAsync(AzureMonitorQueryBatchMetricsTestCase):

    @pytest.mark.asyncio
    async def test_batch_metrics_auth(self, recorded_test, monitor_info):
        client = self.get_client(
            MetricsBatchQueryClient, self.get_credential(MetricsBatchQueryClient, is_async=True))
        async with client:
            responses = await client.query_batch(
                [monitor_info['metrics_resource_id']],
                METRIC_RESOURCE_PROVIDER,
                metric_names=[METRIC_NAME],
                aggregations=[MetricAggregationType.COUNT],
            )
            assert responses
            assert len(responses) == 1

    @pytest.mark.asyncio
    async def test_batch_metrics_granularity(self, recorded_test, monitor_info):
        client = self.get_client(
            MetricsBatchQueryClient, self.get_credential(MetricsBatchQueryClient, is_async=True))
        async with client:
            responses = await client.query_batch(
                [monitor_info['metrics_resource_id']],
                METRIC_RESOURCE_PROVIDER,
                metric_names=[METRIC_NAME],
                granularity=timedelta(minutes=5),
                aggregations=[MetricAggregationType.COUNT],
            )
            assert responses
            for response in responses:
                assert response.granularity == timedelta(minutes=5)
                metric = response.metrics[METRIC_NAME]
                assert metric.timeseries
                for t in metric.timeseries:
                    assert t.metadata_values is not None
