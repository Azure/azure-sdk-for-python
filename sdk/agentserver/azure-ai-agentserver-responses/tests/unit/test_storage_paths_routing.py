# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 024 Phase 3a RED tests for the responses-side storage rename.

Verifies that ``_configure_streams_registry`` and the response-store
default-path resolution use the unified ``_config.resolve_state_subdir``
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
    """``_routing.py`` must not USE ``AGENTSERVER_STREAM_STORE_PATH`` env var.

    Post-Phase-3a the stream store path is resolved via
    ``_config.resolve_state_subdir('streams')`` — single env var
    ``AGENTSERVER_STATE_ROOT`` covers all three subdirs. Comment
    references to the legacy var (historical migration notes) are
    permitted; only ``os.environ.get(...)`` reads of the legacy name
    are forbidden.
    """
    from azure.ai.agentserver.responses.hosting import _routing

    src = inspect.getsource(_routing)
    # The actual env-var read pattern: os.environ.get("...") or os.getenv("...")
    forbidden_patterns = [
        'environ.get("AGENTSERVER_STREAM_STORE_PATH")',
        "environ.get('AGENTSERVER_STREAM_STORE_PATH')",
        'getenv("AGENTSERVER_STREAM_STORE_PATH")',
        "getenv('AGENTSERVER_STREAM_STORE_PATH')",
    ]
    for pat in forbidden_patterns:
        assert pat not in src, (
            f"spec 024 Phase 3a: _routing.py must not read the legacy "
            f"AGENTSERVER_STREAM_STORE_PATH env var. Found '{pat}' in source. "
            f"Use _config.resolve_state_subdir('streams') instead."
        )
    assert "agentserver_streams" not in src or "deleted" in src.split("agentserver_streams")[0][-100:].lower(), (
        "spec 024 Phase 3a: _routing.py uses the legacy 'agentserver_streams' "
        "temp-dir name as a fallback. Use _config.resolve_state_subdir('streams')."
    )


def test_routing_source_no_legacy_response_store_env_var() -> None:
    """``_routing.py`` must not USE ``AGENTSERVER_RESPONSE_STORE_PATH`` env var."""
    from azure.ai.agentserver.responses.hosting import _routing

    src = inspect.getsource(_routing)
    forbidden_patterns = [
        'environ.get("AGENTSERVER_RESPONSE_STORE_PATH")',
        "environ.get('AGENTSERVER_RESPONSE_STORE_PATH')",
        'getenv("AGENTSERVER_RESPONSE_STORE_PATH")',
        "getenv('AGENTSERVER_RESPONSE_STORE_PATH')",
    ]
    for pat in forbidden_patterns:
        assert pat not in src, (
            f"spec 024 Phase 3a: _routing.py must not read the legacy "
            f"AGENTSERVER_RESPONSE_STORE_PATH env var. Found '{pat}' in source."
        )


def test_streams_dir_uses_unified_root(monkeypatch, tmp_path) -> None:
    """With ``AGENTSERVER_STATE_ROOT`` set, streams use ``<root>/streams/``."""
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    monkeypatch.delenv("AGENTSERVER_STREAM_STORE_PATH", raising=False)

    from azure.ai.agentserver.core import _config

    streams_path = _config.resolve_state_subdir("streams")
    assert streams_path == tmp_path / "streams"


def test_responses_dir_uses_unified_root(monkeypatch, tmp_path) -> None:
    """With ``AGENTSERVER_STATE_ROOT`` set, responses use ``<root>/responses/``."""
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    monkeypatch.delenv("AGENTSERVER_RESPONSE_STORE_PATH", raising=False)

    from azure.ai.agentserver.core import _config

    responses_path = _config.resolve_state_subdir("responses")
    assert responses_path == tmp_path / "responses"
