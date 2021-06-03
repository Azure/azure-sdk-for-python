import pytest
import os
from azure.identity import ClientSecretCredential
from azure.core.exceptions import HttpResponseError
from azure.monitor.query import MetricsClient

def _credential():
    credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )
    return credential

async def test_metrics_auth():
    credential = _credential()
    client = MetricsClient(credential)
    # returns LogsQueryResults 
    response = await client.query(os.environ['METRICS_RESOURCE_URI'], metric_names=["PublishSuccessCount"], timespan='P2D')

    assert response is not None
    assert response.metrics is not None

async def test_metrics_namespaces():
    client = MetricsClient(_credential())

    response = await client.list_metric_namespaces(os.environ['METRICS_RESOURCE_URI'])

    assert response is not None

async def test_metrics_definitions():
    client = MetricsClient(_credential())

    response = await client.list_metric_definitions(os.environ['METRICS_RESOURCE_URI'], metric_namespace='microsoft.eventgrid/topics')

    assert response is not None
