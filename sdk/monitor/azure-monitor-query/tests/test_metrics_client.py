import pytest
import os
from datetime import datetime, timedelta
from azure.identity import ClientSecretCredential
from azure.monitor.query import MetricsQueryClient, MetricAggregationType, Metric

def _credential():
    credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )
    return credential

@pytest.mark.live_test_only
def test_metrics_auth():
    credential = _credential()
    client = MetricsQueryClient(credential)
    response = client.query_resource(
        os.environ['METRICS_RESOURCE_URI'],
        metric_names=["MatchedEventCount"],
        timespan=timedelta(days=1),
        aggregations=[MetricAggregationType.COUNT]
        )
    assert response
    assert response.metrics

@pytest.mark.live_test_only
def test_metrics_granularity():
    credential = _credential()
    client = MetricsQueryClient(credential)
    response = client.query_resource(
        os.environ['METRICS_RESOURCE_URI'],
        metric_names=["MatchedEventCount"],
        timespan=timedelta(days=1),
        granularity=timedelta(minutes=5),
        aggregations=[MetricAggregationType.COUNT]
        )
    assert response
    assert response.granularity == timedelta(minutes=5)

@pytest.mark.live_test_only
def test_metrics_filter():
    credential = _credential()
    client = MetricsQueryClient(credential)
    response = client.query_resource(
        os.environ['METRICS_RESOURCE_URI'],
        metric_names=["MatchedEventCount"],
        timespan=timedelta(days=1),
        granularity=timedelta(minutes=5),
        filter="EventSubscriptionName eq '*'",
        aggregations=[MetricAggregationType.COUNT]
        )
    assert response
    metric = response.metrics['MatchedEventCount']
    for t in metric.timeseries:
        assert t.metadata_values is not None

@pytest.mark.live_test_only
def test_metrics_list():
    credential = _credential()
    client = MetricsQueryClient(credential)
    response = client.query_resource(
        os.environ['METRICS_RESOURCE_URI'],
        metric_names=["MatchedEventCount"],
        timespan=timedelta(days=1),
        granularity=timedelta(minutes=5),
        aggregations=[MetricAggregationType.COUNT]
        )
    assert response
    metrics = response.metrics
    assert len(metrics) == 1
    assert metrics[0].__class__ == Metric
    assert metrics['MatchedEventCount'].__class__ == Metric
    assert metrics['MatchedEventCount'] == metrics[0]

@pytest.mark.live_test_only
def test_metrics_namespaces():
    client = MetricsQueryClient(_credential())

    response = client.list_metric_namespaces(os.environ['METRICS_RESOURCE_URI'])

    assert response is not None

@pytest.mark.live_test_only
def test_metrics_definitions():
    client = MetricsQueryClient(_credential())

    response = client.list_metric_definitions(os.environ['METRICS_RESOURCE_URI'], namespace='microsoft.eventgrid/topics')

    assert response is not None
