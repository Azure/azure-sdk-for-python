# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Callable

from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._builders import Command
from azure.ai.ml.entities._job.pipeline._component_translatable import ComponentTranslatableMixin


# pylint: disable=unused-argument
def to_component(*, job: ComponentTranslatableMixin, **kwargs: Any) -> Callable[..., Command]:
    """Translate a job object to a component function, provided job should be able to translate to a component.

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

    :keyword job: Job load from local or remote.
    :paramtype job: ~azure.ai.ml.entities._job.pipeline._component_translatable.ComponentTranslatableMixin

    :return: Wrapped function call.
    :rtype: typing.Callable[..., ~azure.ai.ml.entities._builders.command.Command]
    """
    from pathlib import Path

    # set default base path as "./". Because if code path is relative path and base path is None, will raise error when
    # get arm id of Code
    res: Callable = job._to_component(context={BASE_PATH_CONTEXT_KEY: Path("./")})  # type: ignore[arg-type, assignment]
    return res
