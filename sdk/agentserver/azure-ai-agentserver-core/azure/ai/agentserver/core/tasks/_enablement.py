# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Explicit opt-in switch for the resilient task subsystem.

The resilient ``TaskManager`` is constructed by ``AgentServerHost`` **only when
this switch is on**. It is the single source of truth for the durable task
subsystem: when the switch is off, no ``TaskManager`` is installed, so
``get_task_manager()`` raises
:class:`~azure.ai.agentserver.core.tasks.TaskManagerNotInitialized` and
``.run()`` / ``.start()`` cannot run a task. When on, the manager is
constructed and the startup crash-recovery scan (plus the periodic recovery
loop) runs.

Recovery — and durable tasks as a whole — is therefore strictly opt-in. Merely
declaring a durable task (``@task`` / ``@multi_turn_task``) does **not** turn
the subsystem on; you must set this switch (directly, or via a protocol option
that maps to it, e.g. the responses ``resilient_background`` server option).

The switch is process-global and defaults to ``False``. Set it before
``AgentServerHost`` lifespan startup (typically at import time)::

    from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled

    set_resilient_tasks_enabled(True)
"""

from azure.ai.agentserver.core._experimental import experimental

_RESILIENT_TASKS_ENABLED: bool = False


@experimental
def set_resilient_tasks_enabled(value: bool = True) -> None:
    """Opt in to (or clear) the resilient task subsystem process-wide.

    This gates whether ``AgentServerHost`` constructs the ``TaskManager`` at
    lifespan startup. Setting it to ``True`` constructs the manager, runs the
    startup crash-recovery scan, and starts the periodic recovery loop. When it
    is ``False`` no manager is installed: ``get_task_manager()`` raises
    :class:`~azure.ai.agentserver.core.tasks.TaskManagerNotInitialized` and a
    durable task cannot run (callers such as the responses ``store=true`` path
    swallow that and degrade to non-durable in-process execution).

    Must be called before ``AgentServerHost`` lifespan startup (typically at
    import time) to take effect. Defaults to enabling when called with no
    argument.

    :param value: ``True`` to enable the resilient task subsystem, ``False`` to
        clear.
    :type value: bool
    """
    global _RESILIENT_TASKS_ENABLED  # pylint: disable=global-statement
    _RESILIENT_TASKS_ENABLED = bool(value)


@experimental
def resilient_tasks_enabled() -> bool:
    """Return whether the resilient task subsystem is enabled.

    This is the authoritative gate: a ``False`` return means no ``TaskManager``
    is constructed and durable tasks / crash recovery are inactive (declaring a
    task does NOT change this — the subsystem is opt-in).

    :return: ``True`` if :func:`set_resilient_tasks_enabled` turned it on.
    :rtype: bool
    """
    return _RESILIENT_TASKS_ENABLED
