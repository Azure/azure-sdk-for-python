# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Owned default-provider resources and caller-owned Decision credentials."""

import asyncio
import json
import threading
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from azure.ai.evaluation._legacy._common import _async_token_provider as providers
from azure.ai.evaluation._evaluators._common._model_runners import DecisionModelRunner
from azure.ai.evaluation._exceptions import EvaluationException

from test_decision_model_support import DECISION_CONFIG, FakeClient, FakeResponse, QUESTIONS, level_payload


@pytest.fixture
def resources(monkeypatch):
    client = Mock(close=AsyncMock())
    credential = Mock(get_token=Mock(return_value=SimpleNamespace(token="local-token")))
    monkeypatch.setattr(providers, "AzureEnvironmentClient", Mock(return_value=client))
    initialize = AsyncMock(return_value=credential)
    monkeypatch.setattr(providers.AsyncAzureTokenProvider, "_initialize_async", initialize)
    return client, credential, initialize


@pytest.mark.parametrize("failure", [None, RuntimeError, asyncio.CancelledError])
def test_context_closes_owned_resources_after_token_outcome(resources, failure):
    client, credential, _ = resources
    if failure:
        credential.get_token.side_effect = failure("token failed")

    async def request():
        async with providers.AsyncAzureTokenProvider() as provider:
            return await provider.get_token("scope")

    if failure:
        with pytest.raises(failure, match="token failed" if failure is RuntimeError else None):
            asyncio.run(request())
    else:
        assert asyncio.run(request()).token == "local-token"
    credential.close.assert_called_once_with()
    client.close.assert_awaited_once_with()


@pytest.mark.parametrize("failure", [RuntimeError, asyncio.CancelledError])
def test_failed_context_entry_closes_environment_client(resources, failure):
    client, credential, initialize = resources
    initialize.side_effect = failure("initialization failed")

    async def request():
        async with providers.AsyncAzureTokenProvider():
            pytest.fail("Context entry must fail")

    with pytest.raises(failure, match="initialization failed" if failure is RuntimeError else None):
        asyncio.run(request())
    client.close.assert_awaited_once_with()
    credential.close.assert_not_called()


def test_lazy_provider_reuses_credential_and_close_is_idempotent(resources):
    client, credential, initialize = resources

    async def request():
        provider = providers.AsyncAzureTokenProvider()
        await provider.get_token("first")
        await provider.get_token("second")
        await provider.__aenter__()
        await provider.close()
        await provider.close()

    asyncio.run(request())
    initialize.assert_awaited_once()
    assert credential.get_token.call_count == 2
    credential.close.assert_called_once_with()
    client.close.assert_awaited_once_with()


def test_repeated_provider_contexts_close_each_owned_provider(monkeypatch):
    clients = [Mock(close=AsyncMock()) for _ in range(3)]
    credentials = [Mock(get_token=Mock(return_value=SimpleNamespace(token="local-token"))) for _ in range(3)]
    monkeypatch.setattr(providers, "AzureEnvironmentClient", Mock(side_effect=clients))
    monkeypatch.setattr(providers.AsyncAzureTokenProvider, "_initialize_async", AsyncMock(side_effect=credentials))

    async def request():
        for _ in range(3):
            async with providers.AsyncAzureTokenProvider() as provider:
                await provider.get_token("https://cognitiveservices.azure.com/.default")

    asyncio.run(request())
    for client, credential in zip(clients, credentials):
        client.close.assert_awaited_once_with()
        credential.close.assert_called_once_with()


@pytest.mark.parametrize("credential_fails,client_fails", [(True, False), (False, True), (True, True)])
def test_close_attempts_both_resources_and_exposes_cleanup_failures(resources, credential_fails, client_fails):
    client, credential, _ = resources
    if credential_fails:
        credential.close.side_effect = RuntimeError("credential close failed")
    if client_fails:
        client.close.side_effect = ValueError("environment close failed")

    async def request():
        provider = providers.AsyncAzureTokenProvider()
        await provider.__aenter__()
        try:
            await provider.close()
        finally:
            await provider.close()

    expected = ValueError if client_fails else RuntimeError
    with pytest.raises(expected) as raised:
        asyncio.run(request())
    if credential_fails and client_fails:
        assert isinstance(raised.value.__context__, RuntimeError)
    credential.close.assert_called_once_with()
    client.close.assert_awaited_once_with()


@pytest.mark.parametrize("outcome", ["success", "failure", "timeout", "cancelled"])
def test_explicit_request_credential_ownership_and_worker_cleanup(resources, monkeypatch, outcome):
    from azure.ai.evaluation._evaluators._common import _model_runners

    client, credential, _ = resources
    http = FakeClient(FakeResponse(body=json.dumps(level_payload(4)).encode()))
    monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: http)
    config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
    entered, release = threading.Event(), threading.Event()
    if outcome == "failure":
        credential.get_token.side_effect = RuntimeError("private token failure")
    elif outcome in ("timeout", "cancelled"):

        def blocked_token(*_, **__):
            entered.set()
            assert release.wait(2)
            return SimpleNamespace(token="local-token")

        credential.get_token.side_effect = blocked_token

    async def request():
        cancel = False
        runner = DecisionModelRunner(config, credential, cancellation_requested=lambda: cancel)
        task = asyncio.create_task(runner(state={}, questions=QUESTIONS, timeout=0.1 if outcome == "timeout" else 2))
        try:
            if outcome in ("timeout", "cancelled"):
                while not entered.is_set():
                    await asyncio.sleep(0.001)
                cancel = outcome == "cancelled"
            if outcome == "success":
                await task
            else:
                with pytest.raises(EvaluationException):
                    await task
        finally:
            release.set()

    asyncio.run(request())
    credential.close.assert_not_called()
    client.close.assert_not_awaited()
    assert len(http.calls) == (1 if outcome == "success" else 0)


def test_repeated_decision_calls_reuse_caller_credential_without_creating_provider(resources, monkeypatch):
    from azure.ai.evaluation._evaluators._common import _model_runners

    client, credential, initialize = resources
    http = FakeClient(FakeResponse(body=json.dumps(level_payload(4)).encode()))
    monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: http)
    config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
    runner = DecisionModelRunner(config, credential)
    for _ in range(3):
        asyncio.run(runner(state={}, questions=QUESTIONS, timeout=1))
    assert len(http.calls) == credential.get_token.call_count == 3
    initialize.assert_not_awaited()
    credential.close.assert_not_called()
    client.close.assert_not_awaited()


def test_prompty_still_constructs_default_provider_when_no_credential_is_supplied(resources):
    from azure.ai.evaluation import FluencyEvaluator
    from test_decision_model_support import CHAT_CONFIG

    client, credential, initialize = resources
    evaluator = FluencyEvaluator({key: value for key, value in CHAT_CONFIG.items() if key != "api_key"})
    provider = evaluator._flow._token_credential
    assert isinstance(provider, providers.AsyncAzureTokenProvider)
    initialize.assert_not_awaited()
    asyncio.run(provider.close())
    client.close.assert_awaited_once_with()
    credential.close.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("in_config", [False, True])
@pytest.mark.parametrize("outcome", ["success", "failure", "cancelled"])
def test_explicit_credentials_remain_caller_owned(monkeypatch, asynchronous, in_config, outcome):
    from azure.ai.evaluation._evaluators._common import _model_runners

    http = FakeClient(
        FakeResponse(body=json.dumps(level_payload(4)).encode()), delay=0.2 if outcome == "cancelled" else 0
    )
    monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: http)
    credential = Mock()
    token_call = AsyncMock if asynchronous else Mock
    credential.get_token = token_call(return_value=SimpleNamespace(token="caller-token"))
    if outcome == "failure":
        credential.get_token.side_effect = RuntimeError("private token failure")
    config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}
    if in_config:
        config["credential"] = credential

    async def request():
        cancelled = asyncio.Event()
        runner = DecisionModelRunner(config, None if in_config else credential, cancellation_requested=cancelled.is_set)
        task = asyncio.create_task(runner(state={}, questions=QUESTIONS, timeout=1))
        if outcome == "cancelled":
            while not http.calls:
                await asyncio.sleep(0.001)
            cancelled.set()
        if outcome == "success":
            await task
        else:
            with pytest.raises(EvaluationException):
                await task

    asyncio.run(request())
    credential.close.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("termination", ["timeout", "cancelled"])
def test_caller_credential_remains_open_when_authentication_is_interrupted(monkeypatch, asynchronous, termination):
    from azure.ai.evaluation._evaluators._common import _model_runners

    http = FakeClient()
    monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: http)
    entered, release = threading.Event(), threading.Event()
    credential = Mock()

    def sync_token(*_):
        entered.set()
        assert release.wait(2)
        return SimpleNamespace(token="caller-token")

    async def async_token(*_):
        entered.set()
        await asyncio.sleep(10)

    credential.get_token = AsyncMock(side_effect=async_token) if asynchronous else Mock(side_effect=sync_token)
    config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}

    async def request():
        cancel = False
        runner = DecisionModelRunner(config, credential, cancellation_requested=lambda: cancel)
        task = asyncio.create_task(
            runner(state={}, questions=QUESTIONS, timeout=0.1 if termination == "timeout" else 2)
        )
        try:
            while not entered.is_set():
                await asyncio.sleep(0.001)
            cancel = termination == "cancelled"
            with pytest.raises(EvaluationException):
                await task
        finally:
            release.set()

    asyncio.run(request())
    credential.close.assert_not_called()
    assert not http.calls
