# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for activity protocol tests.

Provides a tiny in-process ASGI test client (``asgi_client``) so the tests can
drive the Starlette ASGI app directly without depending on ``httpx``.
"""

import json as _json

import pytest


class _Headers:
    """Case-insensitive, read-only view of response headers."""

    def __init__(self, pairs):
        self._store = {key.lower(): value for key, value in pairs}

    def __getitem__(self, key):
        return self._store[key.lower()]

    def __contains__(self, key):
        return key.lower() in self._store

    def get(self, key, default=None):
        return self._store.get(key.lower(), default)


class _ASGIResponse:
    """Minimal response object exposing the surface the tests use."""

    def __init__(self, status_code, headers, body):
        self.status_code = status_code
        self.headers = _Headers(headers)
        self._body = body

    def json(self):
        return _json.loads(self._body.decode("utf-8"))

    @property
    def text(self):
        return self._body.decode("utf-8")


class _ASGIClient:
    """In-process ASGI client that invokes an app via ``scope``/``receive``/``send``.

    Mirrors the subset of the ``httpx.AsyncClient`` surface the tests rely on
    (``post`` / ``get`` returning an object with ``status_code`` / ``json()`` /
    ``headers``) without taking an ``httpx`` dependency.
    """

    def __init__(self, app):
        self._app = app

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc):
        return False

    async def post(self, url, *, json=None, headers=None):
        return await self._send("POST", url, json, headers)

    async def get(self, url, *, json=None, headers=None):
        return await self._send("GET", url, json, headers)

    async def _send(self, method, url, json_body, headers):
        path, _, query = url.partition("?")
        req_headers = dict(headers or {})
        if json_body is not None:
            body = _json.dumps(json_body).encode("utf-8")
            req_headers.setdefault("content-type", "application/json")
        else:
            body = b""

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("utf-8"),
            "query_string": query.encode("utf-8"),
            "root_path": "",
            "headers": [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in req_headers.items()],
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
        }

        request_sent = False

        async def receive():
            nonlocal request_sent
            if request_sent:
                return {"type": "http.disconnect"}
            request_sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        result = {"status": 500, "headers": []}
        body_chunks = []

        async def send(message):
            if message["type"] == "http.response.start":
                result["status"] = message["status"]
                result["headers"] = [(k.decode("latin-1"), v.decode("latin-1")) for k, v in message.get("headers", [])]
            elif message["type"] == "http.response.body":
                body_chunks.append(message.get("body", b""))

        await self._app(scope, receive, send)
        return _ASGIResponse(result["status"], result["headers"], b"".join(body_chunks))


@pytest.fixture
def asgi_client():
    """Return a factory that wraps an ASGI app in an in-process test client."""

    def _factory(app):
        return _ASGIClient(app)

    return _factory


# ---------------------------------------------------------------------------
# E2E tracing fixtures (used by test_tracing_e2e.py, selected via -m tracing_e2e)
# ---------------------------------------------------------------------------


@pytest.fixture()
def appinsights_connection_string():
    """Return APPLICATIONINSIGHTS_CONNECTION_STRING or skip the test."""
    import os

    cs = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not cs:
        pytest.skip("APPLICATIONINSIGHTS_CONNECTION_STRING not set")
    return cs


@pytest.fixture()
def appinsights_resource_id():
    """Return the App Insights resource ID provisioned by test-resources.bicep."""
    import os

    rid = os.environ.get("APPLICATIONINSIGHTS_RESOURCE_ID")
    if not rid:
        pytest.skip("APPLICATIONINSIGHTS_RESOURCE_ID not set")
    return rid


@pytest.fixture()
def logs_query_client():
    """Create a ``LogsQueryClient`` for querying Application Insights.

    In CI the pipeline runs inside ``AzurePowerShell@5`` — use
    ``AzurePowerShellCredential`` directly to get a token from the correct
    tenant. Locally fall back to ``DefaultAzureCredential``.
    """
    import os

    from azure.monitor.query import LogsQueryClient

    if os.environ.get("AZURESUBSCRIPTION_TENANT_ID"):
        from azure.identity import AzurePowerShellCredential

        credential = AzurePowerShellCredential(tenant_id=os.environ["AZURESUBSCRIPTION_TENANT_ID"])
    else:
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
    return LogsQueryClient(credential)


def pytest_configure(config):
    config.addinivalue_line("markers", "tracing_e2e: end-to-end tracing tests against live Application Insights")
