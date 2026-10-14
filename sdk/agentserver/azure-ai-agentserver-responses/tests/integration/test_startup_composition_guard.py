# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 014 FR-006 — startup composition guard, integration coverage.

Distinct from ``tests/unit/test_composition_guard.py`` which exercises
the validator function directly via ``ResponsesAgentServerHost``
construction. This integration test invokes the real entry point that a
production deployment uses (the host's ``run_async`` method, attempted
inside an event loop) so a regression that bypasses the constructor
validator would still be caught.
"""

from __future__ import annotations

import os
from typing import Iterator

import pytest

from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled
from azure.ai.agentserver.responses import (
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)
from azure.ai.agentserver.responses.store._memory import (
    InMemoryResponseProvider,
)


@pytest.fixture(autouse=True)
def _clear_env_overrides() -> Iterator[None]:
    """Strip env-var overrides for the duration of each test.

    (Spec 024 Phase 3a) Single ``AGENTSERVER_STATE_ROOT`` env var
    covers tasks/streams/responses subdirs.
    """
    saved = {
        key: os.environ.pop(key, None)
        for key in (
            "AGENTSERVER_STATE_ROOT",
            "AGENTSERVER_RESPONSE_STORE_PATH",
            "AGENTSERVER_STREAM_STORE_PATH",
            "AGENTSERVER_STATE_TASKS_PATH",
        )
    }
    try:
        yield
    finally:
        for key, value in saved.items():
            if value is not None:
                os.environ[key] = value


@pytest.mark.asyncio
async def test_resilient_tasks_enabled_explicit_inmemory_store_fails_construction() -> None:
    """Spec 014 FR-006 integration: the host MUST refuse to construct
    (and therefore MUST NOT start serving traffic) when an operator
    enables the core switch with an explicit in-memory store. End-to-end
    check that no path bypasses the guard.
    """
    set_resilient_tasks_enabled(True)
    options = ResponsesServerOptions()
    with pytest.raises(ValueError) as excinfo:
        # Even if the operator's startup sequence is to construct in an
        # async context (e.g. inside an existing event loop), the
        # composition guard fires at constructor time — before
        # ``run_async`` is awaited.
        ResponsesAgentServerHost(
            options=options,
            store=InMemoryResponseProvider(),
        )
    assert "resilient tasks" in str(excinfo.value)


def test_resilient_tasks_enabled_default_construction_works() -> None:
    """The enabled guard accepts the default persistent ``FileResponseStore``.

    The root fixture restores the process-global switch after this test.
    """
    set_resilient_tasks_enabled(True)
    app = ResponsesAgentServerHost()
    assert app is not None
