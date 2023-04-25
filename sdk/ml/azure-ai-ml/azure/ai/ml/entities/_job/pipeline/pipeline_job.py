# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
import itertools
import logging
import typing
from functools import partial
from pathlib import Path
from typing import Dict, List, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import JobBase
from azure.ai.ml._restclient.v2023_04_01_preview.models import PipelineJob as RestPipelineJob
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.pipeline.pipeline_job import PipelineJobSchema
from azure.ai.ml._utils._arm_id_utils import get_resource_name_from_arm_id_safe
from azure.ai.ml._utils.utils import (
    camel_to_snake,
    is_data_binding_expression,
    is_private_preview_enabled,
    transform_dict_keys,
)
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import AZUREML_PRIVATE_FEATURES_ENV_VAR, BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._component import ComponentSource
from azure.ai.ml.constants._job.pipeline import ValidationErrorCode
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._builders.condition_node import ConditionNode
from azure.ai.ml.entities._builders.control_flow_node import LoopNode
from azure.ai.ml.entities._builders.import_node import Import
from azure.ai.ml.entities._builders.parallel import Parallel
from azure.ai.ml.entities._builders.pipeline import Pipeline
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._component.pipeline_component import PipelineComponent
from azure.ai.ml.entities._inputs_outputs.group_input import GroupInput

# from azure.ai.ml.entities._job.identity import AmlToken, Identity, ManagedIdentity, UserIdentity
from azure.ai.ml.entities._credentials import (
    AmlTokenConfiguration,
    ManagedIdentityConfiguration,
    UserIdentityConfiguration,
    _BaseJobIdentityConfiguration,
)
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job._input_output_helpers import (
    from_rest_data_outputs,
    from_rest_inputs_to_dataset_literal,
    to_rest_data_outputs,
    to_rest_dataset_literal_inputs,
)
from azure.ai.ml.entities._job.import_job import ImportJob
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.job_service import JobServiceBase
from azure.ai.ml.entities._job.pipeline._io import PipelineInput, PipelineIOMixin
from azure.ai.ml.entities._job.pipeline.pipeline_job_settings import PipelineJobSettings
from azure.ai.ml.entities._mixins import YamlTranslatableMixin
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._validation import MutableValidationResult, SchemaValidatableMixin
from azure.ai.ml.exceptions import ErrorTarget, UserErrorException

module_logger = logging.getLogger(__name__)


class PipelineJob(Job, YamlTranslatableMixin, PipelineIOMixin, SchemaValidatableMixin):
    """Pipeline job.

    You should not instantiate this class directly. Instead, you should
    use @pipeline decorator to create a PipelineJob

    :param component: Pipeline component version. The field is mutual exclusive with 'jobs'.
    :type component: Union[str, PipelineComponent]
    :param inputs: Inputs to the pipeline job.
    :type inputs: dict[str, Union[Input, str, bool, int, float]]
    :param outputs: Outputs the pipeline job.
    :type outputs: dict[str, Output]
    :param name: Name of the PipelineJob.
    :type name: str
    :param description: Description of the pipeline job.
    :type description: str
    :param display_name: Display name of the pipeline job.
    :type display_name: str
    :param experiment_name: Name of the experiment the job will be created under, \
        if None is provided, experiment will be set to current directory.
    :type experiment_name: str
    :param jobs: Pipeline component node name to component object.
    :type jobs: dict[str, BaseNode]
    :param settings: Setting of pipeline job.
    :type settings: ~azure.ai.ml.entities.PipelineJobSettings
    :param identity: Identity that training job will use while running on compute.
    :type identity: Union[
        ManagedIdentityConfiguration,
        AmlTokenConfiguration,
        UserIdentityConfiguration]
    :param compute: Compute target name of the built pipeline.
    :type compute: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        component: Optional[Union[str, PipelineComponent]] = None,
        inputs: Optional[Dict[str, Union[Input, str, bool, int, float]]] = None,
        outputs: Optional[Dict[str, Output]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        display_name: Optional[str] = None,
        experiment_name: Optional[str] = None,
        jobs: Optional[Dict[str, BaseNode]] = None,
        settings: Optional[PipelineJobSettings] = None,
        identity: Optional[
            Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]
        ] = None,
        compute: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        # initialize io
        inputs, outputs = inputs or {}, outputs or {}
        if isinstance(component, PipelineComponent) and component._source in [
            ComponentSource.DSL,
            ComponentSource.YAML_COMPONENT,
        ]:
            self._inputs = self._build_inputs_dict(component.inputs, inputs)
            # for pipeline component created pipeline jobs,
            # it's output should have same value with the component outputs
            self._outputs = self._build_pipeline_outputs_dict(component.outputs)
        else:
            # Build inputs/outputs dict without meta when definition not available
            self._inputs = self._build_inputs_dict_without_meta(inputs)
            # for node created pipeline jobs,
            # it's output should have same value with the given outputs
            self._outputs = self._build_pipeline_outputs_dict(outputs=outputs)
        source = kwargs.pop("_source", ComponentSource.CLASS)
        if component is None:
            component = PipelineComponent(
                jobs=jobs,
                description=description,
                display_name=display_name,
                base_path=kwargs.get(BASE_PATH_CONTEXT_KEY),
                _source=source,
            )

        # If component is Pipeline component, jobs will be component.jobs
        self._jobs = (jobs or {}) if isinstance(component, str) else {}

        self.component: Union[PipelineComponent, str] = component
        if "type" not in kwargs.keys():
            kwargs["type"] = JobType.PIPELINE
        if isinstance(component, PipelineComponent):
            description = component.description if description is None else description
            display_name = component.display_name if display_name is None else display_name
        super(PipelineJob, self).__init__(
            name=name,
            description=description,
            tags=tags,
            display_name=display_name,
            experiment_name=experiment_name,
            compute=compute,
            **kwargs,
        )

        self._remove_pipeline_input()
        self.compute = compute
        self._settings = None
        self.settings = settings
        self.identity = identity
        # TODO: remove default code & environment?
        self._default_code = None
        self._default_environment = None

    @property
    def inputs(self) -> Dict[str, Union[Input, str, bool, int, float]]:
        """Inputs of the pipeline job.

        :return: Inputs of the pipeline job.
        :rtype: dict
        """
        return self._inputs

    @property
    def outputs(self) -> Dict[str, Union[str, Output]]:
        """Outputs of the pipeline job.

        :return: Outputs of the pipeline job.
        :rtype: dict
        """
        return self._outputs

    @property
    def jobs(self):
        """Return jobs of pipeline job.

        :return: Jobs of pipeline job.
        :rtype: dict
        """
        return self.component.jobs if isinstance(self.component, PipelineComponent) else self._jobs

    @property
    def settings(self) -> PipelineJobSettings:
        """Settings of the pipeline job.

        :return: Settings of the pipeline job.
        :rtype: ~azure.ai.ml.entities.PipelineJobSettings
        """
        if self._settings is None:
            self._settings = PipelineJobSettings()
        return self._settings

    @settings.setter
    def settings(self, value):
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
    def _get_validation_error_target(cls) -> ErrorTarget:
        return ErrorTarget.PIPELINE

    @classmethod
    def _create_schema_for_validation(cls, context) -> PathAwareSchema:
        # import this to ensure that nodes are registered before schema is created.

        return PipelineJobSchema(context=context)

    @classmethod
    def _get_skip_fields_in_schema_validation(cls) -> typing.List[str]:
        # jobs validations are done in _customized_validate()
        return ["component", "jobs"]

    @property
    def _skip_required_compute_missing_validation(self):
        return True

    def _validate_compute_is_set(self):
        validation_result = self._create_empty_validation_result()
        if self.compute is not None:
            return validation_result
        if self.settings is not None and self.settings.default_compute is not None:
            return validation_result

        validation_result.merge_with(self.component._validate_compute_is_set())
        return validation_result

    def _customized_validate(self) -> MutableValidationResult:
        """Validate that all provided inputs and parameters are valid for current pipeline and components in it."""
        validation_result = super(PipelineJob, self)._customized_validate()

        if isinstance(self.component, PipelineComponent):
            # Merge with pipeline component validate result for structure validation.
            # Skip top level parameter missing type error
            validation_result.merge_with(
                self.component._customized_validate(),
                condition_skip=lambda x: x.error_code == ValidationErrorCode.PARAMETER_TYPE_UNKNOWN
                and x.yaml_path.startswith("inputs"),
            )
            # Validate compute
            validation_result.merge_with(self._validate_compute_is_set())
        # Validate Input
        validation_result.merge_with(self._validate_input())
        # Validate initialization & finalization jobs
        validation_result.merge_with(self._validate_init_finalize_job())

        return validation_result

    def _validate_input(self):
        validation_result = self._create_empty_validation_result()
        # TODO(1979547): refine this logic: not all nodes have `_get_input_binding_dict` method
        used_pipeline_inputs = set(
            itertools.chain(
                *[
                    self.component._get_input_binding_dict(node if not isinstance(node, LoopNode) else node.body)[0]
                    for node in self.jobs.values()
                    if not isinstance(node, ConditionNode)
                    # condition node has no inputs
                ]
            )
        )
        # validate inputs
        if not isinstance(self.component, Component):
            return validation_result
        for key, meta in self.component.inputs.items():
            if key not in used_pipeline_inputs:
                # Only validate inputs certainly used.
                continue
            # raise error when required input with no default value not set
            if (
                self.inputs.get(key, None) is None  # input not provided
                and meta.optional is not True  # and it's required
                and meta.default is None  # and it does not have default
            ):
                name = self.name or self.display_name
                name = f"{name!r} " if name else ""
                validation_result.append_error(
                    yaml_path=f"inputs.{key}",
                    message=f"Required input {key!r} for pipeline {name}not provided.",
                )
        return validation_result

    def _validate_init_finalize_job(self) -> MutableValidationResult:
        validation_result = self._create_empty_validation_result()
        # subgraph (PipelineComponent) should not have on_init/on_finalize set
        for job_name, job in self.jobs.items():
            if job.type != "pipeline":
                continue
            if job.settings.on_init:
                validation_result.append_error(
                    yaml_path=f"jobs.{job_name}.settings.on_init",
                    message="On_init is not supported for pipeline component.",
                )
            if job.settings.on_finalize:
                validation_result.append_error(
                    yaml_path=f"jobs.{job_name}.settings.on_finalize",
                    message="On_finalize is not supported for pipeline component.",
                )

        # quick return if neither on_init nor on_finalize is set
        if self.settings.on_init is None and self.settings.on_finalize is None:
            return validation_result

        on_init, on_finalize = self.settings.on_init, self.settings.on_finalize
        append_on_init_error = partial(validation_result.append_error, "settings.on_init")
        append_on_finalize_error = partial(validation_result.append_error, "settings.on_finalize")
        # on_init and on_finalize cannot be same
        if on_init == on_finalize:
            append_on_init_error(f"Invalid on_init job {on_init}, it should be different from on_finalize.")
            append_on_finalize_error(f"Invalid on_finalize job {on_finalize}, it should be different from on_init.")
        # pipeline should have at least one normal node
        if len(set(self.jobs.keys()) - {on_init, on_finalize}) == 0:
            validation_result.append_error(yaml_path="jobs", message="No other job except for on_init/on_finalize job.")

        def _is_control_flow_node(_validate_job_name: str) -> bool:
            from azure.ai.ml.entities._builders.control_flow_node import ControlFlowNode

            _validate_job = self.jobs[_validate_job_name]
            return issubclass(type(_validate_job), ControlFlowNode)

        def _is_isolated_job(_validate_job_name: str) -> bool:
            def _try_get_data_bindings(_name: str, _input_output_data) -> Union[List[str], None]:
                """Try to get data bindings from input/output data, return None if not found."""
                # handle group input
                if GroupInput._is_group_attr_dict(_input_output_data):
                    # flatten to avoid nested cases
                    flattened_values = list(_input_output_data.flatten(_name).values())
                    # handle invalid empty group
                    if len(flattened_values) == 0:
                        return None
                    return [_value.path for _value in flattened_values]
                _input_output_data = _input_output_data._data
                if isinstance(_input_output_data, str):
                    return [_input_output_data]
                if not hasattr(_input_output_data, "_data_binding"):
                    return None
                return [_input_output_data._data_binding()]

            _validate_job = self.jobs[_validate_job_name]
            # no input to validate job
            for _input_name in _validate_job.inputs:
                _data_bindings = _try_get_data_bindings(_input_name, _validate_job.inputs[_input_name])
                if _data_bindings is None:
                    continue
                for _data_binding in _data_bindings:
                    if is_data_binding_expression(_data_binding, ["parent", "jobs"]):
                        return False
            # no output from validate job - iterate other jobs input(s) to validate
            for _job_name, _job in self.jobs.items():
                # exclude control flow node as it does not have inputs
                if _is_control_flow_node(_job_name):
                    continue
                for _input_name in _job.inputs:
                    _data_bindings = _try_get_data_bindings(_input_name, _job.inputs[_input_name])
                    if _data_bindings is None:
                        continue
                    for _data_binding in _data_bindings:
                        if is_data_binding_expression(_data_binding, ["parent", "jobs", _validate_job_name]):
                            return False
            return True

        # validate on_init
        if on_init is not None:
            if on_init not in self.jobs:
                append_on_init_error(f"On_init job name {on_init} not exists in jobs.")
            else:
                if _is_control_flow_node(on_init):
                    append_on_init_error("On_init job should not be a control flow node.")
                elif not _is_isolated_job(on_init):
                    append_on_init_error("On_init job should not have connection to other execution node.")
        # validate on_finalize
        if on_finalize is not None:
            if on_finalize not in self.jobs:
                append_on_finalize_error(f"On_finalize job name {on_finalize} not exists in jobs.")
            else:
                if _is_control_flow_node(on_finalize):
                    append_on_finalize_error("On_finalize job should not be a control flow node.")
                elif not _is_isolated_job(on_finalize):
                    append_on_finalize_error("On_finalize job should not have connection to other execution node.")
        return validation_result

    def _remove_pipeline_input(self):
        """Remove None pipeline input.If not remove, it will pass "None" to backend."""
        redundant_pipeline_inputs = []
        for pipeline_input_name, pipeline_input in self._inputs.items():
            if isinstance(pipeline_input, PipelineInput) and pipeline_input._data is None:
                redundant_pipeline_inputs.append(pipeline_input_name)
        for redundant_pipeline_input in redundant_pipeline_inputs:
            self._inputs.pop(redundant_pipeline_input)

    def _check_private_preview_features(self):
        """Checks is private preview features included in pipeline.

        If private preview environment not set, raise exception.
        """
        if not is_private_preview_enabled():
            error_msg = (
                "{} is a private preview feature, "
                f"please set environment variable {AZUREML_PRIVATE_FEATURES_ENV_VAR} to true to use it."
            )
            # check has not supported nodes
            for _, node in self.jobs.items():
                # TODO: Remove in PuP
                if isinstance(node, (ImportJob, Import)):
                    msg = error_msg.format("Import job in pipeline")
                    raise UserErrorException(message=msg, no_personal_data_message=msg)

    def _to_node(self, context: Optional[Dict] = None, **kwargs):
        """Translate a command job to a pipeline node when load schema.

        (Write a pipeline job as node in yaml is not supported presently.)

        :param context: Context of command job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated command component.
        """
        component = self._to_component(context, **kwargs)

        return Pipeline(  # pylint: disable=abstract-class-instantiated
            component=component,
            compute=self.compute,
            # Need to supply the inputs with double curly.
            inputs=self.inputs,
            outputs=self.outputs,
            description=self.description,
            tags=self.tags,
            display_name=self.display_name,
            properties=self.properties,
        )

    def _to_rest_object(self) -> JobBase:
        """Build current parameterized pipeline instance to a pipeline job object before submission.

        :return: Rest pipeline job.
        """
        # Check if there are private preview features in it
        self._check_private_preview_features()

        # Build the inputs to dict. Handle both value & binding assignment.
        # Example: {
        #   "input_data": {"data": {"path": "path/to/input/data"},  "mode"="Mount"},
        #   "input_value": 10,
        #   "learning_rate": "${{jobs.step1.inputs.learning_rate}}"
        # }
        built_inputs = self._build_inputs()

        # Build the outputs to dict
        # example: {"eval_output": "${{jobs.eval.outputs.eval_output}}"}
        built_outputs = self._build_outputs()

        settings_dict = self.settings._to_dict()

        if isinstance(self.component, PipelineComponent):
            source = self.component._source
            # Build the jobs to dict
            rest_component_jobs = self.component._build_rest_component_jobs()
        else:
            source = ComponentSource.REMOTE_WORKSPACE_JOB
            rest_component_jobs = {}
        # add _source on pipeline job.settings
        if "_source" not in settings_dict:
            settings_dict.update({"_source": source})

        # TODO: Revisit this logic when multiple types of component jobs are supported
        rest_compute = self.compute
        # This will be resolved in job_operations _resolve_arm_id_or_upload_dependencies.
        component_id = self.component if isinstance(self.component, str) else self.component.id

        # TODO remove it in the future.
        # MFE not support pass None or empty input value. Remove the empty inputs in pipeline job.
        built_inputs = {k: v for k, v in built_inputs.items() if v is not None and v != ""}

        pipeline_job = RestPipelineJob(
            compute_id=rest_compute,
            component_id=component_id,
            display_name=self.display_name,
            tags=self.tags,
            description=self.description,
            properties=self.properties,
            experiment_name=self.experiment_name,
            jobs=rest_component_jobs,
            inputs=to_rest_dataset_literal_inputs(built_inputs, job_type=self.type),
            outputs=to_rest_data_outputs(built_outputs),
            settings=settings_dict,
            services={k: v._to_rest_object() for k, v in self.services.items()} if self.services else None,
            identity=self.identity._to_job_rest_object() if self.identity else None,
        )

        rest_job = JobBase(properties=pipeline_job)
        rest_job.name = self.name
        return rest_job

    @classmethod
    def _load_from_rest(cls, obj: JobBase) -> "PipelineJob":
        """Build a pipeline instance from rest pipeline object.

        :return: pipeline job.
        """
        properties: RestPipelineJob = obj.properties
        # Workaround for BatchEndpoint as these fields are not filled in
        # Unpack the inputs
        from_rest_inputs = from_rest_inputs_to_dataset_literal(properties.inputs) or {}
        from_rest_outputs = from_rest_data_outputs(properties.outputs) or {}
        # Unpack the component jobs
        sub_nodes = PipelineComponent._resolve_sub_nodes(properties.jobs) if properties.jobs else {}
        # backend may still store Camel settings, eg: DefaultDatastore, translate them to snake when load back
        settings_dict = transform_dict_keys(properties.settings, camel_to_snake) if properties.settings else None
        settings_sdk = PipelineJobSettings(**settings_dict) if settings_dict else PipelineJobSettings()
        # Create component or use component id
        if getattr(properties, "component_id", None):
            component = properties.component_id
        else:
            component = PipelineComponent._load_from_rest_pipeline_job(
                dict(
                    inputs=from_rest_inputs,
                    outputs=from_rest_outputs,
                    display_name=properties.display_name,
                    description=properties.description,
                    jobs=sub_nodes,
                )
            )

        job = PipelineJob(
            component=component,
            inputs=from_rest_inputs,
            outputs=from_rest_outputs,
            name=obj.name,
            id=obj.id,
            jobs=sub_nodes,
            display_name=properties.display_name,
            tags=properties.tags,
            properties=properties.properties,
            experiment_name=properties.experiment_name,
            status=properties.status,
            creation_context=SystemData._from_rest_object(obj.system_data) if obj.system_data else None,
            services=JobServiceBase._from_rest_job_services(properties.services) if properties.services else None,
            compute=get_resource_name_from_arm_id_safe(properties.compute_id),
            settings=settings_sdk,
            identity=_BaseJobIdentityConfiguration._from_rest_object(properties.identity)
            if properties.identity
            else None,
        )

        return job

    def _to_dict(self) -> Dict:
        return self._dump_for_validation()

    @classmethod
    def _component_items_from_path(cls, data: Dict):
        if "jobs" in data:
            for node_name, job_instance in data["jobs"].items():
                potential_component_path = job_instance["component"] if "component" in job_instance else None
                if isinstance(potential_component_path, str) and potential_component_path.startswith("file:"):
                    yield node_name, potential_component_path

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "PipelineJob":
        path_first_occurrence = {}
        component_first_occurrence = {}
        for node_name, component_path in cls._component_items_from_path(data):
            if component_path in path_first_occurrence:
                component_first_occurrence[node_name] = path_first_occurrence[component_path]
                # set components to be replaced here may break the validation logic
            else:
                path_first_occurrence[component_path] = node_name

        # use this instead of azure.ai.ml.entities._util.load_from_dict to avoid parsing
        # pylint: disable=no-member
        loaded_schema = cls._create_schema_for_validation(context=context).load(data, **kwargs)

        # replace repeat component with first occurrence to reduce arm id resolution
        # current load yaml file logic is in azure.ai.ml._schema.core.schema.YamlFileSchema.load_from_file
        # is it possible to load the same yaml file only once in 1 pipeline loading?
        for node_name, first_occurrence in component_first_occurrence.items():
            job = loaded_schema["jobs"][node_name]
            job._component = loaded_schema["jobs"][first_occurrence].component
            # For Parallel job, should also align task attribute which is usually from component.task
            if isinstance(job, Parallel):
                job.task = job._component.task
                # parallel.task.code is based on parallel._component.base_path, so need to update it
                job._base_path = job._component.base_path
        return PipelineJob(
            base_path=context[BASE_PATH_CONTEXT_KEY],
            _source=ComponentSource.YAML_JOB,
            **loaded_schema,
        )

    def __str__(self):
        try:
            return self._to_yaml()
        except BaseException:  # pylint: disable=broad-except
            return super(PipelineJob, self).__str__()

    def _get_telemetry_values(self):
        telemetry_values = super()._get_telemetry_values()
        if isinstance(self.component, PipelineComponent):
            telemetry_values.update(self.component._get_telemetry_values())
        else:
            telemetry_values.update({"source": ComponentSource.REMOTE_WORKSPACE_JOB})
        telemetry_values.pop("is_anonymous")
        return telemetry_values

    def _to_component(self, context: Optional[Dict] = None, **kwargs):
        """Translate a pipeline job to pipeline component.

        :param context: Context of pipeline job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated pipeline component.
        """
        ignored_keys = PipelineComponent._check_ignored_keys(self)
        if ignored_keys:
            name = self.name or self.display_name
            name = f"{name!r} " if name else ""
            module_logger.warning("%s ignored when translating PipelineJob %sto PipelineComponent.", ignored_keys, name)
        pipeline_job_dict = kwargs.get("pipeline_job_dict", {})
        context = context or {BASE_PATH_CONTEXT_KEY: Path("./")}

        # Create anonymous pipeline component with default version as 1
        return PipelineComponent(
            base_path=context[BASE_PATH_CONTEXT_KEY],
            display_name=self.display_name,
            inputs=self._to_inputs(inputs=self.inputs, pipeline_job_dict=pipeline_job_dict),
            outputs=self._to_outputs(outputs=self.outputs, pipeline_job_dict=pipeline_job_dict),
            jobs=self.jobs,
        )
