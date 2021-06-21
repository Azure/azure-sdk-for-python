from datetime import datetime, time, timedelta
import pytest
import json
import os
from msrest.serialization import UTC

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
def test_query_no_duration():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppRequests | 
    where TimeGenerated > ago(12h) | 
    summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

    def callback(request):
        dic = json.loads(request.http_request.body)
        assert dic.get('timespan') is None
    # returns LogsQueryResults 
    client.query(os.environ['LOG_WORKSPACE_ID'], query)

@pytest.mark.live_test_only
def test_query_start_and_end_time():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = "AppRequests | take 5"

    end_time = datetime.now(UTC())
    start_time = end_time - timedelta(days=3)

    def callback(request):
        dic = json.loads(request.http_request.body)
        assert dic.get('timespan') is not None

    client.query(os.environ['LOG_WORKSPACE_ID'], query, start_time=start_time, end_time=end_time, raw_request_hook=callback)

@pytest.mark.live_test_only
def test_query_duration_and_end_time():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = "AppRequests | take 5"

    end_time = datetime.now(UTC())
    duration = 'P3D'

    def callback(request):
        dic = json.loads(request.http_request.body)
        assert 'P3D/' in dic.get('timespan')

    client.query(os.environ['LOG_WORKSPACE_ID'], query, duration=duration, end_time=end_time, raw_request_hook=callback)

@pytest.mark.live_test_only
def test_query_duration_and_start_time():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = "AppRequests | take 5"

    end_time = datetime.now(UTC())
    start_time = end_time - timedelta(days=3)
    duration = 'P3D'

    def callback(request):
        dic = json.loads(request.http_request.body)
        assert '/P3D' in dic.get('timespan')

    client.query(os.environ['LOG_WORKSPACE_ID'], query, duration=duration, start_time=start_time, raw_request_hook=callback)


@pytest.mark.live_test_only
def test_query_duration_only():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = "AppRequests | take 5"

    duration = 'P3D'

    def callback(request):
        dic = json.loads(request.http_request.body)
        assert 'P3D' in dic.get('timespan')

    client.query(os.environ['LOG_WORKSPACE_ID'], query, duration=duration, raw_request_hook=callback)
