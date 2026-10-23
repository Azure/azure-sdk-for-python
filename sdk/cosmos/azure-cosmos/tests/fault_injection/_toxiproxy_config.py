# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Local test inputs shared with the runner before any SDK import."""

import hashlib
from pathlib import Path
from urllib.parse import urlsplit

DRIVER_COMMIT = "84e2bb66c9911fa730dc9756c8fc3f9612456344"
VERSION = "2.13.0"
SERVER_SHA256 = "04b710eefd7690c89f7cc67289e3e14618f1ff3c26e4a5f752a34a879b895bab"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_endpoint(endpoint):
    parsed = urlsplit(endpoint)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in ("localhost", "127.0.0.1")
        or parsed.username
        or parsed.password
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Only an HTTPS loopback emulator endpoint is permitted")
    if parsed.port is not None and not 0 < parsed.port < 65536:
        raise ValueError("Invalid emulator port")


def verify_server(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Set TOXIPROXY_SERVER to the installed v{VERSION} Windows x64 server")
    if digest(path) != SERVER_SHA256:
        raise ValueError(f"Toxiproxy server does not match the pinned v{VERSION} Windows x64 checksum")
    return path
