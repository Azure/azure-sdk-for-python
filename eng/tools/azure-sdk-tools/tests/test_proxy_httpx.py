from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest

httpx = pytest.importorskip("httpx")

from devtools_testutils import RecordedTransport, recorded_by_proxy
from devtools_testutils import proxy_testcase


class _PlaybackHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/playback/start":
            self.server.sessions.append("start")
            self.send_response(200)
            self.send_header("x-recording-id", "test-recording")
        elif self.path == "/playback/stop":
            self.server.sessions.append("stop")
            self.send_response(200)
        else:
            self.send_error(404)
            return
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        self.server.requests.append(
            (self.path, self.headers.get("x-recording-upstream-base-uri"), self.headers.get("x-recording-mode"))
        )
        self.send_response(200)
        self.send_header("Content-Length", "8")
        self.end_headers()
        self.wfile.write(b"playback")

    def log_message(self, format, *args):
        pass


class _RejectingProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.requests.append(self.path)
        self.send_error(400)

    do_CONNECT = do_GET

    def log_message(self, format, *args):
        pass


@contextmanager
def _serve(handler):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server.requests = []
    server.sessions = []
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.fixture
def playback_servers(monkeypatch):
    with _serve(_PlaybackHandler) as playback, _serve(_RejectingProxyHandler) as outbound_proxy:
        playback_url = f"http://127.0.0.1:{playback.server_port}"
        outbound_url = f"http://127.0.0.1:{outbound_proxy.server_port}"
        monkeypatch.setenv("PROXY_URL", playback_url)
        monkeypatch.setattr(proxy_testcase, "PLAYBACK_START_URL", f"{playback_url}/playback/start")
        monkeypatch.setattr(proxy_testcase, "PLAYBACK_STOP_URL", f"{playback_url}/playback/stop")
        monkeypatch.setattr(proxy_testcase, "is_live", lambda: False)
        monkeypatch.setattr(proxy_testcase, "is_live_and_not_recording", lambda: False)
        for name in ("HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy", "NO_PROXY", "no_proxy"):
            monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv("https_proxy", raising=False)
        monkeypatch.setenv("HTTPS_PROXY", outbound_url)
        yield playback, outbound_proxy


def test_recorded_httpx_bypasses_https_proxy(playback_servers):
    playback, outbound_proxy = playback_servers
    upstream_url = "https://example.invalid/echo?name=sync"

    with httpx.Client() as client:

        @recorded_by_proxy(RecordedTransport.HTTPX)
        def request(variables=None):
            return client.get(upstream_url)

        response = request()
        assert response.status_code == 200
        assert playback.requests == [("/echo?name=sync", "https://example.invalid", "playback")]
        assert playback.sessions == ["start", "stop"]
        assert outbound_proxy.requests == []

        with pytest.raises(httpx.ProxyError):
            client.get(upstream_url)

    assert outbound_proxy.requests == ["example.invalid:443"]


@pytest.mark.asyncio
async def test_recorded_async_httpx_bypasses_https_proxy(playback_servers, monkeypatch):
    pytest.importorskip("aiohttp")
    from devtools_testutils.aio import recorded_by_proxy_async, proxy_testcase_async

    monkeypatch.setattr(proxy_testcase_async, "is_live_and_not_recording", lambda: False)
    playback, outbound_proxy = playback_servers
    upstream_url = "https://example.invalid/echo?name=async"

    async with httpx.AsyncClient() as client:

        @recorded_by_proxy_async(RecordedTransport.HTTPX)
        async def request(variables=None):
            return await client.get(upstream_url)

        response = await request()
        assert response.status_code == 200
        assert playback.requests == [("/echo?name=async", "https://example.invalid", "playback")]
        assert playback.sessions == ["start", "stop"]
        assert outbound_proxy.requests == []

        with pytest.raises(httpx.ProxyError):
            await client.get(upstream_url)

    assert outbound_proxy.requests == ["example.invalid:443"]
