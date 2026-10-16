# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Turning client construction options into settings, without any account access.

There are two ways to ask for the same thing: a grouped policy object handed to the
client, and individual keywords. Both must end up meaning the same thing, and where
both are given the keyword wins. On top of that the settings have to reach two places
at once -- the Rust configuration and the older path's policy object -- and those two
must agree.

Three recurring hazards are covered throughout. Zero is a real answer and must not be
mistaken for absent. The caller's own policy object must come back unchanged, since
they may reuse it for another client. And a setting the Rust path cannot honor must be
refused at construction rather than quietly ignored.

The real client classes are used; only the older connection object is stood in for, so
nothing opens a socket.
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
    """Run every test below against both the synchronous and asynchronous client.

    The two have separate construction code that reads the same options. Testing only
    one would let the other drift, and the difference would show up as a client that
    honors a setting in one program and ignores it in another.
    """
    return request.param


@pytest.fixture
def construct_client(client_module, monkeypatch):
    """Build real clients and hand back both the client and the older policy it produced.

    Returning both is the point of this fixture: nearly every test needs to check that
    the Rust configuration and the older path's policy say the same thing, and having
    them side by side is what makes that possible in one assertion.

    The backend selector is cleared first. The address and key are not real;
    nothing connects or initializes a native runtime.

    Every client built is closed at the end, awaiting the close where the asynchronous
    client needs it. Left open, the native side holds resources for the rest of the run.
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
    """A policy where every setting differs from the stock one.

    That is deliberate. Code here treats a setting equal to the stock value as "the
    caller did not ask", so a policy that happened to match the defaults would pass
    tests that a real one would fail.
    """
    policy = ConnectionPolicy()
    policy.PreferredLocations = ["West US", "East US"]
    policy.ExcludedLocations = ["Central US"]
    policy.RetryOptions = RetryOptions(max_retry_attempt_count=3, max_wait_time_in_seconds=12)
    return policy


def test_grouped_settings_match_direct_keywords(construct_client):
    """Asking with a policy object and asking with keywords produce the same client.

    Two clients are built, one each way, with the same four settings. Their Rust
    configurations are compared to each other and to a written-out expected value, so
    the two agreeing on something wrong would still fail.

    Then the older path's policy is checked to carry the same four. A setting that
    reached one path and not the other would behave differently depending on which
    backend happened to run.
    """
    policy = configured_policy()
    grouped, legacy = construct_client(connection_policy=policy)
    direct, _ = construct_client(
        preferred_locations=["West US", "East US"], excluded_locations=["Central US"],
        retry_throttle_total=3, retry_throttle_backoff_max=12,
    )
    assert grouped._adapter._client_config == direct._adapter._client_config == PreparedClientConfig(
        preferred_locations=("West US", "East US"), excluded_locations=("Central US",),
        throttling_max_retry_count=3, throttling_max_retry_wait_time_seconds=12,
    )
    assert legacy.PreferredLocations == policy.PreferredLocations
    assert legacy.ExcludedLocations == policy.ExcludedLocations
    assert legacy.RetryOptions.MaxRetryAttemptCount == 3
    assert legacy.RetryOptions.MaxWaitTimeInSeconds == 12


@pytest.mark.parametrize("policy", [None, ConnectionPolicy()])
def test_default_policy_does_not_pin_rust_settings(construct_client, policy):
    """A caller who chose nothing pins nothing, whether they passed no policy or a stock one.

    The public clients build a policy for every client whether or not one was asked for,
    so a stock policy cannot be read as a request. If it were, every client would arrive
    with a full set of settings fixed in place, and the native side could never apply its
    own defaults or adjust them later.

    Both forms must give no configuration at all, not an empty one.
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
def test_rust_routing_switches_fail_before_startup(
    client_module, monkeypatch, from_connection_string, selection, grouped, option, attribute, value,
):
    policy = ConnectionPolicy()
    if grouped:
        setattr(policy, attribute, value)
        kwargs = {"connection_policy": policy}
        rejected_name = rf"connection_policy\.{attribute}"
    else:
        kwargs = {option: value}
        rejected_name = option
    original = dict(vars(policy))
    if selection == "environment":
        monkeypatch.setenv("COSMOS_BACKEND", "rust")
    else:
        monkeypatch.setenv("COSMOS_BACKEND", "core-python")
        kwargs["_backend"] = "rust"
    connection = MagicMock()
    factory = MagicMock()
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    factory_name = "make_async_backend" if client_module is async_client else "make_backend"
    monkeypatch.setattr(client_module, factory_name, factory)
    with pytest.raises(TypeError, match=rejected_name + " is not supported by Rust-backed clients"):
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://policy.invalid;AccountKey=ZmFrZQ==;", **kwargs,
            )
        else:
            client_module.CosmosClient("https://policy.invalid", "ZmFrZQ==", **kwargs)
    connection.assert_not_called()
    factory.assert_not_called()
    assert vars(policy) == original


@pytest.mark.parametrize("attribute,default", [
    ("EnableEndpointDiscovery", True), ("UseMultipleWriteLocations", False),
])
@pytest.mark.parametrize("duplicate", [copy, deepcopy])
def test_copied_explicit_default_routing_policy_is_rejected(construct_client, attribute, default, duplicate):
    policy = ConnectionPolicy()
    setattr(policy, attribute, default)
    with pytest.raises(TypeError, match=attribute):
        construct_client(connection_policy=duplicate(policy))


@pytest.mark.parametrize("attribute,value", [
    ("EnableEndpointDiscovery", True), ("EnableEndpointDiscovery", False),
    ("UseMultipleWriteLocations", False), ("UseMultipleWriteLocations", True),
])
def test_subclass_routing_switch_is_rejected(construct_client, attribute, value):
    policy = type("RoutingPolicy", (ConnectionPolicy,), {attribute: value})()
    with pytest.raises(TypeError, match=attribute):
        construct_client(connection_policy=policy)


@pytest.mark.parametrize("backend", ["core-python", "rust"])
def test_untouched_routing_policy_can_be_reused(construct_client, backend):
    policy = configured_policy()
    original = dict(vars(policy))
    _, prepared_policy = construct_client(_backend=backend, connection_policy=policy)
    client, _ = construct_client(connection_policy=prepared_policy)
    assert client._adapter._client_config.preferred_locations == ("West US", "East US")
    assert client._adapter._client_config.excluded_locations == ("Central US",)
    assert vars(policy) == original
    assert "EnableEndpointDiscovery" not in vars(prepared_policy)
    assert "UseMultipleWriteLocations" not in vars(prepared_policy)


@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("grouped", [False, True])
@pytest.mark.parametrize("discovery,multi_write", [(True, False), (False, True), (None, None)])
def test_legacy_routing_switches_remain_available(
    construct_client, monkeypatch, from_connection_string, grouped, discovery, multi_write,
):
    monkeypatch.setenv("COSMOS_BACKEND", "rust")
    if grouped:
        policy = ConnectionPolicy()
        policy.EnableEndpointDiscovery = discovery
        policy.UseMultipleWriteLocations = multi_write
        options = {"connection_policy": policy}
    else:
        options = {"enable_endpoint_discovery": discovery, "multiple_write_locations": multi_write}
    client, prepared = construct_client(
        _backend="core-python", from_connection_string=from_connection_string, **options,
    )
    assert client._adapter.name == "core-python"
    assert prepared.EnableEndpointDiscovery is discovery
    assert prepared.UseMultipleWriteLocations is multi_write


def test_connection_string_factory_preserves_grouped_settings(construct_client):
    """Building from a connection string keeps the policy just as the direct constructor does.

    There are two ways to make a client and they take different routes to the same
    place. The second is easy to forget when options are added, and a setting silently
    dropped there would only show up for the customers who use it.
    """
    client, legacy = construct_client(
        from_connection_string=True, connection_policy=configured_policy()
    )
    assert client._adapter._client_config.preferred_locations == ("West US", "East US")
    assert legacy.RetryOptions.MaxRetryAttemptCount == 3


@pytest.mark.parametrize("seconds", [2.5, 10.0])
def test_fractional_throttle_wait_budget_reaches_prepared_config(construct_client, seconds):
    client, legacy = construct_client(retry_throttle_total=5, retry_throttle_backoff_max=seconds)
    assert client._adapter._client_config.throttling_max_retry_count == 5
    assert client._adapter._client_config.throttling_max_retry_wait_time_seconds == seconds
    assert legacy.RetryOptions.MaxWaitTimeInSeconds == seconds


def test_policy_zero_retry_limits_are_not_replaced_by_defaults(construct_client):
    """Asking for no retries at all means no retries, not the default number.

    Zero and "not set" look alike to code written in a hurry, and the mistake is quiet:
    the customer asked to fail fast and instead the client keeps retrying, which is the
    opposite of what they wanted and shows up as requests that hang far longer than the
    limit they set.

    Both limits are checked on both paths.
    """
    policy = ConnectionPolicy()
    policy.RetryOptions = RetryOptions(max_retry_attempt_count=0, max_wait_time_in_seconds=0)
    client, legacy = construct_client(connection_policy=policy)
    assert client._adapter._client_config.throttling_max_retry_count == 0
    assert client._adapter._client_config.throttling_max_retry_wait_time_seconds == 0
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
    """The specific retry keyword beats the general one, the general one beats the policy,
    and passing nothing means the keyword was not used.

    Five combinations, each a different rung of that order. The general keywords alone
    win over the policy. Zero through the general keywords is honored. The specific
    keywords win over the general ones, including when they are zero. Passing the
    specific ones as nothing steps down to the general ones rather than being treated as
    a choice of nothing. Passing both as nothing falls all the way back to the policy.

    That last distinction is the delicate one, and it is why the value meaning "absent"
    has to be separate from zero. Run on both backends, since the same order has to hold
    whichever one is chosen.
    """
    client, legacy = construct_client(
        _backend=backend, connection_policy=configured_policy(), **overrides
    )
    if backend == "rust":
        assert client._adapter._client_config.throttling_max_retry_count == count
        assert client._adapter._client_config.throttling_max_retry_wait_time_seconds == wait
    assert legacy.RetryOptions.MaxRetryAttemptCount == count
    assert legacy.RetryOptions.MaxWaitTimeInSeconds == wait


@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("locations", [[], ["North Europe"]])
def test_region_keywords_override_policy_including_empty(construct_client, backend, locations):
    """An empty list of regions is a real instruction and must not fall back to the policy.

    The policy names regions; the keywords ask for an empty list. Empty means "no
    preference, use the account's own order", which is a different request from "I did
    not say". Treating it as unsaid would leave the client pinned to regions the caller
    just cleared, sending their requests somewhere they had specifically stopped asking
    for.

    Both an empty list and a real one are run, on both backends.
    """
    client, legacy = construct_client(
        _backend=backend, connection_policy=configured_policy(),
        preferred_locations=locations, excluded_locations=[],
    )
    assert legacy.PreferredLocations == locations
    assert legacy.ExcludedLocations == []
    if backend == "rust":
        assert client._adapter._client_config.preferred_locations == tuple(locations)
        assert client._adapter._client_config.excluded_locations == ()


def test_legacy_policy_timeouts_still_resolve_with_keyword_and_alias_precedence(construct_client):
    """The older millisecond name for the connection timeout still wins, and the caller's
    policy is left alone.

    Two keywords mean the same timeout. The older one is counted in thousandths, the
    newer in whole seconds, and both are passed here with different values. The older one
    wins, so two thousand of the smaller units becomes two seconds and the three passed
    in the newer form is not used. Keeping that order is what stops an old program
    changing behavior when it is run against a newer client.

    The read timeout, given only as a keyword, beats the one in the policy. The caller's
    policy object is then checked to still hold its original numbers, since they may hand
    the same policy to another client and expect it unchanged.
    """
    policy = configured_policy()
    policy.RequestTimeout = 4
    _, legacy = construct_client(
        _backend="core-python", connection_policy=policy,
        request_timeout=2000, connection_timeout=3,
    )
    assert legacy.RequestTimeout == 2
    assert policy.RequestTimeout == 4
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize(
    "option",
    ["proxy_config", "proxies", "ssl_config", "connection_verify", "connection_cert", "transport"],
)
@pytest.mark.parametrize("value", [None, True, False, {}, "alpha-bank-ca.pem"])
def test_removed_network_options_fail_before_startup(
    client_module, monkeypatch, backend, from_connection_string, option, value,
):
    connection = MagicMock()
    backend_factory = MagicMock()
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    factory_name = "make_async_backend" if client_module is async_client else "make_backend"
    monkeypatch.setattr(client_module, factory_name, backend_factory)
    kwargs = {"_backend": backend, option: value}
    with pytest.raises(TypeError, match=rf"{option} has been removed"):
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://alpha-bank-account.invalid;AccountKey=ZmFrZQ==;", **kwargs,
            )
        else:
            client_module.CosmosClient("https://alpha-bank-account.invalid", "ZmFrZQ==", **kwargs)
    connection.assert_not_called()
    backend_factory.assert_not_called()


@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("attribute", ["ProxyConfiguration", "SSLConfiguration", "DisableSSLVerification"])
@pytest.mark.parametrize("value", [None, False, object()])
def test_removed_policy_fields_fail_before_startup(
    client_module, monkeypatch, backend, from_connection_string, attribute, value,
):
    policy = ConnectionPolicy()
    setattr(policy, attribute, value)
    connection = MagicMock()
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    with pytest.raises(TypeError, match=rf"connection_policy\.{attribute} has been removed"):
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://alpha-bank-account.invalid;AccountKey=ZmFrZQ==;",
                connection_policy=policy, _backend=backend,
            )
        else:
            client_module.CosmosClient(
                "https://alpha-bank-account.invalid", "ZmFrZQ==", connection_policy=policy, _backend=backend,
            )
    connection.assert_not_called()
    assert getattr(policy, attribute) is value


@pytest.mark.parametrize("nested", ["request_options", "feed_options", "options"])
@pytest.mark.parametrize(
    "option",
    ["proxy_config", "proxies", "ssl_config", "connection_verify", "connection_cert", "transport"],
)
def test_nested_removed_network_options_are_rejected(nested, option):
    from azure.cosmos._backend.capabilities import reject_removed_options

    with pytest.raises(TypeError, match=rf"{option} has been removed"):
        reject_removed_options({nested: {option: None}})


@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("option", ["raw_request_hook", "raw_response_hook"])
@pytest.mark.parametrize("value", [None, False, lambda _message: None])
def test_removed_raw_hooks_fail_before_startup(
    client_module, monkeypatch, backend, from_connection_string, option, value,
):
    connection = MagicMock()
    backend_factory = MagicMock()
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    factory_name = "make_async_backend" if client_module is async_client else "make_backend"
    monkeypatch.setattr(client_module, factory_name, backend_factory)
    kwargs = {"_backend": backend, option: value}
    with pytest.raises(TypeError, match=rf"{option} has been removed"):
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://policy.invalid;AccountKey=ZmFrZQ==;", **kwargs,
            )
        else:
            client_module.CosmosClient("https://policy.invalid", "ZmFrZQ==", **kwargs)
    connection.assert_not_called()
    backend_factory.assert_not_called()


def test_removed_configuration_classes_are_not_exported():
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
def test_direct_connection_rejects_removed_options(client_module, option):
    with pytest.raises(TypeError, match=rf"{option} has been removed"):
        client_module.CosmosClientConnection("https://alpha-bank-account.invalid", None, **{option: None})


@pytest.mark.parametrize("from_connection_string", [False, True])
def test_test_sender_uses_internal_pipeline_and_restores_factory(client_module, from_connection_string):
    import importlib
    from azure.core.pipeline.policies import CustomHookPolicy
    from azure.core.pipeline.transport import AsyncHttpTransport, HttpTransport
    from _client_transport import create_client_with_transport

    async_mode = client_module is async_client
    connection_module = importlib.import_module(client_module.CosmosClientConnection.__module__)
    factory_name = "AsyncPipelineClient" if async_mode else "PipelineClient"
    original_factory = getattr(connection_module, factory_name)
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
        assert getattr(connection_module, factory_name) is original_factory
        transport.send.assert_not_called()
    finally:
        result = client.close()
        if inspect.isawaitable(result):
            asyncio.run(result)


def test_mutable_policy_settings_are_snapshotted(construct_client):
    """Changing the policy the client produced does not reach back into the caller's.

    The earlier tests changed nothing after construction. This one attacks from the other
    side: the client's own policy is changed afterwards, adding to one region list,
    emptying the other, and lowering a retry count. All three are the kind of change
    something inside the client might make while running.

    None of it may show up in the caller's policy, and the Rust configuration is checked
    too -- it took its own copy, so it must still hold the regions asked for rather than
    the amended list.
    """
    policy = configured_policy()
    client, legacy = construct_client(connection_policy=policy)
    legacy.PreferredLocations.append("North Europe")
    legacy.ExcludedLocations.clear()
    legacy.RetryOptions._max_retry_attempt_count = 1
    assert policy.PreferredLocations == ["West US", "East US"]
    assert policy.ExcludedLocations == ["Central US"]
    assert policy.RetryOptions.MaxRetryAttemptCount == 3
    assert client._adapter._client_config.preferred_locations == ("West US", "East US")


def test_normalization_does_not_modify_input_and_is_idempotent():
    """Working out the settings changes nothing it was given, and doing it twice changes
    nothing further.

    The first half checks the arguments and the policy's retry settings are exactly as
    they were. The second feeds the result back in: the answer must be identical.

    Running twice is not hypothetical. Both construction routes call this, and the
    connection string route can end up calling it on arguments that have already been
    through it. If each pass promoted values a little further, the same options would
    mean different things depending on how the client was built.
    """
    policy = configured_policy()
    kwargs = {"connection_policy": policy, "retry_total": 0}
    original = dict(vars(policy.RetryOptions))
    resolved = resolve_connection_policy_kwargs(kwargs)
    assert kwargs == {"connection_policy": policy, "retry_total": 0}
    assert vars(policy.RetryOptions) == original
    assert resolve_connection_policy_kwargs(resolved) == resolved


def test_invalid_policy_rejected_before_startup(construct_client, client_module):
    """Something that is not a policy object is refused, with the error naming the option.

    A plain dictionary is the natural mistake, and its keys even look right. Accepting it
    would mean reading every setting off it as missing, so the client would be built with
    none of what was asked for and no complaint anywhere.

    The error names the option so the caller knows which argument to fix, and the older
    connection object is checked never to have been built.
    """
    with pytest.raises(TypeError, match="connection_policy"):
        construct_client(connection_policy={"preferred_locations": ["West US"]})
    client_module.CosmosClientConnection.assert_not_called()
