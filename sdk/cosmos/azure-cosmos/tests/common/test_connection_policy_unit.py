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

    Environment variables that could pick a different backend are removed first, and the
    registry is cleared before and after, so a client built by an earlier test cannot
    change what this one gets. The address and key are not real; nothing connects.

    Every client built is closed at the end, awaiting the close where the asynchronous
    client needs it. Left open, the native side holds resources for the rest of the run.
    """
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
    """A caller who chose nothing pins nothing, whether they passed no policy or a stock one.

    The public clients build a policy for every client whether or not one was asked for,
    so a stock policy cannot be read as a request. If it were, every client would arrive
    with a full set of settings fixed in place, and the native side could never apply its
    own defaults or adjust them later.

    Both forms must give no configuration at all, not an empty one.
    """
    client, _ = construct_client(connection_policy=policy)
    assert client._backend._client_config is None


def test_connection_string_factory_preserves_grouped_settings(construct_client):
    """Building from a connection string keeps the policy just as the direct constructor does.

    There are two ways to make a client and they take different routes to the same
    place. The second is easy to forget when options are added, and a setting silently
    dropped there would only show up for the customers who use it.
    """
    client, legacy = construct_client(
        from_connection_string=True, connection_policy=configured_policy()
    )
    assert client._backend._client_config.preferred_locations == ("West US", "East US")
    assert legacy.RetryOptions.MaxRetryAttemptCount == 3


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
        assert client._backend._client_config.throttling_max_retry_count == count
        assert client._backend._client_config.throttling_max_retry_wait_time_seconds == wait
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
        assert client._backend._client_config.preferred_locations == tuple(locations)
        assert client._backend._client_config.excluded_locations == ()


def test_policy_timeouts_still_resolve_with_keyword_and_alias_precedence(construct_client):
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
    """Settings the Rust path cannot honor are refused at construction, not ignored.

    A proxy, any of the three certificate settings, or turning certificate checking off:
    each is set inside the policy object rather than passed as a keyword, which is the
    easy place for a check to miss.

    Ignoring them would be the dangerous outcome. Turning certificate checking off and
    having it stay on merely breaks a test setup, but naming a proxy and having it
    ignored means traffic leaves by a route the customer believed it would not take.

    The error names the equivalent keyword rather than the field inside the policy, which
    is the thing the caller can actually change. The older connection object is checked
    never to have been built, so the failure really did come first.

    The last line then builds a client that does set a proxy choice. That choice is fixed
    for the whole process and a later client disagreeing with it is refused, so this
    succeeding proves the rejected constructions reserved nothing on their way out. A
    failed client that left its choice behind would poison every client built afterwards.
    """
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
    """Passing nothing for a transport setting clears what the policy said, and clearing it
    is enough to make the client acceptable.

    The policy carries a proxy, a certificate authority file, and certificate checking
    turned off -- all three of which would otherwise be refused. Passing the keywords
    explicitly as nothing withdraws them, and the client builds. That is the escape route
    for a caller who has a policy they cannot easily change.

    Once withdrawn nothing is pinned at all, so the Rust configuration is empty rather
    than holding cleared-out fields. The caller's policy is checked to still hold its
    original values, since withdrawing them for this client must not disarm it for the
    next one.
    """
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
    """On the older backend the transport settings are kept, and the caller's policy is
    still not touched.

    The refusals above belong to the Rust path alone. Choosing the older backend must
    behave exactly as it always has: the proxy survives, certificate checking stays off,
    and a certificate passed as a keyword replaces the one in the policy rather than
    being rejected.

    The rest checks that the policy handed to the older path is a separate object, along
    with the pieces nested inside it that get written to. A shallow copy would leave those
    shared, so changing one client's certificate would change another's. The caller's
    original values are checked one by one afterwards, including a region list and a
    retry count that were overridden for this client.
    """
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
    """A certificate holder passed as a keyword is not written to either.

    The test above protects one passed inside a policy. This is the same object arriving
    by the other door, and the copying happens in different code. A caller who keeps one
    of these around and builds several clients from it, each with a different certificate,
    would otherwise find them all using the last one.
    """
    ssl = SSLConfiguration()
    ssl.SSLCertFile = "original-cert.pem"
    _, legacy = construct_client(
        _backend="core-python", ssl_config=ssl, connection_cert="override-cert.pem"
    )
    assert ssl.SSLCertFile == "original-cert.pem"
    assert legacy.SSLConfiguration.SSLCertFile == "override-cert.pem"


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
    assert client._backend._client_config.preferred_locations == ("West US", "East US")


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
