# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Explicit task-runtime opt-in for the Invocations protocol.

The switch defaults to ``False`` and is evaluated before Invocations lifespan
startup. Declaring ``@task`` or ``@multi_turn_task`` does not enable execution.
The low-level ``AgentServerHost`` also uses this switch when no protocol has
provided its own activation requirements.

Responses does not read or change this switch. Its task runtime is enabled by
``ResponsesServerOptions.resilient_background`` or ``steerable_conversations``.
Protocol request scopes prevent one protocol's opt-in from enabling another.

Set the switch before Invocations lifespan startup::

    from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled

    set_resilient_tasks_enabled(True)
"""

_RESILIENT_TASKS_ENABLED: bool = False


def set_resilient_tasks_enabled(value: bool = True) -> None:
    """Enable or disable task execution for Invocations hosts.

    Enabled hosts initialize a persistent task manager, perform startup recovery
    and run the periodic recovery loop. Set this before lifespan startup.
    Responses hosts use their own feature options independently, including on
    cooperative multi-protocol hosts. This setting remains process-global for
    Invocations configuration and defaults to enabling when called without an
    argument.

    :param value: ``True`` to enable the resilient task subsystem, ``False`` to
        clear.
    :type value: bool
    """
    global _RESILIENT_TASKS_ENABLED  # pylint: disable=global-statement
    _RESILIENT_TASKS_ENABLED = bool(value)


def resilient_tasks_enabled() -> bool:
    """Return the Invocations task-runtime opt-in setting.

    This does not report whether a Responses host has enabled its own runtime.

    :return: ``True`` if :func:`set_resilient_tasks_enabled` turned it on.
    :rtype: bool
    """
    return _RESILIENT_TASKS_ENABLED
