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
from contextlib import contextmanager
from copy import deepcopy
from typing import Any, Mapping, get_args, get_type_hints
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from azure.core.credentials import AccessToken
from websockets.typing import Subprotocol

from azure.ai.projects import AIProjectClient, models, operations
from azure.ai.projects._realtime import (
    Realtime,
    RealtimeConnectionManager,
    _assert_trusted_connection_url,
    _to_ws_url,
    _USER_AGENT,
)
from azure.ai.projects._version import VERSION
from azure.ai.projects.models import (
    RealtimeClientEventResponseCreate,
    RealtimeServerEventSessionCreated,
)
from azure.ai.projects.operations import RealtimeConnection, ServerEvent

_ENDPOINT = "https://my-account.services.ai.azure.com/api/projects/my-project"


class _FakeCredential:
    """Sync stub credential that returns a never-expiring token."""

    def __init__(self, token: str = "fake-token") -> None:
        self._token = token

    def get_token(self, *args, **kwargs) -> AccessToken:  # pylint: disable=unused-argument
        return AccessToken(self._token, 9_999_999_999)


def test_realtime_constructor_hides_config_in_kwargs():
    config = MagicMock()
    client = MagicMock(_config=config)

    realtime = Realtime(client)

    assert realtime._config is config
    assert tuple(inspect.signature(Realtime.__init__).parameters) == ("self", "args", "kwargs")


def _make_manager(**overrides) -> RealtimeConnectionManager:
    kwargs = {
        "endpoint": _ENDPOINT,
        "credential": _FakeCredential(),
        "credential_scopes": ["https://ai.azure.com/.default"],
        "api_version": "v1",
        "agent_name": "my-agent",
    }
    kwargs.update(overrides)
    return RealtimeConnectionManager(**kwargs)


@contextmanager
def _helper_connection():
    sent = []
    transport = MagicMock()
    transport.send.side_effect = lambda payload: sent.append(json.loads(payload))
    with patch("websockets.sync.client.connect", return_value=transport):
        with _make_manager() as connection:
            yield connection, sent


def test_public_server_event_union_covers_generated_events_and_shared_error():
    expected_models = set(models.RealtimeServerEvent.__mapping__.values()) | {models.RealtimeServerEventError}

    assert set(get_args(ServerEvent)) == expected_models | {Mapping[str, Any]}
    assert get_type_hints(RealtimeConnection.recv)["return"] == ServerEvent
    assert get_args(get_type_hints(RealtimeConnection.__iter__)["return"]) == (ServerEvent,)


def test_ga_realtime_public_types_are_used_by_the_client():
    with AIProjectClient(_ENDPOINT, _FakeCredential()) as client:
        assert type(client.voice_agents.realtime) is operations.Realtime
        assert type(client.voice_agents.realtime).__name__ == "Realtime"
        with patch("websockets.sync.client.connect", return_value=MagicMock()):
            manager = client.voice_agents.realtime.connect(agent_name="my-agent")
            assert type(manager) is operations.RealtimeConnectionManager
            assert type(manager).__name__ == "RealtimeConnectionManager"
            with manager as connection:
                assert type(connection) is operations.RealtimeConnection
                assert type(connection).__name__ == "RealtimeConnection"

    assert not any(name.startswith("BetaRealtime") for name in dir(operations))


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
        # RealtimeConnectionManager.enter() unconditionally rejects any non-"wss://" URL to
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
    """Unit tests for ``RealtimeConnectionManager.enter()``: URL/header construction and errors."""

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
        assert "Foundry-Features" not in kwargs["additional_headers"]
        assert "foundry_features" not in parse_qs(urlparse(called_url).query)

    @pytest.mark.parametrize("extra_headers", [{}, {"foundry-features": "Custom=V1Preview"}])
    def test_enter_preserves_preview_opt_in(self, extra_headers):
        with patch("websockets.sync.client.connect", return_value=MagicMock()) as mock_connect:
            with _make_manager(allow_preview=True, extra_headers=extra_headers):
                pass

        headers = mock_connect.call_args.kwargs["additional_headers"]
        feature_headers = {key.lower(): value for key, value in headers.items() if key.lower() == "foundry-features"}
        assert feature_headers == {"foundry-features": extra_headers.get("foundry-features", "VoiceAgents=V1Preview")}

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
            for cls in RealtimeConnectionManager.__mro__
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
        # "structured_inputs" query parameter -- the service never actually read the header.
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection) as mock_connect:
            manager = _make_manager(structured_inputs={"greeting_name": "Alex"})
            manager.enter()
            manager.__exit__()

        _args, kwargs = mock_connect.call_args
        query = parse_qs(urlparse(_args[0]).query)
        assert json.loads(query["structured_inputs"][0]) == {"greeting_name": "Alex"}
        assert "structured_input" not in query
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
    """Unit tests for ``RealtimeConnection.recv()``: event dispatch and error/timeout handling."""

    @pytest.mark.parametrize(
        "event_type,event_model",
        list(models.RealtimeServerEvent.__mapping__.items()),
        ids=list(models.RealtimeServerEvent.__mapping__),
    )
    def test_every_generated_realtime_server_event_is_dispatched(self, event_type, event_model):
        payload = {
            "type": event_type,
            "event_id": "event-dispatch",
            "output_index": 0,
            "content_index": 0,
            "future_field": {"enabled": False, "count": 0},
        }
        if event_type == "response.audio_timestamp.delta":
            payload["timestamp_type"] = "word"
        expected = dict(payload)
        transport = MagicMock()
        transport.recv.return_value = json.dumps(payload)
        with patch("websockets.sync.client.connect", return_value=transport):
            with _make_manager() as connection:
                event = connection.recv()

        assert type(event) is event_model
        assert event.type == event_type
        assert event.as_dict() == expected

    def test_recv_dispatches_shared_error_not_registered_on_generated_base(self):
        payload = {
            "type": "error",
            "event_id": "event-error",
            "error": {
                "type": "invalid_request_error",
                "code": "invalid_command",
                "message": "offline error",
                "event_id": "event-request",
                "future_field": False,
            },
            "future_field": {"enabled": False, "count": 0},
        }
        transport = MagicMock()
        transport.recv.return_value = json.dumps(payload)
        with patch("websockets.sync.client.connect", return_value=transport):
            with _make_manager() as connection:
                event = connection.recv()

        assert type(event) is models.RealtimeServerEventError
        assert event.error.message == "offline error"
        assert event.as_dict() == payload

    @pytest.mark.parametrize(
        "event_type,event_model",
        [
            ("session.handoff.started", models.VoiceAgentServerEventSessionHandoffStarted),
            ("session.handoff.completed", models.VoiceAgentServerEventSessionHandoffCompleted),
            ("session.handoff.aborted", models.VoiceAgentServerEventSessionHandoffAborted),
        ],
    )
    def test_recv_dispatches_handoff_events(self, request, event_type, event_model):
        payload = {
            "type": event_type,
            "event_id": "event-test",
            "handoff_id": "handoff-test",
            "edge_id": "edge-test",
            "from_node_id": "$entrypoint",
            "to_node_id": "node-test",
            "from_model": "source-model-test",
            "to_model": "target-model-test",
            "tool_call_id": "call-test",
            "node_generation": 0,
        }
        if event_type == "session.handoff.aborted":
            payload["reason"] = "user_interruption"
        transport = MagicMock()
        transport.recv.return_value = json.dumps(payload)
        with patch("websockets.sync.client.connect", return_value=transport):
            manager = _make_manager()
            connection = manager.enter()
            request.addfinalizer(manager.__exit__)
            event = connection.recv()
        assert isinstance(event, event_model)
        assert event.as_dict() == payload

    @pytest.mark.parametrize(
        "event_type,fields",
        [
            ("input_collection.status", {"channel": "dtmf", "status": "completed", "value": "0012"}),
            ("response.system_tool_arguments.delta", {"delta": '{"secret":'}),
            ("response.system_tool_arguments.done", {"name": "collect_dtmf", "arguments": '{"secret":false}'}),
        ],
    )
    def test_recv_dispatches_system_tool_events(self, request, event_type, fields):
        payload = {"type": event_type, "event_id": "event-test", "call_id": "call-test", **fields}
        if event_type.startswith("response."):
            payload.update(response_id="response-test", item_id="item-test", output_index=0)
        transport = MagicMock()
        transport.recv.return_value = json.dumps(payload)
        with patch("websockets.sync.client.connect", return_value=transport):
            manager = _make_manager()
            connection = manager.enter()
            request.addfinalizer(manager.__exit__)
            event = connection.recv()
        assert isinstance(event, models.RealtimeServerEvent.__mapping__[event_type])
        assert event.as_dict() == payload

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
        payload = {"type": "some.new.event", "foo": "bar", "future_field": {"enabled": False, "count": 0}}
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection):
            manager = _make_manager()
            conn = manager.enter()
            request.addfinalizer(manager.__exit__)

            fake_connection.recv.return_value = json.dumps(payload)
            event = conn.recv()
            assert isinstance(event, dict)
            assert event == payload

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
    """Unit tests for ``RealtimeConnection.send()``: model/str/mapping serialization."""

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


@pytest.mark.parametrize("event_id", [None, "event-helper"], ids=["default-event-id", "explicit-event-id"])
class TestRealtimeHelperSerialization:
    """Exercise the actual resource helper, SDK encoder, and socket send together."""

    @pytest.mark.parametrize("typed", [False, True], ids=["mapping", "generated-model"])
    def test_session_update_preserves_sparse_settings(self, typed, event_id):
        settings = {
            "instructions": "",
            "temperature": 0.0,
            "parallel_tool_calls": False,
            "tools": [],
            "output_modalities": ["text"],
        }
        if typed:
            session = models.VoiceAgentSessionUpdateConfig(**settings)
            expected_settings = {"type": "realtime", **settings}
        else:
            settings["future_settings"] = {"enabled": False, "count": 0}
            session = settings
            expected_settings = deepcopy(settings)
        original = deepcopy(session)
        kwargs = {"event_id": event_id} if event_id is not None else {}
        expected = {"type": "session.update", "session": expected_settings, **kwargs}

        with _helper_connection() as (connection, sent):
            assert connection.session.update(session=session, **kwargs) is None

        assert sent == [expected]
        assert session == original

    @pytest.mark.parametrize(
        "helper,arguments,expected",
        [
            pytest.param(
                "session.avatar_connect",
                {"client_sdp": "v=0\r\ns=offline\r\n"},
                {"type": "session.avatar.connect", "client_sdp": "v=0\r\ns=offline\r\n"},
                id="avatar-connect",
            ),
            pytest.param(
                "input_audio_buffer.append",
                {"audio": b"\x00\x01\xfe\xff"},
                {"type": "input_audio_buffer.append", "audio": "AAH+/w=="},
                id="append-bytes",
            ),
            pytest.param(
                "input_audio_buffer.append",
                {"audio": bytearray(b"\x00\x01\xfe\xff")},
                {"type": "input_audio_buffer.append", "audio": "AAH+/w=="},
                id="append-bytearray",
            ),
            pytest.param(
                "input_audio_buffer.append",
                {"audio": "AAH+/w=="},
                {"type": "input_audio_buffer.append", "audio": "AAH+/w=="},
                id="append-base64",
            ),
            pytest.param(
                "input_audio_buffer.append",
                {"audio": b""},
                {"type": "input_audio_buffer.append", "audio": ""},
                id="append-empty-bytes",
            ),
            pytest.param("input_audio_buffer.commit", {}, {"type": "input_audio_buffer.commit"}, id="commit-input"),
            pytest.param("input_audio_buffer.clear", {}, {"type": "input_audio_buffer.clear"}, id="clear-input"),
            pytest.param("output_audio_buffer.clear", {}, {"type": "output_audio_buffer.clear"}, id="clear-output"),
            pytest.param(
                "conversation.item.delete",
                {"item_id": "item-test"},
                {"type": "conversation.item.delete", "item_id": "item-test"},
                id="delete-item",
            ),
            pytest.param(
                "conversation.item.retrieve",
                {"item_id": "item-test"},
                {"type": "conversation.item.retrieve", "item_id": "item-test"},
                id="retrieve-item",
            ),
            pytest.param(
                "conversation.item.truncate",
                {"item_id": "item-test", "content_index": 0, "audio_end_ms": 0},
                {"type": "conversation.item.truncate", "item_id": "item-test", "content_index": 0, "audio_end_ms": 0},
                id="truncate-at-zero",
            ),
            pytest.param(
                "conversation.item.truncate",
                {"item_id": "item-test", "content_index": 1, "audio_end_ms": 240},
                {"type": "conversation.item.truncate", "item_id": "item-test", "content_index": 1, "audio_end_ms": 240},
                id="truncate-at-offset",
            ),
            pytest.param("response.create", {}, {"type": "response.create"}, id="create-default-response"),
            pytest.param("response.create", {"response": None}, {"type": "response.create"}, id="create-none-response"),
            pytest.param(
                "response.create",
                {"response": {}},
                {"type": "response.create", "response": {}},
                id="create-empty-response",
            ),
            pytest.param("response.cancel", {}, {"type": "response.cancel"}, id="cancel-current-response"),
            pytest.param(
                "response.cancel",
                {"response_id": "response-test"},
                {"type": "response.cancel", "response_id": "response-test"},
                id="cancel-specific-response",
            ),
        ],
    )
    def test_resource_helpers_send_exact_wire_payload(self, helper, arguments, expected, event_id):
        original = deepcopy(arguments)
        kwargs = {"event_id": event_id} if event_id is not None else {}

        with _helper_connection() as (connection, sent):
            resource = connection
            for name in helper.split("."):
                resource = getattr(resource, name)
            assert resource(**arguments, **kwargs) is None

        assert sent == [{**expected, **kwargs}]
        assert arguments == original

    @pytest.mark.parametrize("typed", [False, True], ids=["mapping", "generated-model"])
    @pytest.mark.parametrize("previous_item_id", [None, "", "previous-test"])
    def test_conversation_item_create_preserves_tool_output(self, typed, previous_item_id, event_id):
        item_payload = {
            "type": "function_call_output",
            "call_id": "canonical-call-test",
            "output": '{"available":false,"count":0}',
        }
        if typed:
            item = models.RealtimeConversationItemFunctionCallOutput(
                call_id="canonical-call-test", output='{"available":false,"count":0}'
            )
        else:
            item_payload["future_field"] = {"enabled": False, "count": 0}
            item = deepcopy(item_payload)
        original = deepcopy(item)
        kwargs = {"event_id": event_id} if event_id is not None else {}
        if previous_item_id is not None:
            kwargs["previous_item_id"] = previous_item_id

        with _helper_connection() as (connection, sent):
            assert connection.conversation.item.create(item=item, **kwargs) is None

        assert sent == [{"type": "conversation.item.create", "item": item_payload, **kwargs}]
        assert item == original

    @pytest.mark.parametrize("typed", [False, True], ids=["mapping", "generated-model"])
    def test_response_create_preserves_per_response_overrides(self, typed, event_id):
        response_payload = {
            "instructions": "",
            "parallel_tool_calls": False,
            "input": [],
            "output_modalities": ["text"],
        }
        if typed:
            response = models.VoiceAgentResponseCreateParams(**response_payload)
        else:
            response_payload["future_settings"] = {"enabled": False, "count": 0}
            response = deepcopy(response_payload)
        original = deepcopy(response)
        kwargs = {"event_id": event_id} if event_id is not None else {}

        with _helper_connection() as (connection, sent):
            assert connection.response.create(response=response, **kwargs) is None

        assert sent == [{"type": "response.create", "response": response_payload, **kwargs}]
        assert response == original


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
