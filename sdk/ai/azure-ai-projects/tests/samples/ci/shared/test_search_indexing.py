# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Offline tests of the Bicep-managed Search data-plane executor."""

import importlib.util
from io import BytesIO
import json
import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.core.pipeline.transport import RequestsTransport
from azure.identity._credentials import azure_cli
import pytest
from requests import Response, Session
from urllib3 import HTTPResponse

spec = importlib.util.spec_from_file_location("search_indexing", Path(__file__).parent / "infra" / "search-indexing.py")
indexing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(indexing)


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://sample.search.windows.net",
        "https://sample.search.windows.net.evil.invalid",
        "https://user@sample.search.windows.net",
        "https://sample.search.windows.net:8443",
        "https://sample.blob.core.windows.net",
        "https://sample.search.windows.net/path",
        "https://sample.search.windows.net?query=value",
        "https://untrusted.invalid\\.search.windows.net",
    ],
)
def test_invalid_endpoint_is_rejected_before_client_creation(endpoint, monkeypatch):
    client = Mock()
    monkeypatch.setattr(indexing, "SearchIndexClient", client)
    with pytest.raises(ValueError, match="token audience"):
        indexing.provision(
            {"searchEndpoint": endpoint, "storageEndpoint": "https://sample.blob.core.windows.net"}, Mock()
        )
    client.assert_not_called()


def wire_response(status, body=b""):
    response = Response()
    response.status_code = status
    response.headers.update(
        {"Content-Type": "application/json", "Retry-After": "10", "Location": "https://untrusted.invalid"}
    )
    response._content = body
    response._content_consumed = True
    response.raw = HTTPResponse(body=BytesIO(body))
    return response


@pytest.mark.parametrize("operation", ["upload", "create", "query"])
@pytest.mark.parametrize("status", [302, 401, 403, 429, 500, 503])
def test_sdk_retries_only_throttling(operation, status, monkeypatch):
    failure = wire_response(status, b'{"error":{"code":"Test","message":"sensitive-response"}}')
    success = {
        "upload": wire_response(201),
        "create": wire_response(201, b'{"name":"sample"}'),
        "query": wire_response(200, b'{"value":[{"chunk":"searchable"}]}'),
    }[operation]
    request = Mock(side_effect=[failure, success])
    sleep = Mock()
    monkeypatch.setattr(Session, "request", request)
    monkeypatch.setattr(RequestsTransport, "sleep", sleep)
    monkeypatch.setattr(indexing, "time", SimpleNamespace(monotonic=indexing.time.monotonic, sleep=sleep))
    credential = Mock(spec=["get_token"])
    credential.get_token.return_value = AccessToken("offline-token", 4_000_000_000)
    options = {**indexing.CLIENT_OPTIONS, "retry_policy": indexing.ThrottlingRetryPolicy()}
    if operation == "upload":
        client = indexing.BlobServiceClient(
            "https://unit.blob.core.windows.net", credential, retry_total=0, **indexing.CLIENT_OPTIONS
        )
    else:
        options["api_version"] = indexing.SEARCH_API_VERSION
        if operation == "create":
            client = indexing.SearchIndexClient("https://unit.search.windows.net", credential, **options)
        else:
            client = indexing.SearchClient("https://unit.search.windows.net", "sample", credential, **options)

    def run():
        if operation == "upload":
            indexing.upload_document(client.get_container_client("sample"), "doc.md", b"sample content")
            return
        if operation == "create":
            return client.create_or_update_index(indexing.SearchIndex({"name": "sample"}))
        return next(iter(client.search("*", top=1)))

    with client:
        if status == 429:
            run()
            assert request.call_count == 2
            if operation == "upload":
                assert [call.kwargs["data"] for call in request.call_args_list] == [b"sample content"] * 2
            sleep.assert_called_once_with(10)
        else:
            with pytest.raises(HttpResponseError) as error:
                run()
            assert error.value.status_code == status
            request.assert_called_once()
            sleep.assert_not_called()
    assert all(not call.kwargs["allow_redirects"] for call in request.call_args_list)


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (ClientAuthenticationError(message="sensitive-credential-detail"), "details suppressed"),
        (
            HttpResponseError(
                response=SimpleNamespace(status_code=403, reason="Forbidden"), message="sensitive-response"
            ),
            "HTTP 403",
        ),
    ],
)
def test_deployment_error_details_are_suppressed(error, message, monkeypatch):
    monkeypatch.setenv("SEARCH_INDEXING_CONFIGURATION", "{}")
    monkeypatch.setattr(indexing, "provision", Mock(side_effect=error))
    with pytest.raises(RuntimeError, match=message) as result:
        indexing.main()
    assert "sensitive-" not in str(result.value)
    assert result.value.__suppress_context__


def test_real_credential_failure_does_not_log_cli_details(monkeypatch, caplog, capsys):
    configuration = {
        "searchEndpoint": "https://unit.search.windows.net",
        "storageEndpoint": "https://unit.blob.core.windows.net",
        "containerName": "sample",
        "blobs": [{"name": "doc.md", "content": "content"}],
        "index": {"name": "sample"},
    }
    monkeypatch.setenv("SEARCH_INDEXING_CONFIGURATION", json.dumps(configuration))
    monkeypatch.setattr(
        azure_cli, "_run_command", Mock(side_effect=ClientAuthenticationError(message="sensitive-cli-diagnostic"))
    )
    loggers = [
        logging.getLogger("azure.identity._internal.decorators"),
        logging.getLogger("azure.identity._credentials.azure_cli"),
    ]
    initial_states = [logger.disabled for logger in loggers]
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(RuntimeError, match="details suppressed") as result:
            indexing.main()
    assert "sensitive-cli-diagnostic" not in str(result.value)
    assert "sensitive-cli-diagnostic" not in caplog.text
    assert "sensitive-cli-diagnostic" not in capsys.readouterr().err
    assert [logger.disabled for logger in loggers] == initial_states


def test_search_retries_more_than_three_throttling_responses(monkeypatch):
    request = Mock(side_effect=[wire_response(429) for _ in range(5)] + [wire_response(201, b'{"name":"sample"}')])
    sleep = Mock()
    monkeypatch.setattr(Session, "request", request)
    monkeypatch.setattr(RequestsTransport, "sleep", sleep)
    credential = Mock(spec=["get_token"])
    credential.get_token.return_value = AccessToken("offline-token", 4_000_000_000)
    with indexing.SearchIndexClient(
        "https://unit.search.windows.net",
        credential,
        **indexing.CLIENT_OPTIONS,
        retry_policy=indexing.ThrottlingRetryPolicy(),
        api_version=indexing.SEARCH_API_VERSION,
    ) as client:
        assert client.create_or_update_index(indexing.SearchIndex({"name": "sample"})).name == "sample"
    assert request.call_count == 6
    assert sleep.call_count == 5


def test_status_throttling_does_not_retry_past_readiness_deadline(monkeypatch):
    request = Mock(return_value=wire_response(429))
    sleep = Mock()
    monkeypatch.setattr(Session, "request", request)
    monkeypatch.setattr(RequestsTransport, "sleep", sleep)
    clock = Mock(side_effect=[0, 591, 591, 591])
    monkeypatch.setattr(indexing, "time", Mock(monotonic=clock))
    credential = Mock(spec=["get_token"])
    credential.get_token.return_value = AccessToken("offline-token", 4_000_000_000)
    with indexing.SearchIndexerClient(
        "https://unit.search.windows.net",
        credential,
        **indexing.CLIENT_OPTIONS,
        retry_policy=indexing.ThrottlingRetryPolicy(),
        api_version=indexing.SEARCH_API_VERSION,
    ) as client:
        with pytest.raises(HttpResponseError) as error:
            indexing.wait_for_indexer(client, "sample-indexer")
    assert error.value.status_code == 429
    request.assert_called_once()
    sleep.assert_not_called()
