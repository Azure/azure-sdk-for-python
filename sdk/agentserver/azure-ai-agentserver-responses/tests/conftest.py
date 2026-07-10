# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Root conftest — ensures the project root is on sys.path so that
``from tests._helpers import …`` works regardless of how pytest is invoked."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


@pytest.fixture(autouse=True, scope="session")
def _prevent_distro_setup():
    """Prevent microsoft-opentelemetry distro from contaminating global OTel
    state during tests.  Without this, CI environments that have the distro
    installed and APPLICATIONINSIGHTS_CONNECTION_STRING set would trigger
    ``use_microsoft_opentelemetry()`` on the first server construction,
    installing a global TracerProvider that breaks later traceparent-
    propagation tests."""
    with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
        yield
