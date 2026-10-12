import os
import ssl
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator, Optional

import certifi

from ci_tools.logging import logger


def _read_ca_bundle(path: str, source: str) -> bytes:
    try:
        contents = Path(path).read_bytes()
        if not contents:
            raise ValueError("CA bundle is empty")
        ssl.create_default_context(cafile=path)
    except (OSError, ValueError) as exc:
        raise ValueError(f"Invalid {source} CA bundle at {path!r}: {exc}") from exc
    return contents


@contextmanager
def cibuildwheel_environment() -> Iterator[Optional[dict[str, str]]]:
    """Supply temporary proxy trust only to Windows cibuildwheel and its descendants."""
    if sys.platform != "win32" or "NODE_EXTRA_CA_CERTS" not in os.environ:
        yield None
        return

    env = os.environ.copy()
    proxy_roots = _read_ca_bundle(env["NODE_EXTRA_CA_CERTS"], "NODE_EXTRA_CA_CERTS")
    ssl_source = "SSL_CERT_FILE" if "SSL_CERT_FILE" in env else "certifi"
    ssl_path = env.get("SSL_CERT_FILE", certifi.where())
    ssl_roots = _read_ca_bundle(ssl_path, ssl_source)

    # Requests prefers these environment overrides; pip also supports PIP_CERT.
    requests_source = next(
        (name for name in ("REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "PIP_CERT") if env.get(name)),
        None,
    )
    requests_path = env[requests_source] if requests_source else ssl_path
    requests_roots = (
        ssl_roots if requests_path == ssl_path else _read_ca_bundle(requests_path, requests_source or ssl_source)
    )

    with TemporaryDirectory(prefix="cibw-proxy-ca-") as directory:
        ssl_bundle = Path(directory) / "ssl.pem"
        ssl_bundle.write_bytes(ssl_roots + b"\n" + proxy_roots + b"\n")
        ssl.create_default_context(cafile=str(ssl_bundle))
        env["SSL_CERT_FILE"] = str(ssl_bundle)

        if requests_path == ssl_path:
            env["REQUESTS_CA_BUNDLE"] = str(ssl_bundle)
        else:
            requests_bundle = Path(directory) / "requests.pem"
            requests_bundle.write_bytes(requests_roots + b"\n" + proxy_roots + b"\n")
            ssl.create_default_context(cafile=str(requests_bundle))
            env["REQUESTS_CA_BUNDLE"] = str(requests_bundle)

        logger.info("Using temporary network-isolation proxy CA bundles for Windows cibuildwheel.")
        yield env
