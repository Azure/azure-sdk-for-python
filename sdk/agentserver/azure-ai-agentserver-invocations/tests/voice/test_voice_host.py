# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Standalone CE endpoint registration and legacy transport isolation tests."""

import re

import pytest
from starlette.applications import Starlette
from starlette.routing import Host, Mount, WebSocketRoute
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.invocations.voice import (
    ResponseCreated,
    ResponseDone,
    ResponseOutputTextDone,
    Session,
    SessionReady,
    SessionStart,
    UserMessage,
    VoiceAgentServerHost,
)


@pytest.fixture(name="session_start_frame")
def _session_start_frame() -> dict[str, object]:
    return {
        "type": "session.start",
        "id": "m_start",
        "ts": "2026-10-15T00:00:00Z",
        "protocol_version": "1.0",
        "reconnect": False,
        "response_timeouts": {"first_output_ms": 1000, "idle_ms": 1000, "max_duration_ms": 3000},
    }


class TestVoiceEndpointRoutes:
    """Keep both endpoints independent of the unchanged typed Bridge wire contract."""

    def test_host_adds_ce_without_replacing_legacy_route(self) -> None:
        app = VoiceAgentServerHost(configure_observability=None)
        routes = [(route.path, route.name) for route in app.routes if isinstance(route, WebSocketRoute)]
        assert routes == [
            ("/invocations_ws", "invocations_ws"),
            ("/voice_conversation_engine", "voice_conversation_engine"),
        ]
        assert app.url_path_for("invocations_ws") == "/invocations_ws"
        assert app.url_path_for("voice_conversation_engine") == "/voice_conversation_engine"

    def test_typed_host_does_not_expose_superseded_ce_route(self) -> None:
        app = VoiceAgentServerHost(configure_observability=None)

        with TestClient(app) as client:
            with pytest.raises(WebSocketDisconnect):
                with client.websocket_connect("/conversation_engine"):
                    pytest.fail("The superseded CE route must not be accepted")

    @pytest.mark.parametrize("protocol", ["invocations_ws", "voice_conversation_engine"])
    def test_both_endpoints_relay_existing_bridge_messages(self, protocol: str, session_start_frame) -> None:
        app = VoiceAgentServerHost(configure_observability=None)
        paths = [route.path for route in app.routes if isinstance(route, WebSocketRoute)]
        assert paths == ["/invocations_ws", "/voice_conversation_engine"]

        @app.on_session_start
        async def start(session: Session, event: SessionStart) -> None:
            assert event.protocol_version == "1.0"
            await session.send(SessionReady())

        @app.on_user_message
        async def respond(session: Session, event: UserMessage) -> None:
            await session.send(ResponseCreated(response_id="r_reply", in_reply_to=(event.item_id,)))
            await session.send(ResponseOutputTextDone(response_id="r_reply", item_id="it_reply", text="Hello."))
            await session.send(ResponseDone(response_id="r_reply"))

        with TestClient(app).websocket_connect(f"/{protocol}") as websocket:
            websocket.send_json(session_start_frame)
            assert websocket.receive_json()["type"] == "session.ready"
            websocket.send_json(
                {
                    "type": "user.message",
                    "id": "m_input",
                    "ts": "2026-10-15T00:00:01Z",
                    "item_id": "in_question",
                    "content": [{"type": "input_text", "text": "Hello"}],
                }
            )
            created = websocket.receive_json()
            assert created["type"] == "response.created"
            assert created["in_reply_to"] == ["in_question"]
            assert websocket.receive_json()["text"] == "Hello."
            assert websocket.receive_json()["type"] == "response.done"

    def test_endpoints_keep_connection_sessions_separate(self, session_start_frame) -> None:
        app = VoiceAgentServerHost(configure_observability=None)
        sessions = []

        @app.on_session_start
        async def start(session: Session, _event: SessionStart) -> None:
            sessions.append(session)
            await session.send(SessionReady())

        @app.on_user_message
        async def respond(session: Session, event: UserMessage) -> None:
            await session.send(ResponseCreated(response_id=f"r_{event.item_id}", in_reply_to=(event.item_id,)))
            await session.send(ResponseDone(response_id=f"r_{event.item_id}"))

        with TestClient(app) as client:
            with client.websocket_connect("/invocations_ws") as legacy:
                legacy.send_json(session_start_frame)
                assert legacy.receive_json()["type"] == "session.ready"
                with client.websocket_connect("/voice_conversation_engine") as ce:
                    ce.send_json(session_start_frame)
                    assert ce.receive_json()["type"] == "session.ready"
                    ce.send_json(
                        {
                            "type": "user.message",
                            "id": "m_ce",
                            "ts": "2026-10-15T00:00:01Z",
                            "item_id": "in_ce",
                            "content": [{"type": "input_text", "text": "CE"}],
                        }
                    )
                    assert ce.receive_json()["response_id"] == "r_in_ce"
                    assert ce.receive_json()["type"] == "response.done"
                # Closing a CE connection must not close or replace the legacy session.
                legacy.send_json(
                    {
                        "type": "user.message",
                        "id": "m_legacy",
                        "ts": "2026-10-15T00:00:02Z",
                        "item_id": "in_legacy",
                        "content": [{"type": "input_text", "text": "Legacy"}],
                    }
                )
                assert legacy.receive_json()["response_id"] == "r_in_legacy"
                assert legacy.receive_json()["type"] == "response.done"
        assert len(sessions) == 2
        assert sessions[0] is not sessions[1]

    @pytest.mark.parametrize("protocol", ["invocations_ws", "voice_conversation_engine"])
    def test_both_routes_reject_same_scope_conflicts(self, protocol: str) -> None:
        async def conflicting_endpoint(websocket: WebSocket) -> None:
            await websocket.accept()

        path = f"/{protocol}"
        with pytest.raises(RuntimeError, match=re.escape(f"cannot own {path}")):
            VoiceAgentServerHost(
                routes=[WebSocketRoute(path, conflicting_endpoint)],
                configure_observability=None,
            )

    @pytest.mark.parametrize("protocol", ["invocations_ws", "voice_conversation_engine"])
    def test_both_routes_recheck_live_conflicts(self, protocol: str) -> None:
        app = VoiceAgentServerHost(configure_observability=None)

        async def conflicting_endpoint(websocket: WebSocket) -> None:
            await websocket.accept()

        path = f"/{protocol}"
        app.router.routes.append(WebSocketRoute(path, conflicting_endpoint))
        with pytest.raises(RuntimeError, match=re.escape(f"cannot own {path}")):
            with TestClient(app).websocket_connect(path):
                pytest.fail("A conflicting route must not be accepted")

    @pytest.mark.parametrize("protocol", ["invocations_ws", "voice_conversation_engine"])
    @pytest.mark.parametrize("authority_kind", ["host", "mount"])
    def test_both_routes_preserve_host_and_mount_authority(self, protocol: str, authority_kind: str) -> None:
        async def authority_endpoint(websocket: WebSocket) -> None:
            await websocket.accept()
            await websocket.send_text("authority")

        path = f"/{protocol}"
        nested = Starlette(routes=[WebSocketRoute(path, authority_endpoint)])
        authority = Host("tenant.example", app=nested) if authority_kind == "host" else Mount("/", app=nested)
        app = VoiceAgentServerHost(routes=[authority], configure_observability=None)
        headers = {"host": "tenant.example"} if authority_kind == "host" else {}
        with TestClient(app).websocket_connect(path, headers=headers) as websocket:
            assert websocket.receive_text() == "authority"

    @pytest.mark.parametrize("protocol", ["invocations_ws", "voice_conversation_engine"])
    def test_both_routes_precede_live_catch_all(self, protocol: str, session_start_frame) -> None:
        async def catch_all(websocket: WebSocket) -> None:
            await websocket.accept()
            await websocket.send_text("catch_all")

        app = VoiceAgentServerHost(configure_observability=None)
        app.router.routes.insert(0, WebSocketRoute("/{path:path}", catch_all))

        @app.on_session_start
        async def start(session: Session, _event: SessionStart) -> None:
            await session.send(SessionReady())

        with TestClient(app) as client:
            with client.websocket_connect(f"/{protocol}") as websocket:
                websocket.send_json(session_start_frame)
                assert websocket.receive_json()["type"] == "session.ready"
            with client.websocket_connect("/other") as websocket:
                assert websocket.receive_text() == "catch_all"
        paths = [route.path for route in app.routes if isinstance(route, WebSocketRoute)]
        assert paths == ["/invocations_ws", "/voice_conversation_engine", "/{path:path}"]

    def test_generic_invocations_host_still_exposes_only_raw_ws(self) -> None:
        app = InvocationAgentServerHost(configure_observability=None)

        @app.ws_handler
        async def raw_ws(websocket: WebSocket) -> None:
            await websocket.send_text("raw protocol")

        with TestClient(app) as client:
            with client.websocket_connect("/invocations_ws") as websocket:
                assert websocket.receive_text() == "raw protocol"
            with pytest.raises(WebSocketDisconnect):
                with client.websocket_connect("/voice_conversation_engine"):
                    pytest.fail("A raw WS handler must not enable CE")

    @pytest.mark.parametrize("protocol", ["invocations_ws", "voice_conversation_engine"])
    def test_both_endpoints_preserve_reconnect_contract(self, protocol: str, session_start_frame) -> None:
        app = VoiceAgentServerHost(configure_observability=None)
        reconnects = []

        @app.on_session_start
        async def start(session: Session, event: SessionStart) -> None:
            reconnects.append(event.reconnect)
            assert event.protocol_version == "1.0"
            await session.send(SessionReady())

        with TestClient(app) as client:
            for reconnect in (False, True):
                with client.websocket_connect(f"/{protocol}") as websocket:
                    websocket.send_json({**session_start_frame, "reconnect": reconnect})
                    assert websocket.receive_json()["type"] == "session.ready"
        assert reconnects == [False, True]

    def test_typed_host_keeps_legacy_raw_handler_replacement_error(self) -> None:
        app = VoiceAgentServerHost(configure_observability=None)

        async def raw_ws(_websocket: WebSocket) -> None:
            pass

        with pytest.raises(
            RuntimeError, match="^VoiceAgentServerHost owns /invocations_ws; use on_<event> decorators$"
        ):
            app.ws_handler(raw_ws)
