# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Root conftest — ensures the project root is on sys.path so that
``from tests._helpers import …`` works regardless of how pytest is invoked."""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


def pytest_configure(config):
    """Register custom pytest markers used by this package."""
    config.addinivalue_line(
        "markers",
        "live: end-to-end tests that hit a real external SDK (e.g. gh copilot). "
        "Skipped by default; opt in with `-m live` or `--run-live`.",
    )


@pytest.fixture(autouse=True)
def _isolated_durable_tasks_root(tmp_path):
    """Isolate the LocalFileTaskProvider's default storage per test.

    (Spec 013) Without this, the LocalFileTaskProvider defaults to
    ``~/.durable-tasks`` which is shared across all test runs and lets
    in-progress task state leak between tests — when durable_background
    actually works, recovery on startup fires for these stale tasks and
    breaks tests that assume a clean slate.

    Per-test scope (autouse) so every test starts with a clean durable
    task store.

    (Spec 024 Phase 3a) Uses ``AGENTSERVER_DURABLE_ROOT`` — the unified
    env var that controls tasks/responses/streams subdirs together.
    """
    root = tmp_path / "durable-tasks-isolated"
    root.mkdir(parents=True, exist_ok=True)
    prior = os.environ.get("AGENTSERVER_DURABLE_ROOT")
    os.environ["AGENTSERVER_DURABLE_ROOT"] = str(root)
    try:
        yield
    finally:
        if prior is None:
            os.environ.pop("AGENTSERVER_DURABLE_ROOT", None)
        else:
            os.environ["AGENTSERVER_DURABLE_ROOT"] = prior


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
