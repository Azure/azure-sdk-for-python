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
    "import_all": 5008,
    "mypy": 5003,
    "next-mypy": 5020,
    "pylint": 5002,
    "next-pylint": 5002,
    "ruff": 5022,
    "pyright": 5018,
    "next-pyright": 5021,
    "verifytypes": 5019,
    "apistub": 5014,
    "verify_sdist": 5010,
    "verify_whl": 5009,
    "whl": DEFAULT_PROXY_PORT,
    "whl_no_aio": 5004,
    "sdist": 5005,
    "samples": 5016,
    "devtest": 5011,
    "latestdependency": 5012,
    "mindependency": 5013,
    "bandit": 5015,
    "verify_keywords": 5005,
    "generate": DEFAULT_PROXY_PORT,
    "breaking": 5017,
    "sphinx": 5007,
    "next-sphinx": 5023,
    "optional": 5018,
    "black": DEFAULT_PROXY_PORT,
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
