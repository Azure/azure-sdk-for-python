# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Models for platform-directed agent process lifecycle hooks."""

import asyncio  # pylint: disable=do-not-import-asyncio
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Awaitable, Callable, Optional


@dataclass(frozen=True, init=False)
class AgentSessionContext:
    """Session context supplied after a process is restored from a snapshot.

    :param session_id: Opaque identifier for the session served by the process.
    :type session_id: str
    :param restore_id: Opaque identifier for this process materialization.
    :type restore_id: str
    :param session_env_overrides: Sparse environment values that differ from
        the captured process.
    :type session_env_overrides: Mapping[str, str]
    """

    session_id: str
    restore_id: str
    session_env_overrides: Mapping[str, str]

    def __init__(
        self,
        session_id: str,
        restore_id: str,
        session_env_overrides: Optional[Mapping[str, str]] = None,
    ) -> None:
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "restore_id", restore_id)
        object.__setattr__(
            self,
            "session_env_overrides",
            MappingProxyType(dict(session_env_overrides or {})),
        )


@dataclass
class _LifecycleState:
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    before_snapshot_fn: Optional[Callable[[], Awaitable[None]]] = None
    after_restore_fn: Optional[Callable[[AgentSessionContext], Awaitable[None]]] = None
    before_snapshot_completed: bool = False
    restored_session_context: Optional[AgentSessionContext] = None
    completed_restore_ids: set[str] = field(default_factory=set)
    captured_environment_values: dict[str, Optional[str]] = field(default_factory=dict)
    applied_environment_variables: set[str] = field(default_factory=set)
