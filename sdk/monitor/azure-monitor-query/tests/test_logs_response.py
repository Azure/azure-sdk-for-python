from datetime import datetime
import pytest
import six
import os

from azure.identity import ClientSecretCredential
from azure.monitor.query import LogsQueryClient

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
    result = client.query_workspace(os.environ['LOG_WORKSPACE_ID'], query, timespan=None)
    assert isinstance(result.tables[0].rows[0][0], datetime) # TimeGenerated generated is a datetime
    assert isinstance(result.tables[0].rows[0][1], six.string_types) # _ResourceId generated is a string
    assert isinstance(result.tables[0].rows[0][2], bool) # Success generated is a bool
    assert isinstance(result.tables[0].rows[0][3], int) # ItemCount generated is a int
