# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unified storage paths for agentserver durable subsystems.

Public module — both ``azure-ai-agentserver-core`` (durable tasks) and
``azure-ai-agentserver-responses`` (response store + stream store) resolve
their on-disk storage locations through this single helper. The unified
layout is::

    <root>/
      tasks/      ← durable task records (core)
      streams/    ← SSE event store (responses)
      responses/  ← response object store (responses)

where ``<root>`` is ``${AGENTSERVER_DURABLE_ROOT:-~/.durable}``.

The single env var ``AGENTSERVER_DURABLE_ROOT`` controls the root for
all three subdirectories — there is intentionally no per-subdir override.
Operators wanting per-subdir paths should symlink the desired locations
into the root.

replaces the pre-migration per-subsystem
env vars:

  - ``AGENTSERVER_DURABLE_TASKS_PATH`` (was: ``~/.durable-tasks/``)
  - ``AGENTSERVER_STREAM_STORE_PATH``  (was: ``<tempdir>/agentserver_streams``)
  - ``AGENTSERVER_RESPONSE_STORE_PATH`` (was: no default; required for non-mem store)

All three legacy env vars are deleted (not deprecated). The unified
``AGENTSERVER_DURABLE_ROOT`` is the only operator knob.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

# Public type alias for the kinds of storage subdirectories the agentserver
# durable subsystems own.
DurableSubdir = Literal["tasks", "streams", "responses"]

# Default root when ``AGENTSERVER_DURABLE_ROOT`` is unset.
_DEFAULT_ROOT_RELATIVE = ".durable"

# Env var that overrides the root. Single var covers all subdirs.
DURABLE_ROOT_ENV_VAR = "AGENTSERVER_DURABLE_ROOT"

# The full set of valid subdirectory kinds.
_VALID_SUBDIRS: frozenset[str] = frozenset({"tasks", "streams", "responses"})


def resolve_durable_root() -> Path:
    """Resolve the root directory for agentserver durable storage.

    Returns ``Path(os.environ['AGENTSERVER_DURABLE_ROOT'])`` if the env
    var is set; otherwise ``Path.home() / ".durable"``.

    :returns: The resolved root path.
    :rtype: Path
    """
    env_value = os.environ.get(DURABLE_ROOT_ENV_VAR)
    if env_value:
        return Path(env_value)
    return Path.home() / _DEFAULT_ROOT_RELATIVE


def resolve_durable_subdir(kind: DurableSubdir) -> Path:
    """Resolve the on-disk path for a specific durable storage subdirectory.

    :param kind: One of ``"tasks"`` (core), ``"streams"`` (responses),
        ``"responses"`` (responses).
    :type kind: DurableSubdir
    :returns: The resolved absolute path. Created lazily on first write
        by the caller — this helper does not mkdir.
    :rtype: Path
    :raises ValueError: If ``kind`` is not one of the valid subdir kinds.
    """
    if kind not in _VALID_SUBDIRS:
        raise ValueError(f"Unknown durable subdir kind: {kind!r}. " f"Valid kinds: {sorted(_VALID_SUBDIRS)}")
    return resolve_durable_root() / kind


__all__ = [
    "DurableSubdir",
    "DURABLE_ROOT_ENV_VAR",
    "resolve_durable_root",
    "resolve_durable_subdir",
]
