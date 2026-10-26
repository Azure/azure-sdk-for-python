# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore ests
from contextlib import contextmanager
import os
from unittest.mock import patch

import pytest
from msal import TokenCache
from azure.core.pipeline import AsyncPipeline, Pipeline
from azure.core.pipeline.policies import AsyncRetryPolicy, RetryPolicy
from azure.core.pipeline.transport import AsyncHttpTransport
from azure.core.rest import HttpRequest
from azure.identity import WorkloadIdentityCredential
from azure.identity._internal import within_credential_chain, within_dac
from azure.identity._internal.token_binding_transport_mixin import TokenBindingTransportMixin
from azure.identity._internal.token_binding_transport_requests import CustomRequestsTransport
from azure.identity.aio import WorkloadIdentityCredential as AsyncWorkloadIdentityCredential
from azure.identity.aio._internal.token_binding_transport_aiohttp import CustomAioHttpTransport
from azure.identity.aio._internal.token_binding_transport_asyncio import CustomAsyncioRequestsTransport

from proxy_server import TokenProxyHandler, TokenProxyTestServer


@pytest.mark.asyncio
@pytest.mark.parametrize("transport_mode", ["sync", "aiohttp", "asyncio-requests"])
@pytest.mark.parametrize("proxy_path", ["", "/binding", "/api/binding/"])
@pytest.mark.parametrize("retry", [False, True])
@pytest.mark.parametrize("enable_cae", [False, True])
async def test_proxy_token_cache_uses_original_endpoint(transport_mode, proxy_path, retry, enable_cae, tmp_path):
    paths = []
    expected_path = proxy_path.rstrip("/") + "/tenant/oauth2/v2.0/token"

    def handle_request(handler):
        paths.append(handler.path)
        handler.rfile.read(int(handler.headers["Content-Length"]))
        if handler.path != expected_path:
            handler._send_json_response({"error": "wrong path"}, status_code=404)
        elif retry and len(paths) == 1:
            handler._send_json_response({"error": "temporarily unavailable"}, status_code=503)
        else:
            handler._send_json_response({"access_token": "cached-token", "token_type": "Bearer", "expires_in": 3600})

    token_file = tmp_path / "token"
    token_file.write_text("test-assertion", encoding="utf-8")
    credential_type = WorkloadIdentityCredential if transport_mode == "sync" else AsyncWorkloadIdentityCredential
    unavailable_modules = (
        {"azure.identity.aio._internal.token_binding_transport_aiohttp": None}
        if transport_mode == "asyncio-requests"
        else {}
    )
    with patch.object(TokenProxyHandler, "_handle_request", handle_request):
        with TokenProxyTestServer() as server:
            env = {
                "AZURE_KUBERNETES_TOKEN_PROXY": server.base_url + proxy_path,
                "AZURE_KUBERNETES_CA_FILE": server.ca_file,
            }
            with patch.dict(os.environ, env, clear=True), patch.dict("sys.modules", unavailable_modules):
                credential = credential_type(
                    tenant_id="tenant",
                    client_id="client",
                    token_file_path=str(token_file),
                    enable_azure_proxy=True,
                    use_env_settings=False,
                    retry_total=1,
                    retry_backoff_factor=0,
                )
                scope = "https://graph.microsoft.com/.default"
                if isinstance(credential, AsyncWorkloadIdentityCredential):
                    async with credential:
                        first = await credential.get_token(scope, enable_cae=enable_cae)
                        cached = await credential.get_token(scope, enable_cae=enable_cae)
                else:
                    with credential:
                        first = credential.get_token(scope, enable_cae=enable_cae)
                        cached = credential.get_token(scope, enable_cae=enable_cae)

                assert first.token == cached.token == "cached-token"
                cache = credential._client._get_cache(enable_cae=enable_cae)
                entries = list(cache.search(TokenCache.CredentialType.ACCESS_TOKEN))
                assert len(entries) == 1
                assert entries[0]["realm"] == "tenant"
                assert entries[0]["environment"] == "login.microsoftonline.com"
    assert paths == [expected_path] * (2 if retry else 1)


@pytest.mark.asyncio
@pytest.mark.parametrize("transport_mode", ["sync", "aiohttp", "asyncio-requests"])
@pytest.mark.parametrize(
    "options",
    [
        {},
        {
            "connection_timeout": 7,
            "read_timeout": 9,
            "connection_data_block_size": 8192,
            "use_env_settings": False,
        },
        {
            "connection_timeout": 11,
            "read_timeout": 13,
            "connection_data_block_size": 16384,
            "use_env_settings": True,
        },
    ],
    ids=["defaults", "custom-without-env", "custom-with-env"],
)
async def test_credential_forwards_proxy_transport_options(transport_mode, options, tmp_path):
    token_file = tmp_path / "token"
    token_file.write_text("test-assertion", encoding="utf-8")
    credential_type = WorkloadIdentityCredential if transport_mode == "sync" else AsyncWorkloadIdentityCredential
    expected_type = {
        "sync": CustomRequestsTransport,
        "aiohttp": CustomAioHttpTransport,
        "asyncio-requests": CustomAsyncioRequestsTransport,
    }[transport_mode]
    unavailable_modules = (
        {"azure.identity.aio._internal.token_binding_transport_aiohttp": None}
        if transport_mode == "asyncio-requests"
        else {}
    )
    with TokenProxyTestServer() as server:
        env = {
            "AZURE_KUBERNETES_TOKEN_PROXY": server.base_url,
            "AZURE_KUBERNETES_SNI_NAME": "1234.ests.aks",
            "AZURE_KUBERNETES_CA_FILE": server.ca_file,
        }
        if options.get("use_env_settings") is False:
            env["HTTPS_PROXY"] = "http://unreachable.invalid:1"
            env["REQUESTS_CA_BUNDLE"] = "unused-ca.pem"
        with patch.dict(os.environ, env, clear=True), patch.dict("sys.modules", unavailable_modules):
            credential = credential_type(
                tenant_id="tenant",
                client_id="client",
                token_file_path=str(token_file),
                enable_azure_proxy=True,
                connection_verify=False,
                connection_cert="unused-cert.pem",
                session=object(),
                session_owner=False,
                transport=object(),
                sni="unused.example",
                token_proxy_endpoint="https://unused.example",
                ca_file="unused-ca.pem",
                ca_data="unused CA data",
                **options,
            )
            transport = credential._client._pipeline._transport
            assert type(transport) is expected_type
            config = transport.connection_config
            assert config.timeout == options.get("connection_timeout", 300)
            assert config.read_timeout == options.get("read_timeout", 300)
            assert config.data_block_size == options.get("connection_data_block_size", 4096)
            assert config.verify is True
            assert config.cert is None
            assert transport._session_owner is True
            assert transport._sni == env["AZURE_KUBERNETES_SNI_NAME"]
            assert transport._proxy_endpoint == server.base_url
            assert transport._ca_file == server.ca_file

            if isinstance(credential, AsyncWorkloadIdentityCredential):
                async with credential:
                    with patch.object(transport.session, "request", wraps=transport.session.request) as send:
                        token = await credential.get_token("https://graph.microsoft.com/.default")
                    assert transport.session.trust_env == options.get("use_env_settings", True)
            else:
                with credential:
                    with patch.object(transport.session, "request", wraps=transport.session.request) as send:
                        token = credential.get_token("https://graph.microsoft.com/.default")
                    assert transport.session.trust_env == options.get("use_env_settings", True)

            assert token.token
            timeout = send.call_args.kwargs["timeout"]
            if transport_mode == "aiohttp":
                assert timeout.sock_connect == config.timeout
                assert timeout.sock_read == config.read_timeout
            else:
                assert timeout == (config.timeout, config.read_timeout)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "options,expected_timeout",
    [
        ({}, (7, 9)),
        ({"connection_timeout": 11}, (11, 9)),
        ({"read_timeout": 13}, (7, 13)),
        ({"connection_timeout": 11, "read_timeout": 13}, (11, 13)),
        ({"connection_timeout": (17, 19)}, (17, 19)),
    ],
)
async def test_asyncio_requests_timeout_overrides(options, expected_timeout):
    with TokenProxyTestServer() as server:
        async with CustomAsyncioRequestsTransport(
            ca_file=server.ca_file, connection_timeout=7, read_timeout=9, use_env_settings=False
        ) as transport:
            with patch.object(transport.session, "request", wraps=transport.session.request) as send:
                response = await transport.send(HttpRequest("GET", server.base_url + "/health"), **options)
            assert response.status_code == 200
            assert send.call_args.kwargs["timeout"] == expected_timeout
            with pytest.raises(ValueError, match="Cannot set tuple connection_timeout and read_timeout together"):
                await transport.send(
                    HttpRequest("GET", server.base_url + "/health"), connection_timeout=(17, 19), read_timeout=13
                )


@pytest.mark.asyncio
@pytest.mark.parametrize("credential_type", [WorkloadIdentityCredential, AsyncWorkloadIdentityCredential])
@pytest.mark.parametrize("in_dac", [False, True])
@pytest.mark.parametrize("in_chain", [False, True])
async def test_proxy_selection_respects_credential_context(credential_type, in_dac, in_chain):
    dac_context = within_dac.set(in_dac)
    chain_context = within_credential_chain.set(in_chain)
    try:
        with patch.dict(os.environ, {"AZURE_KUBERNETES_TOKEN_PROXY": "https://proxy.example/binding"}, clear=True):
            credential = credential_type(
                tenant_id="tenant-id",
                client_id="client-id",
                token_file_path="token-file",
                enable_azure_proxy=True,
            )
            try:
                transport = credential._client._pipeline._transport
                assert isinstance(transport, TokenBindingTransportMixin) == (not in_dac and not in_chain)
            finally:
                if isinstance(credential, AsyncWorkloadIdentityCredential):
                    await credential.close()
                else:
                    credential.close()
    finally:
        within_credential_chain.reset(chain_context)
        within_dac.reset(dac_context)


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://login.example/tenant/token?q=1", "https://proxy.example/binding/tenant/token?q=1"),
        ("https://proxy.example/binding/tenant/token?q=1", "https://proxy.example/binding/tenant/token?q=1"),
        ("https://PROXY.example:443/binding/tenant/token", "https://PROXY.example:443/binding/tenant/token"),
        ("https://proxy.example/binding", "https://proxy.example/binding"),
        ("https://proxy.example/binding-other/token", "https://proxy.example/binding/binding-other/token"),
        ("https://proxy.example:444/binding/token", "https://proxy.example/binding/binding/token"),
        ("https://proxy.example:0/binding/token", "https://proxy.example/binding/binding/token"),
        ("https://proxy.example.other/binding/token", "https://proxy.example/binding/binding/token"),
        ("http://proxy.example/binding/token", "https://proxy.example/binding/binding/token"),
    ],
)
def test_proxy_url_rewrite_is_idempotent(url, expected):
    transport = TokenBindingTransportMixin(proxy_endpoint="https://proxy.example/binding/")
    request = HttpRequest("POST", url)
    transport._update_request_url(request)
    assert request.url == expected
    transport._update_request_url(request)
    assert request.url == expected


def test_ca_file_atomic_replacement(tmp_path):
    ca_file = tmp_path / "ca.pem"
    ca_file.write_text("old CA", encoding="utf-8")
    old_mtime = ca_file.stat().st_mtime
    replacement = tmp_path / "replacement.pem"
    replacement.write_text("new CA", encoding="utf-8")
    os.utime(replacement, (old_mtime + 60, old_mtime + 60))
    original_open = open

    @contextmanager
    def replace_after_read(*args, **kwargs):
        with original_open(*args, **kwargs) as stream:
            yield stream
        os.replace(replacement, ca_file)

    with patch("builtins.open", replace_after_read):
        transport = TokenBindingTransportMixin(ca_file=str(ca_file))

    assert transport._ca_data == "old CA"
    assert transport._ca_file_mtime == old_mtime
    assert transport._has_ca_file_changed()
    transport._load_ca_file_to_data()
    assert transport._ca_data == "new CA"
    assert transport._ca_file_mtime == ca_file.stat().st_mtime
    assert not transport._has_ca_file_changed()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "transport_type", [CustomRequestsTransport, CustomAioHttpTransport, CustomAsyncioRequestsTransport]
)
@pytest.mark.parametrize("proxy_path", ["", "/binding", "/binding/"])
@pytest.mark.parametrize("recover", [True, False], ids=["recovers", "exhausted"])
async def test_proxy_url_with_pipeline_retry(transport_type, proxy_path, recover):
    paths = []
    bodies = []
    expected_path = proxy_path.rstrip("/") + "/tenant/oauth2/v2.0/token?test=1"
    body = b"client_assertion=test-assertion"

    def handle_request(handler):
        paths.append(handler.path)
        bodies.append(handler.rfile.read(int(handler.headers["Content-Length"])))
        if handler.path != expected_path:
            handler._send_json_response({"error": "wrong path"}, status_code=404)
        elif len(paths) == 1 or not recover:
            handler._send_json_response({"error": "temporarily unavailable"}, status_code=503)
        else:
            handler._send_json_response({"access_token": "test-token"})

    with patch.object(TokenProxyHandler, "_handle_request", handle_request):
        with TokenProxyTestServer() as server:
            transport = transport_type(
                proxy_endpoint=server.base_url + proxy_path, ca_file=server.ca_file, use_env_settings=False
            )
            request = HttpRequest("POST", "https://login.example/tenant/oauth2/v2.0/token?test=1", content=body)
            retry_options = {"retry_total": 1, "retry_status": 1, "retry_backoff_factor": 0}
            if isinstance(transport, AsyncHttpTransport):
                async with AsyncPipeline(transport, policies=[AsyncRetryPolicy(**retry_options)]) as pipeline:
                    response = await pipeline.run(request, retry_on_methods=["POST"])
            else:
                with Pipeline(transport, policies=[RetryPolicy(**retry_options)]) as pipeline:
                    response = pipeline.run(request, retry_on_methods=["POST"])

            assert response.http_response.status_code == (200 if recover else 503)
            assert request.url == server.base_url + expected_path
    assert paths == [expected_path, expected_path]
    assert bodies == [body, body]
