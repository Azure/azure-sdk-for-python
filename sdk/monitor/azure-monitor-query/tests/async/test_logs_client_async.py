import pytest
import os
from azure.identity.aio import ClientSecretCredential
from azure.core.exceptions import HttpResponseError
from azure.monitor.query import LogsQueryRequest
from azure.monitor.query.aio import LogsQueryClient

def _credential():
    credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )
    return credential

@pytest.mark.live_test_only
async def test_logs_auth():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppRequests | 
    where TimeGenerated > ago(12h) | 
    summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

    # returns LogsQueryResults 
    response = await client.query(os.environ['LOG_WORKSPACE_ID'], query)

    assert response is not None
    assert response.tables is not None

@pytest.mark.live_test_only
async def test_logs_server_timeout():
    client = LogsQueryClient(_credential())

    with pytest.raises(HttpResponseError) as e:
        response = await client.query(
            os.environ['LOG_WORKSPACE_ID'],
            "range x from 1 to 10000000000 step 1 | count",
            server_timeout=1,
        )
        assert e.message.contains('Gateway timeout')

@pytest.mark.live_test_only
async def test_logs_batch_query():
    client = LogsQueryClient(_credential())

    requests = [
        LogsQueryRequest(
            query="AzureActivity | summarize count()",
            timespan="PT1H",
            workspace_id= os.environ['LOG_WORKSPACE_ID']
        ),
        LogsQueryRequest(
            query= """AppRequests | take 10  |
                summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId""",
            timespan="PT1H",
            workspace_id= os.environ['LOG_WORKSPACE_ID']
        ),
        LogsQueryRequest(
            query= "AppRequests | take 2",
            workspace_id= os.environ['LOG_WORKSPACE_ID']
        ),
    ]
    response = await client.batch_query(requests)

    assert len(response.responses) == 3

@pytest.mark.skip('https://github.com/Azure/azure-sdk-for-python/issues/19382')
@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_single_query_additional_workspaces_async():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = "union * | where TimeGenerated > ago(100d) | project TenantId | summarize count() by TenantId"

    # returns LogsQueryResults 
    response = await client.query(
        os.environ['LOG_WORKSPACE_ID'],
        query,
        additional_workspaces=[os.environ["SECONDARY_WORKSPACE_ID"]],
        )

    assert response
    assert len(response.tables[0].rows) == 2

@pytest.mark.skip('https://github.com/Azure/azure-sdk-for-python/issues/19382')
@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_batch_query_additional_workspaces():
    client = LogsQueryClient(_credential())
    query = "union * | where TimeGenerated > ago(100d) | project TenantId | summarize count() by TenantId"

    requests = [
        LogsQueryRequest(
            query,
            timespan="PT1H",
            workspace_id= os.environ['LOG_WORKSPACE_ID'],
            additional_workspaces=[os.environ['SECONDARY_WORKSPACE_ID']]
        ),
        LogsQueryRequest(
            query,
            timespan="PT1H",
            workspace_id= os.environ['LOG_WORKSPACE_ID'],
            additional_workspaces=[os.environ['SECONDARY_WORKSPACE_ID']]
        ),
        LogsQueryRequest(
            query,
            workspace_id= os.environ['LOG_WORKSPACE_ID'],
            additional_workspaces=[os.environ['SECONDARY_WORKSPACE_ID']]
        ),
    ]
    response = await client.batch_query(requests)

    assert len(response.responses) == 3

    for resp in response.responses:
        assert len(resp.body.tables[0].rows) == 2
