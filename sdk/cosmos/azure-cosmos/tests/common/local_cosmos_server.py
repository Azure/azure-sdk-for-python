# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Loopback HTTP account endpoint for tests exercising the real native transport."""

from contextlib import contextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from types import SimpleNamespace


@dataclass(frozen=True)
class RecordedRequest:
    method: str
    path: str
    headers: dict[str, str]
    body: bytes


@contextmanager
def local_cosmos_server(respond=None):
    """Record requests and delegate non-account responses to ``respond(request)``.

    The callback returns an HTTP status and a JSON-serializable body. Unexpected
    requests fail with HTTP 500. Callers must disable the native HTTP/2 probe in
    an isolated process; this server supports HTTP/1.x only.
    """
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def handle_request(self):
            request = RecordedRequest(
                self.command, self.path,
                {name.lower(): value for name, value in self.headers.items()},
                self.rfile.read(int(self.headers.get("Content-Length", "0"))),
            )
            requests.append(request)
            if request.method == "GET" and request.path == "/":
                location = {"name": "East US", "databaseAccountEndpoint": endpoint}
                status, body = 200, {
                    "id": "test", "_rid": "AQAAAA==", "_self": "",
                    "writableLocations": [location], "readableLocations": [location],
                    "enableMultipleWriteLocations": False,
                    "userConsistencyPolicy": {
                        "defaultConsistencyLevel": "Session",
                        "maxStalenessPrefix": 100, "maxIntervalInSeconds": 5,
                    },
                }
            elif respond is not None:
                status, body = respond(request)
            else:
                status, body = 500, {
                    "code": "UnexpectedRequest",
                    "message": f"Unexpected {request.method} {request.path}",
                }
            data = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        do_GET = handle_request
        do_POST = handle_request
        do_PUT = handle_request
        do_DELETE = handle_request
        do_PATCH = handle_request

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    endpoint = f"http://127.0.0.1:{server.server_port}"
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield SimpleNamespace(endpoint=endpoint, requests=requests)
    finally:
        server.shutdown()
        server.server_close()
        worker.join(3)
        assert not worker.is_alive(), "Loopback server did not stop"
