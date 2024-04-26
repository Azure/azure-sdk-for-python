# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import copy
import json
import logging
import os
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Type, Union, cast

from marshmallow import INCLUDE, Schema

from azure.ai.ml._schema.core.fields import NestedField, UnionField
from azure.ai.ml._schema.job.identity import AMLTokenIdentitySchema, ManagedIdentitySchema, UserIdentitySchema
from azure.ai.ml.entities._credentials import (
    AmlTokenConfiguration,
    ManagedIdentityConfiguration,
    UserIdentityConfiguration,
    _BaseJobIdentityConfiguration,
)
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.parallel.run_function import RunFunction
from azure.ai.ml.entities._job.pipeline._io import NodeOutput
from azure.ai.ml.exceptions import MlException

from ..._schema import PathAwareSchema
from ..._utils.utils import is_data_binding_expression
from ...constants._common import ARM_ID_PREFIX
from ...constants._component import NodeType
from .._component.component import Component
from .._component.flow import FlowComponent
from .._component.parallel_component import ParallelComponent
from .._inputs_outputs import Input, Output
from .._job.job_resource_configuration import JobResourceConfiguration
from .._job.parallel.parallel_job import ParallelJob
from .._job.parallel.parallel_task import ParallelTask
from .._job.parallel.retry_settings import RetrySettings
from .._job.pipeline._io import NodeWithGroupInputMixin
from .._util import convert_ordered_dict_to_dict, get_rest_dict_for_node_attrs, validate_attribute_type
from .base_node import BaseNode

module_logger = logging.getLogger(__name__)


class Parallel(BaseNode, NodeWithGroupInputMixin):  # pylint: disable=too-many-instance-attributes
    """Base class for parallel node, used for parallel component version consumption.

    You should not instantiate this class directly. Instead, you should
    create from builder function: parallel.

    :param component: Id or instance of the parallel component/job to be run for the step
    :type component: ~azure.ai.ml.entities._component.parallel_component.parallelComponent
    :param name: Name of the parallel
    :type name: str
    :param description: Description of the commad
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated
    :type tags: dict[str, str]
    :param properties: The job property dictionary
    :type properties: dict[str, str]
    :param display_name: Display name of the job
    :type display_name: str
    :param retry_settings: Parallel job run failed retry
    :type retry_settings: BatchRetrySettings
    :param logging_level: A string of the logging level name
    :type logging_level: str
    :param max_concurrency_per_instance: The max parallellism that each compute instance has
    :type max_concurrency_per_instance: int
    :param error_threshold: The number of item processing failures should be ignored
    :type error_threshold: int
    :param mini_batch_error_threshold: The number of mini batch processing failures should be ignored
    :type mini_batch_error_threshold: int
    :param task: The parallel task
    :type task: ParallelTask
    :param mini_batch_size: For FileDataset input, this field is the number of files
                            a user script can process in one run() call.
                            For TabularDataset input, this field is the approximate size of data
                            the user script can process in one run() call.
                            Example values are 1024, 1024KB, 10MB, and 1GB. (optional, default value is 10 files
                            for FileDataset and 1MB for TabularDataset.)
                            This value could be set through PipelineParameter
    :type mini_batch_size: str
    :param partition_keys: The keys used to partition dataset into mini-batches. If specified,
                           the data with the same key will be partitioned into the same mini-batch.
                           If both partition_keys and mini_batch_size are specified,
                           the partition keys will take effect.
                           The input(s) must be partitioned dataset(s),
                           and the partition_keys must be a subset of the keys of every input dataset for this to work.
    :keyword identity: The identity that the command job will use while running on compute.
    :paramtype identity: Optional[Union[
        dict[str, str],
        ~azure.ai.ml.entities.ManagedIdentityConfiguration,
        ~azure.ai.ml.entities.AmlTokenConfiguration,
        ~azure.ai.ml.entities.UserIdentityConfiguration]]
    :type partition_keys: List
    :param input_data: The input data
    :type input_data: str
    :param inputs: Inputs of the component/job
    :type inputs: dict
    :param outputs: Outputs of the component/job
    :type outputs: dict
    """

    # pylint: disable=too-many-statements
    def __init__(
        self,
        *,
        component: Union[ParallelComponent, str],
        compute: Optional[str] = None,
        inputs: Optional[Dict[str, Union[NodeOutput, Input, str, bool, int, float, Enum]]] = None,
        outputs: Optional[Dict[str, Union[str, Output, "Output"]]] = None,
        retry_settings: Optional[Union[RetrySettings, Dict[str, str]]] = None,
        logging_level: Optional[str] = None,
        max_concurrency_per_instance: Optional[int] = None,
        error_threshold: Optional[int] = None,
        mini_batch_error_threshold: Optional[int] = None,
        input_data: Optional[str] = None,
        task: Optional[Union[ParallelTask, RunFunction, Dict]] = None,
        partition_keys: Optional[List] = None,
        mini_batch_size: Optional[Union[str, int]] = None,
        resources: Optional[JobResourceConfiguration] = None,
        environment_variables: Optional[Dict] = None,
        identity: Optional[
            Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration, Dict]
        ] = None,
        **kwargs: Any,
    ) -> None:
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())
        kwargs.pop("type", None)

        if isinstance(component, FlowComponent):
            # make input definition fit actual inputs for flow component
            # pylint: disable=protected-access
            with component._inputs._fit_inputs(inputs):  # type: ignore[attr-defined]
                BaseNode.__init__(
                    self,
                    type=NodeType.PARALLEL,
                    component=component,
                    inputs=inputs,
                    outputs=outputs,
                    compute=compute,
                    **kwargs,
                )
        else:
            BaseNode.__init__(
                self,
                type=NodeType.PARALLEL,
                component=component,
                inputs=inputs,
                outputs=outputs,
                compute=compute,
                **kwargs,
            )
        # init mark for _AttrDict
        self._init = True

        self._task = task

        if (
            mini_batch_size is not None
            and not isinstance(mini_batch_size, int)
            and not is_data_binding_expression(mini_batch_size)
        ):
            """Convert str to int."""  # pylint: disable=pointless-string-statement
            pattern = re.compile(r"^\d+([kKmMgG][bB])*$")
            if not pattern.match(mini_batch_size):
                raise ValueError(r"Parameter mini_batch_size must follow regex rule ^\d+([kKmMgG][bB])*$")

            try:
                mini_batch_size = int(mini_batch_size)
            except ValueError as e:
                if not isinstance(mini_batch_size, int):
                    unit = mini_batch_size[-2:].lower()
                    if unit == "kb":
                        mini_batch_size = int(mini_batch_size[0:-2]) * 1024
                    elif unit == "mb":
                        mini_batch_size = int(mini_batch_size[0:-2]) * 1024 * 1024
                    elif unit == "gb":
                        mini_batch_size = int(mini_batch_size[0:-2]) * 1024 * 1024 * 1024
                    else:
                        raise ValueError("mini_batch_size unit must be kb, mb or gb") from e

        self.mini_batch_size = mini_batch_size
        self.partition_keys = partition_keys
        self.input_data = input_data
        self._retry_settings = retry_settings
        self.logging_level = logging_level
        self.max_concurrency_per_instance = max_concurrency_per_instance
        self.error_threshold = error_threshold
        self.mini_batch_error_threshold = mini_batch_error_threshold
        self._resources = resources
        self.environment_variables = {} if environment_variables is None else environment_variables
        self._identity = identity
        if isinstance(self.component, ParallelComponent):
            self.resources = cast(JobResourceConfiguration, self.resources) or cast(
                JobResourceConfiguration, copy.deepcopy(self.component.resources)
            )
            # TODO: Bug Item number: 2897665
            self.retry_settings = self.retry_settings or copy.deepcopy(self.component.retry_settings)  # type: ignore
            self.input_data = self.input_data or self.component.input_data
            self.max_concurrency_per_instance = (
                self.max_concurrency_per_instance or self.component.max_concurrency_per_instance
            )
            self.mini_batch_error_threshold = (
                self.mini_batch_error_threshold or self.component.mini_batch_error_threshold
            )
            self.mini_batch_size = self.mini_batch_size or self.component.mini_batch_size
            self.partition_keys = self.partition_keys or copy.deepcopy(self.component.partition_keys)

            if not self.task:
                self.task = self.component.task
                # task.code is based on self.component.base_path
                self._base_path = self.component.base_path

        self._init = False

    @classmethod
    def _get_supported_outputs_types(cls) -> Tuple:
        return str, Output

    @property
    def retry_settings(self) -> RetrySettings:
        """Get the retry settings for the parallel job.

        :return: The retry settings for the parallel job.
        :rtype: ~azure.ai.ml.entities._job.parallel.retry_settings.RetrySettings
        """
        return self._retry_settings  # type: ignore

    @retry_settings.setter
    def retry_settings(self, value: Union[RetrySettings, Dict]) -> None:
        """Set the retry settings for the parallel job.

        :param value: The retry settings for the parallel job.
        :type value: ~azure.ai.ml.entities._job.parallel.retry_settings.RetrySettings or dict
        """
        if isinstance(value, dict):
            value = RetrySettings(**value)
        self._retry_settings = value

    @property
    def resources(self) -> Optional[JobResourceConfiguration]:
        """Get the resource configuration for the parallel job.

        :return: The resource configuration for the parallel job.
        :rtype: ~azure.ai.ml.entities._job.job_resource_configuration.JobResourceConfiguration
        """
        return self._resources

    @resources.setter
    def resources(self, value: Union[JobResourceConfiguration, Dict]) -> None:
        """Set the resource configuration for the parallel job.

        :param value: The resource configuration for the parallel job.
        :type value: ~azure.ai.ml.entities._job.job_resource_configuration.JobResourceConfiguration or dict
        """
        if isinstance(value, dict):
            value = JobResourceConfiguration(**value)
        self._resources = value

    @property
    def identity(
        self,
    ) -> Optional[Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration, Dict]]:
        """The identity that the job will use while running on compute.

        :return: The identity that the job will use while running on compute.
        :rtype: Optional[Union[~azure.ai.ml.ManagedIdentityConfiguration, ~azure.ai.ml.AmlTokenConfiguration,
            ~azure.ai.ml.UserIdentityConfiguration]]
        """
        return self._identity

    @identity.setter
    def identity(
        self,
        value: Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration, None],
    ) -> None:
        """Sets the identity that the job will use while running on compute.

        :param value: The identity that the job will use while running on compute.
        :type value: Union[dict[str, str], ~azure.ai.ml.ManagedIdentityConfiguration,
            ~azure.ai.ml.AmlTokenConfiguration, ~azure.ai.ml.UserIdentityConfiguration]
        """
        if isinstance(value, dict):
            identity_schema = UnionField(
                [
                    NestedField(ManagedIdentitySchema, unknown=INCLUDE),
                    NestedField(AMLTokenIdentitySchema, unknown=INCLUDE),
                    NestedField(UserIdentitySchema, unknown=INCLUDE),
                ]
            )
            value = identity_schema._deserialize(value=value, attr=None, data=None)
        self._identity = value

    @property
    def component(self) -> Union[str, ParallelComponent]:
        """Get the component of the parallel job.

        :return: The component of the parallel job.
        :rtype: str or ~azure.ai.ml.entities._component.parallel_component.ParallelComponent
        """
        res: Union[str, ParallelComponent] = self._component
        return res

    @property
    def task(self) -> Optional[ParallelTask]:
        """Get the parallel task.

        :return: The parallel task.
        :rtype: ~azure.ai.ml.entities._job.parallel.parallel_task.ParallelTask
        """
        return self._task  # type: ignore

    @task.setter
    def task(self, value: Union[ParallelTask, Dict]) -> None:
        """Set the parallel task.

        :param value: The parallel task.
        :type value: ~azure.ai.ml.entities._job.parallel.parallel_task.ParallelTask or dict
        """
        # base path should be reset if task is set via sdk
        self._base_path: Optional[Union[str, os.PathLike]] = None
        if isinstance(value, dict):
            value = ParallelTask(**value)
        self._task = value

    def _set_base_path(self, base_path: Optional[Union[str, os.PathLike]]) -> None:
        if self._base_path:
            return
        super(Parallel, self)._set_base_path(base_path)

    def set_resources(
        self,
        *,
        instance_type: Optional[Union[str, List[str]]] = None,
        instance_count: Optional[int] = None,
        properties: Optional[Dict] = None,
        docker_args: Optional[str] = None,
        shm_size: Optional[str] = None,
        # pylint: disable=unused-argument
        **kwargs: Any,
    ) -> None:
        """Set the resources for the parallel job.

        :keyword instance_type: The instance type or a list of instance types used as supported by the compute target.
        :paramtype instance_type: Union[str, List[str]]
        :keyword instance_count: The number of instances or nodes used by the compute target.
        :paramtype instance_count: int
        :keyword properties: The property dictionary for the resources.
        :paramtype properties: dict
        :keyword docker_args: Extra arguments to pass to the Docker run command.
        :paramtype docker_args: str
        :keyword shm_size: Size of the Docker container's shared memory block.
        :paramtype shm_size: str
        """
        if self.resources is None:
            self.resources = JobResourceConfiguration()

        if instance_type is not None:
            self.resources.instance_type = instance_type
        if instance_count is not None:
            self.resources.instance_count = instance_count
        if properties is not None:
            self.resources.properties = properties
        if docker_args is not None:
            self.resources.docker_args = docker_args
        if shm_size is not None:
            self.resources.shm_size = shm_size

        # Save the resources to internal component as well, otherwise calling sweep() will loose the settings
        if isinstance(self.component, Component):
            self.component.resources = self.resources

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "component": (str, ParallelComponent, FlowComponent),
            "retry_settings": (dict, RetrySettings),
            "resources": (dict, JobResourceConfiguration),
            "task": (dict, ParallelTask),
            "logging_level": str,
            "max_concurrency_per_instance": (str, int),
            "error_threshold": (str, int),
            "mini_batch_error_threshold": (str, int),
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
            partition_keys=self.partition_keys,
            mini_batch_size=self.mini_batch_size,
            task=self.task,
            retry_settings=self.retry_settings,
            input_data=self.input_data,
            logging_level=self.logging_level,
            identity=self.identity,
            max_concurrency_per_instance=self.max_concurrency_per_instance,
            error_threshold=self.error_threshold,
            mini_batch_error_threshold=self.mini_batch_error_threshold,
            environment_variables=self.environment_variables,
            inputs=self._job_inputs,
            outputs=self._job_outputs,
        )

    def _parallel_attr_to_dict(self, attr: str, base_type: Type) -> dict:
        # Convert parallel attribute to dict
        rest_attr = {}
        parallel_attr = getattr(self, attr)
        if parallel_attr is not None:
            if isinstance(parallel_attr, base_type):
                rest_attr = parallel_attr._to_dict()
            elif isinstance(parallel_attr, dict):
                rest_attr = parallel_attr
            else:
                msg = f"Expecting {base_type} for {attr}, got {type(parallel_attr)} instead."
                raise MlException(message=msg, no_personal_data_message=msg)
        # TODO: Bug Item number: 2897665
        res: dict = convert_ordered_dict_to_dict(rest_attr)  # type: ignore
        return res

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
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

    def _to_rest_object(self, **kwargs: Any) -> dict:
        rest_obj: Dict = super(Parallel, self)._to_rest_object(**kwargs)
        rest_obj.update(
            convert_ordered_dict_to_dict(
                {
                    "componentId": self._get_component_id(),
                    "retry_settings": get_rest_dict_for_node_attrs(self.retry_settings),
                    "logging_level": self.logging_level,
                    "mini_batch_size": self.mini_batch_size,
                    "partition_keys": (
                        json.dumps(self.partition_keys) if self.partition_keys is not None else self.partition_keys
                    ),
                    "identity": get_rest_dict_for_node_attrs(self.identity),
                    "resources": get_rest_dict_for_node_attrs(self.resources),
                }
            )
        )
        return rest_obj

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: dict) -> Dict:
        obj = super()._from_rest_object_to_init_params(obj)
        # retry_settings
        if "retry_settings" in obj and obj["retry_settings"]:
            obj["retry_settings"] = RetrySettings._from_dict(obj["retry_settings"])

        if "task" in obj and obj["task"]:
            obj["task"] = ParallelTask._from_dict(obj["task"])
            task_code = obj["task"].code
            task_env = obj["task"].environment
            # remove azureml: prefix in code and environment which is added in _to_rest_object
            if task_code and isinstance(task_code, str) and task_code.startswith(ARM_ID_PREFIX):
                obj["task"].code = task_code[len(ARM_ID_PREFIX) :]
            if task_env and isinstance(task_env, str) and task_env.startswith(ARM_ID_PREFIX):
                obj["task"].environment = task_env[len(ARM_ID_PREFIX) :]

        if "resources" in obj and obj["resources"]:
            obj["resources"] = JobResourceConfiguration._from_rest_object(obj["resources"])

        if "partition_keys" in obj and obj["partition_keys"]:
            obj["partition_keys"] = json.dumps(obj["partition_keys"])
        if "identity" in obj and obj["identity"]:
            obj["identity"] = _BaseJobIdentityConfiguration._from_rest_object(obj["identity"])
        return obj

    def _build_inputs(self) -> Dict:
        inputs = super(Parallel, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value
        return built_inputs

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline import ParallelSchema

        return ParallelSchema(context=context)

    # pylint: disable-next=docstring-missing-param
    def __call__(self, *args: Any, **kwargs: Any) -> "Parallel":
        """Call Parallel as a function will return a new instance each time.

        :return: A Parallel node
        :rtype: Parallel
        """
        if isinstance(self._component, Component):
            # call this to validate inputs
            node: Parallel = self._component(*args, **kwargs)
            # merge inputs
            for name, original_input in self.inputs.items():
                if name not in kwargs:
                    # use setattr here to make sure owner of input won't change
                    setattr(node.inputs, name, original_input._data)
                # get outputs
            for name, original_output in self.outputs.items():
                # use setattr here to make sure owner of input won't change
                if not isinstance(original_output, str):
                    setattr(node.outputs, name, original_output._data)
            self._refine_optional_inputs_with_no_value(node, kwargs)
            # set default values: compute, environment_variables, outputs
            node._name = self.name
            node.compute = self.compute
            node.tags = self.tags
            node.display_name = self.display_name
            node.mini_batch_size = self.mini_batch_size
            node.partition_keys = self.partition_keys
            node.logging_level = self.logging_level
            node.max_concurrency_per_instance = self.max_concurrency_per_instance
            node.error_threshold = self.error_threshold
            # deep copy for complex object
            node.retry_settings = copy.deepcopy(self.retry_settings)
            node.input_data = self.input_data
            node.task = copy.deepcopy(self.task)
            node._base_path = self.base_path
            node.resources = copy.deepcopy(self.resources)
            node.environment_variables = copy.deepcopy(self.environment_variables)
            node.identity = copy.deepcopy(self.identity)
            return node
        msg = f"Parallel can be called as a function only when referenced component is {type(Component)}, \
            currently got {self._component}."
        raise MlException(message=msg, no_personal_data_message=msg)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> "Job":
        raise NotImplementedError()
