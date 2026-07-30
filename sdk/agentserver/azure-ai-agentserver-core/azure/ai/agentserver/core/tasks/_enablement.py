# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Explicit force-enable switch for the resilient task recovery scan.

The resilient ``TaskManager`` is always constructed by ``AgentServerHost`` (a
cheap, in-memory object that makes no task-store calls), so ``get_task_manager``
and ``.run()`` / ``.start()`` work regardless of this switch. What this switch
affects is only the network-backed **startup recovery scan** (a hosted
task-store ``list()`` plus credential-token acquisition) and the periodic
recovery loop it spawns.

That recovery runs at startup when EITHER a durable task has been declared
(``@task`` / ``@multi_turn_task``) OR this switch is on. So an app that uses
tasks gets recovery automatically; this switch is a **force-enable** that
starts the recovery loop even before any task is declared (useful when tasks
are registered lazily after startup — the running loop then picks them up).

The switch is process-global and defaults to ``False``. It is intentionally
decoupled from any ``AgentServerHost`` instance so it can be flipped
independently at import time, e.g.::

    from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled

    set_resilient_tasks_enabled(True)
"""

_RESILIENT_TASKS_ENABLED: bool = False


def set_resilient_tasks_enabled(value: bool = True) -> None:
    """Force-enable (or clear) the resilient task recovery scan process-wide.

    Setting this to ``True`` starts the startup recovery scan + periodic
    recovery loop even when no durable task is declared at startup. It does
    NOT gate the ``TaskManager``'s existence: ``.run()`` / ``.start()`` work
    whether or not this is set — this only controls automatic crash recovery.

    Must be called before ``AgentServerHost`` lifespan startup (typically at
    import time) to take effect. Defaults to enabling when called with no
    argument.

    :param value: ``True`` to force-enable recovery, ``False`` to clear.
    :type value: bool
    """
    global _RESILIENT_TASKS_ENABLED  # pylint: disable=global-statement
    _RESILIENT_TASKS_ENABLED = bool(value)


def resilient_tasks_enabled() -> bool:
    """Return whether the recovery scan was explicitly force-enabled.

    Note this reflects only the switch — recovery also runs automatically when
    a durable task is declared, so a ``False`` return does not mean recovery is
    off, nor that tasks are unavailable.

    :return: ``True`` if :func:`set_resilient_tasks_enabled` turned it on.
    :rtype: bool
    """
    return _RESILIENT_TASKS_ENABLED
