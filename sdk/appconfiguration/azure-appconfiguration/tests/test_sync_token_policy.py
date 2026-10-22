# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.pipeline.transport import HttpRequest, HttpResponse
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.appconfiguration._sync_token import SyncToken, SyncTokenPolicy


def test_parse_sync_token():
    test_sync_token = "jtqGc1I4=MDoyOA==;sn=28"
    sync_token = SyncToken.from_sync_token_string(test_sync_token)
    assert sync_token.token_id == "jtqGc1I4"
    assert sync_token.value == "MDoyOA=="
    assert sync_token.sequence_number == 28


def test_save_sync_token():
    test_sync_token = "jtqGc1I4=MDoyOA==;sn=28"
    header = {"Sync-Token": test_sync_token}
    request = HttpRequest("GET", "https://bing.com/")
    response = HttpResponse(request, None)
    response.headers = header
    pipeline_response = PipelineResponse(request, response, None)
    sync_token_policy = SyncTokenPolicy()
    sync_token_policy.on_response(None, pipeline_response)
    sync_token = sync_token_policy._sync_tokens["jtqGc1I4"]
    assert sync_token.token_id == "jtqGc1I4"
    assert sync_token.value == "MDoyOA=="
    assert sync_token.sequence_number == 28


def test_set_sync_token():
    test_sync_token = "jtqGc1I4=MDoyOA==;sn=28"
    header = {"Sync-Token": test_sync_token}
    request = HttpRequest("GET", "https://bing.com/")
    response = HttpResponse(request, None)
    response.headers = header
    pipeline_response = PipelineResponse(request, response, None)
    pipeline_request = PipelineRequest(request, None)
    sync_token_policy = SyncTokenPolicy()
    sync_token_policy.on_response(None, pipeline_response)
    sync_token_policy.on_request(pipeline_request)
    sync_token_header = pipeline_request.http_request.headers.get("Sync-Token")
    assert sync_token_header == "jtqGc1I4=MDoyOA=="


def test_save_multi_sync_token():
    test_sync_token = "syncToken1=val1;sn=6,syncToken2=val2;sn=10"
    header = {"Sync-Token": test_sync_token}
    request = HttpRequest("GET", "https://bing.com/")
    response = HttpResponse(request, None)
    response.headers = header
    pipeline_response = PipelineResponse(request, response, None)
    sync_token_policy = SyncTokenPolicy()
    sync_token_policy.on_response(None, pipeline_response)
    sync_token = sync_token_policy._sync_tokens["syncToken1"]
    assert sync_token.token_id == "syncToken1"
    assert sync_token.value == "val1"
    assert sync_token.sequence_number == 6
    sync_token = sync_token_policy._sync_tokens["syncToken2"]
    assert sync_token.token_id == "syncToken2"
    assert sync_token.value == "val2"
    assert sync_token.sequence_number == 10


def test_set_multi_sync_token():
    test_sync_token = "syncToken1=val1;sn=6,syncToken2=val2;sn=10"
    header = {"Sync-Token": test_sync_token}
    request = HttpRequest("GET", "https://bing.com/")
    response = HttpResponse(request, None)
    response.headers = header
    pipeline_response = PipelineResponse(request, response, None)
    pipeline_request = PipelineRequest(request, None)
    sync_token_policy = SyncTokenPolicy()
    sync_token_policy.on_response(None, pipeline_response)
    sync_token_policy.on_request(pipeline_request)
    sync_token_header = pipeline_request.http_request.headers.get("Sync-Token")
    assert "syncToken1=val1" in sync_token_header
    assert "syncToken2=val2" in sync_token_header


def test_update_cached_sync_token():
    test_sync_token = "syncToken1=val1;sn=6"
    header = {"Sync-Token": test_sync_token}
    request = HttpRequest("GET", "https://bing.com/")
    response = HttpResponse(request, None)
    response.headers = header
    pipeline_response = PipelineResponse(request, response, None)
    sync_token_policy = SyncTokenPolicy()
    sync_token_policy.on_response(None, pipeline_response)
    sync_token = sync_token_policy._sync_tokens["syncToken1"]
    assert sync_token.token_id == "syncToken1"
    assert sync_token.value == "val1"
    assert sync_token.sequence_number == 6
    test_new_sync_token = "syncToken1=val2;sn=10"
    header["Sync-Token"] = test_new_sync_token
    response.headers = header
    pipeline_response = PipelineResponse(request, response, None)
    sync_token_policy.on_response(None, pipeline_response)
    sync_token = sync_token_policy._sync_tokens["syncToken1"]
    assert sync_token.token_id == "syncToken1"
    assert sync_token.value == "val2"
    assert sync_token.sequence_number == 10
