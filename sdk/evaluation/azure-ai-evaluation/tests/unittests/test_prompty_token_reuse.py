"""The chat flow's token provider reuses a caller credential's token, kept apart from Decision tokens."""

import asyncio
import gc
import threading
import time
import weakref
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from openai import AuthenticationError, InternalServerError

import azure.ai.evaluation._evaluators._coherence as coherence
from azure.ai.evaluation._common.utils import construct_prompty_model_config, validate_model_config
from azure.ai.evaluation._constants import TokenScope
from azure.ai.evaluation._legacy._common._async_token_provider import AsyncAzureTokenProvider
from azure.ai.evaluation._legacy._common._token_cache import TOKENS
from azure.ai.evaluation._legacy.prompty import AsyncPrompty
from azure.ai.evaluation._legacy.prompty._exceptions import WrappedOpenAIError

CHAT_SCOPE = TokenScope.COGNITIVE_SERVICES_MANAGEMENT
DECISION_SCOPE = "https://cognitiveservices.azure.com/.default"
COHERENCE_PROMPTY = Path(coherence.__file__).parent / "coherence.prompty"
CHAT_MODEL = construct_prompty_model_config(
    validate_model_config({"azure_endpoint": "https://example.openai.azure.com", "azure_deployment": "judge"}),
    "2024-10-21",
    "test-agent",
)


def access_token(value):
    return AccessToken(value, int(time.time()) + 3600)


def request_token(credential):
    return asyncio.run(AsyncPrompty.get_token_provider(credential)())


class Credential:
    """A synchronous credential that records each token request and answers from a queue of results."""

    def __init__(self, *results, delay=0.0):
        self.scopes = []
        self._results = list(results)
        self._delay = delay
        self._lock = threading.Lock()

    def get_token(self, *scopes, **_):
        with self._lock:
            self.scopes.append(scopes)
            result = self._results.pop(0) if len(self._results) > 1 else self._results[0]
        time.sleep(self._delay)
        if isinstance(result, Exception):
            raise result
        return result


@pytest.mark.unittest
class TestChatTokenReuse:
    def test_a_fresh_token_is_reused_across_requests_and_flows(self):
        credential = Credential(access_token("chat"))

        assert [request_token(credential) for _ in range(3)] == ["chat"] * 3
        assert asyncio.run(AsyncPrompty.get_token_provider(credential)()) == "chat"
        assert credential.scopes == [(CHAT_SCOPE,)]

    def test_concurrent_requests_wait_for_one_token_request(self):
        credential = Credential(access_token("shared"), delay=0.3)
        tokens = []
        threads = [threading.Thread(target=lambda: tokens.append(request_token(credential))) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(10)

        assert tokens == ["shared"] * 8
        assert credential.scopes == [(CHAT_SCOPE,)]

    def test_chat_and_decision_tokens_are_kept_apart(self):
        credential = Credential(access_token("chat"))
        TOKENS.store(credential, DECISION_SCOPE, access_token("decision"))

        assert request_token(credential) == "chat"
        assert credential.scopes == [(CHAT_SCOPE,)]
        assert TOKENS.cached(credential, DECISION_SCOPE).token == "decision"

    def test_a_failed_token_request_raises_the_credential_error_and_is_retried(self):
        credential = Credential(ClientAuthenticationError("Please run az login."), access_token("recovered"))

        with pytest.raises(ClientAuthenticationError, match="az login"):
            request_token(credential)
        assert request_token(credential) == "recovered"
        assert len(credential.scopes) == 2

    def test_requests_queued_behind_a_failed_token_request_share_its_failure(self):
        release = threading.Event()

        class FailingCredential(Credential):
            def get_token(self, *scopes, **kwargs):
                release.wait(5)
                return super().get_token(*scopes, **kwargs)

        credential = FailingCredential(ClientAuthenticationError("Please run az login."), access_token("recovered"))
        outcomes = []

        def request():
            try:
                outcomes.append(request_token(credential))
            except ClientAuthenticationError as error:
                outcomes.append(str(error))

        threads = [threading.Thread(target=request) for _ in range(4)]
        for thread in threads:
            thread.start()
        time.sleep(0.3)
        release.set()
        for thread in threads:
            thread.join(10)

        assert outcomes == ["Please run az login."] * 4
        assert len(credential.scopes) == 1
        # A request made after the failure tries again.
        assert request_token(credential) == "recovered"

    def test_other_failures_are_not_shared_so_each_request_keeps_the_error_type(self):
        class TokenServiceOutage(Exception):
            pass

        release = threading.Event()

        class OutageCredential(Credential):
            def get_token(self, *scopes, **kwargs):
                release.wait(5)
                return super().get_token(*scopes, **kwargs)

        credential = OutageCredential(TokenServiceOutage("The token service is unavailable."))
        outcomes = []

        def request():
            try:
                outcomes.append(request_token(credential))
            except Exception as error:  # pylint: disable=broad-except
                outcomes.append(type(error).__name__)

        threads = [threading.Thread(target=request) for _ in range(3)]
        for thread in threads:
            thread.start()
        time.sleep(0.3)
        release.set()
        for thread in threads:
            thread.join(10)

        assert outcomes == ["TokenServiceOutage"] * 3
        assert len(credential.scopes) == 3

    def test_a_token_without_an_expiry_is_requested_each_time(self):
        credential = Credential(SimpleNamespace(token="no-expiry", expires_on=None))

        assert [request_token(credential) for _ in range(2)] == ["no-expiry"] * 2
        assert len(credential.scopes) == 2

    def test_an_asynchronous_credentials_token_is_reused(self):
        class AsyncCredential:
            def __init__(self):
                self.calls = 0

            async def get_token(self, *_, **__):
                self.calls += 1
                return access_token("async")

        credential = AsyncCredential()

        assert [request_token(credential) for _ in range(3)] == ["async"] * 3
        assert credential.calls == 1

    def test_the_cache_does_not_keep_the_credential_alive(self):
        credential = Credential(access_token("caller-owned"))
        assert request_token(credential) == "caller-owned"
        assert TOKENS.cached(credential, CHAT_SCOPE) is not None

        reference = weakref.ref(credential)
        del credential
        gc.collect()
        assert reference() is None

    @pytest.mark.parametrize("default_provider", [False, True], ids=["caller credential", "default provider"])
    @pytest.mark.parametrize(
        "error_type, status, tokens_sent",
        [(AuthenticationError, 401, ["rejected", "replacement"]), (InternalServerError, 500, ["rejected", "rejected"])],
    )
    def test_only_a_token_rejected_with_401_is_requested_again(
        self, monkeypatch, error_type, status, tokens_sent, default_provider
    ):
        credential = Credential(access_token("rejected"), access_token("replacement"))
        if default_provider:
            provider = AsyncAzureTokenProvider()
            provider._credential = credential
            token_credential = provider
        else:
            token_credential = credential
        flow = AsyncPrompty.load(source=COHERENCE_PROMPTY, model=CHAT_MODEL, token_credential=token_credential)
        sent = []

        async def send(self, *, api_client, params, timeout):
            sent.append(await api_client._azure_ad_token_provider())
            response = httpx.Response(status, request=httpx.Request("POST", "https://example.openai.azure.com"))
            error = error_type("request failed", response=response, body=None)
            raise WrappedOpenAIError(error=error) from error

        monkeypatch.setattr(AsyncPrompty, "_send_with_retries", send)
        for _ in range(2):
            with pytest.raises(WrappedOpenAIError):
                asyncio.run(flow(query="When does the museum open?", response="At noon."))

        assert sent == tokens_sent
        assert len(credential.scopes) == len(set(tokens_sent))

    def test_the_default_provider_reuses_its_token(self):
        provider = AsyncAzureTokenProvider()
        inner = Credential(access_token("default"))
        provider._credential = inner

        assert [request_token(provider) for _ in range(3)] == ["default"] * 3
        assert inner.scopes == [(CHAT_SCOPE,)]
        asyncio.run(provider.close())

    def test_a_token_rejected_while_another_request_awaits_it_is_not_stored_again(self):
        async def scenario():
            gate = asyncio.Event()
            calls = []

            class AsyncCredential:
                async def get_token(self, *_, **__):
                    calls.append(1)
                    if len(calls) == 1:
                        await gate.wait()
                    return access_token("rejected")

            credential = AsyncCredential()
            waiting = AsyncPrompty.get_token_provider(credential)
            rejected = AsyncPrompty.get_token_provider(credential)
            pending = asyncio.ensure_future(waiting())
            # The first request misses the cache and awaits its token.
            await asyncio.sleep(0)
            assert await rejected() == "rejected"
            # The service rejects that token with a 401 before the first request resumes.
            rejected.discard()
            gate.set()
            assert await pending == "rejected"
            assert TOKENS.cached(credential, CHAT_SCOPE) is None
            # A different token from the credential is cached again.
            TOKENS.store(credential, CHAT_SCOPE, access_token("new"))
            assert TOKENS.cached(credential, CHAT_SCOPE).token == "new"

        asyncio.run(scenario())
