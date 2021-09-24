from datetime import timedelta, datetime
import pytest
import os
from azure.identity.aio import ClientSecretCredential
from azure.core.exceptions import HttpResponseError
from azure.monitor.query import LogsBatchQuery, LogsQueryError,LogsQueryResult, LogsQueryPartialResult
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
async def test_logs_single_query_fatal_exception():
    credential = _credential()
    client = LogsQueryClient(credential)
    with pytest.raises(HttpResponseError):
        await client.query_workspace('bad_workspace_id', 'AppRequests', timespan=None)

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_single_query_partial_exception_not_allowed():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """let Weight = 92233720368547758;
    range x from 1 to 3 step 1
    | summarize percentilesw(x, Weight * 100, 50)"""
    response = await client.query_workspace(os.environ['LOG_WORKSPACE_ID'], query, timespan=timedelta(days=1))
    assert response.__class__ == LogsQueryPartialResult
    assert response.partial_error is not None
    assert response.partial_error.code == 'PartialError'
    assert response.partial_error.__class__ == LogsQueryError

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_batch_query_fatal_exception():
    credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = 'bad_secret',
        tenant_id = os.environ['AZURE_TENANT_ID']
    )
    client = LogsQueryClient(credential)
    requests = [
        LogsBatchQuery(
            query="AzureActivity | summarize count()",
            timespan=timedelta(hours=1),
            workspace_id= os.environ['LOG_WORKSPACE_ID']
        ),
        LogsBatchQuery(
            query= """AppRequestsss | take 10""",
            timespan=(datetime(2021, 6, 2), timedelta(days=1)),
            workspace_id= os.environ['LOG_WORKSPACE_ID']
        ),
        LogsBatchQuery(
            query= """let Weight = 92233720368547758;
            range x from 1 to 3 step 1
            | summarize percentilesw(x, Weight * 100, 50)""",
            workspace_id= os.environ['LOG_WORKSPACE_ID'],
            timespan=(datetime(2021, 6, 2), datetime(2021, 6, 3)),
            include_statistics=True
        ),
    ]
    with pytest.raises(HttpResponseError):
        await client.query_batch(requests)

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_logs_batch_query_partial_exception_not_allowed():
    credential = _credential()
    client = LogsQueryClient(credential)
    requests = [
        LogsBatchQuery(
            query="AzureActivity | summarize count()",
            timespan=timedelta(hours=1),
            workspace_id= os.environ['LOG_WORKSPACE_ID']
        ),
        LogsBatchQuery(
            query= """bad query | take 10""",
            timespan=(datetime(2021, 6, 2), timedelta(days=1)),
            workspace_id= os.environ['LOG_WORKSPACE_ID']
        ),
        LogsBatchQuery(
            query= """let Weight = 92233720368547758;
            range x from 1 to 3 step 1
            | summarize percentilesw(x, Weight * 100, 50)""",
            workspace_id= os.environ['LOG_WORKSPACE_ID'],
            timespan=(datetime(2021, 6, 2), datetime(2021, 6, 3)),
            include_statistics=True
        ),
    ]
    responses = await client.query_batch(requests)
    r1, r2, r3 = responses[0], responses[1], responses[2]
    assert r1.__class__ == LogsQueryResult
    assert r2.__class__ == LogsQueryError
    assert r3.__class__ == LogsQueryPartialResult
