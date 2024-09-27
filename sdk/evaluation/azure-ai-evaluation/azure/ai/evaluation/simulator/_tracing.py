# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=C0103,C0114,C0116,E0401,E0611

import functools
from typing import Callable, TypeVar

from promptflow._sdk._telemetry.activity import ActivityType, monitor_operation
from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


def monitor_adversarial_scenario(activity_name: str = "adversarial.simulator.call"):
    """
    Monitor an adversarial scenario.

    :param activity_name: The name of the activity to monitor.
    :type activity_name: str
    :returns: A decorator
    :rtype: Callable[[Callable], Callable]
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        """
        Decorator for monitoring an adversarial scenario.

        :param func: The function to be decorated.
        :type func: Callable[P, R]
        :returns: The decorated function
        :rtype: Callable[P, R]
        """

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            scenario = str(kwargs.get("scenario", None))
            max_conversation_turns = kwargs.get("max_conversation_turns", None)
            max_simulation_results = kwargs.get("max_simulation_results", None)
            jailbreak = kwargs.get("jailbreak", None)
            decorated_func = monitor_operation(
                activity_name=activity_name,
                activity_type=ActivityType.PUBLICAPI,
                custom_dimensions={
                    "scenario": scenario,
                    "max_conversation_turns": max_conversation_turns,
                    "max_simulation_results": max_simulation_results,
                    "jailbreak": jailbreak,
                },
            )(func)

            return decorated_func(*args, **kwargs)

        return wrapper

    return decorator


def monitor_task_simulator(func: Callable[P, R]) -> Callable[P, R]:
    """
    Monitor a task simulator.

    :param func: The function to be decorated.
    :type func: Callable[P, R]
    :returns: The decorated function
    :rtype: Callable[P, R]
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        text = kwargs.get("text")
        user_persona = kwargs.get("user_persona")
        num_queries = kwargs.get("num_queries", 0)
        max_conversation_turns = kwargs.get("max_conversation_turns", 0)
        decorated_func = monitor_operation(
            activity_name="task.simulator.call",
            activity_type=ActivityType.PUBLICAPI,
            custom_dimensions={
                "text_length": len(text) if isinstance(text, str) else 0,
                "user_persona_length": len(user_persona) if isinstance(user_persona, list) else 0,
                "number_of_queries": num_queries,
                "max_conversation_turns": max_conversation_turns,
            },
        )(func)

        return decorated_func(*args, **kwargs)

    return wrapper
