# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import importlib
import threading
import time
from unittest.mock import AsyncMock, Mock
from urllib.parse import urlparse

import pytest
from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.pipeline import AsyncPipeline, Pipeline, PipelineContext, PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import (
    AsyncRedirectPolicy,
    AsyncRetryPolicy,
    RedirectPolicy,
    RetryPolicy,
    SensitiveHeaderCleanupPolicy,
)
from azure.core.rest import HttpRequest
from test_challenge_auth import (
    AsyncChallengeAuthPolicy,
    ChallengeAuthPolicy,
    HttpChallenge,
    HttpChallengeCache,
    get_random_url,
)


HEADER = 'Bearer authorization="https://authority.net/tenant", resource=https://vault.azure.net'
CLAIMS = 'Bearer authorization="https://authority.net/replacement", scope=https://vault.azure.net/new, claims="e30="'
FLOWS = {
    "malformed": ["Bearer"],
    "mismatch": ['Bearer authorization="https://authority.net/tenant", resource=https://other.example'],
    "missing": [None],
    "kv-missing": [HEADER, None],
    "cae-missing": [CLAIMS, None],
    "kv-cae-missing": [HEADER, CLAIMS, None],
    "skipped-kv": [HEADER, HEADER],
}


@pytest.mark.parametrize("state", ["unchanged", "replacement", "identical", "absent"])
@pytest.mark.parametrize("alias", ["path", "case", "default-port"])
def test_conditional_cache_removal_is_atomic(monkeypatch, state, alias):
    url = get_random_url()
    expected = HttpChallenge(url, HEADER)
    replacement = HttpChallenge(url, HEADER if state == "identical" else HEADER.replace("tenant", "other"))
    HttpChallengeCache.set_challenge_for_url(url, expected if state == "unchanged" else replacement)
    target = url + "/next" if alias == "path" else url.upper()
    if alias == "default-port":
        parsed = urlparse(url)
        target = f"https://{parsed.netloc.upper()}:443{parsed.path}"

    class RecordingLock:
        def __init__(self):
            self.lock = threading.Lock()
            self.entries = 0

        def __enter__(self):
            self.lock.acquire()
            self.entries += 1

        def __exit__(self, *args):
            self.lock.release()

    lock = RecordingLock()

    class LockedCache(dict):
        def get(self, *args):
            assert lock.lock.locked()
            return super().get(*args)

        def pop(self, *args):
            assert lock.lock.locked()
            return super().pop(*args)

    monkeypatch.setattr(HttpChallengeCache, "_lock", lock)
    monkeypatch.setattr(HttpChallengeCache, "_cache", LockedCache(HttpChallengeCache._cache))
    HttpChallengeCache.remove_challenge_for_url_if_matches(
        url=target, expected_challenge=None if state == "absent" else expected
    )
    assert lock.entries == 1
    assert HttpChallengeCache.get_challenge_for_url(url) is (None if state == "unchanged" else replacement)
    HttpChallengeCache.remove_challenge_for_url_if_matches(target, expected)
    assert HttpChallengeCache.get_challenge_for_url(url) is (None if state == "unchanged" else replacement)


@pytest.mark.parametrize("url", ["", None, "https://host:invalid", "https://[invalid"])
def test_conditional_cache_removal_validates_url_when_absent(url):
    with pytest.raises(ValueError):
        HttpChallengeCache.remove_challenge_for_url_if_matches(url, None)


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("token_type", [AccessToken, AccessTokenInfo])
@pytest.mark.parametrize("warm", [False, True])
@pytest.mark.parametrize("flow", list(FLOWS))
@pytest.mark.parametrize("replacement_valid", [False, True])
async def test_failed_request_preserves_concurrent_challenge(is_async, token_type, warm, flow, replacement_valid):
    url = get_random_url()
    if warm:
        HttpChallengeCache.set_challenge_for_url(url, HttpChallenge(url, HEADER))
    method = "get_token" if token_type == AccessToken else "get_token_info"
    token_mock = (AsyncMock if is_async else Mock)(return_value=token_type("token", time.time() + 3600))
    credential = Mock(spec_set=[method], **{method: token_mock})
    policy = (AsyncChallengeAuthPolicy if is_async else ChallengeAuthPolicy)(credential)
    if warm:
        policy._token = token_type("token", time.time() + 3600)
    replacement = HttpChallenge(
        url, HEADER if replacement_valid else HEADER.replace("vault.azure.net", "other.example")
    )
    pending = FLOWS[flow].copy()
    failed = Mock(status_code=401, headers={})
    sent = []

    def send(request):
        sent.append(request)
        assert request.body == (b"payload" if warm or len(sent) > 1 else None)
        if not warm and len(sent) == 1:
            assert "Authorization" not in request.headers
        header = pending.pop(0)
        if not pending:
            HttpChallengeCache.set_challenge_for_url(url, replacement)
            failed.headers = {"WWW-Authenticate": header} if header is not None else {}
            return failed
        return Mock(status_code=401, headers={"WWW-Authenticate": header})

    transport = Mock(send=AsyncMock(wraps=send) if is_async else Mock(wraps=send))
    pipeline = (AsyncPipeline if is_async else Pipeline)(
        policies=[
            AsyncRedirectPolicy() if is_async else RedirectPolicy(),
            AsyncRetryPolicy(retry_total=0) if is_async else RetryPolicy(retry_total=0),
            policy,
            SensitiveHeaderCleanupPolicy(),
        ],
        transport=transport,
    )
    request = HttpRequest("PUT", url, content=b"payload")
    if flow == "mismatch":
        with pytest.raises(ValueError):
            if is_async:
                await pipeline.run(request)
            else:
                pipeline.run(request)
    else:
        response = await pipeline.run(request) if is_async else pipeline.run(request)
        assert response.http_response is failed
    assert not pending
    assert policy._token is None
    assert HttpChallengeCache.get_challenge_for_url(url) is replacement
    assert token_mock.call_count == len(FLOWS[flow]) - 1
    if not replacement_valid:
        next_request = HttpRequest("PUT", url, content=b"next")
        with pytest.raises(ValueError):
            if is_async:
                await pipeline.run(next_request)
            else:
                pipeline.run(next_request)
        assert HttpChallengeCache.get_challenge_for_url(url) is None
        assert "Authorization" not in next_request.headers
        assert next_request.body == b"next"
        assert len(sent) == len(FLOWS[flow])
        assert token_mock.call_count == len(FLOWS[flow]) - 1


@pytest.mark.parametrize("target", ["path", "case", "default-port", "other-host", "other-port", "other-scheme"])
def test_eviction_candidate_is_origin_bound(target):
    url = get_random_url()
    parsed = urlparse(url)
    urls = {
        "path": url + "/next",
        "case": url.upper(),
        "default-port": f"https://{parsed.netloc.upper()}:443{parsed.path}",
        "other-host": get_random_url(),
        "other-port": f"https://{parsed.netloc}:8443{parsed.path}",
        "other-scheme": url.replace("https://", "http://"),
    }
    original = HttpChallenge(url, HEADER)
    HttpChallengeCache.set_challenge_for_url(url, original)
    policy = ChallengeAuthPolicy(Mock(spec_set=["get_token"]))
    policy._token = AccessToken("token", time.time() + 3600)
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    policy.on_request(request)
    request.http_request.url = urls[target]
    module = importlib.import_module(ChallengeAuthPolicy.__module__)
    assert module._get_challenge_candidate(request) is (None if target.startswith("other") else original)
    replacement = HttpChallenge(urls[target], HEADER)
    if target.startswith("other"):
        HttpChallengeCache.set_challenge_for_url(urls[target], replacement)
    response = PipelineResponse(request.http_request, Mock(status_code=401, headers={}), request.context)
    assert policy.handle_challenge_flow(request, response) is response
    assert policy._token is None
    assert HttpChallengeCache.get_challenge_for_url(urls[target]) is (
        replacement if target.startswith("other") else None
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("token_type", [AccessToken, AccessTokenInfo])
@pytest.mark.parametrize("failure", ["missing", "malformed", "mismatch"])
async def test_credential_boundary_replacement_survives_failure(is_async, token_type, failure):
    url = get_random_url()
    replacement = HttpChallenge(url, HEADER.replace("tenant", "other"))
    method = "get_token" if token_type == AccessToken else "get_token_info"

    def acquire(*_args, **_kwargs):
        assert HttpChallengeCache.get_challenge_for_url(url) is not None
        HttpChallengeCache.set_challenge_for_url(url, replacement)
        return token_type("token", time.time() + 3600)

    credential = Mock(spec_set=[method], **{method: (AsyncMock if is_async else Mock)(side_effect=acquire)})
    policy = (AsyncChallengeAuthPolicy if is_async else ChallengeAuthPolicy)(credential)
    request = PipelineRequest(HttpRequest("PUT", url, content=b"payload"), PipelineContext(None))
    challenge = PipelineResponse(
        request.http_request, Mock(status_code=401, headers={"WWW-Authenticate": HEADER}), request.context
    )
    if is_async:
        await policy.on_request(request)
        assert await policy.on_challenge(request, challenge)
    else:
        policy.on_request(request)
        assert policy.on_challenge(request, challenge)
    headers = {} if failure == "missing" else {"WWW-Authenticate": FLOWS[failure][0]}
    rejected = PipelineResponse(request.http_request, Mock(status_code=401, headers=headers), request.context)
    if failure == "mismatch":
        with pytest.raises(ValueError):
            if is_async:
                await policy.handle_challenge_flow(request, rejected)
            else:
                policy.handle_challenge_flow(request, rejected)
    else:
        result = (
            await policy.handle_challenge_flow(request, rejected)
            if is_async
            else policy.handle_challenge_flow(request, rejected)
        )
        assert result is rejected
    assert policy._token is None
    assert request.http_request.body == b"payload"
    assert HttpChallengeCache.get_challenge_for_url(url) is replacement


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("path", ["cached-resource", "cached-parse", "fallback-resource", "fallback-parse"])
@pytest.mark.parametrize("replacement_valid", [False, True])
async def test_validation_preserves_replacement_of_evaluated_challenge(is_async, path, replacement_valid):
    url = get_random_url()
    original = HttpChallenge(url, HEADER)
    replacement = HttpChallenge(
        url, HEADER if replacement_valid else HEADER.replace("vault.azure.net", "other.example")
    )

    def scope():
        HttpChallengeCache.set_challenge_for_url(url, replacement)
        return "https://other.example/.default" if path.endswith("resource") else "https://[invalid"

    original.get_scope = Mock(side_effect=scope)
    HttpChallengeCache.set_challenge_for_url(url, original)
    credential = Mock(spec_set=["get_token", "get_token_info"])
    policy = (AsyncChallengeAuthPolicy if is_async else ChallengeAuthPolicy)(credential)
    policy._token = AccessTokenInfo("stale-token", time.time() + 3600)
    request = PipelineRequest(
        HttpRequest("PUT", url, headers={"Authorization": "Bearer stale-token"}, content=b"payload"),
        PipelineContext(None),
    )
    with pytest.raises(ValueError):
        if path.startswith("cached"):
            if is_async:
                await policy.on_request(request)
            else:
                policy.on_request(request)
        else:
            response = PipelineResponse(
                request.http_request,
                Mock(
                    status_code=401,
                    headers={"WWW-Authenticate": 'Bearer authorization="https://authority.net/", claims="e30="'},
                ),
                request.context,
            )
            if is_async:
                await policy.on_challenge(request, response)
            else:
                policy.on_challenge(request, response)
    assert HttpChallengeCache.get_challenge_for_url(url) is replacement
    assert policy._token is None
    assert "Authorization" not in request.http_request.headers
    assert request.http_request.body == b"payload"
    credential.get_token.assert_not_called()
    credential.get_token_info.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_retry_resets_eviction_candidate_to_observed_absence(is_async):
    url = get_random_url()
    original = HttpChallenge(url, HEADER)
    HttpChallengeCache.set_challenge_for_url(url, original)
    policy = (AsyncChallengeAuthPolicy if is_async else ChallengeAuthPolicy)(Mock(spec_set=["get_token"]))
    policy._token = AccessToken("token", time.time() + 3600)
    request = PipelineRequest(HttpRequest("PUT", url, content=b"payload"), PipelineContext(None))
    if is_async:
        await policy.on_request(request)
    else:
        policy.on_request(request)
    HttpChallengeCache.remove_challenge_for_url(url)
    if is_async:
        await policy.on_request(request)
    else:
        policy.on_request(request)
    replacement = HttpChallenge(url, HEADER)
    HttpChallengeCache.set_challenge_for_url(url, replacement)
    response = PipelineResponse(request.http_request, Mock(status_code=401, headers={}), request.context)
    result = (
        await policy.handle_challenge_flow(request, response)
        if is_async
        else policy.handle_challenge_flow(request, response)
    )
    assert result is response
    assert HttpChallengeCache.get_challenge_for_url(url) is replacement
    assert "Authorization" not in request.http_request.headers
    assert not request.http_request.body
