"""Tests for the direct-path header contract and the insecure-HTTP guard.

Istio authenticates the direct caller. ``loom_api`` derives the customer context
from headers that APIM injects on the project route and the command job supplies
on the direct route. See ``docs/command-job-direct-loom-api-design.md``.
"""

import asyncio

import pytest

from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline import policies
from azure.ai.finetuningsessions import FineTuningSessionClient
from azure.ai.finetuningsessions import _patch as p
from azure.ai.finetuningsessions._client_options import _is_local_endpoint
from azure.ai.finetuningsessions.aio import FineTuningSessionClient as AsyncFineTuningSessionClient

# Every env var _base_headers consults, cleared before each test so a real
# developer environment cannot leak into assertions.
_ALL_ENV_VARS = (
    "X_COGNITIVE_SUBSCRIPTION_ID",
    "COGNITIVE_SUBSCRIPTION_ID",
    "AZURE_SUBSCRIPTION_ID",
    "LOOM_AZURE_RESOURCE_ID",
    "LOOM_AZURE_RESOURCE_TENANT_ID",
    "LOOM_AZURE_RESOURCE_LOCATION",
    "LOOM_WORKSPACE_RESOURCE_ID",
)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for name in _ALL_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


class _FakeCredential:
    """Minimal TokenCredential stand-in; never invoked in these tests."""

    def get_token(self, *scopes, **kwargs):  # pragma: no cover - not called
        raise AssertionError("get_token should not be called")


class _FakeAsyncCredential:
    async def get_token(self, *scopes, **kwargs):  # pragma: no cover - not called
        raise AssertionError("get_token should not be called")


# ── _base_headers ──────────────────────────────────────────────────────────────


def test_no_identity_headers_when_env_is_empty():
    """APIM path: nothing injected client-side, so only the constants are sent."""
    headers = p._base_headers()

    assert headers["Accept"] == "application/json"
    assert "Foundry-Features" in headers
    for absent in (
        "apim-subscription-id",
        "azure-resource-id",
        "azure-resource-tenant-id",
        "azure-resource-location",
        "X-Workspace-Resource-Id",
        "apim-request-id",
    ):
        assert absent not in headers


@pytest.mark.parametrize(
    "env_var",
    ["X_COGNITIVE_SUBSCRIPTION_ID", "COGNITIVE_SUBSCRIPTION_ID", "AZURE_SUBSCRIPTION_ID"],
)
def test_subscription_id_read_from_each_supported_var(monkeypatch, env_var):
    monkeypatch.setenv(env_var, "sub-from-" + env_var)

    assert p._base_headers()["apim-subscription-id"] == "sub-from-" + env_var


def test_subscription_id_precedence_is_x_cognitive_first(monkeypatch):
    monkeypatch.setenv("X_COGNITIVE_SUBSCRIPTION_ID", "winner")
    monkeypatch.setenv("COGNITIVE_SUBSCRIPTION_ID", "loser")
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "loser-too")

    assert p._base_headers()["apim-subscription-id"] == "winner"


def test_direct_path_forwards_customer_context_headers(monkeypatch):
    monkeypatch.setenv("X_COGNITIVE_SUBSCRIPTION_ID", "cog-sub")
    monkeypatch.setenv("LOOM_AZURE_RESOURCE_ID", "/subscriptions/s/resourceGroups/rg")
    monkeypatch.setenv("LOOM_AZURE_RESOURCE_TENANT_ID", "tenant-abc")
    monkeypatch.setenv("LOOM_AZURE_RESOURCE_LOCATION", "eastus2")
    monkeypatch.setenv("LOOM_WORKSPACE_RESOURCE_ID", "/subscriptions/s/.../workspaces/ws")

    headers = p._base_headers()

    assert headers["apim-subscription-id"] == "cog-sub"
    assert headers["azure-resource-id"] == "/subscriptions/s/resourceGroups/rg"
    assert headers["azure-resource-tenant-id"] == "tenant-abc"
    assert headers["azure-resource-location"] == "eastus2"
    assert headers["X-Workspace-Resource-Id"] == "/subscriptions/s/.../workspaces/ws"
    assert "apim-request-id" not in headers


def test_header_env_table_covers_direct_customer_context_mapping():
    """Guard against drift in the environment-backed context header table."""
    mapped = {header for header, _ in p._DIRECT_PATH_HEADER_ENV}

    assert mapped == {
        "azure-resource-id",
        "azure-resource-tenant-id",
        "azure-resource-location",
        "X-Workspace-Resource-Id",
    }


def test_empty_string_env_var_is_not_sent(monkeypatch):
    """Unset job YAML fields arrive as '' -- an empty header is worse than none."""
    monkeypatch.setenv("LOOM_AZURE_RESOURCE_ID", "")
    monkeypatch.setenv("LOOM_AZURE_RESOURCE_LOCATION", "")

    headers = p._base_headers()

    assert "azure-resource-id" not in headers
    assert "azure-resource-location" not in headers


def test_extra_headers_merge_and_override(monkeypatch):
    monkeypatch.setenv("LOOM_AZURE_RESOURCE_LOCATION", "from-env")

    headers = p._base_headers({"Content-Type": "application/json", "azure-resource-location": "explicit"})

    assert headers["Content-Type"] == "application/json"
    assert headers["azure-resource-location"] == "explicit"


# ── allow_insecure_http guard ──────────────────────────────────────────────────


def _client_config(client_class, **kwargs):
    """Exercise public constructor guards without opening the transports."""
    client = client_class(**kwargs)
    try:
        return client._config
    finally:
        if isinstance(client, AsyncFineTuningSessionClient):
            asyncio.run(client.close())
        else:
            try:
                client.close()
            finally:
                client._session_client.close()


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://localhost:8080",
        "http://127.0.0.1:8080/api",
        "http://[::1]:8080",
        "http://LOCALHOST:9000",
    ],
)
def test_is_local_endpoint_accepts_loopback(endpoint):
    assert _is_local_endpoint(endpoint) is True


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://loom-api-eastus2.internal.example.com",
        "https://acct.services.ai.azure.com/api/projects/p",
        "http://169.254.169.254",
        "http://localhost.evil.example.com",
    ],
)
def test_is_local_endpoint_rejects_remote(endpoint):
    assert _is_local_endpoint(endpoint) is False


def test_insecure_http_rejected_against_remote_plaintext_endpoint():
    """Downgrading TLS on the direct path would leak identity headers + token."""
    with pytest.raises(ValueError, match="only supported for local endpoints"):
        _client_config(
            FineTuningSessionClient,
            endpoint="http://loom-api-eastus2.internal.example.com",
            credential=_FakeCredential(),
            allow_insecure_http=True,
        )


def test_insecure_http_flag_remains_compatible_with_https_endpoint():
    config = _client_config(
        FineTuningSessionClient,
        endpoint="https://loom-api-eastus2.internal.example.com",
        credential=_FakeCredential(),
        allow_insecure_http=True,
    )

    assert config.allow_insecure_http is True
    assert type(config.authentication_policy) is policies.BearerTokenCredentialPolicy


def test_insecure_http_flag_remains_compatible_with_remote_api_key_endpoint():
    config = _client_config(
        FineTuningSessionClient,
        endpoint="http://legacy-dev.example.com",
        credential=AzureKeyCredential("test-key"),
        allow_insecure_http=True,
    )

    assert config.allow_insecure_http is True


def test_insecure_http_allowed_against_localhost():
    config = _client_config(
        FineTuningSessionClient,
        endpoint="http://localhost:8080",
        credential=_FakeCredential(),
        allow_insecure_http=True,
    )

    assert config.allow_insecure_http is True


def test_async_insecure_http_rejected_against_remote_plaintext_endpoint():
    with pytest.raises(ValueError, match="only supported for local endpoints"):
        _client_config(
            AsyncFineTuningSessionClient,
            endpoint="http://loom-api-eastus2.internal.example.com",
            credential=_FakeAsyncCredential(),
            allow_insecure_http=True,
        )


def test_async_insecure_http_flag_remains_compatible_with_https_endpoint():
    config = _client_config(
        AsyncFineTuningSessionClient,
        endpoint="https://loom-api-eastus2.internal.example.com",
        credential=_FakeAsyncCredential(),
        allow_insecure_http=True,
    )

    assert config.allow_insecure_http is True
    assert type(config.authentication_policy) is policies.AsyncBearerTokenCredentialPolicy


def test_async_insecure_http_flag_remains_compatible_with_remote_api_key_endpoint():
    config = _client_config(
        AsyncFineTuningSessionClient,
        endpoint="http://legacy-dev.example.com",
        credential=AzureKeyCredential("test-key"),
        allow_insecure_http=True,
    )

    assert config.allow_insecure_http is True


def test_async_insecure_http_allowed_against_localhost():
    config = _client_config(
        AsyncFineTuningSessionClient,
        endpoint="http://localhost:8080",
        credential=_FakeAsyncCredential(),
        allow_insecure_http=True,
    )

    assert config.allow_insecure_http is True


def test_secure_endpoint_unaffected_by_guard():
    config = _client_config(
        FineTuningSessionClient,
        endpoint="https://acct.services.ai.azure.com/api/projects/p",
        credential=_FakeCredential(),
    )

    assert config.allow_insecure_http is False
