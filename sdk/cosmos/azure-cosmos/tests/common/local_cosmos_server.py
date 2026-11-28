# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""A small local HTTP server that stands in for a Cosmos DB account, so tests can check the exact requests the SDK sends."""

from contextlib import contextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from types import SimpleNamespace


@dataclass(frozen=True)
class RecordedRequest:
    """One request received by the server. Header names are stored in lower case."""

    method: str
    path: str
    headers: dict[str, str]
    body: bytes


@contextmanager
def local_cosmos_server(respond=None):
    """Starts a local server and records every request it receives.

    Yields an object with ``endpoint`` (the URL to give the client) and ``requests``
    (the recorded requests). The server answers the client's account lookup
    (GET /) itself, as a single-region account in East US. Every other request is
    passed to ``respond(request)``, which returns an HTTP status and a body that can
    be turned into JSON. If ``respond`` is not given, those requests get HTTP 500.

    The server supports HTTP/1.x only, so callers run the test in a separate
    process with AZURE_COSMOS_CONNECTION_POOL_IS_HTTP2_ALLOWED set to "false".
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
        assert not worker.is_alive(), "Local test server did not stop"
