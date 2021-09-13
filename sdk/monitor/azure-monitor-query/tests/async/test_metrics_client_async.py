from datetime import datetime, time, timedelta
import pytest
import os
from azure.identity.aio import ClientSecretCredential
from azure.monitor.query import MetricAggregationType
from azure.monitor.query.aio import MetricsQueryClient

def _credential():
    credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )
    return credential

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_metrics_auth():
    credential = _credential()
    client = MetricsQueryClient(credential)
    response = await client.query(
        os.environ['METRICS_RESOURCE_URI'],
        metric_names=["MatchedEventCount"],
        timespan=timedelta(days=1),
        aggregations=[MetricAggregationType.COUNT]
        )
    assert response
    assert response.metrics

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_metrics_granularity():
    credential = _credential()
    client = MetricsQueryClient(credential)
    response = await client.query(
        os.environ['METRICS_RESOURCE_URI'],
        metric_names=["MatchedEventCount"],
        timespan=timedelta(days=1),
        granularity=timedelta(minutes=5),
        aggregations=[MetricAggregationType.COUNT]
        )
    assert response
    assert response.granularity == timedelta(minutes=5)

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_metrics_namespaces():
    client = MetricsQueryClient(_credential())

    async with client:
        response = client.list_metric_namespaces(os.environ['METRICS_RESOURCE_URI'])

        assert response is not None

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_metrics_definitions():
    client = MetricsQueryClient(_credential())

    async with client:
        response = client.list_metric_definitions(os.environ['METRICS_RESOURCE_URI'], namespace='microsoft.eventgrid/topics')

        assert response is not None
