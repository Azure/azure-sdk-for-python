import pytest
import os
from azure.identity import ClientSecretCredential
from azure.monitor.query import MetricsQueryClient

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
    # returns LogsQueryResults 
    response = client.query(os.environ['METRICS_RESOURCE_URI'], metric_names=["PublishSuccessCount"], timespan='P2D')

    assert response is not None
    assert response.metrics is not None

@pytest.mark.live_test_only
def test_metrics_namespaces():
    client = MetricsQueryClient(_credential())

    response = client.list_metric_namespaces(os.environ['METRICS_RESOURCE_URI'])

    assert response is not None

@pytest.mark.live_test_only
def test_metrics_definitions():
    client = MetricsQueryClient(_credential())

    response = client.list_metric_definitions(os.environ['METRICS_RESOURCE_URI'], metric_namespace='microsoft.eventgrid/topics')

    assert response is not None
