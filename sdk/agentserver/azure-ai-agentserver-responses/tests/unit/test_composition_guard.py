# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Composition guard for the responses host startup.

When ``durable_background=True`` AND the caller EXPLICITLY supplied a
``store=`` argument that does not persist across crashes,
``ResponsesAgentServerHost`` construction MUST raise an explicit,
descriptive error naming the offending store — NOT start up and silently
degrade.

The guard intentionally does NOT fire for the default-only path
(``store=None`` → ``InMemoryResponseProvider``). That path satisfies
in-process tests and local development that don't need cross-process
recovery; production deployments must supply an explicit persistent
store either via the ``store=`` constructor argument or the
``AGENTSERVER_RESPONSE_STORE_PATH`` env var. Streaming durability is
provided independently by the process-wide streams registry, configured
by the host at startup against ``AGENTSERVER_STREAM_STORE_PATH``.
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
    """Strip ``AGENTSERVER_RESPONSE_STORE_PATH`` and ``AGENTSERVER_STREAM_STORE_PATH``
    for the duration of each test so the explicit-provider path is exercised.
    """
    saved = {
        key: os.environ.pop(key, None)
        for key in (
            "AGENTSERVER_RESPONSE_STORE_PATH",
            "AGENTSERVER_STREAM_STORE_PATH",
        )
    }
    try:
        yield
    finally:
        for key, value in saved.items():
            if value is not None:
                os.environ[key] = value


def test_durable_background_explicit_inmemory_store_raises_at_startup() -> None:
    """Composition guard: explicit ``store=InMemoryResponseProvider()`` with
    ``durable_background=True`` MUST raise — operator deliberately chose
    a non-persistent store while opting into crash recovery, which is
    contradictory and the framework refuses to silently degrade.
    """
    from azure.ai.agentserver.responses.store._memory import (
        InMemoryResponseProvider,
    )

    options = ResponsesServerOptions(durable_background=True)
    with pytest.raises(ValueError) as excinfo:
        ResponsesAgentServerHost(
            options=options,
            store=InMemoryResponseProvider(),
        )
    msg = str(excinfo.value)
    assert "durable_background" in msg
    assert (
        "InMemoryResponseProvider" in msg or "not persist" in msg
    ), f"Error must name the missing/non-durable store; got: {msg}"


def test_durable_background_with_custom_nondurable_store_raises_at_startup() -> None:
    """Composition guard: explicit ``store=`` with ``durable_background=True``
    that does not persist across crashes MUST raise — the operator
    deliberately chose a non-persistent store while opting into crash
    recovery, which is contradictory and the framework refuses to silently
    degrade. The guard only inspects the response store; streaming
    durability is owned by the streams registry configured at startup,
    so any explicit non-persistent store fails the same way.
    """
    from azure.ai.agentserver.responses.store._memory import (
        InMemoryResponseProvider,
    )

    class _NonDurableStore(InMemoryResponseProvider):
        """Subclass of the non-persistent in-memory store."""

    options = ResponsesServerOptions(durable_background=True)
    with pytest.raises(ValueError) as excinfo:
        ResponsesAgentServerHost(options=options, store=_NonDurableStore())
    msg = str(excinfo.value)
    assert "durable_background" in msg
    assert "_NonDurableStore" in msg or "not persist" in msg, msg


def test_durable_background_false_with_inmemory_does_not_raise() -> None:
    """Composition guard is gated on ``durable_background=True``. With it
    disabled, the default in-memory provider is permitted.
    """
    options = ResponsesServerOptions(durable_background=False)
    host = ResponsesAgentServerHost(options=options)
    assert host is not None


def test_durable_background_true_with_default_inmemory_does_not_raise() -> None:
    """The DEFAULT path (no explicit ``store=``) is not considered an
    operator misconfiguration — it satisfies in-process tests and local
    development. The guard only fires when the operator EXPLICITLY
    supplied a non-durable store. Backward-compat regression guard so
    the existing test/dev workflows continue to work.
    """
    options = ResponsesServerOptions(durable_background=True)
    host = ResponsesAgentServerHost(options=options)
    assert host is not None


def test_durable_background_true_with_env_store_paths_does_not_raise(
    tmp_path: object,
) -> None:
    """The ``AGENTSERVER_RESPONSE_STORE_PATH`` + ``AGENTSERVER_STREAM_STORE_PATH``
    operator overrides together satisfy the composition guard:
    ``FileResponseStore`` for the response provider + the registry's
    file-backed replay backing for streams (configured by the host at
    startup against ``AGENTSERVER_STREAM_STORE_PATH``).
    """
    os.environ["AGENTSERVER_RESPONSE_STORE_PATH"] = str(tmp_path / "responses")
    os.environ["AGENTSERVER_STREAM_STORE_PATH"] = str(tmp_path / "streams")
    try:
        options = ResponsesServerOptions(durable_background=True)
        host = ResponsesAgentServerHost(options=options)
        assert host is not None
    finally:
        os.environ.pop("AGENTSERVER_RESPONSE_STORE_PATH", None)
        os.environ.pop("AGENTSERVER_STREAM_STORE_PATH", None)

