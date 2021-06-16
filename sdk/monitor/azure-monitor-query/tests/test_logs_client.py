import pytest
import os
from azure.identity import ClientSecretCredential
from azure.core.exceptions import HttpResponseError
from azure.monitor.query import LogsQueryClient, LogsQueryRequest

def _credential():
    credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )
    return credential

@pytest.mark.live_test_only
def test_logs_auth():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppRequests | 
    where TimeGenerated > ago(12h) | 
    summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

    # returns LogsQueryResults 
    response = client.query(os.environ['LOG_WORKSPACE_ID'], query)

    assert response is not None
    assert response.tables is not None

@pytest.mark.live_test_only
def test_logs_server_timeout():
    client = LogsQueryClient(_credential())

    with pytest.raises(HttpResponseError) as e:
        response = client.query(
            os.environ['LOG_WORKSPACE_ID'],
            "range x from 1 to 10000000000 step 1 | count",
            server_timeout=1,
        )
        assert e.message.contains('Gateway timeout')

@pytest.mark.live_test_only
def test_logs_batch_query():
    client = LogsQueryClient(_credential())

    requests = [
        LogsQueryRequest(
            query="AzureActivity | summarize count()",
            timespan="PT1H",
            workspace= os.environ['LOG_WORKSPACE_ID']
        ),
        LogsQueryRequest(
            query= """AppRequests | take 10  |
                summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId""",
            timespan="PT1H",
            workspace= os.environ['LOG_WORKSPACE_ID']
        ),
        LogsQueryRequest(
            query= "AppRequests | take 2",
            workspace= os.environ['LOG_WORKSPACE_ID']
        ),
    ]
    response = client.batch_query(requests)

    assert len(response.responses) == 3

