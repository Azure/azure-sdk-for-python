# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

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
from azure.ai.evaluation._exceptions import EvaluationException
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
# Only bounds a hung test; no assertion depends on how long anything takes.
WAIT_SECONDS = 10


def access_token(value):
    return AccessToken(value, int(time.time()) + 3600)


def request_token(credential):
    return asyncio.run(AsyncPrompty.get_token_provider(credential)())


def join_all(threads):
    for thread in threads:
        thread.join(WAIT_SECONDS)
    assert not any(thread.is_alive() for thread in threads)


def watch_token_queue(credential, requests):
    """Return an event set once ``requests`` threads have queued for the credential's chat token request.

    Each request reads the cache's attempt count before it queues, so a token request released after this event
    completes while every request is queued, whatever the thread scheduling.
    """
    entry = TOKENS._entry(credential, CHAT_SCOPE, create=True)
    lock, queued, all_queued = entry.lock, set(), threading.Event()

    class QueueWatchingLock:
        def acquire(self, *args, **kwargs):
            queued.add(threading.get_ident())
            if len(queued) >= requests:
                all_queued.set()
            return lock.acquire(*args, **kwargs)

        def release(self):
            lock.release()

    entry.lock = QueueWatchingLock()
    return all_queued


class Credential:
    """A synchronous credential that records each token request and answers from a queue of results.

    With ``gate``, each token request waits until the test sets the event; tests set it in ``finally``.
    """

    def __init__(self, *results, gate=None):
        self.scopes = []
        self._results = list(results)
        self._gate = gate
        self._lock = threading.Lock()

    def get_token(self, *scopes, **_):
        with self._lock:
            self.scopes.append(scopes)
            result = self._results.pop(0) if len(self._results) > 1 else self._results[0]
        if self._gate is not None:
            self._gate.wait()
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
        release = threading.Event()
        credential = Credential(access_token("shared"), gate=release)
        all_queued = watch_token_queue(credential, 8)
        tokens = []
        threads = [threading.Thread(target=lambda: tokens.append(request_token(credential))) for _ in range(8)]
        try:
            for thread in threads:
                thread.start()
            assert all_queued.wait(WAIT_SECONDS)
        finally:
            release.set()
        join_all(threads)

        assert tokens == ["shared"] * 8
        assert credential.scopes == [(CHAT_SCOPE,)]

    @pytest.mark.parametrize("expiry", ["none", "near", "past", "zero"])
    def test_concurrent_requests_share_a_token_that_is_not_cached(self, expiry):
        expires_on = {"none": None, "near": time.time() + 120, "past": time.time() - 1, "zero": 0}[expiry]
        issued = SimpleNamespace(token="uncached", expires_on=expires_on)
        release = threading.Event()
        credential = Credential(issued, gate=release)
        all_queued = watch_token_queue(credential, 6)
        tokens = []
        threads = [threading.Thread(target=lambda: tokens.append(request_token(credential))) for _ in range(6)]
        try:
            for thread in threads:
                thread.start()
            assert all_queued.wait(WAIT_SECONDS)
        finally:
            release.set()
        join_all(threads)

        assert tokens == ["uncached"] * 6
        assert len(credential.scopes) == 1
        assert TOKENS.cached(credential, CHAT_SCOPE) is None
        # A request that did not wait on that token request makes its own.
        assert request_token(credential) == "uncached"
        assert len(credential.scopes) == 2

    def test_a_token_without_a_value_is_not_given_to_waiting_requests(self):
        release = threading.Event()
        credential = Credential(SimpleNamespace(token=None, expires_on=None), gate=release)
        all_queued = watch_token_queue(credential, 3)
        outcomes = []
        threads = [threading.Thread(target=lambda: outcomes.append(request_token(credential))) for _ in range(3)]
        try:
            for thread in threads:
                thread.start()
            assert all_queued.wait(WAIT_SECONDS)
        finally:
            release.set()
        join_all(threads)

        # Each request asks the credential itself and returns its value, as before.
        assert outcomes == [None] * 3
        assert len(credential.scopes) == 3

    def test_waiting_for_another_requests_token_does_not_block_the_event_loop(self):
        entered, release = threading.Event(), threading.Event()

        class SlowCredential(Credential):
            def get_token(self, *scopes, **kwargs):
                entered.set()
                return super().get_token(*scopes, **kwargs)

        credential = SlowCredential(access_token("shared"), gate=release)
        all_queued = watch_token_queue(credential, 2)
        leader = threading.Thread(target=lambda: request_token(credential))
        # Releases the token request if waiting blocked the loop, so a regression fails instead of hanging.
        watchdog = threading.Timer(WAIT_SECONDS, release.set)

        async def scenario():
            waiting = asyncio.ensure_future(AsyncPrompty.get_token_provider(credential)())
            assert await asyncio.to_thread(all_queued.wait, WAIT_SECONDS)
            # The loop ran this coroutine while the request waits for the first request's token.
            assert not waiting.done() and not release.is_set()
            release.set()
            return await waiting

        try:
            watchdog.start()
            leader.start()
            assert entered.wait(WAIT_SECONDS)
            assert asyncio.run(scenario()) == "shared"
        finally:
            release.set()
            watchdog.cancel()
        join_all([leader])
        assert len(credential.scopes) == 1

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
        credential = Credential(
            ClientAuthenticationError("Please run az login."), access_token("recovered"), gate=release
        )
        all_queued = watch_token_queue(credential, 4)
        outcomes = []

        def request():
            try:
                outcomes.append(request_token(credential))
            except ClientAuthenticationError as error:
                outcomes.append(str(error))

        threads = [threading.Thread(target=request) for _ in range(4)]
        try:
            for thread in threads:
                thread.start()
            assert all_queued.wait(WAIT_SECONDS)
        finally:
            release.set()
        join_all(threads)

        assert outcomes == ["Please run az login."] * 4
        assert len(credential.scopes) == 1
        # A request made after the failure tries again.
        assert request_token(credential) == "recovered"

    def test_other_failures_are_not_shared_so_each_request_keeps_the_error_type(self):
        class TokenServiceOutage(Exception):
            pass

        release = threading.Event()
        credential = Credential(TokenServiceOutage("The token service is unavailable."), gate=release)
        all_queued = watch_token_queue(credential, 3)
        outcomes = []

        def request():
            try:
                outcomes.append(request_token(credential))
            except Exception as error:  # pylint: disable=broad-except
                outcomes.append(type(error).__name__)

        threads = [threading.Thread(target=request) for _ in range(3)]
        try:
            for thread in threads:
                thread.start()
            assert all_queued.wait(WAIT_SECONDS)
        finally:
            release.set()
        join_all(threads)

        assert outcomes == ["TokenServiceOutage"] * 3
        assert len(credential.scopes) == 3

    def test_requests_waiting_on_a_token_kept_out_of_the_cache_use_it(self):
        entered, release = threading.Event(), threading.Event()

        class SlowCredential(Credential):
            def get_token(self, *scopes, **kwargs):
                entered.set()
                release.wait()
                return super().get_token(*scopes, **kwargs)

        credential = SlowCredential(access_token("issued"))
        all_queued = watch_token_queue(credential, 4)
        tokens = []
        threads = [threading.Thread(target=lambda: tokens.append(request_token(credential))) for _ in range(4)]
        try:
            for thread in threads:
                thread.start()
            assert entered.wait(WAIT_SECONDS) and all_queued.wait(WAIT_SECONDS)
            # Another request's 401 lands while the token is requested, so the token is not cached.
            TOKENS.discard(credential, CHAT_SCOPE, "rejected-earlier")
        finally:
            release.set()
        join_all(threads)

        assert tokens == ["issued"] * 4
        assert len(credential.scopes) == 1
        assert TOKENS.cached(credential, CHAT_SCOPE) is None
        # A request that starts afterwards requests its own token, which is cached again.
        assert request_token(credential) == "issued"
        assert len(credential.scopes) == 2
        assert TOKENS.cached(credential, CHAT_SCOPE).token == "issued"

    def test_a_rejected_token_is_not_given_to_waiting_requests(self):
        credential = Credential(access_token("unused"))
        entry = TOKENS._entry(credential, CHAT_SCOPE, create=True)
        entry.unstored = access_token("issued")

        TOKENS.discard(credential, CHAT_SCOPE, "other")
        assert entry.unstored.token == "issued"
        TOKENS.discard(credential, CHAT_SCOPE, "issued")
        assert entry.unstored is None

    def test_a_rejection_cannot_land_between_caching_and_the_hand_off_to_waiting_requests(self, monkeypatch):
        credential = Credential(access_token("issued"))
        store = TOKENS.store
        guard_free = []

        def probe_guard():
            # A rejection from another request needs this lock.
            acquired = TOKENS._guard.acquire(blocking=False)
            if acquired:
                TOKENS._guard.release()
            guard_free.append(acquired)

        def store_then_probe(*args, **kwargs):
            # A rejection while the token was requested keeps it out of the cache for waiting requests.
            TOKENS.discard(credential, CHAT_SCOPE, "rejected-earlier")
            stored = store(*args, **kwargs)
            probe = threading.Thread(target=probe_guard)
            probe.start()
            join_all([probe])
            return stored

        monkeypatch.setattr(TOKENS, "store", store_then_probe)
        assert request_token(credential) == "issued"

        # The decision to cache and the hand-off happen while the lock is held, so no rejection lands between them.
        assert guard_free == [False]
        assert TOKENS._entry(credential, CHAT_SCOPE).unstored.token == "issued"
        # A rejection afterwards still reaches the handed-off token.
        TOKENS.discard(credential, CHAT_SCOPE, "issued")
        assert TOKENS._entry(credential, CHAT_SCOPE).unstored is None

    def test_requests_waiting_on_a_failed_token_request_do_not_get_an_older_token(self):
        class TokenServiceOutage(Exception):
            pass

        entered, first_release, second_release = threading.Event(), threading.Event(), threading.Event()
        calls = []

        class StagedCredential(Credential):
            def get_token(self, *scopes, **kwargs):
                calls.append(1)
                if len(calls) == 1:
                    entered.set()
                    first_release.wait()
                elif len(calls) == 2:
                    second_release.wait()
                return super().get_token(*scopes, **kwargs)

        credential = StagedCredential(
            access_token("issued"), TokenServiceOutage("The token service is unavailable."), access_token("recovered")
        )
        results = {}

        def request(name):
            try:
                results[name] = request_token(credential)
            except Exception as error:  # pylint: disable=broad-except
                results[name] = type(error).__name__

        # A rejection while the first token is requested keeps that token out of the cache.
        first = threading.Thread(target=request, args=("first",))
        try:
            first.start()
            assert entered.wait(WAIT_SECONDS)
            TOKENS.discard(credential, CHAT_SCOPE, "rejected-earlier")
        finally:
            first_release.set()
        join_all([first])
        assert results["first"] == "issued" and TOKENS.cached(credential, CHAT_SCOPE) is None

        # The next token request fails; the requests waiting on it make their own attempt.
        all_queued = watch_token_queue(credential, 3)
        names = ["second", "waiter-1", "waiter-2"]
        threads = [threading.Thread(target=request, args=(name,)) for name in names]
        try:
            for thread in threads:
                thread.start()
            assert all_queued.wait(WAIT_SECONDS)
        finally:
            second_release.set()
        join_all(threads)

        assert sorted(results[name] for name in names) == ["TokenServiceOutage", "recovered", "recovered"]
        assert len(calls) == 3

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

    def test_concurrent_requests_share_the_default_providers_token_request(self):
        release = threading.Event()
        provider = AsyncAzureTokenProvider()
        inner = Credential(access_token("default"), gate=release)
        provider._credential = inner
        all_queued = watch_token_queue(inner, 6)
        tokens = []
        threads = [threading.Thread(target=lambda: tokens.append(request_token(provider))) for _ in range(6)]
        try:
            for thread in threads:
                thread.start()
            assert all_queued.wait(WAIT_SECONDS)
        finally:
            release.set()
        join_all(threads)

        assert tokens == ["default"] * 6
        assert inner.scopes == [(CHAT_SCOPE,)]
        asyncio.run(provider.close())

    def test_the_default_provider_creates_its_credential_once(self, monkeypatch):
        inner = Credential(access_token("created"))
        created = []

        async def initialize(client):
            created.append(client)
            return inner

        monkeypatch.setattr(AsyncAzureTokenProvider, "_initialize_async", staticmethod(initialize))
        provider = AsyncAzureTokenProvider()

        assert [request_token(provider) for _ in range(3)] == ["created"] * 3
        assert len(created) == 1 and inner.scopes == [(CHAT_SCOPE,)]
        # Its own get_token still asks the credential it created.
        assert asyncio.run(provider.get_token(CHAT_SCOPE)).token == "created"
        assert len(inner.scopes) == 2
        asyncio.run(provider.close())

    def test_concurrent_first_requests_share_one_default_credential_and_token_request(self, monkeypatch):
        requests = 4
        barrier = threading.Barrier(requests)
        created, closed = [], []

        class ClosableCredential(Credential):
            def close(self):
                closed.append(self)

        async def initialize(client):
            # Every first request creates a credential at the same time.
            await asyncio.to_thread(barrier.wait, WAIT_SECONDS)
            credential = ClosableCredential(access_token("default"))
            created.append(credential)
            return credential

        monkeypatch.setattr(AsyncAzureTokenProvider, "_initialize_async", staticmethod(initialize))
        provider = AsyncAzureTokenProvider()
        tokens = []
        threads = [threading.Thread(target=lambda: tokens.append(request_token(provider))) for _ in range(requests)]
        for thread in threads:
            thread.start()
        join_all(threads)

        assert tokens == ["default"] * requests
        # The first credential created is kept and the others are closed, so one token request serves every row.
        assert len(created) == requests and len(closed) == requests - 1
        assert sum(len(credential.scopes) for credential in created) == 1
        asyncio.run(provider.close())

    def test_a_credential_created_while_the_default_provider_closes_is_closed(self, monkeypatch):
        closed = []

        class ClosableCredential(Credential):
            def close(self):
                closed.append(self)

        created = ClosableCredential(access_token("late"))

        async def scenario():
            entered, gate = asyncio.Event(), asyncio.Event()

            async def initialize(client):
                entered.set()
                await gate.wait()
                return created

            monkeypatch.setattr(AsyncAzureTokenProvider, "_initialize_async", staticmethod(initialize))
            provider = AsyncAzureTokenProvider()
            pending = asyncio.ensure_future(provider.get_credential())
            await entered.wait()
            await provider.close()
            gate.set()
            with pytest.raises(EvaluationException, match="already been closed"):
                await pending
            assert provider._credential is None

        asyncio.run(scenario())
        assert closed == [created]

    def test_a_token_rejected_while_another_request_awaits_it_is_not_stored_again(self):
        async def scenario():
            entered, gate = asyncio.Event(), asyncio.Event()
            calls = []

            class AsyncCredential:
                async def get_token(self, *_, **__):
                    calls.append(1)
                    if len(calls) == 1:
                        entered.set()
                        await gate.wait()
                    return access_token("rejected")

            credential = AsyncCredential()
            waiting = AsyncPrompty.get_token_provider(credential)
            rejected = AsyncPrompty.get_token_provider(credential)
            pending = asyncio.ensure_future(waiting())
            # The first request misses the cache and awaits its token.
            await entered.wait()
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

    def test_a_token_the_credential_reissues_after_a_rejection_is_cached_again(self):
        credential = Credential(access_token("same"))

        async def reject_once():
            provider = AsyncPrompty.get_token_provider(credential)
            assert await provider() == "same"
            # The service rejects the token with a 401, for example while a role assignment still propagates.
            provider.discard()

        asyncio.run(reject_once())
        assert TOKENS.cached(credential, CHAT_SCOPE) is None
        # The credential re-issues the same token: it is requested once more, then reused again.
        assert [request_token(credential) for _ in range(3)] == ["same"] * 3
        assert len(credential.scopes) == 2
        assert TOKENS.cached(credential, CHAT_SCOPE).token == "same"

    def test_an_acquisition_that_began_before_two_rejections_is_not_stored(self):
        async def scenario():
            entered, gate = asyncio.Event(), asyncio.Event()
            calls = []

            class AsyncCredential:
                async def get_token(self, *_, **__):
                    calls.append(1)
                    call = len(calls)
                    if call == 1:
                        entered.set()
                        await gate.wait()
                    # The delayed first acquisition and the second return token A; later ones return token B.
                    return access_token("token-A" if call <= 2 else "token-B")

            credential = AsyncCredential()
            pending = asyncio.ensure_future(AsyncPrompty.get_token_provider(credential)())
            await entered.wait()
            # Two later acquisitions complete first, and the service rejects each token with a 401.
            for expected in ("token-A", "token-B"):
                provider = AsyncPrompty.get_token_provider(credential)
                assert await provider() == expected
                provider.discard()
            gate.set()
            # The delayed acquisition returns a token the service already rejected; it must not be cached.
            assert await pending == "token-A"
            assert TOKENS.cached(credential, CHAT_SCOPE) is None
            # The next acquisition is cached again.
            assert await AsyncPrompty.get_token_provider(credential)() == "token-B"
            assert TOKENS.cached(credential, CHAT_SCOPE).token == "token-B"

        asyncio.run(scenario())
