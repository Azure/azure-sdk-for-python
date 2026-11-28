# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for the connection settings given when a client is created.

A caller can give these settings in two ways: as fields on a connection
policy, or as keywords on ``CosmosClient``. Both ways must give the same
result. When both give the same setting, the keyword wins.

These tests check three rules:

- Zero is a real value. It must not be treated as "not set".
- The caller's connection policy is never changed, because they may use it
  for another client.
- A setting the client cannot apply is refused with ``TypeError`` when the
  client is created, instead of being ignored.

Terms used in this file:

- connection policy: a ``ConnectionPolicy`` object that groups settings such
  as preferred regions and retry limits.
- compiled module: the part of the SDK that sends most requests to the service.
- compiled-module settings: the settings the client passes to the compiled
  module (``client._adapter._client_config``). It is ``None`` when the caller
  set nothing.
- connection object: the client's internal ``CosmosClientConnection``. Most
  tests replace it with a mock.
- built policy: the copy of the connection policy that the client makes and
  passes to its connection object.
- sender choice: the private ``_backend`` argument, or the ``COSMOS_BACKEND``
  environment variable, picks the code that sends requests. These tests choose
  ``"rust"``, the compiled module. The argument wins over the variable.
- throttled: the service replied 429 (too many requests) and the SDK waits
  before retrying.
- throttled retry count: how many times the SDK retries a throttled request
  (``retry_throttle_total``, or ``RetryOptions.MaxRetryAttemptCount``).
- throttled wait limit: how many seconds the SDK normally spends waiting to
  retry throttled requests (``throttle_retry_wait_threshold_seconds``, or
  ``RetryOptions.MaxWaitTimeInSeconds``).
- hedging: the ``availability_strategy`` option. When it is on, a request that
  is slow in one region may also be sent to another region.
- pipeline: the chain of steps (from ``azure-core``) that the connection
  object uses to send each HTTP request.
- transport: the last pipeline step, which actually sends the HTTP request.

Every test runs against both the sync and async client. No test contacts a
Cosmos DB account.
"""
import asyncio
from copy import copy, deepcopy
import inspect
from unittest.mock import MagicMock

import pytest

import azure.cosmos.cosmos_client as sync_client
import azure.cosmos.aio._cosmos_client as async_client
from azure.cosmos._backend.contracts import PreparedClientConfig
from azure.cosmos._connection_policy import resolve_connection_policy_kwargs
from azure.cosmos._retry_options import RetryOptions
from azure.cosmos.documents import ConnectionPolicy


@pytest.fixture(params=[sync_client, async_client], ids=["sync", "async"])
def client_module(request):
    """Run each test with the sync client module and then the async one.

    The two clients have separate code that reads the same options.
    """
    return request.param


@pytest.fixture
def construct_client(client_module, monkeypatch):
    """Return a function that creates a real client and returns it with its built policy.

    Most tests compare the compiled-module settings with the built policy, so the
    function returns both. The connection object is replaced with a mock, and the
    account address and key are fake. ``_backend`` is ``"rust"`` unless the test
    passes its own. ``COSMOS_BACKEND`` is removed first so the outside environment
    cannot change the result.

    Every client is closed at the end of the test, so it does not hold resources
    for the rest of the run.
    """
    monkeypatch.delenv("COSMOS_BACKEND", raising=False)
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
        if client._adapter.name == "rust":
            result = client._adapter.close()
            if inspect.isawaitable(result):
                asyncio.run(result)


def configured_policy():
    """Return a connection policy where every setting differs from its default.

    The SDK treats a value equal to the default as "not set". If this policy used
    default values, a test could pass even when a setting was lost.
    """
    policy = ConnectionPolicy()
    policy.PreferredLocations = ["West US", "East US"]
    policy.ExcludedLocations = ["Central US"]
    policy.RetryOptions = RetryOptions(max_retry_attempt_count=3, max_wait_time_in_seconds=12)
    return policy


def test_policy_and_keywords_give_same_settings_rust(construct_client):
    """A connection policy and the matching keywords give the same settings.

    Two clients are created, one each way, with the same four settings: preferred
    regions, excluded regions, throttled retry count and throttled wait limit. The
    compiled-module settings of both clients must equal each other and a
    written-out expected value. The built policy must also hold all four values.
    """
    policy = configured_policy()
    policy_client, built_policy = construct_client(connection_policy=policy)
    keyword_client, _ = construct_client(
        preferred_locations=["West US", "East US"], excluded_locations=["Central US"],
        retry_throttle_total=3, throttle_retry_wait_threshold_seconds=12,
    )
    assert policy_client._adapter._client_config == keyword_client._adapter._client_config == PreparedClientConfig(
        preferred_locations=("West US", "East US"), excluded_locations=("Central US",),
        throttling_max_retry_count=3, throttling_max_retry_wait_time_seconds=12,
    )
    assert built_policy.PreferredLocations == policy.PreferredLocations
    assert built_policy.ExcludedLocations == policy.ExcludedLocations
    assert built_policy.RetryOptions.MaxRetryAttemptCount == 3
    assert built_policy.RetryOptions.MaxWaitTimeInSeconds == 12


@pytest.mark.parametrize("policy", [None, ConnectionPolicy()])
def test_default_policy_sets_nothing_rust(construct_client, policy):
    """No policy and a default policy both leave the compiled-module settings as ``None``.

    The client creates a policy even when the caller gives none, so a default
    policy must not count as a request. Otherwise every client would pass every
    setting, and the compiled module could not use its own defaults.
    """
    client, _ = construct_client(connection_policy=policy)
    assert client._adapter._client_config is None


@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("selection", ["keyword", "environment"])
@pytest.mark.parametrize("grouped", [False, True], ids=["keyword-option", "policy-field"])
@pytest.mark.parametrize("option,attribute", [
    ("enable_endpoint_discovery", "EnableEndpointDiscovery"),
    ("multiple_write_locations", "UseMultipleWriteLocations"),
])
@pytest.mark.parametrize("value", [True, False, None, "unused"])
def test_routing_options_are_refused_before_client_starts_rust(
    client_module, monkeypatch, from_connection_string, selection, grouped, option, attribute, value,
):
    """``enable_endpoint_discovery`` and ``multiple_write_locations`` are refused.

    They are refused whether given as keywords or as policy fields. The compiled
    module picks regions from the account's settings, so these options cannot be
    applied. Any value is refused, even ``None``. The error must come before the
    connection object or the sender is created, and the caller's policy must not
    change. The sender choice is given both ways: as the argument and as the
    environment variable.
    """
    policy = ConnectionPolicy()
    if grouped:
        setattr(policy, attribute, value)
        kwargs = {"connection_policy": policy}
        rejected_name = rf"connection_policy\.{attribute}"
    else:
        kwargs = {option: value}
        rejected_name = option
    policy_before = dict(vars(policy))
    if selection == "environment":
        monkeypatch.setenv("COSMOS_BACKEND", "rust")
    else:
        monkeypatch.setenv("COSMOS_BACKEND", "core-python")
        kwargs["_backend"] = "rust"
    connection = MagicMock()
    sender_factory = MagicMock()
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    factory_name = "make_async_backend" if client_module is async_client else "make_backend"
    monkeypatch.setattr(client_module, factory_name, sender_factory)
    with pytest.raises(TypeError, match=rejected_name + " is not supported by Rust-backed clients"):
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://policy.invalid;AccountKey=ZmFrZQ==;", **kwargs,
            )
        else:
            client_module.CosmosClient("https://policy.invalid", "ZmFrZQ==", **kwargs)
    connection.assert_not_called()
    sender_factory.assert_not_called()
    assert vars(policy) == policy_before


@pytest.mark.parametrize("attribute,default", [
    ("EnableEndpointDiscovery", True), ("UseMultipleWriteLocations", False),
])
@pytest.mark.parametrize("duplicate", [copy, deepcopy])
def test_routing_field_set_to_default_is_refused_even_in_copy_rust(
    construct_client, attribute, default, duplicate,
):
    """Setting a routing field on a policy is refused even when the value equals the default.

    The SDK checks whether the field was set, not its value. A copy made with
    ``copy`` or ``deepcopy`` keeps the field, so the copy is refused too.
    """
    policy = ConnectionPolicy()
    setattr(policy, attribute, default)
    with pytest.raises(TypeError, match=attribute):
        construct_client(connection_policy=duplicate(policy))


@pytest.mark.parametrize("attribute,value", [
    ("EnableEndpointDiscovery", True), ("EnableEndpointDiscovery", False),
    ("UseMultipleWriteLocations", False), ("UseMultipleWriteLocations", True),
])
def test_routing_field_set_by_policy_subclass_is_refused_rust(construct_client, attribute, value):
    """A routing field set as a class attribute on a ``ConnectionPolicy`` subclass is refused too.
    """
    policy = type("RoutingPolicy", (ConnectionPolicy,), {attribute: value})()
    with pytest.raises(TypeError, match=attribute):
        construct_client(connection_policy=policy)


def test_built_policy_can_create_another_client_rust(construct_client):
    """A built policy can be given to a second client.

    Creating the first client must not add routing fields to the built policy
    or change the caller's policy. The second client gets the same regions.
    """
    policy = configured_policy()
    policy_before = dict(vars(policy))
    _, built_policy = construct_client(connection_policy=policy)
    # The built policy holds a connection retry object, which the async client
    # refuses. Clear it so the same steps work for both clients.
    built_policy.ConnectionRetryConfiguration = None
    client, _ = construct_client(connection_policy=built_policy)
    assert client._adapter._client_config.preferred_locations == ("West US", "East US")
    assert client._adapter._client_config.excluded_locations == ("Central US",)
    assert vars(policy) == policy_before
    assert "EnableEndpointDiscovery" not in vars(built_policy)
    assert "UseMultipleWriteLocations" not in vars(built_policy)


@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("selection", ["keyword", "environment"])
@pytest.mark.parametrize(
    "grouped,value",
    [
        (False, None),
        (False, 0),
        (False, 500),
        (False, False),
        (False, "500"),
        (True, 0),
        (True, 500),
        (True, False),
        (True, "500"),
    ],
)
def test_fixed_throttled_retry_wait_is_refused_rust(
    client_module, monkeypatch, from_connection_string, selection, grouped, value
):
    """A fixed wait between throttled retries is refused.

    It can be given as the ``retry_fixed_interval`` keyword or as the policy field
    ``RetryOptions.FixedRetryIntervalInMilliseconds``. The compiled module has no
    setting for a fixed wait, so it cannot be applied. The keyword is refused with
    any value, even ``None``; the policy field is refused when it is not ``None``.
    The error must come before the connection object or the sender is created, and
    the caller's retry options must not change.
    """
    policy = configured_policy()
    if grouped:
        policy.RetryOptions = RetryOptions(fixed_retry_interval_in_milliseconds=value)
        kwargs = {"connection_policy": policy}
    else:
        kwargs = {"retry_fixed_interval": value}
    retry_options_before = dict(vars(policy.RetryOptions))
    if selection == "environment":
        monkeypatch.setenv("COSMOS_BACKEND", "rust")
    else:
        monkeypatch.setenv("COSMOS_BACKEND", "core-python")
        kwargs["_backend"] = "rust"
    connection = MagicMock()
    sender_factory = MagicMock()
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    factory_name = "make_async_backend" if client_module is async_client else "make_backend"
    monkeypatch.setattr(client_module, factory_name, sender_factory)
    with pytest.raises(TypeError, match="Fixed throttle retry intervals are not supported by Rust-backed clients"):
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://policy.invalid;AccountKey=ZmFrZQ==;", **kwargs
            )
        else:
            client_module.CosmosClient("https://policy.invalid", "ZmFrZQ==", **kwargs)
    sender_factory.assert_not_called()
    connection.assert_not_called()
    assert vars(policy.RetryOptions) == retry_options_before


@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("selection", ["keyword", "environment"])
@pytest.mark.parametrize("keyword", [
    "retry_connect", "retry_read", "connection_retry_policy", "retry_mode", "retry_backoff_factor",
    "retry_total", "retry_backoff_max", "retry_status", "retry_on_status_codes", "retry_write",
])
@pytest.mark.parametrize("value", [None, 0, 2, False, "2", MagicMock()])
def test_connection_retry_keywords_are_refused_rust(
    client_module, monkeypatch, from_connection_string, selection, keyword, value
):
    """These retry keywords are refused with any value, even ``None``.

    They are: connection and read retry counts, a custom retry policy, retry delay
    settings, the general retry count and wait (``retry_total`` and
    ``retry_backoff_max``), the status codes to retry, and ``retry_write``. The
    compiled module chooses its own retries and has no matching setting for any of
    them. Instead of ``retry_total`` and ``retry_backoff_max``, use the throttled
    retry count and throttled wait limit keywords. The error must come before the
    built policy, the sender or the connection object is created.
    """
    kwargs = {keyword: value}
    if selection == "environment":
        monkeypatch.setenv("COSMOS_BACKEND", "rust")
    else:
        monkeypatch.setenv("COSMOS_BACKEND", "core-python")
        kwargs["_backend"] = "rust"
    connection = MagicMock()
    sender_factory = MagicMock()
    build_policy = MagicMock()
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    monkeypatch.setattr(client_module, "_build_connection_policy", build_policy)
    factory_name = "make_async_backend" if client_module is async_client else "make_backend"
    monkeypatch.setattr(client_module, factory_name, sender_factory)
    with pytest.raises(TypeError, match=keyword + " is not supported by Rust-backed clients; omit this keyword"):
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://policy.invalid;AccountKey=ZmFrZQ==;", **kwargs
            )
        else:
            client_module.CosmosClient("https://policy.invalid", "ZmFrZQ==", **kwargs)
    build_policy.assert_not_called()
    sender_factory.assert_not_called()
    connection.assert_not_called()


@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("selection", ["keyword", "environment"])
@pytest.mark.parametrize("value", [None, 0, 2])
def test_hedging_concurrency_options_are_refused_rust(
    client_module, monkeypatch, from_connection_string, selection, value,
):
    """The options that control how hedged requests run are refused with any value, even ``None``.

    The sync client's option is ``availability_strategy_executor`` and the async
    client's is ``availability_strategy_max_concurrency``. The compiled module runs
    hedged requests itself. The error must come before the sender, the connection
    object or the built policy is created.
    """
    keyword = (
        "availability_strategy_max_concurrency" if client_module is async_client
        else "availability_strategy_executor"
    )
    kwargs = {keyword: value}
    monkeypatch.setenv("COSMOS_BACKEND", "rust" if selection == "environment" else "core-python")
    if selection == "keyword":
        kwargs["_backend"] = "rust"
    factory_name = "make_async_backend" if client_module is async_client else "make_backend"
    sender_factory = MagicMock()
    connection = MagicMock()
    build_policy = MagicMock()
    monkeypatch.setattr(client_module, factory_name, sender_factory)
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    monkeypatch.setattr(client_module, "_build_connection_policy", build_policy)
    with pytest.raises(TypeError, match=keyword + " is not supported by Rust-backed clients"):
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://policy.invalid;AccountKey=ZmFrZQ==;", **kwargs,
            )
        else:
            client_module.CosmosClient("https://policy.invalid", "ZmFrZQ==", **kwargs)
    sender_factory.assert_not_called()
    connection.assert_not_called()
    build_policy.assert_not_called()


@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("selection", ["keyword", "environment"])
@pytest.mark.parametrize("custom_policy", [0, False, 4, MagicMock()])
def test_async_client_refuses_policy_connection_retry_rust(
    monkeypatch, from_connection_string, selection, custom_policy,
):
    """The async client refuses a policy whose ``ConnectionRetryConfiguration`` is not ``None``.

    Even ``0`` and ``False`` are refused. The compiled module chooses its own
    retries, so a retry setting on the policy cannot be applied. The error must
    come before the sender, the connection object or the built policy is created,
    and the caller's policy must keep its value. The sync client does not read this
    field from the caller's policy, so only the async client is tested.
    """
    policy = ConnectionPolicy()
    policy.ConnectionRetryConfiguration = custom_policy
    kwargs = {"connection_policy": policy}
    monkeypatch.setenv("COSMOS_BACKEND", "rust" if selection == "environment" else "core-python")
    if selection == "keyword":
        kwargs["_backend"] = "rust"
    sender_factory = MagicMock()
    connection = MagicMock()
    build_policy = MagicMock()
    monkeypatch.setattr(async_client, "make_async_backend", sender_factory)
    monkeypatch.setattr(async_client, "CosmosClientConnection", connection)
    monkeypatch.setattr(async_client, "_build_connection_policy", build_policy)
    with pytest.raises(TypeError, match=r"connection_policy\.ConnectionRetryConfiguration"):
        if from_connection_string:
            async_client.CosmosClient.from_connection_string(
                "AccountEndpoint=https://policy.invalid;AccountKey=ZmFrZQ==;", **kwargs,
            )
        else:
            async_client.CosmosClient("https://policy.invalid", "ZmFrZQ==", **kwargs)
    sender_factory.assert_not_called()
    connection.assert_not_called()
    build_policy.assert_not_called()
    assert policy.ConnectionRetryConfiguration is custom_policy


def test_connection_string_keeps_policy_settings_rust(construct_client):
    """Creating a client with ``from_connection_string`` keeps the policy's settings.

    It must behave just as the constructor does. The compiled-module settings must
    have the policy's regions, and the built policy must have its throttled retry
    count.
    """
    client, built_policy = construct_client(
        from_connection_string=True, connection_policy=configured_policy()
    )
    assert client._adapter._client_config.preferred_locations == ("West US", "East US")
    assert built_policy.RetryOptions.MaxRetryAttemptCount == 3


@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("seconds", [0, 2.5, 10.0, None])
def test_throttled_wait_limit_reaches_both_settings_rust(construct_client, from_connection_string, seconds):
    """The throttled wait limit keyword reaches the compiled-module settings and the built policy.

    ``0`` stays ``0``. ``None`` means not set, so the policy's value of 12 is
    used. The throttled retry count keyword (5) is checked too.
    """
    client, built_policy = construct_client(
        from_connection_string=from_connection_string,
        connection_policy=configured_policy(),
        retry_throttle_total=5,
        throttle_retry_wait_threshold_seconds=seconds,
    )
    expected = 12 if seconds is None else seconds
    assert client._adapter._client_config.throttling_max_retry_count == 5
    assert client._adapter._client_config.throttling_max_retry_wait_time_seconds == expected
    assert built_policy.RetryOptions.MaxWaitTimeInSeconds == expected


@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize(
    "options",
    [
        {"retry_throttle_backoff_max": None},
        {"retry_throttle_backoff_max": 2.5},
        {"retry_throttle_backoff_max": 0, "throttle_retry_wait_threshold_seconds": 1},
        {"request_options": {"retry_throttle_backoff_max": None}},
        {"feed_options": {"retry_throttle_backoff_max": None}},
        {"options": {"retry_throttle_backoff_max": None}},
    ],
)
def test_old_throttled_wait_keyword_name_is_refused_rust(
    client_module,
    monkeypatch,
    from_connection_string,
    options,
):
    """The old keyword ``retry_throttle_backoff_max`` is refused, and the message gives the new name.

    The new name is ``throttle_retry_wait_threshold_seconds``. The old one is
    refused with any value, even ``None``, and also when it is inside
    ``request_options``, ``feed_options`` or ``options``. The error must come
    before the sender or the connection object is created.
    """
    connection = MagicMock()
    sender_factory = MagicMock()
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    factory_name = "make_async_backend" if client_module is async_client else "make_backend"
    monkeypatch.setattr(client_module, factory_name, sender_factory)
    with pytest.raises(
        TypeError,
        match="retry_throttle_backoff_max has been renamed; use throttle_retry_wait_threshold_seconds",
    ):
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://policy.invalid;AccountKey=ZmFrZQ==;",
                _backend="rust",
                **options,
            )
        else:
            client_module.CosmosClient(
                "https://policy.invalid",
                "ZmFrZQ==",
                _backend="rust",
                **options,
            )
    sender_factory.assert_not_called()
    connection.assert_not_called()


def test_policy_zero_retry_limits_are_kept_rust(construct_client):
    """A policy with a throttled retry count and wait limit of ``0`` keeps both zeros.

    Neither the compiled-module settings nor the built policy may replace them
    with defaults.
    """
    policy = ConnectionPolicy()
    policy.RetryOptions = RetryOptions(max_retry_attempt_count=0, max_wait_time_in_seconds=0)
    client, built_policy = construct_client(connection_policy=policy)
    assert client._adapter._client_config.throttling_max_retry_count == 0
    assert client._adapter._client_config.throttling_max_retry_wait_time_seconds == 0
    assert built_policy.RetryOptions.MaxRetryAttemptCount == 0
    assert built_policy.RetryOptions.MaxWaitTimeInSeconds == 0


@pytest.mark.parametrize("overrides,count,wait", [
    ({"retry_throttle_total": 0, "throttle_retry_wait_threshold_seconds": 0}, 0, 0),
    ({"retry_throttle_total": 7, "throttle_retry_wait_threshold_seconds": 20}, 7, 20),
    ({"retry_throttle_total": None, "throttle_retry_wait_threshold_seconds": None}, 3, 12),
])
def test_retry_keywords_win_over_policy_including_zero_rust(construct_client, overrides, count, wait):
    """The throttled retry count and wait limit keywords win over the policy, even when they are ``0``.

    Zero must not be treated as "not set". ``None`` means not set, so the
    policy's values (3 and 12) are used.
    """
    client, built_policy = construct_client(connection_policy=configured_policy(), **overrides)
    assert client._adapter._client_config.throttling_max_retry_count == count
    assert client._adapter._client_config.throttling_max_retry_wait_time_seconds == wait
    assert built_policy.RetryOptions.MaxRetryAttemptCount == count
    assert built_policy.RetryOptions.MaxWaitTimeInSeconds == wait


@pytest.mark.parametrize("locations", [[], ["North Europe"]])
def test_region_keywords_win_over_policy_even_when_empty_rust(construct_client, locations):
    """Region keywords win over the policy, even when the keyword is an empty list.

    An empty list means the caller wants no regions in that list. That is
    different from "not set", so it must not fall back to the policy's regions.
    Both an empty list and a one-region list are tried.
    """
    client, built_policy = construct_client(
        connection_policy=configured_policy(), preferred_locations=locations, excluded_locations=[],
    )
    assert built_policy.PreferredLocations == locations
    assert built_policy.ExcludedLocations == []
    assert client._adapter._client_config.preferred_locations == tuple(locations)
    assert client._adapter._client_config.excluded_locations == ()


@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize(
    "option",
    ["proxy_config", "proxies", "ssl_config", "connection_verify", "connection_cert", "transport"],
)
@pytest.mark.parametrize("value", [None, True, False, {}, "alpha-bank-ca.pem"])
def test_removed_network_options_are_refused_rust(
    client_module, monkeypatch, from_connection_string, option, value,
):
    """Proxy, secure connection (TLS) and transport options are no longer accepted.

    They are refused with any value, even ``None``, and the error says the option
    has been removed. The error must come before the sender or the connection
    object is created.
    """
    connection = MagicMock()
    sender_factory = MagicMock()
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    factory_name = "make_async_backend" if client_module is async_client else "make_backend"
    monkeypatch.setattr(client_module, factory_name, sender_factory)
    kwargs = {"_backend": "rust", option: value}
    with pytest.raises(TypeError, match=rf"{option} has been removed"):
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://alpha-bank-account.invalid;AccountKey=ZmFrZQ==;", **kwargs,
            )
        else:
            client_module.CosmosClient("https://alpha-bank-account.invalid", "ZmFrZQ==", **kwargs)
    connection.assert_not_called()
    sender_factory.assert_not_called()


@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("attribute", ["ProxyConfiguration", "SSLConfiguration", "DisableSSLVerification"])
@pytest.mark.parametrize("value", [None, False, object()])
def test_removed_policy_fields_are_refused_rust(
    client_module, monkeypatch, from_connection_string, attribute, value,
):
    """A policy with ``ProxyConfiguration``, ``SSLConfiguration`` or ``DisableSSLVerification`` is refused.

    It is refused with any value, even ``None``. The connection object must not
    be created, and the caller's policy must keep its value.
    """
    policy = ConnectionPolicy()
    setattr(policy, attribute, value)
    connection = MagicMock()
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    with pytest.raises(TypeError, match=rf"connection_policy\.{attribute} has been removed"):
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://alpha-bank-account.invalid;AccountKey=ZmFrZQ==;",
                connection_policy=policy, _backend="rust",
            )
        else:
            client_module.CosmosClient(
                "https://alpha-bank-account.invalid", "ZmFrZQ==", connection_policy=policy, _backend="rust",
            )
    connection.assert_not_called()
    assert getattr(policy, attribute) is value


@pytest.mark.parametrize("nested", ["request_options", "feed_options", "options"])
@pytest.mark.parametrize(
    "option",
    ["proxy_config", "proxies", "ssl_config", "connection_verify", "connection_cert", "transport"],
)
def test_removed_network_options_inside_option_dicts_are_refused_rust(nested, option):
    """The removed network options are refused even inside ``request_options``, ``feed_options`` or ``options``.
    """
    from azure.cosmos._backend.capabilities import reject_removed_options

    with pytest.raises(TypeError, match=rf"{option} has been removed"):
        reject_removed_options({nested: {option: None}})


@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("option", ["raw_request_hook", "raw_response_hook"])
@pytest.mark.parametrize("value", [None, False, lambda _message: None])
def test_removed_raw_hooks_are_refused_rust(
    client_module, monkeypatch, from_connection_string, option, value,
):
    """``raw_request_hook`` and ``raw_response_hook`` are refused with any value, even ``None``.

    The error must come before the sender or the connection object is created.
    """
    connection = MagicMock()
    sender_factory = MagicMock()
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    factory_name = "make_async_backend" if client_module is async_client else "make_backend"
    monkeypatch.setattr(client_module, factory_name, sender_factory)
    kwargs = {"_backend": "rust", option: value}
    with pytest.raises(TypeError, match=rf"{option} has been removed"):
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://policy.invalid;AccountKey=ZmFrZQ==;", **kwargs,
            )
        else:
            client_module.CosmosClient("https://policy.invalid", "ZmFrZQ==", **kwargs)
    connection.assert_not_called()
    sender_factory.assert_not_called()


def test_removed_configuration_classes_are_not_exported_rust():
    """``ProxyConfiguration`` and ``SSLConfiguration`` can no longer be imported.

    Neither ``azure.cosmos`` nor ``azure.cosmos.documents`` has them.
    """
    import azure.cosmos
    from azure.cosmos import documents

    for name in ("ProxyConfiguration", "SSLConfiguration"):
        assert not hasattr(azure.cosmos, name)
        assert not hasattr(documents, name)


@pytest.mark.parametrize(
    "option",
    ["proxy_config", "proxies", "ssl_config", "connection_verify", "connection_cert", "transport",
     "raw_request_hook", "raw_response_hook"],
)
def test_connection_object_refuses_removed_options_rust(client_module, option):
    """The connection object also refuses every removed option when it is created directly.

    This test uses the real connection object, not a mock.
    """
    with pytest.raises(TypeError, match=rf"{option} has been removed"):
        client_module.CosmosClientConnection("https://alpha-bank-account.invalid", None, **{option: None})


@pytest.mark.parametrize("from_connection_string", [False, True])
def test_transport_helper_sets_transport_and_restores_pipeline_rust(client_module, from_connection_string):
    """The test helper ``create_client_with_transport`` gives the client's pipeline a custom transport.

    To do this, it replaces the SDK's pipeline factory while the client is
    created, and it must put the original factory back afterwards. The pipeline
    must not include ``CustomHookPolicy``, the step that runs raw request and
    response hooks. No request is sent.
    """
    import importlib
    from azure.core.pipeline.policies import CustomHookPolicy
    from azure.core.pipeline.transport import AsyncHttpTransport, HttpTransport
    from _client_transport import create_client_with_transport

    async_mode = client_module is async_client
    connection_module = importlib.import_module(client_module.CosmosClientConnection.__module__)
    pipeline_factory_name = "AsyncPipelineClient" if async_mode else "PipelineClient"
    original_pipeline_factory = getattr(connection_module, pipeline_factory_name)
    transport = MagicMock(spec=AsyncHttpTransport if async_mode else HttpTransport)
    if from_connection_string:
        client = create_client_with_transport(
            client_module.CosmosClient.from_connection_string,
            "AccountEndpoint=https://alpha-bank-account.invalid;AccountKey=ZmFrZQ==;",
            transport=transport, _backend="rust",
        )
    else:
        client = create_client_with_transport(
            client_module.CosmosClient, "https://alpha-bank-account.invalid", "ZmFrZQ==",
            transport=transport, _backend="rust",
        )
    try:
        assert client.client_connection.pipeline_client._pipeline._transport is transport
        assert not any(
            isinstance(getattr(policy, "_policy", policy), CustomHookPolicy)
            for policy in client.client_connection.pipeline_client._pipeline._impl_policies
        )
        assert getattr(connection_module, pipeline_factory_name) is original_pipeline_factory
        transport.send.assert_not_called()
    finally:
        result = client.close()
        if inspect.isawaitable(result):
            asyncio.run(result)


def test_changing_built_policy_does_not_change_caller_policy_rust(construct_client):
    """Changing the built policy after the client is created changes nothing else.

    The test adds a region to one list, empties the other and lowers the retry
    count, all on the built policy. The caller's policy must keep its values, and
    the compiled-module settings must keep the original regions.
    """
    policy = configured_policy()
    client, built_policy = construct_client(connection_policy=policy)
    built_policy.PreferredLocations.append("North Europe")
    built_policy.ExcludedLocations.clear()
    built_policy.RetryOptions._max_retry_attempt_count = 1
    assert policy.PreferredLocations == ["West US", "East US"]
    assert policy.ExcludedLocations == ["Central US"]
    assert policy.RetryOptions.MaxRetryAttemptCount == 3
    assert client._adapter._client_config.preferred_locations == ("West US", "East US")


def test_resolving_settings_changes_nothing_and_repeats_same_result_rust():
    """``resolve_connection_policy_kwargs`` turns policy fields and keywords into one set of settings.

    It must not change the keywords or the policy it is given, and running it
    again on its own result must give the same result.
    """
    policy = configured_policy()
    options = {"connection_policy": policy, "retry_total": 0}
    original = dict(vars(policy.RetryOptions))
    resolved = resolve_connection_policy_kwargs(options)
    assert options == {"connection_policy": policy, "retry_total": 0}
    assert vars(policy.RetryOptions) == original
    assert resolve_connection_policy_kwargs(resolved) == resolved


def test_value_that_is_not_a_policy_is_refused_rust(construct_client, client_module):
    """A value that is not a ``ConnectionPolicy`` is refused, and the error names ``connection_policy``.

    A plain dictionary is an easy mistake, so one is used here. The connection
    object must not be created.
    """
    with pytest.raises(TypeError, match="connection_policy"):
        construct_client(connection_policy={"preferred_locations": ["West US"]})
    client_module.CosmosClientConnection.assert_not_called()
