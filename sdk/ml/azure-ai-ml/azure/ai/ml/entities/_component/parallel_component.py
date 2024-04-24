# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import os
import re
from typing import Any, Dict, List, Optional, Union, cast

from marshmallow import Schema

from azure.ai.ml._restclient.v2022_10_01.models import ComponentVersion
from azure.ai.ml._schema.component.parallel_component import ParallelComponentSchema
from azure.ai.ml.constants._common import COMPONENT_TYPE
from azure.ai.ml.constants._component import NodeType
from azure.ai.ml.entities._job.job_resource_configuration import JobResourceConfiguration
from azure.ai.ml.entities._job.parallel.parallel_task import ParallelTask
from azure.ai.ml.entities._job.parallel.parameterized_parallel import ParameterizedParallel
from azure.ai.ml.entities._job.parallel.retry_settings import RetrySettings
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

from ..._schema import PathAwareSchema
from .._util import validate_attribute_type
from .._validation import MutableValidationResult
from .code import ComponentCodeMixin
from .component import Component


class ParallelComponent(
    Component, ParameterizedParallel, ComponentCodeMixin
):  # pylint: disable=too-many-instance-attributes
    """Parallel component version, used to define a parallel component.

    :param name: Name of the component. Defaults to None
    :type name: str
    :param version: Version of the component. Defaults to None
    :type version: str
    :param description: Description of the component. Defaults to None
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated. Defaults to None
    :type tags: dict
    :param display_name: Display name of the component. Defaults to None
    :type display_name: str
    :param retry_settings: parallel component run failed retry. Defaults to None
    :type retry_settings: BatchRetrySettings
    :param logging_level: A string of the logging level name. Defaults to None
    :type logging_level: str
    :param max_concurrency_per_instance: The max parallellism that each compute instance has. Defaults to None
    :type max_concurrency_per_instance: int
    :param error_threshold: The number of item processing failures should be ignored. Defaults to None
    :type error_threshold: int
    :param mini_batch_error_threshold: The number of mini batch processing failures should be ignored. Defaults to None
    :type mini_batch_error_threshold: int
    :param task: The parallel task. Defaults to None
    :type task: ParallelTask
    :param mini_batch_size: For FileDataset input, this field is the number of files a user script can process
        in one run() call. For TabularDataset input, this field is the approximate size of data the user script
        can process in one run() call. Example values are 1024, 1024KB, 10MB, and 1GB.
        (optional, default value is 10 files for FileDataset and 1MB for TabularDataset.) This value could be set
        through PipelineParameter.
    :type mini_batch_size: str
    :param partition_keys:  The keys used to partition dataset into mini-batches. Defaults to None
        If specified, the data with the same key will be partitioned into the same mini-batch.
        If both partition_keys and mini_batch_size are specified, partition_keys will take effect.
        The input(s) must be partitioned dataset(s),
        and the partition_keys must be a subset of the keys of every input dataset for this to work.
    :type partition_keys: list
    :param input_data: The input data. Defaults to None
    :type input_data: str
    :param resources: Compute Resource configuration for the component. Defaults to None
    :type resources: Union[dict, ~azure.ai.ml.entities.JobResourceConfiguration]
    :param inputs: Inputs of the component. Defaults to None
    :type inputs: dict
    :param outputs: Outputs of the component. Defaults to None
    :type outputs: dict
    :param code: promoted property from task.code
    :type code: str
    :param instance_count: promoted property from resources.instance_count. Defaults to None
    :type instance_count: int
    :param is_deterministic: Whether the parallel component is deterministic. Defaults to True
    :type is_deterministic: bool
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if ParallelComponent cannot be successfully validated.
        Details will be provided in the error message.
    """

    def __init__(  # pylint: disable=too-many-locals
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        display_name: Optional[str] = None,
        retry_settings: Optional[RetrySettings] = None,
        logging_level: Optional[str] = None,
        max_concurrency_per_instance: Optional[int] = None,
        error_threshold: Optional[int] = None,
        mini_batch_error_threshold: Optional[int] = None,
        task: Optional[ParallelTask] = None,
        mini_batch_size: Optional[str] = None,
        partition_keys: Optional[List] = None,
        input_data: Optional[str] = None,
        resources: Optional[JobResourceConfiguration] = None,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        code: Optional[str] = None,  # promoted property from task.code
        instance_count: Optional[int] = None,  # promoted property from resources.instance_count
        is_deterministic: bool = True,
        **kwargs: Any,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        kwargs[COMPONENT_TYPE] = NodeType.PARALLEL

        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            display_name=display_name,
            inputs=inputs,
            outputs=outputs,
            is_deterministic=is_deterministic,
            **kwargs,
        )

        # No validation on value passed here because in pipeline job, required code&environment maybe absent
        # and fill in later with job defaults.
        self.task = task
        self.mini_batch_size: int = 0
        self.partition_keys = partition_keys
        self.input_data = input_data
        self.retry_settings = retry_settings
        self.logging_level = logging_level
        self.max_concurrency_per_instance = max_concurrency_per_instance
        self.error_threshold = error_threshold
        self.mini_batch_error_threshold = mini_batch_error_threshold
        self.resources = resources

        # check mutual exclusivity of promoted properties
        if self.resources is not None and instance_count is not None:
            msg = "instance_count and resources are mutually exclusive"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPONENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        self.instance_count = instance_count
        self.code = code

        if mini_batch_size is not None:
            # Convert str to int.
            pattern = re.compile(r"^\d+([kKmMgG][bB])*$")
            if not pattern.match(mini_batch_size):
                raise ValueError(r"Parameter mini_batch_size must follow regex rule ^\d+([kKmMgG][bB])*$")

            try:
                self.mini_batch_size = int(mini_batch_size)
            except ValueError as e:
                unit = mini_batch_size[-2:].lower()
                if unit == "kb":
                    self.mini_batch_size = int(mini_batch_size[0:-2]) * 1024
                elif unit == "mb":
                    self.mini_batch_size = int(mini_batch_size[0:-2]) * 1024 * 1024
                elif unit == "gb":
                    self.mini_batch_size = int(mini_batch_size[0:-2]) * 1024 * 1024 * 1024
                else:
                    raise ValueError("mini_batch_size unit must be kb, mb or gb") from e

    @property
    def instance_count(self) -> Optional[int]:
        """Return value of promoted property resources.instance_count.

        :return: Value of resources.instance_count.
        :rtype: Optional[int]
        """
        return self.resources.instance_count if self.resources and not isinstance(self.resources, dict) else None

    @instance_count.setter
    def instance_count(self, value: int) -> None:
        """Set the value of the promoted property resources.instance_count.

        :param value: The value to set for resources.instance_count.
        :type value: int
        """
        if not value:
            return
        if not self.resources:
            self.resources = JobResourceConfiguration(instance_count=value)
        else:
            if not isinstance(self.resources, dict):
                self.resources.instance_count = value

    @property
    def code(self) -> Optional[str]:
        """Return value of promoted property task.code, which is a local or
        remote path pointing at source code.

        :return: Value of task.code.
        :rtype: Optional[str]
        """
        return self.task.code if self.task else None

    @code.setter
    def code(self, value: str) -> None:
        """Set the value of the promoted property task.code.

        :param value: The value to set for task.code.
        :type value: str
        """
        if not value:
            return
        if not self.task:
            self.task = ParallelTask(code=value)
        else:
            self.task.code = value

    def _to_ordered_dict_for_yaml_dump(self) -> Dict:
        """Dump the component content into a sorted yaml string.

        :return: The ordered dict
        :rtype: Dict
        """

        obj: dict = super()._to_ordered_dict_for_yaml_dump()
        # dict dumped base on schema will transfer code to an absolute path, while we want to keep its original value
        if self.code and isinstance(self.code, str):
            obj["task"]["code"] = self.code
        return obj

    @property
    def environment(self) -> Optional[str]:
        """Return value of promoted property task.environment, indicate the
        environment that training job will run in.

        :return: Value of task.environment.
        :rtype: Optional[Environment, str]
        """
        if self.task:
            return cast(Optional[str], self.task.environment)
        return None

    @environment.setter
    def environment(self, value: str) -> None:
        """Set the value of the promoted property task.environment.

        :param value: The value to set for task.environment.
        :type value: str
        """
        if not value:
            return
        if not self.task:
            self.task = ParallelTask(environment=value)
        else:
            self.task.environment = value

    def _customized_validate(self) -> MutableValidationResult:
        validation_result = super()._customized_validate()
        self._append_diagnostics_and_check_if_origin_code_reliable_for_local_path_validation(validation_result)
        return validation_result

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "retry_settings": (dict, RetrySettings),
            "task": (dict, ParallelTask),
            "logging_level": str,
            "max_concurrency_per_instance": int,
            "input_data": str,
            "error_threshold": int,
            "mini_batch_error_threshold": int,
            "code": (str, os.PathLike),
            "resources": (dict, JobResourceConfiguration),
        }

    def _to_rest_object(self) -> ComponentVersion:
        rest_object = super()._to_rest_object()
        # schema required list while backend accept json string
        if self.partition_keys:
            rest_object.properties.component_spec["partition_keys"] = json.dumps(self.partition_keys)
        return rest_object

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: ComponentVersion) -> Dict:
        # schema required list while backend accept json string
        # update rest obj as it will be
        partition_keys = obj.properties.component_spec.get("partition_keys", None)
        if partition_keys:
            obj.properties.component_spec["partition_keys"] = json.loads(partition_keys)
        res: dict = super()._from_rest_object_to_init_params(obj)
        return res

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        return ParallelComponentSchema(context=context)

    def __str__(self) -> str:
        try:
            toYaml: str = self._to_yaml()
            return toYaml
        except BaseException:  # pylint: disable=W0718
            toStr: str = super(ParallelComponent, self).__str__()
            return toStr
