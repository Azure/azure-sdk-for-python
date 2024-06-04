# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

from marshmallow import Schema

from azure.ai.ml.entities._component.component import Component, NodeType
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._validation import MutableValidationResult

from ..._schema import PathAwareSchema
from .._job.pipeline.pipeline_job_settings import PipelineJobSettings
from .._util import convert_ordered_dict_to_dict, copy_output_setting, validate_attribute_type
from .base_node import BaseNode

if TYPE_CHECKING:
    from azure.ai.ml.entities._job.pipeline.pipeline_job import PipelineJob

module_logger = logging.getLogger(__name__)


class Pipeline(BaseNode):
    """Base class for pipeline node, used for pipeline component version consumption. You should not instantiate this
    class directly. Instead, you should use @pipeline decorator to create a pipeline node.

    :param component: Id or instance of the pipeline component/job to be run for the step.
    :type component: Union[~azure.ai.ml.entities.Component, str]
    :param inputs: Inputs of the pipeline node.
    :type inputs: Optional[Dict[str, Union[
                                    ~azure.ai.ml.entities.Input,
                                    str, bool, int, float, Enum, "Input"]]].
    :param outputs: Outputs of the pipeline node.
    :type outputs: Optional[Dict[str, Union[str, ~azure.ai.ml.entities.Output, "Output"]]]
    :param settings: Setting of pipeline node, only taking effect for root pipeline job.
    :type settings: Optional[~azure.ai.ml.entities._job.pipeline.pipeline_job_settings.PipelineJobSettings]
    """

    def __init__(
        self,
        *,
        component: Union[Component, str],
        inputs: Optional[
            Dict[
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
            ]
        ] = None,
        outputs: Optional[Dict[str, Union[str, Output, "Output"]]] = None,
        settings: Optional[PipelineJobSettings] = None,
        **kwargs: Any,
    ) -> None:
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
        # copy pipeline component output's setting to node level
        self._copy_pipeline_component_out_setting_to_node()
        self._settings: Optional[PipelineJobSettings] = None
        self.settings = settings

    @property
    def component(self) -> Optional[Union[str, Component]]:
        """Id or instance of the pipeline component/job to be run for the step.

        :return: Id or instance of the pipeline component/job.
        :rtype: Union[str, ~azure.ai.ml.entities.Component]
        """
        res: Union[str, Component] = self._component
        return res

    @property
    def settings(self) -> Optional[PipelineJobSettings]:
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
    def settings(self, value: Union[PipelineJobSettings, Dict]) -> None:
        """Set the settings of the pipeline.

        :param value: The settings of the pipeline.
        :type value: Union[~azure.ai.ml.entities.PipelineJobSettings, dict]
        :raises TypeError: If the value is not an instance of PipelineJobSettings or a dict.
        """
        if value is not None:
            if isinstance(value, PipelineJobSettings):
                # since PipelineJobSettings inherit _AttrDict, we need add this branch to distinguish with dict
                pass
            elif isinstance(value, dict):
                value = PipelineJobSettings(**value)
            else:
                raise TypeError("settings must be PipelineJobSettings or dict but got {}".format(type(value)))
        self._settings = value

    @classmethod
    def _get_supported_inputs_types(cls) -> None:
        # Return None here to skip validation,
        # as input could be custom class object(parameter group).
        return None

    @property
    def _skip_required_compute_missing_validation(self) -> bool:
        return True

    @classmethod
    def _get_skip_fields_in_schema_validation(cls) -> List[str]:
        # pipeline component must be a file reference when loading from yaml,
        # so the created object can't pass schema validation.
        return ["component"]

    @classmethod
    def _attr_type_map(cls) -> dict:
        # Use local import to avoid recursive reference as BaseNode is imported in PipelineComponent.
        from azure.ai.ml.entities import PipelineComponent

        return {
            "component": (str, PipelineComponent),
        }

    def _to_job(self) -> "PipelineJob":
        from azure.ai.ml.entities._job.pipeline.pipeline_job import PipelineJob

        return PipelineJob(
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            tags=self.tags,
            properties=self.properties,
            # Filter None out to avoid case below failed with conflict keys check:
            # group: None (user not specified)
            # group.xx: 1 (user specified
            inputs={k: v for k, v in self._job_inputs.items() if v},
            outputs=self._job_outputs,
            component=self.component,
            settings=self.settings,
        )

    def _customized_validate(self) -> MutableValidationResult:
        """Check unsupported settings when use as a node.

        :return: The validation result
        :rtype: MutableValidationResult
        """
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

    def _to_rest_object(self, **kwargs: Any) -> dict:
        rest_obj: Dict = super()._to_rest_object(**kwargs)
        rest_obj.update(
            convert_ordered_dict_to_dict(
                {
                    "componentId": self._get_component_id(),
                }
            )
        )
        return rest_obj

    def _build_inputs(self) -> Dict:
        inputs = super(Pipeline, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value
        return built_inputs

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline.pipeline_component import PipelineSchema

        return PipelineSchema(context=context)

    def _copy_pipeline_component_out_setting_to_node(self) -> None:
        """Copy pipeline component output's setting to node level."""
        from azure.ai.ml.entities import PipelineComponent
        from azure.ai.ml.entities._job.pipeline._io import NodeOutput

        if not isinstance(self.component, PipelineComponent):
            return
        for key, val in self.component.outputs.items():
            node_output = cast(NodeOutput, self.outputs.get(key))
            copy_output_setting(source=val, target=node_output)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> "Job":
        raise NotImplementedError()
