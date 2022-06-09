# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable, Mapping, Union

from azure.ai.ml.dsl._component_func import to_component_func
from azure.ai.ml.dsl._overrides_definition import OverrideDefinition
from azure.ai.ml.entities._builders import Command, Parallel
from azure.ai.ml.constants import ComponentSource
from azure.ai.ml.entities import Component, CommandComponent, ParallelComponent

from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget


def _generate_component_function(
    component_entity: Component, override_definitions: Mapping[str, OverrideDefinition] = None
) -> Callable[..., Union[Command, Parallel]]:
    # Generate a function which returns a component node.
    def create_component_func(**kwargs):
        if isinstance(component_entity, CommandComponent):
            return Command(component=component_entity, inputs=kwargs, _from_component_func=True)
        elif isinstance(component_entity, ParallelComponent):
            return Parallel(component=component_entity, inputs=kwargs, _from_component_func=True)
        else:
            raise NotImplementedError(f"Not supported component type: {type(component_entity)}.")

    return to_component_func(component_entity, create_component_func)


def load_component(
    *,
    yaml_file: str = None,
    **kwargs,
) -> Union[CommandComponent, ParallelComponent]:
    """Load component from local or remote to a component function.

    For example:

    .. code-block:: python

        # Load a local component to a component function.
        component_func = dsl.load_component(yaml_file="custom_component/component_spec.yaml")
        # Load a remote component to a component function.
        component_func = dsl.load_component(client=ml_client, name="my_component", version=1)

        # Consuming the component func
        component = component_func(param1=xxx, param2=xxx)

    :param yaml_file: Local component yaml file.
    :type yaml_file: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict

    :return: A function that can be called with parameters to get a `azure.ai.ml.entities.Component`
    :rtype: Union[CommandComponent]
    """
    client = kwargs.get("client", None)
    name = kwargs.get("name", None)
    version = kwargs.get("version", None)
    if yaml_file:
        component_entity = Component.load(path=yaml_file)
    elif client and name and version:
        component_entity = client.components.get(name, version)
    else:
        msg = "One of (client, name, version), (yaml_file) should be provided."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.COMPONENT,
            error_category=ErrorCategory.USER_ERROR,
        )
    return component_entity
