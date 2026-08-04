# ------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------
"""Spec 033 Phase 4 (FR-007) import-lint gate.

Responses production source MUST NOT reach into the core package's private
modules that were promoted to public API in Phase 4. It consumes them through
the supported public surface instead:

* ``core._platform_headers`` → ``core.platform_headers``
* ``core._config`` (``AgentConfig``) → ``core`` (top-level)
* ``core._request_id`` (``REQUEST_ID_STATE_KEY``) → ``core.read_request_id``
* ``TaskRun._queued_cancel_callback`` → ``TaskRun.is_queued``

Scope is production source under ``azure/`` (white-box tests may still import
internals). The two reaches deliberately out of FR-007's enumerated scope —
the same-package ``ResponseContext._task_context`` attribute and the
defensively-coded ``core.tasks._context._ExitForRecovery`` sentinel type that
backs the public ``ExitForRecoverySignal`` alias — are documented groundings and
are not asserted here.
"""
from __future__ import annotations

import pathlib

import azure.ai.agentserver.responses as responses_pkg

_SRC_ROOT = pathlib.Path(responses_pkg.__file__).parent

# The FR-007-enumerated private core modules that were promoted to public API.
_FORBIDDEN_PRIVATE_MODULE_IMPORTS = (
    "azure.ai.agentserver.core._platform_headers",
    "azure.ai.agentserver.core._config",
    "azure.ai.agentserver.core._request_id",
)


def _iter_source_files():
    for path in _SRC_ROOT.rglob("*.py"):
        # Skip generated model code (vendored, not hand-authored layering).
        if "_generated" in path.parts:
            continue
        yield path


def test_no_imports_from_promoted_private_core_modules() -> None:
    offenders: list[str] = []
    for path in _iter_source_files():
        text = path.read_text(encoding="utf-8")
        for forbidden in _FORBIDDEN_PRIVATE_MODULE_IMPORTS:
            if f"import {forbidden} " in text or f"from {forbidden} " in text or f"from {forbidden}\n" in text:
                offenders.append(f"{path.relative_to(_SRC_ROOT)} → {forbidden}")
    assert not offenders, "FR-007: responses source still imports promoted private core modules:\n" + "\n".join(
        offenders
    )


def test_no_queued_cancel_callback_reach() -> None:
    offenders: list[str] = []
    for path in _iter_source_files():
        if "_queued_cancel_callback" in path.read_text(encoding="utf-8"):
            offenders.append(str(path.relative_to(_SRC_ROOT)))
    assert not offenders, (
        "FR-007: responses source still reaches TaskRun._queued_cancel_callback "
        "(use the public TaskRun.is_queued):\n" + "\n".join(offenders)
    )
