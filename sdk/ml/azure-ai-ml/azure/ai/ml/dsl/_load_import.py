# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Callable

from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._builders import Command
from azure.ai.ml.entities._job.pipeline._component_translatable import ComponentTranslatableMixin


def to_component(*, job: ComponentTranslatableMixin, **kwargs) -> Callable[..., Command]:
    """Translate a job object to a component function, provided job should be
    able to translate to a component.

    For example:

    .. code-block:: python

        # Load a local command job to a component function.
        my_job = load_job("my_job.yaml")
        component_func = dsl.to_component(my_job)
        # Load a remote command job component to a component function.
        my_job = ml_client.jobs.get("my_job")
        component_func = dsl.to_component(my_job)

        # Consuming the component func
        component = component_func(param1=xxx, param2=xxx)

    :param job: Job load from local or remote.
    :type job: ~azure.ai.ml.entities._job.pipeline._component_translatable.ComponentTranslatableMixin
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict

    :return: Wrapped function call.
    :rtype: typing.Callable[..., ~azure.ai.ml.entities._builders.command.Command]
    """
    from pathlib import Path

    # set default base path as "./". Because if code path is relative path and base path is None, will raise error when
    # get arm id of Code
    return job._to_component(context={BASE_PATH_CONTEXT_KEY: Path("./")})
