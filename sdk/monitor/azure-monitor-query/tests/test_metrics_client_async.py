# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import timedelta

import pytest

from azure.monitor.query import MetricAggregationType
from azure.monitor.query.aio import MetricsClient

from base_testcase import MetricsClientTestCase


METRIC_NAME = "requests/count"
METRIC_RESOURCE_PROVIDER = "Microsoft.Insights/components"


class TestMetricsClientAsync(MetricsClientTestCase):

    @pytest.mark.asyncio
    async def test_batch_metrics_auth(self, recorded_test, monitor_info):
        client: MetricsClient = self.get_client(
            MetricsClient, self.get_credential(MetricsClient, is_async=True))
        async with client:
            responses = await client.query_resources(
                resource_ids=[monitor_info['metrics_resource_id']],
                metric_namespace=METRIC_RESOURCE_PROVIDER,
                metric_names=[METRIC_NAME],
                aggregations=[MetricAggregationType.COUNT],
            )
            assert responses
            assert len(responses) == 1

    @pytest.mark.asyncio
    async def test_batch_metrics_granularity(self, recorded_test, monitor_info):
        client: MetricsClient = self.get_client(
            MetricsClient, self.get_credential(MetricsClient, is_async=True))
        async with client:
            responses = await client.query_resources(
                resource_ids=[monitor_info['metrics_resource_id']],
                metric_namespace=METRIC_RESOURCE_PROVIDER,
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

    @pytest.mark.asyncio
    async def test_client_different_endpoint(self):
        credential = self.get_credential(MetricsClient, is_async=True)
        endpoint = "https://usgovvirginia.metrics.monitor.azure.us"
        audience = "https://metrics.monitor.azure.us"
        client = MetricsClient(endpoint, credential, audience=audience)

        assert client._endpoint == endpoint
        assert f"{audience}/.default" in client._client._config.authentication_policy._scopes
