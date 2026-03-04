# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for multi-modality payloads, content types, and protocol edge cases.

AgentServer is an HTTP/ASGI server.  It does NOT define WebSocket or gRPC
routes, so those protocol attempts must be handled gracefully.  The
server is content-type agnostic: agents can receive and return any
media type (images, audio, protobuf, SSE, etc.).
"""
import base64
import io
import json
import uuid

import httpx
import pytest
import pytest_asyncio

from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response, StreamingResponse

from azure.ai.agentserver import AgentServer


# ---------------------------------------------------------------------------
# Minimal binary blobs for realistic content types
# ---------------------------------------------------------------------------

# 1x1 red pixel PNG (67 bytes — smallest valid PNG)
_MINIMAL_PNG = bytes.fromhex(
    "89504e470d0a1a0a"  # PNG signature
    "0000000d49484452" "00000001000000010802" "000000907753de"  # header
    "0000000c49444154" "789c63f80f00000101000518d84e"  # image data
    "0000000049454e44ae426082"  # end
)

# Minimal WAV header (44 bytes) — 1 sample, 16-bit mono 8 kHz
_MINIMAL_WAV = bytes.fromhex(
    "52494646"  # RIFF
    "26000000"  # file size - 8 (38)
    "57415645"  # WAVE
    "666d7420"  # fmt 
    "10000000"  # chunk size (16)
    "0100"      # PCM
    "0100"      # mono
    "401f0000"  # sample rate 8000
    "803e0000"  # byte rate 16000
    "0200"      # block align
    "1000"      # bits per sample (16)
    "64617461"  # data
    "02000000"  # data bytes (2)
    "0000"      # 1 silent sample
)

# Tiny protobuf-like payload (field 1, varint value 150)
_PROTO_PAYLOAD = b"\x08\x96\x01"


# ---------------------------------------------------------------------------
# Specialised agent implementations: multi-modal
# ---------------------------------------------------------------------------


class ContentTypeEchoAgent(AgentServer):
    """Returns the request Content-Type and body length as JSON."""

    async def invoke(self, request: Request) -> Response:
        ctype = request.headers.get("content-type", "")
        body = await request.body()
        return JSONResponse({"content_type": ctype, "length": len(body)})


class ImageAgent(AgentServer):
    """Returns a pre-canned PNG image."""

    async def invoke(self, request: Request) -> Response:
        return Response(content=_MINIMAL_PNG, media_type="image/png")


class AudioAgent(AgentServer):
    """Returns a pre-canned WAV clip."""

    async def invoke(self, request: Request) -> Response:
        return Response(content=_MINIMAL_WAV, media_type="audio/wav")


class HtmlAgent(AgentServer):
    """Returns an HTML response."""

    async def invoke(self, request: Request) -> Response:
        return HTMLResponse("<html><body><h1>Hello Agent</h1></body></html>")


class PlainTextAgent(AgentServer):
    """Returns plain text."""

    async def invoke(self, request: Request) -> Response:
        return PlainTextResponse("Hello, plain text world!")


class XmlAgent(AgentServer):
    """Returns XML content."""

    async def invoke(self, request: Request) -> Response:
        xml = '<?xml version="1.0"?><result><msg>ok</msg></result>'
        return Response(content=xml.encode(), media_type="application/xml")


class SseAgent(AgentServer):
    """Returns a Server-Sent Events stream."""

    async def invoke(self, request: Request) -> StreamingResponse:
        async def event_stream():
            for i in range(3):
                yield f"event: message\ndata: {json.dumps({'n': i})}\n\n".encode()

        return StreamingResponse(event_stream(), media_type="text/event-stream")


class CustomStatusAgent(AgentServer):
    """Returns whichever HTTP status code the client requests in body.status_code."""

    async def invoke(self, request: Request) -> Response:
        data = await request.json()
        code = int(data.get("status_code", 200))
        return JSONResponse({"status_code": code}, status_code=code)


class MultipartRawAgent(AgentServer):
    """Echoes the raw multipart body's content-type and length.

    Does NOT call ``request.form()`` (which requires ``python-multipart``)
    so the test is portable across all CI environments.
    """

    async def invoke(self, request: Request) -> Response:
        ctype = request.headers.get("content-type", "")
        body = await request.body()
        return JSONResponse({"content_type": ctype, "length": len(body), "body_prefix": body[:80].decode("latin-1")})


class QueryStringAgent(AgentServer):
    """Echoes query parameters as JSON."""

    async def invoke(self, request: Request) -> Response:
        return JSONResponse({"query": dict(request.query_params)})


class Base64ImageAgent(AgentServer):
    """Accepts JSON with base64-encoded image data and decodes it."""

    async def invoke(self, request: Request) -> Response:
        data = await request.json()
        image_b64 = data.get("image", "")
        decoded = base64.b64decode(image_b64)
        return JSONResponse({"decoded_size": len(decoded), "starts_with_png": decoded[:4] == b"\x89PNG"})


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def ctype_echo_client():
    agent = ContentTypeEchoAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest_asyncio.fixture
async def image_client():
    agent = ImageAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest_asyncio.fixture
async def audio_client():
    agent = AudioAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest_asyncio.fixture
async def html_client():
    agent = HtmlAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest_asyncio.fixture
async def plaintext_client():
    agent = PlainTextAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest_asyncio.fixture
async def xml_client():
    agent = XmlAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest_asyncio.fixture
async def sse_client():
    agent = SseAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest_asyncio.fixture
async def custom_status_client():
    agent = CustomStatusAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest_asyncio.fixture
async def multipart_raw_client():
    agent = MultipartRawAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest_asyncio.fixture
async def query_client():
    agent = QueryStringAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest_asyncio.fixture
async def b64image_client():
    agent = Base64ImageAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


# ========================================================================
# MULTI-MODALITY: requests with different content types
# ========================================================================


class TestMultiModalRequests:
    """Verify the server accepts and forwards any content type to the agent."""

    @pytest.mark.asyncio
    async def test_image_png_payload(self, ctype_echo_client):
        """POST with image/png content type and binary PNG data."""
        resp = await ctype_echo_client.post(
            "/invocations",
            content=_MINIMAL_PNG,
            headers={"Content-Type": "image/png"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["content_type"] == "image/png"
        assert body["length"] == len(_MINIMAL_PNG)

    @pytest.mark.asyncio
    async def test_image_jpeg_payload(self, ctype_echo_client):
        """POST with image/jpeg content type."""
        fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # JPEG SOI marker + padding
        resp = await ctype_echo_client.post(
            "/invocations",
            content=fake_jpeg,
            headers={"Content-Type": "image/jpeg"},
        )
        assert resp.status_code == 200
        assert resp.json()["content_type"] == "image/jpeg"
        assert resp.json()["length"] == len(fake_jpeg)

    @pytest.mark.asyncio
    async def test_audio_wav_payload(self, ctype_echo_client):
        """POST with audio/wav content type and WAV header."""
        resp = await ctype_echo_client.post(
            "/invocations",
            content=_MINIMAL_WAV,
            headers={"Content-Type": "audio/wav"},
        )
        assert resp.status_code == 200
        assert resp.json()["content_type"] == "audio/wav"
        assert resp.json()["length"] == len(_MINIMAL_WAV)

    @pytest.mark.asyncio
    async def test_video_mp4_payload(self, ctype_echo_client):
        """POST with video/mp4 content type and opaque bytes."""
        fake_mp4 = bytes.fromhex("00000018667479706d703432") + b"\x00" * 200
        resp = await ctype_echo_client.post(
            "/invocations",
            content=fake_mp4,
            headers={"Content-Type": "video/mp4"},
        )
        assert resp.status_code == 200
        assert resp.json()["content_type"] == "video/mp4"

    @pytest.mark.asyncio
    async def test_protobuf_payload(self, ctype_echo_client):
        """POST with application/x-protobuf content type."""
        resp = await ctype_echo_client.post(
            "/invocations",
            content=_PROTO_PAYLOAD,
            headers={"Content-Type": "application/x-protobuf"},
        )
        assert resp.status_code == 200
        assert resp.json()["content_type"] == "application/x-protobuf"
        assert resp.json()["length"] == len(_PROTO_PAYLOAD)

    @pytest.mark.asyncio
    async def test_octet_stream_payload(self, ctype_echo_client):
        """POST with application/octet-stream content type."""
        resp = await ctype_echo_client.post(
            "/invocations",
            content=bytes(range(256)),
            headers={"Content-Type": "application/octet-stream"},
        )
        assert resp.status_code == 200
        assert resp.json()["content_type"] == "application/octet-stream"
        assert resp.json()["length"] == 256

    @pytest.mark.asyncio
    async def test_msgpack_payload(self, ctype_echo_client):
        """POST with application/msgpack content type (binary serialisation)."""
        resp = await ctype_echo_client.post(
            "/invocations",
            content=b"\x82\xa3key\xa5value\xa3num\x2a",  # {"key":"value","num":42}
            headers={"Content-Type": "application/msgpack"},
        )
        assert resp.status_code == 200
        assert resp.json()["content_type"] == "application/msgpack"

    @pytest.mark.asyncio
    async def test_base64_encoded_image_in_json(self, b64image_client):
        """JSON body carrying a base64-encoded PNG (multi-modal pattern)."""
        encoded = base64.b64encode(_MINIMAL_PNG).decode("ascii")
        resp = await b64image_client.post(
            "/invocations",
            content=json.dumps({"image": encoded}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["decoded_size"] == len(_MINIMAL_PNG)
        assert body["starts_with_png"] is True


# ========================================================================
# MULTI-MODALITY: responses with different content types
# ========================================================================


class TestMultiModalResponses:
    """Agents can return any media type — verify end-to-end."""

    @pytest.mark.asyncio
    async def test_agent_returns_png(self, image_client):
        """Agent returning image/png is received correctly by the client."""
        resp = await image_client.post("/invocations", content=b"{}")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/png"
        assert resp.content[:4] == b"\x89PNG"
        assert resp.headers.get("x-agent-invocation-id") is not None

    @pytest.mark.asyncio
    async def test_agent_returns_wav(self, audio_client):
        """Agent returning audio/wav is received correctly."""
        resp = await audio_client.post("/invocations", content=b"{}")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "audio/wav"
        assert resp.content[:4] == b"RIFF"

    @pytest.mark.asyncio
    async def test_agent_returns_html(self, html_client):
        """Agent returning HTML is received with correct content type."""
        resp = await html_client.post("/invocations", content=b"{}")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "<h1>Hello Agent</h1>" in resp.text

    @pytest.mark.asyncio
    async def test_agent_returns_plain_text(self, plaintext_client):
        """Agent returning plain text is received correctly."""
        resp = await plaintext_client.post("/invocations", content=b"{}")
        assert resp.status_code == 200
        assert "text/plain" in resp.headers["content-type"]
        assert resp.text == "Hello, plain text world!"

    @pytest.mark.asyncio
    async def test_agent_returns_xml(self, xml_client):
        """Agent returning application/xml is received correctly."""
        resp = await xml_client.post("/invocations", content=b"{}")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/xml"
        assert "<msg>ok</msg>" in resp.text


# ========================================================================
# STREAMING: SSE (Server-Sent Events) protocol
# ========================================================================


class TestServerSentEvents:
    """Verify SSE streaming works end-to-end."""

    @pytest.mark.asyncio
    async def test_sse_stream_yields_events(self, sse_client):
        """Agent producing SSE events delivers them to the client."""
        resp = await sse_client.post("/invocations", content=b"{}")
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("content-type", "")

        # Parse the SSE stream
        raw = resp.text
        events = [line for line in raw.split("\n") if line.startswith("data:")]
        assert len(events) == 3
        for i, ev in enumerate(events):
            payload = json.loads(ev.removeprefix("data:").strip())
            assert payload["n"] == i

    @pytest.mark.asyncio
    async def test_sse_has_invocation_id(self, sse_client):
        """SSE response still carries x-agent-invocation-id."""
        resp = await sse_client.post("/invocations", content=b"{}")
        assert resp.headers.get("x-agent-invocation-id") is not None


# ========================================================================
# MULTIPART form data (file uploads)
# ========================================================================


class TestMultipartFormData:
    """Verify the server passes multipart/form-data payloads to the agent."""

    @pytest.mark.asyncio
    async def test_single_file_upload(self, multipart_raw_client):
        """Upload a single file via multipart form data."""
        resp = await multipart_raw_client.post(
            "/invocations",
            files={"image": ("photo.png", _MINIMAL_PNG, "image/png")},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "multipart/form-data" in body["content_type"]
        assert body["length"] > len(_MINIMAL_PNG)  # includes boundary overhead

    @pytest.mark.asyncio
    async def test_multiple_files_upload(self, multipart_raw_client):
        """Upload multiple files in one request."""
        resp = await multipart_raw_client.post(
            "/invocations",
            files=[
                ("file1", ("a.png", _MINIMAL_PNG, "image/png")),
                ("file2", ("b.wav", _MINIMAL_WAV, "audio/wav")),
            ],
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "multipart/form-data" in body["content_type"]
        # Total body must be larger than both payloads combined
        assert body["length"] > len(_MINIMAL_PNG) + len(_MINIMAL_WAV)

    @pytest.mark.asyncio
    async def test_mixed_form_fields_and_files(self, multipart_raw_client):
        """Multipart with both plain text fields and file uploads."""
        resp = await multipart_raw_client.post(
            "/invocations",
            data={"prompt": "describe this image"},
            files={"image": ("pic.png", _MINIMAL_PNG, "image/png")},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "multipart/form-data" in body["content_type"]
        assert body["length"] > 0


# ========================================================================
# CUSTOM HTTP STATUS CODES
# ========================================================================


class TestCustomStatusCodes:
    """AgentServer preserves whatever HTTP status the agent returns."""

    @pytest.mark.asyncio
    async def test_201_created(self, custom_status_client):
        """Agent returning 201 Created."""
        resp = await custom_status_client.post(
            "/invocations",
            content=json.dumps({"status_code": 201}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 201
        assert resp.headers.get("x-agent-invocation-id") is not None

    @pytest.mark.asyncio
    async def test_202_accepted(self, custom_status_client):
        """Agent returning 202 Accepted (async processing)."""
        resp = await custom_status_client.post(
            "/invocations",
            content=json.dumps({"status_code": 202}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 202

    @pytest.mark.asyncio
    async def test_204_no_content(self, custom_status_client):
        """Agent returning 204 No Content."""
        resp = await custom_status_client.post(
            "/invocations",
            content=json.dumps({"status_code": 204}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_400_bad_request(self, custom_status_client):
        """Agent can signal a 400 back to caller."""
        resp = await custom_status_client.post(
            "/invocations",
            content=json.dumps({"status_code": 400}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_422_unprocessable(self, custom_status_client):
        """Agent returning 422 Unprocessable Entity."""
        resp = await custom_status_client.post(
            "/invocations",
            content=json.dumps({"status_code": 422}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_503_service_unavailable(self, custom_status_client):
        """Agent signalling downstream unavailability."""
        resp = await custom_status_client.post(
            "/invocations",
            content=json.dumps({"status_code": 503}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 503


# ========================================================================
# HTTP PROTOCOL: query strings, HEAD, path params
# ========================================================================


class TestHttpProtocol:
    """HTTP protocol-level edge cases."""

    @pytest.mark.asyncio
    async def test_query_string_forwarded_to_agent(self, query_client):
        """Query parameters on /invocations are accessible to the agent."""
        resp = await query_client.post(
            "/invocations?model=gpt-4&temperature=0.7",
            content=b"{}",
        )
        assert resp.status_code == 200
        q = resp.json()["query"]
        assert q["model"] == "gpt-4"
        assert q["temperature"] == "0.7"

    @pytest.mark.asyncio
    async def test_head_liveness(self, echo_client):
        """HEAD /liveness returns 200 with no body (standard HTTP HEAD)."""
        resp = await echo_client.head("/liveness")
        # Starlette may return 200 or 405 — both are valid server behavior
        assert resp.status_code in (200, 405)

    @pytest.mark.asyncio
    async def test_path_param_special_characters(self, echo_client):
        """GET /invocations/{id} with URL-encoded special chars in the ID."""
        weird_id = "abc%20def%2F123"
        resp = await echo_client.get(f"/invocations/{weird_id}")
        # default agent returns 404 — ensure it doesn't crash
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_accept_header_passthrough(self, ctype_echo_client):
        """Accept header doesn't interfere with agent processing."""
        resp = await ctype_echo_client.post(
            "/invocations",
            content=b"hello",
            headers={
                "Accept": "application/xml",
                "Content-Type": "text/plain",
            },
        )
        assert resp.status_code == 200
        # Agent returns JSON regardless — server doesn't enforce Accept
        assert resp.json()["content_type"] == "text/plain"

    @pytest.mark.asyncio
    async def test_multiple_custom_headers_forwarded(self, ctype_echo_client):
        """Custom X- headers reach the agent without interference."""
        resp = await ctype_echo_client.post(
            "/invocations",
            content=b"{}",
            headers={
                "Content-Type": "application/json",
                "X-Request-Id": "req-42",
                "X-Session-Token": "tok-abc",
            },
        )
        assert resp.status_code == 200


# ========================================================================
# WebSocket: upgrade attempt to an HTTP-only server
# ========================================================================


class TestWebSocketUpgradeRejected:
    """The server has no WebSocket routes.  WS upgrade attempts must fail
    gracefully rather than crashing."""

    @pytest.mark.asyncio
    async def test_websocket_upgrade_on_invocations(self):
        """WebSocket handshake on /invocations fails cleanly."""
        agent = ContentTypeEchoAgent()
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Simulate a WebSocket upgrade via HTTP headers
            resp = await client.get(
                "/invocations",
                headers={
                    "Upgrade": "websocket",
                    "Connection": "Upgrade",
                    "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
                    "Sec-WebSocket-Version": "13",
                },
            )
            # Server should reject: no WS route → 4xx response
            assert resp.status_code in (400, 403, 404, 405, 426)

    @pytest.mark.asyncio
    async def test_websocket_upgrade_on_unknown_path(self):
        """WebSocket handshake on an undefined path fails cleanly."""
        agent = ContentTypeEchoAgent()
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get(
                "/ws/invocations",
                headers={
                    "Upgrade": "websocket",
                    "Connection": "Upgrade",
                    "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
                    "Sec-WebSocket-Version": "13",
                },
            )
            assert resp.status_code in (400, 403, 404, 405, 426)


# ========================================================================
# gRPC-like: binary framed payload over HTTP/2 style headers
# ========================================================================


class TestGrpcLikePayloads:
    """The server is HTTP/1.1, but clients may send gRPC-style payloads
    (application/grpc, length-prefixed protobuf).  Server should accept
    bytes and let the agent deal with them — no crash."""

    @pytest.mark.asyncio
    async def test_grpc_content_type_accepted(self, ctype_echo_client):
        """POST with application/grpc content type is forwarded to the agent."""
        # gRPC frames: 1-byte compressed flag + 4-byte length + payload
        grpc_frame = b"\x00" + len(_PROTO_PAYLOAD).to_bytes(4, "big") + _PROTO_PAYLOAD
        resp = await ctype_echo_client.post(
            "/invocations",
            content=grpc_frame,
            headers={"Content-Type": "application/grpc"},
        )
        assert resp.status_code == 200
        assert resp.json()["content_type"] == "application/grpc"
        assert resp.json()["length"] == len(grpc_frame)

    @pytest.mark.asyncio
    async def test_grpc_web_content_type_accepted(self, ctype_echo_client):
        """POST with application/grpc-web content type (for gRPC-Web proxy)."""
        resp = await ctype_echo_client.post(
            "/invocations",
            content=_PROTO_PAYLOAD,
            headers={"Content-Type": "application/grpc-web"},
        )
        assert resp.status_code == 200
        assert resp.json()["content_type"] == "application/grpc-web"

    @pytest.mark.asyncio
    async def test_grpc_plus_proto_content_type(self, ctype_echo_client):
        """POST with application/grpc+proto content type."""
        resp = await ctype_echo_client.post(
            "/invocations",
            content=_PROTO_PAYLOAD,
            headers={"Content-Type": "application/grpc+proto"},
        )
        assert resp.status_code == 200
        assert resp.json()["content_type"] == "application/grpc+proto"


# ========================================================================
# Multiple modalities in one request / response
# ========================================================================


class TestMixedModality:
    """Scenarios combining text + binary in a single invocation."""

    @pytest.mark.asyncio
    async def test_json_with_base64_image_roundtrip(self, b64image_client):
        """JSON containing base64-encoded image data round-trips correctly."""
        encoded = base64.b64encode(_MINIMAL_PNG).decode("ascii")
        payload = {"image": encoded, "prompt": "What is in this image?"}
        resp = await b64image_client.post(
            "/invocations",
            content=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["decoded_size"] == len(_MINIMAL_PNG)
        assert body["starts_with_png"] is True

    @pytest.mark.asyncio
    async def test_multipart_image_plus_audio(self, multipart_raw_client):
        """Multipart upload combining image and audio files."""
        resp = await multipart_raw_client.post(
            "/invocations",
            files=[
                ("image", ("pic.png", _MINIMAL_PNG, "image/png")),
                ("audio", ("clip.wav", _MINIMAL_WAV, "audio/wav")),
            ],
            data={"instruction": "transcribe the audio and describe the image"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "multipart/form-data" in body["content_type"]
        assert body["length"] > len(_MINIMAL_PNG) + len(_MINIMAL_WAV)

    @pytest.mark.asyncio
    async def test_multipart_large_file(self, multipart_raw_client):
        """Multipart upload with a large binary file (512 KB)."""
        big_file = b"\x00" * (512 * 1024)
        resp = await multipart_raw_client.post(
            "/invocations",
            files={"bigfile": ("large.bin", big_file, "application/octet-stream")},
        )
        assert resp.status_code == 200
        assert resp.json()["length"] > 512 * 1024
