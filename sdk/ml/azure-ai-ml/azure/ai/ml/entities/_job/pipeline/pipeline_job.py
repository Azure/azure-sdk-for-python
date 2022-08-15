# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import itertools
import json
import logging
import typing
from pathlib import Path
from typing import Dict, Union

from marshmallow import Schema

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2022_02_01_preview.models import AmlToken, JobBaseData, ManagedIdentity
from azure.ai.ml._restclient.v2022_02_01_preview.models import PipelineJob as RestPipelineJob
from azure.ai.ml._restclient.v2022_02_01_preview.models import UserIdentity
from azure.ai.ml._restclient.v2022_06_01_preview.models import PipelineJob as RestPipelineJob0601
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.pipeline import PipelineJobSchema
from azure.ai.ml._utils._arm_id_utils import get_resource_name_from_arm_id_safe
from azure.ai.ml._utils.utils import camel_to_snake, is_private_preview_enabled, transform_dict_keys
from azure.ai.ml.constants import AZUREML_PRIVATE_FEATURES_ENV_VAR, BASE_PATH_CONTEXT_KEY, ComponentSource
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._builders.parallel import Parallel
from azure.ai.ml.entities._builders.pipeline import Pipeline
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._component.pipeline_component import PipelineComponent
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job._input_output_helpers import (
    from_rest_data_outputs,
    from_rest_inputs_to_dataset_literal,
    to_rest_data_outputs,
    to_rest_dataset_literal_inputs,
)
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.pipeline._exceptions import UserErrorException
from azure.ai.ml.entities._job.pipeline._io import InputsAttrDict, OutputsAttrDict, PipelineIOMixin
from azure.ai.ml.entities._job.pipeline.pipeline_job_settings import PipelineJobSettings
from azure.ai.ml.entities._mixins import YamlTranslatableMixin
from azure.ai.ml.entities._validation import SchemaValidatableMixin, ValidationResult

module_logger = logging.getLogger(__name__)


class PipelineJob(Job, YamlTranslatableMixin, PipelineIOMixin, SchemaValidatableMixin):
    """Pipeline job. Please use @pipeline decorator to create a PipelineJob,
    not recommended instantiating it directly.

    :param component: Pipeline component version. Used to validate given value against
    :type component: PipelineComponent
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
    :param experiment_name: Name of the experiment the job will be created under, if None is provided, experiment will be set to current directory.
    :type experiment_name: str
    :param jobs: Pipeline component node name to component object.
    :type jobs: dict[str, BaseNode]
    :param settings: Setting of pipeline job.
    :type settings: ~azure.ai.ml.entities.PipelineJobSettings
    :param identity: Identity that training job will use while running on compute.
    :type identity: Union[ManagedIdentity, AmlToken, UserIdentity]
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
        component: PipelineComponent = None,
        inputs: Dict[str, Union[Input, str, bool, int, float]] = None,
        outputs: Dict[str, Output] = None,
        name: str = None,
        description: str = None,
        display_name: str = None,
        experiment_name: str = None,
        jobs: Dict[str, BaseNode] = None,
        settings: PipelineJobSettings = None,
        identity: Union[ManagedIdentity, AmlToken, UserIdentity] = None,
        compute: str = None,
        tags: Dict[str, str] = None,
        **kwargs,
    ):
        # initialize io
        inputs, outputs = inputs or {}, outputs or {}
        if isinstance(component, PipelineComponent) and component._source == ComponentSource.DSL:
            self._inputs = self._build_inputs_dict(component.inputs, inputs)
            # Build the outputs from entity output definition
            self._outputs = self._build_outputs_dict(component.outputs, outputs)
        else:
            # Build inputs/outputs dict without meta when definition not available
            self._inputs = self._build_inputs_dict_without_meta(inputs)
            self._outputs = self._build_outputs_dict_without_meta(outputs)
        if component is None:
            component = PipelineComponent(
                jobs=jobs,
                description=description,
                display_name=display_name,
                base_path=kwargs.get(BASE_PATH_CONTEXT_KEY),
                _source=kwargs.pop("_source", ComponentSource.CLASS),
            )

        self.component = component
        if "type" not in kwargs.keys():
            kwargs["type"] = "pipeline"
        super(PipelineJob, self).__init__(
            name=name,
            description=description or component.description,
            tags=tags,
            display_name=display_name or component.display_name,
            experiment_name=experiment_name,
            compute=compute,
            **kwargs,
        )

        self._remove_pipeline_input()
        self.compute = compute
        self._settings = settings if settings else PipelineJobSettings()
        self.identity = identity
        # TODO: remove default code & environment?
        self._default_code = None
        self._default_environment = None

    @property
    def inputs(self) -> InputsAttrDict:
        """Inputs of the pipeline job.

        :return: Inputs of the pipeline job.
        :rtype: dict
        """
        return self._inputs

    @property
    def outputs(self) -> OutputsAttrDict:
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
        return self.component.jobs

    @property
    def settings(self) -> PipelineJobSettings:
        """Settings of the pipeline job.

        :return: Settings of the pipeline job.
        :rtype: ~azure.ai.ml.entities.PipelineJobSettings
        """
        return self._settings

    @settings.setter
    def settings(self, value):
        self._settings = value

    @classmethod
    def _get_validation_error_target(cls) -> ErrorTarget:
        return ErrorTarget.PIPELINE

    @classmethod
    def _create_schema_for_validation(cls, context) -> typing.Union[PathAwareSchema, Schema]:
        # import this to ensure that nodes are registered before schema is created.

        return PipelineJobSchema(context=context)

    def _get_skip_fields_in_schema_validation(self) -> typing.List[str]:
        # jobs validations are done in _customized_validate()
        return ["jobs"]

    @property
    def _skip_required_compute_missing_validation(self):
        return True

    def _validate_compute_is_set(self):
        validation_result = self._create_empty_validation_result()
        if self.compute is not None:
            return validation_result
        if self.settings is not None and self.settings.default_compute is not None:
            return validation_result

        no_compute_nodes = []
        for node_name, node in self.jobs.items():
            if hasattr(node, "compute") and node.compute is None:
                if (
                    hasattr(node, "_skip_required_compute_missing_validation")
                    and node._skip_required_compute_missing_validation
                ):
                    continue
                no_compute_nodes.append(node_name)

        for node_name in no_compute_nodes:
            validation_result.append_error(
                yaml_path=f"jobs.{node_name}.compute",
                message="Compute not set",
            )
        return validation_result

    def _customized_validate(self) -> ValidationResult:
        """Validate that all provided inputs and parameters are valid for
        current pipeline and components in it."""
        validation_result = super(PipelineJob, self)._customized_validate()

        # Merge with pipeline component validate result for structure validation.
        validation_result.merge_with(self.component._customized_validate())
        # Validate compute
        validation_result.merge_with(self._validate_compute_is_set())
        # Validate Input
        validation_result.merge_with(self._validate_input())

        return validation_result

    def _validate_input(self):
        validation_result = self._create_empty_validation_result()
        used_pipeline_inputs = set(
            itertools.chain(*[self.component._get_input_binding_dict(node)[0] for node in self.jobs.values()])
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
                not self.inputs.get(key, None)  # input not provided
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

    def _remove_pipeline_input(self):
        """Remove None pipeline input.If not remove, it will pass "None" to
        backend."""
        redundant_pipeline_inputs = []
        for pipeline_input_name, pipeline_input in self._inputs.items():
            if pipeline_input._data is None:
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
                if isinstance(node, PipelineJob):
                    msg = error_msg.format("Pipeline job in pipeline")
                    raise UserErrorException(message=msg, no_personal_data_message=msg)

    def _to_node(self, context: Dict = None, **kwargs):
        """Translate a command job to a pipeline node when load schema.

        :param context: Context of command job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated command component.
        """
        component = self._to_component(context, **kwargs)

        return Pipeline(
            component=component,
            compute=self.compute,
            # Need to supply the inputs with double curly.
            inputs=self.inputs,
            outputs=self.outputs,
            description=self.description,
            tags=self.tags,
            display_name=self.display_name,
        )

    def _to_rest_object(self, new_version=False) -> JobBaseData:
        """Build current parameterized pipeline instance to a pipeline job object
        before submission.

        :param new_version: Use new model for inputs/outputs if new_version is true, as 0501 and later version
            change enum (like JobInputType) from camel to snake.
            Side effect by https://msdata.visualstudio.com/Vienna/_git/vienna/pullrequest/783594.
            TODO: Remove this after all Job and Component migrate to new version afterwards.
        :type new_version: bool
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

        settings_dict = vars(self.settings) if self.settings else {}
        settings_dict = {key: val for key, val in settings_dict.items() if val is not None}

        # add _source on pipeline job.settings
        if "_source" not in settings_dict:
            settings_dict.update({"_source": self.component._source})

        # Build the jobs to dict
        rest_component_jobs = {}
        for job_name, job in self.jobs.items():
            if isinstance(job, BaseNode):
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

        # TODO: Revisit this logic when multiple types of component jobs are supported
        rest_compute = self.compute

        # TODO: Remove this after all Job and Component migrate to new version afterwards.
        if new_version:
            pipeline_job = RestPipelineJob0601(
                compute_id=rest_compute,
                display_name=self.display_name,
                tags=self.tags,
                description=self.description,
                properties=self.properties,
                experiment_name=self.experiment_name,
                jobs=rest_component_jobs,
                inputs=to_rest_dataset_literal_inputs(built_inputs, new_version=new_version),
                outputs=to_rest_data_outputs(built_outputs, new_version=new_version),
                settings=settings_dict,
                identity=self.identity,
                source_job_id=self.id,
            )
        else:
            pipeline_job = RestPipelineJob(
                compute_id=rest_compute,
                display_name=self.display_name,
                tags=self.tags,
                description=self.description,
                properties=self.properties,
                experiment_name=self.experiment_name,
                jobs=rest_component_jobs,
                inputs=to_rest_dataset_literal_inputs(built_inputs, new_version=new_version),
                outputs=to_rest_data_outputs(built_outputs, new_version=new_version),
                settings=settings_dict,
                identity=self.identity,
            )
        rest_job = JobBaseData(properties=pipeline_job)
        rest_job.name = self.name
        return rest_job

    @classmethod
    def _load_from_rest(cls, obj: JobBaseData, new_version=False) -> "PipelineJob":
        """Build a pipeline instance from rest pipeline object.

        :param new_version: Use new model for inputs/outputs if new_version is true, as 0501 and later version
            change enum (like JobInputType) from camel to snake.
            Side effect by https://msdata.visualstudio.com/Vienna/_git/vienna/pullrequest/783594.
            TODO: Remove this after all Job and Component migrate to new version afterwards.
        :type new_version: bool
        :return: pipeline job.
        """
        properties: RestPipelineJob = obj.properties
        # Workaround for BatchEndpoint as these fields are not filled in
        # Unpack the inputs
        from_rest_inputs = from_rest_inputs_to_dataset_literal(properties.inputs, new_version=new_version) or {}
        from_rest_outputs = from_rest_data_outputs(properties.outputs, new_version=new_version) or {}
        # Unpack the component jobs
        sub_nodes = {}
        if properties.jobs:
            for node_name, node in properties.jobs.items():
                sub_nodes[node_name] = BaseNode._from_rest_object(node)
        # backend may still store Camel settings, eg: DefaultDatastore, translate them to snake when load back
        settings_dict = transform_dict_keys(properties.settings, camel_to_snake) if properties.settings else None
        settings_sdk = PipelineJobSettings(**settings_dict) if settings_dict else PipelineJobSettings()

        job = PipelineJob(
            component=PipelineComponent._load_from_rest_pipeline_job(
                dict(
                    inputs=from_rest_inputs,
                    outputs=from_rest_outputs,
                    display_name=properties.display_name,
                    description=properties.description,
                    jobs=sub_nodes,
                )
            ),
            inputs=from_rest_inputs,
            outputs=from_rest_outputs,
            name=obj.name,
            id=obj.id,
            display_name=properties.display_name,
            tags=properties.tags,
            properties=properties.properties,
            experiment_name=properties.experiment_name,
            status=properties.status,
            creation_context=obj.system_data,
            services=properties.services,
            compute=get_resource_name_from_arm_id_safe(properties.compute_id),
            settings=settings_sdk,
            identity=properties.identity,
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
        loaded_schema = cls._create_schema_for_validation(context=context).load(data, **kwargs)

        # replace repeat component with first occurrence to reduce arm id resolution
        # current load yaml file logic is in azure.ai.ml._schema.core.schema.YamlFileSchema.load_from_file
        # is it possible to load the same yaml file only once in 1 pipeline loading?
        for node_name, first_occurrence in component_first_occurrence.items():
            job = loaded_schema["jobs"][node_name]
            job._component = loaded_schema["jobs"][first_occurrence].component
            # For Parallel job, should also align task attribute which is usually from component.task
            if isinstance(job, Parallel):
                job.task = loaded_schema["jobs"][first_occurrence].task
        return PipelineJob(
            base_path=context[BASE_PATH_CONTEXT_KEY],
            _source=ComponentSource.YAML_JOB,
            **loaded_schema,
        )

    def __str__(self):
        try:
            return self._to_yaml()
        except BaseException:
            return super(PipelineJob, self).__str__()

    def _get_telemetry_values(self):
        telemetry_values = super()._get_telemetry_values()
        telemetry_values.update(self.component._get_telemetry_values())
        telemetry_values.pop("is_anonymous")
        return telemetry_values

    def _to_component(self, context: Dict = None, **kwargs):
        """Translate a pipeline job to pipeline component.

        :param context: Context of pipeline job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated pipeline component.
        """
        from azure.ai.ml.entities._component.pipeline_component import PipelineComponent

        ignored_keys = PipelineComponent._check_ignored_keys(self)
        if ignored_keys:
            name = self.name or self.display_name
            name = f"{name!r} " if name else ""
            module_logger.warning(f"{ignored_keys} ignored when translating PipelineJob {name}to PipelineComponent.")

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
