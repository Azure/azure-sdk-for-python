from datetime import datetime, timedelta
import pytest
import json
import os
from msrest.serialization import UTC

from azure.identity import ClientSecretCredential
from azure.core.exceptions import HttpResponseError
from azure.monitor.query import LogsQueryClient, LogsQueryRequest

from azure.monitor.query._helpers import construct_iso8601

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
    duration = timedelta(days=3)

    def callback(request):
        dic = json.loads(request.http_request.body)
        assert 'PT259200.0S/' in dic.get('timespan')

    client.query(os.environ['LOG_WORKSPACE_ID'], query, duration=duration, end_time=end_time, raw_request_hook=callback)

@pytest.mark.live_test_only
def test_query_duration_and_start_time():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = "AppRequests | take 5"

    end_time = datetime.now(UTC())
    start_time = end_time - timedelta(days=3)
    duration = timedelta(days=3)

    def callback(request):
        dic = json.loads(request.http_request.body)
        assert '/PT259200.0S' in dic.get('timespan')

    client.query(os.environ['LOG_WORKSPACE_ID'], query, duration=duration, start_time=start_time, raw_request_hook=callback)


@pytest.mark.live_test_only
def test_query_duration_only():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = "AppRequests | take 5"

    duration = timedelta(days=3)

    def callback(request):
        dic = json.loads(request.http_request.body)
        assert 'PT259200.0S' in dic.get('timespan')

    client.query(os.environ['LOG_WORKSPACE_ID'], query, duration=duration, raw_request_hook=callback)

def test_duration_to_iso8601():
    d1 = timedelta(days=1)
    d2 = timedelta(weeks=1)
    d3 = timedelta(weeks=3, days=4)
    d4 = timedelta(seconds=10)
    d5 = timedelta(microseconds=1000)
    d6 = timedelta(milliseconds=100000)
    d7 = timedelta(hours=24, days=1)

    assert construct_iso8601(duration=d1) == 'PT86400.0S'
    assert construct_iso8601(duration=d2) == 'PT604800.0S'
    assert construct_iso8601(duration=d3) == 'PT2160000.0S'
    assert construct_iso8601(duration=d4) == 'PT10.0S'
    assert construct_iso8601(duration=d5) == 'PT0.001S'
    assert construct_iso8601(duration=d5) == 'PT0.001S'
    assert construct_iso8601(duration=d7) == 'PT172800.0S'

    with pytest.raises(ValueError, match="End time must be provided along with duration or start time."):
        construct_iso8601(end=datetime.now(UTC()))

    with pytest.raises(ValueError, match="Start time must be provided along with duration or end time."):
        construct_iso8601(start=datetime.now(UTC()))

    with pytest.raises(ValueError, match="start_time can only be provided with duration or end_time, but not both."):
        construct_iso8601(end=datetime.now(UTC()), start=datetime(2020, 10, 10), duration=d3)
