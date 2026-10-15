# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Composition guard for the responses host startup.

When ``resilient_background=True`` AND the caller EXPLICITLY supplied a
``store=`` argument that does not persist across crashes,
``ResponsesAgentServerHost`` construction MUST raise an explicit,
descriptive error naming the offending store — NOT start up and silently
degrade.

The guard intentionally does NOT fire for the default-only path
(``store=None`` → ``FileResponseStore`` under
``${AGENTSERVER_STATE_ROOT}/responses/`` per spec 024 Phase 3a). That
path is persistent and safe for ``resilient_background=True``. Streaming
resilience is provided independently by the process-wide streams
registry, configured by the host at startup against the same root.
"""

from __future__ import annotations

import os
from typing import Iterator

import pytest

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


def test_resilient_background_explicit_inmemory_store_raises_at_startup() -> None:
    """Composition guard: explicit ``store=InMemoryResponseProvider()`` with
    ``resilient_background=True`` MUST raise — operator deliberately chose
    a non-persistent store while opting into crash recovery, which is
    contradictory and the framework refuses to silently degrade.
    """
    from azure.ai.agentserver.responses.store._memory import (
        InMemoryResponseProvider,
    )

    options = ResponsesServerOptions(resilient_background=True)
    with pytest.raises(ValueError) as excinfo:
        ResponsesAgentServerHost(
            options=options,
            store=InMemoryResponseProvider(),
        )
    msg = str(excinfo.value)
    assert "resilient_background" in msg
    assert (
        "InMemoryResponseProvider" in msg or "not persist" in msg
    ), f"Error must name the missing/non-resilient store; got: {msg}"


def test_resilient_background_with_custom_nonresilient_store_raises_at_startup() -> None:
    """Composition guard: explicit ``store=`` with ``resilient_background=True``
    that does not persist across crashes MUST raise — the operator
    deliberately chose a non-persistent store while opting into crash
    recovery, which is contradictory and the framework refuses to silently
    degrade. The guard only inspects the response store; streaming
    resilience is owned by the streams registry configured at startup,
    so any explicit non-persistent store fails the same way.
    """
    from azure.ai.agentserver.responses.store._memory import (
        InMemoryResponseProvider,
    )

    class _NonResilientStore(InMemoryResponseProvider):
        """Subclass of the non-persistent in-memory store."""

    options = ResponsesServerOptions(resilient_background=True)
    with pytest.raises(ValueError) as excinfo:
        ResponsesAgentServerHost(options=options, store=_NonResilientStore())
    msg = str(excinfo.value)
    assert "resilient_background" in msg
    assert "_NonResilientStore" in msg or "not persist" in msg, msg


def test_resilient_background_false_with_inmemory_does_not_raise() -> None:
    """Composition guard is gated on ``resilient_background=True``. With it
    disabled, the default in-memory provider is permitted.
    """
    options = ResponsesServerOptions(resilient_background=False)
    host = ResponsesAgentServerHost(options=options)
    assert host is not None


def test_resilient_background_true_with_default_inmemory_does_not_raise() -> None:
    """The DEFAULT path (no explicit ``store=``) is not considered an
    operator misconfiguration — it satisfies in-process tests and local
    development. The guard only fires when the operator EXPLICITLY
    supplied a non-resilient store. Backward-compat regression guard so
    the existing test/dev workflows continue to work.
    """
    options = ResponsesServerOptions(resilient_background=True)
    host = ResponsesAgentServerHost(options=options)
    assert host is not None


def test_resilient_background_true_with_env_store_paths_does_not_raise(
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
        options = ResponsesServerOptions(resilient_background=True)
        host = ResponsesAgentServerHost(options=options)
        assert host is not None
    finally:
        os.environ.pop("AGENTSERVER_STATE_ROOT", None)
