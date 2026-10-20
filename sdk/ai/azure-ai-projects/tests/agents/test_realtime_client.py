# pylint: disable=too-many-lines,line-too-long,useless-suppression,protected-access
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
"""Transport-mocked unit tests for the hand-written sync realtime (WebSocket) client.

Unlike ``test_voice_agent_crud.py``, these tests never make an HTTP/WS call: the underlying
``websockets.sync.client.connect`` is replaced with a fake so URL construction, header/auth
handling, event serialization/deserialization, connection cleanup, and dependency/error paths
can all be verified without a live service or a recorded transport.
"""

import json
import inspect
import logging
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from azure.core.credentials import AccessToken
from websockets.typing import Subprotocol

from azure.ai.projects import models
from azure.ai.projects._realtime import (
    BetaRealtime,
    BetaRealtimeConnectionManager,
    _assert_trusted_connection_url,
    _to_ws_url,
    _USER_AGENT,
)
from azure.ai.projects._version import VERSION
from azure.ai.projects.models import (
    RealtimeClientEventResponseCreate,
    RealtimeServerEventSessionCreated,
)

_ENDPOINT = "https://my-account.services.ai.azure.com/api/projects/my-project"


@pytest.mark.parametrize(
    "sub_protocol,expected_type",
    [
        (None, models.VoiceAgentDefinition),
        ("realtime", models.VoiceAgentDefinition),
        ("live", models.VoiceAgentLiveDefinition),
        ("future-protocol", models.VoiceAgentBaseDefinition),
    ],
)
def test_voice_agent_readback_preserves_concrete_types_and_wire_omission(sub_protocol, expected_type):
    definition = {
        "kind": "voice",
        "model": "deployment-test",
        "model_type": "self_deployed" if sub_protocol == "live" else "managed",
    }
    if sub_protocol is not None:
        definition["sub_protocol"] = sub_protocol
    version = models.AgentVersionDetails({"name": "agent-test", "version": "1", "definition": definition})

    assert type(version.definition) is expected_type
    assert version.definition.as_dict() == definition
    assert expected_type(definition).as_dict() == definition
    if isinstance(version.definition, (models.VoiceAgentDefinition, models.VoiceAgentLiveDefinition)):
        assert version.definition.model == "deployment-test"


@pytest.mark.parametrize(
    "definition,expected_type",
    [
        ({"kind": "prompt", "model": "deployment-test"}, models.PromptAgentDefinition),
        ({"kind": "future-agent-kind", "custom": {"setting": True}}, models.AgentDefinition),
    ],
)
def test_voice_readback_customization_does_not_change_other_agent_kinds(definition, expected_type):
    version = models.AgentVersionDetails({"name": "agent-test", "version": "1", "definition": definition})

    assert type(version.definition) is expected_type
    assert version.definition.as_dict() == definition


class _FakeCredential:
    """Sync stub credential that returns a never-expiring token."""

    def __init__(self, token: str = "fake-token") -> None:
        self._token = token

    def get_token(self, *args, **kwargs) -> AccessToken:  # pylint: disable=unused-argument
        return AccessToken(self._token, 9_999_999_999)


def test_realtime_constructor_hides_config_in_kwargs():
    config = MagicMock()
    client = MagicMock(_config=config)

    realtime = BetaRealtime(client)

    assert realtime._config is config
    assert tuple(inspect.signature(BetaRealtime.__init__).parameters) == ("self", "args", "kwargs")


def _make_manager(**overrides) -> BetaRealtimeConnectionManager:
    kwargs = {
        "endpoint": _ENDPOINT,
        "credential": _FakeCredential(),
        "credential_scopes": ["https://ai.azure.com/.default"],
        "api_version": "v1",
        "agent_name": "my-agent",
    }
    kwargs.update(overrides)
    return BetaRealtimeConnectionManager(**kwargs)


class TestToWsUrl:
    """Unit tests for the pure ``_to_ws_url`` URL-construction helper."""

    def test_https_endpoint_becomes_wss(self):
        url = _to_ws_url(_ENDPOINT, "my-agent")
        assert (
            url
            == "wss://my-account.services.ai.azure.com/api/projects/my-project/agents/my-agent/endpoint/protocols/voice"
        )

    def test_non_https_endpoint_scheme_is_left_unchanged(self):
        # Regression test: _to_ws_url used to translate "http://" to "ws://", but
        # BetaRealtimeConnectionManager.enter() unconditionally rejects any non-"wss://" URL to
        # protect the live Authorization token in transit, so that translated "ws://" URL could
        # never actually be used to connect. Leaving the scheme untouched here means the
        # downstream "wss://" check surfaces a clear error instead of an unreachable "ws://" path.
        url = _to_ws_url("http://localhost:8080", "my-agent")
        assert url == "http://localhost:8080/agents/my-agent/endpoint/protocols/voice"

    def test_trailing_slash_is_stripped(self):
        url = _to_ws_url(_ENDPOINT + "/", "my-agent")
        assert (
            url
            == "wss://my-account.services.ai.azure.com/api/projects/my-project/agents/my-agent/endpoint/protocols/voice"
        )


class TestAssertTrustedConnectionUrl:
    """Unit tests for the connection_url host allow-list guard (security fix)."""

    def test_matching_host_does_not_raise(self):
        _assert_trusted_connection_url(f"wss://{'my-account.services.ai.azure.com'}/custom/path", _ENDPOINT)

    def test_mismatched_host_raises_value_error(self):
        with pytest.raises(ValueError):
            _assert_trusted_connection_url("wss://evil.example.com/steal-token", _ENDPOINT)

    def test_empty_host_raises_value_error(self):
        with pytest.raises(ValueError):
            _assert_trusted_connection_url("not-a-url", _ENDPOINT)

    def test_matching_host_explicit_default_port_does_not_raise(self):
        # An explicit ":443" is the wss/https default, so this is the same origin as _ENDPOINT
        # (which omits the port) and must be accepted.
        _assert_trusted_connection_url("wss://my-account.services.ai.azure.com:443/custom/path", _ENDPOINT)

    def test_mismatched_port_raises_value_error(self):
        # Regression test (security fix): comparing hostname alone let an override targeting the
        # same host on a different, non-default port (a different origin) slip through and
        # receive the live bearer token.
        with pytest.raises(ValueError):
            _assert_trusted_connection_url("wss://my-account.services.ai.azure.com:8443/steal-token", _ENDPOINT)


class TestRealtimeConnectionManagerEnter:
    """Unit tests for ``BetaRealtimeConnectionManager.enter()``: URL/header construction and errors."""

    def test_enter_builds_bearer_auth_and_query(self):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection) as mock_connect:
            manager = _make_manager()
            conn = manager.enter()
            try:
                assert conn is not None
            finally:
                manager.__exit__()

        assert mock_connect.call_count == 1
        _args, kwargs = mock_connect.call_args
        called_url = _args[0]
        assert called_url.startswith("wss://my-account.services.ai.azure.com")
        assert "api-version=v1" in called_url
        assert kwargs["additional_headers"]["Authorization"] == "Bearer fake-token"
        assert kwargs["additional_headers"]["Foundry-Features"] == "VoiceAgents=V1Preview"

    def test_enter_identifies_sdk_via_user_agent_and_query(self):
        # The generated HTTP surface gets SDK identification for free from the core pipeline's
        # UserAgentPolicy; this hand-written client builds its own request and must opt in
        # explicitly, both as a User-Agent header and (since some proxies/paths don't forward
        # WebSocket upgrade headers) as an x-ms-client-sdk query parameter.
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection) as mock_connect:
            manager = _make_manager()
            manager.enter()
            manager.__exit__()

        _args, kwargs = mock_connect.call_args
        assert kwargs["additional_headers"]["User-Agent"] == _USER_AGENT
        assert "azsdk-python-ai-projects" in _USER_AGENT
        assert VERSION in _USER_AGENT

        query = parse_qs(urlparse(_args[0]).query)
        assert query["x-ms-client-sdk"] == [_USER_AGENT]

    def test_enter_caller_user_agent_overrides_default(self):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection) as mock_connect:
            manager = _make_manager(extra_headers={"User-Agent": "custom-user-agent"})
            manager.enter()
            manager.__exit__()

        _args, kwargs = mock_connect.call_args
        assert kwargs["additional_headers"]["User-Agent"] == "custom-user-agent"

    def test_enter_caller_user_agent_overrides_default_case_insensitive(self):
        # Regression test: a plain dict merge of extra_headers would leave a differently-cased
        # caller override (e.g. "user-agent") as a *separate* key alongside our own "User-Agent"
        # default, since Python dict keys are case-sensitive but HTTP header names are not --
        # sending two User-Agent-like headers instead of cleanly honoring the caller's override.
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection) as mock_connect:
            manager = _make_manager(extra_headers={"user-agent": "custom-user-agent"})
            manager.enter()
            manager.__exit__()

        _args, kwargs = mock_connect.call_args
        headers = kwargs["additional_headers"]
        assert "User-Agent" not in headers
        assert headers["user-agent"] == "custom-user-agent"

    def test_enter_source_retains_client_identification_wiring(self):
        # SDK identification belongs to the authenticated transport shared by Live and Realtime.
        source = "\n".join(
            inspect.getsource(cls.__dict__[method])
            for cls in BetaRealtimeConnectionManager.__mro__
            for method in ("enter", "_get_query")
            if method in cls.__dict__
        )
        assert "_USER_AGENT" in source
        assert "_has_header_case_insensitive" in source
        assert "x-ms-client-sdk" in source

    def test_enter_disables_library_default_user_agent_header(self):
        # Regression test: unlike aiohttp (where an explicit "User-Agent" in `headers` already
        # takes precedence over its own default), `websockets.sync.client.connect`'s
        # `user_agent_header` is a wholly separate mechanism from `additional_headers` -- passing
        # our own "User-Agent" there does not suppress it. Without explicitly disabling it, the
        # connection would carry two distinct User-Agent-like values.
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection) as mock_connect:
            manager = _make_manager()
            manager.enter()
            manager.__exit__()

        _args, kwargs = mock_connect.call_args
        assert kwargs["user_agent_header"] is None

    def test_enter_overrides_caller_supplied_subprotocols_kwarg(self):
        # Regression test: subprotocols=[Subprotocol("realtime")] is passed explicitly to
        # _ws_connect, so a caller-supplied subprotocols override forwarded through **kwargs would
        # otherwise collide ("got multiple values for keyword argument 'subprotocols'"). The
        # service requires the "realtime" subprotocol, so the override is dropped rather than
        # honored -- matching the async implementation's handling of its equivalent `protocols`
        # kwarg.
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection) as mock_connect:
            manager = _make_manager(subprotocols=["other"])
            manager.enter()
            manager.__exit__()

        _args, kwargs = mock_connect.call_args
        assert kwargs["subprotocols"] == [Subprotocol("realtime")]

    def test_enter_appends_extra_query_and_headers(self):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection) as mock_connect:
            manager = _make_manager(extra_query={"foo": "bar"}, extra_headers={"X-Custom": "1"})
            manager.enter()
            manager.__exit__()

        _args, kwargs = mock_connect.call_args
        assert "foo=bar" in _args[0]
        assert kwargs["additional_headers"]["X-Custom"] == "1"

    def test_enter_sends_structured_inputs_as_query_parameter(self):
        # Regression test: structured_inputs used to be serialized into a custom
        # "x-ms-voice-structured-inputs" header, but the generated request builder
        # (build_beta_voice_agents_realtime_connect_voice_agent_request) defines this as the
        # "structured_input" query parameter -- the service never actually read the header.
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection) as mock_connect:
            manager = _make_manager(structured_inputs={"greeting_name": "Alex"})
            manager.enter()
            manager.__exit__()

        _args, kwargs = mock_connect.call_args
        query = parse_qs(urlparse(_args[0]).query)
        assert json.loads(query["structured_input"][0]) == {"greeting_name": "Alex"}
        assert "x-ms-voice-structured-inputs" not in kwargs["additional_headers"]

    def test_enter_preserves_existing_query_on_connection_url_override(self):
        # Regression test: the URL builder used to unconditionally append "?", corrupting an
        # override URL that already has a query string (e.g. a SAS-style "?sig=...").
        fake_connection = MagicMock()
        override = f"wss://{'my-account.services.ai.azure.com'}/custom?sig=abc"
        with patch("websockets.sync.client.connect", return_value=fake_connection) as mock_connect:
            manager = _make_manager(connection_url=override)
            manager.enter()
            manager.__exit__()

        called_url = mock_connect.call_args[0][0]
        assert called_url.count("?") == 1
        assert "sig=abc&api-version=v1" in called_url

    def test_enter_rejects_untrusted_connection_url_host(self):
        manager = _make_manager(connection_url="wss://evil.example.com/steal-token")
        with pytest.raises(ValueError):
            manager.enter()

    def test_enter_rejects_non_wss_url(self):
        # A plain http(s) endpoint that somehow produced a non-ws(s) URL should never proceed.
        manager = _make_manager(endpoint="ftp://not-http-or-https")
        with pytest.raises(ValueError):
            manager.enter()

    def test_enter_raises_runtime_error_when_websockets_missing(self):
        manager = _make_manager()
        with patch.dict("sys.modules", {"websockets.sync.client": None, "websockets.typing": None}):
            with pytest.raises(RuntimeError, match="websockets"):
                manager.enter()

    def test_context_manager_closes_connection_on_exit(self):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            with _make_manager() as conn:
                pass
        fake_connection.close.assert_called_once()


class TestRealtimeConnectionRecv:
    """Unit tests for ``BetaRealtimeConnection.recv()``: event dispatch and error/timeout handling."""

    def test_recv_dispatches_known_event_type(self, request):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            manager = _make_manager()
            conn = manager.enter()
            request.addfinalizer(manager.__exit__)

            fake_connection.recv.return_value = json.dumps({"type": "session.created", "session": {}})
            event = conn.recv()
            assert isinstance(event, RealtimeServerEventSessionCreated)

    def test_recv_unknown_event_type_returns_dict(self, request):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            manager = _make_manager()
            conn = manager.enter()
            request.addfinalizer(manager.__exit__)

            fake_connection.recv.return_value = json.dumps({"type": "some.new.event", "foo": "bar"})
            event = conn.recv()
            assert isinstance(event, dict)
            assert event["foo"] == "bar"

    def test_recv_forwards_timeout_to_underlying_connection(self, request):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            manager = _make_manager()
            conn = manager.enter()
            request.addfinalizer(manager.__exit__)

            fake_connection.recv.return_value = json.dumps({"type": "error", "error": {"message": "boom"}})
            conn.recv(timeout=5.0)
            fake_connection.recv.assert_called_once_with(timeout=5.0)

    def test_recv_timeout_error_propagates(self, request):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            manager = _make_manager()
            conn = manager.enter()
            request.addfinalizer(manager.__exit__)

            fake_connection.recv.side_effect = TimeoutError()
            with pytest.raises(TimeoutError):
                conn.recv(timeout=0.1)

    def test_recv_connection_closed_raises_connection_reset_error(self, request):
        from websockets.exceptions import ConnectionClosedOK

        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            manager = _make_manager()
            conn = manager.enter()
            request.addfinalizer(manager.__exit__)

            fake_connection.recv.side_effect = ConnectionClosedOK(None, None)
            with pytest.raises(ConnectionResetError):
                conn.recv()

    def test_iteration_stops_cleanly_on_connection_reset(self, request):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            manager = _make_manager()
            conn = manager.enter()
            request.addfinalizer(manager.__exit__)

            fake_connection.recv.side_effect = ConnectionResetError()
            assert list(conn) == []

    def test_iteration_stops_cleanly_on_graceful_close(self, request):
        from websockets.exceptions import ConnectionClosedOK
        from websockets.frames import Close

        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            manager = _make_manager()
            conn = manager.enter()
            request.addfinalizer(manager.__exit__)

            fake_connection.recv.side_effect = ConnectionClosedOK(Close(1000, "bye"), None)
            assert list(conn) == []

    def test_iteration_propagates_abnormal_closure(self, request):
        # Regression test: recv() converts every websockets.exceptions.ConnectionClosed
        # (graceful *and* abnormal) into ConnectionResetError, so a blanket except clause here
        # made a real server-side failure (e.g. close code 1011) indistinguishable from a normal
        # end of stream -- a `for event in conn:` caller could silently accept a truncated
        # response. Only a graceful closure (ConnectionClosedOK) should end iteration quietly.
        from websockets.exceptions import ConnectionClosedError
        from websockets.frames import Close

        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            manager = _make_manager()
            conn = manager.enter()
            request.addfinalizer(manager.__exit__)

            fake_connection.recv.side_effect = ConnectionClosedError(Close(1011, "internal error"), None)
            with pytest.raises(ConnectionResetError):
                list(conn)


class TestRealtimeConnectionSend:
    """Unit tests for ``BetaRealtimeConnection.send()``: model/str/mapping serialization."""

    def test_send_serializes_typed_model(self, request):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            manager = _make_manager()
            conn = manager.enter()
            request.addfinalizer(manager.__exit__)

            conn.send(RealtimeClientEventResponseCreate())
            sent_raw = fake_connection.send.call_args[0][0]
            payload = json.loads(sent_raw)
            assert payload["type"] == "response.create"

    def test_send_passes_through_valid_json_string(self, request):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            manager = _make_manager()
            conn = manager.enter()
            request.addfinalizer(manager.__exit__)

            conn.send('{"type": "response.create"}')
            fake_connection.send.assert_called_once_with('{"type": "response.create"}')

    def test_send_rejects_invalid_json_string(self, request):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            manager = _make_manager()
            conn = manager.enter()
            request.addfinalizer(manager.__exit__)

            with pytest.raises(ValueError):
                conn.send("not valid json")

    def test_send_serializes_mapping(self, request):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            manager = _make_manager()
            conn = manager.enter()
            request.addfinalizer(manager.__exit__)

            conn.send({"type": "response.cancel"})
            sent_raw = fake_connection.send.call_args[0][0]
            assert json.loads(sent_raw) == {"type": "response.cancel"}


def test_realtime_logging_emits_metadata_without_sensitive_content(caplog):
    fake_connection = MagicMock()
    fake_connection.recv.return_value = json.dumps({"type": "some.new.event", "text": "secret-inbound-content"})
    connection_url = "wss://my-account.services.ai.azure.com/custom?sig=secret-query"

    caplog.set_level(logging.DEBUG, logger="azure.ai.projects.realtime")
    with patch("websockets.sync.client.connect", return_value=fake_connection):
        manager = _make_manager(
            connection_url=connection_url,
            structured_inputs={"value": "secret-structured-input"},
        )
        conn = manager.enter()
        conn.send({"type": "response.create", "text": "secret-outbound-content"})
        conn.recv()
        manager.__exit__()

    messages = "\n".join(record.getMessage() for record in caplog.records)
    assert "WebSocket CONNECT target=wss://my-account.services.ai.azure.com/custom" in messages
    assert "WebSocket CONNECTED target=wss://my-account.services.ai.azure.com/custom" in messages
    assert "WebSocket SEND type=response.create bytes=" in messages
    assert "WebSocket RECEIVE type=some.new.event bytes=" in messages
    assert "WebSocket CLOSE code=1000" in messages
    for sensitive_value in (
        "fake-token",
        "secret-query",
        "secret-structured-input",
        "secret-inbound-content",
        "secret-outbound-content",
    ):
        assert sensitive_value not in messages
