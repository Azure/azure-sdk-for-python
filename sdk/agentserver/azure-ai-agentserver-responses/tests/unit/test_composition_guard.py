# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Composition guard for the responses host startup.

When ``resilient_tasks_enabled=True`` AND the caller EXPLICITLY supplied a
``store=`` argument that does not persist across crashes,
``ResponsesAgentServerHost`` construction MUST raise an explicit,
descriptive error naming the offending store — NOT start up and silently
degrade.

The guard intentionally does NOT fire for the default-only path
(``store=None`` → ``FileResponseStore`` under
``${AGENTSERVER_STATE_ROOT}/responses/`` per spec 024 Phase 3a). That
path is persistent and safe for ``resilient_tasks_enabled=True``. Streaming
resilience is provided independently by the process-wide streams
registry, configured by the host at startup against the same root.
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


@pytest.fixture(autouse=True)
def _clear_env_overrides() -> Iterator[None]:
    """Strip ``AGENTSERVER_STATE_ROOT`` for the duration of each test
    so the explicit-provider path is exercised against the home default.

    (Spec 024 Phase 3a) Single env var covers tasks/streams/responses.
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


def test_resilient_tasks_explicit_inmemory_store_raises_at_startup() -> None:
    """An explicit in-memory store with the core switch enabled MUST raise.

    The operator deliberately chose a non-persistent store while opting into
    crash recovery, which is contradictory and cannot silently degrade.
    """
    from azure.ai.agentserver.responses.store._memory import (
        InMemoryResponseProvider,
    )

    set_resilient_tasks_enabled(True)
    options = ResponsesServerOptions()
    with pytest.raises(ValueError) as excinfo:
        ResponsesAgentServerHost(
            options=options,
            store=InMemoryResponseProvider(),
        )
    msg = str(excinfo.value)
    assert "resilient tasks" in msg
    assert (
        "InMemoryResponseProvider" in msg or "not persist" in msg
    ), f"Error must name the missing/non-resilient store; got: {msg}"


def test_resilient_tasks_with_custom_inmemory_subclass_raises_at_startup() -> None:
    """An explicit in-memory subclass with the core switch enabled MUST raise.

    The guard uses ``isinstance`` so custom subclasses cannot silently weaken
    crash recovery. Streaming resilience is configured separately by the
    process-wide streams registry.
    """
    from azure.ai.agentserver.responses.store._memory import (
        InMemoryResponseProvider,
    )

    class _NonResilientStore(InMemoryResponseProvider):
        """Subclass of the non-persistent in-memory store."""

    set_resilient_tasks_enabled(True)
    options = ResponsesServerOptions()
    with pytest.raises(ValueError) as excinfo:
        ResponsesAgentServerHost(options=options, store=_NonResilientStore())
    msg = str(excinfo.value)
    assert "resilient tasks" in msg
    assert "_NonResilientStore" in msg or "not persist" in msg, msg


def test_resilient_tasks_disabled_with_default_file_store_does_not_raise() -> None:
    """With the switch disabled, the default file-backed store constructs cleanly.

    Omitting ``store=`` resolves to ``FileResponseStore``; this verifies the
    ordinary default composition path, not an in-memory provider.
    """
    set_resilient_tasks_enabled(False)
    options = ResponsesServerOptions()
    host = ResponsesAgentServerHost(options=options)
    assert host is not None


def test_resilient_tasks_enabled_with_default_file_store_does_not_raise() -> None:
    """The default ``FileResponseStore`` satisfies the enabled composition guard.

    Omitting ``store=`` resolves to persistent file-backed storage, so host
    construction must succeed without treating the default as an explicit
    non-persistent provider.
    """
    set_resilient_tasks_enabled(True)
    options = ResponsesServerOptions()
    host = ResponsesAgentServerHost(options=options)
    assert host is not None


def test_resilient_tasks_enabled_with_env_store_paths_does_not_raise(
    tmp_path: object,
) -> None:
    """The ``AGENTSERVER_STATE_ROOT`` operator override satisfies the
    composition guard: ``FileResponseStore`` at ``<root>/responses/`` for
    the response provider + the registry's file-backed replay backing
    for streams at ``<root>/streams/`` (configured by the host at startup
    via the unified storage-paths helper, spec 024 Phase 3a).
    """
    os.environ["AGENTSERVER_STATE_ROOT"] = str(tmp_path)
    try:
        set_resilient_tasks_enabled(True)
        options = ResponsesServerOptions()
        host = ResponsesAgentServerHost(options=options)
        assert host is not None
    finally:
        os.environ.pop("AGENTSERVER_STATE_ROOT", None)
