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
from unittest.mock import MagicMock, patch

import pytest
from azure.core.credentials import AccessToken

from azure.ai.projects._realtime import (
    RealtimeConnectionManager,
    _assert_trusted_connection_url,
    _to_ws_url,
)
from azure.ai.projects.models import (
    RealtimeClientEventResponseCreate,
    RealtimeServerEventError,
    RealtimeServerEventSessionCreated,
)

_ENDPOINT = "https://my-account.services.ai.azure.com/api/projects/my-project"


class _FakeCredential:
    """Sync stub credential that returns a never-expiring token."""

    def __init__(self, token: str = "fake-token") -> None:
        self._token = token

    def get_token(self, *args, **kwargs) -> AccessToken:  # pylint: disable=unused-argument
        return AccessToken(self._token, 9_999_999_999)


def _make_manager(**overrides) -> RealtimeConnectionManager:
    kwargs = {
        "endpoint": _ENDPOINT,
        "credential": _FakeCredential(),
        "credential_scopes": ["https://ai.azure.com/.default"],
        "api_version": "v1",
        "agent_name": "my-agent",
        "foundry_features": "VoiceAgents=V1Preview",
    }
    kwargs.update(overrides)
    return RealtimeConnectionManager(**kwargs)


class TestToWsUrl:
    """Unit tests for the pure ``_to_ws_url`` URL-construction helper."""

    def test_https_endpoint_becomes_wss(self):
        url = _to_ws_url(_ENDPOINT, "my-agent")
        assert (
            url
            == "wss://my-account.services.ai.azure.com/api/projects/my-project/agents/my-agent/endpoint/protocols/voice"
        )

    def test_http_endpoint_becomes_ws(self):
        url = _to_ws_url("http://localhost:8080", "my-agent")
        assert url == "ws://localhost:8080/agents/my-agent/endpoint/protocols/voice"

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
        assert kwargs["additional_headers"]["Foundry-Features"] == "VoiceAgents=V1Preview"

    def test_enter_appends_extra_query_and_headers(self):
        fake_connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=fake_connection) as mock_connect:
            manager = _make_manager(extra_query={"foo": "bar"}, extra_headers={"X-Custom": "1"})
            manager.enter()
            manager.__exit__()

        _args, kwargs = mock_connect.call_args
        assert "foo=bar" in _args[0]
        assert kwargs["additional_headers"]["X-Custom"] == "1"

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
