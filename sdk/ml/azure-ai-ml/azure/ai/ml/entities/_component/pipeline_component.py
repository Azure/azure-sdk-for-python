# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import json
import logging
import os
import re
import time
import typing
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple, Union

from marshmallow import Schema

from azure.ai.ml._restclient.v2022_10_01.models import ComponentVersion, ComponentVersionProperties
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.pipeline.pipeline_component import PipelineComponentSchema
from azure.ai.ml._utils._asset_utils import get_object_hash
from azure.ai.ml._utils.utils import hash_dict, is_data_binding_expression
from azure.ai.ml.constants._common import ARM_ID_PREFIX, ASSET_ARM_ID_REGEX_FORMAT, COMPONENT_TYPE
from azure.ai.ml.constants._component import ComponentSource, NodeType
from azure.ai.ml.constants._job.pipeline import ValidationErrorCode
from azure.ai.ml.entities._builders import BaseNode, Command
from azure.ai.ml.entities._builders.control_flow_node import ControlFlowNode, LoopNode
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._inputs_outputs import GroupInput, Input
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job.pipeline._attr_dict import has_attr_safe, try_get_non_arbitrary_attr
from azure.ai.ml.entities._job.pipeline._pipeline_expression import PipelineExpression
from azure.ai.ml.entities._validation import MutableValidationResult
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

module_logger = logging.getLogger(__name__)


class PipelineComponent(Component):
    """Pipeline component, currently used to store components in an azure.ai.ml.dsl.pipeline.

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
    :param inputs: Component inputs.
    :type inputs: dict
    :param outputs: Component outputs.
    :type outputs: dict
    :param jobs: Id to components dict inside the pipeline definition.
    :type jobs: Dict[str, ~azure.ai.ml.entities._builders.BaseNode]
    :param is_deterministic: Whether the pipeline component is deterministic.
    :type is_deterministic: bool
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if PipelineComponent cannot be successfully validated.
        Details will be provided in the error message.
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        display_name: Optional[str] = None,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        jobs: Optional[Dict[str, BaseNode]] = None,
        is_deterministic: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        kwargs[COMPONENT_TYPE] = NodeType.PIPELINE
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            display_name=display_name,
            inputs=inputs,
            outputs=outputs,
            is_deterministic=is_deterministic,  # type: ignore[arg-type]
            **kwargs,
        )
        self._jobs = self._process_jobs(jobs) if jobs else {}
        # for telemetry
        self._job_types, self._job_sources = self._get_job_type_and_source()
        # Private support: create pipeline component from pipeline job
        self._source_job_id = kwargs.pop("source_job_id", None)
        # TODO: set anonymous hash for reuse

    def _process_jobs(self, jobs: Dict[str, BaseNode]) -> Dict[str, BaseNode]:
        """Process and validate jobs.

        :param jobs: A map of node name to node
        :type jobs: Dict[str, BaseNode]
        :return: The processed jobs
        :rtype: Dict[str, BaseNode]
        """
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

            if not isinstance(job_instance, (BaseNode, AutoMLJob, ControlFlowNode)):
                msg = f"Not supported pipeline job type: {type(job_instance)}"
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
        return jobs

    def _customized_validate(self) -> MutableValidationResult:
        """Validate pipeline component structure.

        :return: The validation result
        :rtype: MutableValidationResult
        """
        validation_result = super(PipelineComponent, self)._customized_validate()

        # Validate inputs
        for input_name, input_value in self.inputs.items():
            if input_value.type is None:
                validation_result.append_error(
                    yaml_path="inputs.{}".format(input_name),
                    message="Parameter type unknown, please add type annotation or specify input default value.",
                    error_code=ValidationErrorCode.PARAMETER_TYPE_UNKNOWN,
                )

        # Validate all nodes
        for node_name, node in self.jobs.items():
            if isinstance(node, BaseNode):
                # Node inputs will be validated.
                validation_result.merge_with(node._validate(), "jobs.{}".format(node_name))
                if isinstance(node.component, Component):
                    # Validate binding if not remote resource.
                    validation_result.merge_with(self._validate_binding_inputs(node))
            elif isinstance(node, AutoMLJob):
                pass
            elif isinstance(node, ControlFlowNode):
                # Validate control flow node.
                validation_result.merge_with(node._validate(), "jobs.{}".format(node_name))
            else:
                validation_result.append_error(
                    yaml_path="jobs.{}".format(node_name),
                    message=f"Not supported pipeline job type: {type(node)}",
                )

        return validation_result

    def _validate_compute_is_set(self, *, parent_node_name: Optional[str] = None) -> MutableValidationResult:
        """Validate compute in pipeline component.

        This function will only be called from pipeline_job._validate_compute_is_set
        when both of the pipeline_job.compute and pipeline_job.settings.default_compute is None.
        Rules:
        - For pipeline node: will call node._component._validate_compute_is_set to validate node compute in sub graph.
        - For general node:
            - If _skip_required_compute_missing_validation is True, validation will be skipped.
            - All the rest of cases without compute will add compute not set error to validation result.

        :keyword parent_node_name: The name of the parent node.
        :type parent_node_name: Optional[str]
        :return: The validation result
        :rtype: MutableValidationResult
        """

        # Note: do not put this into customized validate, as we would like call
        # this from pipeline_job._validate_compute_is_set
        validation_result = self._create_empty_validation_result()
        no_compute_nodes = []
        parent_node_name = parent_node_name if parent_node_name else ""
        for node_name, node in self.jobs.items():
            full_node_name = f"{parent_node_name}{node_name}.jobs."
            if node.type == NodeType.PIPELINE and isinstance(node._component, PipelineComponent):
                validation_result.merge_with(node._component._validate_compute_is_set(parent_node_name=full_node_name))
                continue
            if isinstance(node, BaseNode) and node._skip_required_compute_missing_validation:
                continue
            if has_attr_safe(node, "compute") and node.compute is None:
                no_compute_nodes.append(node_name)

        for node_name in no_compute_nodes:
            validation_result.append_error(
                yaml_path=f"jobs.{parent_node_name}{node_name}.compute",
                message="Compute not set",
            )
        return validation_result

    def _get_input_binding_dict(self, node: BaseNode) -> Tuple[dict, dict]:
        """Return the input binding dict for each node.

        :param node: The node
        :type node: BaseNode
        :return: A 2-tuple of (binding_dict, optional_binding_in_expression_dict)
        :rtype: Tuple[dict, dict]
        """
        # pylint: disable=too-many-nested-blocks
        binding_inputs = node._build_inputs()
        # Collect binding relation dict {'pipeline_input': ['node_input']}
        binding_dict: dict = {}
        optional_binding_in_expression_dict: dict = {}
        for component_input_name, component_binding_input in binding_inputs.items():
            if isinstance(component_binding_input, PipelineExpression):
                for pipeline_input_name in component_binding_input._inputs.keys():
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
                    for pipeline_input_name in PipelineExpression.parse_pipeline_inputs_from_data_binding(
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

    def _validate_binding_inputs(self, node: BaseNode) -> MutableValidationResult:
        """Validate pipeline binding inputs and return all used pipeline input names.

        Mark input as optional if all binding is optional and optional not set. Raise error if pipeline input is
        optional but link to required inputs.

        :param node: The node to validate
        :type node: BaseNode
        :return: The validation result
        :rtype: MutableValidationResult
        """
        component_definition_inputs = {}
        # Add flattened group input into definition inputs.
        # e.g. Add {'group_name.item': PipelineInput} for {'group_name': GroupInput}
        for name, val in node.component.inputs.items():
            if isinstance(val, GroupInput):
                component_definition_inputs.update(val.flatten(group_parameter_name=name))
            component_definition_inputs[name] = val
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
                if name in component_definition_inputs and component_definition_inputs[name].optional is not True:
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
                        yaml_path="inputs.{}".format(pipeline_input._port_name),
                        message=f"Pipeline optional Input binding to required inputs: {required_bindings}",
                    )
        return validation_result

    def _get_job_type_and_source(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        """Get job types and sources for telemetry.

        :return: A 2-tuple of
          * A map of job type to the number of occurrences
          * A map of job source to the number of occurrences
        :rtype: Tuple[Dict[str, int], Dict[str, int]]
        """
        job_types: list = []
        job_sources = []
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
        """Return a dictionary from component variable name to component object.

        :return: Dictionary mapping component variable names to component objects.
        :rtype: Dict[str, ~azure.ai.ml.entities._builders.BaseNode]
        """
        return self._jobs

    def _get_anonymous_hash(self) -> str:
        """Get anonymous hash for pipeline component.

        :return: The anonymous hash of the pipeline component
        :rtype: str
        """
        # ideally we should always use rest object to generate hash as it's the same as
        # what we send to server-side, but changing the hash function will break reuse of
        # existing components except for command component (hash result is the same for
        # command component), so we just use rest object to generate hash for pipeline component,
        # which doesn't have reuse issue.
        component_interface_dict = self._to_rest_object().properties.component_spec
        # Hash local inputs in pipeline component jobs
        for job_name, job in self.jobs.items():
            if getattr(job, "inputs", None):
                for input_name, input_value in job.inputs.items():
                    try:
                        if (
                            isinstance(input_value._data, Input)
                            and input_value.path
                            and os.path.exists(input_value.path)
                        ):
                            start_time = time.time()
                            component_interface_dict["jobs"][job_name]["inputs"][input_name]["content_hash"] = (
                                get_object_hash(input_value.path)
                            )
                            module_logger.debug(
                                "Takes %s seconds to calculate the content hash of local input %s",
                                time.time() - start_time,
                                input_value.path,
                            )
                    except ValidationException:
                        pass
        hash_value: str = hash_dict(
            component_interface_dict,
            keys_to_omit=[
                # omit name since anonymous component will have same name
                "name",
                # omit _source since it doesn't impact component's uniqueness
                "_source",
                # omit id since it will be set after component is registered
                "id",
                # omit version since it will be set to this hash later
                "version",
            ],
        )
        return hash_value

    @classmethod
    def _load_from_rest_pipeline_job(cls, data: Dict) -> "PipelineComponent":
        # TODO: refine this?
        # Set type as None here to avoid schema validation failed
        definition_inputs = {p: {"type": None} for p in data.get("inputs", {}).keys()}
        definition_outputs = {p: {"type": None} for p in data.get("outputs", {}).keys()}
        return PipelineComponent(
            display_name=data.get("display_name"),
            description=data.get("description"),
            inputs=definition_inputs,
            outputs=definition_outputs,
            jobs=data.get("jobs"),
            _source=ComponentSource.REMOTE_WORKSPACE_JOB,
        )

    @classmethod
    def _resolve_sub_nodes(cls, rest_jobs: Dict) -> Dict:
        from azure.ai.ml.entities._job.pipeline._load_component import pipeline_node_factory

        sub_nodes = {}
        if rest_jobs is None:
            return sub_nodes
        for node_name, node in rest_jobs.items():
            # TODO: Remove this ad-hoc fix after unified arm id format in object
            component_id = node.get("componentId", "")
            if isinstance(component_id, str) and re.match(ASSET_ARM_ID_REGEX_FORMAT, component_id):
                node["componentId"] = component_id[len(ARM_ID_PREFIX) :]
            if not LoopNode._is_loop_node_dict(node):
                # skip resolve LoopNode first since it may reference other nodes
                # use node factory instead of BaseNode._from_rest_object here as AutoMLJob is not a BaseNode
                sub_nodes[node_name] = pipeline_node_factory.load_from_rest_object(obj=node)
        for node_name, node in rest_jobs.items():
            if LoopNode._is_loop_node_dict(node):
                # resolve LoopNode after all other nodes are resolved
                sub_nodes[node_name] = pipeline_node_factory.load_from_rest_object(obj=node, pipeline_jobs=sub_nodes)
        return sub_nodes

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        return PipelineComponentSchema(context=context)

    @classmethod
    def _get_skip_fields_in_schema_validation(cls) -> typing.List[str]:
        # jobs validations are done in _customized_validate()
        return ["jobs"]

    @classmethod
    def _check_ignored_keys(cls, obj: object) -> List[str]:
        """Return ignored keys in obj as a pipeline component when its value be set.

        :param obj: The object to examine
        :type obj: object
        :return: List of keys to ignore
        :rtype: List[str]
        """
        examine_mapping = {
            "compute": lambda val: val is not None,
            "settings": lambda val: val is not None and any(v is not None for v in val._to_dict().values()),
        }
        # Avoid new attr added by use `try_get_non...` instead of `hasattr` or `getattr` directly.
        return [k for k, has_set in examine_mapping.items() if has_set(try_get_non_arbitrary_attr(obj, k))]

    def _get_telemetry_values(self, *args: Any, **kwargs: Any) -> Dict:
        telemetry_values: dict = super()._get_telemetry_values()
        telemetry_values.update(
            {
                "source": self._source,
                "node_count": len(self.jobs),
                "node_type": json.dumps(self._job_types),
                "node_source": json.dumps(self._job_sources),
            }
        )
        return telemetry_values

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: ComponentVersion) -> Dict:
        # Pop jobs to avoid it goes with schema load
        jobs = obj.properties.component_spec.pop("jobs", None)
        init_params_dict: dict = super()._from_rest_object_to_init_params(obj)
        if jobs:
            try:
                init_params_dict["jobs"] = PipelineComponent._resolve_sub_nodes(jobs)
            except Exception as e:  # pylint: disable=W0718
                # Skip parse jobs if error exists.
                # TODO: https://msdata.visualstudio.com/Vienna/_workitems/edit/2052262
                module_logger.debug("Parse pipeline component jobs failed with: %s", e)
        return init_params_dict

    def _to_dict(self) -> Dict:
        return {**self._other_parameter, **super()._to_dict()}

    def _build_rest_component_jobs(self) -> Dict[str, dict]:
        """Build pipeline component jobs to rest.

        :return: A map of job name to rest objects
        :rtype: Dict[str, dict]
        """
        # Build the jobs to dict
        rest_component_jobs = {}
        for job_name, job in self.jobs.items():
            if isinstance(job, (BaseNode, ControlFlowNode)):
                rest_node_dict = job._to_rest_object()
            elif isinstance(job, AutoMLJob):
                rest_node_dict = json.loads(json.dumps(job._to_dict(inside_pipeline=True)))
            else:
                msg = f"Non supported job type in Pipeline jobs: {type(job)}"
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
            rest_component_jobs[job_name] = rest_node_dict
        return rest_component_jobs

    def _to_rest_object(self) -> ComponentVersion:
        """Check ignored keys and return rest object.

        :return: The component version
        :rtype: ComponentVersion
        """
        ignored_keys = self._check_ignored_keys(self)
        if ignored_keys:
            module_logger.warning("%s ignored on pipeline component %r.", ignored_keys, self.name)
        component = self._to_dict()
        # add source type to component rest object
        component["_source"] = self._source
        component["jobs"] = self._build_rest_component_jobs()
        component["sourceJobId"] = self._source_job_id
        if self._intellectual_property:
            # hack while full pass through supported is worked on for IPP fields
            component.pop("intellectual_property")
            component["intellectualProperty"] = self._intellectual_property._to_rest_object().serialize()
        properties = ComponentVersionProperties(
            component_spec=component,
            description=self.description,
            is_anonymous=self._is_anonymous,
            properties=self.properties,
            tags=self.tags,
        )
        result = ComponentVersion(properties=properties)
        result.name = self.name
        return result

    def __str__(self) -> str:
        try:
            toYaml: str = self._to_yaml()
            return toYaml
        except BaseException:  # pylint: disable=W0718
            toStr: str = super(PipelineComponent, self).__str__()
            return toStr
