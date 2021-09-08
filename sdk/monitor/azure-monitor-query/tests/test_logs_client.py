from datetime import timedelta
import pytest
import os
from azure.identity import ClientSecretCredential
from azure.core.exceptions import HttpResponseError
from azure.monitor.query import LogsQueryClient, LogsBatchQuery

def _credential():
    credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )
    return credential

@pytest.mark.live_test_only
def test_logs_single_query():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppRequests | 
    where TimeGenerated > ago(12h) | 
    summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

    # returns LogsQueryResult 
    response = client.query(os.environ['LOG_WORKSPACE_ID'], query, timespan=None)

    assert response is not None
    assert response.tables is not None

@pytest.mark.live_test_only
def test_logs_single_query_raises_no_timespan():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppRequests | 
    where TimeGenerated > ago(12h) | 
    summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

    # returns LogsQueryResult 
    with pytest.raises(TypeError):
        client.query(os.environ['LOG_WORKSPACE_ID'], query)

@pytest.mark.live_test_only
def test_logs_single_query_with_non_200():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppInsights | 
    where TimeGenerated > ago(12h)"""

    with pytest.raises(HttpResponseError) as e:
        client.query(os.environ['LOG_WORKSPACE_ID'], query, timespan=None)

    assert "SemanticError" in e.value.message

@pytest.mark.live_test_only
def test_logs_single_query_with_partial_success():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = "set truncationmaxrecords=1; union * | project TimeGenerated | take 10"

    response = client.query(os.environ['LOG_WORKSPACE_ID'], query, timespan=None)

    assert response is not None

@pytest.mark.skip("https://github.com/Azure/azure-sdk-for-python/issues/19917")
@pytest.mark.live_test_only
def test_logs_server_timeout():
    client = LogsQueryClient(_credential())

    with pytest.raises(HttpResponseError) as e:
        response = client.query(
            os.environ['LOG_WORKSPACE_ID'],
            "range x from 1 to 1000000000000000 step 1 | count",
            timespan=None,
            server_timeout=1,
        )
    assert 'Gateway timeout' in e.value.message

@pytest.mark.live_test_only
def test_logs_query_batch_default():
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
    response = client.query_batch(requests)

    assert len(response) == 3
    
    r0 = response[0]
    assert r0.tables[0].columns == ['count_']
    r1 = response[1]
    assert r1.tables[0].columns[0] == 'TimeGenerated'
    assert r1.tables[0].columns[1] == '_ResourceId'
    assert r1.tables[0].columns[2] == 'avgRequestDuration'
    r2 = response[2]
    assert r2.error is not None

@pytest.mark.live_test_only
def test_logs_single_query_with_statistics():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppRequests"""

    # returns LogsQueryResult 
    response = client.query(os.environ['LOG_WORKSPACE_ID'], query, timespan=None, include_statistics=True)

    assert response.statistics is not None

@pytest.mark.live_test_only
def test_logs_single_query_with_render():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppRequests"""

    # returns LogsQueryResult 
    response = client.query(os.environ['LOG_WORKSPACE_ID'], query, timespan=None, include_visualization=True)

    assert response.visualization is not None

@pytest.mark.live_test_only
def test_logs_single_query_with_render_and_stats():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppRequests"""

    # returns LogsQueryResult 
    response = client.query(os.environ['LOG_WORKSPACE_ID'], query, timespan=None, include_visualization=True, include_statistics=True)

    assert response.visualization is not None
    assert response.statistics is not None

@pytest.mark.live_test_only
def test_logs_query_batch_with_statistics_in_some():
    client = LogsQueryClient(_credential())

    requests = [
        LogsBatchQuery(
            query="AzureActivity | summarize count()",
            timespan=timedelta(hours=1),
            workspace_id= os.environ['LOG_WORKSPACE_ID']
        ),
        LogsBatchQuery(
            query= """AppRequests|
                summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId""",
            timespan=timedelta(hours=1),
            workspace_id= os.environ['LOG_WORKSPACE_ID'],
            include_statistics=True
        ),
        LogsBatchQuery(
            query= "AppRequests",
            workspace_id= os.environ['LOG_WORKSPACE_ID'],
            timespan=None,
            include_statistics=True
        ),
    ]
    response = client.query_batch(requests)

    assert len(response) == 3
    assert response[0].statistics is None
    assert response[2].statistics is not None

@pytest.mark.skip('https://github.com/Azure/azure-sdk-for-python/issues/19382')
@pytest.mark.live_test_only
def test_logs_single_query_additional_workspaces():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = "union * | where TimeGenerated > ago(100d) | project TenantId | summarize count() by TenantId"

    # returns LogsQueryResult 
    response = client.query(
        os.environ['LOG_WORKSPACE_ID'],
        query,
        timespan=None,
        additional_workspaces=[os.environ["SECONDARY_WORKSPACE_ID"]],
        )

    assert response is not None
    assert len(response.tables[0].rows) == 2

@pytest.mark.live_test_only
@pytest.mark.skip('https://github.com/Azure/azure-sdk-for-python/issues/19382')
def test_logs_query_batch_additional_workspaces():
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
    response = client.query_batch(requests)

    for resp in response:
        assert len(resp.tables[0].rows) == 2
