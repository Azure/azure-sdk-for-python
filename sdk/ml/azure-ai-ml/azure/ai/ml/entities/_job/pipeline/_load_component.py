# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable, Mapping, Union

from azure.ai.ml.dsl._component_func import to_component_func
from azure.ai.ml.dsl._overrides_definition import OverrideDefinition
from azure.ai.ml.entities._builders import Command, Parallel
from azure.ai.ml.entities import Component, CommandComponent, ParallelComponent


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
