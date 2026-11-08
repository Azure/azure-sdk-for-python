# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline guards for client-owned inference, independent of Cosmos connections."""

import asyncio
import ast
import inspect
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from urllib3.util.retry import Retry

from azure.cosmos import cosmos_client, database
from azure.cosmos import _inference_service as sync_service
from azure.cosmos.aio import _cosmos_client, _database
from azure.cosmos.aio import _inference_service_async as async_service
from azure.cosmos._cosmos_client_connection import CosmosClientConnection as SyncConnection
from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection as AsyncConnection
from azure.cosmos._inference_client import InferenceClient, InferenceClientSettings
from azure.cosmos._retry_utility import ConnectionRetryPolicy
from azure.cosmos.aio._retry_utility_async import _ConnectionRetryPolicy
from azure.cosmos._utils import get_user_agent, get_user_agent_async
from azure.cosmos.documents import ConnectionPolicy
from azure.cosmos.exceptions import CosmosHttpResponseError

_ENDPOINT = "AZURE_COSMOS_SEMANTIC_RERANKER_INFERENCE_ENDPOINT"


def _resolve(result):
    return asyncio.run(result) if inspect.isawaitable(result) else result


class _ForbiddenConnection:
    def __getattribute__(self, name):
        raise AssertionError(f"Reranking accessed the Cosmos connection: {name}")


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def setup(request, monkeypatch):
    asynchronous = request.param
    module = _cosmos_client if asynchronous else cosmos_client
    service_module = async_service if asynchronous else sync_service
    monkeypatch.setattr(module, "CosmosClientConnection", MagicMock())
    monkeypatch.delenv(_ENDPOINT, raising=False)
    factory = MagicMock(wraps=service_module._InferenceService)
    monkeypatch.setattr(module, "_InferenceService", factory)
    credential = SimpleNamespace(get_token=AsyncMock() if asynchronous else MagicMock())
    policy = ConnectionPolicy()
    policy.InferenceRequestTimeout = 17
    policy.ConnectionRetryConfiguration = 7
    client = module.CosmosClient(
        "https://account.invalid",
        credential,
        _backend="rust",
        connection_policy=policy,
        user_agent_suffix="contoso-bank",
        enable_diagnostics_logging=True,
    )
    yield SimpleNamespace(
        client=client,
        module=module,
        service_module=service_module,
        asynchronous=asynchronous,
        factory=factory,
        credential=credential,
    )
    _resolve(client._adapter.close())


def test_rerank_is_lazy_shared_and_independent_of_connection_rust(setup, monkeypatch):
    setup.factory.assert_not_called()
    client = setup.client
    client.client_connection = _ForbiddenConnection()
    containers = [client.get_database_client(name).get_container_client("documents") for name in ("sales", "support")]
    setup.factory.assert_not_called()
    for container in containers:
        assert container._inference_client is client._inference_client

    # Read the endpoint on first use, not during CosmosClient construction.
    monkeypatch.setenv(_ENDPOINT, "https://inference.invalid")
    response = MagicMock()
    response.status_code = 200
    response.headers = {"x-test": "inference"}
    response.body.return_value = b'{"Scores":[{"index":0,"score":0.9}]}'
    run_type = AsyncMock if setup.asynchronous else MagicMock
    run = run_type(return_value=SimpleNamespace(http_response=response))
    pipeline = SimpleNamespace(_pipeline=SimpleNamespace(run=run))
    pipeline_factory = MagicMock(return_value=pipeline)
    monkeypatch.setattr(
        setup.service_module,
        "AsyncPipelineClient" if setup.asynchronous else "PipelineClient",
        pipeline_factory,
    )

    for container in containers:
        result = _resolve(
            container.semantic_rerank(
                context="bank account",
                documents=["Contoso Bank"],
                options={"top_k": 1, "return_documents": False},
            )
        )
        assert result["Scores"] == [{"index": 0, "score": 0.9}]
        assert result.get_response_headers()["x-test"] == "inference"
    setup.factory.assert_called_once()
    pipeline_factory.assert_called_once()
    settings = setup.factory.call_args.args[0]
    assert settings.aad_credentials is setup.credential
    assert settings.request_timeout == 17
    prepared_policy = setup.module.CosmosClientConnection.call_args.kwargs["connection_policy"]
    assert settings.retry_configuration is prepared_policy.ConnectionRetryConfiguration
    assert settings.enable_diagnostics_logging is True
    expected_agent = (get_user_agent_async if setup.asynchronous else get_user_agent)("contoso-bank")
    assert settings.user_agent == expected_agent
    policies = pipeline_factory.call_args.kwargs["policies"]
    assert policies[1].user_agent == expected_agent + ("_inference" if setup.asynchronous else "")
    assert policies[4]._credential is setup.credential
    assert policies[4]._scopes == (setup.service_module._InferenceService.inference_service_default_scope,)
    assert policies[-1]._enable_diagnostics_logging is True
    assert run.call_count == 2
    for call in run.call_args_list:
        request = call.args[0]
        assert request.method == "POST"
        assert request.url == "https://inference.invalid/inference/semanticReranking"
        assert json.loads(request.body) == {
            "query": "bank account",
            "documents": ["Contoso Bank"],
            "top_k": 1,
            "return_documents": False,
        }
        assert call.kwargs["connection_timeout"] == 17
        assert call.kwargs["read_timeout"] == 17
        if setup.asynchronous:
            assert call.kwargs["connection_verify"] is True
    setup.credential.get_token.assert_not_called()


def test_failed_initialization_can_retry_without_connection_rust(setup, monkeypatch):
    setup.client.client_connection = _ForbiddenConnection()
    container = setup.client.get_database_client("sales").get_container_client("documents")
    with pytest.raises(CosmosHttpResponseError, match="Failed to initialize inference service") as caught:
        _resolve(container.semantic_rerank(context="query", documents=["document"]))
    assert caught.value.status_code == 400
    assert isinstance(caught.value.__cause__, ValueError)
    assert _ENDPOINT in str(caught.value)
    monkeypatch.setenv(_ENDPOINT, "https://inference.invalid")
    service = setup.client._inference_client.get_service()
    assert service is setup.client._inference_client.get_service()
    assert setup.factory.call_count == 2
    _resolve(service._inference_pipeline_client.close())


@pytest.mark.parametrize("credential", ["ZmFrZQ==", {"masterKey": "ZmFrZQ=="}])
def test_key_client_preserves_aad_error_without_initialization_rust(setup, credential):
    client = setup.module.CosmosClient("https://account.invalid", credential, _backend="rust")
    try:
        client.client_connection = _ForbiddenConnection()
        container = client.get_database_client("sales").get_container_client("documents")
        with pytest.raises(CosmosHttpResponseError, match="Semantic reranking requires AAD credentials"):
            _resolve(container.semantic_rerank(context="query", documents=["document"]))
        setup.factory.assert_not_called()
    finally:
        _resolve(client._adapter.close())


def test_service_requires_a_credential_rust(setup, monkeypatch):
    monkeypatch.setenv(_ENDPOINT, "https://inference.invalid")
    settings = replace(setup.client._inference_client._settings, aad_credentials=None)
    with pytest.raises(ValueError, match="Semantic reranking requires AAD credentials"):
        setup.service_module._InferenceService(settings)


def test_missing_retry_policy_is_rejected_rust(setup, monkeypatch):
    monkeypatch.setenv(_ENDPOINT, "https://inference.invalid")
    settings = replace(setup.client._inference_client._settings, retry_configuration=None)
    with pytest.raises(TypeError, match="Unsupported retry policy"):
        setup.service_module._InferenceService(settings)


def test_concurrent_first_use_creates_one_service_rust():
    settings = InferenceClientSettings(MagicMock(), 5, 3, "test-agent", False)
    entered = threading.Event()
    release = threading.Event()
    expected = object()

    def build(configuration):
        assert configuration is settings
        entered.set()
        assert release.wait(5)
        return expected

    factory = MagicMock(side_effect=build)
    client = InferenceClient(settings, factory)
    with ThreadPoolExecutor(max_workers=8) as executor:
        first = executor.submit(client.get_service)
        try:
            assert entered.wait(5)
            remaining = [executor.submit(client.get_service) for _ in range(7)]
        finally:
            release.set()
        assert all(future.result(timeout=5) is expected for future in [first, *remaining])
    factory.assert_called_once_with(settings)
    other = InferenceClient(settings, MagicMock(return_value=object()))
    assert other.get_service() is not expected


@pytest.mark.parametrize("configuration", ["integer", "policy", "urllib3"])
def test_retry_settings_preserved_rust(setup, monkeypatch, configuration):
    monkeypatch.setenv(_ENDPOINT, "https://inference.invalid")
    retry_type = _ConnectionRetryPolicy if setup.asynchronous else ConnectionRetryPolicy
    if configuration == "integer":
        retry = 4
        expected = {"total": 4}
    elif configuration == "urllib3":
        retry = Retry(total=4, connect=2, read=1, status=3, status_forcelist=[429, 503], backoff_factor=0.25)
        expected = dict(
            retry_total=4,
            retry_connect=2,
            retry_read=1,
            retry_status=3,
            retry_backoff_max=Retry.DEFAULT_BACKOFF_MAX,
            retry_on_status_codes=[429, 503],
            retry_backoff_factor=0.25,
        )
    else:
        retry = retry_type()
        expected = dict(
            retry_total=4,
            retry_connect=2,
            retry_read=1,
            retry_status=3,
            retry_backoff_max=60,
            retry_on_status_codes=[429, 503],
            retry_backoff_factor=0.25,
        )
        for name, value in expected.items():
            setattr(retry, name, value)
    factory = MagicMock(wraps=retry_type)
    monkeypatch.setattr(
        setup.service_module, "_ConnectionRetryPolicy" if setup.asynchronous else "ConnectionRetryPolicy", factory
    )
    settings = replace(setup.client._inference_client._settings, retry_configuration=retry)
    service = setup.service_module._InferenceService(settings)
    try:
        factory.assert_called_once_with(**expected)
    finally:
        _resolve(service._inference_pipeline_client.close())


def test_retired_connection_getters_and_proxy_propagation_rust():
    assert not hasattr(SyncConnection, "_get_inference_service")
    assert not hasattr(AsyncConnection, "_get_inference_service")
    for module in (cosmos_client, _cosmos_client, database, _database):
        tree = ast.parse(inspect.getsource(module))
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in ("DatabaseProxy", "ContainerProxy")
        ]
        assert calls
        for call in calls:
            assert any(
                keyword.arg == "_inference_client" and ast.unparse(keyword.value) == "self._inference_client"
                for keyword in call.keywords
            )
