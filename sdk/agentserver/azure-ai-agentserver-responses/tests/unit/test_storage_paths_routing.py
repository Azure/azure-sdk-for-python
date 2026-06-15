# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 024 Phase 3a RED tests for the responses-side storage rename.

Verifies that ``_configure_streams_registry`` and the response-store
default-path resolution use the unified ``storage_paths.resolve_durable_subdir``
helper from azure-ai-agentserver-core (NOT the legacy
``AGENTSERVER_STREAM_STORE_PATH`` / ``AGENTSERVER_RESPONSE_STORE_PATH``
env vars).

Test-file rationale (Principle XII §4 non-duplication): no existing test
file covers stream-store / response-store default-path resolution at the
unit level. ``test_streams_bootstrap.py`` checks initialization but not
the new env-var contract.

EXPECTED: RED at this commit; GREEN after Phase 3a implementation
commit lands. See ``sdk/agentserver/specs/024-responses-redesign.md``
Phase 3a steps 16c-16e.
"""

from __future__ import annotations

import inspect
from pathlib import Path


def test_routing_source_no_legacy_stream_env_var() -> None:
    """``_routing.py`` must not reference ``AGENTSERVER_STREAM_STORE_PATH``.

    Post-Phase-3a the stream store path is resolved via
    ``storage_paths.resolve_durable_subdir('streams')`` — single env var
    ``AGENTSERVER_DURABLE_ROOT`` covers all three subdirs.
    """
    from azure.ai.agentserver.responses.hosting import _routing

    src = inspect.getsource(_routing)
    assert "AGENTSERVER_STREAM_STORE_PATH" not in src, (
        "spec 024 Phase 3a: _routing.py must not reference the legacy "
        "AGENTSERVER_STREAM_STORE_PATH env var. Use storage_paths.resolve_durable_subdir."
    )
    assert "agentserver_streams" not in src, (
        "spec 024 Phase 3a: _routing.py must not reference the legacy "
        "'agentserver_streams' temp-dir name. Use storage_paths.resolve_durable_subdir('streams')."
    )


def test_routing_source_no_legacy_response_store_env_var() -> None:
    """``_routing.py`` must not reference ``AGENTSERVER_RESPONSE_STORE_PATH``."""
    from azure.ai.agentserver.responses.hosting import _routing

    src = inspect.getsource(_routing)
    assert "AGENTSERVER_RESPONSE_STORE_PATH" not in src, (
        "spec 024 Phase 3a: _routing.py must not reference the legacy "
        "AGENTSERVER_RESPONSE_STORE_PATH env var. Use storage_paths.resolve_durable_subdir."
    )


def test_streams_dir_uses_unified_root(monkeypatch, tmp_path) -> None:
    """With ``AGENTSERVER_DURABLE_ROOT`` set, streams use ``<root>/streams/``."""
    monkeypatch.setenv("AGENTSERVER_DURABLE_ROOT", str(tmp_path))
    monkeypatch.delenv("AGENTSERVER_STREAM_STORE_PATH", raising=False)

    from azure.ai.agentserver.core import storage_paths

    streams_path = storage_paths.resolve_durable_subdir("streams")
    assert streams_path == tmp_path / "streams"


def test_responses_dir_uses_unified_root(monkeypatch, tmp_path) -> None:
    """With ``AGENTSERVER_DURABLE_ROOT`` set, responses use ``<root>/responses/``."""
    monkeypatch.setenv("AGENTSERVER_DURABLE_ROOT", str(tmp_path))
    monkeypatch.delenv("AGENTSERVER_RESPONSE_STORE_PATH", raising=False)

    from azure.ai.agentserver.core import storage_paths

    responses_path = storage_paths.resolve_durable_subdir("responses")
    assert responses_path == tmp_path / "responses"
