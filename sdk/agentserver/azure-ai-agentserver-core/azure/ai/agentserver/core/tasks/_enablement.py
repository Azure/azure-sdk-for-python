# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Explicit enablement switch for the resilient task subsystem.

The resilient ``TaskManager`` performs network-backed startup work (a hosted
task-store recovery scan plus credential-token acquisition). To avoid making
any of those calls unless an app genuinely relies on durable tasks,
``AgentServerHost`` only stands up the ``TaskManager`` when BOTH conditions
hold:

1. this switch has been turned on via :func:`set_resilient_tasks_enabled`, AND
2. at least one durable task has been declared (``@task`` / ``@multi_turn_task``).

The switch is process-global and defaults to ``False`` (disabled). It is
intentionally decoupled from any ``AgentServerHost`` instance so it can be
flipped independently at import time, e.g.::

    from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled

    set_resilient_tasks_enabled(True)
"""

_RESILIENT_TASKS_ENABLED: bool = False


def set_resilient_tasks_enabled(value: bool = True) -> None:
    """Enable or disable the resilient task subsystem process-wide.

    Must be called before ``AgentServerHost`` lifespan startup (typically at
    import time) to take effect for eager initialization. Defaults the switch
    to enabled when called with no argument.

    :param value: ``True`` to enable resilient tasks, ``False`` to disable.
    :type value: bool
    """
    global _RESILIENT_TASKS_ENABLED  # pylint: disable=global-statement
    _RESILIENT_TASKS_ENABLED = bool(value)


def resilient_tasks_enabled() -> bool:
    """Return whether the resilient task subsystem has been explicitly enabled.

    :return: ``True`` if :func:`set_resilient_tasks_enabled` turned it on.
    :rtype: bool
    """
    return _RESILIENT_TASKS_ENABLED
