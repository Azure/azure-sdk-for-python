# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from enum import Enum
from typing import Dict, Union

from marshmallow import Schema

from azure.ai.ml.constants import NodeType
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._component.pipeline_component import PipelineComponent
from azure.ai.ml.entities._inputs_outputs import Input, Output

from ..._schema import PathAwareSchema
from .._job.pipeline._io import PipelineInput, PipelineOutputBase
from .._util import validate_attribute_type
from .base_node import BaseNode

module_logger = logging.getLogger(__name__)


class Pipeline(BaseNode):
    """Base class for pipeline node, used for pipeline component version
    consumption.

    :param component: Id or instance of the pipeline component/job to be run for the step
    :type component: PipelineComponent
    :param description: Description of the pipeline node.
    :type description: str
    :param inputs: Inputs of the pipeline node.
    :type inputs: dict
    :param outputs: Outputs of the pipeline node.
    :type outputs: dict
    """

    def __init__(
        self,
        *,
        component: Union[PipelineComponent, str],
        inputs: Dict[
            str,
            Union[
                PipelineInput,
                PipelineOutputBase,
                Input,
                str,
                bool,
                int,
                float,
                Enum,
                "Input",
            ],
        ] = None,
        outputs: Dict[str, Union[str, Output, "Output"]] = None,
        **kwargs,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())
        kwargs.pop("type", None)

        BaseNode.__init__(
            self,
            type=NodeType.PIPELINE,
            component=component,
            inputs=inputs,
            outputs=outputs,
            **kwargs,
        )

    @property
    def component(self) -> Union[str, PipelineComponent]:
        return self._component

    @property
    def jobs(self):
        """Return inner pipeline component's jobs."""
        return self._component.jobs

    @property
    def _skip_required_compute_missing_validation(self):
        return True

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "component": (str, PipelineComponent),
        }

    def _to_job(self):
        from azure.ai.ml.entities._job.pipeline.pipeline_job import PipelineJob

        return PipelineJob(
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            tags=self.tags,
            properties=self.properties,
            inputs=self._job_inputs,
            outputs=self._job_outputs,
            jobs=self.component.jobs,
        )

    @classmethod
    def _from_rest_object(cls, obj: dict) -> "Pipeline":
        obj = BaseNode._rest_object_to_init_params(obj)

        # Change componentId -> component
        component_id = obj.pop("componentId", None)
        obj["component"] = component_id
        return Pipeline(**obj)

    def _build_inputs(self):
        inputs = super(Pipeline, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value
        return built_inputs

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline.pipeline_component import PipelineSchema

        return PipelineSchema(context=context)

    def __call__(self, *args, **kwargs) -> "Pipeline":
        """Call Pipeline as a function will return a new instance each time."""
        if isinstance(self._component, PipelineComponent):
            # call this to validate inputs
            node = self._component(*args, **kwargs)
            # merge inputs
            for name, original_input in self.inputs.items():
                if name not in kwargs.keys():
                    # use setattr here to make sure owner of input won't change
                    setattr(node.inputs, name, original_input._data)
                # get outputs
            for name, original_output in self.outputs.items():
                # use setattr here to make sure owner of input won't change
                setattr(node.outputs, name, original_output._data)
            self._refine_optional_inputs_with_no_value(node, kwargs)
            node._name = self.name
            node.tags = self.tags
            node.display_name = self.display_name
            return node
        else:
            raise Exception(
                f"Pipeline can be called as a function only when referenced component is {type(Component)}, "
                f"currently got {self._component}."
            )
