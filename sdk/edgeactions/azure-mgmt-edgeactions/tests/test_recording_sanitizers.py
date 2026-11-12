# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from unittest.mock import Mock, patch
from urllib.parse import parse_qsl, urlsplit

import pytest
import requests
from devtools_testutils.config import PROXY_URL
from devtools_testutils.helpers import is_live

from edgeactions_test_settings import POLLING_QUERY_SECRET_REGEX, TRACE_HEADERS


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "?t=123&c=encoded%26value&s=signature%3D&h=hash",
            "?t=Sanitized&c=Sanitized&s=Sanitized&h=Sanitized",
        ),
        (
            "?api-version=2026-10-01&C=opaque#fragment",
            "?api-version=2026-10-01&C=Sanitized#fragment",
        ),
        (
            "?count=2&st=unchanged&c=&other=value",
            "?count=2&st=unchanged&c=&other=value",
        ),
        (
            '{"url":"https://example.test/operations/one?c=opaque"}',
            '{"url":"https://example.test/operations/one?c=Sanitized"}',
        ),
    ],
)
def test_polling_query_redaction_preserves_non_secret_fields(value, expected):
    assert re.sub(POLLING_QUERY_SECRET_REGEX, "Sanitized", value) == expected


def test_identity_sanitizers_use_literal_nonempty_values(monkeypatch, sanitizer_configuration):
    for name in (
        "AZURE_SUBSCRIPTION_ID",
        "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("AZURE_CLIENT_ID", "")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "fake.secret+[regex]")
    mocks = {
        name: Mock()
        for name in (
            "add_body_key_sanitizer",
            "add_general_regex_sanitizer",
            "add_general_string_sanitizer",
            "add_header_regex_sanitizer",
            "remove_batch_sanitizers",
        )
    }

    with patch.dict(sanitizer_configuration.__globals__, mocks):
        sanitizer_configuration()

    mocks["add_general_string_sanitizer"].assert_called_once_with(
        target="fake.secret+[regex]", value="00000000-0000-0000-0000-000000000000"
    )
    mocks["add_general_regex_sanitizer"].assert_called_once_with(regex=POLLING_QUERY_SECRET_REGEX, value="Sanitized")
    mocks["remove_batch_sanitizers"].assert_called_once_with(["AZSDK2003", "AZSDK3430", "AZSDK3493"])


@pytest.fixture
def local_upstream():
    class Handler(BaseHTTPRequestHandler):
        calls = 0

        def do_GET(self):
            Handler.calls += 1
            polling_url = (
                f"http://127.0.0.1:{self.server.server_port}/operations/one"
                "?api-version=2026-10-01&t=fake-time&c=fake-context&s=fake-signature&h=fake-hash"
            )
            body = json.dumps(
                {
                    "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test-rg/"
                    "providers/Microsoft.Cdn/edgeActions/test-action",
                    "name": "test-action",
                    "sku": {"name": "Standard"},
                    "pollingUrl": polling_url,
                    "access_token": "fake-access-token",
                    "refresh_token": "fake-refresh-token",
                    "id_token": "fake-id-token",
                    "systemData": {
                        "createdBy": "fake-creator",
                        "lastModifiedBy": "fake-modifier",
                    },
                }
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            for header in ("Location", "Azure-AsyncOperation", "operation-location"):
                self.send_header(header, polling_url)
            for header in TRACE_HEADERS:
                self.send_header(header, "fake-trace-value")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    with HTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = Thread(target=server.serve_forever)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}", Handler
        finally:
            server.shutdown()
            thread.join()


@pytest.mark.usefixtures("add_sanitizers")
@pytest.mark.skipif(
    is_live(),
    reason="Local proxy sanitizer regression runs only in playback/offline mode.",
)
@pytest.mark.parametrize(
    "use_recorded_polling_url",
    [False, True],
    ids=["changed-values", "sanitized-polling-url"],
)
def test_proxy_redacts_tokens_without_erasing_polling_urls(tmp_path, local_upstream, use_recorded_polling_url):
    upstream_url, handler = local_upstream
    recording_path = tmp_path / "sanitizer-recording.json"
    query = "?api-version=2026-10-01&t=fake-time&c=fake-context&s=fake-signature&h=fake-hash"
    start = requests.post(
        f"{PROXY_URL()}/record/start",
        json={"x-recording-file": str(recording_path)},
        timeout=30,
    )
    start.raise_for_status()
    recording_id = start.headers["x-recording-id"]
    try:
        response = requests.get(
            f"{PROXY_URL()}/operations/one{query}",
            headers={
                "x-recording-id": recording_id,
                "x-recording-mode": "record",
                "x-recording-upstream-base-uri": upstream_url,
            },
            timeout=30,
        )
        response.raise_for_status()
    finally:
        stop = requests.post(
            f"{PROXY_URL()}/record/stop",
            headers={"x-recording-id": recording_id, "x-recording-save": "true"},
            json={},
            timeout=30,
        )
        stop.raise_for_status()

    text = recording_path.read_text(encoding="utf-8-sig")
    assert "fake-" not in text
    entry = json.loads(text)["Entries"][0]
    body = entry["ResponseBody"]
    assert body["name"] == "test-action"
    assert body["sku"]["name"] == "Standard"
    assert body["id"].endswith("/edgeActions/test-action")
    response_headers = {key.lower(): value for key, value in entry["ResponseHeaders"].items()}
    urls = [entry["RequestUri"], body["pollingUrl"]]
    for header in ("location", "azure-asyncoperation", "operation-location"):
        value = response_headers[header]
        urls.append(value[0] if isinstance(value, list) else value)
    for url in urls:
        assert urlsplit(url).path == "/operations/one"
        assert dict(parse_qsl(urlsplit(url).query)) == {
            "api-version": "2026-10-01",
            "t": "Sanitized",
            "c": "Sanitized",
            "s": "Sanitized",
            "h": "Sanitized",
        }

    start = requests.post(
        f"{PROXY_URL()}/playback/start",
        json={"x-recording-file": str(recording_path)},
        timeout=30,
    )
    start.raise_for_status()
    recording_id = start.headers["x-recording-id"]
    try:
        if use_recorded_polling_url:
            polling_url = response_headers["azure-asyncoperation"]
            polling_url = polling_url[0] if isinstance(polling_url, list) else polling_url
            playback_query = "?" + urlsplit(polling_url).query
        else:
            playback_query = query.replace("fake-", "different-")
        response = requests.get(
            f"{PROXY_URL()}/operations/one{playback_query}",
            headers={
                "x-recording-id": recording_id,
                "x-recording-mode": "playback",
                "x-recording-upstream-base-uri": upstream_url,
            },
            timeout=30,
        )
        response.raise_for_status()
        assert response.json()["name"] == "test-action"
        assert handler.calls == 1
    finally:
        stop = requests.post(
            f"{PROXY_URL()}/playback/stop",
            headers={"x-recording-id": recording_id},
            timeout=30,
        )
        stop.raise_for_status()
