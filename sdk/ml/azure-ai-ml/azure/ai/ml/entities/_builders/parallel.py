# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import logging
import uuid
from typing import Dict, List, Union
from enum import Enum
import re

from marshmallow import Schema

from .base_node import BaseNode
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    JobInput as RestJobInput,
    JobOutput as RestJobOutput,
)
from azure.ai.ml.constants import (
    ComponentJobConstants,
    BASE_PATH_CONTEXT_KEY,
    NodeType,
    ComponentSource,
    ARM_ID_PREFIX,
)

from azure.ai.ml.entities._job._input_output_helpers import (
    to_rest_dataset_literal_inputs,
    from_rest_inputs_to_dataset_literal,
    to_rest_data_outputs,
    from_rest_data_outputs,
)
from azure.ai.ml.entities._job.pipeline._pipeline_job_helpers import (
    process_sdk_component_job_io,
    from_dict_to_rest_io,
)
from azure.ai.ml.entities import (
    Component,
    ParallelComponent,
    ParallelJob,
    ResourceConfiguration,
    Environment,
)
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml._restclient.v2022_02_01_preview.models import ResourceConfiguration as RestResourceConfiguration
from .._job.pipeline._io import PipelineInput, PipelineOutputBase
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from azure.ai.ml.entities._job.parallel.parallel_task import ParallelTask
from azure.ai.ml.entities._job.parallel.retry_settings import RetrySettings
from azure.ai.ml.entities._job.parallel.parameterized_parallel import ParameterizedParallel
from .._util import validate_attribute_type, convert_ordered_dict_to_dict, get_rest_dict
from ..._schema import PathAwareSchema
from ..._utils._arm_id_utils import get_resource_name_from_arm_id_safe

module_logger = logging.getLogger(__name__)


class Parallel(BaseNode):
    """Base class for parallel node, used for parallel component version consumption.

    :param component: Id or instance of the parallel component/job to be run for the step
    :type component: parallelComponent
    :param name: Name of the parallel.
    :type name: str
    :param description: Description of the commad.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The job property dictionary.
    :type properties: dict[str, str]
    :param display_name: Display name of the job.
    :type display_name: str
    :param retry_settings: parallel job run failed retry
    :type retry_settings: BatchRetrySettings
    :param logging_level: A string of the logging level name
    :type logging_level: str
    :param max_concurrency_per_instance: The max parallellism that each compute instance has.
    :type max_concurrency_per_instance: int
    :param error_threshold: The number of item processing failures should be ignored.
    :type error_threshold: int
    :param mini_batch_error_threshold: The number of mini batch processing failures should be ignored.
    :type mini_batch_error_threshold: int
    :param task: The parallel task.
    :type task: ParallelTask
    :param mini_batch_size: For FileDataset input, this field is the number of files a user script can process
        in one run() call. For TabularDataset input, this field is the approximate size of data the user script
        can process in one run() call. Example values are 1024, 1024KB, 10MB, and 1GB.
        (optional, default value is 10 files for FileDataset and 1MB for TabularDataset.) This value could be set
        through PipelineParameter
    :type mini_batch_size: str
    :param input_data: The input data.
    :type input_data: str
    :param inputs: Inputs of the component/job.
    :type inputs: dict
    :param outputs: Outputs of the component/job.
    :type outputs: dict
    """

    def __init__(
        self,
        *,
        component: Union[ParallelComponent, str],
        compute: str = None,
        inputs: Dict[str, Union[PipelineInput, PipelineOutputBase, Input, str, bool, int, float, Enum, "Input"]] = None,
        outputs: Dict[str, Union[str, Output, "Output"]] = None,
        retry_settings: Dict[str, Union[RetrySettings, str]] = None,
        logging_level: str = None,
        max_concurrency_per_instance: int = None,
        error_threshold: int = None,
        mini_batch_error_threshold: int = None,
        input_data: str = None,
        task: Dict[str, Union[ParallelTask, str]] = None,
        mini_batch_size: int = None,
        resources: ResourceConfiguration = None,
        environment_variables: Dict = None,
        **kwargs,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())
        self._init = True
        kwargs.pop("type", None)
        _from_component_func = kwargs.pop("_from_component_func", False)

        BaseNode.__init__(self, type=NodeType.PARALLEL, component=component, compute=compute, **kwargs)

        self._task = task

        if mini_batch_size is not None and not isinstance(mini_batch_size, int):
            """Convert str to int."""
            pattern = re.compile(r"^\d+([kKmMgG][bB])*$")
            if not pattern.match(mini_batch_size):
                raise ValueError(r"Parameter mini_batch_size must follow regex rule ^\d+([kKmMgG][bB])*$")

            try:
                mini_batch_size = int(mini_batch_size)
            except ValueError:
                unit = mini_batch_size[-2:].lower()
                if unit == "kb":
                    mini_batch_size = int(mini_batch_size[0:-2]) * 1024
                elif unit == "mb":
                    mini_batch_size = int(mini_batch_size[0:-2]) * 1024 * 1024
                elif unit == "gb":
                    mini_batch_size = int(mini_batch_size[0:-2]) * 1024 * 1024 * 1024
                else:
                    raise ValueError("mini_batch_size unit must be kb, mb or gb")

        self.mini_batch_size = mini_batch_size
        self.input_data = input_data
        self._retry_settings = retry_settings
        self.logging_level = logging_level
        self.max_concurrency_per_instance = max_concurrency_per_instance
        self.error_threshold = error_threshold
        self.mini_batch_error_threshold = mini_batch_error_threshold
        self._resources = resources
        self.environment_variables = {} if environment_variables is None else environment_variables

        if isinstance(self.component, ParallelComponent):
            self.resources = self.resources or self.component.resources
            self.input_data = self.input_data or self.component.input_data
            self.max_concurrency_per_instance = (
                self.max_concurrency_per_instance or self.component.max_concurrency_per_instance
            )
            self.mini_batch_error_threshold = (
                self.mini_batch_error_threshold or self.component.mini_batch_error_threshold
            )
            self.mini_batch_size = self.mini_batch_size or self.component.mini_batch_size
            self._task = self._task or self.component.task

        # initialize io
        inputs, outputs = inputs or {}, outputs or {}
        # when command node is constructed inside dsl.pipeline, inputs can be PipelineInput or Output of another node
        supported_input_types = (
            PipelineInput,
            PipelineOutputBase,
            Input,
            str,
            bool,
            int,
            float,
            Enum,
        )
        self._validate_io(inputs, supported_input_types, Input)
        supported_output_types = (str, Output)
        self._validate_io(outputs, supported_output_types, Output)
        # parse empty dict to None so we won't pass default mode, type to backend
        for k, v in inputs.items():
            if v == {}:
                inputs[k] = None
        # TODO: get rid of self._job_inputs, self._job_outputs once we have unified Input
        self._job_inputs, self._job_outputs = inputs, outputs
        if isinstance(component, Component):
            # Build the inputs from component input definition and given inputs, unfilled inputs will be None
            self._inputs = self._build_inputs_dict(component.inputs, inputs or {})
            # Build the outputs from component output definition and given outputs, unfilled outputs will be None
            self._outputs = self._build_outputs_dict(component.outputs, outputs or {})
        else:
            # Build inputs/outputs dict without meta when definition not available
            self._inputs = self._build_inputs_dict_without_meta(inputs or {})
            self._outputs = self._build_outputs_dict_without_meta(outputs or {})

        # Generate an id for every component instance
        self._instance_id = str(uuid.uuid4())
        if _from_component_func:
            # add current component in pipeline stack for dsl scenario
            self._register_in_current_pipeline_component_builder()

        self._init = False

    @property
    def retry_settings(self) -> RetrySettings:
        return self._retry_settings

    @retry_settings.setter
    def retry_settings(self, value):
        if isinstance(value, dict):
            value = RetrySettings(**value)
        self._retry_settings = value

    @property
    def resources(self) -> ResourceConfiguration:
        return self._resources

    @resources.setter
    def resources(self, value):
        if isinstance(value, dict):
            value = ResourceConfiguration(**value)
        self._resources = value

    @property
    def component(self) -> Union[str, ParallelComponent]:
        return self._component

    @property
    def task(self) -> ParallelTask:
        return self._task

    @task.setter
    def task(self, value):
        if isinstance(value, dict):
            value = ParallelTask(**value)
        self._task = value

    def set_resources(
        self,
        *,
        instance_type: Union[str, List[str]] = None,
        instance_count: int = None,
        properties: Dict = None,
        **kwargs,
    ):
        """Set resources for Parallel."""
        if self.resources is None:
            self.resources = ResourceConfiguration()

        if instance_type is not None:
            self.resources.instance_type = instance_type
        if instance_count is not None:
            self.resources.instance_count = instance_count
        if properties is not None:
            self.resources.properties = properties

        # Save the resources to internal component as well, otherwise calling sweep() will loose the settings
        if isinstance(self.component, Component):
            self.component.resources = self.resources

    def _initializing(self) -> bool:
        # use this to indicate ongoing init process so all attributes set during init process won't be set as
        # arbitrary attribute in _AttrDict
        # TODO: replace this hack
        return self._init

    @classmethod
    def _validate_io(cls, io_dict: dict, allowed_types: tuple, parse_cls):
        for key, value in io_dict.items():
            # output mode of last node should not affect input mode of next node
            if isinstance(value, PipelineOutputBase):
                # value = copy.deepcopy(value)
                value = value._deepcopy()  # Decoupled input and output
                io_dict[key] = value
                value.mode = None
            if value is None or isinstance(value, allowed_types):
                pass
            elif isinstance(value, dict):
                # parse dict to allowed type
                io_dict[key] = parse_cls(**value)
            else:
                raise Exception(f"Expecting {allowed_types} for input/output {key}, got {type(value)} instead.")

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "component": (str, ParallelComponent),
            "retry_settings": (dict, RetrySettings),
            "resources": (dict, ResourceConfiguration),
            "task": (dict, ParallelTask),
            "logging_level": str,
            "max_concurrency_per_instance": int,
            "error_threshold": int,
            "mini_batch_error_threshold": int,
            "environment_variables": dict,
        }

    def _to_job(self) -> ParallelJob:
        return ParallelJob(
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            tags=self.tags,
            properties=self.properties,
            compute=self.compute,
            resources=self.resources,
            mini_batch_size=self.mini_batch_size,
            task=self.task,
            retry_settings=self.retry_settings,
            input_data=self.input_data,
            logging_level=self.logging_level,
            max_concurrency_per_instance=self.max_concurrency_per_instance,
            error_threshold=self.error_threshold,
            mini_batch_error_threshold=self.mini_batch_error_threshold,
            environment_variables=self.environment_variables,
            inputs=self._job_inputs,
            outputs=self._job_outputs,
        )

    def _parallel_attr_to_dict(self, attr, base_type) -> dict:
        # Convert parallel attribute to dict
        rest_attr = None
        parallel_attr = getattr(self, attr)
        if parallel_attr is not None:
            if isinstance(parallel_attr, base_type):
                rest_attr = parallel_attr._to_dict()
            elif isinstance(parallel_attr, dict):
                rest_attr = parallel_attr
            else:
                raise Exception(f"Expecting {base_type} for {attr}, got {type(parallel_attr)} instead.")
        return convert_ordered_dict_to_dict(rest_attr)

    @classmethod
    def _picked_fields_in_to_rest(cls) -> List[str]:
        return [
            "type",
            "resources",
            "error_threshold",
            "mini_batch_error_threshold",
            "environment_variables",
            "max_concurrency_per_instance",
            "task",
            "input_data",
        ]

    def _node_specified_pre_to_rest_operations(self, rest_obj):
        for key in self._picked_fields_in_to_rest():
            if key not in rest_obj:
                rest_obj[key] = None

        rest_obj.update(
            dict(
                componentId=self._get_component_id(),
                retry_settings=get_rest_dict(self.retry_settings),
                logging_level=self.logging_level,
                mini_batch_size=self.mini_batch_size,
                resources=self.resources._to_rest_object().as_dict() if self.resources else None,
            )
        )

    @classmethod
    def _from_rest_object(cls, obj: dict) -> "Parallel":
        inputs = obj.get("inputs", {})
        outputs = obj.get("outputs", {})

        # JObject -> RestJobInput/RestJobOutput
        input_bindings, rest_inputs = from_dict_to_rest_io(inputs, RestJobInput, [ComponentJobConstants.INPUT_PATTERN])
        output_bindings, rest_outputs = from_dict_to_rest_io(
            outputs, RestJobOutput, [ComponentJobConstants.OUTPUT_PATTERN]
        )

        # RestJobInput/RestJobOutput -> JobInput/JobOutput
        dataset_literal_inputs = from_rest_inputs_to_dataset_literal(rest_inputs)
        data_outputs = from_rest_data_outputs(rest_outputs)

        obj["inputs"] = {**dataset_literal_inputs, **input_bindings}
        obj["outputs"] = {**data_outputs, **output_bindings}

        # resources
        if "resources" in obj and obj["resources"]:
            resources = RestResourceConfiguration.from_dict(obj["resources"])
            obj["resources"] = ResourceConfiguration._from_rest_object(resources)

        # retry_settings
        if "retry_settings" in obj and obj["retry_settings"]:
            obj["retry_settings"] = RetrySettings.from_dict(obj["retry_settings"])

        if "task" in obj and obj["task"]:
            obj["task"] = ParallelTask.from_dict(obj["task"])
            task_code = obj["task"].code
            task_env = obj["task"].environment
            # remove azureml: prefix in code and environment which is added in _to_rest_object
            if task_code and isinstance(task_code, str) and task_code.startswith(ARM_ID_PREFIX):
                obj["task"].code = task_code[len(ARM_ID_PREFIX) :]
            if task_env and isinstance(task_env, str) and task_env.startswith(ARM_ID_PREFIX):
                obj["task"].environment = task_env[len(ARM_ID_PREFIX) :]

        # Change componentId -> component, computeId -> compute
        component_id = obj.pop("componentId", None)
        compute_id = obj.pop("computeId", None)
        obj["component"] = component_id
        obj["compute"] = get_resource_name_from_arm_id_safe(compute_id)
        return Parallel(**obj)

    def _build_inputs(self):
        inputs = super(Parallel, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value
        return built_inputs

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline import ParallelSchema

        return ParallelSchema(context=context)

    def __call__(self, *args, **kwargs) -> "Parallel":
        """Call Parallel as a function will return a new instance each time."""
        if isinstance(self._component, Component):
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
            # set default values: compute, environment_variables, outputs
            node._name = self.name
            node.compute = self.compute
            node.tags = self.tags
            node.display_name = self.display_name
            node.mini_batch_size = self.mini_batch_size
            node.logging_level = self.logging_level
            node.max_concurrency_per_instance = self.max_concurrency_per_instance
            node.error_threshold = self.error_threshold
            # deep copy for complex object
            node.retry_settings = copy.deepcopy(self.retry_settings)
            node.input_data = self.input_data
            node.task = copy.deepcopy(self.task)
            node.resources = copy.deepcopy(self.resources)
            node.environment_variables = copy.deepcopy(self.environment_variables)
            return node
        else:
            raise Exception(
                f"Parallel can be called as a function only when referenced component is {type(Component)}, "
                f"currently got {self._component}."
            )

    @property
    def _extra_skip_fields_in_validation(self) -> List[str]:
        """
        Extra fields that should be skipped in validation.
        """
        return ["component"]
