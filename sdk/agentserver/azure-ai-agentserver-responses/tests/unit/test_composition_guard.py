# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 014 FR-006 — startup composition guard.

When ``durable_background=True`` is configured on the server but a
required supporting provider is absent, ``ResponsesAgentServerHost``
construction MUST raise an explicit, descriptive error naming the
missing provider — NOT start up and silently degrade.

The two required providers for ``durable_background=True``:

- A ``ResponseProviderProtocol`` that persists across process crashes
  (NOT the default ``InMemoryResponseProvider``).
- A ``DurableStreamProviderProtocol``-capable stream provider (so
  reconnecting clients can replay events after recovery).

Both can be explicit constructor arguments or provided via the
``AGENTSERVER_RESPONSE_STORE_PATH`` / ``AGENTSERVER_STREAM_STORE_PATH``
env vars. Without either path, durable_background cannot honour the
contract and the server MUST refuse to start.

Contract sources:
- ``durability-contract.md`` (FR-006 / RD-3).
- ``spec.md`` § Edge cases — provider-missing composition.
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


def test_durable_background_default_inmemory_store_raises_at_startup() -> None:
    """Spec 014 FR-006: durable_background=True with the default in-memory
    response provider MUST raise — in-memory does not survive a crash so
    durable_background cannot honour its recovery promise.
    """
    options = ResponsesServerOptions(durable_background=True)
    with pytest.raises(ValueError) as excinfo:
        ResponsesAgentServerHost(options=options)
    msg = str(excinfo.value)
    # Error message must name the missing component (store) so operators
    # know what to configure.
    assert "durable_background" in msg
    assert (
        "store" in msg.lower()
        or "ResponseProviderProtocol" in msg
        or "InMemoryResponseProvider" in msg
    ), f"Error must name the missing store provider; got: {msg}"


def test_durable_background_with_nondurable_stream_provider_raises_at_startup() -> None:
    """Spec 014 FR-006: durable_background=True with a stream provider that
    does NOT implement ``DurableStreamProviderProtocol`` MUST raise —
    reconnecting clients need durable replay to honour the row-1 stream
    sub-contract.

    We construct the host with a persistent ``ResponseStore`` (so the
    "store missing" branch doesn't fire) but a stream provider that lacks
    the durable-stream protocol. The check must still fire.
    """
    # InMemoryResponseProvider both implements ResponseProviderProtocol and
    # is a stream provider for non-durable scenarios. Wrapping in a custom
    # store that ONLY implements ResponseProviderProtocol triggers the
    # auto-compose path; we want to test the case where the auto-compose
    # is bypassed (e.g. operator explicitly opts out via env var).
    #
    # The simplest way to write this test today: rely on the absence of
    # both env vars + custom non-DurableStreamProviderProtocol store, so
    # the auto-compose path doesn't engage and the check fires.
    from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider

    class _NonDurableStore(InMemoryResponseProvider):
        """Pretends to be a persistent store but only implements the
        non-durable stream protocol."""

    options = ResponsesServerOptions(durable_background=True)
    with pytest.raises(ValueError) as excinfo:
        ResponsesAgentServerHost(options=options, store=_NonDurableStore())
    msg = str(excinfo.value)
    assert "durable_background" in msg
    assert (
        "stream" in msg.lower()
        or "DurableStreamProviderProtocol" in msg
    ), f"Error must name the missing stream provider; got: {msg}"


def test_durable_background_false_with_inmemory_does_not_raise() -> None:
    """Spec 014 FR-006: composition guard is gated on ``durable_background``.
    With it disabled, the default in-memory provider is permitted.
    Regression guard against the guard firing in non-durable mode.
    """
    options = ResponsesServerOptions(durable_background=False)
    # Should not raise.
    host = ResponsesAgentServerHost(options=options)
    assert host is not None


def test_durable_background_true_with_env_store_path_does_not_raise(
    tmp_path: object,
) -> None:
    """The ``AGENTSERVER_RESPONSE_STORE_PATH`` operator override should
    satisfy the composition guard's store requirement (the env var
    selects FileResponseStore which persists across crashes).
    """
    os.environ["AGENTSERVER_RESPONSE_STORE_PATH"] = str(tmp_path)
    try:
        options = ResponsesServerOptions(durable_background=True)
        # Should not raise — FileResponseStore is selected via env var,
        # and the durable_background auto-compose path provides a
        # DurableStreamProviderProtocol via FileStreamProvider.
        host = ResponsesAgentServerHost(options=options)
        assert host is not None
    finally:
        os.environ.pop("AGENTSERVER_RESPONSE_STORE_PATH", None)
