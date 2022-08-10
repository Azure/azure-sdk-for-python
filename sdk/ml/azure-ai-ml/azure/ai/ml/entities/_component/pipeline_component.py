# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import json
import logging
import typing
from collections import Counter
from typing import Dict, Tuple, Union

from marshmallow import INCLUDE, Schema

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2022_05_01.models import ComponentVersionData
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.pipeline.pipeline_component import PipelineComponentSchema, RestPipelineComponentSchema
from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, COMPONENT_TYPE, ComponentSource, NodeType
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._builders import BaseNode, Command
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job.pipeline._attr_dict import try_get_non_arbitrary_attr_for_potential_attr_dict
from azure.ai.ml.entities._job.pipeline._pipeline_expression import PipelineExpression
from azure.ai.ml.entities._validation import ValidationResult

module_logger = logging.getLogger(__name__)


class PipelineComponent(Component):
    """Pipeline component, currently used to store components in a
    azure.ai.ml.dsl.pipeline.

    :param name: Name of the component.
    :type name: str
    :param version: Version of the component.
    :type version: str
    :param description: Description of the component.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param display_name: Display name of the component.
    :type display_name: str
    :type inputs: Component inputs
    :param outputs: Outputs of the component.
    :type outputs: Component outputs
    :param jobs: Id to components dict inside pipeline definition.
    :type jobs: OrderedDict[str, Component]
    """

    def __init__(
        self,
        *,
        name: str = None,
        version: str = None,
        description: str = None,
        tags: Dict = None,
        display_name: str = None,
        inputs: Dict = None,
        outputs: Dict = None,
        jobs: Dict[str, BaseNode],
        **kwargs,
    ):
        kwargs[COMPONENT_TYPE] = NodeType.PIPELINE
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            display_name=display_name,
            inputs=inputs,
            outputs=outputs,
            **kwargs,
        )
        self._jobs = self._process_jobs(jobs) if jobs else {}
        # for telemetry
        self._job_types, self._job_sources = self._get_job_type_and_source()
        # TODO: set anonymous hash for reuse

    def _process_jobs(self, jobs):
        """Process and validate jobs."""
        # Remove swept Command
        node_names_to_skip = []
        for node_name, job_instance in jobs.items():
            if isinstance(job_instance, Command) and job_instance._swept is True:
                node_names_to_skip.append(node_name)

        for key in node_names_to_skip:
            del jobs[key]

        # Set path and validate node type.
        for _, job_instance in jobs.items():
            if isinstance(job_instance, BaseNode):
                job_instance._set_base_path(self.base_path)

            if not isinstance(job_instance, (BaseNode, AutoMLJob)):
                msg = f"Not supported pipeline job type: {type(job_instance)}"
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
        return jobs

    def _customized_validate(self) -> ValidationResult:
        """Validate pipeline component structure."""
        validation_result = super(PipelineComponent, self)._customized_validate()

        # Validate inputs and all nodes.
        for node_name, node in self.jobs.items():
            if isinstance(node, BaseNode):
                # Node inputs will be validated.
                validation_result.merge_with(node._validate(), "jobs.{}".format(node_name))
                if isinstance(node.component, Component):
                    # Validate binding if not remote resource.
                    validation_result.merge_with(self._validate_binding_inputs(node))
            elif isinstance(node, AutoMLJob):
                pass
            else:
                validation_result.append_error(
                    yaml_path="jobs.{}".format(node_name),
                    message=f"Not supported pipeline job type: {type(node)}",
                )

        return validation_result

    def _get_input_binding_dict(self, node: BaseNode) -> Tuple[dict, dict]:
        """Return the input binding dict for each node."""
        binding_inputs = node._build_inputs()
        # Collect binding relation dict {'pipeline_input': ['node_input']}
        binding_dict, optional_binding_in_expression_dict = {}, {}
        for component_input_name, component_binding_input in binding_inputs.items():
            if isinstance(component_binding_input, PipelineExpression):
                for pipeline_input_name, pipeline_input in component_binding_input._inputs.items():
                    if pipeline_input_name not in self.inputs:
                        continue
                    if pipeline_input_name not in binding_dict:
                        binding_dict[pipeline_input_name] = []
                    binding_dict[pipeline_input_name].append(component_input_name)
                    if pipeline_input_name not in optional_binding_in_expression_dict:
                        optional_binding_in_expression_dict[pipeline_input_name] = []
                    optional_binding_in_expression_dict[pipeline_input_name].append(pipeline_input_name)
            else:
                if isinstance(component_binding_input, Input):
                    component_binding_input = component_binding_input.path
                if is_data_binding_expression(component_binding_input, ["parent"]):
                    # data binding may have more than one PipelineInput now
                    for pipeline_input_name in PipelineExpression.parse_pipeline_input_names_from_data_binding(
                        component_binding_input
                    ):
                        if pipeline_input_name not in self.inputs:
                            continue
                        if pipeline_input_name not in binding_dict:
                            binding_dict[pipeline_input_name] = []
                        binding_dict[pipeline_input_name].append(component_input_name)
                        # for data binding expression "${{parent.inputs.pipeline_input}}", it should not be optional
                        if len(component_binding_input.replace("${{parent.inputs." + pipeline_input_name + "}}", "")):
                            if pipeline_input_name not in optional_binding_in_expression_dict:
                                optional_binding_in_expression_dict[pipeline_input_name] = []
                            optional_binding_in_expression_dict[pipeline_input_name].append(pipeline_input_name)
        return binding_dict, optional_binding_in_expression_dict

    def _validate_binding_inputs(self, node: BaseNode) -> ValidationResult:
        """Validate pipeline binding inputs and return all used pipeline input
        names.

        Mark input as optional if all binding is optional and optional
        not set. Raise error if pipeline input is optional but link to
        required inputs.
        """
        component_definition_inputs = node.component.inputs
        # Collect binding relation dict {'pipeline_input': ['node_input']}
        validation_result = self._create_empty_validation_result()
        binding_dict, optional_binding_in_expression_dict = self._get_input_binding_dict(node)

        # Validate links required and optional
        for pipeline_input_name, binding_inputs in binding_dict.items():
            pipeline_input = self.inputs[pipeline_input_name]
            required_bindings = []
            for name in binding_inputs:
                # not check optional/required for pipeline input used in pipeline expression
                if name in optional_binding_in_expression_dict.get(pipeline_input_name, []):
                    continue
                if component_definition_inputs[name].optional is not True:
                    required_bindings.append(f"{node.name}.inputs.{name}")
            if pipeline_input.optional is None and not required_bindings:
                # Set input as optional if all binding is optional and optional not set.
                pipeline_input.optional = True
                pipeline_input._is_inferred_optional = True
            elif pipeline_input.optional is True and required_bindings:
                if pipeline_input._is_inferred_optional:
                    # Change optional=True to None if is inferred by us
                    pipeline_input.optional = None
                else:
                    # Raise exception if pipeline input is optional set by user but link to required inputs.
                    validation_result.append_error(
                        yaml_path="inputs.{}".format(pipeline_input.name),
                        message=f"Pipeline optional Input binding to required inputs: {required_bindings}",
                    )
        return validation_result

    def _get_job_type_and_source(self):
        """Get job type and source for telemetry."""
        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob

        job_types, job_sources = [], []
        for job in self.jobs.values():
            job_types.append(job.type)
            if isinstance(job, BaseNode):
                job_sources.append(job._source)
            elif isinstance(job, AutoMLJob):
                # Consider all automl_job has builder type for now,
                # as it's not easy to distinguish their source(yaml/builder).
                job_sources.append(ComponentSource.BUILDER)
            else:
                # Fall back to CLASS
                job_sources.append(ComponentSource.CLASS)
        return dict(Counter(job_types)), dict(Counter(job_sources))

    @property
    def jobs(self) -> Dict[str, BaseNode]:
        """Return a dictionary from component variable name to component
        object."""
        return self._jobs

    @classmethod
    def _load_from_rest_pipeline_job(cls, data: Dict):
        # TODO: refine this?
        definition_inputs = {p: {"type": "unknown"} for p in data.get("inputs", {}).keys()}
        definition_outputs = {p: {"type": "unknown"} for p in data.get("outputs", {}).keys()}
        return PipelineComponent(
            display_name=data.get("display_name"),
            description=data.get("description"),
            inputs=definition_inputs,
            outputs=definition_outputs,
            jobs=data.get("jobs"),
            _source=ComponentSource.REMOTE_WORKSPACE_JOB,
        )

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        return PipelineComponentSchema(context=context)

    def _get_skip_fields_in_schema_validation(self) -> typing.List[str]:
        # jobs validations are done in _customized_validate()
        return ["jobs"]

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs) -> "Component":
        return PipelineComponent(
            yaml_str=kwargs.pop("yaml_str", None),
            _source=kwargs.pop("_source", ComponentSource.YAML),
            **(PipelineComponentSchema(context=context).load(data, unknown=INCLUDE, **kwargs)),
        )

    @classmethod
    def _load_from_rest(cls, obj: ComponentVersionData) -> "PipelineComponent":
        rest_component_version = obj.properties
        inputs = {
            k: Input._from_rest_object(v) for k, v in rest_component_version.component_spec.pop("inputs", {}).items()
        }
        outputs = {
            k: Output._from_rest_object(v) for k, v in rest_component_version.component_spec.pop("outputs", {}).items()
        }

        pipeline_component = PipelineComponent(
            id=obj.id,
            is_anonymous=rest_component_version.is_anonymous,
            creation_context=obj.system_data,
            inputs=inputs,
            outputs=outputs,
            # use different schema for component from rest since name may be "invalid"
            **RestPipelineComponentSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).load(
                rest_component_version.component_spec, unknown=INCLUDE
            ),
            _source=ComponentSource.REST,
        )
        return pipeline_component

    @classmethod
    def _check_ignored_keys(cls, obj):
        """Return ignored keys in obj as a pipeline component when its value be
        set."""
        examine_mapping = {
            "compute": lambda val: val is not None,
            "settings": lambda val: val is not None and any(v is not None for v in val._to_dict().values()),
        }
        # Avoid new attr added by use `try_get_non...` instead of `hasattr` or `getattr` directly.
        return [
            k
            for k, has_set in examine_mapping.items()
            if has_set(try_get_non_arbitrary_attr_for_potential_attr_dict(obj, k))
        ]

    def _get_telemetry_values(self):
        telemetry_values = super()._get_telemetry_values()
        telemetry_values.update(
            {
                "source": self._source,
                "node_count": len(self.jobs),
                "node_type": json.dumps(self._job_types),
                "node_source": json.dumps(self._job_sources),
            }
        )
        return telemetry_values

    def _to_dict(self) -> Dict:
        """Dump the command component content into a dictionary."""

        # Replace the name of $schema to schema.
        component_schema_dict = self._dump_for_validation()
        component_schema_dict.pop("base_path", None)
        return {**self._other_parameter, **component_schema_dict}

    def _to_rest_object(self) -> ComponentVersionData:
        """Check ignored keys and return rest object."""
        self._check_ignored_keys(self)
        return super()._to_rest_object()

    def __str__(self):
        try:
            return self._to_yaml()
        except BaseException:
            return super(PipelineComponent, self).__str__()
