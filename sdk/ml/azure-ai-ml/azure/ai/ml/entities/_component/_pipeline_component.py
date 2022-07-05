# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Union

from marshmallow import Schema

from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.constants import COMPONENT_TYPE, ComponentSource


class _PipelineComponent(Component):
    """Pipeline component, currently used to store components in a azure.ai.ml.dsl.pipeline.

    # TODO: refine this when pipeline component creation is supported.
    :param components: Id to components dict inside pipeline definition.
    :type components: OrderedDict[str, Component]
    :param inputs: Inputs of the component.
    :type inputs: ComponentInputs
    :param outputs: Outputs of the component.
    :type outputs: ComponentOutputs
    """

    def __init__(self, components: Dict[str, BaseNode], **kwargs):
        kwargs[COMPONENT_TYPE] = "pipeline_component"
        self._components = components
        super().__init__(**kwargs)

    @property
    def components(self) -> Dict[str, BaseNode]:
        """Return a dictionary from component variable name to component object.

        It's order is component creation order.
        """
        return self._components

    @classmethod
    def _load_from_rest_pipeline_job(cls, data: Dict):
        definition_inputs = {p: {"type": "unknown"} for p in data.get("inputs", {}).keys()}
        definition_outputs = {p: {"type": "unknown"} for p in data.get("outputs", {}).keys()}
        return _PipelineComponent(
            display_name=data.get("display_name"),
            description=data.get("description"),
            inputs=definition_inputs,
            outputs=definition_outputs,
            components={},
            _source=ComponentSource.REST,
        )

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        raise NotImplementedError(f"{cls.__name__} do not support schema validation.")

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs) -> "Component":
        raise NotImplementedError(f"{cls.__name__} do not support loading from dict.")

    def _to_dict(self) -> Dict:
        raise NotImplementedError(f"{self.__class__.__name__} do not support dump to dict.")

    def _to_yaml(self) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} do not support dump to yaml.")
