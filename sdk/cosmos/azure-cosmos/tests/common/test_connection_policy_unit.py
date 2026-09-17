# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Client policy normalization using real factories without network startup."""
import asyncio
import inspect
from unittest.mock import MagicMock

import pytest

import azure.cosmos.cosmos_client as sync_client
import azure.cosmos.aio._cosmos_client as async_client
from azure.cosmos._backend._driver_registry import _reset_for_tests
from azure.cosmos._backend.contracts import PreparedClientConfig
from azure.cosmos._connection_policy import resolve_connection_policy_kwargs
from azure.cosmos._retry_options import RetryOptions
from azure.cosmos.documents import ConnectionPolicy, ProxyConfiguration, SSLConfiguration


@pytest.fixture(params=[sync_client, async_client], ids=["sync", "async"])
def client_module(request):
    return request.param


@pytest.fixture
def construct_client(client_module, monkeypatch):
    _reset_for_tests()
    monkeypatch.delenv("COSMOS_BACKEND", raising=False)
    monkeypatch.delenv("COSMOS_RUST_STRICT_ISOLATION", raising=False)
    connection = MagicMock()
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    clients = []

    def construct(*, from_connection_string=False, **kwargs):
        kwargs.setdefault("_backend", "rust")
        if from_connection_string:
            client = client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://policy.invalid;AccountKey=ZmFrZQ==;", **kwargs
            )
        else:
            client = client_module.CosmosClient("https://policy.invalid", "ZmFrZQ==", **kwargs)
        clients.append(client)
        return client, connection.call_args.kwargs["connection_policy"]

    yield construct
    for client in clients:
        if client._backend.name == "rust":
            result = client._backend.close()
            if inspect.isawaitable(result):
                asyncio.run(result)
    _reset_for_tests()


def configured_policy():
    policy = ConnectionPolicy()
    policy.PreferredLocations = ["West US", "East US"]
    policy.ExcludedLocations = ["Central US"]
    policy.RetryOptions = RetryOptions(max_retry_attempt_count=3, max_wait_time_in_seconds=12)
    return policy


def test_grouped_settings_match_direct_keywords(construct_client):
    policy = configured_policy()
    grouped, legacy = construct_client(connection_policy=policy)
    direct, _ = construct_client(
        preferred_locations=["West US", "East US"], excluded_locations=["Central US"],
        retry_throttle_total=3, retry_throttle_backoff_max=12,
    )
    assert grouped._backend._client_config == direct._backend._client_config == PreparedClientConfig(
        preferred_locations=("West US", "East US"), excluded_locations=("Central US",),
        throttling_max_retry_count=3, throttling_max_retry_wait_time_seconds=12,
    )
    assert legacy.PreferredLocations == policy.PreferredLocations
    assert legacy.ExcludedLocations == policy.ExcludedLocations
    assert legacy.RetryOptions.MaxRetryAttemptCount == 3
    assert legacy.RetryOptions.MaxWaitTimeInSeconds == 12


@pytest.mark.parametrize("policy", [None, ConnectionPolicy()])
def test_default_policy_does_not_pin_rust_settings(construct_client, policy):
    client, _ = construct_client(connection_policy=policy)
    assert client._backend._client_config is None


def test_connection_string_factory_preserves_grouped_settings(construct_client):
    client, legacy = construct_client(
        from_connection_string=True, connection_policy=configured_policy()
    )
    assert client._backend._client_config.preferred_locations == ("West US", "East US")
    assert legacy.RetryOptions.MaxRetryAttemptCount == 3


def test_policy_zero_retry_limits_are_not_replaced_by_defaults(construct_client):
    policy = ConnectionPolicy()
    policy.RetryOptions = RetryOptions(max_retry_attempt_count=0, max_wait_time_in_seconds=0)
    client, legacy = construct_client(connection_policy=policy)
    assert client._backend._client_config.throttling_max_retry_count == 0
    assert client._backend._client_config.throttling_max_retry_wait_time_seconds == 0
    assert legacy.RetryOptions.MaxRetryAttemptCount == 0
    assert legacy.RetryOptions.MaxWaitTimeInSeconds == 0


@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("overrides,count,wait", [
    ({"retry_total": 7, "retry_backoff_max": 20}, 7, 20),
    ({"retry_total": 0, "retry_backoff_max": 0}, 0, 0),
    ({"retry_total": 7, "retry_backoff_max": 20,
      "retry_throttle_total": 0, "retry_throttle_backoff_max": 0}, 0, 0),
    ({"retry_total": 7, "retry_throttle_total": None,
      "retry_backoff_max": 20, "retry_throttle_backoff_max": None}, 7, 20),
    ({"retry_throttle_total": None, "retry_throttle_backoff_max": None}, 3, 12),
])
def test_retry_precedence_includes_zero(construct_client, backend, overrides, count, wait):
    client, legacy = construct_client(
        _backend=backend, connection_policy=configured_policy(), **overrides
    )
    if backend == "rust":
        assert client._backend._client_config.throttling_max_retry_count == count
        assert client._backend._client_config.throttling_max_retry_wait_time_seconds == wait
    assert legacy.RetryOptions.MaxRetryAttemptCount == count
    assert legacy.RetryOptions.MaxWaitTimeInSeconds == wait


@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("locations", [[], ["North Europe"]])
def test_region_keywords_override_policy_including_empty(construct_client, backend, locations):
    client, legacy = construct_client(
        _backend=backend, connection_policy=configured_policy(),
        preferred_locations=locations, excluded_locations=[],
    )
    assert legacy.PreferredLocations == locations
    assert legacy.ExcludedLocations == []
    if backend == "rust":
        assert client._backend._client_config.preferred_locations == tuple(locations)
        assert client._backend._client_config.excluded_locations == ()


def test_policy_timeouts_still_resolve_with_keyword_and_alias_precedence(construct_client):
    policy = configured_policy()
    policy.RequestTimeout = 4
    policy.ReadTimeout = 20
    client, legacy = construct_client(
        connection_policy=policy, request_timeout=2000, connection_timeout=3, read_timeout=25
    )
    config = client._backend._client_config
    assert config.connection_timeout_seconds == legacy.RequestTimeout == 2
    assert config.read_timeout_seconds == legacy.ReadTimeout == 25
    assert policy.RequestTimeout == 4
    assert policy.ReadTimeout == 20


@pytest.mark.parametrize("setting", ["proxy", "ca", "cert", "key", "disable_verification"])
def test_nested_unsupported_transport_rejected_before_startup(
    construct_client, client_module, setting
):
    policy = ConnectionPolicy()
    if setting == "proxy":
        policy.ProxyConfiguration = ProxyConfiguration()
        policy.ProxyConfiguration.Host = "proxy.invalid"
        expected = "proxy_config"
    elif setting == "disable_verification":
        policy.DisableSSLVerification = True
        expected = "connection_verify"
    else:
        policy.SSLConfiguration = SSLConfiguration()
        attribute = {"ca": "SSLCaCerts", "cert": "SSLCertFile", "key": "SSLKeyFile"}[setting]
        setattr(policy.SSLConfiguration, attribute, "test-certificate.pem")
        expected = "ssl_config"
    with pytest.raises(ValueError, match=expected):
        construct_client(connection_policy=policy)
    client_module.CosmosClientConnection.assert_not_called()
    construct_client(proxy_allowed=False)


def test_explicit_transport_overrides_clear_nested_settings(construct_client):
    policy = ConnectionPolicy()
    policy.ProxyConfiguration = ProxyConfiguration()
    policy.SSLConfiguration = SSLConfiguration()
    policy.SSLConfiguration.SSLCaCerts = "test-ca.pem"
    policy.DisableSSLVerification = True
    client, legacy = construct_client(
        connection_policy=policy, proxy_config=None, ssl_config=None, connection_verify=True
    )
    assert client._backend._client_config is None
    assert legacy.ProxyConfiguration is None
    assert legacy.SSLConfiguration is None
    assert legacy.DisableSSLVerification is False
    assert policy.SSLConfiguration.SSLCaCerts == "test-ca.pem"
    assert policy.DisableSSLVerification is True


def test_core_python_retains_nested_transport_and_does_not_mutate_caller(construct_client):
    policy = configured_policy()
    policy.ProxyConfiguration = ProxyConfiguration()
    policy.ProxyConfiguration.Host = "proxy.invalid"
    policy.SSLConfiguration = SSLConfiguration()
    policy.SSLConfiguration.SSLCertFile = "original-cert.pem"
    policy.DisableSSLVerification = True
    _, legacy = construct_client(
        _backend="core-python", connection_policy=policy,
        preferred_locations=["North Europe"], retry_throttle_total=0,
        connection_cert="override-cert.pem",
    )
    assert legacy.ProxyConfiguration.Host == "proxy.invalid"
    assert legacy.SSLConfiguration.SSLCertFile == "override-cert.pem"
    assert legacy.DisableSSLVerification is True
    assert legacy is not policy
    assert legacy.SSLConfiguration is not policy.SSLConfiguration
    assert legacy.RetryOptions is not policy.RetryOptions
    assert policy.PreferredLocations == ["West US", "East US"]
    assert policy.RetryOptions.MaxRetryAttemptCount == 3
    assert policy.SSLConfiguration.SSLCertFile == "original-cert.pem"


def test_direct_ssl_object_is_not_mutated(construct_client):
    ssl = SSLConfiguration()
    ssl.SSLCertFile = "original-cert.pem"
    _, legacy = construct_client(
        _backend="core-python", ssl_config=ssl, connection_cert="override-cert.pem"
    )
    assert ssl.SSLCertFile == "original-cert.pem"
    assert legacy.SSLConfiguration.SSLCertFile == "override-cert.pem"


def test_mutable_policy_settings_are_snapshotted(construct_client):
    policy = configured_policy()
    client, legacy = construct_client(connection_policy=policy)
    legacy.PreferredLocations.append("North Europe")
    legacy.ExcludedLocations.clear()
    legacy.RetryOptions._max_retry_attempt_count = 1
    assert policy.PreferredLocations == ["West US", "East US"]
    assert policy.ExcludedLocations == ["Central US"]
    assert policy.RetryOptions.MaxRetryAttemptCount == 3
    assert client._backend._client_config.preferred_locations == ("West US", "East US")


def test_normalization_does_not_modify_input_and_is_idempotent():
    policy = configured_policy()
    kwargs = {"connection_policy": policy, "retry_total": 0}
    original = dict(vars(policy.RetryOptions))
    resolved = resolve_connection_policy_kwargs(kwargs)
    assert kwargs == {"connection_policy": policy, "retry_total": 0}
    assert vars(policy.RetryOptions) == original
    assert resolve_connection_policy_kwargs(resolved) == resolved


def test_invalid_policy_rejected_before_startup(construct_client, client_module):
    with pytest.raises(TypeError, match="connection_policy"):
        construct_client(connection_policy={"preferred_locations": ["West US"]})
    client_module.CosmosClientConnection.assert_not_called()
