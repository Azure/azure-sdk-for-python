from datetime import datetime, time, timedelta
import pytest
import json
import os
from msrest.serialization import UTC

from azure.identity import ClientSecretCredential
from azure.core.exceptions import HttpResponseError
from azure.monitor.query import LogsQueryClient, LogsBatchQuery

from azure.monitor.query._helpers import construct_iso8601

def _credential():
    credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )
    return credential

@pytest.mark.live_test_only
def test_query_response_types():
    credential = _credential()
    client = LogsQueryClient(credential)
    query = """AppRequests |
    summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId, Success, ItemCount, DurationMs"""

    # returns LogsQueryResult 
    result = client.query(os.environ['LOG_WORKSPACE_ID'], query, timespan=None)
    assert result.tables[0].rows[0][0].__class__ == datetime # TimeGenerated generated is a datetime
    assert result.tables[0].rows[0][1].__class__ == str # _ResourceId generated is a string
    assert result.tables[0].rows[0][2].__class__ == bool # Success generated is a bool
    assert result.tables[0].rows[0][3].__class__ == int # ItemCount generated is a int
    assert result.tables[0].rows[0][4].__class__ == float # DurationMs generated is a real

