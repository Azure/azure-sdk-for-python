from datetime import timedelta
from time import time
import pytest
import os
from azure.identity.aio import ClientSecretCredential
from azure.core.exceptions import HttpResponseError
from azure.monitor.query import LogsBatchQuery, LogsQueryError, LogsTable, LogsQueryResult, LogsTableRow
from azure.monitor.query.aio import LogsQueryClient

def _credential():
    credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )
    return credential

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_auth():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppRequests | 
    where TimeGenerated > ago(12h) | 
    summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

    # returns LogsQueryResult 
    response = await client.query_workspace(os.environ['LOG_WORKSPACE_ID'], query, timespan=None)

    assert response is not None
    assert response.tables is not None

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_auth_no_timespan():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppRequests | 
    where TimeGenerated > ago(12h) | 
    summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

    # returns LogsQueryResult 
    with pytest.raises(TypeError):
        await client.query_workspace(os.environ['LOG_WORKSPACE_ID'], query)


@pytest.mark.skip("https://github.com/Azure/azure-sdk-for-python/issues/19917")
@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_server_timeout():
    client = LogsQueryClient(_credential())
    with pytest.raises(HttpResponseError) as e:
        response = await client.query_workspace(
            os.environ['LOG_WORKSPACE_ID'],
            "range x from 1 to 10000000000 step 1 | count",
            timespan=None,
            server_timeout=1,
        )
        assert e.message.contains('Gateway timeout')

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_query_batch_raises_on_no_timespan():
    with pytest.raises(TypeError):
        LogsBatchQuery(
                    query="AzureActivity | summarize count()",
                    workspace_id= os.environ['LOG_WORKSPACE_ID']
                )

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_query_batch_default():
    client = LogsQueryClient(_credential())

    requests = [
        LogsBatchQuery(
            query="AzureActivity | summarize count()",
            timespan=timedelta(hours=1),
            workspace_id= os.environ['LOG_WORKSPACE_ID']
        ),
        LogsBatchQuery(
            query= """AppRequests | take 10  |
                summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId""",
            timespan=timedelta(hours=1),
            workspace_id= os.environ['LOG_WORKSPACE_ID']
        ),
        LogsBatchQuery(
            query= "Wrong query | take 2",
            workspace_id= os.environ['LOG_WORKSPACE_ID'],
            timespan=None
        ),
    ]
    response = await client.query_batch(requests)

    assert len(response) == 3
    r0 = response[0]
    assert r0.tables[0].columns == ['count_']
    r1 = response[1]
    assert r1.tables[0].columns[0] == 'TimeGenerated'
    assert r1.tables[0].columns[1] == '_ResourceId'
    assert r1.tables[0].columns[2] == 'avgRequestDuration'
    r2 = response[2]
    assert r2.__class__ == LogsQueryError

@pytest.mark.skip('https://github.com/Azure/azure-sdk-for-python/issues/19382')
@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_single_query_additional_workspaces_async():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = "union * | where TimeGenerated > ago(100d) | project TenantId | summarize count() by TenantId"

    # returns LogsQueryResult 
    response = await client.query_workspace(
        os.environ['LOG_WORKSPACE_ID'],
        query,
        timespan=None,
        additional_workspaces=[os.environ["SECONDARY_WORKSPACE_ID"]],
        )

    assert response
    assert len(response.tables[0].rows) == 2

@pytest.mark.skip('https://github.com/Azure/azure-sdk-for-python/issues/19382')
@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_query_batch_additional_workspaces():
    client = LogsQueryClient(_credential())
    query = "union * | where TimeGenerated > ago(100d) | project TenantId | summarize count() by TenantId"

    requests = [
        LogsBatchQuery(
            query,
            timespan=timedelta(hours=1),
            workspace_id= os.environ['LOG_WORKSPACE_ID'],
            additional_workspaces=[os.environ['SECONDARY_WORKSPACE_ID']]
        ),
        LogsBatchQuery(
            query,
            timespan=timedelta(hours=1),
            workspace_id= os.environ['LOG_WORKSPACE_ID'],
            additional_workspaces=[os.environ['SECONDARY_WORKSPACE_ID']]
        ),
        LogsBatchQuery(
            query,
            workspace_id= os.environ['LOG_WORKSPACE_ID'],
            additional_workspaces=[os.environ['SECONDARY_WORKSPACE_ID']]
        ),
    ]
    response = await client.query_batch(requests)

    assert len(response) == 3

    for resp in response:
        assert len(resp.tables[0].rows) == 2

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_single_query_with_render():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppRequests | take 10"""

    # returns LogsQueryResult 
    response = await client.query_workspace(os.environ['LOG_WORKSPACE_ID'], query, timespan=None, include_visualization=True)

    assert response.visualization is not None

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_single_query_with_render_and_stats():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppRequests | take 10"""

    # returns LogsQueryResult 
    response = await client.query_workspace(os.environ['LOG_WORKSPACE_ID'], query, timespan=None, include_visualization=True, include_statistics=True)

    assert response.visualization is not None
    assert response.statistics is not None

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_query_result_iterate_over_tables():
    client = LogsQueryClient(_credential())

    query = "AppRequests | take 10; AppRequests | take 5"

    response = await client.query_workspace(
        os.environ['LOG_WORKSPACE_ID'],
        query,
        timespan=None,
        include_statistics=True,
        include_visualization=True
    )

    ## should iterate over tables
    for item in response:
        assert item.__class__ == LogsTable
    
    assert response.statistics is not None
    assert response.visualization is not None
    assert len(response.tables) == 2
    assert response.__class__ == LogsQueryResult

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_query_result_row_type():
    client = LogsQueryClient(_credential())

    query = "AppRequests | take 5"

    response = await client.query_workspace(
        os.environ['LOG_WORKSPACE_ID'],
        query,
        timespan=None,
    )

    ## should iterate over tables
    for table in response:
        assert table.__class__ == LogsTable

        for row in table.rows:
            assert row.__class__ == LogsTableRow
