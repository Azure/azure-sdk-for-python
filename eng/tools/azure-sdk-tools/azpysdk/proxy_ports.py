"""Proxy port assignments for azpysdk checks.

This mapping mirrors the explicit `PROXY_URL` configuration found in
`eng/tox/tox.ini`. Because `dispatch_checks.py` runs multiple checks in
parallel, each check must bind to its own dedicated test-proxy port to avoid
races. Keeping this data in a single module allows both the CLI and the CI
launcher to share the same source of truth without having to parse the tox
configuration file at runtime.
"""

from __future__ import annotations

from typing import Dict, Optional

DEFAULT_PROXY_PORT = 5000
DEFAULT_PROXY_URL = f"http://localhost:{DEFAULT_PROXY_PORT}"

# NOTE: `import_all` shares the same configuration as the legacy `depends`
# tox environment. All other entries match the tox environment names 1:1.
CHECK_PROXY_PORTS: Dict[str, int] = {
    "whl": DEFAULT_PROXY_PORT,
    "sdist": 5001,
    "whl_no_aio": 5002,
    "devtest": 5003,
    "optional": 5004,
    "mindependency": 5005,
    "latestdependency": 5006,
}


def get_proxy_port_for_check(check_name: Optional[str]) -> int:
    """Return the proxy port assigned to the given azpysdk check."""

    if not check_name:
        return DEFAULT_PROXY_PORT
    return CHECK_PROXY_PORTS.get(check_name, DEFAULT_PROXY_PORT)


def get_proxy_url_for_check(check_name: Optional[str]) -> str:
    """Return the proxy URL assigned to the given azpysdk check."""

    port = get_proxy_port_for_check(check_name)
    return f"http://localhost:{port}"


__all__ = [
    "CHECK_PROXY_PORTS",
    "DEFAULT_PROXY_PORT",
    "DEFAULT_PROXY_URL",
    "get_proxy_port_for_check",
    "get_proxy_url_for_check",
]
