# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from enum import Enum
from typing import Dict, Union

from marshmallow import Schema

from azure.ai.ml.entities._component.component import Component, NodeType
from azure.ai.ml.entities._inputs_outputs import Input, Output

from ..._schema import PathAwareSchema
from .._job.pipeline.pipeline_job_settings import PipelineJobSettings
from .._util import convert_ordered_dict_to_dict, validate_attribute_type
from .base_node import BaseNode

module_logger = logging.getLogger(__name__)


class Pipeline(BaseNode):
    """Base class for pipeline node, used for pipeline component version
    consumption. You should not instantiate this class directly. Instead, you should
    use @pipeline decorator to create a pipeline node.

    You should not instantiate this class directly. Instead, you should
    create from @pipeline decorator.

    :param component: Id or instance of the pipeline component/job to be run for the step
    :type component: PipelineComponent
    :param description: Description of the pipeline node.
    :type description: str
    :param inputs: Inputs of the pipeline node.
    :type inputs: dict
    :param outputs: Outputs of the pipeline node.
    :type outputs: dict
    :param settings: Setting of pipeline node, only taking effect for root pipeline job.
    :type settings: ~azure.ai.ml.entities.PipelineJobSettings
    """

    def __init__(
        self,
        *,
        component: Union[Component, str],
        inputs: Dict[
            str,
            Union[
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
        settings: PipelineJobSettings = None,
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
        self._settings = None
        self.settings = settings

    @property
    def component(self) -> Union[str, Component]:
        return self._component

    @property
    def settings(self) -> PipelineJobSettings:
        """Settings of the pipeline.

        Note: settings is available only when create node as a job.
            i.e. ml_client.jobs.create_or_update(node).

        :return: Settings of the pipeline.
        :rtype: ~azure.ai.ml.entities.PipelineJobSettings
        """
        if self._settings is None:
            self._settings = PipelineJobSettings()
        return self._settings

    @settings.setter
    def settings(self, value):
        if value is not None and not isinstance(value, PipelineJobSettings):
            raise TypeError("settings must be PipelineJobSettings or dict but got {}".format(type(value)))
        self._settings = value

    @classmethod
    def _get_supported_inputs_types(cls):
        # Return None here to skip validation,
        # as input could be custom class object(parameter group).
        return None

    @property
    def _skip_required_compute_missing_validation(self):
        return True

    @classmethod
    def _attr_type_map(cls) -> dict:
        # Use local import to avoid recursive reference as BaseNode is imported in PipelineComponent.
        from azure.ai.ml.entities import PipelineComponent

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
            component=self.component,
            settings=self.settings,
        )

    def _customized_validate(self):
        """Check unsupported settings when use as a node."""
        # Note: settings is not supported on node,
        # jobs.create_or_update(node) will call node._to_job() at first,
        # thus won't reach here.
        # pylint: disable=protected-access
        from azure.ai.ml.entities import PipelineComponent

        validation_result = super(Pipeline, self)._customized_validate()
        ignored_keys = PipelineComponent._check_ignored_keys(self)
        if ignored_keys:
            validation_result.append_warning(message=f"{ignored_keys} ignored on node {self.name!r}.")
        if isinstance(self.component, PipelineComponent):
            validation_result.merge_with(self.component._customized_validate())
        return validation_result

    def _to_rest_object(self, **kwargs) -> dict:
        rest_obj = super()._to_rest_object(**kwargs)
        rest_obj.update(
            convert_ordered_dict_to_dict(
                dict(
                    componentId=self._get_component_id(),
                )
            )
        )
        return rest_obj

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
